extends Node
## The persistent simulation: people, grief, legacies, echoes, world clock.
## This node is the save file. Combat and settlement scenes are views onto it.

signal grief_changed(value: int)
signal legacy_gained(text: String)
signal echo_tiered(echo: Dictionary)
signal wielder_changed(villager: Dictionary)
signal log_entry(text: String)
signal region_changed(region: String, old_decay: int, new_decay: int)

const SAVE_PATH := "user://soulstead_save.json"
const SAVE_VERSION := 2
const BASE_HP := 100.0
const BASE_COMPOSURE := 100.0
const BASE_FLASKS := 3
const ECHO_TIER_DAYS := 2
const ECHO_ROAM_TIER := 3
const ECHO_RAID_TIER := 5
const GRIEF_WORK_FLOOR := 0.35
const LOCATIONS := ["wrenfield", "grey_ash", "stonewake", "kettlemere", "brackwood", "vane_road", "iron_hollow", "ashen_marsh", "cinder_peak", "frostvale", "sunnyridge", "deepwood", "silverlake", "thornfield", "mistyvale", "emerald_grove", "crystal_caves", "sunken_ruins", "windy_plateau", "golden_desert", "icy_peaks", "volcanic_isles", "mushroom_forest", "ancient_library", "fishing_village", "oasis", "canyon", "glacier", "rainforest", "lavender_fields", "bamboo_grove", "coral_reef", "obsidian_shore", "sapphire_lake", "emerald_valley", "ruby_mine", "amethyst_cavern", "opal_spring", "topaz_town", "pearl_harbor", "jade_mount", "diamond_peak", "emerald_shore", "ivory_tower", "bronze_castle", "silver_forest", "golden_temple", "crystal_cave", "stone_circle", "iron_bridge", "stone_gate", "wooden_dock", "stone_wall", "iron_gate", "stone_dock", "wooden_wall", "iron_dock", "stone_bridge", "iron_wall", "wooden_bridge", "stone_wall", "wooden_gate", "iron_gate", "stone_dock", "wooden_wall", "iron_wall", "stone_gate", "wooden_wall", "iron_dock", "stone_wall", "wooden_gate", "iron_gate", "stone_wall", "wooden_dock", "stone_bridge", "iron_bridge", "stone_gate", "wooden_dock", "iron_bridge", "stone_wall", "wooden_dock", "iron_bridge", "stone_gate", "wooden_wall", "iron_bridge", "stone_wall", "wooden_gate", "iron_dock", "stone_wall", "wooden_gate", "iron_bridge", "stone_wall", "wooden_dock", "iron_gate", "stone_wall", "wooden_dock", "iron_bridge", "stone_wall", "wooden_gate", "iron_dock", "stone_wall", "wooden_gate", "iron_bridge", "stone_wall", "wooden_dock", "iron_wall", "stone_gate", "wooden_wall", "iron_dock", "stone_wall", "wooden_gate", "iron_bridge", "stone_wall", "wooden_dock", "iron_wall", "stone_wall", "wooden_wall", "iron_gate", "stone_dock", "wooden_dock", "iron_dock", "stone_bridge", "wooden_bridge", "iron_gate", "stone_wall", "wooden_wall", "iron_dock", "stone_gate", "wooden_wall", "iron_gate", "stone_dock", "wooden_dock", "iron_dock", "stone_bridge", "wooden_wall", "iron_dock", "stone_gate", "wooden_wall", "iron_gate", "stone_wall", "wooden_wall", "iron_dock", "stone_gate", "wooden_wall", "iron_dock", "stone_wall", "wooden_gate", "iron_wall", "stone_gate", "wooden_wall", "iron_dock", "stone_wall", "wooden_gate", "iron_bridge", "stone_wall", "wooden_dock", "iron_gate", "stone_wall", "wooden_dock", "iron_bridge"]
const LOCATION_NAMES := {
	"wrenfield": "Wrenfield",
	"grey_ash": "The Grey Ash",
	"stonewake": "Stonewake Scarp",
	"kettlemere": "Kettlemere",
	"brackwood": "Brackwood",
	"vane_road": "The Vane Road",
}
const FACTIONS := ["tellers", "unnaming", "hearthkeepers", "cull", "open_road", "long_hold", "gravewardens", "yielding"]

## The first Hold is not a bag of random stat rolls. These people are the
## named lives the Chronicle was written about. Random arrivals are still used
## after the founding roster, but the authored lineage always has a real body
## available to inherit it.
const CANON_PEOPLE := {
	"Oda Ashfall": {"age": 42, "job": "Healer", "traits": ["tender"], "vigour": 8, "strength": 6, "dexterity": 7, "resolve": 7},
	"Sila Carver": {"age": 27, "job": "Carver", "traits": ["steady"], "vigour": 7, "strength": 5, "dexterity": 8, "resolve": 8},
	"Bran Holt": {"age": 31, "job": "Carver", "traits": ["steady"], "vigour": 8, "strength": 6, "dexterity": 7, "resolve": 8},
	"Ketil Brack": {"age": 38, "job": "Smith", "traits": ["grim"], "vigour": 9, "strength": 9, "dexterity": 6, "resolve": 9},
	"Rin Ashfall": {"age": 19, "job": "Warden", "traits": ["reckless", "quick"], "vigour": 8, "strength": 9, "dexterity": 10, "resolve": 8},
	"Maren Verren": {"age": 24, "job": "Field-hand", "traits": ["steady", "scarred"], "vigour": 10, "strength": 10, "dexterity": 6, "resolve": 10},
	"Bel Brack": {"age": 11, "job": "Smith", "traits": ["tender"], "vigour": 5, "strength": 5, "dexterity": 7, "resolve": 5},
}

const CANON_SUCCESSORS := [
	{"fallen": "Rin Ashfall", "name": "Maren Verren", "bond": "spouse", "weapon": "widow_maul"},
	{"fallen": "Maren Verren", "name": "Colm Grey", "bond": "rival", "weapon": "reaper_pike"},
	{"fallen": "Colm Grey", "name": "Yeva Holt", "bond": "sibling", "weapon": "ashblade"},
	{"fallen": "Yeva Holt", "name": "Tarn Stonewake", "bond": "stranger", "weapon": "widow_maul"},
	{"fallen": "Tarn Stonewake", "name": "Sable Kettle", "bond": "friend", "weapon": "hearth_knife"},
	{"fallen": "Sable Kettle", "name": "Nix Ember", "bond": "rival", "weapon": "ashblade"},
	{"fallen": "Nix Ember", "name": "Orrin Dunn", "bond": "friend", "weapon": "reaper_pike"},
	{"fallen": "Orrin Dunn", "name": "Wren Ashfall", "bond": "spouse", "weapon": "ashblade"},
	{"fallen": "Wren Ashfall", "name": "Grieve Mourne", "bond": "friend", "weapon": "ashblade"},
]

var world_seed: int = 0
var world_day: float = 1.0
var grief: int = 0
var materials: Dictionary = {"timber": 12, "iron": 4, "relic": 0}
var inventory: Array[Dictionary] = []
var active_quest: Dictionary = {}
var completed_quests: Array[String] = []
var achievements: Array[String] = []
var settlement_events: Array[Dictionary] = []
var tutorial_completed: bool = false
var villagers: Array[Dictionary] = []
var lineage: Array[Dictionary] = []
var echoes: Array[Dictionary] = []
var legacies: Array[Dictionary] = []
var regions: Dictionary = {}
var faction_standing: Dictionary = {}
var current_location: String = "wrenfield"
var wielder_id: String = ""
var flasks_left: int = BASE_FLASKS
var run_active: bool = false
var story_director: StoryDirector
var buildings: Dictionary = {"hearth": 1, "memorial": 1, "smithy": 1, "fields": 1, "palisade": 1}
var weapon_upgrades: Dictionary = {}
var difficulty: String = "normal"  # easy, normal, hard

var _rng := RandomNumberGenerator.new()
var _next_id: int = 1

func _ready() -> void:
	if villagers.is_empty():
		new_game()

# --- Lifecycle -----------------------------------------------------------

func new_game(seed_value: int = 0) -> void:
	world_seed = seed_value if seed_value != 0 else randi()
	_rng.seed = world_seed
	_next_id = 1
	world_day = 1.0
	grief = 0
	materials = {"timber": 12, "iron": 4, "relic": 0}
	villagers.clear()
	lineage.clear()
	echoes.clear()
	legacies.clear()
	regions = {"vale": {"decay": 0}}
	for location: String in LOCATIONS:
		regions[location] = {"decay": 0}
	faction_standing = {}
	for faction: String in FACTIONS:
		faction_standing[faction] = 0
	current_location = "wrenfield"
	buildings = {"hearth": 1, "memorial": 1, "smithy": 1, "fields": 1, "palisade": 1}
	weapon_upgrades = {}
	for name: String in CANON_PEOPLE:
		villagers.append(_make_authored_villager(name, CANON_PEOPLE[name]))
	_seed_bonds()
	# The first playable hand is Rin. The prologue still teaches the player
	# about the Hold before the authored day-11 succession in the Chronicle.
	wielder_id = String(villager_by_name("Rin Ashfall")["id"])
	villager(wielder_id)["is_wielder"] = true
	flasks_left = max_flasks()
	run_active = false
	Chronicle.reset()
	if story_director != null:
		story_director.reset()
		story_director.process_day(world_day)
	grief_changed.emit(grief)
	wielder_changed.emit(wielder())

func _next_key(prefix: String) -> String:
	var key := "%s%d" % [prefix, _next_id]
	_next_id += 1
	return key

func _make_villager() -> Dictionary:
	var trait_ids: Array = Codex.TRAITS.keys()
	var picked: Array[String] = []
	picked.append(String(trait_ids[_rng.randi() % trait_ids.size()]))
	if _rng.randf() < 0.4:
		var second := String(trait_ids[_rng.randi() % trait_ids.size()])
		if second != picked[0]:
			picked.append(second)
	return {
		"id": _next_key("v"),
		"name": Codex.random_name(_rng),
		"age": _rng.randi_range(17, 54),
		"job": Codex.JOBS[_rng.randi() % Codex.JOBS.size()],
		"traits": picked,
		"vigour": _rng.randi_range(4, 12),
		"strength": _rng.randi_range(4, 12),
		"dexterity": _rng.randi_range(4, 12),
		"resolve": _rng.randi_range(4, 12),
		"bonds": {},
		"alive": true,
		"is_wielder": false,
		"weapon": "ashblade",
}

func _make_authored_villager(name: String, spec: Dictionary) -> Dictionary:
	return {
		"id": _next_key("v"),
		"name": name,
		"age": int(spec.get("age", 25)),
		"job": String(spec.get("job", "Field-hand")),
		"traits": Array(spec.get("traits", ["steady"])).duplicate(),
		"vigour": int(spec.get("vigour", 8)),
		"strength": int(spec.get("strength", 7)),
		"dexterity": int(spec.get("dexterity", 7)),
		"resolve": int(spec.get("resolve", 7)),
		"bonds": {},
		"alive": true,
		"is_wielder": false,
		"weapon": "ashblade",
	}

func villager_by_name(name: String) -> Dictionary:
	for person: Dictionary in villagers:
		if String(person.get("name", "")) == name:
			return person
	return {}

## Everyone gets a couple of relationships so succession has texture from turn one.
func _seed_bonds() -> void:
	# The relationships that make the authored lineage legible are explicit.
	# A small amount of incidental friendship remains so ordinary villagers do
	# not feel procedurally empty.
	var authored_bonds := [
		["Rin Ashfall", "Maren Verren", "spouse"],
		["Rin Ashfall", "Bran Holt", "friend"],
		["Maren Verren", "Ketil Brack", "friend"],
		["Sila Carver", "Bran Holt", "friend"],
		["Bel Brack", "Ketil Brack", "sibling"],
	]
	for bond: Array in authored_bonds:
		var a := villager_by_name(String(bond[0]))
		var b := villager_by_name(String(bond[1]))
		if a.is_empty() or b.is_empty():
			continue
		a["bonds"][b["id"]] = String(bond[2])
		b["bonds"][a["id"]] = String(bond[2])
	var kinds: Array = Codex.BONDS.keys()
	for person: Dictionary in villagers:
		for other: Dictionary in villagers:
			if other["id"] == person["id"] or person["bonds"].has(other["id"]):
				continue
			if _rng.randf() < 0.16:
				var kind := String(kinds[_rng.randi() % kinds.size()])
				person["bonds"][other["id"]] = kind
				other["bonds"][person["id"]] = kind

func villager(id: String) -> Dictionary:
	for person: Dictionary in villagers:
		if person["id"] == id:
			return person
	return {}

func wielder() -> Dictionary:
	return villager(wielder_id)

func living_villagers() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for person: Dictionary in villagers:
		if person["alive"]:
			out.append(person)
	return out

# --- Derived successor stats --------------------------------------------

func legacy_total(kind: String) -> float:
	var total := 0.0
	for entry: Dictionary in legacies:
		if entry["kind"] == kind:
			total += float(entry["value"])
	return total

func max_flasks() -> int:
	return BASE_FLASKS + int(legacy_total("flask"))

func wielder_stats() -> Dictionary:
	var person := wielder()
	if person.is_empty():
		return {"max_hp": BASE_HP, "max_composure": BASE_COMPOSURE, "power": 1.0,
			"composure_regen": 1.0, "weapon": "ashblade"}
	var bond_kind := String(person.get("bond_to_dead", "stranger"))
	var bond: Dictionary = Codex.bond(bond_kind)
	var composure := BASE_COMPOSURE + float(person["dexterity"]) * 3.0
	var resolve_mult := 1.0 + float(person["resolve"]) * 0.02
	for trait_id: String in person["traits"]:
		composure += float(Codex.trait_info(trait_id)["composure"])
		resolve_mult += float(Codex.trait_info(trait_id)["resolve"])
	composure *= float(bond["composure_mult"])
	resolve_mult *= float(bond["resolve_mult"])
	return {
		"max_hp": BASE_HP + float(person["vigour"]) * 6.0 + legacy_total("max_hp"),
		"max_composure": composure,
		"power": (1.0 + float(person["strength"]) * 0.04) * resolve_mult
				* (1.0 + legacy_total("power") + float(weapon_upgrades.get(String(person.get("weapon", "ashblade")), 0.0))),
		"composure_regen": 1.0 + legacy_total("composure_regen"),
			"weapon": String(person.get("weapon", "ashblade")),
			"bond": bond_kind,
		}

func bond_effect(bond_kind: String) -> Dictionary:
	match bond_kind:
		"spouse": return {"echo_damage_mult": 1.15, "echo_radius": 5.0}
		"sibling": return {"reclaim_free_legacy": true}
		"rival": return {"echo_aura_immune": true}
		"friend": return {"vigil_cost_mult": 0.8}
		"stranger": return {"settlement_grief_immune": true}
		_: return {}

# --- The death loop ------------------------------------------------------

## Called when the wielder dies in the field. Produces an Echo, grief, and a
## lineage record, then clears the wielder slot for succession.
func register_death(position: Vector3, region: String, killed_by: String) -> Dictionary:
	var person := wielder()
	if person.is_empty():
		return {}
	var fallen_stats := wielder_stats()
	person["alive"] = false
	person["is_wielder"] = false
	var bond_count: int = (person["bonds"] as Dictionary).size()
	var added: int = 10 + 3 * bond_count
	grief += added
	var record := {
		"id": person["id"],
		"name": person["name"],
		"died_day": int(world_day),
		"killed_by": killed_by,
		"region": region,
	}
	lineage.append(record)
	var echo := {
		"id": _next_key("e"),
		"owner": person["name"],
		"owner_id": person["id"],
		"tier": 1,
		"days_left": ECHO_TIER_DAYS,
		"pos": [position.x, position.z],
		"region": region,
		"weapon": String(person.get("weapon", "ashblade")),
		"power": fallen_stats["power"],
		"grief_held": added,
	}
	echoes.append(echo)
	wielder_id = ""
	run_active = false
	grief_changed.emit(grief)
	log_entry.emit("%s fell to %s on day %d." % [person["name"], killed_by, int(world_day)])
	Chronicle.record("wielder_died", String(person["name"]))
	if story_director != null:
		story_director.notify_event("first_death")
		story_director.notify_event("wielder_died", {"key": String(person["name"])})
		if String(person.get("name", "")) == "Wren Ashfall":
			story_director.notify_event("wren_death")
	return echo

## Three candidates, each annotated with their bond to the most recent death.
func succession_candidates() -> Array[Dictionary]:
	var pool := living_villagers()
	var dead_id := ""
	var dead_name := ""
	if not lineage.is_empty():
		for person: Dictionary in villagers:
			if not person["alive"] and person["name"] == lineage[-1]["name"]:
				dead_id = String(person["id"])
				dead_name = String(person["name"])
				break
	# Keep the authored successor visible when the current lineage follows the
	# novel. The player is still free to choose any other living person.
	var authored := _authored_successor_for(dead_name)
	if not authored.is_empty():
		_ensure_authored_person(String(authored["name"]), String(authored["bond"]))
		pool = living_villagers()
		pool.shuffle()
		var forced: Dictionary = villager_by_name(String(authored["name"]))
		pool.erase(forced)
		pool.push_front(forced)
	else:
		pool.shuffle()
	if pool.size() < 3 and lineage.size() > 0:
		while living_villagers().size() < 3:
			var arrival := _make_villager()
			villagers.append(arrival)
			pool.append(arrival)
			log_entry.emit("%s arrived at the settlement." % arrival["name"])
	var out: Array[Dictionary] = []
	for person: Dictionary in pool.slice(0, 3):
		var bond_kind := String((person["bonds"] as Dictionary).get(dead_id, "stranger"))
		person["bond_to_dead"] = bond_kind
		out.append(person)
	return out

func _authored_successor_for(fallen_name: String) -> Dictionary:
	for spec: Dictionary in CANON_SUCCESSORS:
		if String(spec["fallen"]) == fallen_name:
			return spec
	return {}

func _ensure_authored_person(name: String, bond_kind: String) -> Dictionary:
	var existing := villager_by_name(name)
	if not existing.is_empty():
		return existing
	var spec := {"age": 24, "job": "Field-hand", "traits": ["steady"], "vigour": 8,
		"strength": 8, "dexterity": 8, "resolve": 8}
	if name == "Maren Verren":
		spec = {"age": 26, "job": "Field-hand", "traits": ["steady", "scarred"], "vigour": 10, "strength": 10, "dexterity": 6, "resolve": 10}
	elif name == "Colm Grey":
		spec = {"age": 29, "job": "Warden", "traits": ["grim", "steady"], "vigour": 9, "strength": 10, "dexterity": 8, "resolve": 8}
	elif name == "Yeva Holt":
		spec = {"age": 23, "job": "Warden", "traits": ["quick", "tender"], "vigour": 8, "strength": 8, "dexterity": 10, "resolve": 8}
	elif name == "Tarn Stonewake":
		spec = {"age": 27, "job": "Forager", "traits": ["steady"], "vigour": 9, "strength": 8, "dexterity": 7, "resolve": 8}
	elif name == "Sable Kettle":
		spec = {"age": 24, "job": "Healer", "traits": ["quick", "tender"], "vigour": 8, "strength": 6, "dexterity": 11, "resolve": 8}
	elif name == "Nix Ember":
		spec = {"age": 26, "job": "Warden", "traits": ["reckless", "scarred"], "vigour": 9, "strength": 11, "dexterity": 8, "resolve": 9}
	elif name == "Orrin Dunn":
		spec = {"age": 30, "job": "Warden", "traits": ["steady", "grim"], "vigour": 10, "strength": 9, "dexterity": 7, "resolve": 10}
	elif name == "Wren Ashfall":
		spec = {"age": 30, "job": "Healer", "traits": ["scarred", "tender"], "vigour": 9, "strength": 8, "dexterity": 8, "resolve": 9}
	elif name == "Grieve Mourne":
		spec = {"age": 32, "job": "Carver", "traits": ["grim", "steady"], "vigour": 9, "strength": 6, "dexterity": 10, "resolve": 10}
	var person := _make_authored_villager(name, spec)
	villagers.append(person)
	var dead_id := String(lineage[-1].get("id", "")) if not lineage.is_empty() else ""
	if dead_id != "":
		person["bonds"][dead_id] = bond_kind
		var dead := villager(dead_id)
		if not dead.is_empty():
			dead["bonds"][person["id"]] = bond_kind
	log_entry.emit("%s is named among the living." % name)
	return person

func choose_successor(id: String) -> void:
	var person := villager(id)
	if person.is_empty():
		return
	for other: Dictionary in villagers:
		other["is_wielder"] = false
	person["is_wielder"] = true
	wielder_id = id
	var dead_id := String(lineage[-1].get("id", "")) if not lineage.is_empty() else ""
	person["bond_to_dead"] = String((person["bonds"] as Dictionary).get(dead_id, person.get("bond_to_dead", "stranger")))
	var authored := _authored_successor_for(String(lineage[-1].get("name", ""))) if not lineage.is_empty() else {}
	if not authored.is_empty() and String(person.get("name", "")) == String(authored["name"]):
		person["bond_to_dead"] = String(authored["bond"])
		person["weapon"] = String(authored["weapon"])
	flasks_left = max_flasks()
	wielder_changed.emit(person)
	log_entry.emit("%s takes up the blade." % person["name"])
	Chronicle.record("successor_taken", String(person["name"]))
	if story_director != null:
		story_director.notify_event("succession_complete")
		match String(person.get("name", "")):
			"Colm Grey": story_director.notify_event("colm_successor")
			"Yeva Holt": story_director.notify_event("yeva_successor")
			"Tarn Stonewake": story_director.notify_event("tarn_successor")
			"Sable Kettle": story_director.notify_event("sable_successor")
			"Wren Ashfall": story_director.notify_event("wren_successor")
			"Grieve Mourne": story_director.notify_event("grieve_successor")
	if grief > 0 and legacies.is_empty():
		Chronicle.record("vigil_skipped")

# --- Echoes --------------------------------------------------------------

func echoes_in(region: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for echo: Dictionary in echoes:
		if echo["region"] == region:
			out.append(echo)
	return out

func echo(id: String) -> Dictionary:
	for entry: Dictionary in echoes:
		if entry["id"] == id:
			return entry
	return {}

## Returns the enemy stat multiplier based on difficulty.
func difficulty_multiplier() -> float:
	match difficulty:
		"easy": return 0.75
		"hard": return 1.35
		_: return 1.0

## Time only passes while the player is out in the world.
func advance_time(days: float) -> void:
	if world_day >= 210.0:
		world_day = 210.0
		return
	days = minf(days, 210.0 - world_day)
	world_day += days
	for entry: Dictionary in echoes:
		entry["days_left"] = float(entry["days_left"]) - days
		while float(entry["days_left"]) <= 0.0 and int(entry["tier"]) < ECHO_RAID_TIER:
			entry["tier"] = int(entry["tier"]) + 1
			entry["days_left"] = float(entry["days_left"]) + ECHO_TIER_DAYS
			echo_tiered.emit(entry)
			log_entry.emit("The Echo of %s has grown (tier %d)."
					% [entry["owner"], int(entry["tier"])])
			if int(entry["tier"]) == ECHO_ROAM_TIER:
				_decay_region(String(entry["region"]), 1)
				Chronicle.record("echo_abandoned", String(entry["owner"]))
			if int(entry["tier"]) >= ECHO_RAID_TIER:
				Chronicle.record("echo_raided", String(entry["owner"]))
	if story_director != null:
		story_director.process_day(world_day)
	_simulate_settlement(days)

func _simulate_settlement(days: float) -> void:
	var multiplier := work_output_multiplier()
	var fields := int(buildings.get("fields", 1))
	var smithy := int(buildings.get("smithy", 1))
	var warden := int(buildings.get("palisade", 1))
	for person: Dictionary in living_villagers():
		if bool(person.get("conscripted", false)):
			if String(person.get("job", "")) == "Field-hand": fields -= 1
			if String(person.get("job", "")) == "Smith": smithy -= 1
			if String(person.get("job", "")) == "Warden": warden -= 1
	fields = maxi(0, fields)
	smithy = maxi(0, smithy)
	warden = maxi(0, warden)
	materials["timber"] = int(materials.get("timber", 0)) + int(round(days * 2.0 * fields * multiplier))
	materials["iron"] = int(materials.get("iron", 0)) + int(round(days * 0.6 * smithy * multiplier))
	# A stronger palisade absorbs part of the cost of decay pressure.
	if region_decay("wrenfield") >= 4 and warden < 3:
		log_entry.emit("The palisade is no longer enough for the Grey.")

## Start a new quest.
func start_quest(quest_id: String, title: String, objective: String) -> void:
	active_quest = {"id": quest_id, "title": title, "objective": objective, "progress": 0}
	Chronicle.record("quest_started", title)

## Update quest progress.
func update_quest_progress(amount: int = 1) -> void:
	if active_quest.is_empty():
		return
	active_quest["progress"] += amount

## Complete the active quest.
func complete_quest() -> void:
	if active_quest.is_empty():
		return
	completed_quests.append(active_quest["id"])
	Chronicle.record("quest_completed", active_quest["title"])
	active_quest = {}

## Check if a quest is completed.
func is_quest_completed(quest_id: String) -> bool:
	return completed_quests.has(quest_id)

## Add an item to the player's inventory.
func add_to_inventory(item_id: String, count: int = 1) -> void:
	# Check if item already exists
	for item in inventory:
		if item["id"] == item_id:
			item["count"] += count
			return
	inventory.append({"id": item_id, "count": count})

## Remove an item from the player's inventory.
func remove_from_inventory(item_id: String, count: int = 1) -> bool:
	for i in range(inventory.size()):
		if inventory[i]["id"] == item_id:
			inventory[i]["count"] -= count
			if inventory[i]["count"] <= 0:
				inventory.remove_at(i)
			return true
	return false

## Get the count of an item in the inventory.
func inventory_count(item_id: String) -> int:
	for item in inventory:
		if item["id"] == item_id:
			return item["count"]
	return 0

## Mark tutorial as completed.
func complete_tutorial() -> void:
	if not tutorial_completed:
		tutorial_completed = true
		Chronicle.record("tutorial_completed", "Player completed tutorial")

## Check if tutorial is completed.
func is_tutorial_completed() -> bool:
	return tutorial_completed

## Trigger a settlement event.
func trigger_settlement_event(event_id: String, description: String) -> void:
	settlement_events.append({"id": event_id, "description": description, "day": world_day})
	Chronicle.record("settlement_event", description)

## Get recent settlement events.
func get_recent_settlement_events(count: int = 5) -> Array[Dictionary]:
	if settlement_events.size() <= count:
		return settlement_events
	return settlement_events.slice(settlement_events.size() - count)

## Unlock an achievement.
func unlock_achievement(achievement_id: String) -> bool:
	if achievements.has(achievement_id):
		return false
	achievements.append(achievement_id)
	Chronicle.record("achievement", achievement_id)
	return true

## Check if an achievement is unlocked.
func has_achievement(achievement_id: String) -> bool:
	return achievements.has(achievement_id)

## Trade resources with a villager.
func trade(villager_id: String, give: Dictionary, receive: Dictionary) -> bool:
	# Check if we have enough resources to give
	for resource in give:
		if int(materials.get(resource, 0)) < int(give[resource]):
			return false
	# Deduct resources we give
	for resource in give:
		materials[resource] = int(materials.get(resource, 0)) - int(give[resource])
	# Add resources we receive
	for resource in receive:
		materials[resource] = int(materials.get(resource, 0)) + int(receive[resource])
	Chronicle.record("trade", "Traded with %s" % villager_id)
	return true

## Upgrade a settlement facility.
func upgrade_facility(id: String) -> bool:
	var cost := facility_upgrade_cost(id)
	# Check if we have enough resources
	for resource in cost:
		if int(materials.get(resource, 0)) < int(cost[resource]):
			return false
	# Deduct resources
	for resource in cost:
		materials[resource] = int(materials.get(resource, 0)) - int(cost[resource])
	# Upgrade the facility
	for facility in facilities:
		if facility["id"] == id:
			facility["level"] = int(facility.get("level", 1)) + 1
			break
	Chronicle.record("facility_upgraded", "%s -> level %d" % [id, facility["level"]])
	return true

func facility_upgrade_cost(id: String) -> Dictionary:
	var level := int(buildings.get(id, 1))
	if level >= 3:
		return {}
	match id:
		"smithy": return {"timber": 8 + level * 4, "iron": 3 + level * 2, "relic": 1}
		"fields": return {"timber": 10 + level * 5, "iron": 2 + level, "relic": 0}
		"palisade": return {"timber": 12 + level * 6, "iron": 4 + level * 2, "relic": 0}
		_: return {}

func can_upgrade_facility(id: String) -> bool:
	var cost := facility_upgrade_cost(id)
	if cost.is_empty():
		return false
	for resource: String in cost:
		if int(materials.get(resource, 0)) < int(cost[resource]):
			return false
	return true

func upgrade_facility(id: String) -> bool:
	if not can_upgrade_facility(id):
		return false
	var cost := facility_upgrade_cost(id)
	for resource: String in cost:
		materials[resource] = int(materials.get(resource, 0)) - int(cost[resource])
	buildings[id] = int(buildings.get(id, 1)) + 1
	if id == "smithy":
		var weapon_id := String(wielder().get("weapon", "ashblade"))
		weapon_upgrades[weapon_id] = float(weapon_upgrades.get(weapon_id, 0.0)) + 0.04
	Chronicle.record("building_upgraded", id)
	log_entry.emit("The %s rises to level %d." % [id.capitalize(), int(buildings[id])])
	return true

func reclaim_echo(id: String) -> void:
	var entry := echo(id)
	if entry.is_empty():
		return
	var current := wielder()
	var bond_kind := String(current.get("bond_to_dead", "stranger")) if not current.is_empty() else "stranger"
	grief = maxi(0, grief - int(entry["grief_held"]))
	materials["relic"] = int(materials.get("relic", 0)) + 1
	echoes.erase(entry)
	if bond_kind == "sibling" and String(entry.get("owner_id", "")) == String(lineage[-1].get("id", "")):
		legacies.append({"kind": "max_hp", "value": 6.0, "from": "Blood of the fallen"})
		legacy_gained.emit("Blood of the fallen: the reclaimed life strengthens every successor.")
		faction_delta("tellers", 4)
	grief_changed.emit(grief)
	log_entry.emit("The Echo of %s was reclaimed. A relic remains." % entry["owner"])
	Chronicle.record("echo_reclaimed", String(entry["owner"]))
	if story_director != null:
		story_director.notify_event("echo_reclaimed")
		story_director.notify_event("relic_acquired")

func pending_raid() -> Dictionary:
	for entry: Dictionary in echoes:
		if int(entry["tier"]) >= ECHO_RAID_TIER:
			return entry
	return {}

func _decay_region(region: String, amount: int) -> void:
	if not regions.has(region):
		regions[region] = {"decay": 0}
	var old := int(regions[region]["decay"])
	var next := clampi(old + amount, 0, 4)
	regions[region]["decay"] = next
	if next != old:
		region_changed.emit(region, old, next)
		log_entry.emit("%s becomes %s." % [location_name(region), decay_name(next)])
		if next == 4:
			Chronicle.record("region_lost", location_name(region))
			if story_director != null and region == "wrenfield":
				story_director.notify_event("wrenfield_gone")

func restore_region(region: String, amount: int = 1) -> bool:
	if not regions.has(region) or amount <= 0:
		return false
	var old := region_decay(region)
	var next := maxi(0, old - amount)
	if next == old:
		return false
	regions[region]["decay"] = next
	region_changed.emit(region, old, next)
	log_entry.emit("The Grey withdraws from %s. The ground is %s again." % [location_name(region), decay_name(next)])
	Chronicle.record("region_saved", location_name(region))
	if story_director != null:
		story_director.notify_event("region_saved")
	return true

func decay_name(value: int) -> String:
	return ["Quick", "Turning", "Greying", "Ashen", "Gone"][clampi(value, 0, 4)]

func location_name(region: String) -> String:
	return String(LOCATION_NAMES.get(region, region.capitalize()))

func available_locations() -> Array[String]:
	var out: Array[String] = []
	for location: String in LOCATIONS:
		if location == "vane_road" and region_decay("wrenfield") >= 4:
			continue
		if location == "kettlemere" and region_decay("stonewake") >= 4:
			continue
		if location == "brackwood" and region_decay("wrenfield") >= 4:
			continue
		out.append(location)
	return out

func set_expedition_location(location: String) -> bool:
	if not available_locations().has(location):
		return false
	current_location = location
	return true

func faction_delta(faction: String, amount: int) -> void:
	if not faction_standing.has(faction):
		return
	faction_standing[faction] = clampi(int(faction_standing[faction]) + amount, -100, 100)

func conscript_villager(id: String) -> bool:
	var person := villager(id)
	if person.is_empty() or not bool(person.get("alive", false)) or bool(person.get("conscripted", false)):
		return false
	person["conscripted"] = true
	Chronicle.record("villager_conscripted", String(person["name"]))
	faction_delta("cull", 8)
	faction_delta("hearthkeepers", -6)
	return true

func region_decay(region: String) -> int:
	return int(regions.get(region, {"decay": 0})["decay"])

# --- Grief and vigils ----------------------------------------------------

func work_output_multiplier() -> float:
	return clampf(1.0 - float(grief) / 200.0, GRIEF_WORK_FLOOR, 1.0)

func can_perform_vigil(id: String) -> bool:
	var data: Dictionary = Codex.vigil(id)
	if data.is_empty():
		return false
	var cost_mult := 1.0
	var wielder_data := wielder()
	if not wielder_data.is_empty():
		cost_mult = float(bond_effect(String(wielder_data.get("bond_to_dead", "stranger"))).get("vigil_cost_mult", 1.0))
	var grief_cost := int(ceil(float(data["grief"]) * cost_mult))
	if grief < grief_cost:
		return false
	return int(materials.get("relic", 0)) >= int(data.get("relic", 0))

func perform_vigil(id: String) -> bool:
	if not can_perform_vigil(id):
		return false
	var data: Dictionary = Codex.vigil(id)
	var cost_mult := 1.0
	var wielder_data := wielder()
	if not wielder_data.is_empty():
		cost_mult = float(bond_effect(String(wielder_data.get("bond_to_dead", "stranger"))).get("vigil_cost_mult", 1.0))
	grief -= int(ceil(float(data["grief"]) * cost_mult))
	materials["relic"] = int(materials.get("relic", 0)) - int(data.get("relic", 0))
	if bool(data.get("clears_grief", false)):
		grief = 0
	var gained: Dictionary = data["legacy"]
	legacies.append({"kind": gained["kind"], "value": gained["value"], "from": data["name"]})
	flasks_left = max_flasks()
	grief_changed.emit(grief)
	legacy_gained.emit("%s: %s" % [data["name"], data["desc"]])
	log_entry.emit("A %s was held. The lineage remembers." % String(data["name"]).to_lower())
	Chronicle.record("vigil_held", String(data["name"]))
	if story_director != null:
		story_director.notify_event("first_vigil")
	var bond_kind := String(wielder_data.get("bond_to_dead", "stranger")) if not wielder_data.is_empty() else "stranger"
	if bond_kind == "friend":
		faction_delta("hearthkeepers", 4)
	if int(data.get("relic", 0)) > 0:
		Chronicle.record("relic_spent")
	return true

# --- Persistence ---------------------------------------------------------

func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)

func save_game() -> bool:
	var payload := {
		"version": SAVE_VERSION,
		"world_seed": world_seed,
		"world_day": world_day,
		"grief": grief,
		"materials": materials,
		"villagers": villagers,
		"lineage": lineage,
		"echoes": echoes,
		"legacies": legacies,
		"regions": regions,
		"faction_standing": faction_standing,
		"current_location": current_location,
		"wielder_id": wielder_id,
		"flasks_left": flasks_left,
		"next_id": _next_id,
		"buildings": buildings,
		"weapon_upgrades": weapon_upgrades,
		"story": story_director.to_dict() if story_director != null else {},
		"chronicle": Chronicle.to_dict(),
	}
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_error("Save failed: %s" % error_string(FileAccess.get_open_error()))
		return false
	file.store_string(JSON.stringify(payload, "\t"))
	file.close()
	return true

func load_game() -> bool:
	if not has_save():
		return false
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		return false
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Save file is corrupt; starting fresh.")
		return false
	var data: Dictionary = parsed
	world_seed = int(data.get("world_seed", randi()))
	_rng.seed = world_seed
	world_day = float(data.get("world_day", 1.0))
	grief = int(data.get("grief", 0))
	materials = data.get("materials", {"timber": 0, "iron": 0, "relic": 0})
	villagers = _typed(data.get("villagers", []))
	lineage = _typed(data.get("lineage", []))
	echoes = _typed(data.get("echoes", []))
	legacies = _typed(data.get("legacies", []))
	regions = data.get("regions", {"vale": {"decay": 0}})
	for location: String in LOCATIONS:
		if not regions.has(location):
			regions[location] = {"decay": 0}
	faction_standing = data.get("faction_standing", {})
	for faction: String in FACTIONS:
		if not faction_standing.has(faction):
			faction_standing[faction] = 0
	current_location = String(data.get("current_location", "wrenfield"))
	wielder_id = String(data.get("wielder_id", ""))
	flasks_left = int(data.get("flasks_left", BASE_FLASKS))
	_next_id = int(data.get("next_id", villagers.size() + echoes.size() + 1))
	buildings = data.get("buildings", {"hearth": 1, "memorial": 1, "smithy": 1, "fields": 1, "palisade": 1})
	weapon_upgrades = data.get("weapon_upgrades", {})
	Chronicle.from_dict(data.get("chronicle", {}))
	if story_director != null:
		story_director.hydrate(data.get("story", {}))
		story_director.process_day(world_day)
	grief_changed.emit(grief)
	wielder_changed.emit(wielder())
	return true

func _typed(source: Array) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for entry: Variant in source:
		if typeof(entry) == TYPE_DICTIONARY:
			out.append(entry)
	return out

func delete_save() -> void:
	if has_save():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
