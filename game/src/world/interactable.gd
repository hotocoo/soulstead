class_name Interactable
extends Node3D
## Anything the player can face and press interact on. The world keeps these in
## a group and picks the closest one inside reach.

const REACH := 2.6

var prompt: String = "Look"

func _ready() -> void:
	add_to_group("interactables")

func can_interact() -> bool:
	return true

## Overridden by subclasses. `world` is the Settlement or Expedition node.
func interact(_world: Node) -> void:
	pass

## Solid props block movement so the player cannot walk through them.
func add_body(size: Vector3 = Vector3(1.4, 2.0, 1.4), offset: Vector3 = Vector3(0, 1.0, 0))\
		-> void:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	shape.position = offset
	body.add_child(shape)
	add_child(body)
