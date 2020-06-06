import os
from os.path import *
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gtk, Gdk
from gettext import gettext as _

import glipper, glipper.About, glipper.Preferences
from glipper.Keybinder import *
from glipper.History import *
from glipper.PluginsManager import *

class StatusIcon:
	def __init__(self):
		self.status_icon = Gtk.StatusIcon()
		self.status_icon.set_from_icon_name("glipper")
		self.status_icon.set_visible(True)
		self.status_icon.set_tooltip_text("Glipper")
		self.status_icon.connect('popup-menu', self.on_status_icon_popup_menu)
		self.status_icon.connect('button-press-event', self.on_status_icon_button_press)

	def on_status_icon_button_press(self, status_icon, event):
		self.menu.popup(None, None, Gtk.StatusIcon.position_menu, status_icon, event.button, event.time)

	def on_status_icon_popup_menu(self, status_icon, button_num, activate_time):
		# this will call Gtk.StatusIcon.position_menu(menu, status_icon) before displaying the menu
		self.menu.popup(None, None, Gtk.StatusIcon.position_menu, status_icon, button_num, activate_time)

	def set_menu(self, menu):
		self.menu = menu

class AppIndicator(object):
	def __init__(self):
		self.menu = Gtk.Menu()
		self._app_indicator = None
		self._status_icon = None

		try:
			gi.require_version('AppIndicator3', '0.1')
			from gi.repository import AppIndicator3
		except ValueError as ImportError:
			self._status_icon = StatusIcon()
			self._status_icon.set_menu(self.menu)
		else:
			self._app_indicator = AppIndicator3.Indicator.new("glipper", "glipper", AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
			self._app_indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
			self._app_indicator.set_menu(self.menu)
			self._app_indicator.set_title("Glipper")

		glipper.GSETTINGS.connect("changed::" + glipper.GSETTINGS_MARK_DEFAULT_ENTRY, lambda x, y, z=None: self.update_menu(get_glipper_history().get_history()))
		glipper.GSETTINGS.connect("changed::" + glipper.GSETTINGS_MAX_ITEM_LENGTH, lambda x, y, z=None: self.update_menu(get_glipper_history().get_history()))
		glipper.GSETTINGS.get_boolean(glipper.GSETTINGS_MARK_DEFAULT_ENTRY)
		glipper.GSETTINGS.get_int(glipper.GSETTINGS_MAX_ITEM_LENGTH)

		Gtk.Window.set_default_icon_name("glipper")

		get_glipper_keybinder().connect('activated', self.on_key_combination_press)
		get_glipper_keybinder().connect('changed', self.on_key_combination_changed)
		get_glipper_history().connect('changed', self.on_history_changed)
		get_glipper_plugins_manager().load()
		get_glipper_history().load()
		get_glipper_plugins_manager().connect('menu-items-changed', self.on_plugins_menu_items_changed)

	def on_plugins_menu_items_changed(self, manager):
		self.update_menu(get_glipper_history().get_history())

	def on_menu_item_activate(self, menuitem, item):
		get_glipper_clipboards().set_text(item)

	def on_clear(self, menuitem):
		get_glipper_history().clear()
		get_glipper_clipboards().clear_text()

	def update_menu(self, history):
		plugins_menu_items = get_glipper_plugins_manager().get_menu_items()

		for c in self.menu.get_children():
			self.menu.remove(c)

		if len(history) == 0:
			menu_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_STOP)
			menu_item.get_child().set_markup(_('<i>Empty history</i>'))
			menu_item.set_sensitive(False)
			self.menu.append(menu_item)
		else:
			for item in history:
				menu_item = Gtk.CheckMenuItem.new_with_label(format_item(item))
				menu_item.set_property('draw-as-radio', True)

				if len(item) > max_item_length :
					menu_item.set_tooltip_text(item[:glipper.MAX_TOOLTIPS_LENGTH])

				if mark_default_entry and item == get_glipper_clipboards().get_default_clipboard_text():
					menu_item.get_child().set_markup('<b>' + GObject.markup_escape_text(menu_item.get_child().get_text()) + '</b>')
					menu_item.set_property('active', True)
				else:
					menu_item.set_property('active', False)

				menu_item.connect('activate', self.on_menu_item_activate, item)
				self.menu.append(menu_item)

		self.menu.append(Gtk.SeparatorMenuItem())

		clear_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_CLEAR)
		clear_item.connect('activate', self.on_clear)
		self.menu.append(clear_item)

		if len(plugins_menu_items) > 0:
			self.menu.append(Gtk.SeparatorMenuItem())

			for module, menu_item in plugins_menu_items:
				self.menu.append(menu_item)

		preferences_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_PREFERENCES)
		preferences_item.connect('activate', self.on_preferences)
		help_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_HELP)
		help_item.connect('activate', self.on_help)
		about_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_ABOUT)
		about_item.connect('activate', self.on_about)
		plugins_item = Gtk.MenuItem.new_with_mnemonic(_("Pl_ugins"))
		plugins_item.connect('activate', self.on_plugins)

		self.menu.append(Gtk.SeparatorMenuItem())
		self.menu.append(preferences_item)
		# uncomment when installing of help files works correctly
		self.menu.append(help_item)
		self.menu.append(about_item)
		self.menu.append(plugins_item)

		self.menu.show_all()

	def on_preferences (self, component):
		glipper.Preferences.Preferences()

	def on_help (self, component):
		Gtk.show_uri(None, 'help:glipper', Gdk.CURRENT_TIME)

	def on_about (self, component):
		glipper.About.About()

	def on_plugins (self, component):
		PluginsWindow()

	def on_key_combination_press(self, widget, time):
		# todo: this doesn't work in gtk3
		self.menu.popup(None, None, None, None, 1, Gtk.get_current_event_time())

	def on_key_combination_changed(self, keybinder, success):
		if success:
			pass # update key combination tooltip when applicable

	def on_history_changed(self, history, history_list):
		self.update_menu(history_list)
		get_glipper_plugins_manager().call('on_history_changed')
		if save_history:
			history.save()

# These variables and functions are available for all Applet instances:

glipper.GSETTINGS.connect("changed::" + glipper.GSETTINGS_MARK_DEFAULT_ENTRY, lambda x, y, z=None: on_mark_default_entry_changed ())
mark_default_entry = glipper.GSETTINGS.get_boolean(glipper.GSETTINGS_MARK_DEFAULT_ENTRY)
if mark_default_entry == None:
	mark_default_entry = True

glipper.GSETTINGS.connect("changed::" + glipper.GSETTINGS_SAVE_HISTORY, lambda x, y, z=None: on_save_history_changed ())
save_history = glipper.GSETTINGS.get_boolean(glipper.GSETTINGS_SAVE_HISTORY)
if save_history == None:
	save_history = True

glipper.GSETTINGS.connect("changed::" + glipper.GSETTINGS_MAX_ITEM_LENGTH, lambda x, y, z=None: on_max_item_length_changed ())
max_item_length = glipper.GSETTINGS.get_int(glipper.GSETTINGS_MAX_ITEM_LENGTH)
if max_item_length == None:
	max_elements = 35

def on_mark_default_entry_changed(value):
	global mark_default_entry
	value = mark_default_entry = glipper.GSETTINGS.get_boolean(glipper.GSETTINGS_MARK_DEFAULT_ENTRY)
	if value is None:
		return
	mark_default_entry = value

def on_save_history_changed(value):
	global save_history
	value = glipper.GSETTINGS.get_boolean(glipper.GSETTINGS_SAVE_HISTORY)
	if value is None:
		return
	save_history = value

def on_max_item_length_changed (value):
	global max_item_length
	value = glipper.GSETTINGS.get_int(glipper.GSETTINGS_MAX_ITEM_LENGTH)
	if value is None:
		return
	max_item_length = value

def format_item(item):
	i = item.replace("\n", " ")
	i = i.replace("\t", " ")
	if len(item) > max_item_length:
	  return i[0:max_item_length//2] + '\u2026' + i[-(max_item_length//2-3):]
	return i
