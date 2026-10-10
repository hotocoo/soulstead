extends Node
## Scene flow: title, settlement, expedition, succession, ending.
## Keeps one live scene in a container node owned by Main, with a short fade
## between them so transitions read as deliberate.

signal scene_changed(name: String)

const FADE_TIME := 0.28
const ENDING_DAY := 210.0

var container: Node
var current: Node
var current_name: String = ""

var _fade: ColorRect

func bind(host: Node) -> void:
	container = host
	var layer := CanvasLayer.new()
	layer.layer = 50
	add_child(layer)
	_fade = ColorRect.new()
	_fade.color = Color(0, 0, 0, 1)
	_fade.anchor_right = 1.0
	_fade.anchor_bottom = 1.0
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(_fade)

func _swap(node: Node, label: String) -> void:
	await _fade_to(1.0)
	if current != null:
		current.queue_free()
		current = null
	current = node
	current_name = label
	container.add_child(node)
	scene_changed.emit(label)
	await _fade_to(0.0)

func _fade_to(alpha: float) -> void:
	if _fade == null:
		return
	var tween := create_tween()
	tween.tween_property(_fade, "color:a", alpha, FADE_TIME)
	await tween.finished

# --- Destinations --------------------------------------------------------

func to_title() -> void:
	var screen := TitleScreen.new()
	screen.new_lineage.connect(func() -> void:
		WorldState.new_game()
		WorldState.save_game()
		to_settlement())
	screen.continue_lineage.connect(func() -> void:
		WorldState.load_game()
		if WorldState.wielder_id == "":
			to_succession()
		else:
			to_settlement())
	_swap(screen, "title")

func to_settlement() -> void:
	# Day 210 is the authored boundary, not a soft recommendation. Once the
	# final story handoff is complete, closing the ending must not reopen a
	# playable post-canon sandbox and accidentally invent Chapter 44+ history.
	if WorldState.world_day >= ENDING_DAY \
			and WorldState.story_director != null \
			and WorldState.story_director.is_story_complete():
		to_ending()
		return
	if WorldState.wielder_id == "":
		to_succession()
		return
	var settlement := Settlement.new()
	settlement.depart_requested.connect(to_expedition)
	_swap(settlement, "settlement")

func to_expedition() -> void:
	var expedition := Expedition.new()
	var hud := FieldHud.new()
	expedition.add_child(hud)
	expedition.ready.connect(func() -> void: hud.bind(expedition.player), CONNECT_ONE_SHOT)
	expedition.wielder_fell.connect(_on_wielder_fell)
	expedition.returned_home.connect(_on_returned_home)
	WorldState.run_active = true
	_swap(expedition, "expedition")

func to_succession() -> void:
	var screen := SuccessionScreen.new()
	screen.chosen.connect(func(_id: String) -> void:
		WorldState.save_game()
		to_settlement())
	_swap(screen, "succession")

func to_ending() -> void:
	var screen := EndingScreen.new()
	screen.dismissed.connect(func() -> void:
		WorldState.save_game()
		to_settlement())
	_swap(screen, "ending")

# --- Transitions driven by play -----------------------------------------

func _on_wielder_fell(position: Vector3, killed_by: String) -> void:
	WorldState.register_death(position, WorldState.current_location, killed_by)
	WorldState.save_game()
	await get_tree().create_timer(1.1).timeout
	to_succession()

func _on_returned_home() -> void:
	WorldState.run_active = false
	WorldState.save_game()
	if _ending_ready():
		to_ending()
	else:
		to_settlement()

## The lineage reaches its reckoning on the world clock, not on a boss kill, so
## the ending is always the sum of what the Chronicle recorded.
func _ending_ready() -> bool:
	return Chronicle.locked_ending == "" \
			and WorldState.world_day >= ENDING_DAY \
			and not WorldState.lineage.is_empty() \
			and (WorldState.story_director == null or WorldState.story_director.is_story_complete())
