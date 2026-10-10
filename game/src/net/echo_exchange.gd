class_name EchoExchange
extends RefCounted
## Asynchronous multiplayer: Echoes drift between settlements.
##
## When an Echo reaches roaming tier it can be exported as a small JSON file
## under `user://drift/`. Any other player's world can import it, and how they
## treat it (kill it or bury it) is written back into their Chronicle. No server
## required: the file is the message.

const DRIFT_DIR := "user://drift"
const OUTBOX := "user://drift/outbox"
const INBOX := "user://drift/inbox"

static func ensure_dirs() -> void:
	for path: String in [DRIFT_DIR, OUTBOX, INBOX]:
		if not DirAccess.dir_exists_absolute(path):
			DirAccess.make_dir_recursive_absolute(path)

## Writes an Echo out for other settlements to receive.
static func send(echo: Dictionary, settlement: String) -> String:
	ensure_dirs()
	var payload := {
		"echo": echo,
		"settlement": settlement,
		"sent_day": WorldState.world_day,
		"sent_at": Time.get_unix_time_from_system(),
	}
	var filename := "%s/echo_%s_%d.json" % [OUTBOX, String(echo["id"]),
			int(payload["sent_at"])]
	var file := FileAccess.open(filename, FileAccess.WRITE)
	if file == null:
		push_error("Could not export Echo: %s" % error_string(FileAccess.get_open_error()))
		return ""
	file.store_string(JSON.stringify(payload, "\t"))
	file.close()
	Chronicle.record("echo_sent", String(echo["owner"]))
	return filename

## Reads every Echo dropped into the inbox. Foreign Echoes keep their original
## owner's name so the player fights a stranger's grief, not a generic monster.
static func receive_all() -> Array[Dictionary]:
	ensure_dirs()
	var out: Array[Dictionary] = []
	var dir := DirAccess.open(INBOX)
	if dir == null:
		return out
	for filename: String in dir.get_files():
		if not filename.ends_with(".json"):
			continue
		var file := FileAccess.open("%s/%s" % [INBOX, filename], FileAccess.READ)
		if file == null:
			continue
		var parsed: Variant = JSON.parse_string(file.get_as_text())
		file.close()
		if typeof(parsed) != TYPE_DICTIONARY:
			push_warning("Skipping malformed drifted Echo: %s" % filename)
			continue
		var payload: Dictionary = parsed
		var echo: Dictionary = payload.get("echo", {})
		if echo.is_empty():
			continue
		echo["foreign"] = true
		echo["from_settlement"] = String(payload.get("settlement", "elsewhere"))
		out.append(echo)
	return out

## Called when the player defeats a drifted Echo: killing and burying are
## different endings' worth of consequence.
static func resolve_foreign(echo: Dictionary, buried: bool) -> void:
	var label := "%s of %s" % [String(echo.get("owner", "a stranger")),
			String(echo.get("from_settlement", "elsewhere"))]
	if buried:
		Chronicle.record("foreign_echo_honoured", label)
	else:
		Chronicle.record("foreign_echo_slain", label)
