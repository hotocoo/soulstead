class_name Settlement
extends Node3D
## The hub. Time does not pass here; consequence still does.
##
## Owns the social layer: villagers you may later have to send out, the
## memorial where grief becomes legacy, the ledger board showing which ending
## the Chronicle points at, and the stone that calls other settlements.

signal depart_requested()
signal panel_opened(panel: String)

const WIDTH := 34
const HEIGHT := 24

var player: PlayerActor
var ui: SettlementUi

var _map: Dictionary = {}

func _process(delta: float) -> void:
	# Update sky based on world time
	var hour := fmod(WorldState.world_day, 1.0) * 24.0
	Look.update_sky(hour)

func _ready() -> void:
	add_child(Look.environment(WorldState.region_decay("wrenfield")))
	add_child(Look.sun())
	_map = _build_map()
	TerrainBuilder.build(_map, self)
	_spawn_props()
	_spawn_villagers()
	_spawn_player()
	_spawn_pending_raid()
	ui = SettlementUi.new()
	ui.settlement = self
	add_child(ui)
	WorldState.save_game()
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("settlement_entered")

# --- Map -----------------------------------------------------------------

func _build_map() -> Dictionary:
	var tiles := PackedByteArray()
	tiles.resize(WIDTH * HEIGHT)
	for i: int in WIDTH * HEIGHT:
		tiles[i] = Terrain.GRASS
	var data := {"width": WIDTH, "height": HEIGHT, "tiles": tiles}
	_ring(data)
	_plaza(data)
	_hut(data, Rect2i(5, 4, 6, 4))
	_hut(data, Rect2i(23, 4, 6, 4))
	_hut(data, Rect2i(4, 16, 6, 4))
	_hut(data, Rect2i(24, 16, 6, 4))
	return data

func _set_tile(data: Dictionary, x: int, y: int, tile: int) -> void:
	if x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT:
		return
	var tiles: PackedByteArray = data["tiles"]
	tiles[y * WIDTH + x] = tile

## A wall of trees frames the settlement and keeps the player inside it.
func _ring(data: Dictionary) -> void:
	for x: int in WIDTH:
		for depth: int in 2:
			_set_tile(data, x, depth, Terrain.TREE)
			_set_tile(data, x, HEIGHT - 1 - depth, Terrain.TREE)
	for y: int in HEIGHT:
		for depth: int in 2:
			_set_tile(data, depth, y, Terrain.TREE)
			_set_tile(data, WIDTH - 1 - depth, y, Terrain.TREE)

func _plaza(data: Dictionary) -> void:
	var cx := WIDTH / 2
	var cy := HEIGHT / 2
	for y: int in range(cy - 6, cy + 7):
		for x: int in range(cx - 8, cx + 9):
			var d := Vector2(x - cx, (y - cy) * 1.3).length()
			if d < 8.0:
				_set_tile(data, x, y, Terrain.PATH)
			if d < 2.6:
				_set_tile(data, x, y, Terrain.FLOOR)

func _hut(data: Dictionary, rect: Rect2i) -> void:
	for y: int in range(rect.position.y, rect.end.y):
		for x: int in range(rect.position.x, rect.end.x):
			_set_tile(data, x, y, Terrain.WALL)
	for y: int in range(rect.position.y + 1, rect.end.y - 1):
		for x: int in range(rect.position.x + 1, rect.end.x - 1):
			_set_tile(data, x, y, Terrain.FLOOR)
	_set_tile(data, rect.position.x + rect.size.x / 2, rect.end.y - 1, Terrain.FLOOR)

# --- Contents ------------------------------------------------------------

func _spawn_props() -> void:
	var cx := WIDTH / 2
	var cy := HEIGHT / 2
	_spawn_house(Vector3(7.0, 0.0, 6.0), Color("#9a6a4a"), Color("#4a3f43"), "Oda's House")
	_spawn_house(Vector3(7.0, 0.0, 20.0), Color("#876b58"), Color("#51494c"), "Carver's House")
	_spawn_house(Vector3(47.0, 0.0, 6.0), Color("#a36b48"), Color("#463c42"), "Smith's House")
	_spawn_house(Vector3(47.0, 0.0, 20.0), Color("#786e5e"), Color("#48484a"), "Warden's House")
	var hearth := Hearth.new()
	hearth.position = Terrain.to_world(Vector2i(cx, cy))
	add_child(hearth)
	var memorial := Memorial.new()
	memorial.position = Terrain.to_world(Vector2i(cx - 6, cy - 3))
	add_child(memorial)
	var board := LedgerBoard.new()
	board.position = Terrain.to_world(Vector2i(cx + 6, cy - 3))
	add_child(board)
	var stone := LobbyStone.new()
	stone.position = Terrain.to_world(Vector2i(cx + 6, cy + 4))
	add_child(stone)
	_spawn_facility("smithy", "Smithy", "Relics bind remembered motion into steel. Timber and iron raise the forge.", Vector2i(cx - 9, cy + 5))
	_spawn_facility("fields", "Fields", "The living work the ground. Grief lowers what the Hold can bring home.", Vector2i(cx - 10, cy - 6))
	_spawn_facility("palisade", "Palisade", "A stronger wall buys time when an Echo comes home armed.", Vector2i(cx + 10, cy + 5))
	_spawn_facility("tavern", "Tavern", "The settlement drinks and remembers. Grief is lighter here.", Vector2i(cx - 5, cy + 8))
	_spawn_facility("library", "Library", "Chronicles of the dead are kept here. Knowledge is power.", Vector2i(cx + 5, cy - 8))

func _spawn_house(at: Vector3, wall_color: Color, roof_color: Color, label: String) -> void:
	var house := Node3D.new()
	house.name = label
	house.position = at
	add_child(house)
	var wall := Look.standard(wall_color, 0.82)
	var timber := Look.standard(Color("#30231d"), 0.88)
	var roof := Look.standard(roof_color, 0.92)
	var glass := Look.standard(Color("#9eb7ba"), 0.16)
	glass.metallic = 0.18
	glass.emission_enabled = true
	glass.emission = Color("#b8d0c8")
	glass.emission_energy_multiplier = 0.35
	var part := func(size: Vector3, pos: Vector3, mat: StandardMaterial3D, rot: Vector3 = Vector3.ZERO) -> void:
		var node := MeshInstance3D.new()
		node.mesh = Look._rounded_block_mesh(size, minf(size.x, size.z) * 0.12, 28)
		node.material_override = mat
		node.position = pos
		node.rotation = rot
		house.add_child(node)
	part.call(Vector3(5.0, 0.34, 3.8), Vector3(0, 0.17, 0), timber)
	part.call(Vector3(4.42, 2.72, 3.18), Vector3(0, 1.52, 0), wall)
	# Deep eaves and a pitched roof with a proper ridge make the silhouette read
	# as a constructed building rather than four boxes placed together.
	part.call(Vector3(2.48, 0.24, 3.82), Vector3(-1.02, 3.03, 0), roof, Vector3(0, 0, deg_to_rad(-31.0)))
	part.call(Vector3(2.48, 0.24, 3.82), Vector3(1.02, 3.03, 0), roof, Vector3(0, 0, deg_to_rad(31.0)))
	part.call(Vector3(0.22, 0.22, 3.95), Vector3(0, 3.72, 0), timber)
	# Structural timber framing on the facade.
	for x: float in [-2.05, 2.05]:
		part.call(Vector3(0.16, 2.62, 0.16), Vector3(x, 1.48, -1.61), timber)
	for y: float in [0.62, 2.38]:
		part.call(Vector3(4.30, 0.13, 0.13), Vector3(0, y, -1.62), timber)
	part.call(Vector3(0.72, 1.45, 0.10), Vector3(0, 0.78, -1.61), timber)
	part.call(Vector3(0.72, 0.68, 0.06), Vector3(-1.30, 1.52, -1.63), glass)
	part.call(Vector3(0.72, 0.68, 0.06), Vector3(1.30, 1.52, -1.63), glass)
	for side: int in [-1, 1]:
		part.call(Vector3(0.08, 0.76, 0.08), Vector3(float(side) * 1.30, 1.52, -1.68), timber)
		part.call(Vector3(0.08, 0.76, 0.08), Vector3(float(side) * 1.30, 1.52, -1.58), timber)
	# Chimney and cap; the forge/house smoke stack is deliberately offset from
	# the roof ridge so every dwelling has a believable vertical landmark.
	part.call(Vector3(0.52, 1.18, 0.52), Vector3(1.35, 3.22, 0.55), timber)
	part.call(Vector3(0.68, 0.12, 0.68), Vector3(1.35, 3.82, 0.55), timber)
	# Small porch step and lintel give the entrance a readable scale reference.
	part.call(Vector3(1.25, 0.16, 0.55), Vector3(0, 0.08, -1.91), timber)
	part.call(Vector3(1.05, 0.12, 0.18), Vector3(0, 1.52, -1.78), timber)

func _spawn_facility(id: String, title: String, detail: String, tile: Vector2i) -> void:
	var facility := SettlementFacility.new()
	facility.position = Terrain.to_world(tile, 0.1)
	add_child(facility)
	facility.configure(id, title, detail)

func _spawn_villagers() -> void:
	var slots := [Vector2i(11, 9), Vector2i(23, 9), Vector2i(10, 15), Vector2i(24, 15),
		Vector2i(15, 18), Vector2i(20, 6), Vector2i(17, 17)]
	var index := 0
	for person: Dictionary in WorldState.living_villagers():
		if index >= slots.size():
			break
		if bool(person.get("is_wielder", false)):
			continue
		var villager := Villager.new()
		villager.data = person
		villager.position = Terrain.to_world(slots[index])
		add_child(villager)
		index += 1

func _spawn_player() -> void:
	player = PlayerActor.new()
	player.position = Terrain.to_world(Vector2i(WIDTH / 2, HEIGHT / 2 + 4), 0.4)
	add_child(player)

func _spawn_pending_raid() -> void:
	var data := WorldState.pending_raid()
	if data.is_empty():
		return
	var echo := EchoActor.new()
	echo.position = Terrain.to_world(Vector2i(WIDTH - 6, HEIGHT / 2), 0.4)
	add_child(echo)
	echo.from_echo(data, WorldState.region_decay(String(data.get("region", "wrenfield"))))
	echo.reclaimed.connect(_on_raid_reclaimed)
	WorldState.log_entry.emit("The Echo of %s has reached the Hold. The gates stay shut." % String(data["owner"]))

func _on_raid_reclaimed(data: Dictionary) -> void:
	WorldState.reclaim_echo(String(data.get("id", "")))
	if ui != null:
		ui.show_line("The Echo is down. The Hold opens its gates again.")

# --- Interaction ---------------------------------------------------------

func _process(_delta: float) -> void:
	if ui == null or player == null:
		return
	var target := nearest_interactable()
	ui.set_prompt(target.prompt if target != null else "")
	if Input.is_action_just_pressed("interact") and target != null and not ui.is_panel_open():
		target.interact(self)

func nearest_interactable() -> Interactable:
	var reach_point: Vector3 = player.global_position + player.facing * 1.2
	var best: Interactable = null
	var best_distance := Interactable.REACH
	for node: Node in get_tree().get_nodes_in_group("interactables"):
		var candidate := node as Interactable
		if candidate == null or not candidate.can_interact():
			continue
		var distance: float = candidate.global_position.distance_to(reach_point)
		if distance < best_distance:
			best_distance = distance
			best = candidate
	return best

# --- Called by props -----------------------------------------------------

func say(text: String) -> void:
	ui.show_line(text)

func open_vigils() -> void:
	ui.open_vigils()
	panel_opened.emit("vigils")

func open_ledger() -> void:
	ui.open_ledger()
	panel_opened.emit("ledger")

func open_lobby() -> void:
	ui.open_lobby()
	panel_opened.emit("lobby")

func open_facility(id: String, title: String, detail: String) -> void:
	ui.open_facility(id, title, detail)
	panel_opened.emit("facility:%s" % id)

func open_departure() -> void:
	if not WorldState.pending_raid().is_empty():
		say("The palisade is under attack. The Echo must be reclaimed before anyone leaves.")
		return
	ui.open_departure()

func depart_to(location: String) -> void:
	if not WorldState.set_expedition_location(location):
		say("That road is closed by the Grey. Another route must be taken.")
		return
	WorldState.save_game()
	depart_requested.emit()
