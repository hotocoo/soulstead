class_name UiTheme
extends RefCounted
## Shared look for every panel, label and bar. One place to retune the game's
## visual language.

const INK := Color("#f4ece1")
const INK_DIM := Color("#a89e92")
const ACCENT := Color("#e0623f")
const PANEL_BG := Color(0.07, 0.06, 0.09, 0.94)
const PANEL_EDGE := Color("#6d5f54")
const HP_COLOR := Color("#5fae86")
const MP_COLOR := Color("#6f8fd6")
const SELECT_BG := Color(0.88, 0.38, 0.25, 0.25)

static func panel(margin: int = 6) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = PANEL_BG
	style.border_color = PANEL_EDGE
	style.set_border_width_all(1)
	style.set_corner_radius_all(3)
	style.content_margin_left = margin
	style.content_margin_right = margin
	style.content_margin_top = margin
	style.content_margin_bottom = margin
	return style

static func make_panel(margin: int = 6) -> PanelContainer:
	var node := PanelContainer.new()
	node.add_theme_stylebox_override("panel", panel(margin))
	return node

static func label(text: String, size: int = 8, color: Color = INK) -> Label:
	var node := Label.new()
	node.text = text
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", color)
	node.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	node.add_theme_constant_override("shadow_offset_y", 1)
	return node

static func bar(color: Color, width: int = 46) -> ProgressBar:
	var node := ProgressBar.new()
	node.show_percentage = false
	node.custom_minimum_size = Vector2(width, 4)
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0, 0, 0, 0.55)
	bg.set_corner_radius_all(2)
	var fill := StyleBoxFlat.new()
	fill.bg_color = color
	fill.set_corner_radius_all(2)
	node.add_theme_stylebox_override("background", bg)
	node.add_theme_stylebox_override("fill", fill)
	return node

## Highlight strip used by every cursor-driven list in the game.
static func selection_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = SELECT_BG
	style.border_color = ACCENT
	style.border_width_left = 2
	style.set_corner_radius_all(2)
	style.content_margin_left = 4
	style.content_margin_right = 4
	style.content_margin_top = 1
	style.content_margin_bottom = 1
	return style
