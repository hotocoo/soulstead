class_name EnemyActor
extends Combatant
## Field enemy with a readable tell: the body flashes ember and rears back for
## `tell` seconds before the active frames. Difficulty comes from reading the
## wind-up, never from hidden information.

signal slain(enemy: EnemyActor)
signal spared(enemy: EnemyActor)

const IDLE_WANDER_TIME := 2.0
const LOSE_AGGRO_DISTANCE := 28.0

var archetype: String = "husk"
var damage: float = 10.0
var tell_time: float = 0.4
var reach: float = 2.0
var aggro_range: float = 14.0
var relics: int = 0
var posture: String = "shambler"
var drop_chance: float = 0.25

var _target: Combatant
var _wander_timer: float = 0.0
var _wander_direction := Vector3.ZERO
var _was_provoked := false
var _tell_phase := 0.0
var _hp_bar: Label3D
var _phase2: bool = false

func _ready() -> void:
	faction = "hostile"
	add_to_group("enemies")
	super()
	if visual == null:
		configure(archetype)
	_build_hp_bar()

func _build_hp_bar() -> void:
	_hp_bar = Label3D.new()
	_hp_bar.text = ""
	_hp_bar.position = Vector3(0, Look.BODY_HEIGHT + 0.5, 0)
	_hp_bar.font_size = 10
	_hp_bar.modulate = Color(1.0, 0.3, 0.3)
	_hp_bar.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	_hp_bar.visible = false
	add_child(_hp_bar)
	health_changed.connect(_on_health_changed)

func _on_health_changed(current: float, maximum: float) -> void:
	if current >= maximum:
		_hp_bar.visible = false
		return
	_hp_bar.visible = true
	var pct := int(current / maximum * 100)
	_hp_bar.text = "%d%%" % pct
	# Flash red when low
	if current < maximum * 0.25:
		_hp_bar.modulate = Color(1.0, 0.1, 0.1)

func configure(id: String, decay: int = 0) -> void:
	archetype = id
	var data: Dictionary = Codex.enemy(id)
	# Region decay makes the same archetype meaner without new content.
	var scale := 1.0 + 0.12 * decay
	display_name = String(data["name"])
	max_health = float(data["hp"]) * scale
	max_poise = float(data["poise"])
	move_speed = float(data["speed"])
	damage = float(data["damage"]) * scale
	tell_time = maxf(0.14, float(data["tell"]) - 0.03 * decay)
	reach = float(data["reach"])
	aggro_range = float(data["aggro"])
	relics = int(data["relics"])
	posture = String(data["posture"])
	health = max_health
	poise = max_poise
	set_visual(_build_visual(data))

func _build_visual(data: Dictionary) -> Node3D:
	var color := Color(data["color"])
	match archetype:
		"husk":
			return Look.authored("ash_husk", 0.34)
		"stalker":
			return Look.authored("cinder_stalker", 0.42)
		"warden":
			return Look.authored("gravewarden", 0.34)
	match String(data["shape"]):
		"beast":
			var beast := Node3D.new()
			var body := MeshInstance3D.new()
			body.mesh = Look._organic_ellipsoid(Vector3(0.46, 0.30, 0.78), 32, 2.4)
			body.material_override = Look.standard(color)
			body.position = Vector3(0, 0.42, 0.18)
			beast.add_child(body)
			var head := MeshInstance3D.new()
			head.mesh = Look._organic_ellipsoid(Vector3(0.28, 0.25, 0.32), 28, 2.8)
			head.material_override = Look.standard(color.lightened(0.2))
			head.position = Vector3(0, 0.48, 0.86)
			beast.add_child(head)
			for side: int in [-1, 1]:
				var horn := MeshInstance3D.new()
				horn.mesh = Look._segment_mesh(Vector3(float(side) * 0.16, 0.63, 0.83), Vector3(float(side) * 0.24, 0.88, 0.98), 0.07, 0.015, 20)
				horn.material_override = Look.standard(color.darkened(0.28), 0.72)
				beast.add_child(horn)
			return beast
		_:
			var figure := Look.figure(color)
			figure.scale = Vector3.ONE * (float(data["size"]) / 16.0)
			return figure

func _physics_process(delta: float) -> void:
	if state == State.DEAD:
		super(delta)
		return
	# Boss phase 2: faster and stronger below 50% health
	if enemy_id == "ash_king" and hp < max_hp * 0.5 and not _phase2:
		_phase2 = true
		speed *= 1.3
		damage *= 1.2
		Chronicle.record("boss_phase2", "Ash King enters phase 2")
	_tick_tell(delta)
	_acquire_target()
	match state:
		State.IDLE:
			_think(delta)
		State.WINDUP:
			_brake(delta)
			if state_time_left() <= 0.0:
				enter_state(State.ACTIVE, 0.12)
				_strike()
		State.ACTIVE:
			if state_time_left() <= 0.0:
				enter_state(State.RECOVER, 0.32)
		State.RECOVER, State.STAGGER:
			_brake(delta)
			if state_time_left() <= 0.0:
				enter_state(State.IDLE, 0.0)
	super(delta)

func _brake(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0.0, 25.0 * delta)
	velocity.z = move_toward(velocity.z, 0.0, 25.0 * delta)

## The tell is the whole difficulty curve: the body rears and glows before it
## commits, and the glow is visible from any camera angle.
func _tick_tell(delta: float) -> void:
	if visual == null:
		return
	if state != State.WINDUP:
		_tell_phase = 0.0
		visual.rotation.x = lerp(visual.rotation.x, 0.0, 10.0 * delta)
		_set_tint(Color.WHITE)
		return
	_tell_phase += delta * 14.0
	var pulse := 0.5 + 0.5 * sin(_tell_phase)
	_set_tint(Color(1.0, 1.0, 1.0).lerp(Color(2.4, 1.1, 0.6), pulse))
	visual.rotation.x = lerp(visual.rotation.x, -0.35, 12.0 * delta)

func _acquire_target() -> void:
	# Check if nearby enemies have a target we should also target
	if _target == null:
		for node: Node in get_tree().get_nodes_in_group("enemies"):
			var other := node as EnemyActor
			if other == null or other == self or other._target == null:
				continue
			if global_position.distance_to(other.global_position) < 8.0:
				# Coordinate: target the same enemy as our neighbor
				if global_position.distance_to(other._target.global_position) <= aggro_range:
					_target = other._target
					return
	if _target != null and _target.is_alive():
		if global_position.distance_to(_target.global_position) > LOSE_AGGRO_DISTANCE:
			if not _was_provoked:
				spared.emit(self)
			_target = null
		return
	_target = null
	for node: Node in get_tree().get_nodes_in_group("combatants"):
		var other := node as Combatant
		if other == null or other.faction == faction or not other.is_alive():
			continue
		if global_position.distance_to(other.global_position) <= aggro_range:
			_target = other
			return

func _think(delta: float) -> void:
	if _target == null:
		_wander(delta)
		return
	# Guardian enemies use special heavy attack occasionally
	if posture == "guardian" and _target != null and randf() < 0.005:
		enter_state(State.WINDUP, tell * 2.0)
	# Fast enemies try to flank
	if posture == "darter" and _target != null:
		var to_target = _target.global_position - global_position
		to_target.y = 0.0
		var perp = Vector3(-to_target.z, 0.0, to_target.x).normalized()
		var flank_target = _target.global_position + perp * 2.0
		var to_flank = flank_target - global_position
		to_flank.y = 0.0
		facing = to_flank.normalized()
		velocity.x = facing.x * move_speed
		velocity.z = facing.z * move_speed
	# Ranged enemies keep distance
	if posture == "ranged" and _target != null and _target.global_position.distance_to(global_position) < reach * 0.6:
		var offset = global_position - _target.global_position
		offset.y = 0.0
		facing = offset.normalized()
		velocity.x = facing.x * move_speed
		velocity.z = facing.z * move_speed
	# Coordinate with nearby enemies
	if _target == null:
		var nearby = get_tree().get_nodes_in_group("enemies")
		for enemy in nearby:
			if enemy != self and enemy._target != null and global_position.distance_to(enemy.global_position) < 8.0:
				_target = enemy._target
				break
	# Retreat when low health
	if hp < max_hp * 0.3 and _target != null and _target.global_position.distance_to(global_position) < 3.0:
		var offset = global_position - _target.global_position
		offset.y = 0.0
		facing = offset.normalized()
		velocity.x = facing.x * move_speed
		velocity.z = facing.z * move_speed
	# Ranged enemies throw projectiles
	if posture == "ranged" and _target != null and _target.global_position.distance_to(global_position) > reach * 0.7 and randf() < 0.02:
		var offset = _target.global_position - global_position
		offset.y = 0.0
		facing = offset.normalized()
		# Throw a rock (represented as a fast melee attack)
		enter_state(State.WINDUP, tell_time * 0.5)
	# Berserker enemies charge at distance
	if posture == "darter" and _target != null and _target.global_position.distance_to(global_position) > 5.0 and randf() < 0.01:
		var offset = _target.global_position - global_position
		offset.y = 0.0
		facing = offset.normalized()
		velocity.x = facing.x * move_speed * 2.5
		velocity.z = facing.z * move_speed * 2.5
	# Healer enemies heal nearby allies when low
	if posture == "dancer" and hp < max_hp * 0.5:
		var nearby = get_tree().get_nodes_in_group("enemies")
		for enemy in nearby:
			if enemy != self and enemy.hp < enemy.max_hp * 0.5 and global_position.distance_to(enemy.global_position) < 8.0:
				enemy.hp = min(enemy.hp + 5.0, enemy.max_hp)
				break
	# Retreat when low on health
	if hp < max_hp * 0.3 and randf() < 0.02:
		var offset: Vector3 = global_position - _target.global_position
		offset.y = 0.0
		facing = offset.normalized()
		velocity.x = facing.x * move_speed * 0.8
		velocity.z = facing.z * move_speed * 0.8
		return
	var offset: Vector3 = _target.global_position - global_position
	offset.y = 0.0
	facing = offset.normalized()
	var distance := offset.length()
	# Ranged enemies keep distance
	if posture == "ranged" and distance < reach * 0.8:
		# Back away
		var retreat := -offset.normalized()
		velocity.x = move_toward(velocity.x, retreat.x * move_speed * 0.6, 20.0 * delta)
		velocity.z = move_toward(velocity.z, retreat.z * move_speed * 0.6, 20.0 * delta)
		return
	if distance <= reach:
		# Special attack: some enemies use heavy attacks occasionally
		if randf() < 0.15 and posture == "guardian":
			enter_state(State.WINDUP, tell_time * 1.5)
		else:
			enter_state(State.WINDUP, tell_time)
		return
	var approach := offset.normalized()
	# Flanking: some enemies circle to the side
	if posture == "dancer" and distance > reach * 1.5:
		approach = approach.rotated(Vector3.UP, sin(Time.get_ticks_msec() * 0.001) * 1.2)
	elif posture == "darter":
		# Stalkers circle before committing, so the player can read a rhythm.
		approach = approach.rotated(Vector3.UP, sin(Time.get_ticks_msec() * 0.002) * 0.8)
	elif posture == "bulwark" and distance < reach * 1.8:
		approach *= 0.4
	velocity.x = move_toward(velocity.x, approach.x * move_speed, 20.0 * delta)
	velocity.z = move_toward(velocity.z, approach.z * move_speed, 20.0 * delta)

func _wander(delta: float) -> void:
	_wander_timer -= delta
	if _wander_timer <= 0.0:
		_wander_timer = IDLE_WANDER_TIME + randf() * 2.0
		_wander_direction = Vector3.FORWARD.rotated(Vector3.UP, randf() * TAU) \
				if randf() < 0.65 else Vector3.ZERO
	if _wander_direction != Vector3.ZERO:
		facing = _wander_direction
	velocity.x = move_toward(velocity.x, _wander_direction.x * move_speed * 0.35, 12.0 * delta)
	velocity.z = move_toward(velocity.z, _wander_direction.z * move_speed * 0.35, 12.0 * delta)

func _strike() -> void:
	# Ranged enemies fire projectiles
	if posture == "ranged":
		_fire_projectile()
		return
	# Melee enemies swing
	swing(reach + 0.5, 1.5, {
		"damage": damage,
		"poise_damage": damage * 1.4,
		"knock_force": 5.0,
	})

func _fire_projectile() -> void:
	# Create a simple projectile
	var projectile := Area3D.new()
	projectile.position = position + Vector3(0, 1.0, 0)
	var shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = 0.2
	shape.shape = sphere
	projectile.add_child(shape)
	# Visual
	var mesh := MeshInstance3D.new()
	var ball := SphereMesh.new()
	ball.radius = 0.15
	ball.height = 0.3
	mesh.mesh = ball
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(1.0, 0.6, 0.2)
	mat.emission_enabled = true
	mat.emission = Color(1.0, 0.6, 0.2)
	mesh.material_override = mat
	projectile.add_child(mesh)
	# Move projectile toward target
	var direction := Vector3(0)
	if _target != null:
		direction = (_target.position - position).normalized()
	projectile.linear_velocity = direction * 10.0
	get_tree().root.add_child(projectile)

func take_hit(info: Dictionary) -> bool:
	_was_provoked = true
	var attacker := info.get("attacker") as Combatant
	if attacker != null:
		_target = attacker
	# Fast enemies dodge occasionally
	if posture == "darter" and randf() < 0.2:
		var dodge_dir = Vector3(randf_range(-1, 1), 0.0, randf_range(-1, 1)).normalized()
		global_position += dodge_dir * 1.5
	# Heavy attacks stagger enemies
	if info.get("heavy", false) and state != State.STAGGER:
		enter_state(State.STAGGER, 0.5)
	# Guardian enemies block with shield
	if posture == "guardian" and randf() < 0.25:
		info["damage"] *= 0.5
		# Call for help: alert nearby enemies
		if randf() < 0.1:
			var nearby = get_tree().get_nodes_in_group("enemies")
			for enemy in nearby:
				if enemy != self and global_position.distance_to(enemy.global_position) < 12.0:
					enemy._target = attacker
	# Fast enemies dodge occasionally
	if posture == "darter" and randf() < 0.15:
		# Dodge: move sideways
		var dodge_dir = facing.rotated(Vector3.UP, PI * 0.5)
		velocity.x = dodge_dir.x * move_speed * 2.0
		velocity.z = dodge_dir.z * move_speed * 2.0
		return false
	# Heavy attacks stagger enemies
	if info.get("heavy", false) and state != State.STAGGER:
		enter_state(State.STAGGER, 0.5)
	return super(info)

func die() -> void:
	if state == State.DEAD:
		return
	slain.emit(self)
	super()
	if get_tree().root.has_node("AudioManager"):
		get_tree().root.get_node("AudioManager").play_death()
	# Drop loot
	if randf() < drop_chance:
		var loot := 1 + int(randf() * 3)
		WorldState.materials["timber"] = int(WorldState.materials.get("timber", 0)) + loot
		Chronicle.record("enemy_loot", "%s dropped %d timber" % [display_name, loot])
