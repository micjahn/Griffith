# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieAllocine.py 1655 2013-11-12 21:52:22Z mikej06 $'

# Copyright (c) 2005-2012 Vasco Nunes, Piotr Ozarowski
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, orprint
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

from datetime import date
import hashlib
import base64
import string
import urllib
import movie
try:
    import simplejson as json
except:
    import json
import logging
log = logging.getLogger("Griffith")

plugin_name         = "Allocine"
plugin_description  = "Internet Movie Database"
plugin_url          = "www.allocine.fr"
plugin_language     = _("French")
plugin_author       = "Pierre-Luc Levy, Michael Jahn (JSON api)"
plugin_author_email = ""
plugin_version      = "1.2"


class Plugin(movie.Movie):
    def __init__(self, id):
        self.movie_id = id
        self.query    = "partner=100043982026&format=json&profile=large&code=%s" % str(self.movie_id)
        self.url      = "http://api.allocine.fr/rest/v3/movie?"
        self.encode   = 'utf-8'
        self.useurllib2 = True

    def open_page(self, parent_window=None, url=None):
        query = self.query + '&sed=' + date.today().strftime("%Y%m%d")
        to_signature = '29d185d98c984a359e6e6f26a0474269' + query
        signature = urllib.quote_plus(base64.b64encode(hashlib.sha1(to_signature).digest()))
        url = self.url + query + '&sig=' + signature
        self.page = movie.Movie.open_page(self, parent_window, url)
        return self.page
        
    def initialize(self):
        self.movie = json.JSONDecoder().decode(self.page)['movie']

    def get_image(self):
        self.image_url = ''
        if 'poster' in self.movie:
            self.image_url = self.movie['poster']['href']

    def get_o_title(self):
        self.o_title = ''
        if 'originalTitle' in self.movie:
            self.o_title = self.movie['originalTitle']
        elif 'title' in self.movie:
            self.o_title = self.movie['title']

    def get_title(self):
        self.title = ''
        if 'title' in self.movie:
            self.title = self.movie['title']
        elif 'originalTitle' in self.movie:
            self.title = self.movie['originalTitle']

    def get_director(self):
        self.director = self.buildfromcast(8002)

    def get_plot(self):
        self.plot = ''
        if 'synopsis' in self.movie:
            self.plot = self.movie['synopsis']

    def get_year(self):
        self.year = ''
        if 'productionYear' in self.movie:
            self.year = self.movie['productionYear']

    def get_runtime(self):
        self.runtime = ''
        if 'runtime' in self.movie:
            self.runtime = self.movie['runtime'] / 60

    def get_genre(self):
        self.genre = ''
        if 'genre' in self.movie:
            for genre in self.movie['genre']:
                self.genre = self.genre + genre['$'] + ', '
        if self.genre:
            self.genre = self.genre[:-2]

    def get_cast(self):
        self.cast = ''
        if 'castMember' in self.movie:
            for cast in self.movie['castMember']:
                if 'activity' in cast:
                    activity = cast['activity']
                    if 'code' in activity:
                        if activity['code'] == 8001:
                            if 'role' in cast:
                                self.cast = self.cast + cast['person']['name'] + _(' as ') + cast['role'] + '\n'
                            else:
                                self.cast = self.cast + cast['person']['name'] + '\n'

    def get_classification(self):
        self.classification = ""
        if 'movieCertificate' in self.movie:
            self.classification = self.movie['movieCertificate']['certificate']['$']

    def get_studio(self):
        self.studio = ""

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = "http://www.allocine.fr/film/fichefilm_gen_cfilm=%s.html" % self.movie_id
        if 'link' in self.movie:
            for link in self.movie['link']:
                if link['rel'] == 'aco:more':
                    self.site = link['href']

    def get_trailer(self):
        self.trailer = "http://www.allocine.fr/film/video_gen_cfilm=%s.html" % self.movie_id
        if 'trailer' in self.movie:
            self.trailer = self.movie['trailer']['href']

    def get_country(self):
        self.country = ''
        if 'nationality' in self.movie:
            for country in self.movie['nationality']:
                self.country = self.country + country['$'] + ', '
        if self.country:
            self.country = self.country[:-2]

    def get_rating(self):
        self.rating = 0
        if 'statistics' in self.movie:
            statistics = self.movie['statistics']
            if 'pressRating' in statistics:
                self.rating = statistics['pressRating'] * 2
            elif 'userRating' in statistics:
                self.rating = statistics['userRating'] * 2

    def get_screenplay(self):
        self.screenplay = self.buildfromcast(8004)

    def get_cameraman(self):
        self.cameraman = self.buildfromcast(8037)

    def buildfromcast(self, code):
        result = ''
        if 'castMember' in self.movie:
            for cast in self.movie['castMember']:
                if 'activity' in cast:
                    activity = cast['activity']
                    if 'code' in activity:
                        if activity['code'] == code:
                            result = result + cast['person']['name'] + ', '
        if result:
            result = result[:-2]
        return result


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.search_query = "partner=100043982026&format=json&q=%s&filter=movie&count=100&page=1&profile=small"
        self.search_url = "http://api.allocine.fr/rest/v3/search?"
        
        self.original_url_search   = "http://api.allocine.fr/rest/v3/search?partner=YW5kcm9pZC12M3M&count=100&profile=small&format=json&filter=movie&q="
        self.translated_url_search = "http://api.allocine.fr/rest/v3/search?partner=YW5kcm9pZC12M3M&count=100&profile=small&format=json&filter=movie&q="
        self.encode                = 'utf-8'
        self.remove_accents        = True
        self.useurllib2 = True

    def search(self, parent_window):
        query = string.replace(self.search_query % self.title, ' ', '%20')
        query = query + '&sed=' + date.today().strftime("%Y%m%d")
        to_signature = '29d185d98c984a359e6e6f26a0474269' + query
        signature = urllib.quote_plus(base64.b64encode(hashlib.sha1(to_signature).digest()))
        self.title = self.search_url + query + '&sig=' + signature
        self.url = ''
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        result = json.JSONDecoder().decode(self.page)
        try:
            movies = result['feed']['movie']
            for movie in movies:
                try:
                    title = ''
                    year = ''
                    if 'title' in movie:
                        title = movie['title']
                    elif 'originalTitle' in movie:
                        title = movie['originalTitle']
                    if 'productionYear' in movie:
                        year = '(%s)' % movie['productionYear']
                    self.titles.append('%s %s' % (title, year))
                    self.ids.append(movie['code'])
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
        'Le Prix à payer' : [ 4, 4 ],
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
        '110585' : {
            'title'               : u'Le Prix à payer',
            'o_title'             : u'Le Prix à payer',
            'director'            : u'Alexandra Leclère',
            'plot'                : True,
            'cast'                : u'Christian Clavier' + _(' as ') + 'Jean-Pierre Ménard\n\
Nathalie Baye' + _(' as ') + 'Odile Ménard\n\
Gérard Lanvin' + _(' as ') + 'Richard\n\
Géraldine Pailhas' + _(' as ') + 'Caroline\n\
Patrick Chesnais' + _(' as ') + 'Grégoire l\'amant\n\
Anaïs Demoustier' + _(' as ') + 'Justine\n\
Maud Buquet' + _(' as ') + 'la prostituée\n\
Francis Leplay' + _(' as ') + 'l\'agent immobilier',
            'country'             : u'France',
            'genre'               : u'Comédie',
            'classification'      : False,
            'studio'              : False,
            'o_site'              : False,
            'site'                : 'http://www.allocine.fr/film/fichefilm_gen_cfilm=110585.html',
            'trailer'             : 'http://www.allocine.fr/blogvision/18726250',
            'year'                : 2007,
            'notes'               : False,
            'runtime'             : 95,
            'image'               : True,
            'rating'              : 4,
            'cameraman'           : u'Jean-François Robin',
            'screenplay'          : u'Alexandra Leclère',
            'barcode'             : False
        },
        '309' : {
            'title'               : u'Terminator',
            'o_title'             : u'Terminator, The',
            'director'            : u'James Cameron',
            'plot'                : True,
            'cast'                : u'Arnold Schwarzenegger' + _(' as ') + 'Le Terminator\n\
Michael Biehn' + _(' as ') + 'Kyle Reese\n\
Linda Hamilton' + _(' as ') + 'Sarah Connor\n\
Lance Henriksen' + _(' as ') + 'l\'inspecteur Vukovich\n\
Paul Winfield' + _(' as ') + 'le lieutenant Ed Traxler\n\
Bess Motta' + _(' as ') + 'Ginger Ventura\n\
Rick Rossovich' + _(' as ') + 'Matt Buchanan\n\
Earl Boen' + _(' as ') + 'le Dr Peter Silberman\n\
Dick Miller' + _(' as ') + 'le marchand d\'armes\n\
Shawn Schepps' + _(' as ') + 'Nancy\n\
Bill Paxton' + _(' as ') + 'Le chef des punks\n\
Brian Thompson' + _(' as ') + 'un punk\n\
Marianne Muellerleile' + _(' as ') + 'la \'mauvaise\' Sarah Connor\n\
Franco Columbu' + _(' as ') + 'le Terminator infiltrant le bunker dans le futur\n\
Ken Fritz' + _(' as ') + 'Policeman\n\
Stan Yale' + _(' as ') + 'Derelict in Alley\n\
Brad Rearden' + _(' as ') + 'Punk\n\
Joe Farago' + _(' as ') + 'TV Anchorman\n\
Anthony Trujillo' + _(' as ') + 'Mexican Boy (close-ups)\n\
Harriet Medin' + _(' as ') + 'Customer\n\
Hugh Farrington' + _(' as ') + 'Customer\n\
Philip Gordon' + _(' as ') + 'Mexican Boy (long shots)\n\
Patrick Pinney' + _(' as ') + 'Bar Customer\n\
Wayne Stone' + _(' as ') + 'Tanker Driver\n\
Norman Friedman' + _(' as ') + 'Cleaning Man at Flophouse\n\
Hettie Lynne Hurtes' + _(' as ') + 'TV Anchorwoman\n\
Al Kahn' + _(' as ') + 'Customer\n\
Bill W. Richmond' + _(' as ') + 'Barman\n\
Bruce M. Kerner' + _(' as ') + 'Desk Sergeant\n\
David Pierce' + _(' as ') + 'Tanker Partner\n\
Barbara Powers' + _(' as ') + 'Ticket Taker at Club Technoir\n\
Ed Dogans' + _(' as ') + 'Cop in Alley\n\
Tony Mirelez' + _(' as ') + 'Gas Station Attendant\n\
Webster Williams' + _(' as ') + 'Reporter\n\
John E. Bristol' + _(' as ') + 'Biker at Phone Booth\n\
Gregory Robbins' + _(' as ') + 'Tiki Motel Customer\n\
Chino \'Fats\' Williams' + _(' as ') + 'Truck Driver',
            'country'             : 'U.S.A.',
            'genre'               : 'Science fiction, Thriller',
            'classification'      : 'Interdit aux moins de 12 ans',
            'studio'              : False,
            'o_site'              : False,
            'site'                : 'http://www.allocine.fr/film/fichefilm_gen_cfilm=309.html',
            'trailer'             : 'http://www.allocine.fr/blogvision/18895020',
            'year'                : 1984,
            'notes'               : False,
            'runtime'             : 108,
            'image'               : True,
            'rating'              : 8,
            'cameraman'           : u'Adam Greenberg',
            'screenplay'          : u'James Cameron, Gale Anne Hurd, Harlan Ellison, William Wisher',
            'barcode'             : False
        },
    }
