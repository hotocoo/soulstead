extends Node

var failures := 0

func _ready() -> void:
	var story := StoryDirector.new()
	add_child(story)
	WorldState.story_director = story
	WorldState.new_game(424242)
	story.dismiss_active()
	WorldState.advance_time(500.0)
	story.notify_event("expedition_entered")

	var guard := 0
	while not story.is_story_complete() and guard < 100:
		guard += 1
		if story.active.is_empty():
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

		var day := int(story.active.get("day", 0))
		if day == 196:
			var wren := WorldState._ensure_authored_person("Wren Ashfall", "spouse")
			if String(WorldState.wielder().get("name", "")) != "Wren Ashfall":
				WorldState.choose_successor(String(wren["id"]))
		if day == 209 and not story.has_event("wren_death") and String(WorldState.wielder().get("name", "")) == "Wren Ashfall":
			WorldState.register_death(Vector3.ZERO, "grey_ash", "story replay")
			for candidate: Dictionary in WorldState.succession_candidates():
				if String(candidate.get("name", "")) == "Grieve Mourne":
					WorldState.choose_successor(String(candidate["id"]))
					break

		var required := story._required_event(story.active)
		if required != "" and not story.has_event(required):
			story.notify_event(required)
		if not story.choices.is_empty():
			if day == 209:
				# The day-209 story beat is the Wake setup, while day 210 is the
				# terminal rite. Leave enough accumulated grief for both authored pages.
				WorldState.grief = maxi(WorldState.grief, 200)
			var picked := -1
			for i: int in story.choices.size():
				if bool(story.choices[i].get("available", true)):
					picked = i
					break
			if picked < 0 or not story.resolve_choice(picked):
				failures += 1
				break
		story.dismiss_active()

	check("all authored story beats can be traversed", story.is_story_complete())
	check("story endpoint is day 210", is_equal_approx(WorldState.world_day, 210.0))
	check("final hand is Grieve Mourne", String(WorldState.wielder().get("name", "")) == "Grieve Mourne")
	check("final Wake clears grief", WorldState.grief == 0)
	check("final death is Wren Ashfall", not WorldState.lineage.is_empty() and String(WorldState.lineage[-1].get("name", "")) == "Wren Ashfall")
	print("\nSTORY E2E %s (%d failures)" % ["PASS" if failures == 0 else "FAIL", failures])
	get_tree().quit(1 if failures > 0 else 0)

func check(label: String, condition: bool) -> void:
	if not condition:
		failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", label])
