# -*- coding: utf-8 -*-

__revision__ = '$Id: PluginMovieFilmweb.py 1615 2012-01-10 20:58:15Z piotrek $'

# Copyright (c) 2005-2012 Piotr Ożarowski
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

plugin_name = 'Filmweb'
plugin_description = 'Web pełen filmów'
plugin_url = 'filmweb.pl'
plugin_url_other = 'filmweb.pl'
plugin_server = '193.200.227.13'
plugin_language = _('Polish')
plugin_author = 'Piotr Ożarowski, Bartosz Kurczewski, Mariusz Szczepanek'
plugin_author_email = '<mariusz2806@gmail.com>'
plugin_version = '1.29'


class Plugin(movie.Movie):
    def __init__(self, id):
        self.movie_id = 'filmweb'
        self.url = str(id)
        self.encode = 'utf-8'

    def get_image(self):
        if self.page.find('<div class=posterLightbox>') > -1:
            self.image_url = gutils.trim(self.page, '<div class=posterLightbox>', '</div>')
            self.image_url = gutils.trim(self.image_url, 'href="', '" ')
        else:
            self.image_url = ''

    def get_o_title(self):
        self.url = self.url.replace(plugin_server, plugin_url)
        self.o_title = gutils.trim(self.page, '<h2 class=origTitle>', '</h2>')
        self.o_title = gutils.after(self.o_title, '</span>')
        if self.o_title == '':
            self.o_title = gutils.trim(self.page, '<title>', '</title>')
            if self.o_title.find('(') > -1:
                self.o_title = gutils.before(self.o_title, '(')
            if self.o_title.find('/') > -1:
                self.o_title = gutils.before(self.o_title, '/')

    def get_title(self):
        self.url = self.url.replace(plugin_server, plugin_url)
        self.title = gutils.trim(self.page, '<title>', '</title>')
        if self.title.find('(') > -1:
            self.title = gutils.before(self.title, '(')
        if self.title.find('/') > -1:
            self.title = gutils.before(self.title, '/')

    def get_director(self):
        self.director = gutils.trim(self.page, "reżyseria:", '</tr>')
        self.director = gutils.after(self.director, '</th>')
        self.director = self.director.replace("(więcej...)", '')
        self.director = gutils.strip_tags(self.director)

    def get_screenplay(self):
        self.screenplay = gutils.trim(self.page, "scenariusz:", '</tr>')
        self.screenplay = gutils.after(self.screenplay, '</th>')
        self.screenplay = self.screenplay.replace("(więcej...)", '')
        self.screenplay = gutils.strip_tags(self.screenplay)

    def get_plot(self):
        self.plot = gutils.trim(self.page, '<span class=filmDescrBg property="v:summary">', '</span>')
        self.plot = self.plot.replace('  ', ' ')

    def get_year(self):
        self.year = gutils.trim(self.page, '<span id=filmYear class=filmYear>', '</span>')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, "czas trwania:", '</tr>')
        self.runtime = gutils.after(self.runtime, '<td>')
        self.runtime = gutils.before(self.runtime, '</td>')
        self.runtime = self.runtime.replace(' ', '')
        if not self.runtime:
            return
        str_m = ''
        str_h = ''
        if self.runtime.find('godz.') > -1:
            str_h = gutils.before(self.runtime, 'godz.')
            self.runtime = gutils.after(self.runtime, 'godz.')
        if self.runtime.find('min.') > -1:
            str_m = gutils.before(self.runtime, 'min.')
        val_runtime = 0
        if str_h:
            val_runtime = 60 * int(float(str_h))
        if str_m:
            val_runtime += int(float(str_m))
        self.runtime = val_runtime

    def get_genre(self):
        self.genre = gutils.trim(self.page, "gatunek:", '</tr>')

    def get_cast(self):
        self.cast = gutils.trim(self.page, '<div class="castListWrapper cl">', '<div class="additional-info comBox">')
        self.cast = gutils.before(self.cast, '</ul>')
        self.cast = self.cast.replace('</span> ', '')
        self.cast = self.cast.replace('<div>', _(" as "))
        self.cast = self.cast.replace('</li>', "\n")
        self.cast = gutils.strip_tags(self.cast)
        self.cast = self.cast.replace('   ', '')
        self.cast = self.cast.replace('  ', ' ')

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = ''

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = gutils.trim(self.page, 'produkcja:', '</tr>')

    def get_rating(self):
        self.rating = gutils.trim(self.page, '<div class=rates>', '</div>')
        self.rating = gutils.trim(self.rating, '<span property="v:average">', '</span>')
        if self.rating != '':
            self.rating = self.rating.replace(' ', '')
            self.rating = self.rating.replace(',', '.')
            self.rating = str(float(self.rating.strip()))

    def get_notes(self):
        self.notes = ''


class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.encode = 'utf-8'
        self.original_url_search = 'http://' + plugin_url_other + '/search/film?q='
        self.translated_url_search = 'http://' + plugin_url_other + '/search/film?q='

    def search(self, parent_window):
        if not self.open_search(parent_window):
            return None
        pos = self.page.find('Filmy (')
        if pos == -1:  # movie page
            self.page = None
        else:  # search results
            items = gutils.trim(self.page, 'Filmy (', ')')
            if items == '0':
                self.page = False
            else:
                self.page = gutils.after(self.page[pos:], '<ul id=searchFixCheck>')
                self.page = gutils.before(self.page, '</ul>')
        return self.page

    def get_searches(self):
        if self.page is None:  # movie page
            self.ids.append(self.url)
            self.titles.append(gutils.convert_entities(self.title))
        elif self.page is False:  # no movie found
            self.number_results = 0
        else:  # multiple matches
            elements = self.page.split('<li ')
            self.number_results = elements[-1]
            if elements != '':
                for element in elements:
                    if (element == ''):
                        continue
                    element = gutils.after(element, 'href="')
                    self.ids.append('http://' + plugin_url_other + gutils.before(element, '"'))
                    element_title = gutils.trim(element, '">', '</a>')
                    element_title = element_title.replace('\t', '')
                    element = gutils.after(element, 'class=searchResultDetails')
                    element_year = gutils.trim(element, '>', '|')
                    element_year = element_year.replace(" ", '')
                    element_year = gutils.strip_tags(element_year)
                    element_country = ''
                    pos_country = element.find('countryIds')
                    if pos_country != -1:
                        element_country = gutils.trim(element[pos_country:], '">', '</a>')
                    element = element_title.strip()
                    if element_year:
                        element += ' (' + element_year.strip() + ')'
                    if element_country:
                        element += ' - ' + element_country.strip()
                    element = gutils.convert_entities(element)
                    element = gutils.strip_tags(element)
                    self.titles.append(element)
            else:
                self.number_results = 0
