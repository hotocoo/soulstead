class_name LedgerBoard
extends Interactable
## The Chronicle made physical: which way the settlement is drifting, and the
## ending that drift currently points at.

func _ready() -> void:
	super()
	prompt = "Read the ledger"
	for side: int in [-1, 1]:
		var post := MeshInstance3D.new()
		post.mesh = Look._segment_mesh(Vector3(0, -1.1, 0), Vector3(0.04, 1.1, 0.03), 0.12, 0.07, 24)
		post.material_override = Look.standard(Color("#4b3520"))
		post.position = Vector3(1.1 * side, 1.1, 0)
		add_child(post)
	var board := MeshInstance3D.new()
	board.mesh = Look._rounded_block_mesh(Vector3(2.6, 1.5, 0.12), 0.05, 24)
	board.material_override = Look.standard(Color("#8a6136"))
	board.position = Vector3(0, 1.6, 0)
	add_child(board)
	add_body(Vector3(2.6, 2.2, 0.6), Vector3(0, 1.1, 0))

func interact(world: Node) -> void:
	if WorldState.story_director != null:
		WorldState.story_director.notify_event("ledger_read")
	world.open_ledger()
