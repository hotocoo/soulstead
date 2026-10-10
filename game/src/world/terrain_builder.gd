class_name TerrainBuilder
extends RefCounted
## Turns a tile grid into a high-detail 3D terrain mesh with smooth
## heightmap interpolation, procedural texturing, and proper PBR materials.
##
## Each tile is subdivided into a high-resolution grid for smooth rolling
## terrain. Vertex colors are blended between neighboring tiles for natural
## transitions. Normal mapping is computed from the heightfield.

const TILE := Terrain.TILE_SIZE
const SUBDIVISION := 16
const VERTEX_COUNT := SUBDIVISION + 1

static func build(data: Dictionary, parent: Node3D) -> MeshInstance3D:
	var mesh_instance := MeshInstance3D.new()
	mesh_instance.mesh = _surface(data)
	var material := _terrain_material()
	mesh_instance.material_override = material
	parent.add_child(mesh_instance)
	# Continuous substrate guarantees no visual voids between procedural terrain
	# cells and keeps the world readable even at steep camera angles.
	var substrate := MeshInstance3D.new()
	var substrate_mesh := PlaneMesh.new()
	substrate_mesh.size = Vector2(float(data["width"]) * TILE, float(data["height"]) * TILE)
	substrate.mesh = substrate_mesh
	substrate.material_override = Look.standard(Terrain.color(Terrain.GRASS).darkened(0.08), 0.98)
	substrate.position = Vector3(float(data["width"]) * TILE * 0.5, -1.0, float(data["height"]) * TILE * 0.5)
	parent.add_child(substrate)
	_collision(data, parent)
	_scatter_water(data, parent)
	_scatter_trees(data, parent)
	_scatter_rocks(data, parent)
	_scatter_grass(data, parent)
	return mesh_instance

static func _terrain_material() -> ShaderMaterial:
	return Look.terrain_material()

static func _surface(data: Dictionary) -> ArrayMesh:
	var width: int = data["width"]
	var height: int = data["height"]
	var tiles: PackedByteArray = data["tiles"]
	var tool := SurfaceTool.new()
	tool.begin(Mesh.PRIMITIVE_TRIANGLES)
	var grid_width := width * SUBDIVISION + 1
	var grid_height := height * SUBDIVISION + 1
	for gz: int in grid_height:
		for gx: int in grid_width:
			var tile_x := mini(int(gx / SUBDIVISION), width - 1)
			var tile_z := mini(int(gz / SUBDIVISION), height - 1)
			var local_x := float(gx % SUBDIVISION) / float(SUBDIVISION)
			var local_z := float(gz % SUBDIVISION) / float(SUBDIVISION)
			if gx == width * SUBDIVISION:
				tile_x = width - 1
				local_x = 1.0
			if gz == height * SUBDIVISION:
				tile_z = height - 1
				local_z = 1.0
			var tile: int = tiles[tile_z * width + tile_x]
			var h: float = _smooth_height(data, tile_x, tile_z, local_x, local_z, tile, Terrain.height(tile))
			var color := _blended_color(data, tile_x, tile_z, local_x, local_z, tile, Terrain.color(tile))
			tool.set_color(color)
			tool.set_uv(Vector2(float(gx) / float(grid_width - 1), float(gz) / float(grid_height - 1)))
			tool.add_vertex(Vector3(float(gx) * TILE / SUBDIVISION, h, float(gz) * TILE / SUBDIVISION))

	for gz: int in height * SUBDIVISION:
		for gx: int in width * SUBDIVISION:
			var a: int = gz * grid_width + gx
			var b: int = a + 1
			var c: int = a + grid_width
			var d: int = c + 1
			tool.add_index(a)
			tool.add_index(c)
			tool.add_index(b)
			tool.add_index(b)
			tool.add_index(c)
			tool.add_index(d)
	
	tool.generate_normals()
	tool.generate_tangents()
	var mesh := tool.commit()
	mesh.surface_set_material(0, null)
	return mesh

static func _smooth_height(data: Dictionary, x: int, z: int, lx: float, lz: float,
		tile: int, base_h: float) -> float:
	var h1: float = _height_at(data, x, z)
	var h2: float = _height_at(data, x + 1, z)
	var h3: float = _height_at(data, x, z + 1)
	var h4: float = _height_at(data, x + 1, z + 1)
	
	var top: float = lerp(h1, h2, lx)
	var bottom: float = lerp(h3, h4, lx)
	var h: float = lerp(top, bottom, lz)
	# Bilinear tile heights remain the macro shape; a low-amplitude smooth
	# curvature removes the visibly tiled planar look without adding noisy ridges.
	var curve := sin((float(x) + lx) * 0.7) * cos((float(z) + lz) * 0.55) * 0.045
	return h + curve

static func _blended_color(data: Dictionary, x: int, z: int, lx: float, lz: float,
		tile: int, base_color: Color) -> Color:
	var c1: Color = Terrain.color(_tile_at(data, x, z))
	var c2: Color = Terrain.color(_tile_at(data, x + 1, z))
	var c3: Color = Terrain.color(_tile_at(data, x, z + 1))
	var c4: Color = Terrain.color(_tile_at(data, x + 1, z + 1))
	
	var top: Color = c1.lerp(c2, lx)
	var bottom: Color = c3.lerp(c4, lx)
	return top.lerp(bottom, lz)

static func _compute_normal(data: Dictionary, x: int, z: int, lx: float, lz: float) -> Vector3:
	var eps: float = 0.05
	var h0: float = _smooth_height(data, x, z, lx, lz, 0, 0.0)
	var h1: float = _smooth_height(data, x, z, lx + eps, lz, 0, 0.0)
	var h2: float = _smooth_height(data, x, z, lx, lz + eps, 0, 0.0)
	
	var dx: float = (h1 - h0) / eps
	var dz: float = (h2 - h0) / eps
	var normal := Vector3(-dx, 1.0, -dz).normalized()
	return normal

static func _height_at(data: Dictionary, x: int, z: int) -> float:
	var width: int = data["width"]
	var height: int = data["height"]
	if x < 0 or z < 0 or x >= width or z >= height:
		return -2.0
	var tiles: PackedByteArray = data["tiles"]
	return Terrain.height(tiles[z * width + x])

static func _tile_at(data: Dictionary, x: int, z: int) -> int:
	var width: int = data["width"]
	var height: int = data["height"]
	if x < 0 or z < 0 or x >= width or z >= height:
		return Terrain.WATER
	var tiles: PackedByteArray = data["tiles"]
	return tiles[z * width + x]

# --- Collision -----------------------------------------------------------

static func _collision(data: Dictionary, parent: Node3D) -> void:
	var body := StaticBody3D.new()
	body.name = "TerrainCollision"
	parent.add_child(body)
	var width: int = data["width"]
	var height: int = data["height"]
	var tiles: PackedByteArray = data["tiles"]
	
	var floor_shape := CollisionShape3D.new()
	var floor_box := BoxShape3D.new()
	floor_box.size = Vector3(width * TILE, 1.0, height * TILE)
	floor_shape.shape = floor_box
	floor_shape.position = Vector3(width * TILE * 0.5, -0.5, height * TILE * 0.5)
	body.add_child(floor_shape)
	
	for z: int in height:
		var run_start := -1
		for x: int in width + 1:
			var blocking: bool = x < width and Terrain.is_blocking(tiles[z * width + x])
			if blocking and run_start < 0:
				run_start = x
			elif not blocking and run_start >= 0:
				_add_wall(body, run_start, x, z)
				run_start = -1

static func _add_wall(body: StaticBody3D, from_x: int, to_x: int, z: int) -> void:
	var span: int = to_x - from_x
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(span * TILE, 4.0, TILE)
	shape.shape = box
	shape.position = Vector3((from_x + span * 0.5) * TILE, 1.6, (z + 0.5) * TILE)
	body.add_child(shape)

# --- Decoration ----------------------------------------------------------

static func _scatter_trees(data: Dictionary, parent: Node3D) -> void:
	var width: int = data["width"]
	var height: int = data["height"]
	var tiles: PackedByteArray = data["tiles"]
	var positions: Array[Vector3] = []
	
	for z: int in height:
		for x: int in width:
			if tiles[z * width + x] == Terrain.TREE:
				var jitter := Vector3(sin(x * 12.9898 + z * 78.233) * 0.4, 0.0,
					cos(x * 78.233 + z * 12.9898) * 0.4)
				positions.append(Terrain.to_world(Vector2i(x, z)) + jitter)
	
	if positions.is_empty():
		return
	
	for i: int in positions.size():
		var tree := _build_tree(i)
		tree.position = positions[i]
		parent.add_child(tree)

static func _build_tree(seed: int) -> Node3D:
	var tree := Node3D.new()
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	
	var trunk_color := Color("#33251d")
	var leaf_color := Terrain.color(Terrain.TREE)
	var foliage_mat := Look.foliage_material(leaf_color.lerp(Color("#587647"), 0.28))
	
	var trunk := MeshInstance3D.new()
	var trunk_height := 3.6 + rng.randf() * 1.8
	var lean := Vector3(rng.randf_range(-0.10, 0.10), trunk_height, rng.randf_range(-0.10, 0.10))
	var trunk_mesh := Look._segment_mesh(Vector3(0, 0, 0), lean,
		0.23 + rng.randf() * 0.08, 0.105 + rng.randf() * 0.04, 56)
	trunk.mesh = trunk_mesh
	trunk.material_override = Look.standard(trunk_color, 0.95)
	tree.add_child(trunk)
	
	for branch_i: int in 7:
		var branch := MeshInstance3D.new()
		var angle: float = branch_i * TAU / 3.2 + rng.randf() * 0.35
		var branch_height := trunk_height * (0.42 + float(branch_i) * 0.075)
		var reach := 0.70 + rng.randf() * 0.85
		var branch_end := Vector3(cos(angle) * reach, branch_height + 0.22 + rng.randf() * 0.26, sin(angle) * reach)
		var branch_start := Vector3(lean.x * branch_height / trunk_height, branch_height, lean.z * branch_height / trunk_height)
		var branch_mesh := Look._segment_mesh(branch_start, branch_end, 0.105, 0.028, 40)
		branch.mesh = branch_mesh
		branch.material_override = Look.standard(trunk_color, 0.95)
		tree.add_child(branch)

	# Layered foliage follows the branch structure instead of forming a few
	# spherical blobs. Many smaller, high-resolution clusters create a broken
	# natural silhouette while keeping the procedural scene asset-free.
	for layer: int in 4:
		var y := trunk_height * (0.48 + float(layer) * 0.135)
		var radius := 1.18 - float(layer) * 0.13
		for lobe: int in 5:
			var leaf := MeshInstance3D.new()
			var angle: float = lobe * TAU / 5.0 + rng.randf_range(-0.22, 0.22) + float(layer) * 0.37
			var reach := radius * rng.randf_range(0.48, 0.82)
			leaf.mesh = _foliage_cluster_mesh(rng.randf_range(0.42, 0.62), rng.randf_range(0.28, 0.46), rng.randi())
			leaf.material_override = foliage_mat
			leaf.position = Vector3(cos(angle) * reach, y + rng.randf_range(-0.18, 0.18), sin(angle) * reach)
			leaf.rotation = Vector3(rng.randf_range(-0.28, 0.28), angle, rng.randf_range(-0.28, 0.28))
			tree.add_child(leaf)
	
	return tree

static func _foliage_cluster_mesh(radius: float, height: float, seed: int) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var segments := 48
	var rings := 10
	for y: int in rings + 1:
		var v := float(y) / float(rings)
		var phi := PI * v
		var sin_phi := sin(phi)
		var cos_phi := cos(phi)
		for x: int in segments:
			var u := float(x) / float(segments)
			var theta := TAU * u
			var irregular := 1.0 + 0.075 * sin(theta * 7.0 + float(seed) * 0.11) * sin_phi
			var p := Vector3(cos(theta) * sin_phi * radius * irregular, cos_phi * height, sin(theta) * sin_phi * radius * irregular)
			st.set_uv(Vector2(u, v))
			st.add_vertex(p)
	for y: int in rings:
		for x: int in segments:
			var a := y * segments + x
			var b := y * segments + (x + 1) % segments
			var c := (y + 1) * segments + x
			var d := (y + 1) * segments + (x + 1) % segments
			st.add_index(a); st.add_index(c); st.add_index(b)
			st.add_index(b); st.add_index(c); st.add_index(d)
	st.generate_normals()
	return st.commit()

static func _canopy_mesh(radius: float, height: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var segments := 64
	var rings := 12
	for y: int in rings + 1:
		var v := float(y) / float(rings)
		var phi := PI * v
		for x: int in segments:
			var u := float(x) / float(segments)
			var theta := TAU * u
			var p := Vector3(cos(theta) * sin(phi) * radius, cos(phi) * height, sin(theta) * sin(phi) * radius)
			st.set_uv(Vector2(u, v))
			st.add_vertex(p)
	for y: int in rings:
		for x: int in segments:
			var a := y * segments + x
			var b := y * segments + (x + 1) % segments
			var c := (y + 1) * segments + x
			var d := (y + 1) * segments + (x + 1) % segments
			st.add_index(a); st.add_index(c); st.add_index(b)
			st.add_index(b); st.add_index(c); st.add_index(d)
	st.generate_normals()
	return st.commit()

static func _scatter_rocks(data: Dictionary, parent: Node3D) -> void:
	var width: int = data["width"]
	var height: int = data["height"]
	var tiles: PackedByteArray = data["tiles"]
	
	for z: int in height:
		for x: int in width:
			if tiles[z * width + x] != Terrain.ROCK:
				continue
			var rock := _build_rock(x * 7919 + z * 104729)
			rock.position = Terrain.to_world(Vector2i(x, z))
			parent.add_child(rock)

static func _build_rock(seed: int) -> Node3D:
	var rock := Node3D.new()
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	
	var rock_mesh := Look._organic_ellipsoid(Vector3(0.62 + rng.randf() * 0.45, 0.42 + rng.randf() * 0.32, 0.55 + rng.randf() * 0.42), 32, 3.0)
	var rock_instance := MeshInstance3D.new()
	rock_instance.mesh = rock_mesh
	var rock_color := Color("#6a6670").lerp(Color("#8a8590"), rng.randf() * 0.3)
	rock_instance.material_override = Look.standard(rock_color, 0.95)
	rock_instance.position.y = 0.35 + rng.randf() * 0.18
	rock_instance.rotation = Vector3(rng.randf_range(-0.2, 0.2), rng.randf() * TAU, rng.randf_range(-0.2, 0.2))
	rock.add_child(rock_instance)
	return rock

static func _scatter_grass(data: Dictionary, parent: Node3D) -> void:
	var width: int = data["width"]
	var height: int = data["height"]
	var tiles: PackedByteArray = data["tiles"]
	
	var grass_positions: Array[Vector3] = []
	var rng := RandomNumberGenerator.new()
	rng.seed = data.get("width", 0) * 1000 + data.get("height", 0)
	
	for z: int in height:
		for x: int in width:
			var tile: int = tiles[z * width + x]
			if tile != Terrain.GRASS and tile != Terrain.TALL_GRASS:
				continue
			if rng.randf() < 0.62:
				var jitter := Vector3(rng.randf() * TILE - TILE * 0.5, 0.0,
					rng.randf() * TILE - TILE * 0.5)
				grass_positions.append(Terrain.to_world(Vector2i(x, z)) + jitter)
	
	if grass_positions.is_empty():
		return
	
	var grass_mesh := Look._segment_mesh(Vector3(0, 0, 0), Vector3(0.10, 0.72, 0.025), 0.05, 0.009, 28)
	var grass_material := Look.standard(Terrain.color(Terrain.GRASS).lightened(0.24), 0.88)
	
	var grass_multimesh := MultiMeshInstance3D.new()
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.mesh = grass_mesh
	multimesh.instance_count = grass_positions.size()
	
	for i: int in grass_positions.size():
		var angle := rng.randf() * TAU
		var scale := rng.randf_range(0.72, 1.35)
		var transform := Transform3D(Basis(Vector3.UP, angle).scaled(Vector3.ONE * scale), grass_positions[i])
		multimesh.set_instance_transform(i, transform)
	
	grass_multimesh.multimesh = multimesh
	grass_multimesh.material_override = grass_material
	parent.add_child(grass_multimesh)

static func _scatter_water(data: Dictionary, parent: Node3D) -> void:
	var width: int = data["width"]
	var height: int = data["height"]
	var tiles: PackedByteArray = data["tiles"]
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var water_y := Terrain.height(Terrain.WATER) + 0.045
	var tile_index := 0
	for z: int in height:
		for x: int in width:
			if tiles[z * width + x] != Terrain.WATER:
				continue
			var base := tile_index * 4
			var x0 := float(x) * TILE
			var z0 := float(z) * TILE
			var x1 := x0 + TILE
			var z1 := z0 + TILE
			st.set_uv(Vector2(0, 0)); st.add_vertex(Vector3(x0, water_y, z0))
			st.set_uv(Vector2(1, 0)); st.add_vertex(Vector3(x1, water_y, z0))
			st.set_uv(Vector2(0, 1)); st.add_vertex(Vector3(x0, water_y, z1))
			st.set_uv(Vector2(1, 1)); st.add_vertex(Vector3(x1, water_y, z1))
			st.add_index(base); st.add_index(base + 2); st.add_index(base + 1)
			st.add_index(base + 1); st.add_index(base + 2); st.add_index(base + 3)
			tile_index += 1
	if tile_index == 0:
		return
	st.generate_normals()
	var water := MeshInstance3D.new()
	water.name = "ProceduralWater"
	water.mesh = st.commit()
	water.material_override = _water_material()
	parent.add_child(water)
	var light := OmniLight3D.new()
	light.light_color = Color("#7ea6c5")
	light.light_energy = 0.35
	light.omni_range = 22.0
	light.position = Vector3(float(width) * TILE * 0.5, 0.0, float(height) * TILE * 0.5)
	parent.add_child(light)

static func _water_material() -> ShaderMaterial:
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
render_mode blend_mix, cull_disabled;

float wave(vec2 p) {
    return sin(p.x * 2.7 + TIME * 0.75) * 0.5 + sin(p.y * 3.4 - TIME * 0.55) * 0.5;
}

void vertex() {
    vec2 p = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz * 0.08;
    VERTEX.y += wave(p) * 0.035;
}

void fragment() {
    vec3 base = vec3(0.075, 0.14, 0.20);
    float ripple = wave(VERTEX.xz * 0.7) * 0.5 + 0.5;
    ALBEDO = base + vec3(0.04, 0.08, 0.11) * ripple;
    METALLIC = 0.18;
    ROUGHNESS = 0.18;
    SPECULAR = 0.72;
    EMISSION = vec3(0.015, 0.025, 0.04);
    ALPHA = 0.84;
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	return material
