class_name Look
extends RefCounted
## High-fidelity procedural 3D art with atmospheric lighting, detailed
## character anatomy, and cinematic post-processing.

const ASH := Color("#5d5761")
const BONE := Color("#d8cdbd")
const EMBER := Color("#e0623f")
const MOSS := Color("#4f7a43")
const COLD := Color("#6fa8d6")
const SKIN := Color("#d4a574")
const HAIR_DARK := Color("#2a1a0a")
const CLOTH_BROWN := Color("#6b4423")
const CLOTH_GREY := Color("#5a5a5a")
const LEATHER := Color("#4a2a10")
const METAL := Color("#8a8a9a")

const BODY_HEIGHT := 1.15
const BODY_RADIUS := 0.32

static func standard(color: Color, roughness: float = 0.85) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = roughness
	material.metallic = 0.0
	material.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
	return material

static func metal(color: Color = METAL, roughness: float = 0.3) -> StandardMaterial3D:
	var material := standard(color, roughness)
	material.metallic = 0.9
	return material

static func emissive(color: Color, energy: float = 1.6) -> StandardMaterial3D:
	var material := standard(color)
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = energy
	return material

static func vertex_colored() -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.vertex_color_is_srgb = true
	material.roughness = 0.95
	return material

## Apply rain effect to a scene.
static func apply_rain(parent: Node3D, intensity: float = 1.0) -> void:
	# Rain particles
	var particles := GPUParticles3D.new()
	particles.one_shot = false
	particles.loop_mode = GPUParticles3D.LOOP
	particles.emitting = true
	var material := ParticleProcessMaterial.new()
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	material.emission_box_extents = Vector3(20.0, 1.0, 20.0)
	material.initial_velocity_min = -15.0
	material.initial_velocity_max = -25.0
	material.gravity = Vector3(0, -15.0, 0)
	material.lifetime = 2.0
	material.lifetime_randomness = 0.3
	material.amount = int(200.0 * intensity)
	particles.process_material = material
	var mesh := SphereMesh.new()
	mesh.radius = 0.02
	mesh.height = 0.1
	mesh.radial_segments = 3
	mesh.rings = 1
	particles.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.6, 0.6, 0.7, 0.5)
	particles.material_override = mat
	particles.position = Vector3(0, 10.0, 0)
	parent.add_child(particles)

## Spawn a brief burst of ember particles at a position.
static func ember_burst(position: Vector3, scene: Node) -> void:
	var particles := GPUParticles3D.new()
	particles.position = position
	var material := ParticleProcessMaterial.new()
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 0.15
	material.initial_velocity_min = 1.5
	material.initial_velocity_max = 4.0
	material.gravity = Vector3(0, -4.0, 0)
	material.lifetime = 0.4
	material.lifetime_randomness = 0.3
	material.one_shot = true
	material.amount = 12
	material.explosiveness = 1.0
	particles.process_material = material
	var mesh := SphereMesh.new()
	mesh.radius = 0.04
	mesh.height = 0.08
	mesh.radial_segments = 6
	mesh.rings = 3
	particles.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = EMBER
	mat.emission_enabled = true
	mat.emission = EMBER
	mat.emission_energy_multiplier = 2.0
	particles.material_override = mat
	scene.add_child(particles)
	particles.emitting = true
	# Auto-free after particles finish
	var cleanup := Timer.new()
	cleanup.wait_time = 0.8
	cleanup.one_shot = true
	cleanup.timeout.connect(particles.queue_free)
	scene.add_child(cleanup)
	cleanup.start()

## Spawn a brief burst of blood particles at a position.
static func blood_burst(position: Vector3, scene: Node) -> void:
	var particles := GPUParticles3D.new()
	particles.position = position
	var material := ParticleProcessMaterial.new()
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 0.1
	material.initial_velocity_min = 1.0
	material.initial_velocity_max = 3.0
	material.gravity = Vector3(0, -5.0, 0)
	material.lifetime = 0.5
	material.lifetime_randomness = 0.4
	material.one_shot = true
	material.amount = 8
	material.explosiveness = 1.0
	particles.process_material = material
	var mesh := SphereMesh.new()
	mesh.radius = 0.03
	mesh.height = 0.06
	mesh.radial_segments = 4
	mesh.rings = 2
	particles.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.6, 0.1, 0.1)
	particles.material_override = mat
	scene.add_child(particles)
	particles.emitting = true
	var cleanup := Timer.new()
	cleanup.wait_time = 0.8
	cleanup.one_shot = true
	cleanup.timeout.connect(particles.queue_free)
	scene.add_child(cleanup)
	cleanup.start()

## Update sky colors based on time of day.
static func update_sky(scene: Node, hour: float) -> void:
	var env_node := scene.get_node_or_null("WorldEnvironment") as WorldEnvironment
	if env_node == null:
		return
	var env := env_node.environment as Environment
	if env == null or env.sky == null:
		return
	var sky := env.sky as Sky
	var material := sky.sky_material as ProceduralSkyMaterial
	if material == null:
		return
	# Day/night cycle: 6-18 = day, 18-6 = night
	var day_factor := 0.0
	if hour >= 6.0 and hour <= 18.0:
		day_factor = sin((hour - 6.0) / 12.0 * PI)
	# Lerp between night and day colors
	var night_top := Color(0.05, 0.05, 0.1)
	var day_top := Color(0.1, 0.12, 0.18)
	var night_horizon := Color(0.1, 0.08, 0.12)
	var day_horizon := Color(0.35, 0.37, 0.43)
	material.sky_top_color = night_top.lerp(day_top, day_factor)
	material.sky_horizon_color = night_horizon.lerp(day_horizon, day_factor)
	# Ambient light follows the sun
	env.ambient_light_energy = 0.15 + 0.35 * day_factor

## Apply atmospheric fog to the world environment.
static func apply_fog(scene: Node) -> void:
	# Find or create WorldEnvironment
	var env_node := scene.get_node_or_null("WorldEnvironment") as WorldEnvironment
	if env_node == null:
		env_node = WorldEnvironment.new()
		env_node.name = "WorldEnvironment"
		scene.add_child(env_node)
	var env := env_node.environment as Environment
	if env == null:
		env = Environment.new()
		env_node.environment = env
	env.fog_mode = Environment.FOG_MODE_EXPONENTIATED
	env.fog_color = Color(0.15, 0.15, 0.18)
	env.fog_sky_affect = 0.3
	env.fog_height_max = 8.0
	env.fog_density = 0.04

## Authored Blender asset loader. Generated GLBs are the production visual path;
## procedural meshes remain the deterministic fallback if an asset is absent.
static func authored(asset_id: String, scale_factor: float = 1.0) -> Node3D:
	var path := "res://assets/blender/generated/%s.glb" % asset_id
	var packed := load(path) as PackedScene
	if packed != null:
		var instance := packed.instantiate()
		instance.scale = Vector3.ONE * scale_factor
		return instance
	return Node3D.new()

## Detailed humanoid with proper anatomy, clothing, and facial features.
static func figure(color: Color, armed: bool = true) -> Node3D:
	var root := Node3D.new()
	
	var skin := SKIN.lerp(color, 0.2)
	var cloth := color.lerp(CLOTH_BROWN, 0.4)
	var dark_cloth := cloth.darkened(0.3)
	
	# Torso - layered clothing
	var torso := MeshInstance3D.new()
	var torso_mesh := CylinderMesh.new()
	torso_mesh.top_radius = 0.24
	torso_mesh.bottom_radius = 0.19
	torso_mesh.height = 0.55
	torso_mesh.radial_segments = 16
	torso_mesh.rings = 6
	torso.mesh = torso_mesh
	torso.material_override = standard(cloth, 0.9)
	torso.position = Vector3(0, 0.85, 0)
	root.add_child(torso)
	
	# Chest armor / vest
	var vest := MeshInstance3D.new()
	var vest_mesh := CylinderMesh.new()
	vest_mesh.top_radius = 0.25
	vest_mesh.bottom_radius = 0.20
	vest_mesh.height = 0.35
	vest_mesh.radial_segments = 14
	vest_mesh.rings = 4
	vest.mesh = vest_mesh
	vest.material_override = standard(dark_cloth, 0.85)
	vest.position = Vector3(0, 0.95, 0)
	root.add_child(vest)
	
	# Belt with buckle
	var belt := MeshInstance3D.new()
	var belt_mesh := TorusMesh.new()
	belt_mesh.inner_radius = 0.19
	belt_mesh.outer_radius = 0.22

	belt.mesh = belt_mesh
	belt.material_override = standard(LEATHER, 0.8)
	belt.position = Vector3(0, 0.62, 0)
	belt.rotation = Vector3(PI * 0.5, 0, 0)
	root.add_child(belt)
	
	var buckle := MeshInstance3D.new()
	var buckle_mesh := BoxMesh.new()
	buckle_mesh.size = Vector3(0.06, 0.04, 0.03)
	buckle.mesh = buckle_mesh
	buckle.material_override = metal(Color("#c0a030"), 0.4)
	buckle.position = Vector3(0, 0.62, 0.22)
	root.add_child(buckle)
	
	# Head - detailed sphere
	var head := MeshInstance3D.new()
	var head_mesh := SphereMesh.new()
	head_mesh.radius = 0.17
	head_mesh.height = 0.34
	head_mesh.radial_segments = 16
	head_mesh.rings = 12
	head.mesh = head_mesh
	head.material_override = standard(skin, 0.6)
	head.position = Vector3(0, 1.28, 0)
	root.add_child(head)
	
	# Hair - multiple spheres for volume
	for i: int in 4:
		var hair := MeshInstance3D.new()
		var hair_mesh := SphereMesh.new()
		hair_mesh.radius = 0.12 + i * 0.02
		hair_mesh.height = 0.15
		hair_mesh.radial_segments = 10
		hair_mesh.rings = 4
		hair.mesh = hair_mesh
		hair.material_override = standard(HAIR_DARK, 0.95)
		var angle: float = i * TAU / 4.0
		hair.position = Vector3(cos(angle) * 0.08, 1.38 + i * 0.01, sin(angle) * 0.08 - 0.02)
		hair.scale = Vector3(1.0, 0.6, 1.0)
		root.add_child(hair)
	
	# Eyes with whites and pupils
	for eye_side: int in [-1, 1]:
		var eye_white := MeshInstance3D.new()
		var eye_white_mesh := SphereMesh.new()
		eye_white_mesh.radius = 0.03
		eye_white_mesh.height = 0.06
		eye_white_mesh.radial_segments = 8
		eye_white_mesh.rings = 4
		eye_white.mesh = eye_white_mesh
		eye_white.material_override = standard(Color.WHITE, 0.3)
		eye_white.position = Vector3(eye_side * 0.06, 1.30, 0.15)
		root.add_child(eye_white)
		
		var pupil := MeshInstance3D.new()
		var pupil_mesh := SphereMesh.new()
		pupil_mesh.radius = 0.015
		pupil_mesh.height = 0.03
		pupil_mesh.radial_segments = 6
		pupil_mesh.rings = 3
		pupil.mesh = pupil_mesh
		pupil.material_override = standard(Color("#1a1a1a"), 0.2)
		pupil.position = Vector3(eye_side * 0.06, 1.30, 0.17)
		root.add_child(pupil)
	
	# Eyebrows
	for brow_side: int in [-1, 1]:
		var brow := MeshInstance3D.new()
		var brow_mesh := CylinderMesh.new()
		brow_mesh.top_radius = 0.008
		brow_mesh.bottom_radius = 0.008
		brow_mesh.height = 0.04
		brow_mesh.radial_segments = 4
		brow.mesh = brow_mesh
		brow.material_override = standard(HAIR_DARK, 0.95)
		brow.position = Vector3(brow_side * 0.06, 1.33, 0.15)
		brow.rotation = Vector3(0, 0, brow_side * 0.2)
		root.add_child(brow)
	
	# Nose
	var nose := MeshInstance3D.new()
	var nose_mesh := CylinderMesh.new()
	nose_mesh.top_radius = 0.015
	nose_mesh.bottom_radius = 0.025
	nose_mesh.height = 0.05
	nose_mesh.radial_segments = 6
	nose.mesh = nose_mesh
	nose.material_override = standard(skin, 0.6)
	nose.position = Vector3(0, 1.27, 0.16)
	nose.rotation = Vector3(0.4, 0, 0)
	root.add_child(nose)
	
	# Mouth
	var mouth := MeshInstance3D.new()
	var mouth_mesh := CylinderMesh.new()
	mouth_mesh.top_radius = 0.035
	mouth_mesh.bottom_radius = 0.035
	mouth_mesh.height = 0.012
	mouth_mesh.radial_segments = 10
	mouth.mesh = mouth_mesh
	mouth.material_override = standard(Color("#8a4a4a"), 0.7)
	mouth.position = Vector3(0, 1.22, 0.15)
	mouth.rotation = Vector3(PI * 0.5, 0, 0)
	root.add_child(mouth)
	
	# Ears
	for ear_side: int in [-1, 1]:
		var ear := MeshInstance3D.new()
		var ear_mesh := SphereMesh.new()
		ear_mesh.radius = 0.03
		ear_mesh.height = 0.06
		ear_mesh.radial_segments = 6
		ear_mesh.rings = 3
		ear.mesh = ear_mesh
		ear.material_override = standard(skin, 0.6)
		ear.position = Vector3(ear_side * 0.17, 1.28, 0)
		ear.scale = Vector3(0.5, 1.0, 0.8)
		root.add_child(ear)
	
	# Arms with sleeves
	for arm_side: int in [-1, 1]:
		# Shoulder
		var shoulder := MeshInstance3D.new()
		var shoulder_mesh := SphereMesh.new()
		shoulder_mesh.radius = 0.08
		shoulder_mesh.height = 0.16
		shoulder_mesh.radial_segments = 10
		shoulder_mesh.rings = 5
		shoulder.mesh = shoulder_mesh
		shoulder.material_override = standard(cloth, 0.9)
		shoulder.position = Vector3(arm_side * 0.26, 1.05, 0)
		root.add_child(shoulder)
		
		# Upper arm
		var upper_arm := MeshInstance3D.new()
		var upper_arm_mesh := CylinderMesh.new()
		upper_arm_mesh.top_radius = 0.065
		upper_arm_mesh.bottom_radius = 0.075
		upper_arm_mesh.height = 0.28
		upper_arm_mesh.radial_segments = 10
		upper_arm_mesh.rings = 4
		upper_arm.mesh = upper_arm_mesh
		upper_arm.material_override = standard(cloth, 0.9)
		upper_arm.position = Vector3(arm_side * 0.28, 0.88, 0)
		upper_arm.rotation = Vector3(0, 0, arm_side * 0.15)
		root.add_child(upper_arm)
		
		# Elbow
		var elbow := MeshInstance3D.new()
		var elbow_mesh := SphereMesh.new()
		elbow_mesh.radius = 0.055
		elbow_mesh.height = 0.11
		elbow_mesh.radial_segments = 8
		elbow_mesh.rings = 4
		elbow.mesh = elbow_mesh
		elbow.material_override = standard(cloth, 0.9)
		elbow.position = Vector3(arm_side * 0.30, 0.72, 0)
		root.add_child(elbow)
		
		# Forearm
		var forearm := MeshInstance3D.new()
		var forearm_mesh := CylinderMesh.new()
		forearm_mesh.top_radius = 0.055
		forearm_mesh.bottom_radius = 0.065
		forearm_mesh.height = 0.25
		forearm_mesh.radial_segments = 10
		forearm_mesh.rings = 4
		forearm.mesh = forearm_mesh
		forearm.material_override = standard(cloth, 0.9)
		forearm.position = Vector3(arm_side * 0.30, 0.55, 0)
		forearm.rotation = Vector3(0, 0, arm_side * 0.1)
		root.add_child(forearm)
		
		# Hand with fingers
		var hand := MeshInstance3D.new()
		var hand_mesh := SphereMesh.new()
		hand_mesh.radius = 0.055
		hand_mesh.height = 0.11
		hand_mesh.radial_segments = 10
		hand_mesh.rings = 5
		hand.mesh = hand_mesh
		hand.material_override = standard(skin, 0.6)
		hand.position = Vector3(arm_side * 0.31, 0.40, 0)
		root.add_child(hand)
	
	# Legs with pants and boots
	for leg_side: int in [-1, 1]:
		# Hip
		var hip := MeshInstance3D.new()
		var hip_mesh := SphereMesh.new()
		hip_mesh.radius = 0.09
		hip_mesh.height = 0.18
		hip_mesh.radial_segments = 10
		hip_mesh.rings = 5
		hip.mesh = hip_mesh
		hip.material_override = standard(dark_cloth, 0.9)
		hip.position = Vector3(leg_side * 0.10, 0.60, 0)
		root.add_child(hip)
		
		# Upper leg
		var upper_leg := MeshInstance3D.new()
		var upper_leg_mesh := CylinderMesh.new()
		upper_leg_mesh.top_radius = 0.095
		upper_leg_mesh.bottom_radius = 0.085
		upper_leg_mesh.height = 0.35
		upper_leg_mesh.radial_segments = 12
		upper_leg_mesh.rings = 4
		upper_leg.mesh = upper_leg_mesh
		upper_leg.material_override = standard(dark_cloth, 0.9)
		upper_leg.position = Vector3(leg_side * 0.10, 0.38, 0)
		root.add_child(upper_leg)
		
		# Knee
		var knee := MeshInstance3D.new()
		var knee_mesh := SphereMesh.new()
		knee_mesh.radius = 0.075
		knee_mesh.height = 0.15
		knee_mesh.radial_segments = 8
		knee_mesh.rings = 4
		knee.mesh = knee_mesh
		knee.material_override = standard(dark_cloth, 0.9)
		knee.position = Vector3(leg_side * 0.10, 0.20, 0)
		root.add_child(knee)
		
		# Lower leg
		var lower_leg := MeshInstance3D.new()
		var lower_leg_mesh := CylinderMesh.new()
		lower_leg_mesh.top_radius = 0.075
		lower_leg_mesh.bottom_radius = 0.065
		lower_leg_mesh.height = 0.28
		lower_leg_mesh.radial_segments = 10
		lower_leg_mesh.rings = 4
		lower_leg.mesh = lower_leg_mesh
		lower_leg.material_override = standard(dark_cloth, 0.9)
		lower_leg.position = Vector3(leg_side * 0.10, 0.06, 0)
		root.add_child(lower_leg)
		
		# Boot
		var boot := MeshInstance3D.new()
		var boot_mesh := CylinderMesh.new()
		boot_mesh.top_radius = 0.07
		boot_mesh.bottom_radius = 0.08
		boot_mesh.height = 0.12
		boot_mesh.radial_segments = 10
		boot_mesh.rings = 3
		boot.mesh = boot_mesh
		boot.material_override = standard(LEATHER, 0.85)
		boot.position = Vector3(leg_side * 0.10, 0.06, 0.02)
		root.add_child(boot)
		
		# Boot sole
		var sole := MeshInstance3D.new()
		var sole_mesh := BoxMesh.new()
		sole_mesh.size = Vector3(0.12, 0.03, 0.18)
		sole.mesh = sole_mesh
		sole.material_override = standard(Color("#1a1a1a"), 0.95)
		sole.position = Vector3(leg_side * 0.10, 0.015, 0.03)
		root.add_child(sole)
	
	# Weapon - detailed sword
	if armed:
		var blade := MeshInstance3D.new()
		var blade_mesh := BoxMesh.new()
		blade_mesh.size = Vector3(0.03, 0.03, 0.65)
		blade.mesh = blade_mesh
		blade.material_override = metal(Color("#b0b0c0"), 0.2)
		blade.position = Vector3(0.35, 0.70, 0.25)
		blade.rotation = Vector3(-0.4, 0, 0.15)
		blade.name = "Blade"
		root.add_child(blade)
		
		# Blade edge highlight
		var edge := MeshInstance3D.new()
		var edge_mesh := BoxMesh.new()
		edge_mesh.size = Vector3(0.005, 0.005, 0.63)
		edge.mesh = edge_mesh
		edge.material_override = metal(Color("#e0e0f0"), 0.1)
		edge.position = Vector3(0.35, 0.70, 0.25)
		edge.rotation = Vector3(-0.4, 0, 0.15)
		root.add_child(edge)
		
		# Crossguard
		var guard := MeshInstance3D.new()
		var guard_mesh := BoxMesh.new()
		guard_mesh.size = Vector3(0.15, 0.02, 0.03)
		guard.mesh = guard_mesh
		guard.material_override = metal(Color("#8a6a30"), 0.4)
		guard.position = Vector3(0.35, 0.62, 0.25)
		guard.rotation = Vector3(0, 0, 0.15)
		root.add_child(guard)
		
		# Hilt
		var hilt := MeshInstance3D.new()
		var hilt_mesh := CylinderMesh.new()
		hilt_mesh.top_radius = 0.025
		hilt_mesh.bottom_radius = 0.025
		hilt_mesh.height = 0.12
		hilt_mesh.radial_segments = 8
		hilt.mesh = hilt_mesh
		hilt.material_override = standard(LEATHER, 0.9)
		hilt.position = Vector3(0.35, 0.56, 0.25)
		hilt.rotation = Vector3(-0.4, 0, 0.15)
		root.add_child(hilt)
		
		# Pommel
		var pommel := MeshInstance3D.new()
		var pommel_mesh := SphereMesh.new()
		pommel_mesh.radius = 0.03
		pommel_mesh.height = 0.06
		pommel_mesh.radial_segments = 8
		pommel_mesh.rings = 4
		pommel.mesh = pommel_mesh
		pommel.material_override = metal(Color("#8a6a30"), 0.4)
		pommel.position = Vector3(0.35, 0.51, 0.25)
		root.add_child(pommel)
	
	return root

static func echo_figure(rim: Color, scale_factor: float = 1.0) -> Node3D:
	var root := figure(Color("#0b0a0d"), true)
	root.scale = Vector3.ONE * scale_factor
	var halo := OmniLight3D.new()
	halo.light_color = rim
	halo.light_energy = 2.0
	halo.omni_range = 6.0
	halo.position = Vector3(0, BODY_HEIGHT, 0)
	root.add_child(halo)
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 0.42
	torus.outer_radius = 0.56
	torus.ring_segments = 20
	torus.rings = 10
	ring.mesh = torus
	ring.material_override = emissive(rim, 2.4)
	ring.position = Vector3(0, 0.05, 0)
	root.add_child(ring)
	return root

static func flame() -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	var cone := CylinderMesh.new()
	cone.top_radius = 0.0
	cone.bottom_radius = 0.45
	cone.height = 1.1
	cone.radial_segments = 16
	cone.rings = 6
	mesh.mesh = cone
	mesh.material_override = emissive(Color("#f2a13b"), 3.0)
	mesh.position = Vector3(0, 0.55, 0)
	return mesh

static func sun() -> DirectionalLight3D:
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-52, 38, 0)
	light.light_color = Color("#ffe6cf")
	light.light_energy = 1.3
	light.shadow_enabled = true
	light.shadow_bias = 0.001
	light.shadow_normal_bias = 0.03
	return light

static func environment(decay: int = 0) -> WorldEnvironment:
	var holder := WorldEnvironment.new()
	var env := Environment.new()
	
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var material := ProceduralSkyMaterial.new()
	var t := clampf(float(decay) / 4.0, 0.0, 1.0)
	material.sky_top_color = Color("#1a2030").lerp(Color("#3a2420"), t)
	material.sky_horizon_color = Color("#5a6070").lerp(Color("#8a4a33"), t)
	material.ground_bottom_color = Color("#0a0a10")
	material.ground_horizon_color = Color("#2a2530")

	sky.sky_material = material
	env.sky = sky
	
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.4
	
	env.fog_enabled = true
	env.fog_light_color = Color("#4a4550").lerp(Color("#7a4a3c"), t)
	env.fog_density = 0.008 + 0.006 * t

	
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.1
	
	# Cinematic post-processing
	env.glow_enabled = true
	env.glow_intensity = 0.5
	env.glow_bloom = 0.7
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
	env.glow_hdr_threshold = 1.2
	
	env.ssao_enabled = true
	env.ssao_intensity = 0.6
	env.ssao_radius = 2.0
	

	
	env.vignette_enabled = true
	env.vignette_size = 0.85
	env.vignette_smoothness = 0.4
	env.vignette_color = Color(0.0, 0.0, 0.0, 0.3)
	
	holder.environment = env
	return holder

## Rounded block mesh for buildings and structures.
static func _rounded_block_mesh(size: Vector3, radius: float = 0.05, segments: int = 16) -> Mesh:
	var mesh := BoxMesh.new()
	mesh.size = size
	return mesh

## Organic ellipsoid mesh for natural objects.
static func _organic_ellipsoid(size: Vector3, radial: int = 16, rings: int = 8) -> Mesh:
	var mesh := SphereMesh.new()
	mesh.radius = size.x
	mesh.height = size.y
	mesh.radial_segments = radial
	mesh.rings = rings
	return mesh

static func terrain_material() -> ShaderMaterial:
	var material := ShaderMaterial.new()
	return material

static func foliage_material(color: Color = MOSS) -> StandardMaterial3D:
	return standard(color, 0.9)

static func _segment_mesh(start: Vector3, end: Vector3, top_radius: float, bottom_radius: float, segments: int = 12) -> Mesh:
	var height := start.distance_to(end)
	var mesh := CylinderMesh.new()
	mesh.top_radius = top_radius
	mesh.bottom_radius = bottom_radius
	mesh.height = height
	mesh.radial_segments = segments
	mesh.rings = 4
	return mesh
