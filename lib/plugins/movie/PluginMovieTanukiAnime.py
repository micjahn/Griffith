# -*- coding: utf-8 -*-

__revision__ = '$Id: PluginMovieTanukiAnime.py 1090 2008-12-16 20:59:02Z piotrek $'

# Copyright (c) 2005-2007 Piotr Ożarowski
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

plugin_name         = 'Tanuki-Anime'
plugin_description  = 'Największy zbiór recenzji anime w Polsce'
plugin_url          = 'anime.tanuki.pl'
plugin_language     = _('Polish')
plugin_author       = 'Piotr Ozarowski'
plugin_author_email = '<ozarow+griffith@gmail.com>'
plugin_version      = '1.3'

class Plugin(movie.Movie):
    def __init__(self, id):
        if str(id).find('http://') != -1:
            self.movie_id = 'TA'
            self.url = str(id)
        else:
            self.movie_id = str(id)
            self.url = "http://anime.tanuki.pl/strony/anime/%s" % str(id)
        self.encode='UTF-8'
    
    def initialize(self):
        if self.movie_id == 'TA':
            self.movie_id = gutils.trim(self.page, '"><a href="/strony/anime/', '/oceny')
            self.url = "http://anime.tanuki.pl/strony/anime/%s" % self.movie_id

    def get_image(self):
        self.image_url = gutils.trim(self.page, '<img src="/screens/', '<br />')
        self.image_url = gutils.before(self.image_url, '"')
        self.image_url = "http://anime.tanuki.pl/screens/%s" % self.image_url

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, '<h3 class="animename"', '</h3>')
        self.o_title = gutils.after(self.o_title, '>')

    def get_title(self):
        self.title = self.o_title

    def get_director(self):
        self.director = gutils.trim(self.page, "<th scope=\"row\">Reżyser:</th>\n\t<td>", '</td>')

    def get_plot(self):
        self.plot = gutils.trim(self.page, "<div class=\"copycat\">\n", '</div>')

    def get_year(self):
        self.year = gutils.trim(self.page,'<div class=\"sitem\">Rok wydania: <', '</a>')
        self.year = gutils.after(self.year, '>')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, "<div class=\"sitem\">Czas trwania: <b>\n\t\t", '\n</b>')
        if self.runtime.find('?') != -1:
            self.runtime = ''
        else:
            self.runtime = gutils.after(self.runtime, '×')
            self.runtime = gutils.before(self.runtime, ' min')

    def get_genre(self):
        self.genre = gutils.trim(self.page, "<div class=\"sitem\">Gatunki:\n\t\t", '</div>')
        self.genre = string.replace(self.genre, "\t\t", ' ')

    def get_cast(self):
        self.cast = ''

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = gutils.trim(self.page, "<th scope=\"row\">Studio:</th>\n\t<td>\n", "\t</td>")

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = ''

    def get_rating(self):
        self.rating = gutils.trim(self.page, ' alt="Ocena ', '/10')

    def get_notes(self):
        self.notes = "Czas trwania: " + gutils.trim(self.page,"<div class=\"sitem\">Czas trwania: <b>\n\t\t","\n</b>") + '\n'

        t = self.page.find("<tr><th scope=\"row\">Autor:</th>")
        if t != -1:
            self.notes += "Autor: %s\n" % gutils.trim(self.page[t:], "<td>\n", "\t</td>")

        t = self.page.find("<th scope=\"row\">Projekt:</th>")
        if t != -1:
            self.notes += "Projekt: %s\n" % gutils.trim(self.page[t:], "<td>\n", "\t</td>")

        t = self.page.find("<tr><th scope=\"row\">Scenariusz:</th>")
        if t != -1:
            self.notes += "Scenariusz: %s\n" % gutils.trim(self.page[t:], "<td>\n", "\t</td>")

        t = self.page.find("<th scope=\"row\">Muzyka:</th>")
        if t != -1:
            self.notes += "Muzyka: %s\n" % gutils.trim(self.page[t:], "<td>\n", "\t</td>")

        self.notes += "\n%s"  % gutils.trim(self.page,"<p class=\"dwazdania\">\n\t\t", "\n</p>")

class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.encode='UTF-8'
        self.original_url_search   = 'http://anime.tanuki.pl/strony/anime/lista/title/1/?&title='
        self.translated_url_search = 'http://anime.tanuki.pl/strony/anime/lista/title/1/?&title='

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        tmp = string.find(self.page, "<table class=\"animelist strippedlist\"")
        if tmp == -1:    # only one match!
            self.page = ''
        else:        # multiple matches
            self.page = gutils.trim(self.page,"<table class=\"animelist strippedlist\"", "</tbody>");
            self.page = gutils.after(self.page, "<tbody>")
        return self.page

    def get_searches(self):
        if self.page == '':    # immediately redirection to movie page
            self.number_results = 1
            self.ids.append(self.url)
            self.titles.append(gutils.convert_entities(self.title))
        else:            # multiple matches
            elements = string.split(self.page,"<tr")
            self.number_results = elements[-1]
            if (elements[0]<>''):
                for element in elements:
                    self.ids.append(gutils.trim(element, 'href="/strony/anime/', '" >'))
                    element = gutils.after(element," >\n\t")
                    element = element.replace("</a>\n\t</td>\n", " (")
                    element = element.replace("\t<td>", "")
                    element = element.replace("</td>\n", "; ")
                    element = element.replace("</tr>", "")
                    element = element[:len(element)-3] + ')'
                    self.titles.append(element)
            else:
                self.number_results = 0
