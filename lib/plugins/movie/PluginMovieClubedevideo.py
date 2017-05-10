# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2010
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

plugin_name         = "Clubedevideo"
plugin_description  = "www.clubedevideo.com"
plugin_url          = "www.clubedevideo.com"
plugin_language     = _("Portuguese")
plugin_author       = "Michael Jahn"
plugin_author_email = "mike@griffith.cc"
plugin_version      = "1.0"


class Plugin(movie.Movie):

    def __init__(self, id):
        self.encode = 'iso-8859-1'
        self.movie_id = id
        self.url = 'http://www.clubedevideo.com/mods/ficha_filme_if.cdv?numero_filme=%s' % self.movie_id

    def get_image(self):
        self.image_url = 'http://www.clubedevideo.com/capas/%s.jpg' % self.movie_id

    def get_o_title(self):
        self.o_title = gutils.after(gutils.trim(self.page, "class='mod_titulos_filme2'", '<'), '>')

    def get_title(self):
        self.title = gutils.after(gutils.trim(self.page, "class='mod_titulos_filme'", '<'), '>')

    def get_director(self):
        self.director = gutils.trim(self.page, u'Realização:', '<br>')
        self.director = string.replace(self.director, '&nbsp', '') # website error, ; missing

    def get_plot(self):
        self.plot = gutils.trim(self.page, u'Sinópse:', '</td>')
        self.plot = string.replace(self.plot, u'\x93', '"')
        self.plot = string.replace(self.plot, u'\x94', '"')

    def get_year(self):
        self.year = ''

    def get_runtime(self):
        self.runtime = gutils.clean(gutils.trim(self.page, u'Duração:', '<br'))

    def get_genre(self):
        self.genre = gutils.trim(self.page, 'Categoria:', '<br')

    def get_cast(self):
        self.cast = gutils.clean(gutils.trim(self.page, 'Protagonistas:', '<br'))
        # double replacement
        self.cast = string.replace(self.cast, ', ', '\n')
        self.cast = string.replace(self.cast, ',', '\n')

    def get_classification(self):
        self.classification = gutils.regextrim(self.page, u'Classificação:', '<br>')

    def get_studio(self):
        self.studio = gutils.trim(self.page, 'Distribuidora:', '<br>')

    def get_o_site(self):
        self.o_site = gutils.trim(self.page, 'website.cdv?path=', "'")

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = 'http://www.clubedevideo.com/mods/mod_trailer.cdv?numero=%s' % self.movie_id

    def get_country(self):
        self.country = ''

    def get_rating(self):
        self.rating = 0
        tmp = gutils.trim(self.page, 'Votação:', '</td>')
        if tmp:
            fullstars = string.split(tmp, 'star_on.gif')
            halfstars = string.split(tmp, 'star_meia')
            rating = 0
            if fullstars:
                rating = len(fullstars) - 1
            if halfstars and len(halfstars) > 1:
                rating = rating + 0.5
            try:
                self.rating = round(rating * 2, 0)
            except:
                pass

    def get_notes(self):
        self.notes = ''

    def get_screenplay(self):
        self.screenplay = ''

    def get_cameraman(self):
        self.cameraman = ''


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search = 'http://www.clubedevideo.com/mods/mod_pesquisa_if.cdv?area_pesquisa=nome_original&submitButtonName=++OK++&valor_pesquisa='
        self.translated_url_search = 'http://www.clubedevideo.com/mods/mod_pesquisa_if.cdv?area_pesquisa=nome&submitButtonName=++OK++&valor_pesquisa='
        self.encode = 'iso-8859-1'
        self.remove_accents = False

    def search(self, parent_window):
        self.open_search(parent_window)
        return self.page

    def get_searches(self):
        elements = string.split(self.page, "href='ficha_filme_if.cdv?numero_filme=")
        for element in elements[1:]:
            id = gutils.before(element, "'")
            title = gutils.trim(element, '>', '</a>')
            if id and title:
                self.ids.append(id)
                self.titles.append(title)

#
# Plugin Test
#


class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky' : [ 9, 9 ]
    }


class PluginTest:
    #
    # Configuration for automated tests:
    # dict { movie_id -> dict { arribute -> value } }
    #
    # value: * True/False if attribute only should be tested for any value
    #        * or the expected value
    #
    test_configuration = {
        '9384' : {
            'title'               : 'Rocky Balboa',
            'o_title'             : 'Rocky Balboa - 2006',
            'director'            : 'Sylvester Stallone',
            'plot'                : True,
            'cast'                : 'Sylvester Stallone\n\
Burt Young\n\
Tony Burton\n\
MiloVentimiglia',
            'country'             : False,
            'genre'               : 'Acção',
            'classification'      : 'M/12',
            'studio'              : 'Lusomundo',
            'o_site'              : 'http://www.mgm.com/rocky/',
            'site'                : 'http://www.clubedevideo.com/mods/ficha_filme_if.cdv?numero_filme=9384',
            'trailer'             : 'http://www.clubedevideo.com/mods/mod_trailer.cdv?numero=9384',
            'year'                : False,
            'notes'               : False,
            'runtime'             : 102,
            'image'               : True,
            'rating'              : 5,
            'cameraman'           : False,
            'screenplay'          : False
        },
    }
