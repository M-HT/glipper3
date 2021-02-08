import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Gdk, Pango
import glipper
from glipper.History import *
from os.path import join
from gettext import gettext as _


class Popup(object):
	__instance = None

	def __init__(self, menu, time):
		if Popup.__instance == None:
			Popup.__instance = self
		else:
			Popup.__instance.show_window(time)
			return

		self.menu = menu

		builder_file = Gtk.Builder()
		builder_file.add_from_file(join(glipper.SHARED_DATA_DIR, "popup-window.ui"))

		self.popup_window = builder_file.get_object("popup_window")
		self.popup_liststore = builder_file.get_object("popup_liststore")
		self.popup_treeview = builder_file.get_object("popup_treeview")

		self.popup_selection = self.popup_treeview.get_selection()
		builder_file.connect_signals({
			'on_popup_window_focus_out_event': self.on_popup_window_focus_out_event,
			'on_popup_treeview_button_press_event': self.on_popup_treeview_button_press_event,
			'on_popup_treeview_key_press_event': self.on_popup_treeview_key_press_event,
		})

		self.popup_window.set_skip_taskbar_hint(True)

		self.show_window(time)

	def on_about (self, component):
		glipper.About.About()

	def on_popup_window_focus_out_event(self, widget, event):
		if event.window != widget:
			widget.hide()
			return True
		return False

	def on_popup_treeview_button_press_event(self, widget, event):
		if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
			if self.choose_item():
				return True
		elif event.button == 3 and event.type == Gdk.EventType.BUTTON_PRESS:
			self.menu.popup(None, None, None, None, event.button, event.time)
			return True
		return False

	def on_popup_treeview_key_press_event(self, widget, event):
		if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
			if self.choose_item():
				return True
		elif event.keyval == Gdk.KEY_0 or event.keyval == Gdk.KEY_KP_0:
			if self.choose_item_num(10):
				return True
		elif event.keyval >= Gdk.KEY_1 and event.keyval <= Gdk.KEY_9:
			if self.choose_item_num(1 + event.keyval - Gdk.KEY_1):
				return True
		elif event.keyval >= Gdk.KEY_KP_1 and event.keyval <= Gdk.KEY_KP_9:
			if self.choose_item_num(1 + event.keyval - Gdk.KEY_KP_1):
				return True
		elif event.keyval == Gdk.KEY_Menu:
			self.menu.popup(None, None, None, None, 0, event.time)
			return True
		elif event.keyval == Gdk.KEY_Escape:
			self.popup_window.hide()
			return True
		return False

	def show_window(self, time):
		display = Gdk.Display.get_default()
		seat = display.get_default_seat()
		pointer = seat.get_pointer()
		(screen, x, y) = pointer.get_position()
		monitor = display.get_monitor_at_point(x, y)
		geom = monitor.get_geometry()
		(w, h) = self.popup_window.get_size()

		if x + w > geom.width:
			x = geom.width - w
		if y + h > geom.height:
			y = geom.height - h

		self.fill_store()

		store_iter = self.popup_liststore.get_iter_first()
		if not store_iter is None:
			self.popup_selection.select_iter(store_iter)
			self.popup_treeview.scroll_to_cell(Gtk.TreePath.new_first(), None, False, 0, 0)

		self.popup_treeview.grab_focus()
		self.popup_window.set_screen(screen)
		self.popup_window.move(x, y)
		self.popup_window.show_all()
		self.popup_window.present_with_time(time)

	def fill_store(self):
		history = glipper.AppIndicator.get_glipper_history().get_history()

		default_clipboard_text = get_glipper_clipboards().get_default_clipboard_text()

		self.popup_liststore.clear()
		item_num = 0
		for item in history:
			item_num = item_num + 1
			if item_num < 10:
				number = str(item_num)
			elif item_num == 10:
				number = "0"
			else:
				number = ""

			text = glipper.AppIndicator.format_item(item)

			if glipper.AppIndicator.mark_default_entry and item == default_clipboard_text:
				circle = u'\u23fa'
				font_weight = Pango.Weight.BOLD
			else:
				circle = ''
				font_weight = Pango.Weight.NORMAL

			self.popup_liststore.append([number, circle, text, font_weight, item])

	def choose_item(self):
		(model, store_iter) = self.popup_selection.get_selected()
		if store_iter is None:
			return False
		clipboard_text = model.get_value(store_iter, 4)
		get_glipper_clipboards().set_text(clipboard_text)
		self.popup_window.hide()
		return True

	def choose_item_num(self, item_num):
		store_iter = self.popup_liststore.get_iter_first()
		while item_num > 1 and not store_iter is None:
			item_num = item_num - 1
			store_iter = self.popup_liststore.iter_next(store_iter)
		if store_iter is None:
			return False
		clipboard_text = self.popup_liststore.get_value(store_iter, 4)
		get_glipper_clipboards().set_text(clipboard_text)
		self.popup_window.hide()
		return True

