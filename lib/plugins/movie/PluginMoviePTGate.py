# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMoviePTGate.py 1513 2011-02-03 19:50:04Z iznogoud $'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ozarowski
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

plugin_name         = "PTGate"
plugin_description  = "Cinema PTGate"
plugin_url          = "cinema.ptgate.pt"
plugin_language     = _("Portuguese")
plugin_author       = "Vasco Nunes"
plugin_author_email = "<vasco.m.nunes@gmail.com>"
plugin_version      = "0.6"

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode   ='iso-8859-1'
        self.movie_id = id
        self.url      = "http://cinema.ptgate.pt/filmes/" + str(self.movie_id)

    def initialize(self):
        self.page = gutils.convert_entities(self.page)
        self.page = self.page.replace(u'\x93', u'"')
        self.page = self.page.replace(u'\x94', u'"')
        self.page = self.page.replace(u'\x96', u'-')

    def get_image(self):
        self.image_url = 'http://cinema.ptgate.pt/Movies/' + str(self.movie_id) + '.jpg'

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, u'<h2 class="title">', u'</h2>')
        self.o_title = self.o_title.encode(self.encode)

    def get_title(self):
        self.title = gutils.trim(self.page, u'<h1>', u' <small>')
        self.title = self.title.encode(self.encode)

    def get_director(self):
        self.director = gutils.trim(self.page, u'Realização:</b><br />', u'</p>')
        self.director = gutils.strip_tags(self.director)

    def get_plot(self):
        self.plot = gutils.trim(self.page, u'<h2>Sinopse</h2>', u'</div>')
        self.plot = self.plot.encode(self.encode)
        self.plot = string.replace(self.plot, "'", "\"")
        self.plot = string.replace(self.plot, "'", "\"")

    def get_year(self):
        self.year = gutils.trim(self.page, u'<b>Ano:</b> ', u'<br />')

    def get_runtime(self):
        self.runtime = ''

    def get_genre(self):
        self.genre = gutils.trim(self.page, u'<b>Género:</b> ', u'<br />')
        self.genre = self.genre.encode(self.encode)

    def get_cast(self):
        self.cast = gutils.trim(self.page, u'Intérpretes:</b><br />', u'</p>')
        self.cast = gutils.strip_tags(self.cast)
        self.cast = string.replace(self.cast, ', ', '\n')

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = ''

    def get_o_site(self):
        self.o_site = ''
        tmp = string.find(self.page, u'(site oficial)')
        if tmp >= 0:
            index = string.rfind(self.page[:tmp], u'<a href="')
            if index >= 0:
                self.o_site = gutils.before(self.page[index + 9:], '"')

    def get_site(self):
        self.site = ''
        tmp = string.find(self.page, u'www.imdb.com/title/')
        if tmp >= 0:
            self.site = u'http://www.imdb.com/title/' + gutils.before(self.page[tmp:], '"')

    def get_trailer(self):
        self.trailer = ''
        tmp = string.find(self.page, u'(trailers)')
        if tmp >= 0:
            index = string.rfind(self.page[:tmp], u'<a href="')
            if index >= 0:
                self.trailer = gutils.before(self.page[index + 9:], '"')

    def get_country(self):
        self.country = gutils.trim(self.page, u'<b>País:</b> ', '<br />')
        self.country = self.country.encode(self.encode)
        
    def get_notes(self):
        self.notes = ''

    def get_rating(self):
        self.rating = gutils.trim(self.page, u'alt="Visitantes" />', ' (<a href="/')
    	self.rating = gutils.strip_tags(self.rating)
    	self.rating = float(self.rating)
    	self.rating = round(self.rating * 2)

class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.original_url_search   = 'http://cinema.ptgate.pt/pesquisa/?q='
        self.translated_url_search = 'http://cinema.ptgate.pt/pesquisa/?q='
        self.encode                = 'iso-8859-1'

    def search(self,parent_window):
        self.open_search(parent_window)
        return self.page

    def get_searches(self):
        elements = string.split(self.page, '<a href="/filmes/')
        self.number_results = elements[-1]

        if len(elements[0]):
            for element in elements:
                id = gutils.digits_only(gutils.before(element, '"'))
                title = gutils.clean(re.sub('</div>.*', '', string.replace(gutils.before(gutils.after(element, '>'), '</small>'), '<small>', ' / ')))
                if id and title and title[0] != '<':
                    self.ids.append(id)
                    self.titles.append(gutils.convert_entities(title))
        else:
            self.number_results = 0