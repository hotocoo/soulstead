extends Node
## Headless scene-flow test: settlement builds, expedition builds, a death
## routes into succession. Run:
## godot --headless --path game res://tests/flow_smoke.tscn

var _failures: int = 0

func _ready() -> void:
	var container := Node.new()
	add_child(container)
	Flow.bind(container)
	WorldState.new_game(24680)

	Flow.to_settlement()
	await _await_scene("settlement")
	var settlement := Flow.current as Settlement
	check("settlement scene built", settlement != null)
	if settlement != null:
		check("settlement spawned the wielder", settlement.player != null)
		check("settlement has interactables",
				get_tree().get_nodes_in_group("interactables").size() >= 4)

	Flow.to_expedition()
	await _await_scene("expedition")
	var expedition := Flow.current as Expedition
	check("expedition scene built", expedition != null)
	if expedition != null:
		check("expedition spawned the wielder", expedition.player != null)
		var enemies := get_tree().get_nodes_in_group("combatants").filter(
				func(n: Node) -> bool: return n is EnemyActor)
		check("expedition populated enemies", enemies.size() > 0)
		var day_before: float = WorldState.world_day
		await _settle(120)
		check("world clock advanced in the field", WorldState.world_day > day_before)

		expedition.player.take_hit({"damage": 99999.0, "attacker": expedition.player})
		await _await_scene("succession")
		check("death routed into succession", Flow.current_name == "succession")
		check("the fall produced an echo", WorldState.echoes.size() > 0)
		check("the lineage recorded a name", WorldState.lineage.size() == 1)
		var successor := WorldState.succession_candidates()[0]
		WorldState.choose_successor(String(successor["id"]))
		WorldState.advance_time(8.1)
		check("tier-five echo becomes a settlement raid", not WorldState.pending_raid().is_empty())
		Flow.to_settlement()
		await _await_scene("settlement")
		var raid_echoes := get_tree().get_nodes_in_group("combatants").filter(
			func(n: Node) -> bool: return n is EchoActor)
		check("settlement instantiates the raid Echo", raid_echoes.size() > 0)

	print("\n%s (%d failures)" % ["FLOW PASS" if _failures == 0 else "FLOW FAIL", _failures])
	get_tree().quit(1 if _failures > 0 else 0)

## Flow fades between scenes, so tests wait for the transition to land rather
## than guessing a frame count.
func _await_scene(label: String, timeout: float = 6.0) -> void:
	var deadline := Time.get_ticks_msec() + int(timeout * 1000.0)
	while Flow.current_name != label and Time.get_ticks_msec() < deadline:
		await get_tree().process_frame
	await get_tree().process_frame

func _settle(frames: int) -> void:
	for i: int in frames:
		await get_tree().process_frame

func check(label: String, condition: bool) -> void:
	if not condition:
		_failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", label])
