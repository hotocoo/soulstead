class_name SettlementFacility
extends Interactable
## A working settlement building. The settlement is not a menu backdrop:
## timber, iron and relics can be turned into stronger infrastructure, and
## infrastructure changes the lives the next successor inherits.

var facility_id: String = "smithy"
var facility_name: String = "Smithy"
var description: String = ""

func configure(id: String, title: String, detail: String) -> void:
	facility_id = id
	facility_name = title
	description = detail
	prompt = "Use %s" % facility_name
	_build_architecture()
	add_body(Vector3(2.2, 1.8, 1.8), Vector3(0, 0.9, 0))

func _part(size: Vector3, at: Vector3, material: StandardMaterial3D, rotation: Vector3 = Vector3.ZERO) -> void:
	var node := MeshInstance3D.new()
	node.mesh = Look._rounded_block_mesh(size, minf(size.x, size.z) * 0.14, 20)
	node.material_override = material
	node.position = at
	node.rotation = rotation
	add_child(node)

func _build_architecture() -> void:
	var wall := Look.standard(_material_color(), 0.78)
	var timber := Look.standard(Color("#35261d"), 0.88)
	var roof := Look.standard(Color("#302b31"), 0.9)
	var glass := Look.standard(Color("#9eb5b8"), 0.22)
	glass.metallic = 0.15

	_part(Vector3(2.5, 0.22, 2.1), Vector3(0, 0.11, 0), timber)
	_part(Vector3(2.2, 1.42, 1.8), Vector3(0, 0.82, 0), wall)
	_part(Vector3(0.14, 1.45, 0.14), Vector3(-0.88, 0.82, -0.94), timber)
	_part(Vector3(0.14, 1.45, 0.14), Vector3(0.88, 0.82, -0.94), timber)
	_part(Vector3(2.32, 0.14, 0.14), Vector3(0, 1.48, -0.94), timber)

	# Steep twin roof planes read as a hand-built structure at distance.
	_part(Vector3(1.35, 0.14, 2.12), Vector3(-0.56, 1.62, 0), roof, Vector3(0, 0, deg_to_rad(-28.0)))
	_part(Vector3(1.35, 0.14, 2.12), Vector3(0.56, 1.62, 0), roof, Vector3(0, 0, deg_to_rad(28.0)))

	# Door, transom and two glazed windows give each facility a readable face.
	_part(Vector3(0.46, 0.9, 0.08), Vector3(0, 0.48, -0.93), timber)
	_part(Vector3(0.34, 0.46, 0.04), Vector3(-0.58, 0.92, -0.96), glass)
	_part(Vector3(0.34, 0.46, 0.04), Vector3(0.58, 0.92, -0.96), glass)
	_part(Vector3(0.08, 0.52, 0.05), Vector3(-0.58, 0.92, -0.99), timber)
	_part(Vector3(0.08, 0.52, 0.05), Vector3(0.58, 0.92, -0.99), timber)

	if facility_id == "smithy":
		_part(Vector3(0.42, 1.0, 0.42), Vector3(0.62, 2.0, 0.32), timber)
		var glow := Look.emissive(Look.EMBER, 1.2)
		_part(Vector3(0.18, 0.18, 0.05), Vector3(0, 1.04, -1.0), glow)
	elif facility_id == "fields":
		for i: int in 4:
			_part(Vector3(0.18, 0.04, 1.25), Vector3(-0.72 + i * 0.48, 0.04, 1.2), Look.standard(Color("#7f6b3f"), 0.92))
	elif facility_id == "palisade":
		for i: int in 5:
			var post := MeshInstance3D.new()
			post.mesh = Look._segment_mesh(Vector3(0, -0.8, 0), Vector3(0.02, 0.8, 0.02), 0.11, 0.045, 24)
			post.material_override = timber
			post.position = Vector3(-1.0 + i * 0.5, 0.8, 0.98)
			add_child(post)

func _material_color() -> Color:
	match facility_id:
		"smithy": return Color("#70452f")
		"fields": return Color("#52663d")
		"palisade": return Color("#51402f")
		_: return Color("#5b5350")

func interact(world: Node) -> void:
	if world.has_method("open_facility"):
		world.open_facility(facility_id, facility_name, description)
