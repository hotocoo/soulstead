class_name EchoActor
extends EnemyActor
## Your own corpse, still swinging.
##
## An Echo carries the dead wielder's weapon and power. Left alone it tiers up
## on the world clock, roams, and eventually raids the settlement. Defeating it
## reclaims the loadout and releases the grief it holds. Drifted Echoes from
## other players' settlements use the same body with a cold rim light.

signal reclaimed(echo_data: Dictionary)

const TIER_HEALTH := 34.0
const TIER_DAMAGE := 4.0
const TIER_SPEED := 0.35

var echo_data: Dictionary = {}
var is_foreign: bool = false

func from_echo(data: Dictionary, decay: int = 0) -> void:
	echo_data = data
	is_foreign = bool(data.get("foreign", false))
	var tier: int = int(data.get("tier", 1))
	var weapon: Dictionary = Codex.weapon(String(data.get("weapon", "ashblade")))
	configure("warden", decay)
	display_name = "Echo of %s" % String(data.get("owner", "someone"))
	if is_foreign:
		display_name += " (%s)" % String(data.get("from_settlement", "elsewhere"))
	max_health = 70.0 + TIER_HEALTH * tier
	health = max_health
	max_poise = 40.0 + 8.0 * tier
	poise = max_poise
	damage = float(weapon["power"]) * float(data.get("power", 1.0)) * 0.6 + TIER_DAMAGE * tier
	move_speed = 2.3 + TIER_SPEED * tier
	reach = float(weapon["reach"])
	tell_time = maxf(0.16, float(weapon["heavy"]["startup"]) - 0.02 * tier)
	posture = "bulwark" if tier >= 3 else "shambler"
	set_visual(Look.echo_figure(Look.COLD if is_foreign else Look.EMBER,
			1.0 + 0.06 * tier))

func _physics_process(delta: float) -> void:
	# A local Echo carries an aura of the dead person's hold. A Rival successor
	# is canonically untouched by it, while everyone else feels the pressure as
	# a small, readable Composure drain rather than hidden damage.
	var wielder := get_tree().get_first_node_in_group("player") as PlayerActor
	if wielder != null and is_alive() and not is_foreign:
		var bond := String(WorldState.wielder().get("bond_to_dead", "stranger"))
		if bond != "rival" and global_position.distance_to(wielder.global_position) < 5.0:
			wielder.composure = maxf(0.0, wielder.composure - 4.0 * delta)
			wielder.composure_changed.emit(wielder.composure, wielder.max_composure)
	super(delta)

func die() -> void:
	if state == State.DEAD:
		return
	reclaimed.emit(echo_data)
	super()
