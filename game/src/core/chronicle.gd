extends Node
## The Chronicle: an append-only ledger of every meaningful action.
##
## Nothing in SOULSTEAD is cosmetic. Each recorded action shifts four ending
## axes, and the ending is resolved from those axes plus hard gates. In
## multiplayer the ledger is the replicated unit: peers exchange entries, not
## world snapshots, so every player's choices bend the shared ending.

signal recorded(entry: Dictionary)
signal axis_shifted(axis: String, value: float)
signal ending_locked(ending_id: String)

const AXES := ["memory", "mercy", "communion", "dominion"]
const AXIS_LABELS := {
	"memory": "Memory vs Oblivion",
	"mercy": "Mercy vs Ruin",
	"communion": "Communion vs Isolation",
	"dominion": "Dominion vs Surrender",
}
const AXIS_CLAMP := 100.0

## Every verb the player can perform, with its consequence weights.
## Positive shifts the first-named pole, negative shifts the second.
const ACTIONS := {
	"echo_reclaimed": {"memory": 6.0, "mercy": 3.0, "communion": 1.0, "dominion": 2.0,
		"text": "Reclaimed the Echo of %s."},
	"echo_abandoned": {"memory": -5.0, "mercy": -3.0, "communion": -2.0, "dominion": -1.0,
		"text": "Left the Echo of %s to grow."},
	"echo_raided": {"memory": -8.0, "mercy": -6.0, "communion": -4.0, "dominion": -5.0,
		"text": "The Echo of %s reached the palisade."},
	"vigil_held": {"memory": 8.0, "mercy": 4.0, "communion": 5.0, "dominion": 0.0,
		"text": "Held a %s."},
	"vigil_skipped": {"memory": -3.0, "mercy": 0.0, "communion": -2.0, "dominion": 2.0,
		"text": "Set out with the dead unburied."},
	"wielder_died": {"memory": 2.0, "mercy": 0.0, "communion": 0.0, "dominion": -3.0,
		"text": "%s fell."},
	"successor_taken": {"memory": 0.0, "mercy": 0.0, "communion": 2.0, "dominion": 1.0,
		"text": "%s took up the blade."},
	"villager_conscripted": {"memory": -1.0, "mercy": -4.0, "communion": -3.0, "dominion": 5.0,
		"text": "Pulled %s from their work to fight."},
	"enemy_spared": {"memory": 0.0, "mercy": 6.0, "communion": 2.0, "dominion": -3.0,
		"text": "Walked past %s without drawing."},
	"enemy_slain": {"memory": 0.0, "mercy": -1.0, "communion": 0.0, "dominion": 2.0,
		"text": "Put down %s."},
	"relic_spent": {"memory": 5.0, "mercy": 0.0, "communion": 3.0, "dominion": 1.0,
		"text": "Spent a relic on stone that will outlast you."},
	"region_saved": {"memory": 4.0, "mercy": 7.0, "communion": 6.0, "dominion": 2.0,
		"text": "Pushed the decay back from %s."},
	"region_lost": {"memory": -4.0, "mercy": -7.0, "communion": -5.0, "dominion": -4.0,
		"text": "%s went to ash."},
	"ally_revived": {"memory": 2.0, "mercy": 8.0, "communion": 9.0, "dominion": -2.0,
		"text": "Lifted %s off the ground."},
	"ally_abandoned": {"memory": -2.0, "mercy": -8.0, "communion": -10.0, "dominion": 3.0,
		"text": "Left %s where they fell."},
	"echo_sent": {"memory": 3.0, "mercy": -2.0, "communion": 6.0, "dominion": 4.0,
		"text": "Sent the Echo of %s drifting into another settlement."},
	"foreign_echo_slain": {"memory": 1.0, "mercy": -3.0, "communion": 4.0, "dominion": 6.0,
		"text": "Put down a stranger's Echo: %s."},
	"foreign_echo_honoured": {"memory": 6.0, "mercy": 7.0, "communion": 9.0, "dominion": -1.0,
		"text": "Buried a stranger's Echo: %s."},
	"route_closed": {"memory": -1.0, "mercy": -2.0, "communion": -2.0, "dominion": -1.0,
		"text": "A road was closed by the Grey: %s."},
	"building_upgraded": {"memory": 1.0, "mercy": 2.0, "communion": 1.0, "dominion": 2.0,
		"text": "Raised the %s."},
	"cache_opened": {"memory": 1.0, "mercy": 0.0, "communion": 1.0, "dominion": 1.0,
		"text": "Opened a field cache: %s."},
}

## Endings resolve from axes plus hard gates. Checked in order; first match wins.
const ENDINGS := [
	{
		"id": "the_wake",
		"name": "The Wake",
		"requires": {"memory": 45.0, "communion": 40.0},
		"gate": "all_echoes_reclaimed",
		"text": "Every name was spoken, every Echo laid down. The settlement outlives its dead"
			+ " and remembers them without fear.",
	},
	{
		"id": "the_long_hold",
		"name": "The Long Hold",
		"requires": {"dominion": 50.0, "mercy": -20.0},
		"gate": "",
		"text": "You held the vale by force and buried nobody. The walls stand. Nobody inside"
			+ " remembers why they are worth holding.",
	},
	{
		"id": "ash_inheritance",
		"name": "Ash Inheritance",
		"requires": {"memory": -40.0},
		"gate": "",
		"text": "The lineage forgot itself. Your own Echo walks the fields now, and the"
			+ " villagers call it by your name because it is the only name they have left.",
	},
	{
		"id": "the_open_hearth",
		"name": "The Open Hearth",
		"requires": {"communion": 55.0, "mercy": 35.0},
		"gate": "",
		"text": "Strangers' Echoes were buried beside your own. Other settlements send"
			+ " travellers now. The valley is bigger than one lineage.",
	},
	{
		"id": "the_quiet_field",
		"name": "The Quiet Field",
		"requires": {},
		"gate": "",
		"text": "No triumph, no collapse. The work continued. Someone will pick up the blade"
			+ " tomorrow.",
	},
]

var axes: Dictionary = {"memory": 0.0, "mercy": 0.0, "communion": 0.0, "dominion": 0.0}
var entries: Array[Dictionary] = []
var locked_ending: String = ""

func reset() -> void:
	axes = {"memory": 0.0, "mercy": 0.0, "communion": 0.0, "dominion": 0.0}
	entries.clear()
	locked_ending = ""

## Records an action. `actor_id` identifies which player caused it, so a
## co-op session can attribute and replicate consequence fairly.
func record(action: String, subject: String = "", actor_id: String = "local",
		replicate: bool = true) -> Dictionary:
	var weights: Dictionary = ACTIONS.get(action, {})
	if weights.is_empty():
		push_warning("Chronicle: unknown action '%s'" % action)
		return {}
	# In a lobby the entry carries who caused it, so both worlds can attribute
	# the consequence rather than silently absorbing it.
	var author := actor_id
	if author == "local" and NetSession.is_networked():
		author = "%s:%d" % [NetSession.settlement_name, multiplayer.get_unique_id()]
	var entry := {
		"action": action,
		"subject": subject,
		"actor": author,
		"remote": false,
		"day": WorldState.world_day,
		"stamp": Time.get_unix_time_from_system(),
		"text": _format_text(String(weights["text"]), subject),
	}
	entries.append(entry)
	for axis: String in AXES:
		if not weights.has(axis):
			continue
		var shifted: float = clampf(float(axes[axis]) + float(weights[axis]),
				-AXIS_CLAMP, AXIS_CLAMP)
		if not is_equal_approx(shifted, float(axes[axis])):
			axes[axis] = shifted
			axis_shifted.emit(axis, shifted)
	recorded.emit(entry)
	if replicate and NetSession.is_networked():
		NetSession.broadcast_entry(entry)
	return entry

func _format_text(template: String, subject: String) -> String:
	if subject != "" and template.find("%s") >= 0:
		return template % subject
	return template

## Applies an entry received from a peer without re-broadcasting it.
func apply_remote(entry: Dictionary) -> void:
	var weights: Dictionary = ACTIONS.get(String(entry.get("action", "")), {})
	if weights.is_empty():
		return
	entry["remote"] = true
	entries.append(entry)
	for axis: String in AXES:
		if weights.has(axis):
			axes[axis] = clampf(float(axes[axis]) + float(weights[axis]),
					-AXIS_CLAMP, AXIS_CLAMP)
			axis_shifted.emit(axis, float(axes[axis]))
	recorded.emit(entry)

func axis(name: String) -> float:
	return float(axes.get(name, 0.0))

## Which ending the current ledger points at. Recomputed live so the player can
## feel the drift, not just discover it at the credits.
func projected_ending() -> Dictionary:
	for ending: Dictionary in ENDINGS:
		if _matches(ending):
			return ending
	return ENDINGS[-1]

func _matches(ending: Dictionary) -> bool:
	var requirements: Dictionary = ending["requires"]
	for axis_name: String in requirements:
		var needed := float(requirements[axis_name])
		var current := axis(axis_name)
		if needed >= 0.0 and current < needed:
			return false
		if needed < 0.0 and current > needed:
			return false
	return _gate_open(String(ending.get("gate", "")))

func _gate_open(gate: String) -> bool:
	match gate:
		"":
			return true
		"all_echoes_reclaimed":
			return WorldState.echoes.is_empty() and not WorldState.lineage.is_empty()
		_:
			return true

func lock_ending() -> Dictionary:
	var ending := projected_ending()
	locked_ending = String(ending["id"])
	ending_locked.emit(locked_ending)
	return ending

## Short human-readable drift, for the HUD and the settlement ledger board.
func summary_lines() -> PackedStringArray:
	var lines := PackedStringArray()
	for axis_name: String in AXES:
		var value := axis(axis_name)
		var pole: String = String(AXIS_LABELS[axis_name]).split(" vs ")[0 if value >= 0.0 else 1]
		lines.append("%s  %+d" % [pole, int(round(value))])
	lines.append("Drifting toward: %s" % projected_ending()["name"])
	return lines

func to_dict() -> Dictionary:
	return {"axes": axes, "entries": entries, "locked_ending": locked_ending}

func from_dict(data: Dictionary) -> void:
	axes = data.get("axes", axes)
	entries.clear()
	for entry: Variant in data.get("entries", []):
		if typeof(entry) == TYPE_DICTIONARY:
			entries.append(entry)
	locked_ending = String(data.get("locked_ending", ""))
