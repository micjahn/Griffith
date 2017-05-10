# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2011 Ivo Nunes
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
import urllib

plugin_name         = "IMDb-pt"
plugin_description  = "Internet Movie Database Portuguese"
plugin_url          = "www.imdb.pt"
plugin_language     = _("Portuguese")
plugin_author       = "Ivo Nunes"
plugin_author_email = "<netherblood@gmail.com>"
plugin_version      = "0.1"

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode   ='iso-8859-1'
        self.movie_id = id
        self.url      = "http://www.imdb.pt/title/tt" + str(self.movie_id)

    def initialize(self):
        self.page = gutils.convert_entities(self.page)
        self.cast_page = self.open_page(url=self.url + '/fullcredits')
        self.cast_page = gutils.convert_entities(self.cast_page)
        self.plot_page = self.open_page(url=self.url + '/plotsummary')
        self.plot_page = gutils.convert_entities(self.plot_page)

    def get_image(self):
        self.image_url = gutils.trim(self.page, u'src="http://ia.media-imdb.com/images/', u'.jpg" /></a>')
        self.image_url = "http://ia.media-imdb.com/images/" + self.image_url + ".jpg"
        
    def get_title(self):
        self.title = gutils.trim(self.page, u'<title>', u' (')
        self.title = self.title.encode(self.encode)

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, u'Conhecido Como:</h5><div class="info-content">"', u'"')
        self.o_title = self.o_title.encode(self.encode)

    def get_director(self):
        self.director = gutils.trim(self.page, u'<h5>Diretor:</h5>', u'</a><br/>')
        self.director = gutils.strip_tags(self.director)

    def get_plot(self):
        self.plot = gutils.trim(self.plot_page, u'<div id="swiki.2.1">', u'</div>')
        self.plot = gutils.strip_tags(self.plot)
        self.plot = self.plot.encode(self.encode)

    def get_year(self):
        self.year = gutils.trim(self.page, u' (', u')</title>')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, u'<h5>Duração:</h5><div class="info-content">', u' min')
        self.runtime = self.runtime.encode(self.encode)

    def get_genre(self):
        self.genre = gutils.trim(self.page, u'<h5>Gênero:</h5>', u'</div>')
        self.genre = gutils.strip_tags(self.genre)
        self.genre = string.replace(self.genre, " | ", ", ")
        self.genre = self.genre.encode(self.encode)

    def get_cast(self):
        self.cast = ''
        self.cast = gutils.trim(self.cast_page, '<table class="cast">', '</table>')
        if self.cast == '':
            self.cast = gutils.trim(self.page, '<table class="cast">', '</table>')
        self.cast = string.replace(self.cast, ' ... ', _(' como ').encode('utf8'))
        self.cast = string.replace(self.cast, '...', _(' como ').encode('utf8'))
        self.cast = string.replace(self.cast, '</tr><tr>', "\n")
        self.cast = re.sub('</tr>[ \t]*<tr[ \t]*class="even">', "\n", self.cast)
        self.cast = re.sub('</tr>[ \t]*<tr[ \t]*class="odd">', "\n", self.cast)
        self.cast = self.__before_more(self.cast)
        self.cast = re.sub('[ ]+', ' ', self.cast)

    def get_classification(self):
        self.classification = gutils.trim(self.page, u'<h5>Certificação:</h5><div class="info-content">', u'</div>')
        self.classification = gutils.strip_tags(self.classification)
        self.classification = string.replace(self.classification, " | ", ", ")
        self.classification = self.classification.encode(self.encode)

    def get_studio(self):
        self.studio = gutils.trim(self.page, u'<h5>Companhia :</h5><div class="info-content">', u'Exibir mais</a>')
        self.studio = gutils.strip_tags(self.studio)
        self.studio = self.studio.encode(self.encode)

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = "http://www.imdb.com/title/" + str(self.movie_id) + "/trailers"

    def get_country(self):
        self.country = gutils.trim(self.page, u'<h5>País:</h5><div class="info-content">', '</div>')
        self.country = string.replace(self.country, " | ", ", ")
        self.country = self.country.encode(self.encode)
        
    def get_notes(self):
        self.notes = ''

    def get_rating(self):
        self.rating = gutils.trim(self.page, u'<div class="starbar-meta">', '/10')
        self.rating = gutils.strip_tags(self.rating)
        self.rating = string.replace(self.rating, ",", ".")
        if self.rating:
            self.rating = float(self.rating)
            self.rating = round(self.rating)

    def get_screenplay(self):
        self.screenplay = ''
        parts = re.split('<a href=', gutils.trim(self.cast_page, u'>Créditos como roteirista<', '</table>'))
        if len(parts) > 1:
            for part in parts[1:]:
                screenplay = gutils.trim(part, '>', '<')
                if screenplay == 'WGA':
                    continue
                screenplay = screenplay.replace(' (escrito por)', '')
                screenplay = screenplay.replace(' and<', '<')
                self.screenplay = self.screenplay + screenplay + ', '
            if len(self.screenplay) > 2:
                self.screenplay = self.screenplay[0:len(self.screenplay) - 2]

    def get_cameraman(self):
        self.cameraman = string.replace('<' + gutils.trim(self.cast_page, u'>Direção de Fotografia de<', '</table>'), u'(diretor de fotografia) ', '')

    def __before_more(self, data):
        for element in [u'>Exibir mais<', '>Full summary<', '>Full synopsis<']:
            tmp = string.find(data, element)
            if tmp>0:
                data = data[:tmp] + '>'
        return data

class SearchPlugin(movie.SearchMovie):
    PATTERN = re.compile(r"""<a href=['"]/title/tt([0-9]+)/[^>]+[>](.*?)</td>""")

    def __init__(self):
        self.original_url_search   = 'http://www.imdb.pt/find?s=tt&q='
        self.translated_url_search = 'http://www.imdb.pt/find?s=tt&q='
        self.encode                = 'utf8'

    def search(self, parent_window):
        """Perform the web search"""
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        """Try to find both id and film title for each search result"""
        elements = string.split(self.page, '<tr')
        if len(elements):
            for element in elements[1:]:
                match = self.PATTERN.findall(element)
                if len(match) > 1:
                    tmp = re.sub('^[0-9]+[.]', '', gutils.clean(match[1][1]))
                    self.ids.append(match[1][0])
                    self.titles.append(tmp)