class_name SuccessionScreen
extends CanvasLayer
## After a death: three real villagers, each with their own bond to the person
## who just fell. Choosing one is a settlement decision, not a stat roll.

signal chosen(villager_id: String)

var _candidates: Array[Dictionary] = []

func _ready() -> void:
	layer = 20
	var backdrop := ColorRect.new()
	backdrop.color = Color(0.03, 0.03, 0.04, 0.94)
	backdrop.anchor_right = 1.0
	backdrop.anchor_bottom = 1.0
	add_child(backdrop)

	var column := VBoxContainer.new()
	column.anchor_left = 0.5
	column.anchor_right = 0.5
	column.anchor_top = 0.0
	column.offset_left = -190
	column.offset_right = 190
	column.offset_top = 14
	column.add_theme_constant_override("separation", 5)
	add_child(column)

	var dead := "Someone"
	if not WorldState.lineage.is_empty():
		dead = String(WorldState.lineage[-1]["name"])
	column.add_child(UiTheme.label("%s is dead." % dead, 13, UiTheme.ACCENT))
	column.add_child(UiTheme.label(
		"The blade goes to whoever will carry it. Grief in the settlement: %d."
			% WorldState.grief, 8, UiTheme.INK_DIM))

	_candidates = WorldState.succession_candidates()
	var first: Button = null
	for person: Dictionary in _candidates:
		var button := _candidate_button(person)
		column.add_child(button)
		if first == null:
			first = button
	column.add_child(UiTheme.label(
		"Taking someone out of the fields costs the settlement their work.",
		7, UiTheme.INK_DIM))
	if first != null:
		first.grab_focus()

func _candidate_button(person: Dictionary) -> Button:
	var bond: Dictionary = Codex.bond(String(person.get("bond_to_dead", "stranger")))
	var trait_names: Array[String] = []
	for trait_id: String in person["traits"]:
		trait_names.append(String(Codex.trait_info(trait_id)["name"]))
	var button := Button.new()
	button.text = "%s, %d - %s   [%s]\n    %s\n    VIG %d  STR %d  DEX %d  RES %d   %s" % [
		String(person["name"]), int(person["age"]), String(person["job"]),
		String(bond["name"]), String(bond["line"]),
		int(person["vigour"]), int(person["strength"]), int(person["dexterity"]),
		int(person["resolve"]), ", ".join(trait_names),
	]
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.add_theme_font_size_override("font_size", 8)
	button.add_theme_stylebox_override("focus", UiTheme.selection_style())
	button.add_theme_stylebox_override("hover", UiTheme.selection_style())
	button.pressed.connect(func() -> void:
		WorldState.choose_successor(String(person["id"]))
		WorldState.conscript_villager(String(person["id"]))
		chosen.emit(String(person["id"])))
	return button
