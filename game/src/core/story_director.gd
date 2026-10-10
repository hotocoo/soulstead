class_name StoryDirector
extends Node
## The authored story layer for the Ashfall Chronicle.
##
## The simulation remains authoritative: this director never invents Chronicle
## entries. It turns the existing novel/lore into playable chapter beats,
## objectives, and witnessed scenes, and persists the last witnessed beat.

signal beat_started(beat: Dictionary)
signal beat_finished(beat: Dictionary)
signal choice_resolved(choice: Dictionary, beat: Dictionary)

const BEATS := [
	{"day": 1, "chapter": 3, "title": "The Coming of the Ashfall Family", "place": "Ashfall Hold", "act": "I — The Hold", "text": "The Hold is small enough that every pair of hands has a name. The Ashfall family arrives carrying nothing worth stealing and everything worth inheriting: habits, tools, and the expectation that the dead must be kept.", "objective": "Walk the Hold. Learn the Hearth, Memorial, and Ledger."},
	{"day": 6, "chapter": 4, "title": "What the Ash Does to the Dead", "place": "Wrenfield", "act": "I — The Hold", "text": "The ash is not only what fell from the Mourne. Something else has begun to draw grey from the ground. The first dead thing that stands again teaches the Hold the difference.", "objective": "Leave the Hold and survive your first field expedition."},
	{"day": 8, "chapter": 5, "title": "The First Interval", "place": "Wrenfield", "act": "I — The Hold", "text": "They wait because nobody agrees what the dead thing is. Ketil Brack learns what a body can survive when he meets it with a fence stake, while Bran Holt notices the roots paling beneath its feet. The Hold gives three motions names: the Loosing, the Holding, the Keeping.", "objective": "Witness the first Echo without mistaking it for the person who died."},
	{"day": 9, "chapter": 6, "title": "The Invention of the Vigil", "place": "Memorial ground", "act": "I — The Hold", "text": "The first Vigil gives the settlement a language for what death leaves behind. The dead leave. The hold remains. Someone must decide what to do with it.", "objective": "At the Memorial, convert grief into a Legacy when enough grief has gathered."},
	{"day": 10, "chapter": 7, "title": "Rin Ashfall", "place": "Smithy", "act": "I — The Hold", "text": "Rin takes the Ashblade. The choice is not made by a hero arriving from elsewhere. It is made by a person the Hold already knows.", "objective": "Take the Ashblade into the field."},
	{"day": 12, "chapter": 8, "title": "Wrenfield and the Long Grass", "place": "Wrenfield", "act": "I — The First Wielder", "text": "The long grass moves before anything is visible. In Soulstead, a tell is mercy: the enemy must show you the shape of the thing that will kill you.", "objective": "Read enemy tells and survive the road through Wrenfield."},
	{"day": 13, "chapter": 9, "title": "The Warden at Stonewake", "place": "Stonewake Scarp", "act": "I — The First Wielder", "text": "A Gravewarden waits among stone that remembers older names. It does not rush. It expects the living to make the first mistake.", "objective": "Break a Gravewarden's poise and live through its counterattack."},
	{"day": 14, "chapter": 10, "title": "The Day the Hillside Was Beautiful", "place": "Beyond the last fence", "act": "I — The First Wielder", "text": "For one afternoon the hillside is beautiful enough to make the danger seem unreasonable. Then the Hold learns that beauty is not protection.", "objective": "Return from the field. Death is part of the Chronicle, not a reset."},
	{"day": 15, "chapter": 11, "title": "Maren Verren Takes the Maul", "place": "Hearth and Smithy", "act": "I — The First Wielder", "text": "Maren does not inherit Rin's life. She inherits the consequences of it. The widow takes the maul because someone has to carry the weight home.", "objective": "Choose the next wielder during Succession."},
	{"day": 19, "chapter": 12, "title": "The Reclaiming of Rin", "place": "Wrenfield", "act": "I — The First Wielder", "text": "Rin's Echo stands where Rin fell. It is not Rin. It is the grip Rin left behind, still closed around the blade.", "objective": "Defeat and reclaim the Echo of the fallen."},
	{"day": 21, "chapter": 13, "title": "The Ledger Board", "place": "Hearth", "act": "I — The First Wielder", "text": "The Hold writes its choices down. Four numbers begin to make a shape: Memory, Mercy, Communion, Dominion. The ending is no longer hidden from the living.", "objective": "Read the Ledger and understand what your choices are becoming."},
	{"day": 24, "chapter": 16, "title": "The Hearthkeepers and the Cull", "place": "West field", "act": "II — The Vale", "text": "A settlement can be merciful until mercy costs hands it cannot spare. The Cull calls that arithmetic honesty. The Hearthkeepers call it something else.", "objective": "Choose what kind of Hold your labour and violence will build."},
	{"day": 25, "chapter": 17, "title": "The Long Hold and the Open Road", "place": "Palisade", "act": "II — The Vale", "text": "Three Wayfarers arrive carrying no goods. They carry entries from other valleys instead. One of them is Tove Rowan, still a stranger to the Hold, and the route-mark she cuts into the post means that another board can hear this one.", "objective": "Open the gate and learn what crosses between settlements."},
	{"day": 27, "chapter": 18, "title": "The Gravewardens and the Yielding", "place": "Stonewake Scarp", "act": "II — The Vale", "text": "Not every enemy must be killed. Sometimes the hardest thing a blade can do is remain sheathed while the dead speak.", "objective": "Encounter an enemy you can spare."},
	{"day": 31, "chapter": 19, "title": "The Unburied Smith", "place": "Smithy", "act": "II — The Vale", "text": "The Smithy understands the economy of the dead better than any priest: ash becomes lye, lye becomes pearl, pearl becomes glass, and relic becomes remembered motion.", "objective": "Bring a relic home and use it to strengthen the lineage."},
	{"day": 38, "chapter": 20, "title": "Low Kettle Under the Mere", "place": "Kettlemere", "act": "II — The Vale", "text": "The lake keeps a village the Ledger cannot count. What is drowned is not necessarily gone. What is unrecorded is not necessarily absent.", "objective": "Reach the water country and return with the Hold's memory intact."},
	{"day": 41, "chapter": 21, "title": "The Cull at Brackwood, One", "place": "Brackwood", "act": "II — The Vale", "text": "Nine charcoal burners return with grey in the seams of their hands. The Healers call it drawn-ash in the lungs. The Cull reads their names from a roster and asks the question the Hold does not want to answer: how many working hands can mercy afford?", "objective": "Inspect the quarantine and hear both sides before the decision."},
	{"day": 47, "chapter": 22, "title": "The Cull at Brackwood", "place": "Brackwood", "act": "II — The Vale", "text": "The Cull wants certainty. Brackwood offers only people, sickness, fear, and the knowledge that certainty made by force is still a choice.", "objective": "Make a consequential choice in Brackwood and live with its Chronicle."},
	{"day": 53, "chapter": 23, "title": "The Gravewarden Who Remembered", "place": "Sealed barrow", "act": "II — The Vale", "text": "A Gravewarden remembers a name it should not know. The Hold's first true argument begins: is remembering a reason to kill the dead, or a reason to listen?", "objective": "Face the remembered dead without surrendering your judgment."},
	{"day": 55, "chapter": 24, "title": "The Shaved Panes", "place": "Memorial", "act": "II — The Vale", "text": "Eleven panes have been smeared. Grieve Mourne, still a child, sees the marks because he looks at the Memorial from the wrong angle. The investigation finds no clean answer: two graves are quiet, two are not, and the pale root refuses to explain itself.", "objective": "Examine the Memorial and decide what evidence is actually worth believing."},
	{"day": 61, "chapter": 25, "title": "The Quiet Doctrine", "place": "Ashfall Hold", "act": "II — The Vale", "text": "A doctrine arrives that promises safety by making the Hold smaller, quieter, and less troubled by names. It is easier to obey than to answer.", "objective": "Keep the Memorial alive while the doctrine spreads."},
	{"day": 66, "chapter": 26, "title": "The Long Grass Road", "place": "Crossing post", "act": "III — Strangers", "text": "The road brings people who are not yours. The Hold must decide whether a stranger's life can become part of its own story without becoming property.", "objective": "Meet the road and decide who gets through the gate."},
	{"day": 70, "chapter": 27, "title": "The Stranger's Echo", "place": "Wrenfield and Memorial", "act": "III — Strangers", "text": "A foreign Echo arrives carrying a life from another Hold. For the first time, the dead outside your lineage stand before you asking the same question as your own.", "objective": "Honour, destroy, or send on a stranger's Echo."},
	{"day": 74, "chapter": 33, "title": "The Carver's Glass", "place": "Memorial", "act": "III — Strangers", "text": "A name-pane is made from the substance of the named. The Memorial becomes less like a wall of names and more like a body the settlement has built together.", "objective": "Spend a relic only when you believe the thing it builds should outlast you."},
	{"day": 79, "chapter": 34, "title": "The Ash Flask", "place": "Hearth", "act": "III — Strangers", "text": "The Flask is not a potion. It is measured ash, water, heat, and restraint. Three is a ration because four has killed people at the Hearth.", "objective": "Treat every Flask as a choice about what happens next."},
	{"day": 84, "chapter": 35, "title": "Colm Grey, Rival", "place": "Stonewake Scarp", "act": "III — Strangers", "text": "Colm takes the blade as a rival. He does not promise to honour the dead. He promises to finish what the dead started.", "objective": "Let the successor's relationship to the dead change how you fight."},
	{"day": 86, "chapter": 28, "title": "The Relic Debt", "place": "Smithy and Wrenfield", "act": "III — Strangers", "text": "Maren's Echo has reached its roaming growth, carrying the relic bound to the Widow's Maul. Colm needs a head for the Reaper Pike. To make one weapon live, he must decide what to do with the memory trapped in another.", "objective": "Recover the relic and decide whether it belongs in steel or stone."},
	{"day": 94, "chapter": 29, "title": "The Fieldhand's Wedding", "place": "Ashfall Hold", "act": "III — Strangers", "text": "A wedding is held while the rota is short and the palisade needs a Warden. Asha Vane is pulled from the Carvers' shed. The ceremony lasts eleven minutes. Work does not stop for long enough to make the day feel like a holiday.", "objective": "See what the settlement pays when one working hand becomes a Warden."},
	{"day": 95, "chapter": 30, "title": "The Cost of a Working Hand", "place": "Ashfall Hold", "act": "III — Strangers", "text": "The Hold discovers that every warrior is also a missing Smith, Forager, Healer, Carver, or Warden. Conscript a person and the settlement pays twice.", "objective": "Choose between field strength and settlement strength."},
	{"day": 99, "chapter": 30, "title": "Vane Hold", "place": "Vane Road", "act": "III — Strangers", "text": "Another Hold appears in the Chronicle's margins. Its survival proves that Soulstead is not only one family's story. It is a pattern other people can enter.", "objective": "Follow the Vane Road and return with a changed understanding of the Vale."},
	{"day": 102, "chapter": 31, "title": "The Ash Orchard", "place": "Grey Ash", "act": "III — Strangers", "text": "Seven people walk north into the Ash Orchard, where the Yielding sits down and leaves no Echo. Colm does not stop them. The Hold has found a choice for which no verb exists.", "objective": "Enter the Grey Ash and confront the strongest argument for surrender."},
	{"day": 104, "chapter": 31, "title": "The Ash Orchard", "place": "Grey Ash", "act": "III — Strangers", "text": "The Grey Ash grows where the ground should be dead. Nothing about the Vale permits a simple answer anymore.", "objective": "Push back decay before a living place becomes Gone."},
	{"day": 109, "chapter": 36, "title": "Yeva Holt, Sibling", "place": "Grey Ash", "act": "IV — The Holding", "text": "Yeva inherits blood and accusation at the same time. A sibling carries a dead person's memory differently from a spouse, a rival, or a stranger.", "objective": "Choose a successor whose bond changes the shape of the next life."},
	{"day": 116, "chapter": 36, "title": "What the Sibling Carries", "place": "Ashfall Hold", "act": "IV — The Holding", "text": "The Hold learns that inheritance is not ownership. The successor carries a person only insofar as the living decide what that person's hold is worth keeping.", "objective": "Turn grief into a Legacy rather than leaving it to the Echo."},
	{"day": 121, "chapter": 37, "title": "Tarn Stonewake, Stranger", "place": "Brackwood", "act": "IV — The Holding", "text": "The stranger is the efficient choice. That is precisely why the choice hurts. A Hold can optimize itself into forgetting what it was for.", "objective": "Choose efficiency without letting the people become numbers."},
	{"day": 128, "chapter": 32, "title": "The Week of the Holding", "place": "Brackwood", "act": "IV — The Holding", "text": "A Vigil is skipped. An Echo is left standing. The Hold has chosen delay, and delay has a body. Somewhere in the dark, the old blade is learning the road home.", "objective": "Return before the Echo reaches the palisade."},
	{"day": 134, "chapter": 32, "title": "The Raid of Yeva Holt", "place": "Palisade", "act": "IV — The Holding", "text": "The dead come home armed with everything the living taught them. The worst enemy in Soulstead is not an ancient monster. It is a life you already spent.", "objective": "Defend the settlement from a tier-five Echo."},
	{"day": 135, "chapter": 32, "title": "Reclaiming the Raider", "place": "Hold lanes", "act": "IV — The Holding", "text": "When the Echo falls, the Hold gets back more than gear. It gets the grief the body had been carrying and the relic that remains when the grip finally opens.", "objective": "Reclaim the Echo and decide what its death becomes."},
	{"day": 136, "chapter": 32, "title": "The Wake", "place": "Memorial", "act": "IV — The Holding", "text": "The settlement gathers because a Wake is not a reward. It is the admission that a life was larger than the weapon it left behind.", "objective": "Use the Wake only if the Hold can afford to spend everything it has gathered."},
	{"day": 140, "chapter": 37, "title": "Another Death, Another Hand", "place": "Stonewake Scarp", "act": "IV — The Holding", "text": "Tarn falls. The blade moves again. Nothing is reset: the fields remember the missing worker, the Memorial remembers the name, and the road remembers the route.", "objective": "Continue the lineage instead of restarting it."},
	{"day": 147, "chapter": 38, "title": "Sable Kettle, Friend", "place": "Stonewake Scarp", "act": "IV — The Holding", "text": "Friendship changes the arithmetic of grief. It also makes the arithmetic personal. Sable knows the dead well enough to hate what their Echo has become.", "objective": "Use relationship, not only numbers, to decide what to keep."},
	{"day": 152, "chapter": 39, "title": "Wrenfield Goes Gone", "place": "Wrenfield", "act": "V — The Grey", "text": "The colour leaves first. Then the insects. Then the road becomes something people remember rather than somewhere they go.", "objective": "Prevent a region from reaching Gone, or witness what happens when it does."},
	{"day": 163, "chapter": 40, "title": "The Pushing Back", "place": "Wrenfield", "act": "V — The Grey", "text": "Decay is not reversed by wishing. The Hold has to put something back into the ground by finishing what it started with the dead.", "objective": "Save Wrenfield through action, not intention."},
	{"day": 168, "chapter": 40, "title": "The Reclaiming of Sable", "place": "Wrenfield", "act": "V — The Grey", "text": "Sable's Echo is reclaimed. The grey ground does not become green in an instant. The point is not restoration. The point is that the Holding has ended here.", "objective": "Reclaim what the lineage has left behind."},
	{"day": 172, "chapter": 39, "title": "Nix Ember, Rival", "place": "Grey Ash", "act": "V — The Grey", "text": "Nix takes the blade with the old rival's distance. By now the lineage is a chain of people who never agreed about what the chain meant.", "objective": "Carry the blade without pretending the past was simple."},
	{"day": 173, "chapter": 40, "title": "Orrin Dunn", "place": "Wrenfield", "act": "V — The Grey", "text": "Orrin becomes the next hand. The Hold has learned to count its dead without reducing them to the count.", "objective": "Keep the settlement alive while the world remains unstable."},
	{"day": 184, "chapter": 41, "title": "The Two Boards", "place": "Holt Vale", "act": "V — The Grey", "text": "Two ledgers can both be honest and still disagree. One records what happened here. The other records what happened elsewhere. Neither owns the whole truth.", "objective": "Meet another Hold and decide whether consequence should cross the road."},
	{"day": 190, "chapter": 41, "title": "The Stranger Honoured", "place": "Holt Vale", "act": "V — The Grey", "text": "A stranger's Echo is buried far from its first death. Communion becomes more than a word on a board: the dead can belong to a place they never knew.", "objective": "Choose what your Hold owes to lives beyond its walls."},
	{"day": 196, "chapter": 42, "title": "Wren Ashfall, Spouse", "place": "Palisade", "act": "VI — The Last Hand", "text": "Wren is the spouse who will eventually be remembered by the person who writes this down. The story is beginning to turn toward its teller.", "objective": "Protect the Hold through the last succession before the reckoning."},
	{"day": 203, "chapter": 42, "title": "The Last Reclaiming", "place": "Grey Ash", "act": "VI — The Last Hand", "text": "Orrin's Echo is reclaimed. The board is almost full. The Hold has not escaped consequence; it has learned to carry it.", "objective": "Enter the final week with no unfinished Echo if you seek the Wake."},
	{"day": 209, "chapter": 43, "title": "Wren Falls", "place": "Grey Ash", "act": "VI — The Last Hand", "text": "Wren falls. Grieve takes the blade. The person who has spent the story writing about everyone else is now inside the sentence.", "objective": "Take up the blade as Grieve Mourne."},
	{"day": 210, "chapter": 43, "title": "The Wake and the Second Book", "place": "Memorial and Hearth", "act": "VI — The Last Hand", "text": "The first book closes where every Hold fears to arrive: after the last death, with the names still present. A second book begins because the living have not finished deciding what the dead mean.", "objective": "Complete the final Vigil. The current story ends here; further history remains unwritten."},
]

var witnessed: Dictionary = {}
var events: Dictionary = {}
var current_index := -1
var active: Dictionary = {}
var choices: Array[Dictionary] = []
var choice_taken := false

func reset() -> void:
	witnessed.clear()
	events.clear()
	# The opening is a real arrival, not a calendar popup. Settlement emits the
	# event again on load, but keeping it here makes a fresh lineage immediately
	# playable before the first scene has finished constructing.
	events["settlement_entered"] = true
	events["blade_taken"] = true
	current_index = -1
	active = {}
	choices.clear()
	choice_taken = false

func hydrate(data: Dictionary) -> void:
	witnessed.clear()
	for key: Variant in data.get("witnessed", {}).keys():
		witnessed[str(key)] = true
	events = data.get("events", {}).duplicate(true)
	current_index = int(data.get("current_index", -1))
	active = data.get("active", {}).duplicate(true)
	choices.clear()
	if not active.is_empty():
		choices = _choices_for(active)
		choice_taken = bool(data.get("choice_taken", false))
	else:
		choice_taken = false

func to_dict() -> Dictionary:
	return {
		"witnessed": witnessed,
		"events": events,
		"current_index": current_index,
		"active": active,
		"choice_taken": choice_taken,
	}

func process_day(day: float) -> void:
	var target := int(floor(day))
	if not active.is_empty():
		return
	for i: int in BEATS.size():
		var beat: Dictionary = BEATS[i]
		var key := _beat_key(beat)
		if int(beat["day"]) > target:
			break
		if _is_witnessed(beat):
			continue
		# Authored history is strictly ordered. A reached-but-unwitnessed beat
		# blocks later beats until its physical requirement has actually happened;
		# otherwise a later already-true flag could make the story jump over the
		# scene the player was supposed to live through.
		if not _beat_ready(beat):
			break
		_start_beat(i)
		break

func _start_beat(index: int) -> void:
	current_index = index
	active = BEATS[index].duplicate(true)
	witnessed[_beat_key(active)] = true
	choices = _choices_for(active)
	choice_taken = false
	beat_started.emit(active)

func dismiss_active() -> void:
	if active.is_empty():
		return
	if not choices.is_empty() and not choice_taken:
		return
	var finished := active.duplicate(true)
	active = {}
	choices.clear()
	choice_taken = false
	beat_finished.emit(finished)
	# If a save was resumed after a long absence, do not silently skip the
	# authored history. The next acknowledgement reveals the next missed beat.
	process_day(WorldState.world_day)

## Physical gameplay reports facts to the authored layer. A chapter can still
## be delayed by the world clock, but reaching its day is never enough by
## itself: the player must have actually performed or witnessed its central
## action. This is the boundary between a story-driven game and a slideshow.
func notify_event(event: String, payload: Dictionary = {}) -> void:
	if event.is_empty():
		return
	events[event] = true
	if not payload.is_empty():
		events["%s:%s" % [event, String(payload.get("key", ""))]] = true
	process_day(WorldState.world_day)

func has_event(event: String) -> bool:
	return bool(events.get(event, false))

func _required_event(beat: Dictionary) -> String:
	var chapter := int(beat.get("chapter", 0))
	match chapter:
		3: return "settlement_entered"
		4: return "expedition_entered"
		5, 6: return "first_death"
		7: return "blade_taken"
		8: return "field_combat"
		9: return "gravewarden_seen"
		10: return "wielder_died:Rin Ashfall"
		11: return "succession_complete"
		12: return "echo_reclaimed"
		13: return "ledger_read"
		16: return "brackwood_entered"
		17, 26: return "open_road_met"
		18, 23: return "gravewarden_encounter"
		19: return "relic_acquired"
		20: return "kettlemere_entered"
		21: return "quarantine_inspected"
		22: return "brackwood_decision"
		24: return "memorial_inspected"
		25: return "doctrine_decision"
		27: return "foreign_echo_seen"
		28: return "relic_decision"
		29: return "wedding_decision"
		30: return "vane_hold_entered"
		31: return "ash_orchard_entered"
		32: return "yeva_raid"
		33: return "carver_glass"
		34: return "flask_used"
		35: return "wielder_died:Maren Verren"
		36: return "wielder_died:Colm Grey"
		37: return "wielder_died:Yeva Holt"
		38: return "wielder_died:Tarn Stonewake"
		39: return "wrenfield_gone"
		40: return "region_saved"
		41: return "two_boards"
		42: return "wielder_died:Orrin Dunn"
		43: return "wielder_died:Wren Ashfall"
		_: return ""

func _beat_ready(beat: Dictionary) -> bool:
	var required := _required_event(beat)
	return required == "" or has_event(required)

func current_objective() -> String:
	return String(active.get("objective", ""))

## Every authored beat is a playable decision, not a collectible paragraph.
## The choice vocabulary is deliberately small so the Chronicle remains the
## game's true authored state: what matters is what the settlement chose to do.
func _choices_for(beat: Dictionary) -> Array[Dictionary]:
	var chapter := int(beat.get("chapter", 0))
	# Not every page of the Chronicle is a branching quest. Some pages are
	# witness scenes: the player is required to see the place and understand
	# what it means before the next physical decision exists. This keeps the
	# story from turning every paragraph into an arbitrary morality button.
	if chapter in [3, 4, 5, 7, 8, 9, 10, 13, 17, 21, 24, 29, 30, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42]:
		if chapter == 29:
			return [
				_choice("Conscript Asha", "villager_conscripted", "Asha Vane"),
				_choice("Leave the rota short", "vigil_skipped", "the wedding day"),
			]
		return []
	if chapter == 6:
		return [
			_choice("Bury her whole", "vigil_held", "Burial"),
			_choice("Keep working", "vigil_skipped", "Oda Ashfall"),
		]
	if chapter == 12:
		return [
			_choice("Reclaim Rin", "echo_reclaimed", "Rin Ashfall"),
			_choice("Leave Rin in the field", "echo_abandoned", "Rin Ashfall"),
		]
	if chapter == 14 or chapter == 25:
		return [
			_choice("Speak the names", "vigil_held", "a Telling"),
			_choice("Let the names go quiet", "vigil_skipped", "the Memorial"),
		]
	if chapter == 16 or chapter == 22:
		return [
			_choice("Keep the sick", "enemy_spared", "Brackwood sick"),
			_choice("Cull the sick", "enemy_slain", "Brackwood sick"),
			_choice("Open the gate and risk the Hold", "enemy_spared", "the quarantine"),
		]
	if chapter == 18 or chapter == 23:
		return [
			_choice("Listen to the Gravewarden", "enemy_spared", "Halde, a Gravewarden"),
			_choice("Put it down", "enemy_slain", "Halde, a Gravewarden"),
		]
	if chapter == 19 or chapter == 34:
		return [
			_choice("Hold the Pyre", "vigil_held", "Pyre"),
			_choice("Keep the gear", "vigil_skipped", "Bel Brack"),
		]
	if chapter == 20:
		return [
			_choice("Go into Low Kettle", "echo_reclaimed", "Bel Kettle"),
			_choice("Leave the water untouched", "echo_abandoned", "Bel Kettle"),
		]
	if chapter == 26:
		return [
			_choice("Lift Tove", "ally_revived", "Tove Rowan"),
			_choice("Leave her in the grass", "ally_abandoned", "Tove Rowan"),
		]
	if chapter == 27 or chapter == 41:
		return [
			_choice("Honour the stranger", "foreign_echo_honoured", String(beat.get("place", "the stranger's Echo"))),
			_choice("Put the stranger down", "foreign_echo_slain", String(beat.get("place", "the stranger's Echo"))),
			_choice("Send the Echo onward", "echo_sent", String(beat.get("place", "the road"))),
		]
	if chapter == 28:
		var can_spend_relic := int(WorldState.materials.get("relic", 0)) > 0
		return [
			_choice("Spend the relic on stone", "relic_spent", "the Brackwood Monument", can_spend_relic),
			_choice("Bind the relic into the Pike", "relic_spent", "the Reaper Pike", can_spend_relic),
			_choice("Wait for another relic", "echo_abandoned", "Maren Verren"),
		]
	if chapter == 31:
		return [
			_choice("Let the Yielding walk north", "enemy_spared", "the Yielding"),
			_choice("Stop them", "villager_conscripted", "the Ash Orchard walkers"),
		]
	if chapter == 32:
		return [
			_choice("Reclaim Yeva's Echo", "echo_reclaimed", "Yeva Holt"),
			_choice("Leave it outside", "echo_abandoned", "Yeva Holt"),
			_choice("Let the Echo into the Hold", "echo_raided", "Yeva Holt"),
		]
	if chapter == 43:
		return [
			_choice("Hold the Wake", "vigil_held", "Wake"),
			_choice("Do not spend the Hold", "vigil_skipped", "Wake"),
		]
	var title := String(beat.get("title", "")).to_lower()
	var text := String(beat.get("text", "")).to_lower()
	var result: Array[Dictionary] = []
	if "stranger" in title or "stranger" in text or "open road" in text:
		result = [
			_choice("Honour the hold", "foreign_echo_honoured", String(beat["place"])),
			_choice("End it here", "foreign_echo_slain", String(beat["place"])),
			_choice("Send it onward", "echo_sent", String(beat["place"])),
		]
	elif "cull" in title or "sickness" in text or "doctrine" in title:
		result = [
			_choice("Keep the gate open", "enemy_spared", String(beat["place"])),
			_choice("Cull the threat", "enemy_slain", String(beat["place"])),
			_choice("Conscript the living", "villager_conscripted", String(beat["place"])),
		]
	elif "echo" in title or "reclaim" in title or "raid" in title or "dead" in text:
		result = [
			_choice("Reclaim what remains", "echo_reclaimed", String(beat["title"])),
			_choice("Leave it to the field", "echo_abandoned", String(beat["title"])),
			_choice("Put the dead down", "enemy_slain", String(beat["title"])),
		]
	elif "gone" in title or "pushing back" in title or "decay" in text or "ash" in title:
		result = [
			_choice("Push the Grey back", "region_saved", String(beat["place"])),
			_choice("Accept what is lost", "region_lost", String(beat["place"])),
			_choice("Remember it before it goes", "vigil_held", String(beat["title"])),
		]
	elif "vigil" in title or "wake" in title or "memorial" in title or "telling" in text:
		result = [
			_choice("Speak the name", "vigil_held", String(beat["title"])),
			_choice("Keep working", "vigil_skipped", String(beat["title"])),
			_choice("Give the dead to stone", "relic_spent", String(beat["title"])),
		]
	else:
		result = [
			_choice("Carry the memory", "vigil_held", String(beat["title"])),
			_choice("Choose the living", "successor_taken", String(beat["title"])),
			_choice("Hold the line", "enemy_slain", String(beat["title"])),
		]
	return result

func _choice(label: String, action: String, subject: String, available: bool = true) -> Dictionary:
	var ready := available
	if action == "vigil_held" and int(active.get("day", 0)) != 210:
		var vigil_id := _vigil_id_for_subject(subject)
		if vigil_id != "":
			ready = ready and WorldState.can_perform_vigil(vigil_id)
	return {"label": label, "action": action, "subject": subject, "available": ready}

func _vigil_id_for_subject(subject: String) -> String:
	var text := subject.to_lower()
	if "burial" in text:
		return "burial"
	if "pyre" in text:
		return "pyre"
	if "telling" in text or "name" in text:
		return "telling"
	if "monument" in text or "stone" in text:
		return "monument"
	if "wake" in text:
		return "wake"
	return ""

func resolve_choice(index: int) -> bool:
	if active.is_empty() or choice_taken or index < 0 or index >= choices.size():
		return false
	var choice := choices[index].duplicate(true)
	if not bool(choice.get("available", true)):
		return false
	if not _apply_choice_consequence(choice):
		return false
	var entry := Chronicle.record(String(choice["action"]), String(choice["subject"]))
	if entry.is_empty():
		return false
	choice_taken = true
	choice["entry"] = entry
	choice_resolved.emit(choice, active)
	return true

## Story decisions are allowed to change the simulation. They never replace
## simulation with flags: a decision either changes a real state or is purely
## Chronicle testimony when the corresponding physical act belongs in the field.
func _apply_choice_consequence(choice: Dictionary) -> bool:
	var action := String(choice.get("action", ""))
	var subject := String(choice.get("subject", ""))
	var chapter := int(active.get("chapter", 0))
	if int(active.get("day", 0)) == 210 and action == "vigil_held":
		# The first book closes at the Memorial. Any remaining local Echo is
		# acknowledged here, so the Wake gate is earned by the final rite rather
		# than by silently deleting unfinished consequence.
		var remaining := WorldState.echoes.duplicate(true)
		for echo: Dictionary in remaining:
			WorldState.reclaim_echo(String(echo.get("id", "")))
		if not WorldState.perform_vigil("wake"):
			return false
		# Wake is the terminal rite. Do not fall through into the generic
		# `vigil_held` branch below and attempt to spend the same grief twice.
		WorldState.faction_delta("tellers", 5)
		WorldState.faction_delta("unnaming", -4)
		return true
	match action:
		"region_saved":
			var region := _region_for_place(String(active.get("place", "")))
			if region != "":
				WorldState.restore_region(region)
		"region_lost":
			var region := _region_for_place(String(active.get("place", "")))
			if region != "":
				WorldState._decay_region(region, 1)
		"villager_conscripted":
			var pool := WorldState.living_villagers()
			pool.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
				return int(a.get("vigour", 0)) < int(b.get("vigour", 0)))
			for person: Dictionary in pool:
				if not bool(person.get("is_wielder", false)) and WorldState.conscript_villager(String(person["id"])):
					break
		"enemy_spared":
			WorldState.faction_delta("hearthkeepers", 3)
			WorldState.faction_delta("cull", -3)
		"enemy_slain":
			WorldState.faction_delta("cull", 3)
			WorldState.faction_delta("hearthkeepers", -2)
		"foreign_echo_honoured":
			WorldState.faction_delta("open_road", 6)
			WorldState.faction_delta("tellers", 2)
		"foreign_echo_slain":
			WorldState.faction_delta("open_road", -5)
			WorldState.faction_delta("cull", 4)
		"echo_sent":
			WorldState.faction_delta("open_road", 8)
			WorldState.faction_delta("long_hold", -4)
		"vigil_held":
			var vigil_id := _vigil_id_for_subject(subject)
			if vigil_id != "":
				if not WorldState.perform_vigil(vigil_id):
					return false
			WorldState.faction_delta("tellers", 5)
			WorldState.faction_delta("unnaming", -4)
		"vigil_skipped":
			WorldState.faction_delta("unnaming", 5)
			WorldState.faction_delta("tellers", -3)
		"echo_reclaimed":
			WorldState.faction_delta("tellers", 3)
			WorldState.faction_delta("cull", 2)
		"echo_abandoned":
			WorldState.faction_delta("unnaming", 4)
			WorldState.faction_delta("yielding", 2)
		"relic_spent":
			if int(WorldState.materials.get("relic", 0)) <= 0:
				return false
			WorldState.materials["relic"] = int(WorldState.materials["relic"]) - 1
			if "pike" in subject.to_lower() or "steel" in subject.to_lower():
				var weapon_id := String(WorldState.wielder().get("weapon", "ashblade"))
				WorldState.weapon_upgrades[weapon_id] = float(WorldState.weapon_upgrades.get(weapon_id, 0.0)) + 0.04
			elif "stone" in subject.to_lower() or "monument" in subject.to_lower():
				WorldState.legacies.append({"kind": "max_hp", "value": 4.0, "from": "Relic monument"})
			WorldState.faction_delta("tellers", 4)
		"successor_taken":
			var candidates := WorldState.succession_candidates()
			if not candidates.is_empty():
				WorldState.choose_successor(String(candidates[0]["id"]))
	# Story beats that are themselves decisions only become physically complete
	# when their consequence was recorded. Witness beats use these same events
	# so authored prose and simulation remain coupled without inventing flags.
	match chapter:
		6: notify_event("first_vigil" if action == "vigil_held" else "first_death")
		16, 22: notify_event("brackwood_decision")
		18, 23: notify_event("gravewarden_encounter")
		25: notify_event("doctrine_decision")
		27: notify_event("foreign_echo_seen")
		28: notify_event("relic_decision")
		29: notify_event("wedding_decision")
		31: notify_event("ash_orchard_entered")
		32: notify_event("yeva_raid")
		33: notify_event("carver_glass")
		34: notify_event("flask_used")
		40: notify_event("region_saved" if action == "region_saved" else "region_lost")
		41: notify_event("two_boards")
		_: pass
	return true

func _region_for_place(place: String) -> String:
	var p := place.to_lower()
	if "wrenfield" in p or "field" in p:
		return "wrenfield"
	if "grey ash" in p or "ash" in p:
		return "grey_ash"
	if "stonewake" in p or "scarp" in p:
		return "stonewake"
	if "kettle" in p or "mere" in p:
		return "kettlemere"
	if "brackwood" in p:
		return "brackwood"
	if "vane" in p or "road" in p:
		return "vane_road"
	return ""

func is_story_complete() -> bool:
	# Reaching the final page is not the same as completing its rite. Keep the
	# endpoint active until the player has resolved and dismissed the day-210
	# handoff, otherwise the second-book successor would never be committed.
	return _is_witnessed(BEATS[-1]) and active.is_empty()

## Days are not unique identifiers. Several Chronicle pages happen on the same
## day, and collapsing them to the calendar day silently skipped authored
## scenes. The chapter/day key is stable, human-readable save data and also
## keeps old saves useful by accepting the legacy day-only key when it is
## unambiguous.
func _beat_key(beat: Dictionary) -> String:
	return "chapter_%d_day_%d" % [int(beat.get("chapter", 0)), int(beat.get("day", 0))]

func _is_witnessed(beat: Dictionary) -> bool:
	if witnessed.has(_beat_key(beat)):
		return true
	# Preserve old saves for days that occurred only once in the authored list.
	var day := int(beat.get("day", 0))
	var count := 0
	for candidate: Dictionary in BEATS:
		if int(candidate.get("day", -1)) == day:
			count += 1
	return count == 1 and witnessed.has(str(day))
