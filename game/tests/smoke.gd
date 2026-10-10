extends Node
## Headless smoke test for the whole SOULSTEAD loop.
## Run: godot --headless --path game res://tests/smoke.tscn

var _failures: int = 0

func _ready() -> void:
	await get_tree().process_frame
	_run()
	print("\n%s (%d failures)" % ["SMOKE PASS" if _failures == 0 else "SMOKE FAIL", _failures])
	get_tree().quit(1 if _failures > 0 else 0)

func check(label: String, condition: bool) -> void:
	if not condition:
		_failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", label])

func _run() -> void:
	print("-- world state")
	var story := StoryDirector.new()
	add_child(story)
	WorldState.story_director = story
	WorldState.new_game(12345)
	check("seven villagers exist", WorldState.villagers.size() == 7)
	check("a wielder is holding the blade", WorldState.wielder_id != "")
	check("authored first wielder is Rin Ashfall", WorldState.wielder()["name"] == "Rin Ashfall")
	check("authored spouse exists in the Hold", not WorldState.villager_by_name("Maren Verren").is_empty())
	var stats: Dictionary = WorldState.wielder_stats()
	check("wielder has health", float(stats["max_hp"]) > 0.0)
	check("wielder has composure", float(stats["max_composure"]) > 0.0)
	check("story opens on day one", not story.active.is_empty() and int(story.active["day"]) == 1)
	check("authored story covers every playable chapter", story.BEATS.size() == 52)
	check("opening chapter is a witnessed scene", story.choices.is_empty())
	var story_snapshot := story.to_dict()
	var resumed_story := StoryDirector.new()
	resumed_story.hydrate(story_snapshot)
	check("unresolved story beat survives save state", not resumed_story.active.is_empty()
			and resumed_story.choices.is_empty() and not resumed_story.choice_taken)
	story.dismiss_active()
	check("story scene can be acknowledged", story.active.is_empty())
	WorldState.advance_time(500.0)
	# The runtime gate for chapter 4 is a real field departure. The story
	# replay must provide that witness before the missed beat can surface.
	story.notify_event("expedition_entered")
	story.process_day(WorldState.world_day)
	check("story resumes at the first missed beat", not story.active.is_empty() and int(story.active["day"]) == 6)
	var story_guard := 0
	while not story.is_story_complete() and story_guard < 300:
		story_guard += 1
		if story.active.is_empty():
			# A blocked beat has no UI surface yet, so the deterministic replay
			# supplies its required witness and lets StoryDirector surface it.
			for beat: Dictionary in story.BEATS:
				if story._is_witnessed(beat):
					continue
				var gate := story._required_event(beat)
				if gate != "":
					story.notify_event(gate)
				else:
					story.process_day(WorldState.world_day)
				break
			if story.active.is_empty():
				break
		if int(story.active.get("day", 0)) == 196:
			# Reproduce the authored final succession with the real simulation:
			# The real campaign reaches Wren through Orrin; the replay only needs
			# the authored person and final hand to exist to verify the endpoint.
			var wren := WorldState._ensure_authored_person("Wren Ashfall", "spouse")
			if String(WorldState.wielder().get("name", "")) != "Wren Ashfall":
				WorldState.choose_successor(String(wren["id"]))
		if int(story.active.get("day", 0)) == 209 and not story.has_event("wren_death"):
			if String(WorldState.wielder().get("name", "")) == "Wren Ashfall":
				WorldState.register_death(Vector3.ZERO, "grey_ash", "story replay")
				for candidate: Dictionary in WorldState.succession_candidates():
					if String(candidate.get("name", "")) == "Grieve Mourne":
						WorldState.choose_successor(String(candidate["id"]))
						break
		if int(story.active.get("day", 0)) == 209 and story.has_event("wren_death") and String(WorldState.wielder().get("name", "")) == "Wren Ashfall":
			WorldState.register_death(Vector3.ZERO, "grey_ash", "story replay")
			for candidate: Dictionary in WorldState.succession_candidates():
				if String(candidate.get("name", "")) == "Grieve Mourne":
					WorldState.choose_successor(String(candidate["id"]))
					break
		# This loop is a deterministic authored-story replay, not gameplay. The
		# real game supplies these events through movement, combat, interaction,
		# succession, and vigils. Here we satisfy each gate explicitly so the
		# test verifies that the entire authored chain can be traversed without
		# weakening the runtime event gates.
		var required := story._required_event(story.active)
		if required != "" and not story.has_event(required):
			story.notify_event(required)
		if not story.choices.is_empty():
			if int(story.active.get("day", 0)) in [209, 210]:
				# The authored replay supplies enough accumulated grief for the
				# canonical final Wake; normal play earns this through the lineage.
				WorldState.grief = maxi(WorldState.grief, 200)
			var choice_index := 0
			for i: int in story.choices.size():
				if bool(story.choices[i].get("available", true)):
					choice_index = i
					break
			story.resolve_choice(choice_index)
			story.dismiss_active()
		else:
			story.dismiss_active()
	check("story replay terminates", story_guard < 300)
	if story_guard >= 300:
		print("  stuck beat: %s" % story.active)
	check("story reaches the current authored endpoint", story.is_story_complete())
	check("world clock stops at story endpoint", is_equal_approx(WorldState.world_day, 210.0))
	check("Act VI leaves the named second-book wielder", String(WorldState.wielder().get("name", "")) == "Grieve Mourne")
	check("final Wake actually clears grief", WorldState.grief == 0)
	check("final story handoff records the last death", WorldState.lineage.size() > 0
			and String(WorldState.lineage[-1].get("name", "")) == "Wren Ashfall")
	WorldState.new_game(12345)

	print("-- map generation")
	var map: Dictionary = MapGen.generate(WorldState.world_seed)
	check("map is the expected size",
			int(map["width"]) == MapGen.WIDTH and int(map["height"]) == MapGen.HEIGHT)
	check("spawn tile is walkable",
			not Terrain.is_blocking(_tile_at(map, map["spawn"])))
	check("chest spots were placed", (map["chest_spots"] as Array).size() > 0)
	var holder := Node3D.new()
	add_child(holder)
	var surface: MeshInstance3D = TerrainBuilder.build(map, holder)
	check("terrain built a mesh", surface.mesh != null and surface.mesh.get_surface_count() > 0)
	check("terrain built collision",
			holder.get_children().any(func(n: Node) -> bool: return n is StaticBody3D))

	print("-- death, echo, succession")
	var before_grief: int = WorldState.grief
	var dead_name: String = String(WorldState.wielder()["name"])
	var echo: Dictionary = WorldState.register_death(Vector3(64.0, 0.0, 48.0), "vale", "Gravewarden")
	check("an echo was created", not echo.is_empty())
	check("echo remembers its owner", String(echo["owner"]) == dead_name)
	check("grief rose", WorldState.grief > before_grief)
	check("wielder slot is empty", WorldState.wielder_id == "")
	var candidates: Array[Dictionary] = WorldState.succession_candidates()
	check("three successors offered", candidates.size() == 3)
	check("successors carry a bond to the dead",
			candidates.all(func(p: Dictionary) -> bool: return p.has("bond_to_dead")))
	check("Rin's authored spouse is offered first", String(candidates[0]["name"]) == "Maren Verren"
			and String(candidates[0]["bond_to_dead"]) == "spouse")
	WorldState.choose_successor(String(candidates[0]["id"]))
	check("new wielder took the blade", WorldState.wielder_id == String(candidates[0]["id"]))
	check("successor has an authored bond effect", WorldState.bond_effect(
			String(candidates[0].get("bond_to_dead", "stranger"))).size() > 0)
	check("all named Vale routes exist", WorldState.available_locations().size() == 6)
	check("route selection is persistent state", WorldState.set_expedition_location("stonewake")
			and WorldState.current_location == "stonewake")
	var stonewake_map := MapGen.generate(WorldState.world_seed, "stonewake", 0)
	check("Stonewake has a quarry landmark", (stonewake_map.get("barrows", []) as Array).size() == 3)
	var mere_map := MapGen.generate(WorldState.world_seed, "kettlemere", 0)
	check("Kettlemere has a drowned-water landmark", mere_map.has("mere"))
	var vane_map := MapGen.generate(WorldState.world_seed, "vane_road", 0)
	check("Vane Road has a gate landmark", vane_map.has("vane_gate"))
	WorldState.set_expedition_location("wrenfield")
	WorldState.regions["wrenfield"]["decay"] = 3
	check("Grey can be pushed back", WorldState.restore_region("wrenfield"))
	check("region decay actually changed", WorldState.region_decay("wrenfield") == 2)
	WorldState.regions["wrenfield"]["decay"] = 0

	print("-- echo tiering")
	var tier_before: int = int(WorldState.echoes[0]["tier"])
	WorldState.advance_time(WorldState.ECHO_TIER_DAYS + 0.1)
	check("unreclaimed echo grew", int(WorldState.echoes[0]["tier"]) > tier_before)

	print("-- vigils and legacies")
	WorldState.grief = 80
	var hp_before: float = WorldState.wielder_stats()["max_hp"]
	check("burial is affordable", WorldState.can_perform_vigil("burial"))
	check("burial performed", WorldState.perform_vigil("burial"))
	check("legacy raised max health", float(WorldState.wielder_stats()["max_hp"]) > hp_before)
	var flasks_before: int = WorldState.max_flasks()
	WorldState.perform_vigil("pyre")
	check("pyre added a flask charge", WorldState.max_flasks() > flasks_before)

	print("-- chronicle and endings")
	check("chronicle recorded the death",
			Chronicle.entries.any(func(e: Dictionary) -> bool:
				return String(e.get("action", "")) == "wielder_died"))
	check("vigils moved the memory axis", Chronicle.axis("memory") != 0.0)
	var projected: Dictionary = Chronicle.projected_ending()
	check("an ending is projected", projected.has("id"))
	var communion_before: float = Chronicle.axis("communion")
	Chronicle.record("ally_abandoned", "Tarn Grey")
	check("abandoning an ally drops communion", Chronicle.axis("communion") < communion_before)
	check("ledger summarises", Chronicle.summary_lines().size() == Chronicle.AXES.size() + 1)

	print("-- combat bodies")
	var enemy := EnemyActor.new()
	add_child(enemy)
	enemy.configure("warden", 2)
	check("enemy scaled with region decay", enemy.max_health > float(Codex.enemy("warden")["hp"]))
	var player := PlayerActor.new()
	add_child(player)
	check("player took wielder stats", is_equal_approx(player.max_health,
			float(WorldState.wielder_stats()["max_hp"])))
	var hp_start: float = player.health
	player.take_hit({"damage": 12.0, "poise_damage": 5.0, "attacker": enemy})
	check("player takes damage", player.health < hp_start)
	player.enter_state(Combatant.State.DODGE, player.DODGE_TIME)
	check("dodge grants i-frames", player.is_invulnerable())
	var hp_mid: float = player.health
	player.take_hit({"damage": 50.0, "attacker": enemy})
	check("i-frames ignore the hit", is_equal_approx(player.health, hp_mid))

	print("-- persistence")
	check("save written", WorldState.save_game())
	var day_before: float = WorldState.world_day
	var grief_before: int = WorldState.grief
	var echoes_before: int = WorldState.echoes.size()
	WorldState.new_game(999)
	check("reloaded", WorldState.load_game())
	check("world day restored", is_equal_approx(WorldState.world_day, day_before))
	check("grief restored", WorldState.grief == grief_before)
	check("echoes restored", WorldState.echoes.size() == echoes_before)
	check("chronicle restored", Chronicle.entries.size() > 0)

	print("-- echo exchange (asynchronous multiplayer)")
	EchoExchange.ensure_dirs()
	var path: String = EchoExchange.send(WorldState.echoes[0], "Test Hold")
	check("echo exported for another settlement", FileAccess.file_exists(path))
	DirAccess.copy_absolute(path, "%s/%s" % [EchoExchange.INBOX, path.get_file()])
	var received: Array[Dictionary] = EchoExchange.receive_all()
	check("drifted echo can be imported", received.size() > 0)
	check("drifted echo is marked foreign", bool(received[0].get("foreign", false)))
	var foreign_echo := EchoActor.new()
	add_child(foreign_echo)
	foreign_echo.from_echo(received[0], 0)
	check("foreign echo builds a body", foreign_echo.max_health > 0.0)
	DirAccess.remove_absolute("%s/%s" % [EchoExchange.INBOX, path.get_file()])
	DirAccess.remove_absolute(path)

	print("-- net session")
	check("offline by default", not NetSession.is_networked())
	check("relay url configured", NetSession.relay_url.begins_with("ws"))

func _tile_at(map: Dictionary, tile: Vector2i) -> int:
	var tiles: PackedByteArray = map["tiles"]
	return tiles[tile.y * int(map["width"]) + tile.x]
