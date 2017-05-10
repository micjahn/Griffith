# -*- coding: utf-8 -*-

__revision__ = '$Id: PluginMovieWP.py 1412 2010-03-28 20:18:54Z mikej06 $'

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
import movie,string
import re

plugin_name         = 'Wirtualna Polska'
plugin_description  = 'Serwis filmowy Wirtualnej Polski'
plugin_url          = 'www.film.wp.pl'
plugin_language     = _('Polish')
plugin_author       = 'Piotr Ożarowski'
plugin_author_email = '<ozarow+griffith@gmail.com>'
plugin_version      = '2.4'

class Plugin(movie.Movie):
    def __init__(self, id):
        self.movie_id = id
        self.url = "http://film.wp.pl/id,%s,film_szczegoly.html" % self.movie_id
        self.encode='iso-8859-2'

    def initialize(self):
        self.page = gutils.trim(self.page, '<h1 class="mp0">', '</div>\n</div>')
        self.cast_page = self.open_page(url="http://film.wp.pl/id,%s,film_obsada_i_tworcy.html" % self.movie_id)

    def get_image(self):
        self.image_url = gutils.trim(self.page, '<img src="', '" name="o')

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, u'<b>Tytuł oryginału:</b>', "\t\t</div><div")
        self.o_title = gutils.clean(self.o_title)
        if self.o_title == '':
            self.o_title = gutils.trim(self.page, '</h1>', '<div')

    def get_title(self):
        self.title = gutils.trim(self.page, u'<b>Tytuł polski:</b>', "\t\t</div><div")
        if self.title == '':
            self.title = gutils.before(self.page, '</h1>')
            pos = string.find(self.title, '(')
            if pos > -1:
                self.title = self.title[:pos]

    def get_director(self):
        self.director = gutils.regextrim(self.cast_page, u'>reżyser[^/]+/div>', '</div>')

    def get_plot(self):
        self.plot = gutils.trim(self.page, ' />', '\t\t<div class="clr">')
        pos = string.find(self.plot, u"<br>Zobacz tak\xBFe:<br>")
        if pos > 0:
            self.plot = self.plot[:pos]
        self.plot = string.replace(self.plot,"\r\n\r\n", '')

    def get_year(self):
        self.year = gutils.trim(self.page, '<b>Rok produkcji:</b>', "\t\t</div><div")
        year = re.findall(r'\d+', self.year)
        if len(year)>0:
            self.year = year[0]

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, '<b>Czas trwania:</b>', 'min')
        runtime =  re.findall(r'\d+', self.runtime)
        if len(runtime)>0:
            self.runtime = runtime

    def get_genre(self):
        self.genre = gutils.trim(self.page, '<b>Gatunek:</b>', "\t\t</div><div")
        self.genre = string.replace(self.genre, '<br />    ', '')
        self.genre = string.replace(self.genre, '<br />', ' / ')

    def get_cast(self):
        self.cast = ''
        tmp = gutils.trim(self.cast_page, '<h2>OBSADA:</h2>', '<div class="b')
        parts = string.split(tmp, '<a href="/id')
        for part in parts[1:]:
            actor = self.cast + gutils.trim(part, '>', '<')
            role = gutils.after(gutils.trim(part, '<div ', '</div>'), '>')
            if role:
                self.cast = actor + _(' as ') + role + '\n'
            else:
                self.cast = actor + '\n'

    def get_classification(self):
        self.classification = gutils.regextrim(self.page, u'<b>Przedział wiekowy:</b>', '</div>[^/]+/div>[^<]+<div')
        self.classification = gutils.trim(self.classification, 'od ', ' ')

    def get_studio(self):
        self.studio = gutils.regextrim(self.page, u'<b>Wytwórnia:</b>', '</div>[^/]+/div>[^<]+<div')

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = "http://film.wp.pl/id,%s,film.html" % self.movie_id

    def get_trailer(self):
        self.trailer = "http://film.wp.pl/id,%s,film_trailer.html" % self.movie_id

    def get_country(self):
        pos = self.page.find('<b>Kraj produkcji:</b>')
        if pos == -1:
            pos = self.page.find('<b>Kraje produkcji:</b>')
        if pos > -1:
            self.country = gutils.trim(self.page[pos:], '</b>', "\t\t</div><div")

    def get_rating(self):
        self.rating = None

    def get_notes(self):
        self.notes = ''

    def get_screenplay(self):
        self.screenplay = gutils.regextrim(self.cast_page, u'>scenarzysta[^/]+/div>', '</div>')

    def get_cameraman(self):
        self.cameraman = gutils.regextrim(self.cast_page, u'>zdjęcia[^/]+/div>', '</div>')

class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.encode='iso-8859-2'
        self.original_url_search = 'http://film.wp.pl/szukaj,%s,type,f,szukaj.html'
        self.translated_url_search = 'http://film.wp.pl/szukaj,%s,type,f,szukaj.html'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        self.page = gutils.trim(self.page, '<div id="filmUS"', '<div id=');
        return self.page

    def get_searches(self):
        elements = string.split(self.page, '</div><br />')
        self.number_results = elements[-1]

        if elements[0] != '':
            for element in elements:
                tmp_id = gutils.trim(element,'<div class="rgt"><a href="/id,', ',')
                self.ids.append(tmp_id)
                tmp_title = gutils.trim(element, 'html"><b>', '</b>')
                self.titles.append(tmp_title)
        else:
            self.number_results = 0
