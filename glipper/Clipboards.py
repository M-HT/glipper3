import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gtk, Gdk
import glipper

class Clipboards(GObject.GObject):

	__gsignals__ = {
		"new-item": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING, GObject.TYPE_BOOLEAN]),
	}

	def __init__(self):
		GObject.GObject.__init__(self)
		self.default_clipboard = Clipboard(Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD),
		                                   self.emit_new_item,
		                                   glipper.GSETTINGS_USE_DEFAULT_CLIPBOARD)
		self.primary_clipboard = Clipboard(Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY),
		                                   self.emit_new_item_selection,
		                                   glipper.GSETTINGS_USE_PRIMARY_CLIPBOARD)

	def set_text(self, text):
		self.default_clipboard.set_text(text)
		self.primary_clipboard.set_text(text)

		self.emit('new-item', text, False)

	def clear_text(self):
		self.default_clipboard.clear()
		self.primary_clipboard.clear()

	def get_default_clipboard_text(self):
		return self.default_clipboard.get_text()

	def emit_new_item(self, item):
		self.emit('new-item', item, False)

	def emit_new_item_selection(self, item):
		self.emit('new-item', item, True)


def unicode_or_none(bytes_utf8):
	if bytes_utf8 is None:
		return None
	else:
		return unicode(bytes_utf8, 'UTF-8')

import sys
if sys.version_info.major >= 3:
	unicode_or_none = lambda x : x

class Clipboard(object):
	def __init__(self, clipboard, new_item_callback, use_clipboard_gconf_key):
		self.new_item_callback = new_item_callback
		self.clipboard = clipboard
		self.clipboard_text = unicode_or_none(clipboard.wait_for_text())
		self.clipboard.connect('owner-change', self.on_clipboard_owner_change)

		glipper.GSETTINGS.connect("changed::" + use_clipboard_gconf_key, self.on_use_clipboard_changed)
		self.use_clipboard = glipper.GSETTINGS.get_boolean(use_clipboard_gconf_key)
		if self.use_clipboard is None:
			self.use_clipboard = True

	def get_text(self):
		return self.clipboard_text

	def set_text(self, text):
		if self.use_clipboard:
			self.clipboard.set_text(text, -1)
			self.clipboard_text = text

	def clear(self):
		if self.use_clipboard:
			self.clipboard.set_text('', 0)
			self.clipboard.clear()
			self.clipboard_text = None


	def on_clipboard_owner_change(self, clipboard, event):
		if self.use_clipboard:
			self.clipboard_text = unicode_or_none(clipboard.wait_for_text())
			self.new_item_callback(self.clipboard_text)

	def on_use_clipboard_changed(self, settings, key, user_data=None):
		value = settings.get_boolean(key)
		if value is None:
			return
		self.use_clipboard = value

clipboards = Clipboards()

def get_glipper_clipboards():
	return clipboards

