class_name MapGen
extends RefCounted
## Deterministic overworld generation: biomes from noise, then hand-carved
## landmarks (village, road, shrine) stamped on top so the map always reads
## as a designed place rather than noise soup.

const WIDTH := 96
const HEIGHT := 72

static func generate(world_seed: int, location: String = "wrenfield", decay: int = 0) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.seed = world_seed
	var tiles := PackedByteArray()
	tiles.resize(WIDTH * HEIGHT)

	var land := FastNoiseLite.new()
	land.seed = world_seed
	land.frequency = 0.032
	var moisture := FastNoiseLite.new()
	moisture.seed = world_seed + 991
	moisture.frequency = 0.06
	var scatter := FastNoiseLite.new()
	scatter.seed = world_seed + 4242
	scatter.frequency = 0.18

	for y: int in HEIGHT:
		for x: int in WIDTH:
			tiles[y * WIDTH + x] = _base_tile(x, y, land, moisture, scatter, location, decay)

	var village := Vector2i(int(WIDTH * 0.24), int(HEIGHT * 0.62))
	var shrine := Vector2i(int(WIDTH * 0.78), int(HEIGHT * 0.20))
	var data := {
		"width": WIDTH,
		"height": HEIGHT,
		"tiles": tiles,
		"village": village,
		"shrine": shrine,
		"npc_spots": [] as Array[Vector2i],
		"chest_spots": [] as Array[Vector2i],
		"location": location,
		"location_name": WorldState.location_name(location) if Engine.has_singleton("WorldState") else location,
		"decay": decay,
	}
	if location != "wrenfield":
		village = _landmark_for(location)
		data["village"] = village
	_carve_village(data, rng)
	_carve_road(data, village, shrine)
	if location == "stonewake":
		_carve_quarry(data, village)
	elif location == "kettlemere":
		_carve_mere(data, village)
	elif location == "brackwood":
		_carve_quarantine(data, village)
	elif location == "vane_road":
		_carve_vane_wall(data, village)
	else:
		_carve_shrine(data, shrine)
	_place_chests(data, rng)
	data["spawn"] = Vector2i(village.x, village.y + 3)
	return data

static func _base_tile(x: int, y: int, land: FastNoiseLite, moisture: FastNoiseLite,
		scatter: FastNoiseLite, location: String = "wrenfield", decay: int = 0) -> int:
	var edge := _edge_falloff(x, y)
	var height := land.get_noise_2d(x, y) - edge
	if height < -0.22:
		return Terrain.WATER
	if height < -0.12:
		return Terrain.SAND
	var is_ashland := x > WIDTH * 0.58 and y < HEIGHT * 0.42
	if height > 0.34:
		return Terrain.ROCK
	if location == "grey_ash":
		return Terrain.ROCK if height > 0.30 else Terrain.ASH
	if location == "stonewake":
		return Terrain.ROCK if height > 0.05 else Terrain.SAND
	if location == "kettlemere":
		if height < 0.12:
			return Terrain.WATER
		if height < 0.20:
			return Terrain.SAND
	if location == "brackwood" and scatter.get_noise_2d(x, y) > 0.05:
		return Terrain.TREE
	if location == "vane_road" and x > WIDTH * 0.56:
		return Terrain.WALL
	if is_ashland:
		if scatter.get_noise_2d(x, y) > 0.42:
			return Terrain.ROCK
		return Terrain.ASH
	var wet := moisture.get_noise_2d(x, y)
	if scatter.get_noise_2d(x * 1.7, y * 1.7) > 0.34:
		return Terrain.TREE
	if wet > 0.12:
		return Terrain.TALL_GRASS
	if decay >= 2 and scatter.get_noise_2d(x * 2.3, y * 2.3) > 0.35:
		return Terrain.ASH
	return Terrain.GRASS

static func _landmark_for(location: String) -> Vector2i:
	match location:
		"grey_ash": return Vector2i(68, 18)
		"stonewake": return Vector2i(72, 52)
		"kettlemere": return Vector2i(68, 42)
		"brackwood": return Vector2i(28, 52)
		"vane_road": return Vector2i(78, 34)
		_: return Vector2i(42, 26)

static func _carve_quarry(data: Dictionary, center: Vector2i) -> void:
	_fill_rect(data, Rect2i(center.x - 12, center.y - 6, 24, 12), Terrain.ROCK)
	_fill_rect(data, Rect2i(center.x - 8, center.y - 3, 16, 6), Terrain.SAND)
	data["barrows"] = [Vector2i(center.x - 6, center.y - 7), Vector2i(center.x, center.y - 7), Vector2i(center.x + 6, center.y - 7)]

static func _carve_mere(data: Dictionary, center: Vector2i) -> void:
	for y: int in range(center.y - 13, center.y + 14):
		for x: int in range(center.x - 15, center.x + 16):
			if Vector2(x - center.x, (y - center.y) * 1.15).length() < 13.0:
				_set_tile(data, x, y, Terrain.WATER)
	data["mere"] = center

static func _carve_quarantine(data: Dictionary, center: Vector2i) -> void:
	for i: int in 3:
		_build_hut(data, Rect2i(center.x - 10 + i * 8, center.y - 3, 6, 5))
	data["quarantine"] = center

static func _carve_vane_wall(data: Dictionary, center: Vector2i) -> void:
	for y: int in range(8, HEIGHT - 8):
		_set_tile(data, center.x, y, Terrain.WALL)
	_set_tile(data, center.x, center.y, Terrain.PATH)
	data["vane_gate"] = center

## Pushes the map toward water at the borders so the world has a coastline.
static func _edge_falloff(x: int, y: int) -> float:
	var nx := absf(float(x) / WIDTH * 2.0 - 1.0)
	var ny := absf(float(y) / HEIGHT * 2.0 - 1.0)
	var d: float = maxf(nx, ny)
	return maxf(0.0, pow(d, 3.4) * 1.5 - 0.16)

static func _set_tile(data: Dictionary, x: int, y: int, tile: int) -> void:
	if x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT:
		return
	var tiles: PackedByteArray = data["tiles"]
	tiles[y * WIDTH + x] = tile

static func _get_tile(data: Dictionary, x: int, y: int) -> int:
	if x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT:
		return Terrain.WATER
	var tiles: PackedByteArray = data["tiles"]
	return tiles[y * WIDTH + x]

static func _fill_rect(data: Dictionary, rect: Rect2i, tile: int) -> void:
	for y: int in range(rect.position.y, rect.end.y):
		for x: int in range(rect.position.x, rect.end.x):
			_set_tile(data, x, y, tile)

static func _carve_village(data: Dictionary, rng: RandomNumberGenerator) -> void:
	var c: Vector2i = data["village"]
	for y: int in range(c.y - 10, c.y + 11):
		for x: int in range(c.x - 12, c.x + 13):
			var d := Vector2(x - c.x, (y - c.y) * 1.25).length()
			if d < 11.0:
				_set_tile(data, x, y, Terrain.GRASS)
			if d < 4.5:
				_set_tile(data, x, y, Terrain.PATH)
	var huts := [
		Rect2i(c.x - 10, c.y - 8, 7, 5),
		Rect2i(c.x + 3, c.y - 8, 8, 5),
		Rect2i(c.x - 11, c.y + 2, 8, 5),
		Rect2i(c.x + 4, c.y + 3, 7, 5),
	]
	var npc_spots: Array[Vector2i] = data["npc_spots"]
	for hut: Rect2i in huts:
		_build_hut(data, hut)
		npc_spots.append(Vector2i(hut.position.x + hut.size.x / 2, hut.end.y + 1))
	npc_spots.append(Vector2i(c.x - 3, c.y - 1))
	npc_spots.append(Vector2i(c.x + 3, c.y + 1))
	# Campfire clearing, used as the save point.
	for y: int in range(c.y - 1, c.y + 2):
		for x: int in range(c.x - 1, c.x + 2):
			_set_tile(data, x, y, Terrain.FLOOR)
	data["campfire"] = c

static func _build_hut(data: Dictionary, rect: Rect2i) -> void:
	_fill_rect(data, rect, Terrain.WALL)
	_fill_rect(data, Rect2i(rect.position + Vector2i.ONE, rect.size - Vector2i(2, 2)), Terrain.FLOOR)
	var door_x: int = rect.position.x + rect.size.x / 2
	_set_tile(data, door_x, rect.end.y - 1, Terrain.FLOOR)

static func _carve_road(data: Dictionary, from: Vector2i, to: Vector2i) -> void:
	var x: int = from.x
	var y: int = from.y
	while x != to.x:
		x += signi(to.x - x)
		for w: int in range(-1, 2):
			if _get_tile(data, x, y + w) != Terrain.WALL:
				_set_tile(data, x, y + w, Terrain.PATH)
	while y != to.y:
		y += signi(to.y - y)
		for w: int in range(-1, 2):
			if _get_tile(data, x + w, y) != Terrain.WALL:
				_set_tile(data, x + w, y, Terrain.PATH)

static func _carve_shrine(data: Dictionary, center: Vector2i) -> void:
	for y: int in range(center.y - 8, center.y + 9):
		for x: int in range(center.x - 9, center.x + 10):
			var d := Vector2(x - center.x, (y - center.y) * 1.3).length()
			if d < 9.0:
				_set_tile(data, x, y, Terrain.ASH)
	var rect := Rect2i(center.x - 5, center.y - 4, 11, 8)
	_fill_rect(data, rect, Terrain.WALL)
	_fill_rect(data, Rect2i(rect.position + Vector2i.ONE, rect.size - Vector2i(2, 2)),
			Terrain.FLOOR)
	var door_x: int = center.x
	_set_tile(data, door_x, rect.end.y - 1, Terrain.FLOOR)
	data["shrine_door"] = Vector2i(door_x, rect.end.y - 1)
	data["shrine_altar"] = Vector2i(center.x, rect.position.y + 2)

## Chests sit on walkable, non-village tiles so exploring pays off.
static func _place_chests(data: Dictionary, rng: RandomNumberGenerator) -> void:
	var spots: Array[Vector2i] = data["chest_spots"]
	var village: Vector2i = data["village"]
	var attempts := 0
	while spots.size() < 6 and attempts < 4000:
		attempts += 1
		var x := rng.randi_range(6, WIDTH - 7)
		var y := rng.randi_range(6, HEIGHT - 7)
		if Vector2(Vector2i(x, y) - village).length() < 16.0:
			continue
		var tile := _get_tile(data, x, y)
		if tile != Terrain.GRASS and tile != Terrain.ASH and tile != Terrain.SAND:
			continue
		var too_close := false
		for other: Vector2i in spots:
			if Vector2(other - Vector2i(x, y)).length() < 12.0:
				too_close = true
				break
		if not too_close:
			spots.append(Vector2i(x, y))
