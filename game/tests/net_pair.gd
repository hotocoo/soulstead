extends Node
## Two-client relay test: proves consequence actually crosses between players.
##
##   godot --headless --path server &
##   SOULSTEAD_TEST_MODE=host godot --headless --path game res://tests/net_pair.tscn
##   SOULSTEAD_TEST_MODE=join SOULSTEAD_TEST_CODE=<code> \
##       godot --headless --path game res://tests/net_pair.tscn
##
## The host writes its lobby code to `user://test_lobby_code.txt` so a harness
## can pick it up without a human reading the log.

const CODE_FILE := "user://test_lobby_code.txt"
const RELAY := "ws://127.0.0.1:8080"

var _failures: int = 0
var _code: String = ""
var _received: Array[Dictionary] = []

func _ready() -> void:
	NetSession.relay_url = OS.get_environment("SOULSTEAD_RELAY") if \
			OS.get_environment("SOULSTEAD_RELAY") != "" else RELAY
	NetSession.lobby_joined.connect(func(code: String, _m: Array) -> void: _code = code)
	NetSession.lobby_failed.connect(func(reason: String) -> void: print("  relay: %s" % reason))
	Chronicle.recorded.connect(func(entry: Dictionary) -> void:
		if bool(entry.get("remote", false)):
			_received.append(entry))

	if OS.get_environment("SOULSTEAD_TEST_MODE") == "join":
		await _run_joiner()
	else:
		await _run_host()

	print("\n%s (%d failures)" % ["PAIR PASS" if _failures == 0 else "PAIR FAIL", _failures])
	get_tree().quit(1 if _failures > 0 else 0)

func _run_host() -> void:
	NetSession.create_lobby("Ashfall Hold")
	await _wait_until(func() -> bool: return _code != "", 8.0)
	check("host opened a lobby", _code != "")
	var file := FileAccess.open(CODE_FILE, FileAccess.WRITE)
	if file != null:
		file.store_string(_code)
		file.close()
	print("  lobby code: %s" % _code)
	# Wait for the joiner, then act so they receive the consequence.
	await _wait_until(func() -> bool: return not NetSession.members.is_empty(), 20.0)
	check("a second settlement joined", not NetSession.members.is_empty())
	# Let the joiner finish its handshake before acting on the shared world.
	await get_tree().create_timer(1.5).timeout
	Chronicle.record("ally_abandoned", "Tarn Grey")
	await _wait_until(func() -> bool: return not _received.is_empty(), 12.0)
	check("host received the joiner's entry", not _received.is_empty())
	# Give the outbound entry a moment on the wire before tearing down.
	await get_tree().create_timer(1.0).timeout
	NetSession.leave()

func _run_joiner() -> void:
	var code := OS.get_environment("SOULSTEAD_TEST_CODE")
	if code == "" and FileAccess.file_exists(CODE_FILE):
		var file := FileAccess.open(CODE_FILE, FileAccess.READ)
		code = file.get_as_text().strip_edges()
		file.close()
	check("a lobby code was available", code != "")
	var communion_before := Chronicle.axis("communion")
	NetSession.join_lobby(code, "Verren Hold")
	await _wait_until(func() -> bool: return NetSession.is_networked(), 10.0)
	check("joined the host's lobby", NetSession.is_networked())
	Chronicle.record("echo_reclaimed", "Maren Holt")
	await _wait_until(func() -> bool: return not _received.is_empty(), 12.0)
	check("the host's action arrived", not _received.is_empty())
	check("a remote action moved this world's ending axes",
			Chronicle.axis("communion") != communion_before)
	await get_tree().create_timer(1.0).timeout
	NetSession.leave()

func _wait_until(predicate: Callable, timeout: float) -> void:
	var deadline := Time.get_ticks_msec() + int(timeout * 1000.0)
	while not bool(predicate.call()) and Time.get_ticks_msec() < deadline:
		await get_tree().process_frame

func check(label: String, condition: bool) -> void:
	if not condition:
		_failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", label])
