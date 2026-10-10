extends Node
## SOULSTEAD relay server.
##
## Headless Godot process. Players anywhere on the internet connect out to this
## over WebSocket, so no player needs port forwarding or a shared network. The
## relay owns lobby membership and forwards Chronicle entries and body state
## between members of the same lobby. It stores no account data and keeps a
## lobby only while somebody is in it.
##
## Run locally:   godot --headless --path server
## Run in Docker: see Dockerfile at the repository root of `server/`.
##
## This node MUST be named `NetSession` (see the autoload entry) because Godot
## routes RPCs by node path, and the client's session node has that name.

const DEFAULT_PORT := 8080
const MAX_LOBBY_MEMBERS := 4
const CODE_CHARS := "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
const CODE_LENGTH := 6
const EMPTY_LOBBY_GRACE_SEC := 120.0

# The relay is a standalone Godot project and therefore cannot reference the
# client's autoloaded Chronicle. Keep only the axis weights here. The client
# remains authoritative for its full Chronicle text and entries.
const ACTION_WEIGHTS := {
	"echo_reclaimed": {"memory": 6.0, "mercy": 3.0, "communion": 1.0, "dominion": 2.0},
	"echo_abandoned": {"memory": -5.0, "mercy": -3.0, "communion": -2.0, "dominion": -1.0},
	"echo_raided": {"memory": -8.0, "mercy": -6.0, "communion": -4.0, "dominion": -5.0},
	"vigil_held": {"memory": 8.0, "mercy": 4.0, "communion": 5.0, "dominion": 0.0},
	"vigil_skipped": {"memory": -3.0, "mercy": 0.0, "communion": -2.0, "dominion": 2.0},
	"wielder_died": {"memory": 2.0, "mercy": 0.0, "communion": 0.0, "dominion": -3.0},
	"successor_taken": {"memory": 0.0, "mercy": 0.0, "communion": 2.0, "dominion": 1.0},
	"villager_conscripted": {"memory": -1.0, "mercy": -4.0, "communion": -3.0, "dominion": 5.0},
	"enemy_spared": {"memory": 0.0, "mercy": 6.0, "communion": 2.0, "dominion": -3.0},
	"enemy_slain": {"memory": 0.0, "mercy": -1.0, "communion": 0.0, "dominion": 2.0},
	"relic_spent": {"memory": 5.0, "mercy": 0.0, "communion": 3.0, "dominion": 1.0},
	"region_saved": {"memory": 4.0, "mercy": 7.0, "communion": 6.0, "dominion": 2.0},
	"region_lost": {"memory": -4.0, "mercy": -7.0, "communion": -5.0, "dominion": -4.0},
	"ally_revived": {"memory": 2.0, "mercy": 8.0, "communion": 9.0, "dominion": -2.0},
	"ally_abandoned": {"memory": -2.0, "mercy": -8.0, "communion": -10.0, "dominion": 3.0},
	"echo_sent": {"memory": 3.0, "mercy": -2.0, "communion": 6.0, "dominion": 4.0},
	"foreign_echo_slain": {"memory": 1.0, "mercy": -3.0, "communion": 4.0, "dominion": 6.0},
	"foreign_echo_honoured": {"memory": 6.0, "mercy": 7.0, "communion": 9.0, "dominion": -1.0},
	"route_closed": {"memory": -1.0, "mercy": -2.0, "communion": -2.0, "dominion": -1.0},
	"building_upgraded": {"memory": 1.0, "mercy": 2.0, "communion": 1.0, "dominion": 2.0},
	"cache_opened": {"memory": 1.0, "mercy": 0.0, "communion": 1.0, "dominion": 1.0},
}

var _peer: WebSocketMultiplayerPeer
var _lobbies: Dictionary = {}
var _peer_lobby: Dictionary = {}
var _peer_settlement: Dictionary = {}
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	_rng.randomize()
	var port := DEFAULT_PORT
	var env_port := OS.get_environment("PORT")
	if env_port.is_valid_int():
		port = int(env_port)
	_peer = WebSocketMultiplayerPeer.new()
	var err := _peer.create_server(port)
	if err != OK:
		push_error("Relay could not bind port %d: %s" % [port, error_string(err)])
		get_tree().quit(1)
		return
	multiplayer.multiplayer_peer = _peer
	multiplayer.peer_connected.connect(_on_peer_connected)
	multiplayer.peer_disconnected.connect(_on_peer_disconnected)
	print("[relay] listening on port %d" % port)

func _on_peer_connected(peer_id: int) -> void:
	print("[relay] peer %d connected" % peer_id)

func _on_peer_disconnected(peer_id: int) -> void:
	var code := String(_peer_lobby.get(peer_id, ""))
	_peer_lobby.erase(peer_id)
	_peer_settlement.erase(peer_id)
	if code == "" or not _lobbies.has(code):
		return
	var lobby: Dictionary = _lobbies[code]
	(lobby["members"] as Array).erase(peer_id)
	for other: int in lobby["members"]:
		member_left.rpc_id(other, peer_id)
	if (lobby["members"] as Array).is_empty():
		lobby["empty_since"] = Time.get_unix_time_from_system()
	print("[relay] peer %d left lobby %s" % [peer_id, code])

func _process(_delta: float) -> void:
	_sweep_empty_lobbies()

func _sweep_empty_lobbies() -> void:
	var now := Time.get_unix_time_from_system()
	for code: String in _lobbies.keys():
		var lobby: Dictionary = _lobbies[code]
		if not (lobby["members"] as Array).is_empty():
			continue
		if now - float(lobby.get("empty_since", now)) > EMPTY_LOBBY_GRACE_SEC:
			_lobbies.erase(code)
			print("[relay] lobby %s expired" % code)

func _new_code() -> String:
	for attempt: int in 64:
		var code := ""
		for i: int in CODE_LENGTH:
			code += CODE_CHARS[_rng.randi() % CODE_CHARS.length()]
		if not _lobbies.has(code):
			return code
	return "L%05d" % (_rng.randi() % 100000)

func _member_list(code: String) -> Array:
	var out: Array = []
	if not _lobbies.has(code):
		return out
	for peer_id: int in _lobbies[code]["members"]:
		out.append({"id": peer_id, "settlement": String(_peer_settlement.get(peer_id, "?"))})
	return out

# --- Client -> relay -----------------------------------------------------

@rpc("any_peer", "reliable")
func _relay_create_lobby(settlement: String) -> void:
	var sender := multiplayer.get_remote_sender_id()
	var code := _new_code()
	_lobbies[code] = {"members": [sender], "ledger": {}, "empty_since": 0.0}
	_peer_lobby[sender] = code
	_peer_settlement[sender] = settlement
	lobby_ready.rpc_id(sender, code, _member_list(code))
	print("[relay] lobby %s created by %d (%s)" % [code, sender, settlement])

## Discovery for players who did not swap a code: every open lobby with room in
## it, visible from any network.
@rpc("any_peer", "reliable")
func _relay_list_lobbies() -> void:
	var sender := multiplayer.get_remote_sender_id()
	var open: Array = []
	for code: String in _lobbies:
		var member_ids: Array = _lobbies[code]["members"]
		if member_ids.is_empty() or member_ids.size() >= MAX_LOBBY_MEMBERS:
			continue
		open.append({
			"code": code,
			"host": String(_peer_settlement.get(member_ids[0], "?")),
			"players": member_ids.size(),
			"capacity": MAX_LOBBY_MEMBERS,
		})
	lobby_list.rpc_id(sender, open)

@rpc("any_peer", "reliable")
func _relay_join_lobby(code: String, settlement: String) -> void:
	var sender := multiplayer.get_remote_sender_id()
	var key := code.strip_edges().to_upper()
	if not _lobbies.has(key):
		lobby_rejected.rpc_id(sender, "No lobby with code %s." % key)
		return
	var lobby: Dictionary = _lobbies[key]
	var member_ids: Array = lobby["members"]
	if member_ids.size() >= MAX_LOBBY_MEMBERS:
		lobby_rejected.rpc_id(sender, "Lobby %s is full." % key)
		return
	for other: int in member_ids:
		member_joined.rpc_id(other, sender, settlement)
	member_ids.append(sender)
	_peer_lobby[sender] = key
	_peer_settlement[sender] = settlement
	lobby_ready.rpc_id(sender, key, _member_list(key))
	var ledger: Dictionary = lobby["ledger"]
	if not ledger.is_empty():
		sync_ledger.rpc_id(sender, ledger)
	print("[relay] peer %d joined lobby %s (%s)" % [sender, key, settlement])

@rpc("any_peer", "reliable")
func _relay_forward(entry: Dictionary) -> void:
	var sender := multiplayer.get_remote_sender_id()
	var code := String(_peer_lobby.get(sender, ""))
	if code == "" or not _lobbies.has(code):
		return
	var lobby: Dictionary = _lobbies[code]
	if String(entry.get("action", "")) == "__ally_down":
		for other: int in lobby["members"]:
			if other != sender:
				deliver_ally_down.rpc_id(other, String(entry.get("subject", "An ally")))
		return
	_remember(lobby, entry)
	for other: int in lobby["members"]:
		if other != sender:
			deliver_entry.rpc_id(other, entry)
			print("[relay] %s: %d -> %d (%s)" % [code, sender, other,
					String(entry.get("action", "?"))])

## The relay keeps a light copy of the ledger purely so a late joiner starts
## from the same drift as everyone else.
func _remember(lobby: Dictionary, entry: Dictionary) -> void:
	var ledger: Dictionary = lobby["ledger"]
	if not ledger.has("entries"):
		ledger["entries"] = []
		ledger["axes"] = {"memory": 0.0, "mercy": 0.0, "communion": 0.0, "dominion": 0.0}
	(ledger["entries"] as Array).append(entry)
	var weights: Dictionary = ACTION_WEIGHTS.get(String(entry.get("action", "")), {})
	var axes: Dictionary = ledger["axes"]
	for axis: String in ["memory", "mercy", "communion", "dominion"]:
		if weights.has(axis):
			axes[axis] = clampf(float(axes.get(axis, 0.0)) + float(weights[axis]), -100.0, 100.0)
	if (ledger["entries"] as Array).size() > 500:
		(ledger["entries"] as Array).pop_front()

@rpc("any_peer", "unreliable_ordered")
func _relay_state(state: Dictionary) -> void:
	var sender := multiplayer.get_remote_sender_id()
	var code := String(_peer_lobby.get(sender, ""))
	if code == "" or not _lobbies.has(code):
		return
	for other: int in _lobbies[code]["members"]:
		if other != sender:
			deliver_state.rpc_id(other, sender, state)

# --- Relay -> client (declared so Godot can route them) ------------------

@rpc("authority", "reliable") func lobby_ready(_code: String, _members: Array) -> void: pass
@rpc("authority", "reliable") func lobby_rejected(_reason: String) -> void: pass
@rpc("authority", "reliable") func lobby_list(_lobbies: Array) -> void: pass
@rpc("authority", "reliable") func member_joined(_peer_id: int, _settlement: String) -> void: pass
@rpc("authority", "reliable") func member_left(_peer_id: int) -> void: pass
@rpc("authority", "reliable") func sync_ledger(_data: Dictionary) -> void: pass
@rpc("authority", "reliable") func deliver_entry(_entry: Dictionary) -> void: pass
@rpc("authority", "reliable") func deliver_ally_down(_ally_name: String) -> void: pass
@rpc("authority", "unreliable_ordered") func deliver_state(_peer_id: int, _state: Dictionary) -> void: pass
