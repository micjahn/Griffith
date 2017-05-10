# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2009
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

import gutils, movie
import string, re
import urllib, httplib
try:
    import simplejson as json
except:
    import json

plugin_name         = 'MovieMeter'
plugin_description  = 'de filmsite voor liefhebbers'
plugin_url          = 'www.moviemeter.nl'
plugin_language     = _('Dutch')
plugin_author       = 'Michael Jahn'
plugin_author_email = 'griffith@griffith.cc'
plugin_version      = '2.0'
# API key created for Griffith
moviemeter_api_key  = '6h70thfmkwhq55hst69gnr65ckbaqu6h'

class Plugin(movie.Movie):

    def __init__(self, id):
        self.encode   = 'iso8859-1'
        self.movie_id = id
        # only for user visible url field, fetching is based on the REST API
        self.url      = "http://www.moviemeter.nl/film/%s" % str(self.movie_id)
        self.useurllib2 = True

    def open_page(self, parent_window=None, url=None):
        url = 'http://www.moviemeter.nl/api/film/' + self.movie_id +'&api_key=' + moviemeter_api_key
        self.page = movie.Movie.open_page(self, parent_window, url)
        return self.page
    
    def initialize(self):
        self.movie = json.JSONDecoder().decode(self.page)

    def get_image(self):
        self.image_url = self.movie['posters']['large']

    def get_o_title(self):
        self.o_title = self.movie['title']

    def get_title(self):
        self.title = self.movie['title']

    def get_director(self):
        self.director = string.join(self.movie['directors'], ', ')

    def get_plot(self):
        self.plot = self.movie['plot']

    def get_year(self):
        self.year = self.movie['year']

    def get_runtime(self):
        self.runtime = self.movie['duration']

    def get_genre(self):
        self.genre = string.join(self.movie['genres'], ', ')

    def get_cast(self):
        self.cast = ''
        for element in self.movie['actors']:
            self.cast = self.cast + element['name'] + '\n'

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = ''

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = self.movie['url']

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = string.join(self.movie['countries'], ', ')

    def get_rating(self):
        try:
            self.rating = round(float(self.movie['average']) * 2.0)
        except:
            self.rating = 0

    def get_notes(self):
        self.notes = 'Alternatieve titel:\n' + self.movie['alternative_title']


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search   = 'http://www.moviemeter.nl/api/film/?api_key=' + moviemeter_api_key + '&q='
        self.translated_url_search = 'http://www.moviemeter.nl/api/film/?api_key=' + moviemeter_api_key + '&q='
        self.encode                = 'iso8859-1'
        self.useurllib2 = True
        
    def search(self, parent_window):
        if not self.open_search(parent_window):
            return None
        return self.page
    
    def get_searches(self):
        result = json.JSONDecoder().decode(self.page)
        try:
            for movie in result:
                try:
                    title = ''
                    year = ''
                    if 'title' in movie:
                        title = movie['title']
                    elif 'alternative_title' in movie:
                        title = movie['alternative_title']
                    if 'year' in movie:
                        year = '(%s)' % movie['year']
                    self.titles.append('%s %s' % (title, year))
                    self.ids.append(movie['id'])
                except:
                    log.exception('')
        except:
            log.exception('')
            log.error(self.page)


#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa'         : [ 1, 1 ],
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
        '1017' : { 
            'title'             : 'Rocky II',
            'o_title'           : 'Rocky II',
            'director'          : 'Sylvester Stallone',
            'plot'              : True,
            'cast'              : 'Sylvester Stallone\n\
Talia Shire\n\
Carl Weathers',
            'country'           : 'Verenigde Staten',
            'genre'             : 'Actie, Drama',
            'classification'    : False,
            'studio'            : False,
            'o_site'            : False,
            'site'              : 'http://www.moviemeter.nl/film/1017',
            'trailer'           : False,
            'year'              : 1979,
            'notes'             : 'Alternatieve titel:\n\
De Uitdager',
            'runtime'           : 119,
            'image'             : True,
            'rating'            : 7
        },
    }
