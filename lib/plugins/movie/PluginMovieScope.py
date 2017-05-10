# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieScope.py 1405 2010-03-02 21:26:35Z mikej06 $'

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

plugin_name         = "Scope"
plugin_description  = "Danmarks største filmguide"
plugin_url          = "www.scope.dk"
plugin_language     = _("Danish")
plugin_author       = "Michael Jahn"
plugin_author_email = "mike@griffith.cc"
plugin_version      = "1.0"


class Plugin(movie.Movie):

    def __init__(self, id):
        self.encode = 'iso-8859-1'
        self.movie_id = id
        self.url = 'http://www.scope.dk/film/' + str(self.movie_id)

    def get_image(self):
        self.image_url = ''
        tmp = gutils.trim(self.page, '<img src="http://www.scope.dk/images/', '"')
        if tmp:
            self.image_url = 'http://www.scope.dk/images/' + tmp

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, '<h2>', '</h2>')

    def get_title(self):
        self.title = gutils.trim(self.page, '<h2>', '</h2>')

    def get_director(self):
        self.director = gutils.trim(self.page, 'Instruktion</th>', '</td>')

    def get_plot(self):
        self.plot = gutils.trim(self.page, '<div id="film-top-middle">', '</div>')
        if self.plot:
            self.plot = string.replace(self.plot, '’', "'")
            self.plot = string.replace(self.plot, 'â€™', "'")
            self.plot = gutils.convert_entities(self.plot)

    def get_year(self):
        self.year = gutils.trim(self.page, 'Produktionsår</th>', '</td>')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, 'Spilletid</th>', '</td>')

    def get_genre(self):
        self.genre = gutils.trim(self.page, 'Genre</th>', '</td>')

    def get_cast(self):
        self.cast = ''
        tmp = gutils.trim(self.page, 'colspan="2">Medvirkende</th>', '<tr style')
        if tmp:
            tmpparts = string.split(tmp, '<tr')
            for tmppart in tmpparts[1:]:
                name = '<th' + gutils.trim(tmppart, '<td', '</')
                role = '<th' + gutils.trim(tmppart, '<th', '</')
                if name:
                    if role:
                        self.cast = self.cast + name + _(' as ') + role + '\n'
                    else:
                        self.cast = self.cast + name + '\n'

    def get_classification(self):
        self.classification = gutils.regextrim(self.page, 'Censur</th>', '</td>')

    def get_studio(self):
        self.studio = gutils.trim(self.page, 'Selskab</th>', '</td>')

    def get_o_site(self):
        self.o_site = ''
        tmp = gutils.trim(self.page, 'Link</th>', '</td>')
        if tmp:
            self.o_site = gutils.trim(tmp, 'href="', '"')

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ''
        tmp = gutils.trim(self.page, 'Trailer</th>', '</td>')
        if tmp:
            self.trailer = gutils.trim(tmp, 'href="', '"')

    def get_country(self):
        self.country = gutils.trim(self.page, 'Land</th>', '</td>')

    def get_rating(self):
        self.rating = 0
        tmp = gutils.trim(self.page, 'Scope-score</th>', '</td>')
        if tmp:
            fullstars = string.split(tmp, 'gul.gif')
            halfstars = string.split(tmp, 'gul_halv.gif')
            rating = 0
            if fullstars:
                rating = len(fullstars) - 1
            if halfstars and len(halfstars) > 1:
                rating = rating + 0.5
            try:
                self.rating = round(rating / 0.6, 0)
            except:
                pass

    def get_notes(self):
        self.notes = ''

    def get_screenplay(self):
        self.screenplay = gutils.regextrim(self.page, 'Manuskript</th>', '</td>')

    def get_cameraman(self):
        self.cameraman = gutils.regextrim(self.page, 'Fotografi</th>', '</td>')


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search = 'http://www.scope.dk/sogning_film.php?id=&filmtitel='
        self.translated_url_search = 'http://www.scope.dk/sogning_film.php?id=&filmtitel='
        self.encode = 'iso-8859-1'
        self.remove_accents = False

    def search(self, parent_window):
        self.open_search(parent_window)
        self.page = gutils.trim(self.page, '<table class="table-list">', '</table>')
        return self.page

    def get_searches(self):
        elements = string.split(self.page, 'href="film/')
        for element in elements[1:]:
            id = gutils.before(element, '"')
            title = gutils.trim(element, '>', '</a>')
            if id and title:
                self.ids.append(id)
                year = gutils.trim(element, '<td>', '</td>')
                if year:
                    self.titles.append(title + ' (' + year + ')')
                else:
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
        'Rocky'                : [ 8, 8 ]
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
        '4834-rocky-balboa' : {
            'title'               : 'Rocky Balboa',
            'o_title'             : 'Rocky Balboa',
            'director'            : 'Sylvester Stallone',
            'plot'                : True,
            'cast'                : 'Sylvester Stallone' + _(' as ') + 'Rocky Balboa\n\
Burt Young' + _(' as ') + 'Paulie\n\
Milo Ventimiglia' + _(' as ') + 'Rocky Balboa Jr.\n\
Geraldine Hughes' + _(' as ') + 'Marie\n\
Antonio Tarver' + _(' as ') + 'Mason \'The Line\' Dixon\n\
James Francis Kelly III' + _(' as ') + 'Steps\n\
Tony Burton' + _(' as ') + 'Duke\n\
Henry G. Sanders' + _(' as ') + 'Martin\n\
Talia Shire' + _(' as ') + 'Adrian\n\
Mike Tyson' + _(' as ') + 'Sig selv',
            'country'             : 'USA',
            'genre'               : 'Action, Drama',
            'classification'      : 'Tilladt for børn over 11 år',
            'studio'              : 'United Artists, Revolution Studios, Chartoff-Winkler Productions',
            'o_site'              : 'http://www.mgm.com/rocky',
            'site'                : 'http://www.scope.dk/film/4834-rocky-balboa',
            'trailer'             : 'http://www.imdb.com/title/tt0479143/trailers',
            'year'                : 2006,
            'notes'               : False,
            'runtime'             : 102,
            'image'               : True,
            'rating'              : 7,
            'cameraman'           : 'J. Clark Mathis',
            'screenplay'          : 'Sylvester Stallone'
        },
    }
