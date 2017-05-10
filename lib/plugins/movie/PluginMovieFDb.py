# -*- coding: utf-8 -*-

__revision__ = '$Id: PluginMovieFDb.py 1385 2010-01-06 19:47:44Z kura666 $'

# Copyright (c) 2006-2007 Piotr Ozarowski
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

plugin_name        = 'FDb'
plugin_description    = 'Internetowa baza filmowa'
plugin_url        = 'fdb.pl'
plugin_language        = _('Polish')
plugin_author        = 'Piotr Ożarowski, Bartosz Kurczewski'
plugin_author_email    = '<bartosz.kurczewski@gmail.com>'
plugin_version        = '1.16'

class Plugin(movie.Movie):
    TRAILER_PATTERN = re.compile('/film/.*/zwiastuny/odtwarzaj/[0-9]*')

    def __init__(self, movie_id):
        from md5 import md5
        self.movie_id = md5(movie_id).hexdigest()
        self.encode   = 'utf-8'
        if string.find(movie_id, 'http://') != -1:
            self.url = str(movie_id)
        else:
            self.url = "http://fdb.pl/%s" % str(movie_id)

    def get_image(self):
        self.image_url = gutils.trim(self.page, 'class="gfx-poster"', '/></a>')
        self.image_url = gutils.trim(self.image_url,'src="','"')
        if self.image_url.endswith('http://fdb.pl/images/fdb2/add_poster.png?1214306282'):
            self.image_url = ''

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, '<h2 class="after-title">', '</h2>')
        self.o_title = gutils.strip_tags(self.o_title)
        self.o_title = string.strip(self.o_title)
        if self.o_title == '':
            self.o_title = self.get_title(True)

    def get_title(self, extra=False):
        data = gutils.trim(self.page,'<h1 id="movie-title">', '</h1>')
        tmp = string.find(data, '(')
        if tmp != -1:
            data = data[:tmp]
        if extra is False:
            self.title = data
        else:
            return data

    def get_director(self):
        self.director = ''
        elements = gutils.trim(self.page,'>Reżyseria: </h4>','</div>')
        elements = string.split(elements, '</li>')
        if elements[0] != '':
            for element in elements:
                element = gutils.trim(element, '>', '</a')
                if element != '':
                    self.director += ', ' + element
            self.director = string.replace(self.director[2:], ', &nbsp;&nbsp;&nbsp;(więcej)', '')

    def get_screenplay(self):
        self.screenplay = ''
        elements = gutils.trim(self.page,'>Scenariusz: </h4>','</div>')
        elements = string.split(elements, '</li>')
        if elements[0] != '':
            for element in elements:
                element = gutils.trim(element, '>', '</a')
                if element != '':
                    self.screenplay += ', ' + element
            self.screenplay = string.replace(self.screenplay[2:], ', &nbsp;&nbsp;&nbsp;(więcej)', '')


    def get_plot(self):
        self.plot = gutils.trim(self.page,'Opis filmu','</div>')
        self.plot = gutils.trim(self.plot,'<p>',"\n\n")

    def get_year(self):
        self.year = gutils.trim(self.page,'<small>  (', ')</small>')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page,'Czas trwania: </h4>','</div>')
        self.runtime = gutils.trim(self.runtime,'<li>',' minut')

    def get_genre(self):
        self.genre = gutils.trim(self.page,'Gatunek: </h4>','</div>')
        self.genre = gutils.trim(self.genre,'<li>','</li>')
        self.genre = string.replace(self.genre, ' / ', ' | ')

    def get_cast(self):
        self.cast = gutils.trim(self.page,'<div class="cast">',"</div>")
        tmpcast = gutils.trim(self.cast,"<table>\n",'</table>')
        if tmpcast == '':
            tmpcast = tmpcast = gutils.trim(self.cast,"<table>\n",'<div class="line">')
        self.cast = tmpcast   
        if self.cast != '':
            self.cast = gutils.strip_tags(self.cast)
            self.cast = self.cast.replace("      ","")
            self.cast = self.cast.replace("    ","")
            self.cast = self.cast.replace("\n...\n\n  ",_(' as '))
            self.cast = self.cast.replace("\n\n\n\n\n","")

    def get_classification(self):
        self.classification = gutils.trim(self.page,"Od lat: </h4>","</div>")
        self.classification = gutils.trim(self.classification,'<li>','</li>')

    def get_studio(self):
        self.studio = ''

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        trailer_url = self.TRAILER_PATTERN.findall(self.page)
        if trailer_url:
            self.trailer = 'http://fdb.pl' + trailer_url[0]

    def get_country(self):
        self.country = gutils.trim(self.page,'Kraj produkcji: </h4>','</div>')
        self.country = gutils.trim(self.country,'<li>','</li>')

    def get_rating(self):
        self.rating = gutils.trim(self.page, 'class="vote"','/10</strong>')
        self.rating = gutils.after(self.rating, '<strong>')
        if self.rating:
            self.rating = str(float(gutils.clean(self.rating)))

class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.encode = 'utf-8'
        self.original_url_search    = 'http://fdb.pl/szukaj/movies?query='
        self.translated_url_search    = 'http://fdb.pl/szukaj/movies?query='

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        tmp = string.find(self.page,'<h1>Wyniki wyszukiwania dla')
        if tmp == -1:        # already a movie page
            self.page = ''
        else:            # multiple matches
            self.page = gutils.before(self.page[tmp:],'>Mapa strony</h3>');
        return self.page

    def get_searches(self):
        if self.page == '':    # movie page already
            self.number_results = 1
            self.ids.append(self.url)
            self.titles.append(self.title)
        else:            # multiple matches
            elements = string.split(self.page,'<div class="content">')
            if len(elements)>1:
                for element in elements:
                    tmpId = gutils.trim(element, '<a href="', '"')
                    if tmpId.startswith('/szukaj'):
                        continue
                    self.ids.append(tmpId)
                    element = gutils.strip_tags(
                        gutils.trim(element, '">', '</div>'))
                    element = element.replace("\n", '')
                    element = element.replace('   ', '')
                    element = element.replace('aka ', ' aka ')
		    element = element.replace('{{rate}}', ' ')
                    element = element.replace(' - Oryginalny', '')
                    self.titles.append(element)
            else:
                self.number_results = 0
