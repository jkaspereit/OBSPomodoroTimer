import obspython as obs
import time
import math

start_time = time.time()
source_name = ""
interval_s = 0
interval_b = 0
current_interval = 0

def update_text():
	global source_name

	source = obs.obs_get_source_by_name(source_name)
	if source is not None:
		time_passed = time.time() - start_time

		if time_passed > (current_interval * 60):
			timer_text = "00:00"
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
			obs.timer_remove(update_text)
			obs.timer_add(update_text, 10)

def start_timer():
	global start_time
	start_time = time.time()
	update_text()

def start_session_pressed(props, prop):
	global interval_s
	global current_interval

	current_interval = interval_s
	start_timer()

def start_break_pressed(props, prop):
	global interval_b
	global current_interval

	current_interval = interval_b
	start_timer()

def script_description():
	return "A simple Pomodoro Timer for OBS.\n\nBy Jonas Kaspereit"

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_int(props, "interval session", "Session Interval", 0, 99, 1)
	obs.obs_properties_add_int(props, "interval break", "Break Interval", 0, 99, 1)

	p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			source_id = obs.obs_source_get_unversioned_id(source)
			if source_id == "text_gdiplus" or source_id == "text_ft2_source":
				name = obs.obs_source_get_name(source)
				obs.obs_property_list_add_string(p, name, name)
		obs.source_list_release(sources)

	obs.obs_properties_add_button(props, "start session button", "Start Session", start_session_pressed)
	obs.obs_properties_add_button(props, "start break button", "Start Break", start_break_pressed)
	return props

def script_update(settings):
	global source_name
	global interval_s
	global interval_b

	source_name = obs.obs_data_get_string(settings, "source")
	interval_s = obs.obs_data_get_int(settings, "interval session")
	interval_b = obs.obs_data_get_int(settings, "interval break")