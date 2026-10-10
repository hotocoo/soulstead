class_name Terrain
extends RefCounted
## Terrain ids shared by the generator, the mesh builder and the world runtime.
## Heights are in world units; the map is built as a low-relief 3D surface.

enum {
	WATER,
	SAND,
	GRASS,
	TALL_GRASS,
	ASH,
	ROCK,
	TREE,
	PATH,
	FLOOR,
	WALL,
}

## One tile is two metres across. A figure is about 1.3 m tall, so the world
## reads at a believable scale from the third-person camera.
const TILE_SIZE := 2.0

const BLOCKING := [WATER, ROCK, TREE, WALL]

const ENCOUNTER_NAMES := {
	TALL_GRASS: "tall_grass",
	ASH: "ash",
}

const COLORS := {
	WATER: Color("#24384f"),
	SAND: Color("#a89571"),
	GRASS: Color("#4c6247"),
	TALL_GRASS: Color("#3d5239"),
	ASH: Color("#564d51"),
	ROCK: Color("#6a6670"),
	TREE: Color("#33492f"),
	PATH: Color("#7a6a55"),
	FLOOR: Color("#5f4d3c"),
	WALL: Color("#3a3038"),
}

const HEIGHTS := {
	WATER: -0.45,
	SAND: -0.05,
	GRASS: 0.0,
	TALL_GRASS: 0.05,
	ASH: 0.0,
	ROCK: 1.9,
	TREE: 0.0,
	PATH: 0.02,
	FLOOR: 0.06,
	WALL: 2.6,
}

static func is_blocking(tile: int) -> bool:
	return BLOCKING.has(tile)

static func height(tile: int) -> float:
	return float(HEIGHTS.get(tile, 0.0))

static func color(tile: int) -> Color:
	return Color(COLORS.get(tile, Color.MAGENTA))

static func encounter_table(tile: int) -> String:
	return ENCOUNTER_NAMES.get(tile, "")

## Converts a tile coordinate to the centre of that tile in world space.
static func to_world(tile: Vector2i, y: float = 0.0) -> Vector3:
	return Vector3((tile.x + 0.5) * TILE_SIZE, y, (tile.y + 0.5) * TILE_SIZE)

static func to_tile(point: Vector3) -> Vector2i:
	return Vector2i(floori(point.x / TILE_SIZE), floori(point.z / TILE_SIZE))
