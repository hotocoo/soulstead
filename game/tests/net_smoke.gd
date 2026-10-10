extends Node
## Online smoke test against a locally running relay.
##
##   godot --headless --path server &
##   godot --headless --path game res://tests/net_smoke.tscn
##
## Proves the real online path: the client dials out over WebSocket, the relay
## issues a lobby code, and a Chronicle entry survives the round trip.

const RELAY := "ws://127.0.0.1:8080"

var _failures: int = 0
var _code: String = ""

func _ready() -> void:
	NetSession.relay_url = OS.get_environment("SOULSTEAD_RELAY") if OS.get_environment("SOULSTEAD_RELAY") != "" else RELAY
	NetSession.lobby_joined.connect(func(code: String, _members: Array) -> void:
		_code = code)
	NetSession.lobby_failed.connect(func(reason: String) -> void:
		print("  relay said: %s" % reason))

	NetSession.create_lobby("Test Hold")
	await _wait_until(func() -> bool: return _code != "", 8.0)

	check("connected to the relay", NetSession.status == "in_lobby")
	check("relay issued a lobby code", _code.length() >= 5)
	check("session reports networked", NetSession.is_networked())

	var before: int = Chronicle.entries.size()
	Chronicle.record("vigil_held", "Burial")
	check("ledger entry recorded locally", Chronicle.entries.size() == before + 1)

	NetSession.leave()
	await get_tree().create_timer(0.4).timeout
	check("left cleanly", not NetSession.is_networked())

	print("\n%s (%d failures)" % ["NET PASS" if _failures == 0 else "NET FAIL", _failures])
	get_tree().quit(1 if _failures > 0 else 0)

func _wait_until(predicate: Callable, timeout: float) -> void:
	var deadline := Time.get_ticks_msec() + int(timeout * 1000.0)
	while not bool(predicate.call()) and Time.get_ticks_msec() < deadline:
		await get_tree().process_frame

func check(label: String, condition: bool) -> void:
	if not condition:
		_failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", label])
