import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Gdk, Pango
import glipper
from glipper.History import *
from os.path import join


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
		self.popup_scrolledwindow = builder_file.get_object("popup_scrolledwindow")
		self.popup_liststore = builder_file.get_object("popup_liststore")
		self.popup_treemodelfilter = builder_file.get_object("popup_treemodelfilter")
		self.popup_treeview = builder_file.get_object("popup_treeview")
		self.popup_entry = builder_file.get_object("popup_entry")

		self.popup_selection = self.popup_treeview.get_selection()
		self.popup_treemodelfilter.set_visible_func(self.visible_func, None)
		self.popup_window.set_skip_taskbar_hint(True)
		self.page_rows = 0
		self.filter_low = ''

		builder_file.connect_signals({
			'on_popup_window_focus_out_event': self.on_popup_window_focus_out_event,
			'on_popup_treeview_button_press_event': self.on_popup_treeview_button_press_event,
			'on_popup_treeview_key_press_event': self.on_popup_treeview_key_press_event,
			'on_popup_treeview_popup_menu': self.on_popup_treeview_popup_menu,
			'on_popup_entry_button_press_event': self.on_popup_entry_button_press_event,
			'on_popup_entry_key_press_event': self.on_popup_entry_key_press_event,
			'on_popup_entry_popup_menu': self.on_popup_entry_popup_menu,
			'on_popup_entry_changed': self.on_popup_entry_changed,
		})

		self.show_window(time)

	def button_event_triggers_context_menu(self, event):
		if hasattr(Gdk.Event, 'triggers_context_menu'):
			if Gdk.Event.triggers_context_menu(event):
				return True
		elif event.button == 3 and event.type == Gdk.EventType.BUTTON_PRESS:
			return True
		return False

	def on_popup_window_focus_out_event(self, widget, event):
		if self.was_entry_popup_menu or event.window == widget:
			self.was_entry_popup_menu = False
			return True
		widget.hide()
		return False

	def on_popup_treeview_button_press_event(self, widget, event):
		if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
			if self.choose_item():
				return True
		elif self.button_event_triggers_context_menu(event):
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
		elif event.keyval == Gdk.KEY_Escape:
			self.popup_window.hide()
			return True
		else:
			unicode_char = Gdk.keyval_to_unicode(event.keyval)
			if unicode_char >= 32:
				self.popup_entry.grab_focus()
				self.popup_entry.insert_text(chr(unicode_char), -1)
				self.popup_entry.set_position(-1)
				return True
		return False

	def on_popup_treeview_popup_menu(self, widget):
		self.menu.popup(None, None, None, None, 0, Gdk.CURRENT_TIME)
		return True

	def on_popup_entry_button_press_event(self, widget, event):
		if self.button_event_triggers_context_menu(event):
			if widget.do_popup_menu(widget):
				self.was_entry_popup_menu = True
			return True
		return False

	def on_popup_entry_key_press_event(self, widget, event):
		if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
			if self.choose_item():
				return True
		elif event.keyval == Gdk.KEY_Up or event.keyval == Gdk.KEY_KP_Up:
			self.move_selection(-1)
			return True
		elif event.keyval == Gdk.KEY_Down or event.keyval == Gdk.KEY_KP_Down:
			self.move_selection(1)
			return True
		elif event.keyval == Gdk.KEY_Page_Up or event.keyval == Gdk.KEY_KP_Page_Up:
			self.move_selection(-self.page_rows)
			return True
		elif event.keyval == Gdk.KEY_Page_Down or event.keyval == Gdk.KEY_KP_Page_Down:
			self.move_selection(self.page_rows)
			return True
		elif event.keyval == Gdk.KEY_Escape:
			self.popup_window.hide()
			return True
		return False

	def on_popup_entry_popup_menu(self, widget):
		if widget.do_popup_menu(widget):
			self.was_entry_popup_menu = True
		return True

	def on_popup_entry_changed(self, editable):
		self.renumber_list(True)
		self.filter_low = self.popup_entry.get_text().lower()
		self.popup_treemodelfilter.refilter()
		self.renumber_list(False)
		store_iter = self.popup_treemodelfilter.get_iter_first()
		if not store_iter is None:
			self.popup_treeview.set_cursor(self.popup_treemodelfilter.get_path(store_iter), None, False)
		return True

	def visible_func(self, model, store_iter, data):
		if self.filter_low == '':
			return True
		clipboard_text = model.get_value(store_iter, 4)
		if clipboard_text.lower().find(self.filter_low) >= 0:
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

		self.was_entry_popup_menu = False
		self.filter_low = ''

		self.fill_store()

		store_iter = self.popup_treemodelfilter.get_iter_first()
		if not store_iter is None:
			self.popup_treeview.set_cursor(self.popup_treemodelfilter.get_path(store_iter), None, False)

		self.popup_treeview.grab_focus()
		self.popup_entry.set_text('')
		self.popup_window.set_screen(screen)
		self.popup_window.move(x, y)
		self.popup_window.show_all()
		self.popup_window.present_with_time(time)

		if self.page_rows <= 1:
			(model, store_iter) = self.popup_selection.get_selected()
			if not store_iter is None:
				row_height = self.popup_treeview.get_cell_area(model.get_path(store_iter), None).height
				view_height = self.popup_scrolledwindow.get_allocated_height()
				self.page_rows = view_height // row_height
			else:
				self.page_rows = 1

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
				circle = u'\u25cf'
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
		store_iter = self.popup_treemodelfilter.get_iter_first()
		while item_num > 1 and not store_iter is None:
			item_num = item_num - 1
			store_iter = self.popup_treemodelfilter.iter_next(store_iter)
		if store_iter is None:
			return False
		clipboard_text = self.popup_treemodelfilter.get_value(store_iter, 4)
		get_glipper_clipboards().set_text(clipboard_text)
		self.popup_window.hide()
		return True

	def move_selection(self, num_rows):
		(model, store_iter) = self.popup_selection.get_selected()
		if not store_iter is None:
			if num_rows > 0:
				iter_dir = model.iter_next
			else:
				iter_dir = model.iter_previous
				num_rows = -num_rows
			while num_rows > 0 and not store_iter is None:
				num_rows = num_rows - 1
				last_iter = store_iter
				store_iter = iter_dir(store_iter)
			if store_iter is None:
				store_iter = last_iter
			self.popup_treeview.set_cursor(model.get_path(store_iter), None, False)

	def renumber_list(self, clear):
		store_iter = self.popup_treemodelfilter.get_iter_first()
		item_num = 1
		while item_num < 11 and not store_iter is None:
			self.popup_treemodelfilter.set_value(store_iter, 0, '' if clear else str(item_num if item_num < 10 else 0))
			item_num = item_num + 1
			store_iter = self.popup_treemodelfilter.iter_next(store_iter)

