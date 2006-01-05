# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import gtk
import version
import os
import sys

class AboutDialog:
	"""Shows a gtk about dialog"""
	def __init__(self):
		dialog = gtk.AboutDialog()
		dialog.set_name(version.pname)
		dialog.set_version(version.pversion)
		dialog.set_copyright("Copyright © 2005-2006 Vasco Nunes")
		dialog.set_website(version.pwebsite)
		dialog.set_authors([_("Main Author") + ", " + _("Programmer")+":\n"+ \
			version.pauthor + "\n",
			'%s:\nPiotr Ozarowski <ozarow@gmail.com>\n'%_("Programmer") +"\n"+ \
			 _('Contributors:'),
			'Christian Sagmueller <christian@sagmueller.net>\n' \
			'Arjen Schwarz <arjen.schwarz@gmail.com>' \
			])
		dialog.set_artists([_("Logo, icon and general artwork " + \
			"by Peek <peekpt@gmail.com>." + \
			"\nPlease visit http://www.peekmambo.com/")])
		dialog.set_translator_credits( \
			_("Czech") + _(" by ") + \
			"Blondak <blondak@neser.cz>" + \
			"\n" + _("Bulgarian") + _(" by ") + \
			"Luchezar P. Petkov <luchezar.petkov@gmail.com>" + \
			"\n" + _("German") + _(" by ") + \
			"Christian Sagmueller <christian@sagmueller.net>" + \
			"\n" + _("Polish") + _(" by ") + \
			"Piotr Ozarowski <ozarow@gmail.com>" + \
			"\n" + _("Portuguese") + _(" by ") + \
			"Vasco Nunes <vasco.m.nunes@gmail.com>" + \
			"\n" + _("Spanish") + _(" by ") + \
			"Daniel Ucero <escaranbujo@gmail.com>" \
			)
		if os.name == 'nt':
			logo = gtk.gdk.pixbuf_new_from_file \
				("%s/images/griffith.png"%os.path.abspath \
				(os.path.dirname(sys.argv[0])))
		else:
			logo_file = os.path.abspath(os.path.dirname(sys.argv[0]))
			logo = gtk.gdk.pixbuf_new_from_file(logo_file.replace \
				("/bin", "/share/griffith") + "/griffith.png")
		dialog.set_logo(logo)
		dialog.set_license(_("This program is released under the GNU" + \
			"General Public License.\n" + \
			"Please visit http://www.gnu.org/copyleft/gpl.html for details."))
		dialog.set_comments(version.pdescription)
		dialog.run()
		dialog.destroy()
