import os, sys
from os.path import join, exists, isdir, isfile, dirname, abspath, expanduser

import xdg.BaseDirectory
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gdk, Gio

# Autotools set the actual data_dir in defs.py
from .defs import VERSION, DATA_DIR

# Allow to use uninstalled glipper ---------------------------------------------
UNINSTALLED_GLIPPER = False
if '_GLIPPER_UNINSTALLED' in os.environ:
	UNINSTALLED_GLIPPER = True
	print("Running glipper uninstalled")

# Sets SHARED_DATA_DIR to local copy, or the system location
# Shared data dir is most the time /usr/share/glipper
if UNINSTALLED_GLIPPER:
	SHARED_DATA_DIR = abspath(join(dirname(__file__), '..', 'data'))
	try:
		file_ = open('.bzr/branch/last-revision')
		string = file_.read()
		file_.close()
	except IOError:
		pass
	else:
		revision = string.split()[0]
		VERSION += "-r%s (bzr)" % revision
else:
	SHARED_DATA_DIR = join(DATA_DIR, "glipper")
print("SHARED_DATA_DIR: %s" % SHARED_DATA_DIR)


# check if it exists first, because save_data_path() creates the folder
xdg_dir_existed = exists(join(xdg.BaseDirectory.xdg_data_home, 'glipper'))
try:
	USER_GLIPPER_DIR = xdg.BaseDirectory.save_data_path('glipper')
except OSError as e:
	print('Error: could not create user glipper dir (%s): %s' % (join(xdg.BaseDirectory.xdg_data_home, 'glipper'), e))
	sys.exit(1)

if exists(expanduser("~/.glipper")) and not xdg_dir_existed:
	# first run for new directory; move old ~/.glipper
	try:
		os.rename(expanduser("~/.glipper"), USER_GLIPPER_DIR)
	except OSError:
		# folder must already have some files in it
		# (race condition with xdg_dir_existed check)
		pass

# ------------------------------------------------------------------------------

# Path to plugins
if UNINSTALLED_GLIPPER:
	PLUGINS_DIR = join(dirname(__file__), 'plugins')
else:
	PLUGINS_DIR = join(SHARED_DATA_DIR, 'plugins')

# Path to plugins save directory
USER_PLUGINS_DIR = xdg.BaseDirectory.save_data_path('glipper', 'plugins')

# Path to history file
HISTORY_FILE = join(USER_GLIPPER_DIR, "history")

# Maximum length constant for tooltips item in the history
MAX_TOOLTIPS_LENGTH = 11347

#Gio settings
if UNINSTALLED_GLIPPER:
	schemaSource = Gio.SettingsSchemaSource.new_from_directory(SHARED_DATA_DIR, None, False)
	schema = schemaSource.lookup("net.launchpad.Glipper", False)
	GSETTINGS = Gio.Settings.new_full(schema, None, None)
else:
	GSETTINGS = Gio.Settings("net.launchpad.Glipper")

# GSettings key to the setting for the amount of elements in history
GSETTINGS_MAX_ELEMENTS = "max-elements"

# GSettings key to the setting for the length of one history item
GSETTINGS_MAX_ITEM_LENGTH = "max-item-length"

# GSettings key to the setting for the key combination to popup glipper
GSETTINGS_KEY_COMBINATION = "key-combination"

# GSettings key to the setting for using the default clipboard
GSETTINGS_USE_DEFAULT_CLIPBOARD = "use-default-clipboard"

# GSettings key to the setting for using the primary clipboard
GSETTINGS_USE_PRIMARY_CLIPBOARD = "use-primary-clipboard"

# GSettings key to the setting for whether the default entry should be marked in bold
GSETTINGS_MARK_DEFAULT_ENTRY = "mark-default-entry"

# GSettings key to the setting for whether the history should be saved
GSETTINGS_SAVE_HISTORY = "save-history"

GSETTINGS_AUTOSTART_PLUGINS = "autostart-plugins"

# Migrate settings from GConf
if GSETTINGS.get_boolean("migrate-from-gconf"):
	from glipper.Migration import migrate_settings_from_gconf
	migrate_settings_from_gconf()
	GSETTINGS.set_boolean("migrate-from-gconf", False)

# Functions callable by plugins

from glipper.History import *
from glipper.Clipboards import *
from glipper.PluginsManager import *

import glipper.AppIndicator

def add_menu_item(menu_item):
	get_glipper_plugins_manager().add_menu_item(menu_item)

def add_history_item(item):
	get_glipper_clipboards().set_text(item)

def set_history_item(index, item):
	get_glipper_history().set(index, item)

def get_history_item(index):
	return get_glipper_history().get(index)

def remove_history_item(index):
	return get_glipper_history().remove(index)

def clear_history():
	return get_glipper_history().clear()

def format_item(item):
	return glipper.AppIndicator.format_item(item)
