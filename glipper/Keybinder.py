import gi
gi.require_version('GConf', '2.0')
from gi.repository import GObject, GConf
import gtk
import glipper
import keybinder

class Keybinder(GObject.GObject):
	__gsignals__ = {
		"activated" : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_ULONG]),
		# When the keybinding changes, passes a boolean indicating wether the keybinding is successful
		"changed" : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_BOOLEAN]),
	}

	def __init__(self):
		GObject.GObject.__init__(self)

		self.bound = False
		self.prevbinding = None

		# Set and retreive global keybinding from GConf
		self.key_combination = glipper.GCONF_CLIENT.get_string(glipper.GCONF_KEY_COMBINATION)
		if self.key_combination == None:
			# This is for uninstalled cases, the real default is in the schema
			self.key_combination = "<Ctrl><Alt>C"
		glipper.GCONF_CLIENT.notify_add(glipper.GCONF_KEY_COMBINATION, lambda x, y, z, a: self.on_config_key_combination(z.value))

		self.bind()

	def on_config_key_combination(self, value=None):
		if value != None and value.type == GConf.ValueType.STRING:
			self.prevbinding = self.key_combination
			self.key_combination = value.get_string()
			self.bind()

	def on_keyboard_shortcut(self):
		self.emit('activated', keybinder.get_current_event_time())

	def get_key_combination(self):
		return self.key_combination

	def bind(self):
		if self.bound:
			self.unbind()

		try:
			print 'Binding shortcut %s to popup glipper' % self.key_combination
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

if gtk.pygtk_version < (2,8,0):
	GObject.type_register(Keybinder)

_keybinder = Keybinder()

def get_glipper_keybinder():
	return _keybinder
