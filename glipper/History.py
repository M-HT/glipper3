import gi
from gi.repository import GObject
import glipper
from glipper.Clipboards import *
from glipper.PluginsManager import *
from gettext import gettext as _
import sys

class History(GObject.GObject):
	__gsignals__ = {
		"changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT]),
	}

	def __init__(self):
		GObject.GObject.__init__(self)
		self.history = []
		get_glipper_clipboards().connect('new-item', self.on_new_item)

		glipper.GSETTINGS.connect("changed::" + glipper.GSETTINGS_MAX_ELEMENTS, lambda x, y, z=None: self.on_max_elements_changed ())
		self.max_elements = glipper.GSETTINGS.get_int(glipper.GSETTINGS_MAX_ELEMENTS)
		if self.max_elements == None:
			self.max_elements = 20

	def get_history(self):
		return self.history

	def on_new_item(self, clipboards, item, is_from_selection):
		self.add(item, is_from_selection)
		get_glipper_plugins_manager().call('on_new_item', item)

	def clear(self):
		self.history = []
		self.emit('changed', self.history)

	def get(self, index):
		if index >= len(self.history):
			return

		return self.history[index]

	def set(self, index, item):
		assert item is not None
		if sys.version_info.major >= 3:
			item = str(item)
		else:
			item = unicode(item)
		if item in self.history:
			self.history.remove(item)

		if index == len(self.history):
			self.history.append(item)
		else:
			self.history[index] = item
		self.emit('changed', self.history)

	def add(self, item, is_from_selection=False):
		if item is not None:
			if sys.version_info.major >= 3:
				item = str(item)
			else:
				item = unicode(item)
			if item in self.history:
				self.history.remove(item)

			last_item = self.history[0] if self.history else None
			if is_from_selection and last_item is not None and \
					(item.startswith(last_item) or item.endswith(last_item)):
				self.history[0] = item
			else:
				self.history.insert(0, item)

			if len(self.history) > self.max_elements:
				self.history = self.history[0:self.max_elements]

			ctrl_c_item = get_glipper_clipboards().get_default_clipboard_text()
			if ctrl_c_item is not None and ctrl_c_item not in self.history:
				self.history[-1] = ctrl_c_item

		# if item is None, emit changed anyway because
		# the current (bold) clipboard item has changed.
		self.emit('changed', self.history)

	def remove(self, index):
		del self.history[index]

	def load(self):
		try:
			file = open(glipper.HISTORY_FILE, "rb")

			length = file.readline()
			while length:
				try:
					bytes_to_read = int(length)
				except ValueError:
					break

				self.history.append(file.read(bytes_to_read).decode('UTF-8'))
				file.read(1) # This is for \n
				length = file.readline()

			file.close()
		except IOError:
			pass

		self.emit('changed', self.history)

	def save(self):
		try:
			file = open(glipper.HISTORY_FILE, "wb")
		except IOError:
			return # Cannot write to history file

		for item in self.history:
			if sys.version_info.major >= 3:
				assert isinstance(item, str)
			else:
				assert isinstance(item, unicode)
			string = item.encode('UTF-8')
			file.write(str(len(string)).encode('UTF-8') + b'\n')
			file.write(string + b'\n')

		file.close()

	def on_max_elements_changed (self):
		value = glipper.GSETTINGS.get_int(glipper.GSETTINGS_MAX_ELEMENTS)
		if value is None:
			return
		self.max_elements = value
		if len(self.history) > self.max_elements:
			self.history = self.history[0:self.max_elements]
			self.emit('changed', self.history)

history = History()

def get_glipper_history():
	return history
