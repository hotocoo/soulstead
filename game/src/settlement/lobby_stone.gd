class_name LobbyStone
extends Interactable
## Multiplayer from inside the fiction: a marker stone that calls to other
## settlements. Friends anywhere on the internet answer it with a lobby code.

var _rune: MeshInstance3D
var _light: OmniLight3D
var _time := 0.0

func _ready() -> void:
	super()
	prompt = "Call another settlement"
	var stone := MeshInstance3D.new()
	stone.mesh = Look._organic_ellipsoid(Vector3(0.56, 1.5, 0.38), 32, 2.8)
	stone.material_override = Look.standard(Color("#565060"))
	stone.position = Vector3(0, 1.5, 0)
	stone.rotation.z = 0.06
	add_child(stone)

	_rune = MeshInstance3D.new()
	_rune.mesh = Look._organic_ellipsoid(Vector3(0.22, 0.04, 0.36), 24, 1.4)
	_rune.material_override = Look.emissive(Look.COLD, 2.4)
	_rune.position = Vector3(0, 2.1, 0.4)
	add_child(_rune)

	_light = OmniLight3D.new()
	_light.light_color = Look.COLD
	_light.light_energy = 1.4
	_light.omni_range = 7.0
	_light.position = Vector3(0, 2.1, 0.6)
	add_child(_light)
	add_body(Vector3(1.2, 3.0, 0.9), Vector3(0, 1.5, 0))

func _process(delta: float) -> void:
	_time += delta
	_rune.rotation.y = _time * 0.8
	var connected := NetSession.is_networked()
	var color: Color = Look.EMBER if connected else Look.COLD
	_light.light_color = color
	_light.light_energy = (2.6 if connected else 1.2) + sin(_time * 2.4) * 0.35
	(_rune.material_override as StandardMaterial3D).emission = color

func interact(world: Node) -> void:
	world.open_lobby()
