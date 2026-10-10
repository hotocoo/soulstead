class_name Hearth
extends Interactable
## The hub fire. Saves the world, refills flasks, and sends the wielder out.

var _flame: MeshInstance3D
var _light: OmniLight3D
var _time := 0.0

func _ready() -> void:
	super()
	prompt = "Set out"
	for i: int in 10:
		var ember_stone := MeshInstance3D.new()
		ember_stone.mesh = Look._organic_ellipsoid(Vector3(0.24, 0.14, 0.18), 24, 2.2)
		ember_stone.material_override = Look.standard(Color("#4a4148"), 0.92)
		var angle := TAU * float(i) / 10.0
		ember_stone.position = Vector3(cos(angle) * 1.05, 0.14, sin(angle) * 1.05)
		add_child(ember_stone)

	_flame = Look.flame()
	add_child(_flame)

	_light = OmniLight3D.new()
	_light.light_color = Color("#ffb36b")
	_light.light_energy = 3.2
	_light.omni_range = 12.0
	_light.position = Vector3(0, 1.2, 0)
	add_child(_light)
	add_body(Vector3(1.6, 1.0, 1.6), Vector3(0, 0.5, 0))

func _process(delta: float) -> void:
	_time += delta
	var flicker := 1.0 + sin(_time * 7.0) * 0.12 + sin(_time * 11.3) * 0.05
	_flame.scale = Vector3(1.0, flicker, 1.0)
	_light.light_energy = 3.0 + sin(_time * 9.0) * 0.4

func interact(world: Node) -> void:
	world.open_departure()
