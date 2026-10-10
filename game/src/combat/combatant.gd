class_name Combatant
extends CharacterBody3D
## Shared 3D body for anything that swings and bleeds.
##
## Combat is commitment-based: startup -> active -> recovery, no cancelling.
## Poise decides whether a hit interrupts, and regenerates out of combat so
## trading blows is a choice rather than a death sentence.

signal died(who: Combatant)
signal health_changed(current: float, maximum: float)
signal poise_broken()

enum State { IDLE, WINDUP, ACTIVE, RECOVER, DODGE, PARRY, GUARD, STAGGER, DEAD }

const GRAVITY := 22.0
const POISE_REGEN := 18.0
const STAGGER_TIME := 0.5
const HIT_FLASH := 0.14
const TURN_SPEED := 12.0

@export var display_name: String = "Combatant"
@export var max_health: float = 100.0
@export var max_poise: float = 30.0
@export var move_speed: float = 4.0
@export var faction: String = "hostile"

var health: float = 100.0
var poise: float = 30.0
var state: State = State.IDLE
## Facing is kept flat on the XZ plane; combat never aims up or down.
var facing: Vector3 = Vector3.FORWARD

var visual: Node3D
var _tinted: Array[Dictionary] = []
var _state_timer: float = 0.0
var _flash_timer: float = 0.0
var _base_material: StandardMaterial3D

func _ready() -> void:
	add_to_group("combatants")
	health = max_health
	poise = max_poise
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = Look.BODY_RADIUS
	capsule.height = Look.BODY_HEIGHT
	shape.shape = capsule
	shape.position = Vector3(0, Look.BODY_HEIGHT * 0.5, 0)
	add_child(shape)

func set_visual(node: Node3D) -> void:
	if visual != null:
		visual.queue_free()
	visual = node
	add_child(node)
	# Materials are duplicated per body so a hit flash tints one combatant
	# rather than every enemy sharing that material.
	_tinted.clear()
	for child: Node in node.get_children():
		var mesh := child as MeshInstance3D
		if mesh == null or mesh.material_override == null:
			continue
		var material := mesh.material_override.duplicate() as StandardMaterial3D
		mesh.material_override = material
		_tinted.append({"material": material, "base": material.albedo_color})

func is_alive() -> bool:
	return state != State.DEAD

func is_busy() -> bool:
	return state in [State.WINDUP, State.ACTIVE, State.RECOVER, State.DODGE, State.PARRY, State.GUARD, State.STAGGER]

## Invulnerability sits at the front of the roll: commit early, recover late.
func is_invulnerable() -> bool:
	return state == State.DODGE and _state_timer > dodge_duration() - dodge_iframe_window()

func dodge_iframe_window() -> float:
	return 0.18

func dodge_duration() -> float:
	return 0.42

func _physics_process(delta: float) -> void:
	_state_timer = maxf(0.0, _state_timer - delta)
	if _flash_timer > 0.0:
		_flash_timer -= delta
		if _flash_timer <= 0.0:
			_set_tint(Color.WHITE)
	if state != State.DEAD and poise < max_poise:
		poise = minf(max_poise, poise + POISE_REGEN * delta)
	if not is_on_floor():
		velocity.y -= GRAVITY * delta
	else:
		velocity.y = 0.0
	_face_visual(delta)
	move_and_slide()

func _face_visual(delta: float) -> void:
	if visual == null or facing.length_squared() < 0.001:
		return
	var target := atan2(facing.x, facing.z)
	visual.rotation.y = lerp_angle(visual.rotation.y, target, TURN_SPEED * delta)

func _set_tint(color: Color) -> void:
	for entry: Dictionary in _tinted:
		var material: StandardMaterial3D = entry["material"]
		var base: Color = entry["base"]
		material.albedo_color = base if color == Color.WHITE else base * color

## Returns true if the hit landed. `info` carries damage, poise_damage and the
## attacker, so parries and knockback can read the source.
func take_hit(info: Dictionary) -> bool:
	if state == State.DEAD or is_invulnerable():
		return false
	if state == State.PARRY and _within_parry_window():
		on_parry_success(info)
		return false
	var damage := float(info.get("damage", 0.0))
	var poise_damage := float(info.get("poise_damage", 0.0))
	# Guarding reduces damage and poise damage
	if state == State.GUARD:
		damage *= guard_damage_reduction()
		poise_damage *= guard_poise_reduction()
	health = maxf(0.0, health - damage)
	poise -= poise_damage
	health_changed.emit(health, max_health)
	_flash()
	show_damage_number(damage)
	if get_tree().root.has_node("AudioManager"):
		get_tree().root.get_node("AudioManager").play_hit()
	var knock: Vector3 = info.get("knockback", Vector3.ZERO)
	if knock != Vector3.ZERO:
		velocity = Vector3(knock.x, velocity.y, knock.z)
	if health <= 0.0:
		die()
		return true
	if poise <= 0.0:
		poise = max_poise
		poise_broken.emit()
		enter_state(State.STAGGER, STAGGER_TIME)
	return true

func guard_damage_reduction() -> float:
	return 0.4

func guard_poise_reduction() -> float:
	return 0.3

func _within_parry_window() -> bool:
	return _state_timer > parry_recovery()

func parry_recovery() -> float:
	return 0.24

func on_parry_success(_info: Dictionary) -> void:
	pass

func _flash() -> void:
	_set_tint(Color(2.0, 1.4, 1.2))
	_flash_timer = HIT_FLASH

## Show floating damage number above the combatant.
func show_damage_number(amount: float) -> void:
	if amount <= 0.0:
		return
	var label := Label3D.new()
	label.text = str(int(amount))
	label.position = global_position + Vector3(0, Look.BODY_HEIGHT + 0.4, 0)
	label.font_size = 14
	label.modulate = Color(1.0, 0.85, 0.6)
	label.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	get_tree().root.add_child(label)
	var tween := get_tree().create_tween()
	tween.tween_property(label, "position:y", label.position.y + 0.8, 0.7)
	tween.parallel().tween_property(label, "modulate:a", 0.0, 0.7)
	tween.tween_callback(label.queue_free)

func enter_state(next: State, duration: float) -> void:
	state = next
	_state_timer = duration

func state_time_left() -> float:
	return _state_timer

func die() -> void:
	state = State.DEAD
	velocity = Vector3.ZERO
	set_collision_layer_value(1, false)
	died.emit(self)
	var tween := create_tween()
	if visual != null:
		tween.tween_property(visual, "scale", Vector3(1.1, 0.05, 1.1), 0.45)
	tween.tween_callback(queue_free)

## Melee resolves as a cone in front of the attacker on the XZ plane.
func swing(reach: float, arc: float, info: Dictionary) -> Array[Combatant]:
	var hits: Array[Combatant] = []
	var origin := global_position
	for node: Node in get_tree().get_nodes_in_group("combatants"):
		var other := node as Combatant
		if other == null or other == self or not other.is_alive():
			continue
		if other.faction == faction:
			continue
		var offset: Vector3 = other.global_position - origin
		offset.y = 0.0
		if offset.length() > reach + Look.BODY_RADIUS:
			continue
		if absf(offset.normalized().signed_angle_to(facing, Vector3.UP)) > arc * 0.5:
			continue
		var hit_info := info.duplicate()
		hit_info["attacker"] = self
		hit_info["knockback"] = offset.normalized() * float(info.get("knock_force", 4.0))
		# Critical hit: 2x damage when hitting an enemy from behind or when poise-broken
		var is_crit := false
		var to_target := offset.normalized()
		if absf(to_target.signed_angle_to(other.facing, Vector3.UP)) > deg_to_rad(90.0):
			is_crit = true  # Backstab
		elif other.state == State.STAGGER:
			is_crit = true  # Poise-broken
		if is_crit:
			hit_info["damage"] = float(hit_info["damage"]) * 2.0
			if other.take_hit(hit_info):
				hits.append(other)
				Look.ember_burst(other.global_position + Vector3(0, Look.BODY_HEIGHT * 0.8, 0), get_tree().root)
				# Larger damage number for crits
				var label := Label3D.new()
				label.text = "CRIT " + str(int(float(hit_info["damage"])))
				label.position = other.global_position + Vector3(0, Look.BODY_HEIGHT + 0.8, 0)
				label.font_size = 16
				label.modulate = Color(1.0, 0.6, 0.2)
				label.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
				get_tree().root.add_child(label)
				var tween := get_tree().create_tween()
				tween.tween_property(label, "position:y", label.position.y + 0.6, 0.6)
				tween.parallel().tween_property(label, "modulate:a", 0.0, 0.6)
				tween.tween_callback(label.queue_free)
		elif other.take_hit(hit_info):
			hits.append(other)
			Look.ember_burst(other.global_position + Vector3(0, Look.BODY_HEIGHT * 0.6, 0), get_tree().root)
	return hits
