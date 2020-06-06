import gi
gi.require_version('Keybinder', '3.0')
from gi.repository import GObject
from gi.repository import Keybinder as keybinder
import glipper

class Keybinder(GObject.GObject):
	__gsignals__ = {
		"activated": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_ULONG]),
		# When the keybinding changes, passes a boolean indicating wether the keybinding is successful
		"changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_BOOLEAN]),
	}

	def __init__(self):
		GObject.GObject.__init__(self)

		self.bound = False
		self.prevbinding = None

		keybinder.init()

		# Set and retreive global keybinding from GSettings
		glipper.GSETTINGS.connect("changed::" + glipper.GSETTINGS_KEY_COMBINATION, lambda x, y, z=None: self.on_config_key_combination())
		self.key_combination = glipper.GSETTINGS.get_string(glipper.GSETTINGS_KEY_COMBINATION)
		if self.key_combination == None:
			# This is for uninstalled cases, the real default is in the schema
			self.key_combination = "<Ctrl><Alt>C"

		self.bind()

	def on_config_key_combination(self):
		value = glipper.GSETTINGS.get_string(glipper.GSETTINGS_KEY_COMBINATION)
		if value != None:
			self.prevbinding = self.key_combination
			self.key_combination = value
			self.bind()

	def on_keyboard_shortcut(self, keystr, user_data=None):
		self.emit('activated', keybinder.get_current_event_time())

	def get_key_combination(self):
		return self.key_combination

	def bind(self):
		if self.bound:
			self.unbind()

		try:
			print('Binding shortcut %s to popup glipper' % self.key_combination)
			keybinder.bind(self.key_combination, self.on_keyboard_shortcut)
			self.bound = True
		except KeyError:
			# if the requested keybinding conflicts with an existing one, a KeyError will be thrown
			self.bound = False

		self.emit('changed', self.bound)

	def unbind(self):
		try:
			keybinder.unbind(self.prevbinding)
			self.bound = False
		except KeyError:
			# if the requested keybinding is not bound, a KeyError will be thrown
			pass

GObject.type_register(Keybinder)

_keybinder = Keybinder()

def get_glipper_keybinder():
	return _keybinder
