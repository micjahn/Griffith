# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2011 Vasco Nunes, Piotr Ożarowski
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

import gtk
import version
import os
import sys

class AboutDialog:
    """Shows a gtk about dialog"""
    def __init__(self, locations):
        TRANSLATORS_FILE = os.path.join(locations['share'], 'TRANSLATORS') # remember to encode this file in UTF-8
        IMAGES_DIR = locations['images']

        def _open_url(dialog, link):
            import gutils
            gutils.run_browser(link)
        gtk.about_dialog_set_url_hook(_open_url)

        dialog = gtk.AboutDialog()
        dialog.set_name(version.pname)
        dialog.set_version(version.pversion)
        dialog.set_copyright("Copyright © 2005-2011 Vasco Nunes. Piotr Ożarowski")
        dialog.set_website(version.pwebsite)
        dialog.set_authors([
            _("Main Authors") + ':',
            version.pauthor.replace(', ', '\n') + "\n",
            _("Programmers") + ':',
            'Jessica Katharina Parth <Jessica.K.P@women-at-work.org>',
            'Michael Jahn <mikej06@hotmail.com>\n',
            _('Contributors:'), # FIXME: remove ":"
            'Christian Sagmueller <christian@sagmueller.net>\n' \
            'Arjen Schwarz <arjen.schwarz@gmail.com>'
        ])
        dialog.set_artists([_("Logo, icon and general artwork " + \
            "by Peek <peekpt@gmail.com>." + \
            "\nPlease visit http://www.peekmambo.com/\n"),
            'seen / unseen icons by dragonskulle <dragonskulle@gmail.com>'
        ])
        data = None
        if os.path.isfile(TRANSLATORS_FILE):
            data = open(TRANSLATORS_FILE).read()
        elif os.path.isfile(TRANSLATORS_FILE+'.gz'):
            from gutils import decompress
            data = decompress(open(TRANSLATORS_FILE + '.gz').read())
        elif os.name == 'posix':
            if os.path.isfile('/usr/share/doc/griffith/TRANSLATORS'):
                data = open('/usr/share/doc/griffith/TRANSLATORS').read()
            elif os.path.isfile('/usr/share/doc/griffith/TRANSLATORS.gz'):
                from gutils import decompress
                data = decompress(open('/usr/share/doc/griffith/TRANSLATORS.gz').read())
        translator_credits = ''
        if data:
            for line in data.split('\n'):
                if line.startswith('* '):
                    lang = line[2:]
                    if _(lang) != lang:
                        line = "* %s:" % _(lang)
                translator_credits += "%s\n" % line
        else:
            translator_credits = _("See TRANSLATORS file")
        dialog.set_translator_credits(translator_credits)
        logo_file = os.path.abspath(os.path.join(IMAGES_DIR, 'griffith.png'))
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
