class_name SettlementUi
extends CanvasLayer
## Settlement HUD and panels: dialogue, vigils, the ledger board, and the
## online lobby.

var settlement: Settlement

var _prompt: Label
var _status: Label
var _line_panel: PanelContainer
var _resources_label: Label
var _minimap: Control
var _line_label: Label
var _panel: PanelContainer
var _panel_body: VBoxContainer

func _ready() -> void:
	layer = 10
	_build_status()
	_build_resources()
	_build_minimap()
	_build_prompt()
	_build_line_box()
	WorldState.grief_changed.connect(func(_v: int) -> void: _refresh_status())
	WorldState.grief_changed.connect(func(_v: int) -> void: _refresh_resources())
	Chronicle.recorded.connect(func(_e: Dictionary) -> void: _refresh_status())
	if WorldState.story_director != null:
		WorldState.story_director.beat_started.connect(_show_story_beat)
		WorldState.story_director.beat_finished.connect(_hide_story_beat)
		WorldState.story_director.choice_resolved.connect(_on_story_choice_resolved)
		if not WorldState.story_director.active.is_empty():
			_show_story_beat(WorldState.story_director.active)
	_refresh_status()

func _build_status() -> void:
	var holder := UiTheme.make_panel(5)
	holder.position = Vector2(6, 6)
	add_child(holder)
	_status = UiTheme.label("", 7)
	holder.add_child(_status)

func _build_minimap() -> void:
	_minimap = Control.new()
	_minimap.position = Vector2(6, 120)
	_minimap.size = Vector2(120, 90)
	_minimap.draw.connect(_draw_minimap)
	add_child(_minimap)

func _draw_minimap() -> void:
	# Draw minimap background
	_minimap.draw_rect(Rect2(0, 0, 120, 90), Color(0.05, 0.05, 0.08, 0.7))
	_minimap.draw_rect(Rect2(0, 0, 120, 90), Color(0.3, 0.3, 0.3, 0.5), false, 1.0)
	# Draw settlement buildings (simplified)
	_minimap.draw_rect(Rect2(20, 20, 20, 15), Color(0.4, 0.3, 0.2, 0.8))
	_minimap.draw_rect(Rect2(80, 20, 20, 15), Color(0.4, 0.3, 0.2, 0.8))
	_minimap.draw_rect(Rect2(20, 55, 20, 15), Color(0.4, 0.3, 0.2, 0.8))
	_minimap.draw_rect(Rect2(80, 55, 20, 15), Color(0.4, 0.3, 0.2, 0.8))
	# Draw player position (center)
	_minimap.draw_circle(Vector2(60, 45), 3.0, Color(0.3, 0.6, 1.0, 1.0))

func _build_resources() -> void:
	_resources_label = UiTheme.label("", 7, UiTheme.INK_DIM)
	_resources_label.anchor_left = 0.0
	_resources_label.anchor_right = 0.0
	_resources_label.offset_left = 8
	_resources_label.offset_right = 8
	_resources_label.offset_top = 60
	_resources_label.offset_bottom = 80
	add_child(_resources_label)
	_refresh_resources()

func _refresh_resources() -> void:
	_resources_label.text = "Timber: %d  Iron: %d  Relics: %d" % [
		WorldState.materials.get("timber", 0),
		WorldState.materials.get("iron", 0),
		WorldState.materials.get("relic", 0),
	]

func _build_prompt() -> void:
	_prompt = UiTheme.label("", 8, UiTheme.ACCENT)
	_prompt.anchor_left = 0.5
	_prompt.anchor_right = 0.5
	_prompt.anchor_top = 1.0
	_prompt.anchor_bottom = 1.0
	_prompt.offset_left = -80
	_prompt.offset_right = 80
	_prompt.offset_top = -34
	_prompt.offset_bottom = -22
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(_prompt)

func _build_line_box() -> void:
	_line_panel = UiTheme.make_panel(7)
	_line_panel.anchor_left = 0.0
	_line_panel.anchor_right = 1.0
	_line_panel.anchor_top = 1.0
	_line_panel.anchor_bottom = 1.0
	_line_panel.offset_left = 16
	_line_panel.offset_right = -16
	_line_panel.offset_top = -58
	_line_panel.offset_bottom = -12
	_line_panel.visible = false
	add_child(_line_panel)
	_line_label = UiTheme.label("", 8)
	_line_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_line_panel.add_child(_line_label)

func _refresh_status() -> void:
	var ending: Dictionary = Chronicle.projected_ending()
	_status.text = "Day %d   Grief %d   Relics %d   Echoes %d\nDrifting toward: %s" % [
		int(WorldState.world_day), WorldState.grief,
		int(WorldState.materials.get("relic", 0)), WorldState.echoes.size(),
		String(ending["name"]),
	]
	if WorldState.story_director != null and not WorldState.story_director.active.is_empty():
		_status.text += "\nChapter %02d  %s" % [int(WorldState.story_director.active["chapter"]), String(WorldState.story_director.active["title"])]

func _show_story_beat(_beat: Dictionary) -> void:
	if _panel != null:
		_close_panel()
	# Settlement story beats use the same authored presentation as field beats;
	# input remains frozen until the player acknowledges the scene.
	_open_story_panel(_beat)

func _open_story_panel(beat: Dictionary) -> void:
	_close_panel()
	settlement.player.input_enabled = false
	_panel = UiTheme.make_panel(10)
	_panel.anchor_left = 0.5
	_panel.anchor_right = 0.5
	_panel.anchor_top = 0.5
	_panel.anchor_bottom = 0.5
	_panel.offset_left = -245
	_panel.offset_right = 245
	_panel.offset_top = -145
	_panel.offset_bottom = 145
	add_child(_panel)
	_panel_body = VBoxContainer.new()
	_panel_body.add_theme_constant_override("separation", 5)
	_panel.add_child(_panel_body)
	_panel_body.add_child(UiTheme.label("CHAPTER %02d  ·  %s" % [int(beat["chapter"]), String(beat["title"])], 12, UiTheme.ACCENT))
	_panel_body.add_child(UiTheme.label("%s  ·  Day %d" % [String(beat["place"]), int(beat["day"])], 7, UiTheme.INK_DIM))
	var prose := UiTheme.label(String(beat["text"]), 8)
	prose.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_panel_body.add_child(prose)
	var objective := UiTheme.label("OBJECTIVE  %s" % String(beat["objective"]), 8, UiTheme.ACCENT)
	objective.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_panel_body.add_child(objective)
	var choices: Array[Dictionary] = WorldState.story_director.choices
	if choices.is_empty():
		_add_button("Continue  [Enter]", true, func() -> void:
			WorldState.story_director.dismiss_active())
	else:
		_panel_body.add_child(UiTheme.label("CHOOSE WHAT THE HOLD DOES", 8, UiTheme.INK_DIM))
		for i: int in choices.size():
			var choice := choices[i]
			_add_button("%d. %s" % [i + 1, String(choice["label"])], bool(choice.get("available", true)),
				_resolve_story_choice.bind(i))
		_panel_body.add_child(UiTheme.label("Your choice enters the Chronicle. There is no undo.", 7,
				UiTheme.INK_DIM))

func _resolve_story_choice(index: int) -> void:
	if WorldState.story_director == null:
		return
	WorldState.story_director.resolve_choice(index)
	WorldState.save_game()

func _on_story_choice_resolved(choice: Dictionary, _beat: Dictionary) -> void:
	if _panel == null:
		return
	for child: Node in _panel_body.get_children():
		if child is Button:
			(child as Button).disabled = true
	_panel_body.add_child(UiTheme.label("RECORDED  %s" % String(choice["label"]), 8, UiTheme.ACCENT))
	_add_button("Continue  [Enter]", true, func() -> void:
		WorldState.story_director.dismiss_active())

func _hide_story_beat(_beat: Dictionary) -> void:
	_close_panel()

func set_prompt(text: String) -> void:
	_prompt.text = "[E]  %s" % text if text != "" else ""

func is_panel_open() -> bool:
	return _panel != null or _line_panel.visible

func show_line(text: String) -> void:
	_line_label.text = text
	_line_panel.visible = true
	await get_tree().create_timer(3.4).timeout
	_line_panel.visible = false

# --- Panels --------------------------------------------------------------

func _open_panel(title: String) -> VBoxContainer:
	_close_panel()
	settlement.player.input_enabled = false
	_panel = UiTheme.make_panel(8)
	_panel.anchor_left = 0.5
	_panel.anchor_top = 0.5
	_panel.anchor_right = 0.5
	_panel.anchor_bottom = 0.5
	_panel.offset_left = -150
	_panel.offset_right = 150
	_panel.offset_top = -90
	_panel.offset_bottom = 90
	add_child(_panel)
	_panel_body = VBoxContainer.new()
	_panel_body.add_theme_constant_override("separation", 4)
	_panel.add_child(_panel_body)
	_panel_body.add_child(UiTheme.label(title, 10, UiTheme.ACCENT))
	return _panel_body

func _close_panel() -> void:
	if _panel != null:
		_panel.queue_free()
		_panel = null
	if settlement != null and settlement.player != null:
		settlement.player.input_enabled = true

func _unhandled_input(event: InputEvent) -> void:
	if _panel != null and event.is_action_pressed("cancel"):
		_close_panel()
		get_viewport().set_input_as_handled()

func _add_button(text: String, enabled: bool, on_press: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.disabled = not enabled
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.add_theme_font_size_override("font_size", 8)
	button.add_theme_stylebox_override("focus", UiTheme.selection_style())
	button.add_theme_stylebox_override("hover", UiTheme.selection_style())
	button.pressed.connect(on_press)
	_panel_body.add_child(button)
	return button

func open_vigils() -> void:
	var body := _open_panel("Vigils   (grief %d)" % WorldState.grief)
	body.add_child(UiTheme.label(
		"Grief spent here becomes a Legacy every future successor inherits.",
		7, UiTheme.INK_DIM))
	var first: Button = null
	for id: String in Codex.VIGILS:
		var data: Dictionary = Codex.VIGILS[id]
		var affordable := WorldState.can_perform_vigil(id)
		var label := "%s  -%d grief%s\n    %s" % [
			String(data["name"]), int(data["grief"]),
			"  (needs a relic)" if int(data.get("relic", 0)) > 0 else "",
			String(data["desc"]),
		]
		var button := _add_button(label, affordable, _perform_vigil.bind(id))
		if first == null and affordable:
			first = button
	if first != null:
		first.grab_focus()
	body.add_child(UiTheme.label("[Esc] step away", 7, UiTheme.INK_DIM))

func _perform_vigil(id: String) -> void:
	if WorldState.perform_vigil(id):
		WorldState.save_game()
		_close_panel()
		show_line("The settlement holds a %s. The lineage carries it forward."
				% String(Codex.vigil(id)["name"]).to_lower())
	else:
		show_line("Not enough grief has gathered for that yet.")

func open_ledger() -> void:
	var body := _open_panel("The Chronicle")
	for line: String in Chronicle.summary_lines():
		body.add_child(UiTheme.label(line, 8))
	body.add_child(UiTheme.label(String(Chronicle.projected_ending()["text"]), 7,
			UiTheme.INK_DIM))
	var recent := UiTheme.label("", 7)
	recent.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var lines: PackedStringArray = PackedStringArray()
	var entries: Array[Dictionary] = Chronicle.entries
	for entry: Dictionary in entries.slice(maxi(0, entries.size() - 6)):
		lines.append("Day %d  %s" % [int(entry.get("day", 0)), String(entry.get("text", ""))])
	recent.text = "\n".join(lines)
	body.add_child(recent)
	body.add_child(UiTheme.label("[Esc] close", 7, UiTheme.INK_DIM))

func open_departure() -> void:
	var body := _open_panel("Choose the road")
	body.add_child(UiTheme.label(
		"One region at a time. The route determines what kind of ground, dead, and argument you meet.",
		7, UiTheme.INK_DIM))
	for location: String in WorldState.available_locations():
		var decay := WorldState.region_decay(location)
		var label := "%s   %s   [decay %d]" % [WorldState.location_name(location), WorldState.decay_name(decay), decay]
		_add_button(label, true, func() -> void:
			_close_panel()
			settlement.depart_to(location))
	body.add_child(UiTheme.label("[Esc] stay at the Hold", 7, UiTheme.INK_DIM))

func open_lobby() -> void:
	var body := _open_panel("Call another settlement")
	if NetSession.is_networked():
		body.add_child(UiTheme.label("Lobby code: %s" % NetSession.lobby_code, 10,
				UiTheme.ACCENT))
		for peer_id: int in NetSession.members:
			body.add_child(UiTheme.label("- %s" % String(NetSession.members[peer_id]), 8))
		body.add_child(UiTheme.label(
			"Their choices move your ending. Yours move theirs.", 7, UiTheme.INK_DIM))
		_add_button("Leave the lobby", true, func() -> void:
			NetSession.leave()
			_close_panel())
		return
	body.add_child(UiTheme.label(
		"Friends anywhere can join with a code. No shared network needed.",
		7, UiTheme.INK_DIM))
	_add_button("Open a lobby (get a code)", true, func() -> void:
		NetSession.create_lobby(_settlement_name()))
	var code_field := LineEdit.new()
	code_field.placeholder_text = "lobby code"
	code_field.max_length = 8
	code_field.add_theme_font_size_override("font_size", 9)
	body.add_child(code_field)
	_add_button("Answer that code", true, func() -> void:
		NetSession.join_lobby(code_field.text, _settlement_name()))
	_add_button("Listen for open settlements", true, func() -> void:
		NetSession.browse_lobbies(_settlement_name()))
	if not NetSession.lobbies_listed.is_connected(_on_lobbies_listed):
		NetSession.lobbies_listed.connect(_on_lobbies_listed)
	var status := UiTheme.label("Relay: %s" % NetSession.relay_url, 7, UiTheme.INK_DIM)
	status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_child(status)
	if not NetSession.lobby_joined.is_connected(_on_lobby_joined):
		NetSession.lobby_joined.connect(_on_lobby_joined)
		NetSession.lobby_failed.connect(_on_lobby_failed)

func open_facility(id: String, title: String, detail: String) -> void:
	var level := int(WorldState.buildings.get(id, 1))
	var body := _open_panel("%s  ·  level %d" % [title, level])
	var description := UiTheme.label(detail, 7, UiTheme.INK_DIM)
	description.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_child(description)
	if id == "smithy":
		var weapon_id := String(WorldState.wielder().get("weapon", "ashblade"))
		var bonus := float(WorldState.weapon_upgrades.get(weapon_id, 0.0)) * 100.0
		body.add_child(UiTheme.label("Current blade: %s  ·  +%.0f%% smith's binding" % [String(Codex.weapon(weapon_id)["name"]), bonus], 8))
	var cost := WorldState.facility_upgrade_cost(id)
	if cost.is_empty():
		body.add_child(UiTheme.label("This building has reached its working limit.", 8, UiTheme.INK_DIM))
	else:
		var cost_parts := PackedStringArray()
		for resource: String in cost:
			cost_parts.append("%s %d" % [resource.capitalize(), int(cost[resource])])
		var cost_text := "  ".join(cost_parts)
		var affordable := WorldState.can_upgrade_facility(id)
		_add_button("Raise to level %d  ·  %s" % [level + 1, cost_text], affordable, func() -> void:
			if WorldState.upgrade_facility(id):
				WorldState.save_game()
				_close_panel()
				show_line("The %s rises. The Hold will work differently tomorrow." % title.to_lower())
		)
	body.add_child(UiTheme.label("Timber %d   Iron %d   Relics %d" % [
		int(WorldState.materials.get("timber", 0)), int(WorldState.materials.get("iron", 0)), int(WorldState.materials.get("relic", 0))], 7, UiTheme.INK_DIM))
	body.add_child(UiTheme.label("[Esc] step away", 7, UiTheme.INK_DIM))

func _settlement_name() -> String:
	if WorldState.lineage.is_empty():
		return "Soulstead"
	return "%s Hold" % String(WorldState.lineage[0]["name"]).split(" ")[-1]

func _on_lobby_joined(code: String, _members: Array) -> void:
	if _panel != null:
		open_lobby()
	show_line("Lobby open. Share the code: %s" % code)

func _on_lobby_failed(reason: String) -> void:
	show_line(reason)

## Discovery for players with no code to type: every open lobby on the relay,
## from any network.
func _on_lobbies_listed(open_lobbies: Array) -> void:
	if _panel == null:
		return
	if open_lobbies.is_empty():
		_panel_body.add_child(UiTheme.label("No settlements are calling right now.", 7,
				UiTheme.INK_DIM))
		return
	_panel_body.add_child(UiTheme.label("Open settlements:", 8, UiTheme.ACCENT))
	for entry: Dictionary in open_lobbies:
		var label := "%s  [%s]  %d/%d" % [String(entry.get("host", "?")),
				String(entry.get("code", "?")), int(entry.get("players", 1)),
				int(entry.get("capacity", 4))]
		_add_button(label, true, func() -> void:
			NetSession.join_lobby(String(entry.get("code", "")), _settlement_name()))
