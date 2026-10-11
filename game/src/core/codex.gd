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
	"long_spear": {
		"name": "Long Spear", "power": 14.0, "windup": 0.25, "active": 0.15, "recovery": 0.55,
		"reach": 5.5, "arc": 0.5, "heavy_ratio": 1.6, "color": Color("#9e8c68"), "shape": "spear",
	},
	"short_sword": {
		"name": "Short Sword", "power": 8.0, "windup": 0.2, "active": 0.08, "recovery": 0.15,
		"reach": 1.5, "arc": 0.8, "heavy_ratio": 1.2, "color": Color("#aaaaaa"), "shape": "short_sword",
	},
	"greatsword": {
		"name": "Greatsword", "power": 18.0, "windup": 0.45, "active": 0.12, "recovery": 0.35,
		"reach": 2.8, "arc": 1.0, "heavy_ratio": 1.5, "color": Color("#999999"), "shape": "greatsword",
	},
	"broadsword": {
		"name": "Broadsword", "power": 14.0, "windup": 0.35, "active": 0.1, "recovery": 0.28,
		"reach": 2.4, "arc": 0.9, "heavy_ratio": 1.4, "color": Color("#aaaaaa"), "shape": "broadsword",
	},
	"warhammer": {
		"name": "Warhammer", "power": 16.0, "windup": 0.4, "active": 0.1, "recovery": 0.32,
		"reach": 2.2, "arc": 0.7, "heavy_ratio": 1.6, "color": Color("#888888"), "shape": "warhammer",
	},
	"mace": {
		"name": "Mace", "power": 12.0, "windup": 0.3, "active": 0.08, "recovery": 0.22,
		"reach": 1.8, "arc": 0.6, "heavy_ratio": 1.3, "color": Color("#aaaaaa"), "shape": "mace",
	},
	"flail": {
		"name": "Flail", "power": 14.0, "windup": 0.35, "active": 0.1, "recovery": 0.28,
		"reach": 2.0, "arc": 0.8, "heavy_ratio": 1.4, "color": Color("#999999"), "shape": "flail",
	},
	"morning_star": {
		"name": "Morning Star", "power": 13.0, "windup": 0.32, "active": 0.09, "recovery": 0.25,
		"reach": 2.0, "arc": 0.7, "heavy_ratio": 1.35, "color": Color("#aaaaaa"), "shape": "morning_star",
	},
	"halberd": {
		"name": "Halberd", "power": 18.0, "windup": 0.42, "active": 0.12, "recovery": 0.32,
		"reach": 3.5, "arc": 0.9, "heavy_ratio": 1.5, "color": Color("#888888"), "shape": "halberd",
	},
	"glaive": {
		"name": "Glaive", "power": 16.0, "windup": 0.38, "active": 0.11, "recovery": 0.3,
		"reach": 3.2, "arc": 0.8, "heavy_ratio": 1.45, "color": Color("#999999"), "shape": "glaive",
	},
	"spear": {
		"name": "Spear", "power": 14.0, "windup": 0.3, "active": 0.08, "recovery": 0.22,
		"reach": 3.0, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#aaaaaa"), "shape": "spear",
	},
	"bow": {
		"name": "Bow", "power": 12.0, "windup": 0.35, "active": 0.05, "recovery": 0.25,
		"reach": 12.0, "arc": 0.4, "heavy_ratio": 1.0, "color": Color("#8a8a8a"), "shape": "bow",
	},
	"shortbow": {
		"name": "Shortbow", "power": 8.0, "windup": 0.25, "active": 0.05, "recovery": 0.18,
		"reach": 10.0, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "shortbow",
	},
	"torch": {
		"name": "Torch", "power": 6.0, "windup": 0.2, "active": 0.08, "recovery": 0.15,
		"reach": 1.8, "arc": 0.6, "heavy_ratio": 1.0, "color": Color("#ff8844"), "shape": "torch",
	},
	"lantern": {
		"name": "Lantern", "power": 4.0, "windup": 0.15, "active": 0.05, "recovery": 0.12,
		"reach": 1.5, "arc": 0.5, "heavy_ratio": 1.0, "color": Color("#ffcc44"), "shape": "lantern",
	},
	"boomerang": {
		"name": "Boomerang", "power": 8.0, "windup": 0.25, "active": 0.08, "recovery": 0.2,
		"reach": 6.0, "arc": 0.5, "heavy_ratio": 1.0, "color": Color("#8a8a8a"), "shape": "boomerang",
	},
	"throwing_knife": {
		"name": "Throwing Knife", "power": 7.0, "windup": 0.15, "active": 0.05, "recovery": 0.15,
		"reach": 5.0, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "throwing_knife",
	},
	"crossbow": {
		"name": "Crossbow", "power": 10.0, "windup": 0.4, "active": 0.05, "recovery": 0.3,
		"reach": 10.0, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#8a8a8a"), "shape": "crossbow",
	},
	"slingshot": {
		"name": "Slingshot", "power": 6.0, "windup": 0.2, "active": 0.05, "recovery": 0.15,
		"reach": 8.0, "arc": 0.2, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "slingshot",
	},
	"spear": {
		"name": "Spear", "power": 14.0, "windup": 0.35, "active": 0.1, "recovery": 0.25,
		"reach": 3.0, "arc": 0.4, "heavy_ratio": 1.3, "color": Color("#8a8a8a"), "shape": "spear",
	},
	"trident": {
		"name": "Trident", "power": 15.0, "windup": 0.4, "active": 0.1, "recovery": 0.3,
		"reach": 3.0, "arc": 0.5, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "trident",
	},
	"halberd": {
		"name": "Halberd", "power": 18.0, "windup": 0.45, "active": 0.12, "recovery": 0.35,
		"reach": 3.5, "arc": 0.9, "heavy_ratio": 1.6, "color": Color("#8a8a8a"), "shape": "halberd",
	},
	"glaive": {
		"name": "Glaive", "power": 15.0, "windup": 0.4, "active": 0.1, "recovery": 0.3,
		"reach": 3.0, "arc": 0.8, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "glaive",
	},
	"warhammer": {
		"name": "Warhammer", "power": 16.0, "windup": 0.4, "active": 0.1, "recovery": 0.3,
		"reach": 2.2, "arc": 0.7, "heavy_ratio": 1.5, "color": Color("#8a8a8a"), "shape": "warhammer",
	},
	"morning_star": {
		"name": "Morning Star", "power": 13.0, "windup": 0.35, "active": 0.09, "recovery": 0.25,
		"reach": 2.0, "arc": 0.6, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "morning_star",
	},
	"mace": {
		"name": "Mace", "power": 12.0, "windup": 0.3, "active": 0.08, "recovery": 0.2,
		"reach": 1.8, "arc": 0.6, "heavy_ratio": 1.2, "color": Color("#8a8a8a"), "shape": "mace",
	},
	"flail": {
		"name": "Flail", "power": 14.0, "windup": 0.35, "active": 0.1, "recovery": 0.25,
		"reach": 2.0, "arc": 0.8, "heavy_ratio": 1.3, "color": Color("#7a7a7a"), "shape": "flail",
	},
	"greatsword": {
		"name": "Greatsword", "power": 18.0, "windup": 0.5, "active": 0.12, "recovery": 0.4,
		"reach": 2.8, "arc": 1.2, "heavy_ratio": 1.8, "color": Color("#8a8a8a"), "shape": "greatsword",
	},
	"broadsword": {
		"name": "Broadsword", "power": 14.0, "windup": 0.4, "active": 0.1, "recovery": 0.3,
		"reach": 2.4, "arc": 1.0, "heavy_ratio": 1.5, "color": Color("#7a7a7a"), "shape": "broadsword",
	},
	"dagger": {
		"name": "Dagger", "power": 5.0, "windup": 0.1, "active": 0.04, "recovery": 0.08,
		"reach": 1.2, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#8a8a8a"), "shape": "dagger",
	},
	"short_sword": {
		"name": "Short Sword", "power": 8.0, "windup": 0.15, "active": 0.06, "recovery": 0.12,
		"reach": 1.5, "arc": 0.4, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "short_sword",
	},
	"bow": {
		"name": "Bow", "power": 12.0, "windup": 0.4, "active": 0.05, "recovery": 0.25,
		"reach": 12.0, "arc": 0.1, "heavy_ratio": 1.0, "color": Color("#8a7a5a"), "shape": "bow",
	},
	"shortbow": {
		"name": "Shortbow", "power": 8.0, "windup": 0.3, "active": 0.04, "recovery": 0.18,
		"reach": 10.0, "arc": 0.1, "heavy_ratio": 1.0, "color": Color("#7a7a5a"), "shape": "shortbow",
	},
	"torch": {
		"name": "Torch", "power": 6.0, "windup": 0.15, "active": 0.08, "recovery": 0.1,
		"reach": 1.5, "arc": 0.5, "heavy_ratio": 1.0, "color": Color("#8a6a4a"), "shape": "torch",
	},
	"lantern": {
		"name": "Lantern", "power": 4.0, "windup": 0.1, "active": 0.05, "recovery": 0.08,
		"reach": 1.2, "arc": 0.4, "heavy_ratio": 1.0, "color": Color("#9a8a6a"), "shape": "lantern",
	},
	"boomerang": {
		"name": "Boomerang", "power": 8.0, "windup": 0.3, "active": 0.05, "recovery": 0.2,
		"reach": 6.0, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#8a7a5a"), "shape": "boomerang",
	},
	"throwing_knife": {
		"name": "Throwing Knife", "power": 7.0, "windup": 0.2, "active": 0.03, "recovery": 0.15,
		"reach": 7.0, "arc": 0.2, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "throwing_knife",
	},
	"crossbow": {
		"name": "Crossbow", "power": 14.0, "windup": 0.5, "active": 0.05, "recovery": 0.3,
		"reach": 10.0, "arc": 0.1, "heavy_ratio": 1.0, "color": Color("#8a7a6a"), "shape": "crossbow",
	},
	"slingshot": {
		"name": "Slingshot", "power": 6.0, "windup": 0.2, "active": 0.03, "recovery": 0.15,
		"reach": 8.0, "arc": 0.1, "heavy_ratio": 1.0, "color": Color("#7a7a6a"), "shape": "slingshot",
	},
	"mace": {
		"name": "Mace", "power": 12.0, "windup": 0.18, "active": 0.06, "recovery": 0.22,
		"reach": 1.6, "arc": 0.7, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "mace",
	},
	"war_hammer": {
		"name": "War Hammer", "power": 16.0, "windup": 0.25, "active": 0.08, "recovery": 0.3,
		"reach": 1.8, "arc": 0.7, "heavy_ratio": 1.2, "color": Color("#8a8a8a"), "shape": "war_hammer",
	},
	"spear": {
		"name": "Spear", "power": 12.0, "windup": 0.15, "active": 0.08, "recovery": 0.2,
		"reach": 3.0, "arc": 0.4, "heavy_ratio": 1.0, "color": Color("#8a8a8a"), "shape": "spear",
	},
	"trident": {
		"name": "Trident", "power": 14.0, "windup": 0.18, "active": 0.08, "recovery": 0.22,
		"reach": 3.5, "arc": 0.5, "heavy_ratio": 1.1, "color": Color("#9a9a9a"), "shape": "trident",
	},
	"halberd": {
		"name": "Halberd", "power": 18.0, "windup": 0.3, "active": 0.1, "recovery": 0.35,
		"reach": 4.5, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#7a7a7a"), "shape": "halberd",
	},
	"glaive": {
		"name": "Glaive", "power": 15.0, "windup": 0.25, "active": 0.08, "recovery": 0.3,
		"reach": 4.0, "arc": 0.6, "heavy_ratio": 1.2, "color": Color("#8a8a8a"), "shape": "glaive",
	},
	"flail": {
		"name": "Flail", "power": 14.0, "windup": 0.2, "active": 0.08, "recovery": 0.25,
		"reach": 2.0, "arc": 0.8, "heavy_ratio": 1.1, "color": Color("#8a8a8a"), "shape": "flail",
	},
	"morning_star": {
		"name": "Morning Star", "power": 12.0, "windup": 0.18, "active": 0.06, "recovery": 0.22,
		"reach": 1.8, "arc": 0.7, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "morning_star",
	},
	"maul": {
		"name": "Maul", "power": 22.0, "windup": 0.4, "active": 0.1, "recovery": 0.5,
		"reach": 2.0, "arc": 0.6, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "maul",
	},
	"greataxe": {
		"name": "Greataxe", "power": 20.0, "windup": 0.35, "active": 0.08, "recovery": 0.45,
		"reach": 2.2, "arc": 0.6, "heavy_ratio": 1.3, "color": Color("#8a7a6a"), "shape": "greataxe",
	},
	"dagger": {
		"name": "Dagger", "power": 5.0, "windup": 0.1, "active": 0.03, "recovery": 0.1,
		"reach": 1.2, "arc": 0.4, "heavy_ratio": 0.9, "color": Color("#7a7a7a"), "shape": "dagger",
	},
	"rapier": {
		"name": "Rapier", "power": 8.0, "windup": 0.12, "active": 0.04, "recovery": 0.15,
		"reach": 2.0, "arc": 0.3, "heavy_ratio": 0.9, "color": Color("#8a8a8a"), "shape": "rapier",
	},
	"katana": {
		"name": "Katana", "power": 10.0, "windup": 0.15, "active": 0.05, "recovery": 0.2,
		"reach": 1.8, "arc": 0.6, "heavy_ratio": 1.1, "color": Color("#9a9a9a"), "shape": "katana",
	},
	"wakizashi": {
		"name": "Wakizashi", "power": 7.0, "windup": 0.12, "active": 0.04, "recovery": 0.15,
		"reach": 1.2, "arc": 0.5, "heavy_ratio": 1.0, "color": Color("#8a8a8a"), "shape": "wakizashi",
	},
	"bow": {
		"name": "Bow", "power": 10.0, "windup": 0.4, "active": 0.05, "recovery": 0.4,
		"reach": 8.0, "arc": 0.2, "heavy_ratio": 1.0, "color": Color("#7a6a5a"), "shape": "bow",
	},
	"crossbow": {
		"name": "Crossbow", "power": 14.0, "windup": 0.6, "active": 0.05, "recovery": 0.5,
		"reach": 10.0, "arc": 0.2, "heavy_ratio": 1.0, "color": Color("#6a5a4a"), "shape": "crossbow",
	},
	"spear": {
		"name": "Spear", "power": 12.0, "windup": 0.25, "active": 0.08, "recovery": 0.35,
		"reach": 3.0, "arc": 0.3, "heavy_ratio": 1.1, "color": Color("#7a6a5a"), "shape": "spear",
	},
	"trident": {
		"name": "Trident", "power": 14.0, "windup": 0.25, "active": 0.08, "recovery": 0.35,
		"reach": 3.5, "arc": 0.3, "heavy_ratio": 1.1, "color": Color("#8a8a8a"), "shape": "trident",
	},
	"mace": {
		"name": "Mace", "power": 12.0, "windup": 0.2, "active": 0.06, "recovery": 0.3,
		"reach": 1.6, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#8a8a8a"), "shape": "mace",
	},
	"war_hammer": {
		"name": "War Hammer", "power": 16.0, "windup": 0.3, "active": 0.08, "recovery": 0.4,
		"reach": 1.8, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#7a7a7a"), "shape": "hammer",
	},
	"great_sword": {
		"name": "Great Sword", "power": 20.0, "windup": 0.35, "active": 0.1, "recovery": 0.5,
		"reach": 2.5, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#9a9a9a"), "shape": "sword",
	},
	"battle_axe": {
		"name": "Battle Axe", "power": 18.0, "windup": 0.3, "active": 0.08, "recovery": 0.45,
		"reach": 2.2, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#8a7a6a"), "shape": "axe",
	},
	"dagger": {
		"name": "Dagger", "power": 5.0, "windup": 0.1, "active": 0.04, "recovery": 0.15,
		"reach": 1.2, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#6a6a6a"), "shape": "dagger",
	},
	"short_sword": {
		"name": "Short Sword", "power": 8.0, "windup": 0.15, "active": 0.05, "recovery": 0.2,
		"reach": 1.5, "arc": 0.4, "heavy_ratio": 1.0, "color": Color("#7a7a7a"), "shape": "sword",
	},
	"broadsword": {
		"name": "Broadsword", "power": 13.0, "windup": 0.2, "active": 0.06, "recovery": 0.3,
		"reach": 2.0, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#8a8a8a"), "shape": "sword",
	},
	"longsword": {
		"name": "Longsword", "power": 11.0, "windup": 0.18, "active": 0.06, "recovery": 0.28,
		"reach": 1.8, "arc": 0.4, "heavy_ratio": 1.1, "color": Color("#9a9a9a"), "shape": "sword",
	},
	"katana": {
		"name": "Katana", "power": 10.0, "windup": 0.15, "active": 0.05, "recovery": 0.25,
		"reach": 1.8, "arc": 0.4, "heavy_ratio": 1.1, "color": Color("#7a7a7a"), "shape": "sword",
	},
	"wakizashi": {
		"name": "Wakizashi", "power": 7.0, "windup": 0.12, "active": 0.04, "recovery": 0.2,
		"reach": 1.2, "arc": 0.4, "heavy_ratio": 1.0, "color": Color("#8a8a8a"), "shape": "sword",
	},
	"bow": {
		"name": "Bow", "power": 10.0, "windup": 0.3, "active": 0.05, "recovery": 0.5,
		"reach": 8.0, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#6a5a4a"), "shape": "bow",
	},
	"arrow": {
		"name": "Arrow", "power": 8.0, "windup": 0.25, "active": 0.05, "recovery": 0.4,
		"reach": 8.0, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#7a6a5a"), "shape": "arrow",
	},
	"spear": {
		"name": "Spear", "power": 12.0, "windup": 0.25, "active": 0.08, "recovery": 0.4,
		"reach": 3.0, "arc": 0.3, "heavy_ratio": 1.2, "color": Color("#6a5a4a"), "shape": "spear",
	},
	"trident": {
		"name": "Trident", "power": 14.0, "windup": 0.3, "active": 0.08, "recovery": 0.45,
		"reach": 3.5, "arc": 0.3, "heavy_ratio": 1.2, "color": Color("#7a6a5a"), "shape": "trident",
	},
	"warhammer": {
		"name": "Warhammer", "power": 16.0, "windup": 0.35, "active": 0.1, "recovery": 0.5,
		"reach": 1.8, "arc": 0.4, "heavy_ratio": 1.3, "color": Color("#5a5a5a"), "shape": "warhammer",
	},
	"morning_star": {
		"name": "Morning Star", "power": 13.0, "windup": 0.28, "active": 0.08, "recovery": 0.42,
		"reach": 1.7, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#7a7a7a"), "shape": "morning_star",
	},
	"mace": {
		"name": "Mace", "power": 12.0, "windup": 0.25, "active": 0.08, "recovery": 0.4,
		"reach": 1.6, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#6a6a6a"), "shape": "mace",
	},
	"flail": {
		"name": "Flail", "power": 14.0, "windup": 0.3, "active": 0.08, "recovery": 0.45,
		"reach": 2.0, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#7a7a7a"), "shape": "flail",
	},
	"halberd": {
		"name": "Halberd", "power": 18.0, "windup": 0.4, "active": 0.1, "recovery": 0.6,
		"reach": 4.5, "arc": 0.3, "heavy_ratio": 1.3, "color": Color("#5a4a3a"), "shape": "halberd",
	},
	"glaive": {
		"name": "Glaive", "power": 15.0, "windup": 0.35, "active": 0.1, "recovery": 0.5,
		"reach": 4.0, "arc": 0.3, "heavy_ratio": 1.2, "color": Color("#6a5a4a"), "shape": "glaive",
	},
	"fan": {
		"name": "Fan", "power": 5.0, "windup": 0.1, "active": 0.05, "recovery": 0.15,
		"reach": 1.5, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#8a7a6a"), "shape": "fan",
	},
	"tonfa": {
		"name": "Tonfa", "power": 9.0, "windup": 0.15, "active": 0.05, "recovery": 0.25,
		"reach": 1.5, "arc": 0.4, "heavy_ratio": 1.1, "color": Color("#6a5a4a"), "shape": "tonfa",
	},
	"whip": {
		"name": "Whip", "power": 6.0, "windup": 0.15, "active": 0.05, "recovery": 0.2,
		"reach": 3.0, "arc": 0.2, "heavy_ratio": 1.0, "color": Color("#7a6a5a"), "shape": "whip",
	},
	"chain": {
		"name": "Chain", "power": 8.0, "windup": 0.2, "active": 0.05, "recovery": 0.3,
		"reach": 2.5, "arc": 0.3, "heavy_ratio": 1.1, "color": Color("#8a8a8a"), "shape": "chain",
	},
	"staff": {
		"name": "Staff", "power": 12.0, "windup": 0.3, "active": 0.1, "recovery": 0.4,
		"reach": 2.5, "arc": 0.3, "heavy_ratio": 1.2, "color": Color("#5a4a3a"), "shape": "staff",
	},
	"mace": {
		"name": "Mace", "power": 14.0, "windup": 0.25, "active": 0.08, "recovery": 0.4,
		"reach": 1.8, "arc": 0.4, "heavy_ratio": 1.3, "color": Color("#6a6a6a"), "shape": "mace",
	},
	"bow": {
		"name": "Bow", "power": 10.0, "windup": 0.3, "active": 0.05, "recovery": 0.4,
		"reach": 8.0, "arc": 0.1, "heavy_ratio": 1.1, "color": Color("#6a5a4a"), "shape": "bow",
	},
	"crossbow": {
		"name": "Crossbow", "power": 14.0, "windup": 0.5, "active": 0.05, "recovery": 0.6,
		"reach": 10.0, "arc": 0.1, "heavy_ratio": 1.2, "color": Color("#5a4a3a"), "shape": "crossbow",
	},
	"spear": {
		"name": "Spear", "power": 12.0, "windup": 0.2, "active": 0.08, "recovery": 0.3,
		"reach": 3.0, "arc": 0.2, "heavy_ratio": 1.2, "color": Color("#5a5a4a"), "shape": "spear",
	},
	"trident": {
		"name": "Trident", "power": 14.0, "windup": 0.25, "active": 0.08, "recovery": 0.4,
		"reach": 3.5, "arc": 0.2, "heavy_ratio": 1.3, "color": Color("#4a4a3a"), "shape": "trident",
	},
	"flail": {
		"name": "Flail", "power": 14.0, "windup": 0.25, "active": 0.1, "recovery": 0.4,
		"reach": 2.0, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#9a9a9a"), "shape": "flail",
	},
	"warhammer": {
		"name": "Warhammer", "power": 16.0, "windup": 0.3, "active": 0.12, "recovery": 0.5,
		"reach": 1.8, "arc": 0.4, "heavy_ratio": 1.4, "color": Color("#8a8a8a"), "shape": "warhammer",
	},
	"mace": {
		"name": "Mace", "power": 12.0, "windup": 0.2, "active": 0.08, "recovery": 0.3,
		"reach": 1.6, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#aaaaaa"), "shape": "mace",
	},
	"morning_star": {
		"name": "Morning Star", "power": 14.0, "windup": 0.25, "active": 0.08, "recovery": 0.4,
		"reach": 1.8, "arc": 0.4, "heavy_ratio": 1.3, "color": Color("#bbbbbb"), "shape": "morning_star",
	},
	"glaive": {
		"name": "Glaive", "power": 15.0, "windup": 0.3, "active": 0.1, "recovery": 0.5,
		"reach": 4.0, "arc": 0.4, "heavy_ratio": 1.3, "color": Color("#6a6a5a"), "shape": "glaive",
	},
	"halberd": {
		"name": "Halberd", "power": 18.0, "windup": 0.35, "active": 0.12, "recovery": 0.6,
		"reach": 4.5, "arc": 0.5, "heavy_ratio": 1.4, "color": Color("#5a5a4a"), "shape": "halberd",
	},
	"lance": {
		"name": "Lance", "power": 18.0, "windup": 0.25, "active": 0.08, "recovery": 0.5,
		"reach": 6.0, "arc": 0.2, "heavy_ratio": 1.4, "color": Color("#6a5a4a"), "shape": "lance",
	},
	"pike": {
		"name": "Pike", "power": 16.0, "windup": 0.3, "active": 0.08, "recovery": 0.6,
		"reach": 7.0, "arc": 0.2, "heavy_ratio": 1.3, "color": Color("#5a4a3a"), "shape": "pike",
	},
	"scythe": {
		"name": "Scythe", "power": 16.0, "windup": 0.3, "active": 0.1, "recovery": 0.5,
		"reach": 2.5, "arc": 0.5, "heavy_ratio": 1.4, "color": Color("#8a8a8a"), "shape": "scythe",
	},
	"flail": {
		"name": "Flail", "power": 14.0, "windup": 0.25, "active": 0.08, "recovery": 0.4,
		"reach": 2.0, "arc": 0.4, "heavy_ratio": 1.3, "color": Color("#9a9a9a"), "shape": "flail",
	},
	"rapier": {
		"name": "Rapier", "power": 8.0, "windup": 0.15, "active": 0.06, "recovery": 0.2,
		"reach": 2.0, "arc": 0.3, "heavy_ratio": 1.1, "color": Color("#aaaaaa"), "shape": "rapier",
	},
	"saber": {
		"name": "Saber", "power": 12.0, "windup": 0.2, "active": 0.08, "recovery": 0.3,
		"reach": 1.8, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#bbbbbb"), "shape": "saber",
	},
	"hammer": {
		"name": "Hammer", "power": 20.0, "windup": 0.35, "active": 0.1, "recovery": 0.6,
		"reach": 2.2, "arc": 0.5, "heavy_ratio": 1.5, "color": Color("#7a7a7a"), "shape": "hammer",
	},
	"maul": {
		"name": "Maul", "power": 25.0, "windup": 0.45, "active": 0.12, "recovery": 0.8,
		"reach": 2.5, "arc": 0.6, "heavy_ratio": 1.6, "color": Color("#6a6a6a"), "shape": "maul",
	},
	"spear": {
		"name": "Spear", "power": 14.0, "windup": 0.25, "active": 0.08, "recovery": 0.4,
		"reach": 5.5, "arc": 0.3, "heavy_ratio": 1.3, "color": Color("#7a6a5a"), "shape": "spear",
	},
	"trident": {
		"name": "Trident", "power": 16.0, "windup": 0.3, "active": 0.1, "recovery": 0.5,
		"reach": 5.0, "arc": 0.4, "heavy_ratio": 1.4, "color": Color("#8a7a6a"), "shape": "trident",
	},
	"shield": {
		"name": "Shield", "power": 4.0, "windup": 0.2, "active": 0.08, "recovery": 0.3,
		"reach": 1.2, "arc": 0.4, "heavy_ratio": 1.1, "color": Color("#8a7a6a"), "shape": "shield",
	},
	"buckler": {
		"name": "Buckler", "power": 3.0, "windup": 0.15, "active": 0.06, "recovery": 0.2,
		"reach": 1.0, "arc": 0.3, "heavy_ratio": 1.0, "color": Color("#9a8a7a"), "shape": "buckler",
	},
	"crossbow": {
		"name": "Crossbow", "power": 14.0, "windup": 0.5, "active": 0.05, "recovery": 0.8,
		"reach": 10.0, "arc": 0.1, "heavy_ratio": 1.0, "color": Color("#7a6a5a"), "shape": "crossbow",
	},
	"slingshot": {
		"name": "Slingshot", "power": 6.0, "windup": 0.2, "active": 0.05, "recovery": 0.3,
		"reach": 8.0, "arc": 0.1, "heavy_ratio": 1.0, "color": Color("#8a7a6a"), "shape": "slingshot",
	},
	"fan": {
		"name": "Fan", "power": 5.0, "windup": 0.1, "active": 0.05, "recovery": 0.15,
		"reach": 1.5, "arc": 0.4, "heavy_ratio": 1.1, "color": Color("#9a8a7a"), "shape": "fan",
	},
	"tonfa": {
		"name": "Tonfa", "power": 9.0, "windup": 0.18, "active": 0.08, "recovery": 0.25,
		"reach": 1.5, "arc": 0.5, "heavy_ratio": 1.2, "color": Color("#8a7a6a"), "shape": "tonfa",
	},
	"whip": {
		"name": "Whip", "power": 6.0, "windup": 0.15, "active": 0.05, "recovery": 0.25,
		"reach": 3.0, "arc": 0.3, "heavy_ratio": 1.2, "color": Color("#8a7a6a"), "shape": "whip",
	},
	"chain": {
		"name": "Chain", "power": 8.0, "windup": 0.2, "active": 0.08, "recovery": 0.3,
		"reach": 2.5, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#7a7a7a"), "shape": "chain",
	},
	"halberd": {
		"name": "Halberd", "power": 18.0, "windup": 0.3, "active": 0.12, "recovery": 0.55,
		"reach": 4.5, "arc": 0.7, "heavy_ratio": 1.5, "color": Color("#6a6a6a"), "shape": "halberd",
	},
	"glaive": {
		"name": "Glaive", "power": 15.0, "windup": 0.25, "active": 0.1, "recovery": 0.45,
		"reach": 4.0, "arc": 0.8, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "glaive",
	},
	"mace": {
		"name": "Mace", "power": 12.0, "windup": 0.22, "active": 0.08, "recovery": 0.35,
		"reach": 1.6, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#7a7a7a"), "shape": "mace",
	},
	"flail": {
		"name": "Flail", "power": 14.0, "windup": 0.28, "active": 0.12, "recovery": 0.5,
		"reach": 2.0, "arc": 0.8, "heavy_ratio": 1.4, "color": Color("#6a6a6a"), "shape": "flail",
	},
	"katana": {
		"name": "Katana", "power": 10.0, "windup": 0.15, "active": 0.08, "recovery": 0.3,
		"reach": 1.8, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#8a8a8a"), "shape": "katana",
	},
	"greatsword": {
		"name": "Greatsword", "power": 20.0, "windup": 0.35, "active": 0.15, "recovery": 0.65,
		"reach": 2.5, "arc": 0.9, "heavy_ratio": 1.6, "color": Color("#6a6a6a"), "shape": "greatsword",
	},
	"broadsword": {
		"name": "Broadsword", "power": 13.0, "windup": 0.2, "active": 0.1, "recovery": 0.4,
		"reach": 2.0, "arc": 0.7, "heavy_ratio": 1.4, "color": Color("#8a8a8a"), "shape": "broadsword",
	},
	"dagger_pair": {
		"name": "Dagger Pair", "power": 5.0, "windup": 0.1, "active": 0.05, "recovery": 0.2,
		"reach": 1.2, "arc": 0.4, "heavy_ratio": 1.1, "color": Color("#9a9a9a"), "shape": "daggers",
	},
	"scythe": {
		"name": "Scythe", "power": 16.0, "windup": 0.3, "active": 0.15, "recovery": 0.6,
		"reach": 2.5, "arc": 1.0, "heavy_ratio": 1.5, "color": Color("#6a6a6a"), "shape": "scythe",
	},
	"morningstar": {
		"name": "Morningstar", "power": 14.0, "windup": 0.25, "active": 0.1, "recovery": 0.45,
		"reach": 2.0, "arc": 0.6, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "morningstar",
	},
	"rapier": {
		"name": "Rapier", "power": 8.0, "windup": 0.12, "active": 0.05, "recovery": 0.25,
		"reach": 2.0, "arc": 0.3, "heavy_ratio": 1.2, "color": Color("#9a9a9a"), "shape": "rapier",
	},
	"warhammer": {
		"name": "Warhammer", "power": 22.0, "windup": 0.4, "active": 0.15, "recovery": 0.75,
		"reach": 1.8, "arc": 0.6, "heavy_ratio": 1.6, "color": Color("#5a5a5a"), "shape": "hammer",
	},
	"crossbow": {
		"name": "Crossbow", "power": 12.0, "windup": 0.5, "active": 0.05, "recovery": 0.8,
		"reach": 10.0, "arc": 0.1, "heavy_ratio": 1.2, "color": Color("#7a7a6a"), "shape": "crossbow",
	},
	"battle_axe": {
		"name": "Battle Axe", "power": 16.0, "windup": 0.3, "active": 0.12, "recovery": 0.55,
		"reach": 2.2, "arc": 0.8, "heavy_ratio": 1.5, "color": Color("#6a6a6a"), "shape": "axe",
	},
	"flail": {
		"name": "Flail", "power": 13.0, "windup": 0.35, "active": 0.15, "recovery": 0.55,
		"reach": 2.0, "arc": 0.8, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "flail",
	},
	"halberd": {
		"name": "Halberd", "power": 15.0, "windup": 0.3, "active": 0.12, "recovery": 0.6,
		"reach": 3.0, "arc": 0.7, "heavy_ratio": 1.5, "color": Color("#6a6a6a"), "shape": "halberd",
	},
	"trident": {
		"name": "Trident", "power": 12.0, "windup": 0.2, "active": 0.1, "recovery": 0.4,
		"reach": 2.2, "arc": 0.6, "heavy_ratio": 1.3, "color": Color("#7a7a7a"), "shape": "trident",
	},
	"mace": {
		"name": "Mace", "power": 14.0, "windup": 0.3, "active": 0.12, "recovery": 0.5,
		"reach": 1.8, "arc": 0.5, "heavy_ratio": 1.4, "color": Color("#6a6a6a"), "shape": "mace",
	},
	"dagger_pair": {
		"name": "Dagger Pair", "power": 5.0, "windup": 0.1, "active": 0.05, "recovery": 0.2,
		"reach": 1.2, "arc": 0.4, "heavy_ratio": 1.1, "color": Color("#8a8a8a"), "shape": "daggers",
	},
	"greatsword": {
		"name": "Greatsword", "power": 20.0, "windup": 0.45, "active": 0.2, "recovery": 0.85,
		"reach": 2.5, "arc": 1.0, "heavy_ratio": 1.6, "color": Color("#6a6a6a"), "shape": "greatsword",
	},
	"katana": {
		"name": "Katana", "power": 10.0, "windup": 0.15, "active": 0.08, "recovery": 0.35,
		"reach": 1.8, "arc": 0.5, "heavy_ratio": 1.3, "color": Color("#9a9a9a"), "shape": "katana",
	},
	"broadsword": {
		"name": "Broadsword", "power": 13.0, "windup": 0.25, "active": 0.12, "recovery": 0.5,
		"reach": 2.0, "arc": 0.7, "heavy_ratio": 1.4, "color": Color("#7a7a7a"), "shape": "broadsword",
	},
	"scythe": {
		"name": "Scythe", "power": 16.0, "windup": 0.4, "active": 0.15, "recovery": 0.7,
		"reach": 2.5, "arc": 1.2, "heavy_ratio": 1.5, "color": Color("#5a5a5a"), "shape": "scythe",
	},
	"morningstar": {
		"name": "Morningstar", "power": 14.0, "windup": 0.3, "active": 0.1, "recovery": 0.5,
		"reach": 2.0, "arc": 0.6, "heavy_ratio": 1.4, "color": Color("#6a6a6a"), "shape": "morningstar",
	},
	"rapier": {
		"name": "Rapier", "power": 8.0, "windup": 0.12, "active": 0.05, "recovery": 0.25,
		"reach": 2.0, "arc": 0.3, "heavy_ratio": 1.2, "color": Color("#8a8a8a"), "shape": "rapier",
	},
	"warhammer": {
		"name": "Warhammer", "power": 22.0, "windup": 0.5, "active": 0.15, "recovery": 0.8,
		"reach": 1.8, "arc": 0.7, "heavy_ratio": 1.6, "color": Color("#5a5a5a"), "shape": "hammer",
	},
	"iron_crossbow": {
		"name": "Iron Crossbow", "power": 14.0, "windup": 0.5, "active": 0.05, "recovery": 0.6,
		"reach": 10.0, "arc": 0.2, "heavy_ratio": 1.5, "color": Color("#5a5a5a"), "shape": "crossbow",
	},
	"battle_axe": {
		"name": "Battle Axe", "power": 17.0, "windup": 0.4, "active": 0.15, "recovery": 0.7,
		"reach": 2.2, "arc": 1.0, "heavy_ratio": 1.5, "color": Color("#6a6a6a"), "shape": "axe",
	},
	"oak_bow": {
		"name": "Oak Bow", "power": 10.0, "windup": 0.3, "active": 0.1, "recovery": 0.4,
		"reach": 8.0, "arc": 0.3, "heavy_ratio": 1.3, "color": Color("#8a6a4a"), "shape": "bow",
	},
	"whip": {
		"name": "Whip", "power": 6.0, "windup": 0.15, "active": 0.05, "recovery": 0.3,
		"reach": 3.0, "arc": 0.4, "heavy_ratio": 1.2, "color": Color("#6a4a3a"), "shape": "whip",
	},
	"iron_fan": {
		"name": "Iron Fan", "power": 5.0, "windup": 0.1, "active": 0.05, "recovery": 0.25,
		"reach": 1.5, "arc": 0.6, "heavy_ratio": 1.1, "color": Color("#8a8a8a"), "shape": "fan",
	},
	"chain_flail": {
		"name": "Chain Flail", "power": 16.0, "windup": 0.35, "active": 0.15, "recovery": 0.6,
		"reach": 2.5, "arc": 1.5, "heavy_ratio": 1.5, "color": Color("#7a7a7a"), "shape": "flail",
	},
	"iron_trident": {
		"name": "Iron Trident", "power": 15.0, "windup": 0.35, "active": 0.15, "recovery": 0.55,
		"reach": 3.5, "arc": 0.6, "heavy_ratio": 1.4, "color": Color("#6a6a6a"), "shape": "trident",
	},
	"iron_mace": {
		"name": "Iron Mace", "power": 18.0, "windup": 0.4, "active": 0.12, "recovery": 0.65,
		"reach": 1.8, "arc": 0.8, "heavy_ratio": 1.5, "color": Color("#7a7a7a"), "shape": "mace",
	},
	"iron_halberd": {
		"name": "Iron Halberd", "power": 18.0, "windup": 0.45, "active": 0.18, "recovery": 0.7,
		"reach": 4.5, "arc": 0.8, "heavy_ratio": 1.6, "color": Color("#6a6a6a"), "shape": "halberd",
	},
	"ember_staff": {
		"name": "Ember Staff", "power": 12.0, "windup": 0.4, "active": 0.15, "recovery": 0.5,
		"reach": 6.0, "arc": 0.5, "heavy_ratio": 1.4, "color": Color("#aa6633"), "shape": "staff",
	},
	"great_axe": {
		"name": "Great Axe", "power": 20.0, "windup": 0.55, "active": 0.2, "recovery": 0.85,
		"reach": 2.8, "arc": 1.3, "heavy_ratio": 1.7, "color": Color("#5a4a3a"), "shape": "axe",
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
	"ash_crawler": {
		"name": "Ash Crawler", "hp": 20.0, "damage": 6.0, "poise": 5.0, "speed": 6.0,
		"tell": 0.2, "reach": 1.2, "color": Color("#5a5a5a"), "shape": "beast",
		"size": 10, "aggro": 15.0, "posture": "darter", "relics": 0,
	},
	"ember_bat": {
		"name": "Ember Bat", "hp": 15.0, "damage": 5.0, "poise": 3.0, "speed": 7.0,
		"tell": 0.15, "reach": 1.0, "color": Color("#6a4a3a"), "shape": "beast",
		"size": 5, "aggro": 12.0, "posture": "darter", "relics": 0,
	},
	"ash_giant": {
		"name": "Ash Giant", "hp": 300.0, "damage": 30.0, "poise": 100.0, "speed": 1.5,
		"tell": 1.0, "reach": 4.0, "color": Color("#5a5a5a"), "shape": "humanoid",
		"size": 30, "aggro": 25.0, "posture": "bulwark", "relics": 3,
	},
	"ash_healer": {
		"name": "Ash Healer", "hp": 40.0, "damage": 5.0, "poise": 15.0, "speed": 2.5,
		"tell": 0.5, "reach": 1.5, "color": Color("#8a9a8a"), "shape": "humanoid",
		"size": 12, "aggro": 15.0, "posture": "dancer", "relics": 1,
	},
	"ash_sphinx": {
		"name": "Ash Sphinx", "hp": 150.0, "damage": 20.0, "poise": 50.0, "speed": 2.5,
		"tell": 0.18, "reach": 2.5, "color": Color("#aa8866"), "shape": "sphinx",
		"size": 16, "aggro": 10.0, "posture": "balanced", "relics": 5,
	},
	"ash_manticore": {
		"name": "Ash Manticore", "hp": 140.0, "damage": 22.0, "poise": 45.0, "speed": 3.0,
		"tell": 0.16, "reach": 2.8, "color": Color("#7a6a5a"), "shape": "manticore",
		"size": 15, "aggro": 11.0, "posture": "darter", "relics": 5,
	},
	"ash_griffin": {
		"name": "Ash Griffin", "hp": 100.0, "damage": 16.0, "poise": 30.0, "speed": 3.5,
		"tell": 0.12, "reach": 2.2, "color": Color("#aa9966"), "shape": "griffin",
		"size": 14, "aggro": 11.0, "posture": "darter", "relics": 4,
	},
	"ash_centaur": {
		"name": "Ash Centaur", "hp": 130.0, "damage": 18.0, "poise": 40.0, "speed": 3.8,
		"tell": 0.15, "reach": 2.5, "color": Color("#7a7a7a"), "shape": "centaur",
		"size": 14, "aggro": 10.0, "posture": "darter", "relics": 4,
	},
	"ash_harpy": {
		"name": "Ash Harpy", "hp": 60.0, "damage": 12.0, "poise": 20.0, "speed": 4.0,
		"tell": 0.1, "reach": 1.8, "color": Color("#7a7a8a"), "shape": "harpy",
		"size": 10, "aggro": 12.0, "posture": "darter", "relics": 2,
	},
	"ash_basilisk": {
		"name": "Ash Basilisk", "hp": 120.0, "damage": 18.0, "poise": 40.0, "speed": 2.0,
		"tell": 0.18, "reach": 2.2, "color": Color("#6a8a6a"), "shape": "basilisk",
		"size": 14, "aggro": 10.0, "posture": "balanced", "relics": 4,
	},
	"ash_troll": {
		"name": "Ash Troll", "hp": 180.0, "damage": 22.0, "poise": 60.0, "speed": 2.0,
		"tell": 0.22, "reach": 2.8, "color": Color("#6a7a6a"), "shape": "troll",
		"size": 18, "aggro": 10.0, "posture": "balanced", "relics": 5,
	},
	"ash_cyclops": {
		"name": "Ash Cyclops", "hp": 250.0, "damage": 30.0, "poise": 70.0, "speed": 1.5,
		"tell": 0.28, "reach": 3.0, "color": Color("#8a8a7a"), "shape": "cyclops",
		"size": 22, "aggro": 11.0, "posture": "balanced", "relics": 7,
	},
	"ash_gargoyle": {
		"name": "Ash Gargoyle", "hp": 80.0, "damage": 16.0, "poise": 30.0, "speed": 3.0,
		"tell": 0.12, "reach": 2.0, "color": Color("#7a7a7a"), "shape": "gargoyle",
		"size": 12, "aggro": 10.0, "posture": "darter", "relics": 3,
	},
	"ash_golem": {
		"name": "Ash Golem", "hp": 200.0, "damage": 24.0, "poise": 80.0, "speed": 1.8,
		"tell": 0.25, "reach": 2.5, "color": Color("#8a8a8a"), "shape": "golem",
		"size": 20, "aggro": 9.0, "posture": "balanced", "relics": 6,
	},
	"ash_hydra": {
		"name": "Ash Hydra", "hp": 250.0, "damage": 26.0, "poise": 80.0, "speed": 2.2,
		"tell": 0.2, "reach": 3.0, "color": Color("#6a7a6a"), "shape": "hydra",
		"size": 22, "aggro": 12.0, "posture": "balanced", "relics": 7,
	},
	"ash_phoenix": {
		"name": "Ash Phoenix", "hp": 200.0, "damage": 28.0, "poise": 60.0, "speed": 3.5,
		"tell": 0.15, "reach": 2.5, "color": Color("#ff8844"), "shape": "phoenix",
		"size": 18, "aggro": 11.0, "posture": "darter", "relics": 6,
	},
	"ash_minotaur": {
		"name": "Ash Minotaur", "hp": 200.0, "damage": 25.0, "poise": 70.0, "speed": 2.5,
		"tell": 0.2, "reach": 2.5, "color": Color("#7a6a7a"), "shape": "minotaur",
		"size": 18, "aggro": 11.0, "posture": "balanced", "relics": 6,
	},
	"ash_chimera": {
		"name": "Ash Chimera", "hp": 220.0, "damage": 28.0, "poise": 65.0, "speed": 2.8,
		"tell": 0.18, "reach": 2.8, "color": Color("#8a7a6a"), "shape": "chimera",
		"size": 20, "aggro": 12.0, "posture": "darter", "relics": 6,
	},
	"ash_centaur": {
		"name": "Ash Centaur", "hp": 130.0, "damage": 18.0, "poise": 40.0, "speed": 3.8,
		"tell": 0.15, "reach": 2.5, "color": Color("#7a7a7a"), "shape": "centaur",
		"size": 14, "aggro": 10.0, "posture": "darter", "relics": 4,
	},
	"ash_manticore": {
		"name": "Ash Manticore", "hp": 160.0, "damage": 22.0, "poise": 55.0, "speed": 3.0,
		"tell": 0.18, "reach": 2.8, "color": Color("#8a7a6a"), "shape": "manticore",
		"size": 16, "aggro": 11.0, "posture": "balanced", "relics": 5,
	},
	"ash_sphinx": {
		"name": "Ash Sphinx", "hp": 150.0, "damage": 20.0, "poise": 50.0, "speed": 2.5,
		"tell": 0.15, "reach": 2.5, "color": Color("#8a7a6a"), "shape": "sphinx",
		"size": 16, "aggro": 10.0, "posture": "balanced", "relics": 5,
	},
	"ash_griffin": {
		"name": "Ash Griffin", "hp": 100.0, "damage": 16.0, "poise": 30.0, "speed": 4.5,
		"tell": 0.12, "reach": 2.0, "color": Color("#9a8a6a"), "shape": "griffin",
		"size": 12, "aggro": 11.0, "posture": "darter", "relics": 3,
	},
	"ash_harpy": {
		"name": "Ash Harpy", "hp": 60.0, "damage": 12.0, "poise": 20.0, "speed": 4.0,
		"tell": 0.1, "reach": 1.8, "color": Color("#8a7a8a"), "shape": "harpy",
		"size": 10, "aggro": 10.0, "posture": "darter", "relics": 2,
	},
	"ash_basilisk": {
		"name": "Ash Basilisk", "hp": 120.0, "damage": 18.0, "poise": 40.0, "speed": 2.2,
		"tell": 0.2, "reach": 2.2, "color": Color("#6a7a6a"), "shape": "basilisk",
		"size": 14, "aggro": 9.0, "posture": "balanced", "relics": 4,
	},
	"ash_minotaur": {
		"name": "Ash Minotaur", "hp": 200.0, "damage": 25.0, "poise": 70.0, "speed": 2.5,
		"tell": 0.2, "reach": 2.5, "color": Color("#7a6a7a"), "shape": "minotaur",
		"size": 18, "aggro": 11.0, "posture": "balanced", "relics": 6,
	},
	"ash_chimera": {
		"name": "Ash Chimera", "hp": 220.0, "damage": 28.0, "poise": 65.0, "speed": 2.8,
		"tell": 0.18, "reach": 2.8, "color": Color("#8a7a6a"), "shape": "chimera",
		"size": 20, "aggro": 12.0, "posture": "darter", "relics": 6,
	},
	"ash_troll": {
		"name": "Ash Troll", "hp": 180.0, "damage": 22.0, "poise": 60.0, "speed": 2.0,
		"tell": 0.25, "reach": 2.5, "color": Color("#6a7a6a"), "shape": "troll",
		"size": 18, "aggro": 9.0, "posture": "balanced", "relics": 5,
	},
	"ash_cyclops": {
		"name": "Ash Cyclops", "hp": 250.0, "damage": 30.0, "poise": 70.0, "speed": 1.8,
		"tell": 0.3, "reach": 3.0, "color": Color("#7a7a6a"), "shape": "cyclops",
		"size": 22, "aggro": 10.0, "posture": "balanced", "relics": 7,
	},
	"ash_gargoyle": {
		"name": "Ash Gargoyle", "hp": 80.0, "damage": 16.0, "poise": 30.0, "speed": 3.2,
		"tell": 0.15, "reach": 2.0, "color": Color("#7a7a7a"), "shape": "gargoyle",
		"size": 14, "aggro": 11.0, "posture": "darter", "relics": 3,
	},
	"ash_golem": {
		"name": "Ash Golem", "hp": 200.0, "damage": 24.0, "poise": 80.0, "speed": 1.5,
		"tell": 0.35, "reach": 2.5, "color": Color("#6a6a6a"), "shape": "golem",
		"size": 20, "aggro": 8.0, "posture": "balanced", "relics": 5,
	},
	"ash_dragon": {
		"name": "Ash Dragon", "hp": 300.0, "damage": 35.0, "poise": 100.0, "speed": 3.0,
		"tell": 0.3, "reach": 3.0, "color": Color("#9a6a6a"), "shape": "dragon",
		"size": 25, "aggro": 15.0, "posture": "balanced", "relics": 8,
	},
	"ash_phoenix": {
		"name": "Ash Phoenix", "hp": 200.0, "damage": 28.0, "poise": 60.0, "speed": 4.0,
		"tell": 0.2, "reach": 2.5, "color": Color("#9a8a6a"), "shape": "bird",
		"size": 18, "aggro": 12.0, "posture": "darter", "relics": 6,
	},
	"ash_wolf": {
		"name": "Ash Wolf", "hp": 50.0, "damage": 12.0, "poise": 15.0, "speed": 3.8,
		"tell": 0.1, "reach": 1.3, "color": Color("#8a8a8a"), "shape": "quadruped",
		"size": 11, "aggro": 10.0, "posture": "darter", "relics": 2,
	},
	"ash_bear": {
		"name": "Ash Bear", "hp": 140.0, "damage": 20.0, "poise": 50.0, "speed": 2.2,
		"tell": 0.25, "reach": 1.8, "color": Color("#7a6a5a"), "shape": "quadruped",
		"size": 16, "aggro": 9.0, "posture": "balanced", "relics": 4,
	},
	"ash_skeleton": {
		"name": "Ash Skeleton", "hp": 40.0, "damage": 10.0, "poise": 15.0, "speed": 2.8,
		"tell": 0.15, "reach": 1.5, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 12, "aggro": 9.0, "posture": "darter", "relics": 2,
	},
	"ash_zombie": {
		"name": "Ash Zombie", "hp": 70.0, "damage": 14.0, "poise": 25.0, "speed": 1.8,
		"tell": 0.3, "reach": 1.5, "color": Color("#7a9a7a"), "shape": "humanoid",
		"size": 13, "aggro": 8.0, "posture": "balanced", "relics": 2,
	},
	"ash_goblin": {
		"name": "Ash Goblin", "hp": 30.0, "damage": 8.0, "poise": 10.0, "speed": 3.5,
		"tell": 0.1, "reach": 1.2, "color": Color("#6a8a6a"), "shape": "humanoid",
		"size": 10, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_orc": {
		"name": "Ash Orc", "hp": 100.0, "damage": 18.0, "poise": 40.0, "speed": 2.5,
		"tell": 0.2, "reach": 2.0, "color": Color("#7a9a7a"), "shape": "humanoid",
		"size": 14, "aggro": 9.0, "posture": "balanced", "relics": 3,
	},
	"ash_knight": {
		"name": "Ash Knight", "hp": 160.0, "damage": 22.0, "poise": 85.0, "speed": 2.2,
		"tell": 0.25, "reach": 2.0, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 14, "aggro": 10.0, "posture": "guardian", "relics": 4,
	},
	"ash_paladin": {
		"name": "Ash Paladin", "hp": 180.0, "damage": 24.0, "poise": 90.0, "speed": 2.0,
		"tell": 0.25, "reach": 2.0, "color": Color("#9a9a9a"), "shape": "humanoid",
		"size": 15, "aggro": 10.0, "posture": "guardian", "relics": 5,
	},
	"ash_samurai": {
		"name": "Ash Samurai", "hp": 80.0, "damage": 16.0, "poise": 35.0, "speed": 2.8,
		"tell": 0.15, "reach": 2.0, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "darter", "relics": 3,
	},
	"ash_ninja": {
		"name": "Ash Ninja", "hp": 40.0, "damage": 10.0, "poise": 12.0, "speed": 3.5,
		"tell": 0.1, "reach": 1.5, "color": Color("#6a6a6a"), "shape": "humanoid",
		"size": 11, "aggro": 9.0, "posture": "darter", "relics": 2,
	},
	"ash_priest": {
		"name": "Ash Priest", "hp": 55.0, "damage": 10.0, "poise": 20.0, "speed": 2.5,
		"tell": 0.25, "reach": 5.0, "color": Color("#9a8a7a"), "shape": "humanoid",
		"size": 12, "aggro": 9.0, "posture": "ranged", "relics": 2,
	},
	"ash_wizard": {
		"name": "Ash Wizard", "hp": 55.0, "damage": 18.0, "poise": 20.0, "speed": 2.5,
		"tell": 0.3, "reach": 10.0, "color": Color("#7a6a8a"), "shape": "humanoid",
		"size": 12, "aggro": 10.0, "posture": "ranged", "relics": 3,
	},
	"ash_hunter": {
		"name": "Ash Hunter", "hp": 45.0, "damage": 11.0, "poise": 15.0, "speed": 3.0,
		"tell": 0.2, "reach": 8.0, "color": Color("#7a8a6a"), "shape": "humanoid",
		"size": 12, "aggro": 10.0, "posture": "ranged", "relics": 1,
	},
	"ash_ranger": {
		"name": "Ash Ranger", "hp": 55.0, "damage": 13.0, "poise": 18.0, "speed": 3.2,
		"tell": 0.2, "reach": 10.0, "color": Color("#8a9a7a"), "shape": "humanoid",
		"size": 12, "aggro": 10.0, "posture": "ranged", "relics": 2,
	},
	"ash_knight": {
		"name": "Ash Knight", "hp": 160.0, "damage": 22.0, "poise": 85.0, "speed": 2.2,
		"tell": 0.25, "reach": 2.0, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 14, "aggro": 10.0, "posture": "guardian", "relics": 4,
	},
	"ash_paladin": {
		"name": "Ash Paladin", "hp": 180.0, "damage": 24.0, "poise": 90.0, "speed": 2.0,
		"tell": 0.25, "reach": 2.0, "color": Color("#9a9a9a"), "shape": "humanoid",
		"size": 15, "aggro": 10.0, "posture": "guardian", "relics": 5,
	},
	"ash_monk": {
		"name": "Ash Monk", "hp": 50.0, "damage": 12.0, "poise": 20.0, "speed": 3.0,
		"tell": 0.15, "reach": 1.5, "color": Color("#7a8a7a"), "shape": "humanoid",
		"size": 12, "aggro": 9.0, "posture": "darter", "relics": 2,
	},
	"ash_warrior": {
		"name": "Ash Warrior", "hp": 90.0, "damage": 18.0, "poise": 45.0, "speed": 2.5,
		"tell": 0.2, "reach": 2.0, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "guardian", "relics": 3,
	},
	"ash_barbarian": {
		"name": "Ash Barbarian", "hp": 100.0, "damage": 20.0, "poise": 50.0, "speed": 2.5,
		"tell": 0.25, "reach": 2.0, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 14, "aggro": 10.0, "posture": "guardian", "relics": 2,
	},
	"ash_berserker": {
		"name": "Ash Berserker", "hp": 120.0, "damage": 22.0, "poise": 60.0, "speed": 2.8,
		"tell": 0.2, "reach": 2.0, "color": Color("#9a8a7a"), "shape": "humanoid",
		"size": 14, "aggro": 12.0, "posture": "guardian", "relics": 3,
	},
	"ash_thief": {
		"name": "Ash Thief", "hp": 30.0, "damage": 8.0, "poise": 8.0, "speed": 3.5,
		"tell": 0.15, "reach": 1.5, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 11, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_rogue": {
		"name": "Ash Rogue", "hp": 35.0, "damage": 9.0, "poise": 10.0, "speed": 3.2,
		"tell": 0.15, "reach": 1.5, "color": Color("#7a8a7a"), "shape": "humanoid",
		"size": 11, "aggro": 9.0, "posture": "darter", "relics": 2,
	},
	"ash_samurai": {
		"name": "Ash Samurai", "hp": 80.0, "damage": 16.0, "poise": 35.0, "speed": 2.8,
		"tell": 0.2, "reach": 1.8, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "darter", "relics": 3,
	},
	"ash_ninja": {
		"name": "Ash Ninja", "hp": 40.0, "damage": 10.0, "poise": 12.0, "speed": 3.5,
		"tell": 0.15, "reach": 1.5, "color": Color("#6a6a6a"), "shape": "humanoid",
		"size": 11, "aggro": 8.0, "posture": "darter", "relics": 2,
	},
	"ash_mage": {
		"name": "Ash Mage", "hp": 45.0, "damage": 15.0, "poise": 12.0, "speed": 2.5,
		"tell": 0.3, "reach": 8.0, "color": Color("#8a6a8a"), "shape": "humanoid",
		"size": 12, "aggro": 10.0, "posture": "balanced", "ranged": true, "relics": 2,
	},
	"ash_wizard": {
		"name": "Ash Wizard", "hp": 55.0, "damage": 18.0, "poise": 15.0, "speed": 2.2,
		"tell": 0.3, "reach": 10.0, "color": Color("#9a7a9a"), "shape": "humanoid",
		"size": 13, "aggro": 12.0, "posture": "balanced", "ranged": true, "relics": 3,
	},
	"ash_hunter": {
		"name": "Ash Hunter", "hp": 45.0, "damage": 11.0, "poise": 15.0, "speed": 3.0,
		"tell": 0.25, "reach": 8.0, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 12, "aggro": 12.0, "posture": "balanced", "ranged": true, "relics": 1,
	},
	"ash_ranger": {
		"name": "Ash Ranger", "hp": 55.0, "damage": 13.0, "poise": 20.0, "speed": 2.8,
		"tell": 0.25, "reach": 10.0, "color": Color("#7a8a7a"), "shape": "humanoid",
		"size": 12, "aggro": 14.0, "posture": "balanced", "ranged": true, "relics": 2,
	},
	"ash_monk": {
		"name": "Ash Monk", "hp": 50.0, "damage": 12.0, "poise": 20.0, "speed": 3.0,
		"tell": 0.2, "reach": 1.5, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 12, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_warrior": {
		"name": "Ash Warrior", "hp": 90.0, "damage": 18.0, "poise": 45.0, "speed": 2.5,
		"tell": 0.3, "reach": 2.0, "color": Color("#7a7a7a"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "balanced", "relics": 2,
	},
	"ash_barbarian": {
		"name": "Ash Barbarian", "hp": 100.0, "damage": 20.0, "poise": 50.0, "speed": 2.8,
		"tell": 0.3, "reach": 2.2, "color": Color("#7a6a5a"), "shape": "humanoid",
		"size": 14, "aggro": 10.0, "posture": "balanced", "relics": 2,
	},
	"ash_berserker": {
		"name": "Ash Berserker", "hp": 120.0, "damage": 22.0, "poise": 60.0, "speed": 3.0,
		"tell": 0.3, "reach": 2.2, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 15, "aggro": 12.0, "posture": "balanced", "relics": 3,
	},
	"ash_rogue": {
		"name": "Ash Rogue", "hp": 35.0, "damage": 9.0, "poise": 10.0, "speed": 3.0,
		"tell": 0.2, "reach": 1.5, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 11, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_thief": {
		"name": "Ash Thief", "hp": 30.0, "damage": 8.0, "poise": 8.0, "speed": 3.5,
		"tell": 0.2, "reach": 1.5, "color": Color("#7a8a7a"), "shape": "humanoid",
		"size": 10, "aggro": 6.0, "posture": "darter", "relics": 1,
	},
	"ash_knight": {
		"name": "Ash Knight", "hp": 160.0, "damage": 22.0, "poise": 85.0, "speed": 2.2,
		"tell": 0.35, "reach": 2.5, "color": Color("#9a9a9a"), "shape": "humanoid",
		"size": 14, "aggro": 12.0, "posture": "guardian", "relics": 3,
	},
	"ash_paladin": {
		"name": "Ash Paladin", "hp": 180.0, "damage": 24.0, "poise": 90.0, "speed": 2.0,
		"tell": 0.35, "reach": 2.5, "color": Color("#aaaaaa"), "shape": "humanoid",
		"size": 15, "aggro": 10.0, "posture": "guardian", "relics": 4,
	},
	"ash_samurai": {
		"name": "Ash Samurai", "hp": 80.0, "damage": 16.0, "poise": 35.0, "speed": 2.5,
		"tell": 0.3, "reach": 2.0, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "balanced", "relics": 2,
	},
	"ash_ninja": {
		"name": "Ash Ninja", "hp": 40.0, "damage": 10.0, "poise": 12.0, "speed": 3.5,
		"tell": 0.2, "reach": 1.5, "color": Color("#6a6a6a"), "shape": "humanoid",
		"size": 11, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_goblin": {
		"name": "Ash Goblin", "hp": 20.0, "damage": 6.0, "poise": 8.0, "speed": 3.0,
		"tell": 0.25, "reach": 1.5, "color": Color("#7a8a6a"), "shape": "humanoid",
		"size": 8, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_kobold": {
		"name": "Ash Kobold", "hp": 25.0, "damage": 7.0, "poise": 10.0, "speed": 3.0,
		"tell": 0.25, "reach": 1.5, "color": Color("#8a9a7a"), "shape": "humanoid",
		"size": 9, "aggro": 10.0, "posture": "darter", "relics": 1,
	},
	"ash_mage": {
		"name": "Ash Mage", "hp": 45.0, "damage": 15.0, "poise": 12.0, "speed": 1.5,
		"tell": 0.35, "reach": 8.0, "color": Color("#8a7a9a"), "shape": "humanoid",
		"size": 12, "aggro": 12.0, "posture": "balanced", "relics": 2,
	},
	"ash_wizard": {
		"name": "Ash Wizard", "hp": 55.0, "damage": 18.0, "poise": 15.0, "speed": 1.5,
		"tell": 0.35, "reach": 8.0, "color": Color("#9a8aaa"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "balanced", "relics": 3,
	},
	"ash_hunter": {
		"name": "Ash Hunter", "hp": 50.0, "damage": 12.0, "poise": 15.0, "speed": 2.5,
		"tell": 0.3, "reach": 10.0, "color": Color("#7a8a7a"), "shape": "humanoid",
		"size": 12, "aggro": 15.0, "posture": "balanced", "relics": 2,
	},
	"ash_tracker": {
		"name": "Ash Tracker", "hp": 60.0, "damage": 14.0, "poise": 20.0, "speed": 2.5,
		"tell": 0.3, "reach": 10.0, "color": Color("#8a9a8a"), "shape": "humanoid",
		"size": 13, "aggro": 18.0, "posture": "balanced", "relics": 2,
	},
	"ash_warrior": {
		"name": "Ash Warrior", "hp": 120.0, "damage": 18.0, "poise": 60.0, "speed": 2.5,
		"tell": 0.35, "reach": 2.2, "color": Color("#7a6a5a"), "shape": "humanoid",
		"size": 13, "aggro": 12.0, "posture": "balanced", "relics": 2,
	},
	"ash_barbarian": {
		"name": "Ash Barbarian", "hp": 140.0, "damage": 20.0, "poise": 70.0, "speed": 2.5,
		"tell": 0.35, "reach": 2.2, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 14, "aggro": 14.0, "posture": "balanced", "relics": 2,
	},
	"ash_knight": {
		"name": "Ash Knight", "hp": 160.0, "damage": 22.0, "poise": 85.0, "speed": 2.0,
		"tell": 0.4, "reach": 2.5, "color": Color("#7a7a7a"), "shape": "humanoid",
		"size": 14, "aggro": 12.0, "posture": "guardian", "relics": 3,
	},
	"ash_paladin": {
		"name": "Ash Paladin", "hp": 180.0, "damage": 24.0, "poise": 90.0, "speed": 2.0,
		"tell": 0.4, "reach": 2.5, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 15, "aggro": 10.0, "posture": "guardian", "relics": 4,
	},
	"ash_wolf": {
		"name": "Ash Wolf", "hp": 30.0, "damage": 8.0, "poise": 10.0, "speed": 3.5,
		"tell": 0.25, "reach": 2.0, "color": Color("#8a8a8a"), "shape": "beast",
		"size": 10, "aggro": 15.0, "posture": "darter", "relics": 1,
	},
	"ash_bear": {
		"name": "Ash Bear", "hp": 120.0, "damage": 20.0, "poise": 50.0, "speed": 2.0,
		"tell": 0.45, "reach": 2.5, "color": Color("#6a5a4a"), "shape": "beast",
		"size": 20, "aggro": 12.0, "posture": "guardian", "relics": 3,
	},
	"ash_goblin": {
		"name": "Ash Goblin", "hp": 20.0, "damage": 6.0, "poise": 8.0, "speed": 3.0,
		"tell": 0.25, "reach": 1.5, "color": Color("#7a8a6a"), "shape": "humanoid",
		"size": 8, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_kobold": {
		"name": "Ash Kobold", "hp": 25.0, "damage": 7.0, "poise": 10.0, "speed": 2.5,
		"tell": 0.3, "reach": 1.6, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 9, "aggro": 10.0, "posture": "balanced", "relics": 1,
	},
	"ash_mage": {
		"name": "Ash Mage", "hp": 45.0, "damage": 15.0, "poise": 10.0, "speed": 2.0,
		"tell": 0.4, "reach": 8.0, "color": Color("#8a7a9a"), "shape": "humanoid",
		"size": 12, "aggro": 12.0, "posture": "balanced", "relics": 2,
	},
	"ash_priest": {
		"name": "Ash Priest", "hp": 55.0, "damage": 10.0, "poise": 20.0, "speed": 1.8,
		"tell": 0.35, "reach": 2.0, "color": Color("#9a9a8a"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "balanced", "relics": 2,
	},
	"ash_archer": {
		"name": "Ash Archer", "hp": 35.0, "damage": 12.0, "poise": 10.0, "speed": 2.0,
		"tell": 0.35, "reach": 10.0, "color": Color("#8a9a7a"), "shape": "humanoid",
		"size": 12, "aggro": 15.0, "posture": "balanced", "relics": 1,
	},
	"ash_ranger": {
		"name": "Ash Ranger", "hp": 45.0, "damage": 14.0, "poise": 15.0, "speed": 2.5,
		"tell": 0.3, "reach": 12.0, "color": Color("#7a8a6a"), "shape": "humanoid",
		"size": 13, "aggro": 12.0, "posture": "balanced", "relics": 2,
	},
	"ash_troll": {
		"name": "Ash Troll", "hp": 250.0, "damage": 30.0, "poise": 100.0, "speed": 1.8,
		"tell": 0.5, "reach": 3.0, "color": Color("#5a6a5a"), "shape": "humanoid",
		"size": 24, "aggro": 15.0, "posture": "guardian", "relics": 4,
	},
	"ash_ogre": {
		"name": "Ash Ogre", "hp": 200.0, "damage": 25.0, "poise": 80.0, "speed": 2.0,
		"tell": 0.45, "reach": 2.8, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 22, "aggro": 12.0, "posture": "balanced", "relics": 3,
	},
	"ash_zombie": {
		"name": "Ash Zombie", "hp": 60.0, "damage": 8.0, "poise": 20.0, "speed": 1.5,
		"tell": 0.5, "reach": 1.8, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 14, "aggro": 8.0, "posture": "balanced", "relics": 1,
	},
	"ash_skeleton": {
		"name": "Ash Skeleton", "hp": 50.0, "damage": 10.0, "poise": 15.0, "speed": 2.0,
		"tell": 0.35, "reach": 1.8, "color": Color("#aaaaaa"), "shape": "humanoid",
		"size": 13, "aggro": 10.0, "posture": "balanced", "relics": 1,
	},
	"ash_ghost": {
		"name": "Ash Ghost", "hp": 40.0, "damage": 10.0, "poise": 10.0, "speed": 2.5,
		"tell": 0.3, "reach": 2.0, "color": Color("#9a9aba"), "shape": "humanoid",
		"size": 12, "aggro": 12.0, "posture": "darter", "relics": 1,
	},
	"ash_spirit": {
		"name": "Ash Spirit", "hp": 30.0, "damage": 8.0, "poise": 5.0, "speed": 3.0,
		"tell": 0.25, "reach": 1.8, "color": Color("#8a8aaa"), "shape": "humanoid",
		"size": 10, "aggro": 10.0, "posture": "darter", "relics": 1,
	},
	"ash_dwarf": {
		"name": "Ash Dwarf", "hp": 70.0, "damage": 12.0, "poise": 30.0, "speed": 1.8,
		"tell": 0.4, "reach": 1.8, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 10, "aggro": 10.0, "posture": "guardian", "relics": 1,
	},
	"ash_gnome": {
		"name": "Ash Gnome", "hp": 30.0, "damage": 8.0, "poise": 10.0, "speed": 3.0,
		"tell": 0.25, "reach": 1.2, "color": Color("#9a8a7a"), "shape": "humanoid",
		"size": 7, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_warrior": {
		"name": "Ash Warrior", "hp": 120.0, "damage": 18.0, "poise": 60.0, "speed": 2.5,
		"tell": 0.35, "reach": 2.2, "color": Color("#7a7a7a"), "shape": "humanoid",
		"size": 16, "aggro": 15.0, "posture": "balanced", "relics": 2,
	},
	"ash_barbarian": {
		"name": "Ash Barbarian", "hp": 140.0, "damage": 20.0, "poise": 40.0, "speed": 3.0,
		"tell": 0.3, "reach": 2.0, "color": Color("#8a6a5a"), "shape": "humanoid",
		"size": 18, "aggro": 12.0, "posture": "darter", "relics": 2,
	},
	"ash_priest": {
		"name": "Ash Priest", "hp": 55.0, "damage": 10.0, "poise": 20.0, "speed": 2.0,
		"tell": 0.5, "reach": 2.0, "color": Color("#9a9aaa"), "shape": "humanoid",
		"size": 14, "aggro": 12.0, "posture": "balanced", "relics": 2,
	},
	"ash_knight": {
		"name": "Ash Knight", "hp": 160.0, "damage": 22.0, "poise": 85.0, "speed": 2.2,
		"tell": 0.4, "reach": 2.5, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 18, "aggro": 15.0, "posture": "guardian", "relics": 3,
	},
	"ash_goblin": {
		"name": "Ash Goblin", "hp": 20.0, "damage": 6.0, "poise": 5.0, "speed": 3.5,
		"tell": 0.2, "reach": 1.2, "color": Color("#7a9a6a"), "shape": "humanoid",
		"size": 8, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_orc": {
		"name": "Ash Orc", "hp": 120.0, "damage": 18.0, "poise": 50.0, "speed": 2.0,
		"tell": 0.4, "reach": 2.2, "color": Color("#6a8a7a"), "shape": "humanoid",
		"size": 20, "aggro": 15.0, "posture": "balanced", "relics": 2,
	},
	"ash_troll": {
		"name": "Ash Troll", "hp": 250.0, "damage": 30.0, "poise": 100.0, "speed": 1.5,
		"tell": 0.7, "reach": 3.5, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 30, "aggro": 20.0, "posture": "guardian", "relics": 4,
	},
	"ash_cyclops": {
		"name": "Ash Cyclops", "hp": 200.0, "damage": 25.0, "poise": 80.0, "speed": 1.8,
		"tell": 0.6, "reach": 3.0, "color": Color("#7a8a7a"), "shape": "humanoid",
		"size": 25, "aggro": 18.0, "posture": "guardian", "relics": 3,
	},
	"ash_mage": {
		"name": "Ash Mage", "hp": 45.0, "damage": 15.0, "poise": 10.0, "speed": 2.0,
		"tell": 0.6, "reach": 8.0, "color": Color("#9a8abb"), "shape": "humanoid",
		"size": 14, "aggro": 18.0, "posture": "balanced", "relics": 2,
	},
	"ash_archer": {
		"name": "Ash Archer", "hp": 35.0, "damage": 12.0, "poise": 8.0, "speed": 2.5,
		"tell": 0.4, "reach": 10.0, "color": Color("#8a9a7a"), "shape": "humanoid",
		"size": 14, "aggro": 20.0, "posture": "balanced", "relics": 1,
	},
	"ash_zombie": {
		"name": "Ash Zombie", "hp": 60.0, "damage": 8.0, "poise": 20.0, "speed": 1.5,
		"tell": 0.5, "reach": 1.8, "color": Color("#6a8a6a"), "shape": "humanoid",
		"size": 16, "aggro": 10.0, "posture": "balanced", "relics": 1,
	},
	"ash_skeleton": {
		"name": "Ash Skeleton", "hp": 50.0, "damage": 10.0, "poise": 15.0, "speed": 2.0,
		"tell": 0.3, "reach": 2.0, "color": Color("#cccccc"), "shape": "humanoid",
		"size": 14, "aggro": 15.0, "posture": "balanced", "relics": 1,
	},
	"ash_ghost": {
		"name": "Ash Ghost", "hp": 40.0, "damage": 10.0, "poise": 10.0, "speed": 4.0,
		"tell": 0.3, "reach": 2.0, "color": Color("#aaaacc"), "shape": "humanoid",
		"size": 14, "aggro": 20.0, "posture": "darter", "relics": 1,
	},
	"ash_spirit": {
		"name": "Ash Spirit", "hp": 30.0, "damage": 8.0, "poise": 5.0, "speed": 5.0,
		"tell": 0.2, "reach": 1.5, "color": Color("#bbccdd"), "shape": "humanoid",
		"size": 10, "aggro": 25.0, "posture": "darter", "relics": 1,
	},
	"ash_giant": {
		"name": "Ash Giant", "hp": 300.0, "damage": 35.0, "poise": 120.0, "speed": 1.8,
		"tell": 0.8, "reach": 4.0, "color": Color("#5a5a5a"), "shape": "humanoid",
		"size": 35, "aggro": 25.0, "posture": "guardian", "relics": 5,
	},
	"ash_dwarf": {
		"name": "Ash Dwarf", "hp": 70.0, "damage": 12.0, "poise": 30.0, "speed": 2.5,
		"tell": 0.3, "reach": 1.5, "color": Color("#6a6a6a"), "shape": "humanoid",
		"size": 10, "aggro": 12.0, "posture": "balanced", "relics": 1,
	},
	"ash_knight": {
		"name": "Ash Knight", "hp": 160.0, "damage": 22.0, "poise": 85.0, "speed": 2.2,
		"tell": 0.4, "reach": 2.5, "color": Color("#8a8a8a"), "shape": "humanoid",
		"size": 18, "aggro": 15.0, "posture": "guardian", "relics": 3,
	},
	"ash_warrior": {
		"name": "Ash Warrior", "hp": 120.0, "damage": 18.0, "poise": 60.0, "speed": 2.8,
		"tell": 0.3, "reach": 2.2, "color": Color("#7a7a7a"), "shape": "humanoid",
		"size": 16, "aggro": 18.0, "posture": "balanced", "relics": 2,
	},
	"ash_archer": {
		"name": "Ash Archer", "hp": 35.0, "damage": 12.0, "poise": 8.0, "speed": 3.0,
		"tell": 0.4, "reach": 10.0, "color": Color("#7a8a6a"), "shape": "humanoid",
		"size": 14, "aggro": 25.0, "posture": "ranged", "relics": 1,
	},
	"ash_priest": {
		"name": "Ash Priest", "hp": 55.0, "damage": 10.0, "poise": 20.0, "speed": 2.5,
		"tell": 0.5, "reach": 3.0, "color": Color("#9a8a7a"), "shape": "humanoid",
		"size": 14, "aggro": 15.0, "posture": "balanced", "relics": 2,
	},
	"ash_troll": {
		"name": "Ash Troll", "hp": 250.0, "damage": 30.0, "poise": 100.0, "speed": 2.0,
		"tell": 0.7, "reach": 3.5, "color": Color("#6a6a5a"), "shape": "humanoid",
		"size": 28, "aggro": 20.0, "posture": "guardian", "relics": 4,
	},
	"ash_dwarf": {
		"name": "Ash Dwarf", "hp": 80.0, "damage": 15.0, "poise": 40.0, "speed": 2.2,
		"tell": 0.3, "reach": 1.8, "color": Color("#7a6a5a"), "shape": "humanoid",
		"size": 10, "aggro": 12.0, "posture": "balanced", "relics": 1,
	},
	"ash_mage": {
		"name": "Ash Mage", "hp": 45.0, "damage": 16.0, "poise": 12.0, "speed": 2.5,
		"tell": 0.6, "reach": 8.0, "color": Color("#8a6a9a"), "shape": "humanoid",
		"size": 14, "aggro": 20.0, "posture": "ranged", "relics": 2,
	},
	"ash_rogue": {
		"name": "Ash Rogue", "hp": 40.0, "damage": 13.0, "poise": 10.0, "speed": 4.2,
		"tell": 0.2, "reach": 1.5, "color": Color("#7a7a6a"), "shape": "humanoid",
		"size": 12, "aggro": 10.0, "posture": "darter", "relics": 1,
	},
	"ash_giant": {
		"name": "Ash Giant", "hp": 300.0, "damage": 35.0, "poise": 120.0, "speed": 1.5,
		"tell": 0.8, "reach": 4.0, "color": Color("#7a7a7a"), "shape": "humanoid",
		"size": 32, "aggro": 25.0, "posture": "guardian", "relics": 5,
	},
	"ash_goblin": {
		"name": "Ash Goblin", "hp": 25.0, "damage": 6.0, "poise": 5.0, "speed": 4.5,
		"tell": 0.2, "reach": 1.2, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 10, "aggro": 10.0, "posture": "darter", "relics": 0,
	},
	"ash_druid": {
		"name": "Ash Druid", "hp": 50.0, "damage": 14.0, "poise": 15.0, "speed": 2.5,
		"tell": 0.5, "reach": 5.0, "color": Color("#6a8a6a"), "shape": "humanoid",
		"size": 14, "aggro": 18.0, "posture": "ranged", "relics": 2,
	},
	"ash_paladin": {
		"name": "Ash Paladin", "hp": 170.0, "damage": 20.0, "poise": 90.0, "speed": 2.0,
		"tell": 0.5, "reach": 2.8, "color": Color("#9a8a7a"), "shape": "humanoid",
		"size": 18, "aggro": 15.0, "posture": "guardian", "relics": 3,
	},
	"ash_assassin": {
		"name": "Ash Assassin", "hp": 45.0, "damage": 15.0, "poise": 10.0, "speed": 4.5,
		"tell": 0.2, "reach": 1.5, "color": Color("#6a6a7a"), "shape": "humanoid",
		"size": 12, "aggro": 8.0, "posture": "darter", "relics": 1,
	},
	"ash_knight": {
		"name": "Ash Knight", "hp": 160.0, "damage": 22.0, "poise": 85.0, "speed": 2.0,
		"tell": 0.5, "reach": 2.8, "color": Color("#7a7a8a"), "shape": "humanoid",
		"size": 18, "aggro": 15.0, "posture": "guardian", "relics": 3,
	},
	"ash_wizard": {
		"name": "Ash Wizard", "hp": 40.0, "damage": 18.0, "poise": 10.0, "speed": 2.5,
		"tell": 0.6, "reach": 8.0, "color": Color("#7a6a9a"), "shape": "humanoid",
		"size": 14, "aggro": 20.0, "posture": "ranged", "relics": 2,
	},
	"ash_barbarian": {
		"name": "Ash Barbarian", "hp": 120.0, "damage": 25.0, "poise": 30.0, "speed": 2.8,
		"tell": 0.4, "reach": 2.0, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 18, "aggro": 20.0, "posture": "darter", "relics": 2,
	},
	"ash_thief": {
		"name": "Ash Thief", "hp": 35.0, "damage": 10.0, "poise": 8.0, "speed": 4.0,
		"tell": 0.25, "reach": 1.5, "color": Color("#7a7a8a"), "shape": "humanoid",
		"size": 12, "aggro": 10.0, "posture": "darter", "relics": 1,
	},
	"ash_monk": {
		"name": "Ash Monk", "hp": 60.0, "damage": 12.0, "poise": 25.0, "speed": 3.0,
		"tell": 0.3, "reach": 1.5, "color": Color("#8a8a7a"), "shape": "humanoid",
		"size": 14, "aggro": 15.0, "posture": "dancer", "relics": 2,
	},
	"ash_berserker": {
		"name": "Ash Berserker", "hp": 100.0, "damage": 22.0, "poise": 20.0, "speed": 3.5,
		"tell": 0.3, "reach": 2.0, "color": Color("#8a6a6a"), "shape": "humanoid",
		"size": 16, "aggro": 20.0, "posture": "darter", "relics": 2,
	},
	"ash_paladin": {
		"name": "Ash Paladin", "hp": 180.0, "damage": 20.0, "poise": 90.0, "speed": 2.0,
		"tell": 0.5, "reach": 2.8, "color": Color("#9a8a7a"), "shape": "humanoid",
		"size": 18, "aggro": 15.0, "posture": "guardian", "relics": 3,
	},
	"ash_slayer": {
		"name": "Ash Slayer", "hp": 80.0, "damage": 18.0, "poise": 30.0, "speed": 3.0,
		"tell": 0.4, "reach": 2.5, "color": Color("#7a6a7a"), "shape": "humanoid",
		"size": 16, "aggro": 18.0, "posture": "darter", "relics": 2,
	},
	"ash_champion": {
		"name": "Ash Champion", "hp": 200.0, "damage": 25.0, "poise": 100.0, "speed": 2.2,
		"tell": 0.5, "reach": 3.0, "color": Color("#8a7a8a"), "shape": "humanoid",
		"size": 20, "aggro": 20.0, "posture": "guardian", "relics": 3,
	},
	"ash_archer": {
		"name": "Ash Archer", "hp": 30.0, "damage": 12.0, "poise": 8.0, "speed": 3.0,
		"tell": 0.4, "reach": 10.0, "color": Color("#8a7a6a"), "shape": "humanoid",
		"size": 12, "aggro": 20.0, "posture": "ranged", "relics": 1,
	},
	"ash_priest": {
		"name": "Ash Priest", "hp": 50.0, "damage": 8.0, "poise": 20.0, "speed": 2.5,
		"tell": 0.5, "reach": 1.5, "color": Color("#9a8a9a"), "shape": "humanoid",
		"size": 14, "aggro": 15.0, "posture": "dancer", "relics": 2,
	},
	"ash_goblin": {
		"name": "Ash Goblin", "hp": 20.0, "damage": 6.0, "poise": 5.0, "speed": 3.5,
		"tell": 0.3, "reach": 1.5, "color": Color("#7a8a6a"), "shape": "humanoid",
		"size": 8, "aggro": 12.0, "posture": "darter", "relics": 0,
	},
	"ash_troll": {
		"name": "Ash Troll", "hp": 250.0, "damage": 35.0, "poise": 120.0, "speed": 1.8,
		"tell": 0.8, "reach": 3.5, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 25, "aggro": 20.0, "posture": "bulwark", "relics": 3,
	},
	"iron_knight": {
		"name": "Iron Knight", "hp": 150.0, "damage": 20.0, "poise": 80.0, "speed": 2.0,
		"tell": 0.5, "reach": 3.0, "color": Color("#6a6a7a"), "shape": "humanoid",
		"size": 18, "aggro": 15.0, "posture": "guardian", "relics": 2,
	},
	"ash_mage": {
		"name": "Ash Mage", "hp": 45.0, "damage": 15.0, "poise": 10.0, "speed": 2.5,
		"tell": 0.6, "reach": 8.0, "color": Color("#7a6a8a"), "shape": "humanoid",
		"size": 14, "aggro": 20.0, "posture": "ranged", "relics": 2,
	},
	"ash_ghost": {
		"name": "Ash Ghost", "hp": 35.0, "damage": 10.0, "poise": 8.0, "speed": 4.0,
		"tell": 0.25, "reach": 2.0, "color": Color("#9a9aaa"), "shape": "humanoid",
		"size": 12, "aggro": 18.0, "posture": "dancer", "relics": 1,
	},
	"skeleton_warrior": {
		"name": "Skeleton Warrior", "hp": 45.0, "damage": 11.0, "poise": 18.0, "speed": 2.8,
		"tell": 0.45, "reach": 2.2, "color": Color("#b0b0a0"), "shape": "humanoid",
		"size": 14, "aggro": 14.0, "posture": "guardian", "relics": 1,
	},
	"shield_bearer": {
		"name": "Shield Bearer", "hp": 100.0, "damage": 12.0, "poise": 60.0, "speed": 1.8,
		"tell": 0.6, "reach": 2.5, "color": Color("#6a7a6a"), "shape": "humanoid",
		"size": 15, "aggro": 12.0, "posture": "bulwark", "relics": 1,
	},
	"swarm_spitter": {
		"name": "Swarm Spitter", "hp": 25.0, "damage": 8.0, "poise": 5.0, "speed": 2.5,
		"tell": 0.3, "reach": 5.0, "color": Color("#7a8a5a"), "shape": "beast",
		"size": 8, "aggro": 15.0, "posture": "ranged", "relics": 0,
	},
	"burrower": {
		"name": "Burrower", "hp": 60.0, "damage": 15.0, "poise": 30.0, "speed": 2.0,
		"tell": 0.8, "reach": 2.0, "color": Color("#5a4a3a"), "shape": "beast",
		"size": 15, "aggro": 10.0, "posture": "bulwark", "relics": 1,
	},
	"ash_wraith": {
		"name": "Ash Wraith", "hp": 50.0, "damage": 12.0, "poise": 20.0, "speed": 3.0,
		"tell": 0.4, "reach": 2.5, "color": Color("#8a8a9a"), "shape": "humanoid",
		"size": 15, "aggro": 20.0, "posture": "dancer", "relics": 1,
	},
	"iron_golem": {
		"name": "Iron Golem", "hp": 200.0, "damage": 25.0, "poise": 120.0, "speed": 1.0,
		"tell": 1.0, "reach": 2.0, "color": Color("#6a6a6a"), "shape": "humanoid",
		"size": 30, "aggro": 10.0, "posture": "bulwark", "relics": 3,
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

## Building recipes: building_id -> {materials, name, description}
const BUILDINGS := {
	"warehouse": {"materials": {"timber": 10, "iron": 2}, "name": "Warehouse", "description": "Stores extra resources."},
	"training_grounds": {"materials": {"timber": 5, "iron": 5}, "name": "Training Grounds", "description": "Villagers train to become better fighters."},
	"library": {"materials": {"timber": 8, "relic": 1}, "name": "Library", "description": "Preserves knowledge of the old world."},
	"wall": {"materials": {"timber": 15, "iron": 5}, "name": "Settlement Wall", "description": "Protects the settlement from raids."},
	"watchtower": {"materials": {"timber": 10, "iron": 3}, "name": "Watchtower", "description": "Early warning of approaching threats."},
	"barracks": {"materials": {"timber": 8, "iron": 8}, "name": "Barracks", "description": "Houses additional defenders."},
	"market": {"materials": {"timber": 12, "iron": 2}, "name": "Market", "description": "Villagers can trade with travelers."},
	"herbalist": {"materials": {"timber": 6, "relic": 1}, "name": "Herbalist", "description": "Crafts healing potions."},
	"stables": {"materials": {"timber": 10, "iron": 2}, "name": "Stables", "description": "Houses pack animals for expeditions."},
	"granary": {"materials": {"timber": 8}, "name": "Granary", "description": "Stores food for the settlement."},
	"well": {"materials": {"iron": 3, "timber": 4}, "name": "Well", "description": "Provides clean water."},
	"forge": {"materials": {"iron": 5, "timber": 5}, "name": "Forge", "description": "Enhances weapon crafting."},
	"church": {"materials": {"timber": 15, "iron": 5}, "name": "Church", "description": "Reduces grief over time."},
	"library": {"materials": {"timber": 10, "relic": 2}, "name": "Library", "description": "Unlocks new recipes."},
	"observatory": {"materials": {"iron": 5, "relic": 3}, "name": "Observatory", "description": "Predicts settlement events."},
	"bathhouse": {"materials": {"timber": 8, "iron": 2}, "name": "Bathhouse", "description": "Restores composure faster."},
	"tavern": {"materials": {"timber": 12, "iron": 3}, "name": "Tavern", "description": "Villagers gain morale."},
	"smithy": {"materials": {"iron": 8, "timber": 6}, "name": "Smithy", "description": "Unlocks advanced weapon upgrades."},
	"granary": {"materials": {"timber": 8, "iron": 2}, "name": "Granary", "description": "Stores food for winter."},
	"well": {"materials": {"iron": 2, "timber": 4}, "name": "Well", "description": "Provides clean water."},
	"stable": {"materials": {"timber": 8, "iron": 2}, "name": "Stable", "description": "Houses horses for travel."},
	"church": {"materials": {"iron": 4, "timber": 10}, "name": "Church", "description": "Provides spiritual comfort."},
	"observatory": {"materials": {"iron": 5, "relic": 3}, "name": "Observatory", "description": "Predicts weather and events."},
	"bathhouse": {"materials": {"timber": 8, "iron": 3}, "name": "Bathhouse", "description": "Restores villager health."},
	"bakery": {"materials": {"timber": 6, "iron": 1}, "name": "Bakery", "description": "Bakes bread for villagers."},
	"brewery": {"materials": {"timber": 8, "iron": 2}, "name": "Brewery", "description": "Brews ale for villagers."},
	"library": {"materials": {"iron": 3, "timber": 8}, "name": "Library", "description": "Teaches villagers new skills."},
	"market": {"materials": {"timber": 10, "iron": 2}, "name": "Market", "description": "Increases trade income."},
	"temple": {"materials": {"iron": 6, "timber": 12}, "name": "Temple", "description": "Provides divine blessings."},
	"academy": {"materials": {"iron": 4, "timber": 10}, "name": "Academy", "description": "Trains skilled villagers."},
	"hospital": {"materials": {"iron": 3, "timber": 8}, "name": "Hospital", "description": "Heals injured villagers."},
	"watchtower": {"materials": {"iron": 2, "timber": 6}, "name": "Watchtower", "description": "Spots approaching enemies."},
	"stables": {"materials": {"timber": 8}, "name": "Stables", "description": "Houses horses for travel."},
	"stable": {"materials": {"timber": 8}, "name": "Stable", "description": "Houses one horse."},
	"lighthouse": {"materials": {"iron": 4, "timber": 6}, "name": "Lighthouse", "description": "Guides ships safely."},
	"granary": {"materials": {"timber": 10}, "name": "Granary", "description": "Stores food for the settlement."},
	"bakery": {"materials": {"timber": 8}, "name": "Bakery", "description": "Bakes bread for the settlement."},
	"brewery": {"materials": {"timber": 10}, "name": "Brewery", "description": "Brews ale for the settlement."},
	"tavern": {"materials": {"timber": 12}, "name": "Tavern", "description": "A place for villagers to gather."},
	"market": {"materials": {"timber": 10}, "name": "Market", "description": "A place for villagers to trade."},
	"inn": {"materials": {"timber": 10}, "name": "Inn", "description": "A place for travelers to rest."},
	"bathhouse": {"materials": {"timber": 8}, "name": "Bathhouse", "description": "A place for villagers to relax."},
	"temple": {"materials": {"timber": 15}, "name": "Temple", "description": "A place for worship."},
	"library": {"materials": {"timber": 12}, "name": "Library", "description": "A place for learning."},
	"market": {"materials": {"timber": 10}, "name": "Market", "description": "A place for trade."},
	"barracks": {"materials": {"timber": 15}, "name": "Barracks", "description": "Houses for guards."},
	"granary": {"materials": {"timber": 12}, "name": "Granary", "description": "Stores food."},
	"tower": {"materials": {"timber": 20}, "name": "Watchtower", "description": "Watchtower for defense."},
	"chapel": {"materials": {"timber": 15}, "name": "Chapel", "description": "A place of worship."},
	"smithy": {"materials": {"iron": 5, "timber": 5}, "name": "Smithy", "description": "Crafts iron items."},
	"stable": {"materials": {"timber": 10}, "name": "Stable", "description": "Houses horses."},
	"library": {"materials": {"timber": 15}, "name": "Library", "description": "Houses books and knowledge."},
	"bakery": {"materials": {"timber": 8}, "name": "Bakery", "description": "Bakes bread."},
	"tavern": {"materials": {"timber": 12}, "name": "Tavern", "description": "Serves drinks and food."},
	"market": {"materials": {"timber": 10}, "name": "Market", "description": "Trades goods."},
	"well": {"materials": {"stone": 5}, "name": "Well", "description": "Provides fresh water."},
	"mill": {"materials": {"timber": 8, "stone": 3}, "name": "Mill", "description": "Grinds grain into flour."},
	"inn": {"materials": {"timber": 15}, "name": "Inn", "description": "Provides lodging for travelers."},
	"library": {"materials": {"timber": 12, "stone": 5}, "name": "Library", "description": "Stores knowledge and scrolls."},
	"bathhouse": {"materials": {"stone": 8}, "name": "Bathhouse", "description": "Provides bathing facilities for villagers."},
	"market": {"materials": {"timber": 10}, "name": "Market", "description": "Central trading hub for villagers."},
	"stable": {"materials": {"timber": 8, "stone": 2}, "name": "Stable", "description": "Houses horses and livestock."},
	"barn": {"materials": {"timber": 10}, "name": "Barn", "description": "Stores crops and equipment."},
	"windmill": {"materials": {"timber": 12}, "name": "Windmill", "description": "Grinds grain into flour."},
	"lumber_mill": {"materials": {"timber": 8, "stone": 4}, "name": "Lumber Mill", "description": "Processes wood into lumber."},
	"ironworks": {"materials": {"timber": 6, "stone": 8}, "name": "Ironworks", "description": "Smelts iron ore into iron ingots."},
	"smithy": {"materials": {"timber": 4, "stone": 6}, "name": "Smithy", "description": "Forges weapons and armor."},
	"tavern": {"materials": {"timber": 10}, "name": "Tavern", "description": "A place for villagers to gather and drink."},
	"library": {"materials": {"timber": 8, "stone": 4}, "name": "Library", "description": "Stores knowledge and scrolls."},
	"chapel": {"materials": {"timber": 6, "stone": 8}, "name": "Chapel", "description": "A place for prayer and reflection."},
	"bathhouse": {"materials": {"stone": 10, "timber": 4}, "name": "Bathhouse", "description": "A place for villagers to relax and bathe."},
	"market": {"materials": {"timber": 8, "stone": 2}, "name": "Market", "description": "A place for trading goods."},
	"school": {"materials": {"timber": 8, "stone": 4}, "name": "School", "description": "A place for children to learn."},
	"library": {"materials": {"timber": 8, "stone": 4}, "name": "Library", "description": "A place to store books and knowledge."},
	"bakery": {"materials": {"timber": 6, "stone": 2}, "name": "Bakery", "description": "Produces bread and pastries."},
	"brewery": {"materials": {"timber": 6, "stone": 4}, "name": "Brewery", "description": "Produces beer and ale."},
	"windmill": {"materials": {"timber": 8, "stone": 4}, "name": "Windmill", "description": "Grinds grain into flour."},
	"quarry": {"materials": {"stone": 8}, "name": "Quarry", "description": "Extracts stone for building."},
	"fishery": {"materials": {"timber": 6, "stone": 2}, "name": "Fishery", "description": "Provides fish for villagers."},
	"pasture": {"materials": {"timber": 8}, "name": "Pasture", "description": "Raises livestock for villagers."},
	"apiary": {"materials": {"timber": 6}, "name": "Apiary", "description": "Produces honey for villagers."},
	"vineyard": {"materials": {"timber": 8, "stone": 2}, "name": "Vineyard", "description": "Grows grapes for wine."},
	"orchard": {"materials": {"timber": 8}, "name": "Orchard", "description": "Grows fruit for villagers."},
	"greenhouse": {"materials": {"timber": 10, "stone": 4}, "name": "Greenhouse", "description": "Grows exotic plants year-round."},
	"windmill": {"materials": {"timber": 12, "stone": 6}, "name": "Windmill", "description": "Grinds grain into flour."},
	"quarry": {"materials": {"stone": 15}, "name": "Quarry", "description": "Extracts stone for building."},
	"fishery": {"materials": {"timber": 8}, "name": "Fishery", "description": "Provides fish for villagers."},
	"pasture": {"materials": {"timber": 6}, "name": "Pasture", "description": "Grassland for grazing animals."},
	"farm": {"materials": {"timber": 6}, "name": "Farm", "description": "Produces food for villagers."},
	"barracks": {"materials": {"iron": 4, "timber": 8}, "name": "Barracks", "description": "Trains more companions."},
	"market": {"materials": {"timber": 10, "iron": 3}, "name": "Market", "description": "Better trade prices."},
	"lumber_mill": {"materials": {"timber": 8, "iron": 2}, "name": "Lumber Mill", "description": "Produces timber automatically."},
	"iron_mine": {"materials": {"iron": 5, "timber": 6}, "name": "Iron Mine", "description": "Produces iron automatically."},
	"relic_temple": {"materials": {"relic": 5, "iron": 3}, "name": "Relic Temple", "description": "Produces relics automatically."},
	"school": {"materials": {"timber": 12, "iron": 3}, "name": "School", "description": "Villagers learn new skills."},
	"hospital": {"materials": {"timber": 10, "iron": 4}, "name": "Hospital", "description": "Heals injured villagers."},
	"farmhouse": {"materials": {"timber": 6}, "name": "Farmhouse", "description": "Houses farm workers."},
	"library": {"materials": {"timber": 15, "iron": 5}, "name": "Library", "description": "Stores knowledge and scrolls."},
	"bathhouse": {"materials": {"timber": 8, "iron": 3}, "name": "Bathhouse", "description": "Restores villager health."},
	"armory": {"materials": {"iron": 8, "timber": 5}, "name": "Armory", "description": "Stores weapons and armor."},
	"observatory": {"materials": {"iron": 5, "relic": 3}, "name": "Observatory", "description": "Predicts weather and events."},
	"tavern": {"materials": {"timber": 12, "iron": 2}, "name": "Tavern", "description": "Villagers relax and share stories."},
	"smithy": {"materials": {"iron": 8, "timber": 6}, "name": "Smithy", "description": "Unlocks advanced weapon upgrades."},
}

## Villager dialogue options
const VILLAGER_DIALOGUE := {
	"trader": [
		{"text": "What do you have for sale?", "response": "I have iron ore and timber. Good quality, from the old mines."},
		{"text": "Tell me about the ash-waste.", "response": "It was once farmland. The ash came down and nothing grew after."},
		{"text": "Any advice for a new wielder?", "response": "Don't swing too hard. The ash-things tire you out."},
	],
	"elder": [
		{"text": "What happened to the old world?", "response": "The sky cracked and the embers fell. We buried what we could."},
		{"text": "Tell me about the blade.", "response": "It chooses who carries it. Not the other way around."},
		{"text": "How do we survive?", "response": "We remember. That's how we survive."},
	],
	"blacksmith": [
		{"text": "Can you forge me a weapon?", "response": "Bring me iron and I'll see what I can do."},
		{"text": "What's the best metal?", "response": "Iron from the old mines. Nothing else holds an edge."},
		{"text": "Tell me about the old forges.", "response": "They burned hot and never stopped. Now we make do."},
	],
}

## Crafting recipes: item_id -> {materials, result, result_type}
const RECIPES := {
	"iron_sword": {"materials": {"iron": 3, "timber": 1}, "result": "iron_sword", "result_type": "weapon"},
	"oathbreaker": {"materials": {"iron": 5, "relic": 1}, "result": "oathbreaker", "result_type": "weapon"},
	"twin_cinders": {"materials": {"iron": 2, "timber": 1}, "result": "twin_cinders", "result_type": "weapon"},
	"long_spear": {"materials": {"timber": 2, "iron": 1}, "result": "long_spear", "result_type": "weapon"},
	"great_axe": {"materials": {"iron": 4, "timber": 2}, "result": "great_axe", "result_type": "weapon"},
	"healing_poultice": {"materials": {"timber": 1}, "result": "healing_poultice", "result_type": "consumable"},
	"iron_shield": {"materials": {"iron": 3, "timber": 2}, "result": "iron_shield", "result_type": "shield"},
	"leather_armor": {"materials": {"timber": 4}, "result": "leather_armor", "result_type": "armor"},
	"iron_helm": {"materials": {"iron": 2, "timber": 1}, "result": "iron_helm", "result_type": "armor"},
	"chainmail": {"materials": {"iron": 5}, "result": "chainmail", "result_type": "armor"},
	"iron_boots": {"materials": {"iron": 2, "timber": 1}, "result": "iron_boots", "result_type": "armor"},
	"iron_gauntlets": {"materials": {"iron": 2}, "result": "iron_gauntlets", "result_type": "armor"},
	"iron_shield": {"materials": {"iron": 3, "timber": 2}, "result": "iron_shield", "result_type": "shield"},
	"leather_helm": {"materials": {"timber": 2}, "result": "leather_helm", "result_type": "armor"},
	"leather_boots": {"materials": {"timber": 2}, "result": "leather_boots", "result_type": "armor"},
	"whip": {"materials": {"timber": 3}, "result": "whip", "result_type": "weapon"},
	"iron_fan": {"materials": {"iron": 1, "timber": 1}, "result": "iron_fan", "result_type": "weapon"},
	"iron_trident": {"materials": {"iron": 3, "timber": 2}, "result": "iron_trident", "result_type": "weapon"},
	"iron_mace": {"materials": {"iron": 4}, "result": "iron_mace", "result_type": "weapon"},
	"oak_bow": {"materials": {"timber": 4}, "result": "oak_bow", "result_type": "weapon"},
	"ember_staff": {"materials": {"timber": 3, "relic": 1}, "result": "ember_staff", "result_type": "weapon"},
	"chain_flail": {"materials": {"iron": 3, "timber": 1}, "result": "chain_flail", "result_type": "weapon"},
	"iron_halberd": {"materials": {"iron": 3, "timber": 3}, "result": "iron_halberd", "result_type": "weapon"},
	"iron_crossbow": {"materials": {"iron": 3, "timber": 2}, "result": "iron_crossbow", "result_type": "weapon"},
	"battle_axe": {"materials": {"iron": 4, "timber": 2}, "result": "battle_axe", "result_type": "weapon"},
	"chainmail": {"materials": {"iron": 5}, "result": "chainmail", "result_type": "armor"},
	"iron_shield": {"materials": {"iron": 3, "timber": 2}, "result": "iron_shield", "result_type": "shield"},
	"rapier": {"materials": {"iron": 2}, "result": "rapier", "result_type": "weapon"},
	"warhammer": {"materials": {"iron": 5, "timber": 2}, "result": "warhammer", "result_type": "weapon"},
	"scythe": {"materials": {"iron": 3, "timber": 3}, "result": "scythe", "result_type": "weapon"},
	"morningstar": {"materials": {"iron": 3, "timber": 1}, "result": "morningstar", "result_type": "weapon"},
	"katana": {"materials": {"iron": 3, "relic": 1}, "result": "katana", "result_type": "weapon"},
	"broadsword": {"materials": {"iron": 3, "timber": 1}, "result": "broadsword", "result_type": "weapon"},
	"dagger_pair": {"materials": {"iron": 1, "timber": 1}, "result": "dagger_pair", "result_type": "weapon"},
	"greatsword": {"materials": {"iron": 5, "timber": 2}, "result": "greatsword", "result_type": "weapon"},
	"trident": {"materials": {"iron": 3, "timber": 1}, "result": "trident", "result_type": "weapon"},
	"mace": {"materials": {"iron": 3, "timber": 1}, "result": "mace", "result_type": "weapon"},
	"flail": {"materials": {"iron": 3, "timber": 1}, "result": "flail", "result_type": "weapon"},
	"halberd": {"materials": {"iron": 3, "timber": 2}, "result": "halberd", "result_type": "weapon"},
	"crossbow": {"materials": {"iron": 2, "timber": 2}, "result": "crossbow", "result_type": "weapon"},
	"battle_axe": {"materials": {"iron": 3, "timber": 1}, "result": "battle_axe", "result_type": "weapon"},
	"rapier": {"materials": {"iron": 2}, "result": "rapier", "result_type": "weapon"},
	"warhammer": {"materials": {"iron": 5, "timber": 2}, "result": "warhammer", "result_type": "weapon"},
	"scythe": {"materials": {"iron": 2, "timber": 2}, "result": "scythe", "result_type": "weapon"},
	"morningstar": {"materials": {"iron": 3, "timber": 1}, "result": "morningstar", "result_type": "weapon"},
	"broadsword": {"materials": {"iron": 3, "timber": 1}, "result": "broadsword", "result_type": "weapon"},
	"dagger_pair": {"materials": {"iron": 1, "timber": 1}, "result": "dagger_pair", "result_type": "weapon"},
	"katana": {"materials": {"iron": 2, "timber": 1}, "result": "katana", "result_type": "weapon"},
	"greatsword": {"materials": {"iron": 5, "timber": 2}, "result": "greatsword", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2, "timber": 1}, "result": "mace", "result_type": "weapon"},
	"flail": {"materials": {"iron": 3, "timber": 2}, "result": "flail", "result_type": "weapon"},
	"halberd": {"materials": {"iron": 4, "timber": 3}, "result": "halberd", "result_type": "weapon"},
	"glaive": {"materials": {"iron": 3, "timber": 2}, "result": "glaive", "result_type": "weapon"},
	"whip": {"materials": {"timber": 2}, "result": "whip", "result_type": "weapon"},
	"chain": {"materials": {"iron": 2}, "result": "chain", "result_type": "weapon"},
	"fan": {"materials": {"timber": 1}, "result": "fan", "result_type": "weapon"},
	"tonfa": {"materials": {"iron": 1, "timber": 1}, "result": "tonfa", "result_type": "weapon"},
	"crossbow": {"materials": {"iron": 3, "timber": 2}, "result": "crossbow", "result_type": "weapon"},
	"slingshot": {"materials": {"timber": 1}, "result": "slingshot", "result_type": "weapon"},
	"shield": {"materials": {"iron": 2, "timber": 1}, "result": "shield", "result_type": "weapon"},
	"buckler": {"materials": {"iron": 1}, "result": "buckler", "result_type": "weapon"},
	"spear": {"materials": {"iron": 1, "timber": 2}, "result": "spear", "result_type": "weapon"},
	"trident": {"materials": {"iron": 2, "timber": 1}, "result": "trident", "result_type": "weapon"},
	"hammer": {"materials": {"iron": 3}, "result": "hammer", "result_type": "weapon"},
	"maul": {"materials": {"iron": 4}, "result": "maul", "result_type": "weapon"},
	"rapier": {"materials": {"iron": 2}, "result": "rapier", "result_type": "weapon"},
	"saber": {"materials": {"iron": 2}, "result": "saber", "result_type": "weapon"},
	"scythe": {"materials": {"iron": 2, "timber": 1}, "result": "scythe", "result_type": "weapon"},
	"flail": {"materials": {"iron": 2}, "result": "flail", "result_type": "weapon"},
	"lance": {"materials": {"iron": 2, "timber": 2}, "result": "lance", "result_type": "weapon"},
	"pike": {"materials": {"iron": 2, "timber": 3}, "result": "pike", "result_type": "weapon"},
	"glaive": {"materials": {"iron": 2, "timber": 2}, "result": "glaive", "result_type": "weapon"},
	"halberd": {"materials": {"iron": 3, "timber": 2}, "result": "halberd", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2}, "result": "mace", "result_type": "weapon"},
	"morning_star": {"materials": {"iron": 2}, "result": "morning_star", "result_type": "weapon"},
	"flail": {"materials": {"iron": 2}, "result": "flail", "result_type": "weapon"},
	"warhammer": {"materials": {"iron": 3}, "result": "warhammer", "result_type": "weapon"},
	"spear": {"materials": {"iron": 1, "timber": 1}, "result": "spear", "result_type": "weapon"},
	"trident": {"materials": {"iron": 2, "timber": 1}, "result": "trident", "result_type": "weapon"},
	"bow": {"materials": {"timber": 2}, "result": "bow", "result_type": "weapon"},
	"crossbow": {"materials": {"iron": 2, "timber": 1}, "result": "crossbow", "result_type": "weapon"},
	"staff": {"materials": {"timber": 3}, "result": "staff", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2}, "result": "mace", "result_type": "weapon"},
	"whip": {"materials": {"timber": 1}, "result": "whip", "result_type": "weapon"},
	"chain": {"materials": {"iron": 1}, "result": "chain", "result_type": "weapon"},
	"fan": {"materials": {"timber": 1}, "result": "fan", "result_type": "weapon"},
	"tonfa": {"materials": {"timber": 1}, "result": "tonfa", "result_type": "weapon"},
	"halberd": {"materials": {"iron": 2, "timber": 2}, "result": "halberd", "result_type": "weapon"},
	"glaive": {"materials": {"iron": 2, "timber": 2}, "result": "glaive", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2}, "result": "mace", "result_type": "weapon"},
	"flail": {"materials": {"iron": 2}, "result": "flail", "result_type": "weapon"},
	"warhammer": {"materials": {"iron": 3}, "result": "warhammer", "result_type": "weapon"},
	"morning_star": {"materials": {"iron": 2}, "result": "morning_star", "result_type": "weapon"},
	"spear": {"materials": {"timber": 2}, "result": "spear", "result_type": "weapon"},
	"trident": {"materials": {"iron": 2, "timber": 1}, "result": "trident", "result_type": "weapon"},
	"bow": {"materials": {"timber": 2}, "result": "bow", "result_type": "weapon"},
	"arrow": {"materials": {"timber": 1}, "result": "arrow", "result_type": "weapon"},
	"katana": {"materials": {"iron": 3}, "result": "katana", "result_type": "weapon"},
	"wakizashi": {"materials": {"iron": 2}, "result": "wakizashi", "result_type": "weapon"},
	"broadsword": {"materials": {"iron": 3}, "result": "broadsword", "result_type": "weapon"},
	"longsword": {"materials": {"iron": 3}, "result": "longsword", "result_type": "weapon"},
	"dagger": {"materials": {"iron": 1}, "result": "dagger", "result_type": "weapon"},
	"short_sword": {"materials": {"iron": 2}, "result": "short_sword", "result_type": "weapon"},
	"great_sword": {"materials": {"iron": 4}, "result": "great_sword", "result_type": "weapon"},
	"battle_axe": {"materials": {"iron": 4}, "result": "battle_axe", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2}, "result": "mace", "result_type": "weapon"},
	"war_hammer": {"materials": {"iron": 3}, "result": "war_hammer", "result_type": "weapon"},
	"spear": {"materials": {"timber": 2, "iron": 1}, "result": "spear", "result_type": "weapon"},
	"trident": {"materials": {"timber": 2, "iron": 2}, "result": "trident", "result_type": "weapon"},
	"bow": {"materials": {"timber": 3}, "result": "bow", "result_type": "weapon"},
	"crossbow": {"materials": {"timber": 2, "iron": 2}, "result": "crossbow", "result_type": "weapon"},
	"katana": {"materials": {"iron": 3}, "result": "katana", "result_type": "weapon"},
	"wakizashi": {"materials": {"iron": 2}, "result": "wakizashi", "result_type": "weapon"},
	"dagger": {"materials": {"iron": 1}, "result": "dagger", "result_type": "weapon"},
	"rapier": {"materials": {"iron": 2}, "result": "rapier", "result_type": "weapon"},
	"maul": {"materials": {"iron": 3}, "result": "maul", "result_type": "weapon"},
	"greataxe": {"materials": {"iron": 3}, "result": "greataxe", "result_type": "weapon"},
	"flail": {"materials": {"iron": 2, "timber": 1}, "result": "flail", "result_type": "weapon"},
	"morning_star": {"materials": {"iron": 2}, "result": "morning_star", "result_type": "weapon"},
	"halberd": {"materials": {"iron": 2, "timber": 2}, "result": "halberd", "result_type": "weapon"},
	"glaive": {"materials": {"iron": 2, "timber": 2}, "result": "glaive", "result_type": "weapon"},
	"spear": {"materials": {"iron": 1, "timber": 2}, "result": "spear", "result_type": "weapon"},
	"trident": {"materials": {"iron": 1, "timber": 2}, "result": "trident", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2}, "result": "mace", "result_type": "weapon"},
	"war_hammer": {"materials": {"iron": 3}, "result": "war_hammer", "result_type": "weapon"},
	"crossbow": {"materials": {"iron": 1, "timber": 1}, "result": "crossbow", "result_type": "weapon"},
	"slingshot": {"materials": {"timber": 1}, "result": "slingshot", "result_type": "weapon"},
	"boomerang": {"materials": {"timber": 2}, "result": "boomerang", "result_type": "weapon"},
	"throwing_knife": {"materials": {"iron": 1}, "result": "throwing_knife", "result_type": "weapon"},
	"torch": {"materials": {"timber": 1}, "result": "torch", "result_type": "weapon"},
	"lantern": {"materials": {"iron": 1, "timber": 1}, "result": "lantern", "result_type": "weapon"},
	"bow": {"materials": {"timber": 2, "iron": 1}, "result": "bow", "result_type": "weapon"},
	"shortbow": {"materials": {"timber": 1, "iron": 1}, "result": "shortbow", "result_type": "weapon"},
	"dagger": {"materials": {"iron": 1}, "result": "dagger", "result_type": "weapon"},
	"short_sword": {"materials": {"iron": 2}, "result": "short_sword", "result_type": "weapon"},
	"greatsword": {"materials": {"iron": 3, "timber": 1}, "result": "greatsword", "result_type": "weapon"},
	"broadsword": {"materials": {"iron": 3}, "result": "broadsword", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2}, "result": "mace", "result_type": "weapon"},
	"flail": {"materials": {"iron": 2, "timber": 1}, "result": "flail", "result_type": "weapon"},
	"warhammer": {"materials": {"iron": 3, "timber": 1}, "result": "warhammer", "result_type": "weapon"},
	"morning_star": {"materials": {"iron": 2}, "result": "morning_star", "result_type": "weapon"},
	"halberd": {"materials": {"iron": 3, "timber": 2}, "result": "halberd", "result_type": "weapon"},
	"glaive": {"materials": {"iron": 3, "timber": 1}, "result": "glaive", "result_type": "weapon"},
	"spear": {"materials": {"iron": 2, "timber": 2}, "result": "spear", "result_type": "weapon"},
	"trident": {"materials": {"iron": 2, "timber": 1}, "result": "trident", "result_type": "weapon"},
	"crossbow": {"materials": {"iron": 2, "timber": 2}, "result": "crossbow", "result_type": "weapon"},
	"slingshot": {"materials": {"timber": 2}, "result": "slingshot", "result_type": "weapon"},
	"boomerang": {"materials": {"timber": 3}, "result": "boomerang", "result_type": "weapon"},
	"throwing_knife": {"materials": {"iron": 1}, "result": "throwing_knife", "result_type": "weapon"},
	"torch": {"materials": {"timber": 2}, "result": "torch", "result_type": "weapon"},
	"lantern": {"materials": {"iron": 1, "timber": 1}, "result": "lantern", "result_type": "weapon"},
	"bow": {"materials": {"timber": 4, "iron": 1}, "result": "bow", "result_type": "weapon"},
	"shortbow": {"materials": {"timber": 3}, "result": "shortbow", "result_type": "weapon"},
	"short_sword": {"materials": {"iron": 2}, "result": "short_sword", "result_type": "weapon"},
	"greatsword": {"materials": {"iron": 4}, "result": "greatsword", "result_type": "weapon"},
	"broadsword": {"materials": {"iron": 3}, "result": "broadsword", "result_type": "weapon"},
	"warhammer": {"materials": {"iron": 3, "timber": 1}, "result": "warhammer", "result_type": "weapon"},
	"mace": {"materials": {"iron": 2}, "result": "mace", "result_type": "weapon"},
	"flail": {"materials": {"iron": 2, "timber": 1}, "result": "flail", "result_type": "weapon"},
	"morning_star": {"materials": {"iron": 2, "timber": 1}, "result": "morning_star", "result_type": "weapon"},
	"halberd": {"materials": {"iron": 3, "timber": 2}, "result": "halberd", "result_type": "weapon"},
}

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
