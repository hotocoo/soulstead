class_name Villager
extends Interactable
## A settlement resident. The same dictionary shown here can be chosen as the
## next wielder, so the person hauling timber is the person whose hands you
## take the blade with.

var data: Dictionary = {}

var _figure: Node3D
var _origin := Vector3.ZERO
var _phase := 0.0

func _ready() -> void:
	super()
	prompt = "Speak"
	_origin = position
	_phase = randf() * TAU
	_figure = Look.authored("villager", 0.32)
	add_child(_figure)
	add_body(Vector3(0.9, 1.6, 0.9), Vector3(0, 0.8, 0))

## Colour reads the person's job, so the settlement is legible at a glance.
func _tint() -> Color:
	match String(data.get("job", "")):
		"Smith": return Color("#b06a3a")
		"Healer": return Color("#5fae86")
		"Warden": return Color("#4d5a6b")
		"Forager": return Color("#7d9a4a")
		"Carver": return Color("#9a7b5a")
		_: return Color("#c9c2b6")

func _process(delta: float) -> void:
	_phase += delta * 0.7
	position.x = _origin.x + sin(_phase) * 0.35
	if _figure != null:
		_figure.rotation.y = sin(_phase * 0.5) * 0.8

func line() -> String:
	var name := String(data.get("name", "Someone"))
	# React to recent player actions
	if WorldState.kill_count > 10:
		return "%s: "You've been out there a while. The ash-things must be thick."" % name
	if WorldState.materials["relic"] > 0:
		return "%s: "Is that a relic you found? Those are rare these days."" % name
	if WorldState.grief > 80:
		return "%s: "I can see the weight on your shoulders. Rest a while."" % name
	var job := String(data.get("job", "Field-hand"))
	if WorldState.grief > 60:
		return "%s, %s: \"Nobody is working. We keep listening for them.\"" % [name, job]
	if not WorldState.echoes.is_empty():
		return "%s, %s: \"%s is still out there. Walking.\"" % [name, job,
				WorldState.echoes[0]["owner"]]
	if WorldState.grief > 20:
		return "%s, %s: \"We should hold something for them. Soon.\"" % [name, job]
	return "%s, %s: \"Work's steady. Keep it that way.\"" % [name, job]

func interact(world: Node) -> void:
	world.say(line())
