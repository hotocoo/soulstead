extends Node
## Renders the settlement and the field to PNGs so the 3D look can be checked
## without playing. Run windowed (needs a real renderer):
##   godot --path game res://tests/screenshot.tscn
## Output: user://shots/*.png, path printed on exit.

const SHOT_DIR := "user://shots"

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(SHOT_DIR)
	var container := Node.new()
	add_child(container)
	Flow.bind(container)
	WorldState.new_game(24680)

	Flow.to_settlement()
	await _wait_for("settlement")
	await _frames(30)
	_capture("settlement")

	Flow.to_expedition()
	await _wait_for("expedition")
	await _frames(30)
	_capture("field")

	print("shots written to %s" % ProjectSettings.globalize_path(SHOT_DIR))
	get_tree().quit()

func _capture(label: String) -> void:
	if DisplayServer.get_name().to_lower() == "headless":
		print("  %s -> skipped (headless renderer has no viewport texture)" % label)
		return
	var texture := get_viewport().get_texture()
	if texture == null:
		# Godot's true headless renderer has no viewport texture. Keep this test
		# usable in CI/headless verification; real PNG capture still happens when
		# launched with a windowed renderer as documented above.
		print("  %s -> skipped (headless renderer has no viewport texture)" % label)
		return
	var image := texture.get_image()
	if image == null:
		print("  %s -> skipped (renderer returned no image)" % label)
		return
	var path := "%s/%s.png" % [SHOT_DIR, label]
	var err := image.save_png(path)
	print("  %s -> %s" % [label, "ok" if err == OK else error_string(err)])

func _wait_for(label: String, timeout: float = 8.0) -> void:
	var deadline := Time.get_ticks_msec() + int(timeout * 1000.0)
	while Flow.current_name != label and Time.get_ticks_msec() < deadline:
		await get_tree().process_frame

func _frames(count: int) -> void:
	for i: int in count:
		await get_tree().process_frame
