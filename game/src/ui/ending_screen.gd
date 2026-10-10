class_name EndingScreen
extends CanvasLayer
## Endings resolve from the Chronicle, so this screen reads back the player's
## own ledger rather than announcing a winner.

signal dismissed()

var ending: Dictionary = {}

func _ready() -> void:
	layer = 25
	var backdrop := ColorRect.new()
	backdrop.color = Color(0.03, 0.03, 0.035, 0.97)
	backdrop.anchor_right = 1.0
	backdrop.anchor_bottom = 1.0
	add_child(backdrop)

	var column := VBoxContainer.new()
	column.anchor_left = 0.5
	column.anchor_right = 0.5
	column.offset_left = -180
	column.offset_right = 180
	column.offset_top = 22
	column.add_theme_constant_override("separation", 6)
	add_child(column)

	if ending.is_empty():
		ending = Chronicle.lock_ending()
	column.add_child(UiTheme.label(String(ending["name"]), 20, UiTheme.ACCENT))
	var body := UiTheme.label(String(ending["text"]), 9)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(body)

	column.add_child(UiTheme.label("The ledger that got you here:", 8, UiTheme.INK_DIM))
	for line: String in Chronicle.summary_lines():
		column.add_child(UiTheme.label(line, 8))

	column.add_child(UiTheme.label("Lineage:", 8, UiTheme.INK_DIM))
	for record: Dictionary in WorldState.lineage:
		column.add_child(UiTheme.label("  %s, day %d, killed by %s" % [
			String(record["name"]), int(record["died_day"]), String(record["killed_by"]),
		], 7))

	var button := Button.new()
	button.text = "Close the Chronicle"
	button.add_theme_font_size_override("font_size", 10)
	button.add_theme_stylebox_override("focus", UiTheme.selection_style())
	button.pressed.connect(func() -> void: dismissed.emit())
	column.add_child(button)
	button.grab_focus()
