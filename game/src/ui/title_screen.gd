class_name TitleScreen
extends CanvasLayer
## Title and entry points. Kept deliberately plain: the pitch is one line.

signal new_lineage()
signal continue_lineage()

func _ready() -> void:
	layer = 20
	var backdrop := ColorRect.new()
	backdrop.color = Color(0.04, 0.035, 0.045, 1.0)
	backdrop.anchor_right = 1.0
	backdrop.anchor_bottom = 1.0
	add_child(backdrop)

	var column := VBoxContainer.new()
	column.anchor_left = 0.5
	column.anchor_right = 0.5
	column.anchor_top = 0.5
	column.anchor_bottom = 0.5
	column.offset_left = -150
	column.offset_right = 150
	column.offset_top = -70
	column.offset_bottom = 70
	column.add_theme_constant_override("separation", 6)
	add_child(column)

	column.add_child(UiTheme.label("SOULSTEAD", 26, UiTheme.ACCENT))
	column.add_child(UiTheme.label("You never respawn. You are inherited.", 9))
	column.add_child(UiTheme.label(
		"WASD move    J light    K heavy    L parry    Space dodge    Q flask    E interact",
		7, UiTheme.INK_DIM))

	# Difficulty selector
	var diff_row := HBoxContainer.new()
	diff_row.add_theme_constant_override("separation", 4)
	column.add_child(diff_row)
	diff_row.add_child(UiTheme.label("Difficulty:", 8, UiTheme.INK_DIM))
	for diff_id in ["easy", "normal", "hard"]:
		var btn := _button(diff_id.capitalize(), true, func() -> void:
			WorldState.difficulty = diff_id
		)
		diff_row.add_child(btn)

	var continue_button := _button("Continue the lineage", WorldState.has_save(),
			func() -> void: continue_lineage.emit())
	column.add_child(continue_button)
	var new_button := _button("Break new ground", true, func() -> void: new_lineage.emit())
	column.add_child(new_button)
	column.add_child(_button("Quit", true, func() -> void: get_tree().quit()))

	if WorldState.has_save():
		continue_button.grab_focus()
	else:
		new_button.grab_focus()

func _button(text: String, enabled: bool, on_press: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.disabled = not enabled
	button.add_theme_font_size_override("font_size", 10)
	button.add_theme_stylebox_override("focus", UiTheme.selection_style())
	button.add_theme_stylebox_override("hover", UiTheme.selection_style())
	button.pressed.connect(on_press)
	return button
