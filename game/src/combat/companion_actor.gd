class_name CompanionActor
extends Combatant
## A settlement villager who accompanies the player on expeditions.
## Follows the player and attacks nearby enemies.

const FOLLOW_DISTANCE := 3.0
const ATTACK_RANGE := 4.0

var player: PlayerActor
var _target: Combatant = null
var _follow_timer: float = 0.0

func _ready() -> void:
	faction = "player"
	state = State.IDLE
	super()

func set_player(p: PlayerActor) -> void:
	player = p

func _physics_process(delta: float) -> void:
	if state == State.DEAD or player == null:
		return
	if is_busy():
		return
	# Find nearest enemy
	if _target == null or _target.state == State.DEAD or global_position.distance_to(_target.global_position) > 20.0:
		_target = null
		var enemies = get_tree().get_nodes_in_group("enemies")
		var best_dist := INF
		for enemy in enemies:
			var dist = global_position.distance_to(enemy.global_position)
			if dist < best_dist and dist < ATTACK_RANGE * 2.5:
				best_dist = dist
				_target = enemy
	if _target != null:
		# Attack target
		var dist = global_position.distance_to(_target.global_position)
		if dist > reach:
			# Move toward target
			var dir = (_target.global_position - global_position).normalized()
			velocity = Vector3(dir.x, 0, dir.z) * WALK_SPEED
			move_and_slide()
			facing = dir
		else:
			# Attack
			velocity = Vector3.ZERO
			move_and_slide()
			facing = (_target.global_position - global_position).normalized()
			_swing_light()
	else:
		# Follow player
		var dist = global_position.distance_to(player.global_position)
		if dist > FOLLOW_DISTANCE:
			var dir = (player.global_position - global_position).normalized()
			velocity = Vector3(dir.x, 0, dir.z) * WALK_SPEED
			move_and_slide()
			facing = dir
		else:
			velocity = Vector3.ZERO
			move_and_slide()
			# Face player
			if player != null:
				facing = (player.global_position - global_position).normalized()

func _swing_light() -> void:
	if is_busy():
		return
	enter_state(State.WINDUP, 0.15)
	_swing_timer = 0.15
	_swing_type = "light"

func _resolve_swing() -> void:
	var damage := 8.0 * power
	var hits := swing(reach, 1.5, {"damage": damage, "poise_damage": 5.0, "knock_force": 3.0})
	if not hits.is_empty():
		AudioManager.play_hit()
	_finish_action()

func _swing(data: Dictionary) -> void:
	_swing_timer = float(data["windup"]) + float(data["active"]) + float(data["recovery"])
	_swing_data = data

func _finish_action() -> void:
	enter_state(State.IDLE, 0.0)

func take_hit(info: Dictionary) -> bool:
	if not super(info):
		return false
	# Aggro the player if companion is hit
	if player != null and _target == null:
		var enemies = get_tree().get_nodes_in_group("enemies")
		for enemy in enemies:
			if global_position.distance_to(enemy.global_position) < 10.0:
				_target = enemy
				break
	return true
