import glipper, os, os.path

from gettext import gettext as _

snippets = []

def load_snippets():
	global snippets
	snippets = []

	conf_path = os.path.join(glipper.USER_PLUGINS_DIR, 'snippets')
	try:
		file = open(conf_path, "r")
	except IOError:
		return
	else:
		length = file.readline()[:-1]
		while(length):
			snippets.append(file.read(int(length)+1)[:-1])
			length = file.readline()[:-1]
		file.close()

def save_snippets():
	conf_path = os.path.join(glipper.USER_PLUGINS_DIR, 'snippets')
	file = open(conf_path, "w")
	for item in snippets:
		file.write(str(len(item)))
		file.write("\n" + item + "\n")
	file.close()


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Manager:
	def update_history_model(self):
		self.history_model.clear()
		index = 0
		item = glipper.get_history_item(index)
		while(item):
			self.history_model.append ([item])
			index = index + 1
			item = glipper.get_history_item(index)

	def __init__(self, parent):
		builder_file = Gtk.Builder()
		builder_file.add_from_file(os.path.join(os.path.dirname(__file__), "snippets.ui"))

		self.manager = builder_file.get_object("manager")
		self.manager.show_all()
		self.history_model = Gtk.ListStore (str)
		self.history_tree = builder_file.get_object('history_tree')
		self.history_tree.set_model(self.history_model)
		self.history_text = Gtk.CellRendererText ()
		self.history_column = Gtk.TreeViewColumn (_("History"), self.history_text, text = 0)
		self.history_tree.append_column (self.history_column)
		self.history_selection = self.history_tree.get_selection()
		self.history_selection.set_mode (Gtk.SelectionMode.SINGLE)
		self.snippets_model = Gtk.ListStore (str)
		self.snippets_tree = builder_file.get_object('snippets_tree')
		self.snippets_tree.set_model(self.snippets_model)
		self.snippets_text = Gtk.CellRendererText ()
		self.snippets_column = Gtk.TreeViewColumn (_("Snippets"), self.snippets_text, text = 0)
		self.snippets_tree.append_column (self.snippets_column)
		self.snippets_selection = self.snippets_tree.get_selection()
		self.snippets_selection.set_mode (Gtk.SelectionMode.SINGLE)
		self.update_history_model()

		for item in snippets:
			self.snippets_model.append([item])

		self.manager.set_transient_for(parent)

		builder_file.connect_signals({
			'on_manager_response': self.on_manager_response,
			'on_add_button_clicked': self.on_add_button_clicked,
			'on_remove_button_clicked': self.on_remove_button_clicked,
			'on_refresh_button_clicked': self.on_refresh_button_clicked,
		})

	def on_manager_response(self, window, response):
		if response == Gtk.ResponseType.DELETE_EVENT or response == Gtk.ResponseType.CLOSE:
			window.destroy()
		if response == 1:
			self.update_history_model()

	def on_add_button_clicked(self, widget):
		self.history_model, iter = self.history_selection.get_selected()
		if iter:
			if self.history_model.get_value(iter,0) not in snippets:
				snippets.append(self.history_model.get_value(iter, 0))
				self.snippets_model.append([self.history_model.get_value(iter, 0)])
				save_snippets()
				update_menu()

	def on_remove_button_clicked(self, widget):
		self.snippets_model, iter = self.snippets_selection.get_selected()
		if iter:
			snippets.remove(self.snippets_model.get_value(iter, 0))
			self.snippets_model.remove(iter)
			save_snippets()
			update_menu()

	def on_refresh_button_clicked(self, widget):
		pass

def on_show_preferences(parent):
	load_snippets()
	Manager(parent)

menu_item = Gtk.MenuItem(_("Snippets"))
menu = Gtk.Menu()

def init():
	load_snippets()
	glipper.add_menu_item(menu_item)
	glipper.GCONF_CLIENT.notify_add(glipper.GCONF_MAX_ITEM_LENGTH, lambda x, y, z, a=None: update_menu())
	update_menu()

def on_activate(menuitem, snippet):
	glipper.add_history_item(snippet)

def update_menu():
	max_length = glipper.GCONF_CLIENT.get_int(glipper.GCONF_MAX_ITEM_LENGTH)
	global menu
	menu.destroy()
	menu = Gtk.Menu()

	if len(snippets) == 0:
		menu.append(Gtk.MenuItem(_("No snippets available")))
	else:
		for snippet in snippets:
			item = Gtk.MenuItem(glipper.format_item(snippet))
			if len(snippet) > max_length:
				item.set_tooltip_text(snippet)
			item.connect('activate', on_activate, snippet)
			menu.append(item)

	menu.show_all()
	menu_item.set_submenu(menu)

def stop():
	menu.destroy()

def on_history_changed():
	update_menu()

def info():
	info = {"Name": _("Snippets"),
		"Description": _("Create snippets from history items"),
		"Preferences": True }
	return info
