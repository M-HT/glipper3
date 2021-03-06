# coding=UTF-8
from gettext import gettext as _
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import glipper


class About(object):
	__instance = None

	def __init__(self):
		if About.__instance == None:
			About.__instance = self
		else:
			About.__instance.about.present()
			return

		self.about = Gtk.AboutDialog()

		infos = {
			"name": _("Glipper"),
			"logo-icon-name": "glipper",
			"version": glipper.VERSION,
			"comments": _("A clipboard manager."),
			"copyright": "Copyright © 2007 Sven Rech, Eugenio Depalo, Karderio.\nCopyright © 2011 Laszlo Pandy\nCopyright © 2021 Roman Pauer",
			"website": "https://github.com/M-HT/glipper3",
			"website-label": _("Glipper website"),
		}

		#about.set_artists([])
		#about.set_documenters([])
		self.about.set_authors(["Sven Rech <sven@gmx.de>",
		                        "Eugenio Depalo <eugeniodepalo@mac.com>",
		                        "Karderio <karderio@gmail.com>",
		                        "Laszlo Pandy <laszlok2@gmail.com>",
		                        "Roman Pauer"])

		#translators: These appear in the About dialog, usual format applies.
		self.about.set_translator_credits( _("translator-credits") )

		self.about.set_license_type(Gtk.License.GPL_2_0_ONLY)

		for prop, val in list(infos.items()):
			self.about.set_property(prop, val)

		self.about.connect("response", self.destroy)
		self.about.show_all()

	def destroy(self, dialog, response):
		dialog.destroy()
		About.__instance = None
