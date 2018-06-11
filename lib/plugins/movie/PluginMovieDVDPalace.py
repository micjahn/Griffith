# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieDVDPalace.py 1626 2012-07-03 20:45:58Z mikej06 $'

# Copyright (c) 2006-2012
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

import gutils
import movie
import string
import re

plugin_name         = "DVD-Palace"
plugin_description  = "DVD-Onlinemagazin mit DVD-Datenbank"
plugin_url          = "www.dvd-palace.de"
plugin_language     = _("German")
plugin_author       = "Michael Jahn"
plugin_author_email = "<mikej06@hotmail.com>"
plugin_version      = "1.3"

class Plugin(movie.Movie):

    def __init__(self, id):
        self.encode   = 'iso-8859-1'
        self.movie_id = id
        self.url      = 'http://www.dvd-palace.de/datenbank/medien/' + self.movie_id

    def get_image(self):
        self.image_url = gutils.trim(self.page, 'src="/showcover.php?', '"')
        if self.image_url <> '':
            self.image_url = 'http://www.dvd-palace.de/showcover.php?' + self.image_url

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, 'Originaltitel', '</b>')
        if self.o_title == '':
            self.o_title = gutils.trim(self.page, '<TITLE>', ' - Details')

    def get_title(self):
        self.title = gutils.trim(self.page, '<TITLE>', ' - Details')

    def get_director(self):
        self.director = gutils.trim(self.page, 'Regisseur(e)', '</TR>')

    def get_plot(self):
        self.plot = re.sub(
                u'[]', '-',
                re.sub(
                    u'[\x93]', '"', gutils.regextrim(self.page, '[0-9 ]+Views', '</td>')))

    def get_year(self):
        self.year = gutils.after(gutils.trim(gutils.trim(self.page, 'Originaltitel', '</TR>'), '(', ')'), ' ')

    def get_runtime(self):
        self.runtime = gutils.strip_tags(string.replace(gutils.trim(self.page, 'Laufzeit', ' min'), 'ca. ', ''))

    def get_genre(self):
        self.genre = string.replace(string.replace(gutils.trim(self.page, 'Genre(s)', '</TR>'), '&nbsp;', ''), '<br>', ', ')

    def get_cast(self):
        self.cast = string.replace(
            re.sub('<em>[^<]*</em>', ' ',
                re.sub(',[ ]*', '\n',
                    gutils.trim(self.page, 'Darsteller / Sprecher', '</TR>')
                )
            ),
            '\n ', '\n')

    def get_classification(self):
        self.classification = string.replace(gutils.trim(gutils.trim(self.page, 'Altersfreigabe (FSK)', '</TR>'), 'alt="', '"'), 'Altersfreigabe ', '')

    def get_studio(self):
        self.studio = string.replace(string.replace(gutils.trim(self.page, 'Label</b>', '</td>'), '&nbsp;', ''), ':', '')
        if not self.studio:
            self.studio = string.replace(string.replace(gutils.trim(self.page, 'Vertrieb</b>', '</td>'), '&nbsp;', ''), ':', '')

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = gutils.before(gutils.trim(gutils.trim(self.page, 'Originaltitel', '</TR>'), '(', ')'), ' ')

    def get_rating(self):
        self.rating = "0"

    def get_notes(self):
        self.notes = ""
        tmp_notes = re.sub('^[ \t]+', '',
            gutils.strip_tags(
            re.sub('(<br>|<br />)', '\r\n',
            re.sub('[\r\n]+', '',
            re.sub('[ \t][ \t\r\n]+', ' ',
            gutils.trim(self.page, 'Bildformat(e)', '</TR>')))))
        )
        if (tmp_notes != ""):
            self.notes = self.notes + "Bildformat(e):\n" + tmp_notes + "\n"
        tmp_notes = re.sub('^[ \t]+', '',
            gutils.strip_tags(
            re.sub('(<br>|<br />)', '\r\n',
            re.sub('[\r\n]+', '',
            re.sub('[ \t][ \t\r\n]+', ' ',
            gutils.trim(self.page, 'Tonformat(e)', '</TR>')))))
        )
        if (tmp_notes != ""):
            self.notes = self.notes + "Tonformat(e):\n" + tmp_notes + "\n\n"
        tmp_notes = re.sub('^[ \t]+', '',
            gutils.strip_tags(
            re.sub('(<br>|<br />)', '\r\n',
            re.sub('[\r\n]+', '',
            re.sub('[ \t][ \t\r\n]+', ' ',
            gutils.trim(self.page, 'Untertitel', '</TR>')))))
        )
        if (tmp_notes != ""):
            self.notes = self.notes + "Untertitel:" + tmp_notes + "\n\n"

    def get_barcode(self):
        self.barcode = gutils.trim(self.page, 'EAN', '</b>')


class SearchPlugin(movie.SearchMovie):

    translations = (
        ('ü', 'ue'),
        ('ä', 'ae'),
        ('ö', 'oe'),
        ('Ü', 'UE'),
        ('Ä', 'AE'),
        ('Ö', 'OE'),
        ('ß', 'ss')
    )

    def __init__(self):
        self.original_url_search   = "http://www.dvd-palace.de/dvddatabase/dbsearch.php?action=1&suchbegriff="
        self.translated_url_search = "http://www.dvd-palace.de/dvddatabase/dbsearch.php?action=1&suchbegriff="
        self.encode='iso-8859-1'
        self.remove_accents = False

    def search(self,parent_window):
        # replace some standard german umlauts
        for from_str, to_str in self.translations:
            self.title = self.title.replace(from_str, to_str)
        # AFTER that remove accents
        self.title = gutils.remove_accents(str(self.title))
        if not self.open_search(parent_window):
            return None
        tmp_pagemovie = self.page
        #
        # try to get all result pages (not so nice, but it works)
        #
        tmp_pagecount = gutils.trim(tmp_pagemovie, 'Seiten (<b>', '</b>)')
        try:
            tmp_pagecountint = int(tmp_pagecount)
        except:
            tmp_pagecountint = 1
        tmp_pagecountintcurrent = 1
        while (tmp_pagecountint > tmp_pagecountintcurrent and tmp_pagecountintcurrent < 5):
            self.url = "http://www.dvd-palace.de/dvddatabase/dbsearch.php?action=1&start=" + str(tmp_pagecountintcurrent * 20) + "&suchbegriff="
            if self.open_search(parent_window):
                tmp_pagemovie = tmp_pagemovie + self.page
                tmp_pagecountintcurrent = tmp_pagecountintcurrent + 1
        self.page = tmp_pagemovie
        return self.page

    def get_searches(self):
        elements = re.split('&nbsp;<a title="[^"]+" href="(/datenbank/medien/dvd/|/datenbank/medien/blu-ray/)', self.page)
        elements[0] = None
        for index in range(1, len(elements), 2):
            element = elements[index + 1]
            if element <> None:
                if elements[index] == '/datenbank/medien/blu-ray/':
                    medium = 'Blu-Ray'
                    self.ids.append('blu-ray/' + gutils.before(element,'"'))
                else:
                    medium = 'DVD'
                    self.ids.append('dvd/' + gutils.before(element,'"'))
                self.titles.append(
                    gutils.trim(element, '>', '</a>') +
                    gutils.clean(
                        '(' + medium + ' - ' +
                        re.sub('[ \t\n]+', ' ',
                        string.replace(
                        string.replace(
                            gutils.regextrim(element, '<div [^>]*>', '</div>'),
                            '<br>', ' - '),
                            '&nbsp;', ''))
                        + ')'
                    )
                )

