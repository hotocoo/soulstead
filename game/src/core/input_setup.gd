extends Node
## Registers gameplay actions at runtime so project.godot stays readable.

const BINDINGS := {
	"move_up": [KEY_W, KEY_UP],
	"move_down": [KEY_S, KEY_DOWN],
	"move_left": [KEY_A, KEY_LEFT],
	"move_right": [KEY_D, KEY_RIGHT],
	"light_attack": [KEY_J],
	"heavy_attack": [KEY_K],
	"parry": [KEY_L],
	"guard": [KEY_I],
	"dodge": [KEY_SPACE],
	"sprint": [KEY_SHIFT],
	"interact": [KEY_E, KEY_ENTER],
	"flask": [KEY_Q],
	"cancel": [KEY_ESCAPE],
	"menu": [KEY_TAB],
	"confirm": [KEY_ENTER, KEY_E],
	"cycle_next": [KEY_D, KEY_RIGHT],
	"cycle_prev": [KEY_A, KEY_LEFT],
}

const MOUSE_BINDINGS := {
	"light_attack": [MOUSE_BUTTON_LEFT],
	"heavy_attack": [MOUSE_BUTTON_RIGHT],
}

func _enter_tree() -> void:
	for action: String in BINDINGS:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for keycode: int in BINDINGS[action]:
			var event := InputEventKey.new()
			event.physical_keycode = keycode
			InputMap.action_add_event(action, event)
	for action: String in MOUSE_BINDINGS:
		for button: int in MOUSE_BINDINGS[action]:
			var event := InputEventMouseButton.new()
			event.button_index = button
			InputMap.action_add_event(action, event)
