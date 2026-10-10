class_name Memorial
extends Interactable
## Where grief is spent. Each Vigil converts grief into a permanent Legacy that
## every future successor inherits. One stone rises per name in the lineage.

func _ready() -> void:
	super()
	prompt = "Hold a vigil"
	var plinth := MeshInstance3D.new()
	plinth.mesh = Look._rounded_block_mesh(Vector3(4.0, 0.4, 2.4), 0.18, 28)
	plinth.material_override = Look.standard(Color("#4a434b"))
	plinth.position = Vector3(0, 0.2, 0)
	add_child(plinth)
	_raise_stones()
	add_body(Vector3(4.0, 2.0, 2.4), Vector3(0, 1.0, 0))

## The memorial is a readout of the lineage: every death that has been buried
## stands here, so the cost of the run is visible before any menu opens.
func _raise_stones() -> void:
	var count: int = maxi(3, mini(WorldState.lineage.size() + 2, 9))
	for i: int in count:
		var stone := MeshInstance3D.new()
		var height := 1.0 + float(i % 3) * 0.45
		stone.mesh = Look._organic_ellipsoid(Vector3(0.24, height * 0.5, 0.17), 24, 2.0)
		stone.material_override = Look.standard(Color("#6e6470").darkened(float(i % 4) * 0.06))
		var offset := -1.6 + float(i) * (3.2 / maxf(1.0, float(count - 1)))
		stone.position = Vector3(offset, 0.4 + height * 0.5, 0.0)
		stone.rotation.y = float(i) * 0.21
		add_child(stone)

func interact(world: Node) -> void:
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("memorial_inspected")
		WorldState.story_director.notify_event("carver_glass")
	world.open_vigils()
