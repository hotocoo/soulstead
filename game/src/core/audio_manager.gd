extends Node
## Procedural audio system. Generates sound effects in real-time using
## AudioStreamGenerator - no audio files needed.

var _master: AudioStreamPlayer
var _hit_stream: AudioStreamGenerator
var _dodge_stream: AudioStreamGenerator
var _death_stream: AudioStreamGenerator
var _pickup_stream: AudioStreamGenerator

func _ready() -> void:
	_master = AudioStreamPlayer.new()
	_master.bus = "Master"
	add_child(_master)
	_build_streams()

func _build_streams() -> void:
	_hit_stream = _make_stream(44100, 0.15)
	_dodge_stream = _make_stream(44100, 0.10)
	_death_stream = _make_stream(44100, 0.40)
	_pickup_stream = _make_stream(44100, 0.12)

func _make_stream(sample_rate: int, duration: float) -> AudioStreamGenerator:
	var stream := AudioStreamGenerator.new()
	stream.format = AudioStreamGenerator.FORMAT_16_BITS
	stream.channels = 1
	stream.sample_rate = sample_rate
	stream.buffer_length = duration
	return stream

func play_hit() -> void:
	_fill_stream(_hit_stream, _hit_buffer)
	_play(_hit_stream)

func play_dodge() -> void:
	_fill_stream(_dodge_stream, _dodge_buffer)
	_play(_dodge_stream)

func play_death() -> void:
	_fill_stream(_death_stream, _death_buffer)
	_play(_death_stream)

func play_pickup() -> void:
	_fill_stream(_pickup_stream, _pickup_buffer)
	_play(_pickup_stream)

func play_flask() -> void:
	_fill_stream(_pickup_stream, _flask_buffer)
	_play(_pickup_stream)

func play_ui_click() -> void:
	_fill_stream(_pickup_stream, _ui_click_buffer)
	_play(_pickup_stream)

func play_ui_select() -> void:
	_fill_stream(_pickup_stream, _ui_select_buffer)
	_play(_pickup_stream)

func play_step() -> void:
	_fill_stream(_dodge_stream, _step_buffer)
	_play(_dodge_stream)

func play_return() -> void:
	_fill_stream(_death_stream, _return_buffer)
	_play(_death_stream)

func _play(stream: AudioStreamGenerator) -> void:
	_master.stream = stream
	_master.play()

func _fill_stream(stream: AudioStreamGenerator, buffer: Callable) -> void:
	var samples := stream.get_buffer_size()
	var data := PackedInt16Array()
	data.resize(samples)
	for i in samples:
		data[i] = buffer.call(float(i) / float(samples), float(i) / float(stream.sample_rate))
	stream.push_data(data)

# Sound buffers - procedural waveforms
func _hit_buffer(t: float, time: float) -> int:
	# Metallic clang: decaying sine with harmonics
	var env = exp(-t * 12.0)
	var wave = sin(time * 800.0 * TAU) * 0.5 + sin(time * 1200.0 * TAU) * 0.3 + sin(time * 2400.0 * TAU) * 0.2
	return int(wave * env * 15000)

func _dodge_buffer(t: float, time: float) -> int:
	# Whoosh: filtered noise
	var env = sin(t * PI)
	var noise = sin(time * 2000.0 * TAU) * sin(time * 137.0 * TAU)
	return int(noise * env * 8000)

func _death_buffer(t: float, time: float) -> int:
	# Deep thud: low sine with decay
	var env = exp(-t * 4.0)
	var wave = sin(time * 120.0 * TAU) * 0.7 + sin(time * 60.0 * TAU) * 0.3
	return int(wave * env * 20000)

func _pickup_buffer(t: float, time: float) -> int:
	# Bright chime: high sine
	var env = exp(-t * 8.0)
	var wave = sin(time * 1500.0 * TAU)
	return int(wave * env * 12000)

func _ui_click_buffer(t: float, time: float) -> int:
	# UI click: short high-pitched blip
	var env = exp(-t * 40.0)
	var wave = sin(time * 800.0 * TAU)
	return int(wave * env * 8000)

func _ui_select_buffer(t: float, time: float) -> int:
	# UI select: slightly longer, higher-pitched blip
	var env = exp(-t * 20.0)
	var wave = sin(time * 1200.0 * TAU)
	return int(wave * env * 8000)

func _flask_buffer(t: float, time: float) -> int:
	# Liquid sound: modulated sine
	var env = exp(-t * 6.0)
	var wave = sin(time * 400.0 * TAU + sin(time * 20.0 * TAU) * 3.0)
	return int(wave * env * 10000)

func _step_buffer(t: float, time: float) -> int:
	# Footstep: short thump
	var env = exp(-t * 20.0)
	var wave = sin(time * 200.0 * TAU)
	return int(wave * env * 6000)

func _return_buffer(t: float, time: float) -> int:
	# Triumphant chord: three sines
	var env = exp(-t * 2.0)
	var wave = sin(time * 440.0 * TAU) * 0.4 + sin(time * 550.0 * TAU) * 0.3 + sin(time * 660.0 * TAU) * 0.2
	return int(wave * env * 15000)
