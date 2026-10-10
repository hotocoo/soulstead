extends Node
## Online session layer for SOULSTEAD.
##
## Friends on different networks join with a six-character lobby code. All
## clients (including the player who created the lobby) connect out to a public
## relay server over WebSocket, so nobody needs port forwarding, a LAN, or the
## same WiFi. The relay owns lobby membership and forwards traffic; see
## `server/` for the headless build and `docs/MULTIPLAYER.md` for deployment.
##
## A direct ENet mode is kept for LAN play and for connecting straight to a
## self-hosted dedicated server.

signal connection_state(status: String)
signal lobby_joined(code: String, members: Array)
signal lobbies_listed(open_lobbies: Array)
signal lobby_failed(reason: String)
signal peer_joined(peer_id: int, settlement: String)
signal peer_left(peer_id: int)
signal session_ended()
signal remote_state(peer_id: int, state: Dictionary)
signal ally_down(ally_name: String)

const RELAY_ID := 1
const DEFAULT_RELAY_URL := "wss://relay.soulstead.game"
const DEFAULT_ENET_PORT := 8377
const HANDSHAKE_TIMEOUT := 10.0
const STATE_HZ := 15.0

var relay_url: String = DEFAULT_RELAY_URL
var settlement_name: String = "Soulstead"
var lobby_code: String = ""
var members: Dictionary = {}
var status: String = "offline"

var _pending_code: String = ""
var _pending_create: bool = false
var _handshake_timer: float = 0.0
var _state_accumulator: float = 0.0

func _ready() -> void:
	set_process(true)
	multiplayer.connected_to_server.connect(_on_connected)
	multiplayer.connection_failed.connect(_on_connection_failed)
	multiplayer.server_disconnected.connect(_on_server_disconnected)
	var override := OS.get_environment("SOULSTEAD_RELAY")
	if override != "":
		relay_url = override

func is_networked() -> bool:
	return status == "in_lobby"

func _process(delta: float) -> void:
	if status == "connecting":
		_handshake_timer -= delta
		if _handshake_timer <= 0.0:
			lobby_failed.emit("Could not reach the relay at %s" % relay_url)
			leave()

# --- Public entry points -------------------------------------------------

## Creates a lobby and returns the code friends should type in. The code comes
## back from the relay through `lobby_joined`.
func create_lobby(settlement: String, url: String = "") -> void:
	settlement_name = settlement
	_pending_create = true
	_pending_code = ""
	_connect_relay(url)

## Joins an existing lobby from anywhere on the internet.
func join_lobby(code: String, settlement: String, url: String = "") -> void:
	settlement_name = settlement
	_pending_create = false
	_pending_code = code.strip_edges().to_upper()
	_connect_relay(url)

## Direct connection for LAN or a private dedicated server.
func join_direct(address: String, port: int = DEFAULT_ENET_PORT, settlement: String = "") -> bool:
	if settlement != "":
		settlement_name = settlement
	var peer := ENetMultiplayerPeer.new()
	var err := peer.create_client(address, port)
	if err != OK:
		lobby_failed.emit("Could not reach %s:%d (%s)" % [address, port, error_string(err)])
		return false
	multiplayer.multiplayer_peer = peer
	_pending_create = false
	_pending_code = ""
	_set_status("connecting")
	return true

## Browse open lobbies. Connects to the relay first if needed; the result
## arrives on `lobbies_listed`.
func browse_lobbies(settlement: String, url: String = "") -> void:
	settlement_name = settlement
	if status == "in_lobby" or status == "connected":
		_relay_list_lobbies.rpc_id(RELAY_ID)
		return
	_pending_create = false
	_pending_code = "__browse__"
	_connect_relay(url)

func leave() -> void:
	if multiplayer.multiplayer_peer != null:
		# Flush anything queued this frame; closing a WebSocket peer drops
		# unsent packets, and a dropped packet here is a lost consequence.
		multiplayer.multiplayer_peer.poll()
		multiplayer.multiplayer_peer.close()
	multiplayer.multiplayer_peer = null
	members.clear()
	lobby_code = ""
	_set_status("offline")
	session_ended.emit()

func _connect_relay(url: String) -> void:
	if url != "":
		relay_url = url
	var peer := WebSocketMultiplayerPeer.new()
	var err := peer.create_client(relay_url)
	if err != OK:
		lobby_failed.emit("Relay URL rejected: %s (%s)" % [relay_url, error_string(err)])
		return
	multiplayer.multiplayer_peer = peer
	_handshake_timer = HANDSHAKE_TIMEOUT
	_set_status("connecting")

func _set_status(next: String) -> void:
	status = next
	connection_state.emit(status)

# --- Handshake -----------------------------------------------------------

func _on_connected() -> void:
	_set_status("connected")
	if _pending_create:
		_relay_create_lobby.rpc_id(RELAY_ID, settlement_name)
	elif _pending_code == "__browse__":
		_pending_code = ""
		_relay_list_lobbies.rpc_id(RELAY_ID)
	elif _pending_code != "":
		_relay_join_lobby.rpc_id(RELAY_ID, _pending_code, settlement_name)
	else:
		_relay_join_lobby.rpc_id(RELAY_ID, "DIRECT", settlement_name)

func _on_connection_failed() -> void:
	lobby_failed.emit("The relay refused the connection.")
	leave()

func _on_server_disconnected() -> void:
	lobby_failed.emit("Lost the relay connection.")
	leave()

# --- Calls into the relay (implemented server-side) ----------------------

@rpc("any_peer", "reliable")
func _relay_create_lobby(_settlement: String) -> void:
	pass

@rpc("any_peer", "reliable")
func _relay_join_lobby(_code: String, _settlement: String) -> void:
	pass

@rpc("any_peer", "reliable")
func _relay_list_lobbies() -> void:
	pass

@rpc("any_peer", "reliable")
func _relay_forward(_entry: Dictionary) -> void:
	pass

@rpc("any_peer", "unreliable_ordered")
func _relay_state(_state: Dictionary) -> void:
	pass

# --- Calls from the relay ------------------------------------------------

@rpc("authority", "reliable")
func lobby_ready(code: String, member_list: Array) -> void:
	lobby_code = code
	members.clear()
	# `members` holds the *other* settlements in the lobby, never this one.
	var self_id := multiplayer.get_unique_id()
	for entry: Dictionary in member_list:
		if int(entry["id"]) == self_id:
			continue
		members[int(entry["id"])] = String(entry["settlement"])
	_set_status("in_lobby")
	lobby_joined.emit(code, member_list)

## Open lobbies anywhere on the internet, for players who have no code to type.
@rpc("authority", "reliable")
func lobby_list(open_lobbies: Array) -> void:
	lobbies_listed.emit(open_lobbies)

@rpc("authority", "reliable")
func lobby_rejected(reason: String) -> void:
	lobby_failed.emit(reason)
	leave()

@rpc("authority", "reliable")
func member_joined(peer_id: int, settlement: String) -> void:
	members[peer_id] = settlement
	peer_joined.emit(peer_id, settlement)

@rpc("authority", "reliable")
func member_left(peer_id: int) -> void:
	members.erase(peer_id)
	peer_left.emit(peer_id)

## The relay hands a joining player the current ledger so both worlds agree on
## the ending they are drifting toward.
@rpc("authority", "reliable")
func sync_ledger(data: Dictionary) -> void:
	Chronicle.from_dict(data)

@rpc("authority", "reliable")
func deliver_entry(entry: Dictionary) -> void:
	Chronicle.apply_remote(entry)

@rpc("authority", "unreliable_ordered")
func deliver_state(peer_id: int, state: Dictionary) -> void:
	remote_state.emit(peer_id, state)

@rpc("authority", "reliable")
func deliver_ally_down(ally_name: String) -> void:
	ally_down.emit(ally_name)

# --- Outbound ------------------------------------------------------------

## Consequence replication: peers exchange Chronicle entries, never snapshots.
func broadcast_entry(entry: Dictionary) -> void:
	if not is_networked():
		return
	# Strip the non-serialisable bits: Chronicle entries must survive JSON and
	# the wire unchanged, or peers disagree about what happened.
	var payload := {
		"action": String(entry.get("action", "")),
		"subject": String(entry.get("subject", "")),
		"actor": String(entry.get("actor", "")),
		"day": float(entry.get("day", 0.0)),
		"text": String(entry.get("text", "")),
	}
	_relay_forward.rpc_id(RELAY_ID, payload)

## Lossy body replication, rate limited so the relay stays cheap to run.
func push_state(state: Dictionary, delta: float) -> void:
	if not is_networked():
		return
	_state_accumulator += delta
	if _state_accumulator < 1.0 / STATE_HZ:
		return
	_state_accumulator = 0.0
	_relay_state.rpc_id(RELAY_ID, state)

func report_ally_down(ally_name: String) -> void:
	if not is_networked():
		return
	_relay_forward.rpc_id(RELAY_ID, {"action": "__ally_down", "subject": ally_name})
