class_name FieldHud
extends CanvasLayer
## Expedition HUD: health, Composure, flasks, the world clock, and a running
## feed of what the Chronicle just recorded.

var player: PlayerActor

var _health_bar: ProgressBar
var _composure_bar: ProgressBar
var _flask_label: Label
var _clock_label: Label
var _feed: Label
var _feed_lines: PackedStringArray = PackedStringArray()
var _story_panel: PanelContainer
var _story_title: Label
var _story_body: Label
var _story_objective: Label
var _exit_arrow: Label
var _vignette: ColorRect
var _tutorial_label: Label
var _kill_label: Label
var _radar: Control


func _ready() -> void:
	layer = 10
	# Tutorial label
	_tutorial_label = UiTheme.label("", 9, Color(1.0, 0.8, 0.4, 0.8))
	_tutorial_label.position = Vector2(10, 50)
	_tutorial_label.visible = false
	add_child(_tutorial_label)
	# Low health vignette
	_vignette = ColorRect.new()
	_vignette.color = Color(0.8, 0.1, 0.1, 0.0)
	_vignette.anchor_right = 1.0
	_vignette.anchor_bottom = 1.0
	add_child(_vignette)
	var frame := VBoxContainer.new()
	frame.position = Vector2(8, 8)
	frame.add_theme_constant_override("separation", 2)
	add_child(frame)
	# Exit compass: shows direction to the settlement exit
	_exit_arrow = UiTheme.label("▼ Home", 9, UiTheme.ACCENT)
	_exit_arrow.anchor_left = 0.5
	_exit_arrow.anchor_right = 0.5
	_exit_arrow.offset_left = -40
	_exit_arrow.offset_right = 40
	_exit_arrow.offset_top = 8
	_exit_arrow.offset_bottom = 24
	_exit_arrow.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(_exit_arrow)
	# Kill counter
	_kill_label = UiTheme.label("Slain: 0", 8, UiTheme.INK_DIM)
	_kill_label.anchor_left = 1.0
	_kill_label.anchor_right = 1.0
	_kill_label.offset_left = -80
	_kill_label.offset_right = -8
	_kill_label.offset_top = 30
	_kill_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(_kill_label)
	# Radar
	_radar = Control.new()
	_radar.anchor_left = 1.0
	_radar.anchor_top = 1.0
	_radar.offset_left = -120
	_radar.offset_top = -120
	_radar.offset_right = -8
	_radar.offset_bottom = -8
	_radar.draw.connect(_draw_radar)
	add_child(_radar)

	_health_bar = UiTheme.bar(UiTheme.HP_COLOR, 92)
	frame.add_child(_health_bar)
	_composure_bar = UiTheme.bar(Color("#d9c27a"), 92)
	frame.add_child(_composure_bar)
	_flask_label = UiTheme.label("", 7)
	frame.add_child(_flask_label)

	_clock_label = UiTheme.label("", 7, UiTheme.INK_DIM)
	_clock_label.anchor_left = 1.0
	_clock_label.anchor_right = 1.0
	_clock_label.offset_left = -110
	_clock_label.offset_right = -8
	_clock_label.offset_top = 8
	_clock_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(_clock_label)

	_feed = UiTheme.label("", 7, UiTheme.INK_DIM)
	_feed.anchor_top = 1.0
	_feed.anchor_bottom = 1.0
	_feed.offset_left = 8
	_feed.offset_top = -56
	_feed.offset_bottom = -8
	add_child(_feed)

	Chronicle.recorded.connect(_on_recorded)
	WorldState.log_entry.connect(_push_line)
	if WorldState.story_director != null:
		WorldState.story_director.beat_started.connect(_show_story_beat)
		WorldState.story_director.beat_finished.connect(_hide_story_beat)
		WorldState.story_director.choice_resolved.connect(_on_story_choice_resolved)
		if not WorldState.story_director.active.is_empty():
			_show_story_beat(WorldState.story_director.active)

func bind(actor: PlayerActor) -> void:
	player = actor
	player.health_changed.connect(_on_health)
	player.composure_changed.connect(_on_composure)
	player.flask_used.connect(func(_left: int) -> void: _refresh_flasks())
	_on_health(player.health, player.max_health)
	_on_composure(player.composure, player.max_composure)
	_refresh_flasks()

func _process(delta: float) -> void:
	# Update radar
	_process_radar(delta)
	# Update kill counter and low health vignette
	var expedition = get_tree().get_first_node_in_group("expedition")
	if expedition != null:
		if expedition.has("kills"):
			_kill_label.text = "Slain: %d" % int(expedition.kills)
	# Low health vignette
	if player != null and player.health > 0.0:
		var health_pct = player.health / player.max_health
		if health_pct < 0.25:
			var pulse = 0.3 + 0.2 * sin(Time.get_ticks_msec() * 0.005)
			_vignette.color = Color(0.8, 0.1, 0.1, pulse)
		else:
			_vignette.color = Color(0.8, 0.1, 0.1, 0.0)
	var hour := int(fmod(WorldState.world_day, 1.0) * 24.0)
	_clock_label.text = "Day %d  %02d:00\n%s" % [
			int(WorldState.world_day), hour,
			"lobby %s" % NetSession.lobby_code if NetSession.is_networked() else "solo",
		]
	_clock_label.text += "\n%s · %s" % [WorldState.location_name(WorldState.current_location),
			WorldState.decay_name(WorldState.region_decay(WorldState.current_location))]
	# Update exit compass
	if player != null and player.camera != null:
		var expedition = get_tree().get_first_node_in_group("expedition")
		if expedition != null and expedition.has("exit_position"):
			var to_exit = expedition.exit_position - player.global_position
			to_exit.y = 0.0
			var cam_forward = -player.camera.global_basis.z
			cam_forward.y = 0.0
			cam_forward = cam_forward.normalized()
			var angle = to_exit.normalized().signed_angle_to(cam_forward, Vector3.UP)
			var dist = to_exit.length()
			var arrow_text = ""
			if absf(angle) < deg_to_rad(30.0):
				arrow_text = "▼ Home %dm" % int(dist)
			elif angle > 0:
				arrow_text = "◀ Home %dm" % int(dist)
			else:
				arrow_text = "Home %dm ▶" % int(dist)
			_exit_arrow.text = arrow_text

func _draw_radar() -> void:
	if player == null:
		return
	var size := _radar.size
	var center := size * 0.5
	var radius := size.x * 0.45
	# Draw radar background
	_radar.draw_circle(center, radius, Color(0.05, 0.05, 0.08, 0.7))
	_radar.draw_arc(center, radius, 0, TAU, 64, Color(0.3, 0.3, 0.3, 0.5), 1.0)
	# Draw crosshairs
	_radar.draw_line(center + Vector2(-radius, 0), center + Vector2(radius, 0), Color(0.2, 0.2, 0.2, 0.5), 0.5)
	_radar.draw_line(center + Vector2(0, -radius), center + Vector2(0, radius), Color(0.2, 0.2, 0.2, 0.5), 0.5)
	# Find expedition for exit position
	var expedition = get_tree().get_first_node_in_group("expedition")
	if expedition == null:
		return
	var radar_range := 30.0
	# Draw exit
	if expedition.has("exit_position"):
		var to_exit = expedition.exit_position - player.global_position
		to_exit.y = 0.0
		if to_exit.length() < radar_range:
			var exit_pos = center + to_exit.normalized() * (to_exit.length() / radar_range) * radius
			_radar.draw_circle(exit_pos, 4.0, Color(0.2, 0.8, 0.3, 0.9))
	# Draw enemies
	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		var to_enemy = enemy.global_position - player.global_position
		to_enemy.y = 0.0
		if to_enemy.length() < radar_range:
			var enemy_pos = center + to_enemy.normalized() * (to_enemy.length() / radar_range) * radius
			_radar.draw_circle(enemy_pos, 3.0, Color(0.8, 0.2, 0.2, 0.9))
	# Draw player (center dot)
	_radar.draw_circle(center, 3.0, Color(0.3, 0.6, 1.0, 1.0))

func _process_radar(delta: float) -> void:
	_radar.queue_redraw()

func _on_health(current: float, maximum: float) -> void:
	_health_bar.max_value = maximum
	_health_bar.value = current

func _on_composure(current: float, maximum: float) -> void:
	_composure_bar.max_value = maximum
	_composure_bar.value = current

func _refresh_flasks() -> void:
	_flask_label.text = "Ash Flask  %d/%d    [Q]" % [WorldState.flasks_left,
			WorldState.max_flasks()]

func _on_recorded(entry: Dictionary) -> void:
	_push_line(String(entry.get("text", "")))

func _push_line(text: String) -> void:
	if text == "":
		return
	_feed_lines.append(text)
	while _feed_lines.size() > 4:
		_feed_lines.remove_at(0)
	_feed.text = "\n".join(_feed_lines)

func _show_story_beat(beat: Dictionary) -> void:
	if _story_panel != null:
		_story_panel.queue_free()
	_story_panel = UiTheme.make_panel(10)
	_story_panel.anchor_left = 0.5
	_story_panel.anchor_right = 0.5
	_story_panel.anchor_top = 0.5
	_story_panel.anchor_bottom = 0.5
	_story_panel.offset_left = -245
	_story_panel.offset_right = 245
	_story_panel.offset_top = -145
	_story_panel.offset_bottom = 145
	add_child(_story_panel)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 5)
	_story_panel.add_child(column)
	_story_title = UiTheme.label("CHAPTER %02d  ·  %s" % [int(beat["chapter"]), String(beat["title"])], 12, UiTheme.ACCENT)
	column.add_child(_story_title)
	column.add_child(UiTheme.label("%s  ·  Day %d" % [String(beat["place"]), int(beat["day"])], 7, UiTheme.INK_DIM))
	_story_body = UiTheme.label(String(beat["text"]), 8)
	_story_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(_story_body)
	_story_objective = UiTheme.label("OBJECTIVE  %s" % String(beat["objective"]), 8, UiTheme.ACCENT)
	_story_objective.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(_story_objective)
	var choices: Array[Dictionary] = WorldState.story_director.choices
	if choices.is_empty():
		var close := Button.new()
		close.text = "Continue  [Enter]"
		close.add_theme_font_size_override("font_size", 9)
		close.pressed.connect(_dismiss_story)
		column.add_child(close)
		close.grab_focus()
	else:
		column.add_child(UiTheme.label("CHOOSE WHAT THE HOLD DOES", 8, UiTheme.INK_DIM))
		for i: int in choices.size():
			var choice := choices[i]
			var button := Button.new()
			button.text = "%d. %s" % [i + 1, String(choice["label"])]
			button.disabled = not bool(choice.get("available", true))
			button.alignment = HORIZONTAL_ALIGNMENT_LEFT
			button.add_theme_font_size_override("font_size", 8)
			button.pressed.connect(_resolve_story_choice.bind(i))
			column.add_child(button)
		column.add_child(UiTheme.label("Your choice enters the Chronicle. There is no undo.", 7, UiTheme.INK_DIM))

func _resolve_story_choice(index: int) -> void:
	if WorldState.story_director != null and WorldState.story_director.resolve_choice(index):
		WorldState.save_game()

func _on_story_choice_resolved(choice: Dictionary, _beat: Dictionary) -> void:
	if _story_panel == null:
		return
	var column := _story_panel.get_child(0) as VBoxContainer
	if column == null:
		return
	for child: Node in column.get_children():
		if child is Button:
			(child as Button).disabled = true
	column.add_child(UiTheme.label("RECORDED  %s" % String(choice["label"]), 8, UiTheme.ACCENT))
	var close := Button.new()
	close.text = "Continue  [Enter]"
	close.add_theme_font_size_override("font_size", 9)
	close.pressed.connect(_dismiss_story)
	column.add_child(close)
	close.grab_focus()
	if player != null:
		player.input_enabled = false

func _dismiss_story() -> void:
	if WorldState.story_director != null:
		WorldState.story_director.dismiss_active()

func _hide_story_beat(_beat: Dictionary) -> void:
	if _story_panel != null:
		_story_panel.queue_free()
		_story_panel = null
	if player != null:
		player.input_enabled = true

func _unhandled_input(event: InputEvent) -> void:
	if _story_panel != null and (event.is_action_pressed("confirm") or event.is_action_pressed("interact")):
		_dismiss_story()
		get_viewport().set_input_as_handled()
