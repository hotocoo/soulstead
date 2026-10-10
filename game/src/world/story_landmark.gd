class_name StoryLandmark
extends Interactable
## A physical story beat in the field. Story progression is allowed to happen
## only after the player walks to the authored place and touches it.

var event_ids: Array[String] = []
var line: String = ""

func configure(events: Array[String], prompt_text: String, text: String) -> void:
	event_ids = events
	prompt = prompt_text
	line = text
	var marker := MeshInstance3D.new()
	marker.mesh = Look._organic_ellipsoid(Vector3(0.30, 0.12, 0.22), 32, 2.4)
	marker.material_override = Look.emissive(Look.EMBER, 1.6)
	marker.position.y = 0.12
	add_child(marker)
	add_body(Vector3(0.8, 0.4, 0.8), Vector3(0, 0.2, 0))

func interact(world: Node) -> void:
	for event_id: String in event_ids:
		if WorldState.story_director != null:
			WorldState.story_director.notify_event(event_id)
	if world.has_method("say") and line != "":
		world.say(line)
