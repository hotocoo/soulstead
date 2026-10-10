class_name PlayerActor
extends Combatant
## The wielder in 3D. Souls weight: committed swings, Composure instead of
## stamina, dodge i-frames at the front of the roll, a tight parry. Stats come
## from whichever villager currently holds the blade.

signal composure_changed(current: float, maximum: float)
signal flask_used(left: int)
signal died_in_field(position: Vector3, killed_by: String)

const WALK_SPEED := 4.4
const DODGE_SPEED := 11.0
const DODGE_TIME := 0.42
const PARRY_TIME := 0.36
const COMPOSURE_DELAY := 0.55
const COMPOSURE_REGEN := 34.0
const DODGE_COST := 22.0
const FLASK_HEAL := 45.0
const FLASK_TIME := 0.9
## True third-person perspective. The camera is physically behind the
## character, orbits freely around them, and movement is camera-relative.
const CAMERA_DISTANCE := 4.8
const CAMERA_HEIGHT := 1.72
const CAMERA_PITCH := -2.0
const CAMERA_TARGET_HEIGHT := 1.18
const CAMERA_FOV := 58.0
const CAMERA_SENSITIVITY := 0.004
const CAMERA_MIN_PITCH := -55.0
const CAMERA_MAX_PITCH := 18.0

var max_composure: float = 100.0
var composure: float = 100.0
var power: float = 1.0
var composure_regen_mult: float = 1.0
var weapon_id: String = "ashblade"
var input_enabled: bool = true
var last_attacker: String = "something in the dark"

var camera: Camera3D

var _regen_delay: float = 0.0
var _attack: Dictionary = {}
var _attack_kind: String = "light"
var _dodge_direction := Vector3.FORWARD
var _blade: Node3D
var _camera_yaw := 0.0
var _camera_pitch := CAMERA_PITCH

func _ready() -> void:
	faction = "player"
	add_to_group("player")
	super()
	apply_wielder_stats()
	set_visual(Look.authored("villager", 0.32))
	_blade = Look.authored("ashblade", 0.22)
	_blade.name = "Blade"
	_blade.position = Vector3(0.34, 0.62, 0.24)
	_blade.rotation_degrees = Vector3(18.0, 0.0, 9.0)
	visual.add_child(_blade)
	_build_camera()
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func apply_wielder_stats() -> void:
	var stats: Dictionary = WorldState.wielder_stats()
	max_health = float(stats["max_hp"])
	max_composure = float(stats["max_composure"])
	power = float(stats["power"])
	composure_regen_mult = float(stats["composure_regen"])
	weapon_id = String(stats["weapon"])
	max_poise = 45.0
	health = max_health
	composure = max_composure
	poise = max_poise
	display_name = String(WorldState.wielder().get("name", "The Wielder"))
	health_changed.emit(health, max_health)
	composure_changed.emit(composure, max_composure)

## The camera is parented to a pivot that does not rotate with the body, so the
## world stays readable while the wielder turns.
func _build_camera() -> void:
	var pivot := Node3D.new()
	pivot.name = "CameraPivot"
	add_child(pivot)
	pivot.position = Vector3.ZERO
	pivot.rotation = Vector3(deg_to_rad(_camera_pitch), _camera_yaw, 0.0)
	# Explicit orbital camera avoids engine-version-dependent SpringArm direction
	# semantics while keeping a true over-the-shoulder third-person view.
	camera = Camera3D.new()
	camera.position = Vector3(0, CAMERA_HEIGHT, CAMERA_DISTANCE)
	camera.fov = CAMERA_FOV
	pivot.add_child(camera)
	camera.make_current()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		var motion := event as InputEventMouseMotion
		_camera_yaw -= motion.relative.x * CAMERA_SENSITIVITY
		_camera_pitch = clampf(_camera_pitch - motion.relative.y * CAMERA_SENSITIVITY,
				CAMERA_MIN_PITCH, CAMERA_MAX_PITCH)
		var pivot := get_node_or_null("CameraPivot") as Node3D
		if pivot != null:
			pivot.rotation = Vector3(_camera_pitch, _camera_yaw, 0.0)
	elif event is InputEventKey:
		var key := event as InputEventKey
		if key.pressed and key.keycode == KEY_ESCAPE:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseButton:
		var button := event as InputEventMouseButton
		if button.pressed and Input.mouse_mode == Input.MOUSE_MODE_VISIBLE:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func dodge_duration() -> float:
	return DODGE_TIME

func weapon() -> Dictionary:
	return Codex.weapon(weapon_id)

func _process(delta: float) -> void:
	var pivot := get_node_or_null("CameraPivot") as Node3D
	if pivot == null:
		return
	if camera != null:
		var view_forward := -pivot.global_basis.z
		view_forward.y = 0.0
		view_forward = view_forward.normalized()
		camera.look_at(global_position + view_forward * 1.7 + Vector3(0, CAMERA_TARGET_HEIGHT, 0), Vector3.UP)

func _physics_process(delta: float) -> void:
	if state == State.DEAD:
		super(delta)
		return
	_tick_composure(delta)
	match state:
		State.IDLE:
			_handle_free_movement(delta)
		State.WINDUP:
			_advance_attack(delta, State.ACTIVE)
		State.ACTIVE:
			_advance_attack(delta, State.RECOVER)
		State.RECOVER:
			_advance_attack(delta, State.IDLE)
		State.DODGE:
			var speed := DODGE_SPEED * clampf(state_time_left() / DODGE_TIME, 0.25, 1.0)
			velocity.x = _dodge_direction.x * speed
			velocity.z = _dodge_direction.z * speed
			if state_time_left() <= 0.0:
				_finish_action()
		State.PARRY, State.STAGGER:
			velocity.x = move_toward(velocity.x, 0.0, 30.0 * delta)
			velocity.z = move_toward(velocity.z, 0.0, 30.0 * delta)
			if state_time_left() <= 0.0:
				_finish_action()
	_animate_blade(delta)
	super(delta)

func _tick_composure(delta: float) -> void:
	_regen_delay = maxf(0.0, _regen_delay - delta)
	if _regen_delay > 0.0 or composure >= max_composure:
		return
	composure = minf(max_composure, composure + COMPOSURE_REGEN * composure_regen_mult * delta)
	composure_changed.emit(composure, max_composure)

func _spend_composure(amount: float) -> void:
	composure = maxf(0.0, composure - amount)
	_regen_delay = COMPOSURE_DELAY
	composure_changed.emit(composure, max_composure)

func _handle_free_movement(delta: float) -> void:
	var input := Vector2.ZERO
	if input_enabled:
		input = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var pivot := get_node_or_null("CameraPivot") as Node3D
	var forward := -global_basis.z
	var right := global_basis.x
	if pivot != null:
		forward = -pivot.global_basis.z
		right = pivot.global_basis.x
	forward.y = 0.0
	right.y = 0.0
	forward = forward.normalized()
	right = right.normalized()
	var direction := (right * input.x + forward * input.y).normalized() if input.length() > 0.1 else Vector3.ZERO
	if direction.length() > 0.1:
		facing = direction.normalized()
	velocity.x = move_toward(velocity.x, direction.x * WALK_SPEED, 40.0 * delta)
	velocity.z = move_toward(velocity.z, direction.z * WALK_SPEED, 40.0 * delta)
	if not input_enabled:
		return
	if Input.is_action_just_pressed("dodge"):
		_try_dodge(direction)
	elif Input.is_action_just_pressed("light_attack"):
		_try_attack("light")
	elif Input.is_action_just_pressed("heavy_attack"):
		_try_attack("heavy")
	elif Input.is_action_just_pressed("parry"):
		_try_parry()
	elif Input.is_action_just_pressed("flask"):
		use_flask()

# --- Actions -------------------------------------------------------------

func _try_dodge(direction: Vector3) -> void:
	if composure < DODGE_COST:
		# Out of Composure: a slow sidestep with no invulnerability. The cost of
		# overspending is positional, not instant death.
		var shove := direction if direction.length() > 0.1 else facing
		velocity.x = shove.x * 2.0
		velocity.z = shove.z * 2.0
		return
	_dodge_direction = direction.normalized() if direction.length() > 0.1 else facing
	_spend_composure(DODGE_COST)
	enter_state(State.DODGE, DODGE_TIME)

func _try_attack(kind: String) -> void:
	var data: Dictionary = weapon()[kind]
	if composure < float(data["cost"]):
		return
	_attack = data
	_attack_kind = kind
	_spend_composure(float(data["cost"]))
	enter_state(State.WINDUP, float(data["startup"]))

func _try_parry() -> void:
	if composure < 10.0:
		return
	_spend_composure(10.0)
	enter_state(State.PARRY, PARRY_TIME)

func parry_recovery() -> float:
	return PARRY_TIME - 0.12

func on_parry_success(info: Dictionary) -> void:
	composure = minf(max_composure, composure + 24.0)
	composure_changed.emit(composure, max_composure)
	var attacker := info.get("attacker") as Combatant
	if attacker != null and attacker.is_alive():
		attacker.take_hit({"damage": 0.0, "poise_damage": attacker.max_poise + 1.0,
			"attacker": self})
	enter_state(State.RECOVER, 0.12)

func _advance_attack(delta: float, next: State) -> void:
	velocity.x = move_toward(velocity.x, 0.0, 40.0 * delta)
	velocity.z = move_toward(velocity.z, 0.0, 40.0 * delta)
	if state_time_left() > 0.0:
		return
	match next:
		State.ACTIVE:
			enter_state(State.ACTIVE, float(_attack["active"]))
			_resolve_swing()
		State.RECOVER:
			enter_state(State.RECOVER, float(_attack["recovery"]))
		_:
			_finish_action()

func _resolve_swing() -> void:
	var data: Dictionary = weapon()
	var damage_multiplier := 1.0
	var bond_kind := String(WorldState.wielder().get("bond_to_dead", "stranger"))
	if bond_kind == "spouse":
		for echo: Dictionary in WorldState.echoes_in(WorldState.current_location):
			var pos: Array = echo.get("pos", [INF, INF])
			if global_position.distance_to(Vector3(float(pos[0]), global_position.y, float(pos[1]))) <= 5.0:
				damage_multiplier = 1.15
				break
	var hits := swing(float(data["reach"]), float(data["arc"]), {
		"damage": float(data["power"]) * float(_attack["motion"]) * power * damage_multiplier,
		"poise_damage": float(_attack["poise"]),
		"knock_force": 6.0 if _attack_kind == "heavy" else 3.0,
	})
	if not hits.is_empty():
		_regen_delay = COMPOSURE_DELAY * 0.5

## The blade reads the attack state: cocked back on windup, swept on active.
func _animate_blade(delta: float) -> void:
	if _blade == null:
		return
	var target := 0.0
	match state:
		State.WINDUP:
			target = -1.5
		State.ACTIVE:
			target = 1.3
		State.RECOVER:
			target = 0.6
	_blade.rotation.y = lerp_angle(_blade.rotation.y, target, 18.0 * delta)

func _finish_action() -> void:
	enter_state(State.IDLE, 0.0)

func use_flask() -> void:
	if WorldState.flasks_left <= 0 or health >= max_health or is_busy():
		return
	WorldState.flasks_left -= 1
	health = minf(max_health, health + FLASK_HEAL)
	health_changed.emit(health, max_health)
	flask_used.emit(WorldState.flasks_left)
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("flask_used")
	enter_state(State.RECOVER, FLASK_TIME)

func take_hit(info: Dictionary) -> bool:
	var attacker := info.get("attacker") as Combatant
	if attacker != null:
		last_attacker = attacker.display_name
	var landed := super(info)
	if landed and state != State.DEAD:
		# Being hit mid-swing costs Composure: pressure compounds.
		_spend_composure(8.0)
	return landed

func die() -> void:
	if state == State.DEAD:
		return
	died_in_field.emit(global_position, last_attacker)
	super()
