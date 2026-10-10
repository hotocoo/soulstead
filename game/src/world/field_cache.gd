class_name FieldCache
extends Interactable
## A small field cache. Exploration needs a physical reward loop, but caches
## never become a conventional loot treadmill: they pay for the settlement's
## work and leave a Chronicle trace instead.

var cache_id: String = ""
var opened := false
var _lid: MeshInstance3D

func configure(id: String, opened_state: bool = false) -> void:
	cache_id = id
	opened = opened_state
	prompt = "Read the cache" if opened else "Open the field cache"
	var body := MeshInstance3D.new()
	body.mesh = Look._rounded_block_mesh(Vector3(0.9, 0.55, 0.65), 0.10, 24)
	body.material_override = Look.standard(Color("#6e4b2e"))
	body.position = Vector3(0, 0.28, 0)
	add_child(body)
	_lid = MeshInstance3D.new()
	_lid.mesh = Look._rounded_block_mesh(Vector3(0.94, 0.10, 0.70), 0.07, 24)
	_lid.material_override = Look.standard(Color("#8b6337"))
	_lid.position = Vector3(0, 0.61, 0)
	add_child(_lid)
	if opened:
		_lid.rotation.x = deg_to_rad(-58.0)
	add_body(Vector3(1.0, 1.0, 0.8), Vector3(0, 0.5, 0))

func interact(world: Node) -> void:
	if opened:
		if world.has_method("say"):
			world.say("The cache is empty. What was taken is already part of the Hold's work.")
		return
	opened = true
	prompt = "Read the cache"
	_lid.rotation.x = deg_to_rad(-58.0)
	var timber := 2 + (absi(cache_id.hash()) % 4)
	var iron := absi((cache_id + "iron").hash()) % 2
	WorldState.materials["timber"] = int(WorldState.materials.get("timber", 0)) + timber
	WorldState.materials["iron"] = int(WorldState.materials.get("iron", 0)) + iron
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("field_cache_opened", {"key": cache_id})
	Chronicle.record("cache_opened", cache_id)
	WorldState.save_game()
	if world.has_method("say"):
		world.say("The cache yields %d timber%s. The Hold can use what the road leaves behind." % [
			timber, " and %d iron" % iron if iron > 0 else ""])
