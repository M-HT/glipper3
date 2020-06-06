import glipper

def migrate_settings_from_gconf():
	try:
		import gi
		gi.require_version('GConf', '2.0')
		from gi.repository import GConf

		#Gconf client
		GCONF_CLIENT = GConf.Client.get_default()

		# GConf directory for deskbar in window mode and shared settings
		GCONF_DIR = "/apps/glipper"

		# GConf key to the setting for the amount of elements in history
		GCONF_MAX_ELEMENTS = GCONF_DIR + "/max_elements"

		# GConf key to the setting for the length of one history item
		GCONF_MAX_ITEM_LENGTH = GCONF_DIR + "/max_item_length"

		# GConf key to the setting for the key combination to popup glipper
		GCONF_KEY_COMBINATION = GCONF_DIR + "/key_combination"

		# GConf key to the setting for using the default clipboard
		GCONF_USE_DEFAULT_CLIPBOARD = GCONF_DIR + "/use_default_clipboard"

		# GConf key to the setting for using the primary clipboard
		GCONF_USE_PRIMARY_CLIPBOARD = GCONF_DIR + "/use_primary_clipboard"

		# GConf key to the setting for whether the default entry should be marked in bold
		GCONF_MARK_DEFAULT_ENTRY = GCONF_DIR + "/mark_default_entry"

		# GConf key to the setting for whether the history should be saved
		GCONF_SAVE_HISTORY = GCONF_DIR + "/save_history"

		GCONF_AUTOSTART_PLUGINS = GCONF_DIR + "/autostart_plugins"

		# Preload GConf directories
		GCONF_CLIENT.add_dir(GCONF_DIR, GConf.ClientPreloadType.PRELOAD_RECURSIVE)

		def get_list_str(val):
			if val is None:
				return None
			_list = val.get_list()
			if _list is None:
				return None
			return [x.get_string() for x in _list]

		max_elements = GCONF_CLIENT.get_int(GCONF_MAX_ELEMENTS)
		max_item_length = GCONF_CLIENT.get_int(GCONF_MAX_ITEM_LENGTH)
		key_combination = GCONF_CLIENT.get_string(GCONF_KEY_COMBINATION)
		use_default_clipboard = GCONF_CLIENT.get_bool(GCONF_USE_DEFAULT_CLIPBOARD)
		use_primary_clipboard = GCONF_CLIENT.get_bool(GCONF_USE_PRIMARY_CLIPBOARD)
		mark_default_entry = GCONF_CLIENT.get_bool(GCONF_MARK_DEFAULT_ENTRY)
		save_history = GCONF_CLIENT.get_bool(GCONF_SAVE_HISTORY)
		autostart_plugins = get_list_str(GCONF_CLIENT.get(GCONF_AUTOSTART_PLUGINS))

		if max_elements != GCONF_CLIENT.get_default_from_schema(GCONF_MAX_ELEMENTS).get_int():
			glipper.GSETTINGS.set_int(glipper.GSETTINGS_MAX_ELEMENTS, max_elements)

		if max_item_length != GCONF_CLIENT.get_default_from_schema(GCONF_MAX_ITEM_LENGTH).get_int():
			glipper.GSETTINGS.set_int(glipper.GSETTINGS_MAX_ITEM_LENGTH, max_item_length)

		if key_combination != GCONF_CLIENT.get_default_from_schema(GCONF_KEY_COMBINATION).get_string():
			glipper.GSETTINGS.set_string(glipper.GSETTINGS_KEY_COMBINATION, key_combination)

		if use_default_clipboard != GCONF_CLIENT.get_default_from_schema(GCONF_USE_DEFAULT_CLIPBOARD).get_bool():
			glipper.GSETTINGS.set_boolean(glipper.GSETTINGS_USE_DEFAULT_CLIPBOARD, use_default_clipboard)

		if use_primary_clipboard != GCONF_CLIENT.get_default_from_schema(GCONF_USE_PRIMARY_CLIPBOARD).get_bool():
			glipper.GSETTINGS.set_boolean(glipper.GSETTINGS_USE_PRIMARY_CLIPBOARD, use_primary_clipboard)

		if mark_default_entry != GCONF_CLIENT.get_default_from_schema(GCONF_MARK_DEFAULT_ENTRY).get_bool():
			glipper.GSETTINGS.set_boolean(glipper.GSETTINGS_MARK_DEFAULT_ENTRY, mark_default_entry)

		if save_history != GCONF_CLIENT.get_default_from_schema(GCONF_SAVE_HISTORY).get_bool():
			glipper.GSETTINGS.set_boolean(glipper.GSETTINGS_SAVE_HISTORY, save_history)

		if sorted(autostart_plugins) != sorted(get_list_str(GCONF_CLIENT.get_default_from_schema(GCONF_AUTOSTART_PLUGINS))):
			glipper.GSETTINGS.set_strv(glipper.GSETTINGS_AUTOSTART_PLUGINS, autostart_plugins)

	except:
		pass
