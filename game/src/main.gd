extends Node
## Entry point. Owns the scene container and hands it to Flow.

func _ready() -> void:
	var container := Node.new()
	container.name = "Scene"
	add_child(container)
	var story := StoryDirector.new()
	story.name = "StoryDirector"
	add_child(story)
	WorldState.story_director = story
	EchoExchange.ensure_dirs()
	Flow.bind(container)
	Flow.to_title()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_F5:
			WorldState.save_game()
			Chronicle.record("quick_saved", {"text": "Quick-saved."})
		elif event.keycode == KEY_F9:
			WorldState.load_game()
			Chronicle.record("quick_loaded", {"text": "Quick-loaded."})

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		if NetSession.is_networked():
			NetSession.leave()
		WorldState.save_game()
