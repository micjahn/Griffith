# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieKinoDe.py 1643 2013-02-21 19:51:43Z mikej06 $'

# Copyright (c) 2006-2011
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
import logging
import json

plugin_name         = "Kino.de"
plugin_description  = "KINO.DE"
plugin_url          = "www.kino.de"
plugin_language     = _("German")
plugin_author       = "Michael Jahn"
plugin_author_email = "<mikej06@hotmail.com>"
plugin_version      = "1.22"

log = logging.getLogger("Griffith")

class Plugin(movie.Movie):
    
    def __init__(self, id):
        self.encode='utf-8'
        self.movie_id = id
        self.url = self.movie_id
        log.info(self.url)
    
    def initialize(self):
        try:
            self.jsondata = json.loads(gutils.trim(gutils.after(self.page, '<body'), '<script type="application/ld+json">', '</script>'))
        except:
            self.jsondata = {}
        
    def get_image(self):
        self.image_url = ''
        try:
            self.image_url = self.jsondata['image']
        except:
            None

    def get_o_title(self):
        self.o_title = gutils.before(gutils.after(gutils.trim(self.page, 'property="og:title"', '/>'), 'content="'), '"')

    def get_title(self):
        self.title = gutils.before(gutils.after(gutils.trim(self.page, 'property="og:title"', '/>'), 'content="'), '"')

    def get_director(self):
        self.director = ''
        try:
            for person in self.jsondata['director']:
                self.director = self.director + ', ' + person['name']
            self.director = self.director[2:]
        except:
            None

    def get_plot(self):
        self.plot = gutils.after(gutils.trim(self.page, 'class="movie-plot-synopsis"', '</section>'), '>')
        start = string.find(self.plot, '<script')
        end = string.find(self.plot, '</script>', start)
        while start > -1 and end > -1:
            self.plot = self.plot[:start]+self.plot[end:]
            start = string.find(self.plot, '<script')
            end = string.find(self.plot, '</script>', start)
        self.plot = string.replace(self.plot, '\n', '')

    def get_year(self):
        self.year = '0'
        try:
            self.year = gutils.trim(self.page, '"published_date": "', '-')
        except:
            None

    def get_runtime(self):
        self.runtime = '0'
        tmp = gutils.clean(gutils.trim(self.page, '>Dauer</dt>', '</dd>'))
        if tmp:
            hours = gutils.trim(tmp, '>', 'h')
            if not hours:
                hours = 0
            minutes = gutils.trim(tmp, 'h', 'min')
            if not minutes:
                minutes = gutils.before(tmp, 'Min')
            try:
                self.runtime = int(hours) * 60 + int(minutes)
            except:
                None

    def get_genre(self):
        self.genre = gutils.trim(self.page, '<dt>Genre</dt>', '</dd>')

    def get_cast(self):
        self.cast = ''
        try:
            for person in self.jsondata['actor']:
                self.cast = self.cast + '\r\n' + person['name']
            self.cast = self.cast[2:]
        except:
            None

    def get_classification(self):
        self.classification = gutils.trim(self.page, '>FSK</dt>', '</dd>')

    def get_studio(self):
        self.studio = gutils.trim(self.page, '<dt>Vertrieb</dt>', '</dd>')

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = self.movie_id

    def get_trailer(self):
        self.trailer = ''
        try:
            self.trailer = self.jsondata['trailer']['embedUrl']
            if self.trailer:
                self.trailer = 'http:' + self.trailer
        except:
            None

    def get_country(self):
        self.country = gutils.regextrim(self.page, '<dt>Produktionsland</dt>[^<]*<dd>', '</dd>')

    def get_rating(self):
        self.rating = 0
        try:
            self.rating = int(self.jsondata['aggregateRating']['ratingValue']) * 2
        except:
            None

    def get_notes(self):
        self.notes = ''

    def get_screenplay(self):
        self.screenplay = ''
        tmp = gutils.regextrim(gutils.trim(self.page, 'id="person-collection"', '</section>'), 'Drehbuch[^<]*[<][/]h3[>]', '[<]h3')
        tmpelements = re.split('href="', tmp)
        delimiter = ''
        for index in range(1, len(tmpelements), 1):
            tmpelement = gutils.before(gutils.after(gutils.after(tmpelements[index], '"'), '>'), '<')
            tmpelement = re.sub('<small[^>]*>[^<]*</small>', '', tmpelement)
            tmpelement = gutils.strip_tags(tmpelement)
            tmpelement = string.replace(tmpelement, '\n', '')
            tmpelement = re.sub('[ \t]+', ' ', tmpelement)
            self.screenplay = self.screenplay + tmpelement + delimiter
            delimiter = ', '
            
    def get_cameraman(self):
        self.cameraman = ''
        tmp = gutils.regextrim(gutils.trim(self.page, 'id="person-collection"', '</section>'), 'Kamera[^<]*[<][/]h3[>]', '<h3')
        tmpelements = re.split('href="', tmp)
        delimiter = ''
        for index in range(1, len(tmpelements), 1):
            tmpelement = gutils.before(gutils.after(gutils.after(tmpelements[index], '"'), '>'), '<')
            tmpelement = re.sub('<small[^>]*>[^<]*</small>', '', tmpelement)
            tmpelement = gutils.strip_tags(tmpelement)
            tmpelement = string.replace(tmpelement, '\n', '')
            tmpelement = re.sub('[ \t]+', ' ', tmpelement)
            self.cameraman = self.cameraman + tmpelement + delimiter
            delimiter = ', '


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search   = 'http://www.kino.de/'# compatibility pre 0.13.1
        self.translated_url_search = 'http://www.kino.de/'# compatibility pre 0.13.1
        self.real_url_search = 'http://www.kino.de/se/%s/?sp_search_filter=movie'# compatibility pre 0.13.1
        self.encode='utf-8'
        self.remove_accents = False
        
    def search(self,parent_window):
        self.url = self.real_url_search # compatibility pre 0.13.1
        self.open_search(parent_window)
        pagemovie = self.page
        #
        # Sub Pages
        #
        pagesarea = gutils.trim(pagemovie, 'class="pagination-list"', '</ol>')
        pagelements = re.split('href="', pagesarea)
        self.title = ''
        self.o_title = ''
        for index in range(1, len(pagelements), 1):
            pagelement = pagelements[index]
            self.url = gutils.before(pagelement, '"')
            self.open_search(parent_window)
            if self.page:
                pagemovie = pagemovie + gutils.trim(self.page, '<ul>', '</ul>')
        self.page = pagemovie

        return self.page

    def get_searches(self):
        elements = re.split('class="card-link', self.page)
        elements[0] = None
        for element in elements:
            if element <> None:
                element = gutils.trim(element, 'href="', '</a>')
                url = gutils.before(element, '"')
                title = gutils.after(element, '>')
                self.ids.append(url)
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
        'Rocky Balboa'         : [ 10, 10 ],
        'Arahan'               : [ 10, 10 ],
        'Ein glückliches Jahr' : [ 4, 4 ]
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
        'K_rocky-balboa/96132.html' : {
            'title'               : 'Rocky Balboa',
            'o_title'             : 'Rocky Balboa',
            'director'            : 'Sylvester Stallone',
            'plot'                : True,
            'cast'                : 'Sylvester Stallone' + _(' as ') + 'Rocky Balboa\n\
Antonio Traver' + _(' as ') + 'Mason "The Line" Dixon\n\
Burt Young' + _(' as ') + 'Paulie\n\
Geraldine Hughes' + _(' as ') + 'Marie\n\
Milo Ventimiglia' + _(' as ') + 'Rocky Jr.\n\
James Francis Kelly III' + _(' as ') + 'Steps\n\
Tony Burton' + _(' as ') + 'Duke\n\
A.J. Benza' + _(' as ') + 'L.C.',
            'country'             : 'USA',
            'genre'               : 'Drama',
            'classification'      : '12',
            'studio'              : 'Fox',
            'o_site'              : False,
            'site'                : 'http://www.kino.de/kinofilm/rocky-balboa/96132.html',
            'trailer'             : 'http://www.kino.de/kinofilm/rocky-balboa/trailer/96132.html',
            'year'                : 2007,
            'notes'               : False,
            'runtime'             : 102,
            'image'               : True,
            'rating'              : False,
            'cameraman'           : 'J. Clark Mathis',
            'screenplay'          : 'Sylvester Stallone'
        },
        'K_ein-glueckliches-jahr/28675.html' : {
            'title'               : 'Ein glückliches Jahr',
            'o_title'             : 'La bonne année',
            'director'            : 'Claude Lelouch',
            'plot'                : True,
            'cast'                : 'Lino Ventura\n\
Françoise Fabian\n\
Charles Gérard\n\
André Falcon',
            'country'             : 'Frankreich/Italien',
            'genre'               : 'Drama',
            'classification'      : '12',
            'studio'              : 'Columbia TriStar',
            'o_site'              : False,
            'site'                : 'http://www.kino.de/kinofilm/ein-glueckliches-jahr/28675.html',
            'trailer'             : 'http://www.kino.de/kinofilm/ein-glueckliches-jahr/trailer/28675.html',
            'year'                : 1973,
            'notes'               : False,
            'runtime'             : 115,
            'image'               : True,
            'rating'              : False,
            'cameraman'           : 'Jean Collomb',
            'screenplay'          : 'Claude Lelouch'
        },
        'V_ein-glueckliches-jahr-dvd/85546.html' : {
            'title'               : 'Ein glückliches Jahr',
            'o_title'             : 'La bonne année',
            'director'            : 'Claude Lelouch',
            'plot'                : True,
            'cast'                : 'Lino Ventura\n\
Françoise Fabian\n\
Charles Gérard\n\
André Falcon',
            'country'             : 'Frankreich/Italien',
            'genre'               : 'Drama',
            'classification'      : 'ab 12',
            'studio'              : 'Black Hill Pictures',
            'o_site'              : False,
            'site'                : 'http://www.video.de/videofilm/ein-glueckliches-jahr-dvd/85546.html',
            'trailer'             : False,
            'year'                : 1973,
            'notes'               : 'Sprachen:\n\
Deutsch DD 2.0, Französisch DD 2.0\n\
\n\
Tonformat:\n\
Dolby Digital 2.0\n\
\n\
Bildformat:\n\
1:1,33/4:3',
            'runtime'             : 110,
            'image'               : True,
            'rating'              : False,
            'cameraman'           : 'Jean Collomb',
            'screenplay'          : 'Claude Lelouch'
        },
        'V_arahan-vanilla-dvd/90405.html' : {
            'title'               : 'Arahan',
            'o_title'             : 'Arahan jangpung dae jakjeon',
            'director'            : 'Ryoo Seung-wan',
            'plot'                : True,
            'cast'                : 'Ryu Seung-beom' + _(' as ') + 'Sang-hwan\n\
Yoon So-yi' + _(' as ') + 'Wi-jin\n\
Ahn Sung-kee' + _(' as ') + 'Ja-woon\n\
Jung Doo-hong' + _(' as ') + 'Heuk-woon\n\
Yun Ju-sang' + _(' as ') + 'Mu-woon',
            'country'             : 'Südkorea',
            'genre'               : 'Action/ Komödie',
            'classification'      : 'ab 16',
            'studio'              : 'Splendid Film',
            'o_site'              : False,
            'site'                : 'http://www.video.de/videofilm/arahan-vanilla-dvd/90405.html',
            'trailer'             : False,
            'year'                : 2004,
            'notes'               : 'Sprachen:\n\
Deutsch DD 5.1\n\
\n\
Tonformat:\n\
Dolby Digital 5.1\n\
\n\
Bildformat:\n\
1:1,78/16:9',
            'runtime'             : 108,
            'image'               : True,
            'rating'              : False,
            'cameraman'           : 'Lee Jun-gyu',
            'screenplay'          : 'Ryoo Seung-wan'
        }
    }
