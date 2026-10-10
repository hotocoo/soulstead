extends Node
## Static game data for SOULSTEAD. Plain dictionaries, one balance surface.

# --- Weapons -------------------------------------------------------------
# motion values are multipliers on weapon power; windows are in seconds.

const WEAPONS := {
	"ashblade": {
		"name": "Ashblade", "power": 16.0, "reach": 2.4, "arc": 1.4,
		"light": {"startup": 0.10, "active": 0.10, "recovery": 0.20, "cost": 12.0, "motion": 1.0, "poise": 14.0},
		"heavy": {"startup": 0.28, "active": 0.14, "recovery": 0.38, "cost": 26.0, "motion": 1.9, "poise": 34.0},
	},
	"reaper_pike": {
		"name": "Reaper Pike", "power": 13.0, "reach": 3.6, "arc": 0.6,
		"light": {"startup": 0.14, "active": 0.09, "recovery": 0.24, "cost": 13.0, "motion": 1.0, "poise": 10.0},
		"heavy": {"startup": 0.34, "active": 0.12, "recovery": 0.40, "cost": 28.0, "motion": 2.0, "poise": 26.0},
	},
	"widow_maul": {
		"name": "Widow's Maul", "power": 24.0, "reach": 2.2, "arc": 1.9,
		"light": {"startup": 0.20, "active": 0.12, "recovery": 0.32, "cost": 20.0, "motion": 1.0, "poise": 26.0},
		"heavy": {"startup": 0.46, "active": 0.16, "recovery": 0.52, "cost": 36.0, "motion": 2.3, "poise": 60.0},
	},
	"hearth_knife": {
		"name": "Hearth Knife", "power": 9.0, "reach": 1.6, "arc": 1.2,
		"light": {"startup": 0.06, "active": 0.08, "recovery": 0.14, "cost": 8.0, "motion": 1.0, "poise": 6.0},
		"heavy": {"startup": 0.18, "active": 0.10, "recovery": 0.26, "cost": 18.0, "motion": 1.6, "poise": 16.0},
	},
	"oathbreaker": {
		"name": "Oathbreaker", "power": 32.0, "reach": 2.8, "arc": 2.2,
		"light": {"startup": 0.24, "active": 0.14, "recovery": 0.36, "cost": 24.0, "motion": 1.0, "poise": 32.0},
		"heavy": {"startup": 0.52, "active": 0.18, "recovery": 0.58, "cost": 40.0, "motion": 2.6, "poise": 72.0},
	},
	"twin_cinders": {
		"name": "Twin Cinders", "power": 7.0, "reach": 1.5, "arc": 1.5,
		"light": {"startup": 0.05, "active": 0.07, "recovery": 0.12, "cost": 7.0, "motion": 1.0, "poise": 5.0},
		"heavy": {"startup": 0.16, "active": 0.09, "recovery": 0.22, "cost": 15.0, "motion": 1.5, "poise": 12.0},
	},
}

# --- Enemies -------------------------------------------------------------
# `tell` is the wind-up time during which the enemy flashes before committing.

const ENEMIES := {
	"husk": {
		"name": "Ash Husk", "hp": 46.0, "damage": 9.0, "poise": 20.0, "speed": 2.4,
		"tell": 0.45, "reach": 2.0, "color": Color("#7c6f66"), "shape": "humanoid",
		"size": 16, "aggro": 14.0, "posture": "shambler", "relics": 0,
	},
	"stalker": {
		"name": "Cinder Stalker", "hp": 34.0, "damage": 12.0, "poise": 12.0, "speed": 4.2,
		"tell": 0.26, "reach": 1.9, "color": Color("#a4462f"), "shape": "beast",
		"size": 15, "aggro": 18.0, "posture": "darter", "relics": 0,
	},
	"villager": {
		"name": "Villager", "hp": 40.0, "damage": 8.0, "poise": 25.0, "speed": 3.5,
		"tell": 0.3, "reach": 1.8, "color": Color("#7a8b6f"), "shape": "humanoid",
		"size": 16, "aggro": 12.0, "posture": "shambler", "relics": 0,
	},
	"warden": {
		"name": "Gravewarden", "hp": 90.0, "damage": 18.0, "poise": 55.0, "speed": 2.2,
		"tell": 0.62, "reach": 2.7, "color": Color("#4d5a6b"), "shape": "humanoid",
		"size": 22, "aggro": 15.0, "posture": "bulwark", "relics": 1,
	},
	"wraith": {
		"name": "Ash Wraith", "hp": 28.0, "damage": 14.0, "poise": 8.0, "speed": 5.0,
		"tell": 0.18, "reach": 1.7, "color": Color("#9a8fb8"), "shape": "humanoid",
		"size": 14, "aggro": 20.0, "posture": "darter", "relics": 0,
	},
	"brute": {
		"name": "Cinder Brute", "hp": 120.0, "damage": 22.0, "poise": 70.0, "speed": 1.8,
		"tell": 0.75, "reach": 3.0, "color": Color("#8b4513"), "shape": "humanoid",
		"size": 24, "aggro": 12.0, "posture": "bulwark", "relics": 2,
	},
	"ember_slinger": {
		"name": "Ember Slinger", "hp": 35.0, "damage": 10.0, "poise": 10.0, "speed": 3.0,
		"tell": 0.5, "reach": 8.0, "color": Color("#b87333"), "shape": "humanoid",
		"size": 15, "aggro": 20.0, "posture": "skirmisher", "relics": 0,
	},
	"ash_king": {
		"name": "The Ash King", "hp": 500.0, "damage": 40.0, "poise": 150.0, "speed": 2.0,
		"tell": 0.8, "reach": 3.5, "color": Color("#4a3a2a"), "shape": "humanoid",
		"size": 35, "aggro": 25.0, "posture": "bulwark", "relics": 5,
	},
	"keeper": {
		"name": "The Keeper", "hp": 200.0, "damage": 28.0, "poise": 100.0, "speed": 1.4,
		"tell": 0.9, "reach": 3.4, "color": Color("#2a2a3a"), "shape": "humanoid",
		"size": 28, "aggro": 16.0, "posture": "bulwark", "relics": 3,
	},
}

# --- Settlement people ---------------------------------------------------

const JOBS := ["Field-hand", "Smith", "Forager", "Warden", "Healer", "Carver"]

const TRAITS := {
	"steady": {"name": "Steady", "composure": 12.0, "resolve": 0.0, "desc": "Hands do not shake."},
	"reckless": {"name": "Reckless", "composure": -8.0, "resolve": 0.15, "desc": "Swings first."},
	"scarred": {"name": "Scarred", "composure": 0.0, "resolve": 0.10, "desc": "Has survived worse."},
	"tender": {"name": "Tender", "composure": 6.0, "resolve": -0.05, "desc": "Heals faster at the Hearth."},
	"grim": {"name": "Grim", "composure": 4.0, "resolve": 0.05, "desc": "Grief lands lighter."},
	"quick": {"name": "Quick", "composure": 10.0, "resolve": -0.05, "desc": "Rolls come cheap."},
}

## Bond to the deceased shapes the successor. See docs/DESIGN.md section 3.
const BONDS := {
	"spouse": {"name": "Spouse", "composure_mult": 0.85, "resolve_mult": 1.25,
		"line": "They shared a roof with the dead."},
	"sibling": {"name": "Sibling", "composure_mult": 0.95, "resolve_mult": 1.10,
		"line": "Blood of the fallen."},
	"rival": {"name": "Rival", "composure_mult": 1.10, "resolve_mult": 0.90,
		"line": "Never liked them. Will still carry the blade."},
	"friend": {"name": "Friend", "composure_mult": 1.0, "resolve_mult": 1.05,
		"line": "Drank with the dead most nights."},
	"stranger": {"name": "Stranger", "composure_mult": 1.15, "resolve_mult": 0.80,
		"line": "Never learned their name."},
}

# --- Vigils --------------------------------------------------------------

const VIGILS := {
	"burial": {"name": "Burial", "grief": 20, "relic": 0,
		"desc": "+6 max health for every successor after this one.",
		"legacy": {"kind": "max_hp", "value": 6.0}},
	"pyre": {"name": "Pyre", "grief": 30, "relic": 0,
		"desc": "Burn their gear. +1 Ash Flask charge.",
		"legacy": {"kind": "flask", "value": 1.0}},
	"telling": {"name": "Telling", "grief": 25, "relic": 0,
		"desc": "Recount the death aloud. +8% Composure regeneration.",
		"legacy": {"kind": "composure_regen", "value": 0.08}},
	"monument": {"name": "Monument", "grief": 40, "relic": 1,
		"desc": "Raise stone over a reclaimed Echo. +10% weapon power.",
		"legacy": {"kind": "power", "value": 0.10}},
	"wake": {"name": "Wake", "grief": 60, "relic": 0,
		"desc": "The whole settlement drinks. Clears all grief, +5% damage.",
		"legacy": {"kind": "power", "value": 0.05}, "clears_grief": true},
}

# --- Names ---------------------------------------------------------------

const GIVEN := ["Rin", "Sable", "Oda", "Maren", "Colm", "Yeva", "Tarn", "Bel", "Halde",
	"Nix", "Orrin", "Sila", "Grieve", "Wren", "Tove", "Ketil", "Asha", "Bran"]
const FAMILY := ["Ashfall", "Grey", "Holt", "Verren", "Stonewake", "Ember", "Dunn",
	"Mourne", "Kettle", "Vane", "Brack", "Rowan"]

static func random_name(rng: RandomNumberGenerator) -> String:
	return "%s %s" % [GIVEN[rng.randi() % GIVEN.size()], FAMILY[rng.randi() % FAMILY.size()]]

func weapon(id: String) -> Dictionary:
	return WEAPONS.get(id, WEAPONS["ashblade"])

func enemy(id: String) -> Dictionary:
	return ENEMIES.get(id, ENEMIES["husk"])

func vigil(id: String) -> Dictionary:
	return VIGILS.get(id, {})

func bond(id: String) -> Dictionary:
	return BONDS.get(id, BONDS["stranger"])

func trait_info(id: String) -> Dictionary:
	return TRAITS.get(id, {"name": id, "composure": 0.0, "resolve": 0.0, "desc": ""})
