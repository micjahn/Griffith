# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes, Piotr Ożarowski
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
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import gtk
import version
import os
import sys

class AboutDialog:
	"""Shows a gtk about dialog"""
	def __init__(self, images_dir):
		dialog = gtk.AboutDialog()
		dialog.set_name(version.pname)
		dialog.set_version(version.pversion)
		dialog.set_copyright("Copyright © 2005-2007 Vasco Nunes. Piotr Ożarowski")
		dialog.set_website(version.pwebsite)
		dialog.set_authors([
			_("Main Authors") + ':',
			version.pauthor.replace(', ', '\n') + "\n",
			_("Programmer") + ':',
			'Jessica Katharina Parth <Jessica.K.P@women-at-work.org>\n',
			_('Contributors:'), # FIXME: remove ":"
			'Christian Sagmueller <christian@sagmueller.net>\n' \
			'Arjen Schwarz <arjen.schwarz@gmail.com>\n' \
			'Michael Jahn <mikej06@hotmail.com>'
		])
		dialog.set_artists([_("Logo, icon and general artwork " + \
			"by Peek <peekpt@gmail.com>." + \
			"\nPlease visit http://www.peekmambo.com/\n"),
			'seen / unseen icons by dragonskulle <dragonskulle@gmail.com>'
		])
		dialog.set_translator_credits(\
			_("Bulgarian") + ":\n\t" + \
				"Luchezar P. Petkov <luchezar.petkov@gmail.com>\n" + \
			_("Brasilian Portuguese") + ":\n\t" + \
				"Fábio Nogueira <deb-user-ba@ubuntu.com>\n" + \
			_("Czech") + ":\n\t" + \
				"Blondak <blondak@neser.cz>,\n\t" + \
				"Ondra 'Kepi' Kudlík <kepi@igloonet.cz>\n" + \
			_("Dutch") + ":\n\t" + \
				"Marcel Dijkstra <mdtje@hotmail.com>\n" + \
			_("French") + ":\n\t" + \
				"Guillaume Pratte <guillaume@guillaumepratte.net>" + \
				"original translation from:\n\t" + \
				"Pierre-Luc Lévy <pllevy@free.fr>\n" + \
			_("German") + ":\n\t" + \
				"Jessica Katharina Parth <Jessica.K.P@women-at-work.org>,\n\t" + \
				"original translation from:\n\t" + \
				"Christian Sagmueller <christian@sagmueller.net>,\n\t" + \
				"Malte Wiemann <ryan2057@gmx.de>\n" + \
			_("Italian") + ":\n\t" + \
				"Diego Porcelli <diego.p77@gmail.com>\n" + \
			_("Polish") + ":\n\t" + \
				"Piotr Ozarowski <ozarow+griffith@gmail.com>\n" + \
			_("Portuguese") + ":\n\t" + \
				"Vasco Nunes <vasco.m.nunes@gmail.com>\n" + \
			_("Spanish") + ":\n\t" + \
				"Daniel Ucero <escaranbujo@gmail.com>\n" + \
			_("Swedish") + ":\n\t" + \
				"Daniel Nylander <po@danielnylander.se>\n" + \
			_("Danish") + ":\n\t" + \
				"Joe Dalton <joedalton2@yahoo.dk>\n" \
		)
		logo_file = os.path.abspath(os.path.join(images_dir, 'griffith.png'))
		logo = gtk.gdk.pixbuf_new_from_file(logo_file)
		dialog.set_logo(logo)
		if os.path.isfile('/usr/share/common-licenses/GPL-2'):
			dialog.set_license(open('/usr/share/common-licenses/GPL-2').read())
		else:
			dialog.set_license(_("This program is released under the GNU" + \
				"General Public License.\n" + \
				"Please visit http://www.gnu.org/copyleft/gpl.html for details."))
		dialog.set_comments(version.pdescription)
		dialog.run()
		dialog.destroy()
