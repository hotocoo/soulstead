class_name Expedition
extends Node3D
## The field: real-time 3D combat, a running world clock, and everything the
## settlement will have to live with afterwards.

signal returned_home()
signal wielder_fell(position: Vector3, killed_by: String)

const HOURS_PER_SECOND := 0.35
const ENEMY_BASE_COUNT := 16
const SAFE_RADIUS := 14.0
const EXIT_RADIUS := 3.0

var map: Dictionary = {}
var player: PlayerActor

var _rng := RandomNumberGenerator.new()
var _exit_position := Vector3.ZERO
var kills := 0
var _expedition_start_time := 0.0
var _remote_bodies: Dictionary = {}

func _ready() -> void:
	Look.apply_fog(self)
	_rng.seed = WorldState.world_seed + int(WorldState.world_day) * 7919
	_expedition_start_time = Time.get_ticks_msec()
	_spawn_companions()
	var location := WorldState.current_location
	var decay := WorldState.region_decay(location)
	map = MapGen.generate(WorldState.world_seed, location, decay)
	add_child(Look.environment(decay))
	add_child(Look.sun())
	TerrainBuilder.build(map, self)
	_spawn_player()
	_mark_exit()
	_spawn_enemies(location, decay)
	_spawn_echoes()
	_spawn_caches()
	_spawn_story_landmarks(location)
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("expedition_entered")
	if not NetSession.remote_state.is_connected(_on_remote_state):
		NetSession.remote_state.connect(_on_remote_state)

func _spawn_companions() -> void:
	# Spawn 1-2 companions based on settlement population
	var population := WorldState.population
	var companion_count := 1
	if population >= 5:
		companion_count = 2
	for i in range(companion_count):
		var companion := CompanionActor.new()
		companion.configure("villager", 0)
		companion.global_position = Vector3(2.0 + i * 1.5, 0.0, 1.0)
		add_child(companion)
		# Set player reference after spawning
		get_tree().create_timer(0.1).timeout.connect(func():
			if player != null:
				companion.set_player(player)
			)

func _spawn_player() -> void:
	var spawn: Vector2i = _open_near(map["spawn"])
	_exit_position = Terrain.to_world(spawn)
	player = PlayerActor.new()
	player.position = _exit_position + Vector3(0, 0.4, 0)
	player.died_in_field.connect(_on_player_died)
	add_child(player)

## The way home is a lit ring, readable from across the field.
func _mark_exit() -> void:
	for i: int in 12:
		var marker := MeshInstance3D.new()
		marker.mesh = Look._organic_ellipsoid(Vector3(0.18, 0.08, 0.34), 24, 1.6)
		marker.material_override = Look.emissive(Look.EMBER, 1.8)
		var angle := TAU * float(i) / 12.0
		marker.position = _exit_position + Vector3(cos(angle) * 2.2, 0.08, sin(angle) * 2.2)
		marker.rotation.y = -angle
		add_child(marker)
	var light := OmniLight3D.new()
	light.light_color = Look.EMBER
	light.light_energy = 2.4
	light.omni_range = 14.0
	light.position = _exit_position + Vector3(0, 2.0, 0)
	add_child(light)

func _spawn_enemies(location: String = "wrenfield", decay: int = 0) -> void:
	var count := ENEMY_BASE_COUNT + decay * 4
	var pool: Array
	match location:
		"stonewake": pool = ["warden", "warden", "husk"]
		"grey_ash": pool = ["husk", "husk", "stalker", "warden"]
		"kettlemere": pool = ["stalker", "stalker", "husk"]
		"brackwood": pool = ["husk", "stalker", "stalker"]
		"vane_road": pool = ["warden", "husk", "warden"]
		_: pool = ["husk", "husk", "stalker", "warden"] if decay >= 2 else ["husk", "husk", "husk", "stalker"]
	# High-decay regions spawn elite Keepers
	if decay >= 3:
		pool.push_back("keeper")
	var placed := 0
	var attempts := 0
	while placed < count and attempts < 4000:
		attempts += 1
		var tile := _random_open_tile()
		if tile == Vector2i(-1, -1):
			continue
		var point := Terrain.to_world(tile, 0.4)
		if point.distance_to(_exit_position) < SAFE_RADIUS:
			continue
		var enemy := EnemyActor.new()
		enemy.position = point
		add_child(enemy)
		# Enemies get stronger as the day progresses (max at dusk)
		var hour := fmod(WorldState.world_day, 1.0) * 24.0
		var time_scale := 1.0 + 0.3 * sin(hour / 24.0 * PI)  # Peaks at noon
		enemy.configure(String(pool[_rng.randi() % pool.size()]), decay)
		var diff_scale := WorldState.difficulty_multiplier()
		enemy.damage *= time_scale * diff_scale
		enemy.max_health *= time_scale * diff_scale
		enemy.health = enemy.max_health
		if String(enemy.archetype) == "warden" and WorldState.story_director != null:
			WorldState.story_director.notify_event("gravewarden_seen")
		enemy.slain.connect(_on_enemy_slain)
		enemy.spared.connect(_on_enemy_spared)
		placed += 1
	# Spawn Ash King boss in highest decay regions
	if decay >= 4:
		var boss := EnemyActor.new()
		boss.configure("ash_king", decay)
		var boss_pos := Terrain.to_world(Vector2i(0, -5), 0.4)
		boss.position = boss_pos
		var time_scale := 1.0
		var diff_scale := WorldState.difficulty_multiplier()
		boss.damage *= time_scale * diff_scale
		boss.max_health *= time_scale * diff_scale
		boss.health = boss.max_health
		boss.slain.connect(_on_enemy_slain)
		boss.spared.connect(_on_enemy_spared)
		add_child(boss)

func _spawn_story_landmarks(location: String) -> void:
	var points: Array[Dictionary] = []
	match location:
		"kettlemere":
			points.append({"tile": map.get("mere", map["village"]), "events": ["kettlemere_entered"],
					"prompt": "Examine the drowned ground", "line": "The water has kept a village outside the Ledger."})
		"brackwood":
			points.append({"tile": map.get("quarantine", map["village"]), "events": ["brackwood_entered", "quarantine_inspected"],
					"prompt": "Inspect the quarantine", "line": "Nine names are written here. Four people who signed them have kin among them."})
		"vane_road":
			points.append({"tile": map.get("vane_gate", map["village"]), "events": ["open_road_met", "vane_hold_entered"],
					"prompt": "Approach the Vane gate", "line": "The gate is barred from inside. The marks in the timber are recent."})
			points.append({"tile": map.get("vane_gate", map["village"]) + Vector2i(3, 0), "events": ["two_boards"],
					"prompt": "Read the second board", "line": "Two boards can both be honest. Neither contains the whole road."})
		"grey_ash":
			points.append({"tile": map.get("shrine", map["village"]), "events": ["ash_orchard_entered"],
					"prompt": "Enter the Ash Orchard", "line": "Seven people have gone north. The ground remembers where they sat down."})
		_:
			points.append({"tile": map.get("shrine", map["village"]), "events": ["field_landmark"],
					"prompt": "Examine the old stone", "line": "The road has a memory of feet even where the grass has forgotten them."})
	for spec: Dictionary in points:
		var tile: Vector2i = spec["tile"]
		var event_ids: Array[String] = []
		for event_id: Variant in spec["events"]:
			event_ids.append(String(event_id))
		var landmark := StoryLandmark.new()
		landmark.position = Terrain.to_world(tile, 0.2)
		add_child(landmark)
		landmark.configure(event_ids, String(spec["prompt"]), String(spec["line"]))

## Echoes stand where their owner died. Drifted Echoes from other players are
## placed at large, so they read as intruders rather than local dead.
func _spawn_echoes() -> void:
	# Echoes belong to the concrete region where their owner fell.  The old
	# implementation used the settlement-wide `vale` bucket here, which meant
	# local Echoes disappeared from expeditions and local decay never scaled the
	# field.  The Chronicle and world state both use the named route instead.
	var location := WorldState.current_location
	var decay := WorldState.region_decay(location)
	for data: Dictionary in WorldState.echoes_in(location):
		var point: Array = data["pos"]
		_add_echo(data, Vector3(float(point[0]), 0.4, float(point[1])), decay)
	for foreign: Dictionary in EchoExchange.receive_all():
		var tile := _random_open_tile()
		if tile == Vector2i(-1, -1):
			continue
		_add_echo(foreign, Terrain.to_world(tile, 0.4), decay)

func _spawn_caches() -> void:
	var spots: Array = map.get("chest_spots", [])
	for i: int in spots.size():
		var cache := FieldCache.new()
		cache.position = Terrain.to_world(spots[i], 0.12)
		cache.configure("%s:%d" % [WorldState.current_location, i])
		add_child(cache)

func _add_echo(data: Dictionary, at: Vector3, decay: int) -> void:
	var echo := EchoActor.new()
	echo.position = at
	add_child(echo)
	echo.from_echo(data, decay)
	echo.reclaimed.connect(_on_echo_reclaimed)
	if bool(data.get("foreign", false)) and WorldState.story_director != null:
		WorldState.story_director.notify_event("foreign_echo_seen")

## Spiral outward until a walkable, roofless tile turns up, so the player never
## starts the run wedged inside a ruin.
func _open_near(tile: Vector2i) -> Vector2i:
	var width: int = map["width"]
	var height: int = map["height"]
	var tiles: PackedByteArray = map["tiles"]
	for radius: int in 12:
		for dz: int in range(-radius, radius + 1):
			for dx: int in range(-radius, radius + 1):
				var x: int = tile.x + dx
				var z: int = tile.y + dz
				if x < 1 or z < 1 or x >= width - 1 or z >= height - 1:
					continue
				var kind: int = tiles[z * width + x]
				if Terrain.is_blocking(kind) or kind == Terrain.FLOOR \
						or kind == Terrain.WATER:
					continue
				return Vector2i(x, z)
	return tile

func _random_open_tile() -> Vector2i:
	var width: int = map["width"]
	var height: int = map["height"]
	var tiles: PackedByteArray = map["tiles"]
	for attempt: int in 40:
		var x := _rng.randi_range(2, width - 3)
		var z := _rng.randi_range(2, height - 3)
		var tile: int = tiles[z * width + x]
		if Terrain.is_blocking(tile) or tile == Terrain.FLOOR:
			continue
		return Vector2i(x, z)
	return Vector2i(-1, -1)

func _process(delta: float) -> void:
	# The clock only runs out here; the settlement is outside time.
	WorldState.advance_time(delta * HOURS_PER_SECOND / 24.0)
	# Update sky based on time of day
	var hour := fmod(WorldState.world_day, 1.0) * 24.0
	Look.update_sky(self, hour)
	if player != null and player.is_alive():
		NetSession.push_state({
			"x": player.global_position.x,
			"y": player.global_position.y,
			"z": player.global_position.z,
			"hp": player.health,
			"name": player.display_name,
		}, delta)
	if Input.is_action_just_pressed("interact") and _near_exit():
		if WorldState.story_director != null:
			WorldState.story_director.notify_event("expedition_returned")
		if get_tree().root.has_node("AudioManager"):
			get_tree().root.get_node("AudioManager").play_return()
		returned_home.emit()

func _near_exit() -> bool:
	return player != null and player.global_position.distance_to(_exit_position) < EXIT_RADIUS

## Co-op allies are drawn as light bodies driven by relayed state. They are
## deliberately simple: the shared thing that matters is the Chronicle.
func _on_remote_state(peer_id: int, state: Dictionary) -> void:
	var body := _remote_bodies.get(peer_id) as Node3D
	if body == null:
		body = Look.figure(Look.COLD)
		add_child(body)
		_remote_bodies[peer_id] = body
	body.global_position = Vector3(float(state.get("x", 0.0)), float(state.get("y", 0.0)),
			float(state.get("z", 0.0)))

# --- Consequence hooks ---------------------------------------------------

func _on_enemy_slain(enemy: EnemyActor) -> void:
	kills += 1
	Chronicle.record("enemy_slain", enemy.display_name)
	WorldState.faction_delta("cull", 2)
	WorldState.faction_delta("hearthkeepers", -1)
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("field_combat")
	if enemy.relics > 0:
		WorldState.materials["relic"] = int(WorldState.materials.get("relic", 0)) + enemy.relics

func _on_enemy_spared(enemy: EnemyActor) -> void:
	Chronicle.record("enemy_spared", enemy.display_name)
	WorldState.faction_delta("hearthkeepers", 2)
	WorldState.faction_delta("cull", -2)
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("gravewarden_encounter" if enemy.archetype == "warden" else "enemy_spared")

func _on_echo_reclaimed(data: Dictionary) -> void:
	if bool(data.get("foreign", false)):
		EchoExchange.resolve_foreign(data, false)
		return
	WorldState.reclaim_echo(String(data["id"]))

func _on_player_died(position: Vector3, killed_by: String) -> void:
	_show_death_recap(killed_by)
	wielder_fell.emit(position, killed_by)

func _show_death_recap(killed_by: String) -> void:
	var elapsed := (Time.get_ticks_msec() - _expedition_start_time) / 1000.0
	var minutes := int(elapsed / 60)
	var seconds := int(elapsed % 60)
	var recap := Label.new()
	recap.text = "You fell to %s\n\nKills: %d\nTime: %d:%02d" % [killed_by, kills, minutes, seconds]
	recap.position = Vector2(100, 200)
	recap.add_theme_color_override("font_color", Color(0.8, 0.4, 0.4))
	recap.add_theme_font_size_override("font_size", 16)
	get_tree().root.add_child(recap)
	# Fade out after 3 seconds
	var tween := get_tree().create_tween()
	tween.tween_interval(3.0)
	tween.tween_property(recap, "modulate:a", 0.0, 1.0)
	tween.tween_callback(recap.queue_free)
