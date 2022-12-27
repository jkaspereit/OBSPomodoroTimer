import obspython as obs
import time
import math

start_time = time.time()
source_name_timer = ""
source_name_state = ""
source_name_session = ""
state = ""
interval_s = 0
interval_b = 0
current_interval = 0
sessions = 0
current_session = 0
auto_play = False

def update_text_timer():
	global interval_s
	global interval_b
	global source_name_timer
	global state
	global current_session

	obs.timer_remove(update_text_timer)

	source = obs.obs_get_source_by_name(source_name_timer)
	if source is not None:
		time_passed = time.time() - start_time

		if time_passed > (current_interval * 60):
			timer_text = "00:00"
			if state == "Session":
				current_session += 1
				update_text_session()
			if auto_play:
				if current_interval == interval_s:
					start_break_pressed(None, None)
					return
				else:
					start_session_pressed(None, None)
					return
		else: 
			minutes_left = math.ceil(current_interval - 1 - time_passed / 60)
			seconds_left = (int) (60 - (time_passed % 60))
			timer_text = "{:02.0f}:{:02d}".format(minutes_left, seconds_left)
		
		settings = obs.obs_data_create()
		obs.obs_data_set_string(
            settings, "text", timer_text
        )
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)
		obs.obs_source_release(source)

		# interval done, stop updating text
		if not time_passed > (current_interval * 60):
			obs.timer_add(update_text_timer, 10)

def update_text_session():
	global source_name_session
	global current_session
	global sessions

	source = obs.obs_get_source_by_name(source_name_session)
	if source is not None:
		settings = obs.obs_data_create()
		obs.obs_data_set_string(
            settings, "text", "Session {}|{}".format(current_session,sessions)
        )
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)
		obs.obs_source_release(source)

def update_text_state():
	global source_name_state
	global state

	source = obs.obs_get_source_by_name(source_name_state)
	if source is not None:
		settings = obs.obs_data_create()
		obs.obs_data_set_string(
            settings, "text", state
        )
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)
		obs.obs_source_release(source)

def start_timer():
	global start_time
	start_time = time.time()
	update_text_state()
	update_text_timer()

def start_session_pressed(props, prop):
	global state
	global interval_s
	global current_interval

	state = "Session"
	current_interval = interval_s
	start_timer()

def start_break_pressed(props, prop):
	global state
	global interval_b
	global current_interval

	state = "Break"
	current_interval = interval_b
	start_timer()

def auto_play_pressed(props, prop):
	global auto_play

	auto_play = not auto_play
	if auto_play:
		start_session_pressed(props, prop)

def script_description():
	return "A simple Pomodoro Timer for OBS.\n\nBy Jonas Kaspereit"

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_int(props, "interval session", "Session Interval", 0, 99, 1)
	obs.obs_properties_add_int(props, "interval break", "Break Interval", 0, 99, 1)
	obs.obs_properties_add_int(props, "sessions", "Sessions", 0, 24, 1)

	add_source(props, "timer source", "Timer Source")
	add_source(props, "state source", "State Source")
	add_source(props, "session source", "Session Source")

	obs.obs_properties_add_button(props, "start session button", "Start Session", start_session_pressed)
	obs.obs_properties_add_button(props, "start break button", "Start Break", start_break_pressed)
	obs.obs_properties_add_button(props, "auto play button", "Auto Play", auto_play_pressed)
	return props

def script_update(settings):
	global source_name_timer
	global source_name_state
	global source_name_session
	global interval_s
	global interval_b
	global sessions

	source_name_timer = obs.obs_data_get_string(settings, "timer source")
	source_name_state = obs.obs_data_get_string(settings, "state source")
	source_name_session = obs.obs_data_get_string(settings, "session source")
	interval_s = obs.obs_data_get_int(settings, "interval session")
	interval_b = obs.obs_data_get_int(settings, "interval break")
	sessions = obs.obs_data_get_int(settings, "sessions")
	update_text_session()

def add_source(props, id, name):
	p = obs.obs_properties_add_list(props, id, name, obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			source_id = obs.obs_source_get_unversioned_id(source)
			if source_id == "text_gdiplus" or source_id == "text_ft2_source":
				name = obs.obs_source_get_name(source)
				obs.obs_property_list_add_string(p, name, name)

		obs.source_list_release(sources)