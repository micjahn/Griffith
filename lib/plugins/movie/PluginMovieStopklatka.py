# -*- coding: utf-8 -*-

__revision__ = '$Id: PluginMovieStopklatka.py 1383 2010-01-05 21:04:00Z mikej06 $'

# Copyright (c) 2005-2010 Piotr Ożarowski
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

plugin_name         = 'Stopklatka'
plugin_description  = 'Internetowy Serwis Filmowy'
plugin_url          = 'www.stopklatka.pl'
plugin_language     = _('Polish')
plugin_author       = 'Piotr Ożarowski, Bartosz Kurczewski'
plugin_author_email = '<bartosz.kurczewski@gmail.com>'
plugin_version      = '1.11'


class Plugin(movie.Movie):
    IMAGE_PATTERN = re.compile('(http://img.stopklatka.pl/film/.*?)"')

    def __init__(self, id):
        self.movie_id = id
        self.url = "http://www.stopklatka.pl/film/film.asp?fi=%s" % str(self.movie_id)
        self.encode = 'utf-8'

    def initialize(self):
        self.page = self.page.replace(u'\x9c', u'ś')
        self.page = self.page.replace(u'š', u'ą')
        self.res = re.findall("""<td class="middle_cell"><span class="bold">(.*?)</span>, (.*?), (.*?), (.*?) min</td>""", self.page)
        if len(self.res) == 0:
            self.res = [('', '', '', '')]
        url = "http://www.stopklatka.pl/film/film.asp?fi=%s&sekcja=osoby" % str(self.movie_id)
        self.creditspage = self.open_page(self.parent_window, url=url)
        self.creditspage = self.creditspage.replace(u'\x9c', u'ś')
        self.creditspage = self.creditspage.replace(u'š', u'ą')

    def get_image(self):
        image = self.IMAGE_PATTERN.findall(self.page)
        if len(image) and image[0] != 'http://img.stopklatka.pl/film/0.jpg':
            self.image_url = image[0]

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, '<h2> (', ')</h2>')
        if self.o_title == '':
            self.o_title = self.get_title(True)

    def get_title(self, ret=False):
        data = gutils.trim(self.page, '<h1>', '</h1>')
        if ret is True:
            return data
        else:
            self.title = data

    def get_director(self):
        self.director = gutils.trim(self.creditspage, u'reżyseria: <', '</tr>')
        self.director = gutils.after(self.director, '>')
        self.director = self.director.replace('<br />', ', ')
        self.director = gutils.clean(self.director)
        if self.director.endswith(','):
            self.director = self.director[:-1]

    def get_plot(self):
        self.plot = gutils.trim(self.page, '<p>', '</p>')
        self.plot = gutils.before(self.plot, u'<b>Więcej ')

    def get_year(self):
        self.year = self.res[0][2]

    def get_runtime(self):
        self.runtime = self.res[0][3]

    def get_genre(self):
        self.genre = self.res[0][0]

    def get_cast(self):
        self.cast = gutils.trim(self.creditspage, 'obsada: <', '</td></tr>')
        self.cast = gutils.after(self.cast, '>')
        self.cast = self.cast.replace(' jako ', _(' as '))
        self.cast = string.replace(self.cast, '<br />', "\n")

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = ""

    def get_o_site(self):
        self.o_site = gutils.trim(self.page, ">strona oficjalna:<", " target=_blank")
        self.o_site = gutils.after(self.o_site, "href=")

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = "http://www.stopklatka.pl/film/film.asp?fi=" + self.movie_id + "&sekcja=mmedia"

    def get_country(self):
        self.country = self.res[0][1]

    def get_rating(self):
        self.rating = 0
        tmp = re.search(u'Ocena użytkowników:[^(]+[(]([0-9]+[,]*[0-9]*)[)]', self.page)
        if tmp:
            try:
                self.rating = int(round(float(tmp.group(1).replace(',', '.')), 0))
            except:
                pass

    def get_notes(self):
        self.notes = ''

    def get_cameraman(self):
        self.cameraman = gutils.regextrim(self.creditspage, u'zdjęcia: <', '(</tr>|<tr>)')
        self.cameraman = gutils.after(self.cameraman, '>')
        self.cameraman = self.cameraman.replace('<br />', ', ')
        self.cameraman = gutils.clean(self.cameraman)
        if self.cameraman.endswith(','):
            self.cameraman = self.cameraman[:-1]

    def get_screenplay(self):
        self.screenplay = gutils.trim(self.creditspage, u'scenariusz: <', '</tr>')
        self.screenplay = gutils.after(self.screenplay, '>')
        self.screenplay = self.screenplay.replace('<br />', ', ')
        self.screenplay = gutils.clean(self.screenplay)
        if self.screenplay.endswith(','):
            self.screenplay = self.screenplay[:-1]


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.encode = 'utf-8'
        self.original_url_search = "http://www.stopklatka.pl/szukaj/szukaj.asp?kategoria=film&szukaj="
        self.translated_url_search = "http://www.stopklatka.pl/szukaj/szukaj.asp?kategoria=film&szukaj="

    def search(self, parent_window):
        if not self.open_search(parent_window):
            return None
        self.page = gutils.trim(self.page, '>Wyniki poszukiwania frazy:', '</div>')
        self.page = self.page.replace(u'\x9c', u'ś')
        self.page = self.page.replace(u'š', u'ą')
        return self.page

    def get_searches(self):
        elements = re.findall("""/film/film.asp\?fi=(\d+)"[^>]*>.*?searchTitle\s*textB">(.*?)</span>.*?"> (.*?)</span>""", self.page)
        self.number_results = len(elements)

        for element in elements:
            self.ids.append(element[0])
            self.titles.append(gutils.clean(element[1]) + ' ' + element[2])
