# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieAllRovi.py 1633 2012-12-28 23:11:42Z mikej06 $'

# Copyright (c) 2009-2011
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
import string, re

plugin_name         = "rovi"
plugin_description  = "rovi"
plugin_url          = "www.allrovi.com"
plugin_language     = _("English")
plugin_author       = "Michael Jahn"
plugin_author_email = "griffith@griffith.cc"
plugin_version      = "2.0"

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode = 'utf-8'
        self.movie_id = id
        self.url = 'http://www.allrovi.com/movies/movie/' + str(self.movie_id)

    def initialize(self):
        self.page_cast = self.open_page(url = 'http://www.allrovi.com/movies/movie/' + str(self.movie_id) + '/cast_crew')

    def get_image(self):
        self.image_url = gutils.trim(self.page, '<img class="cover-art" src="', '"')

    def get_o_title(self):
        self.o_title = gutils.regextrim(self.page, '<div class="page-heading">', '(</div>|<span>)')

    def get_title(self):
        self.title = gutils.regextrim(self.page, '<div class="page-heading">', '(</div>|<span>)')

    def get_director(self):
        self.director = gutils.trim(self.page, '<dt>directed by</dt>', '</ul>')

    def get_plot(self):
        self.plot = gutils.trim(self.page, '>synopsis', '</p>')

    def get_year(self):
        self.year = gutils.after(gutils.trim(self.page, '<dt>release date</dt>', '</div>'), ',')

    def get_runtime(self):
        self.runtime = ''

    def get_genre(self):
        self.genre = gutils.trim(self.page, '<dt>genres</dt>', '</ul>')

    def get_cast(self):
        self.cast = ''
        tmp = gutils.trim(self.page_cast, '<h2>cast</h2>', '</table>')
        elements = string.split(tmp, '<td class="name">')
        for element in elements:
            element = string.replace(element, '</a>', '$$$')
            self.cast = self.cast + string.replace(re.sub('[$][$][$]$', '', re.sub('[ ]+', ' ', string.replace(gutils.clean(element), '\n', ''))), '$$$', _(' as ')) + '\n'

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = gutils.regextrim(self.page, '<dt>produced by</dt>', '(</div>|<dt>)')

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = gutils.regextrim(self.page, '<dt>countries</dt>', '(</div>|<dt>)')

    def get_rating(self):
        self.rating = (len(string.split(gutils.trim(self.page, '<dt>rovi rating</dt>', '</div>'), '"star full"')) - 1) * 2

    def get_notes(self):
        self.notes = ''

    def get_cameraman(self):
        self.cameraman = ''
        tmp = gutils.trim(self.page_cast, '<h2>crew</h2>', '</dl>')
        elements = string.split(tmp, '<dt>')
        for element in elements:
            if string.find(element, 'Cinematographer') > 0:
                self.cameraman = gutils.clean(gutils.before(element, '</a>'))

    def get_screenplay(self):
        self.screenplay = ''
        tmp = gutils.trim(self.page_cast, '<h2>crew</h2>', '</dl>')
        elements = string.split(tmp, '<dt>')
        for element in elements:
            if string.find(element, 'Screenwriter') > 0:
                self.screenplay = gutils.clean(gutils.before(element, '</a>'))

    def get_barcode(self):
        self.barcode = ''


class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.original_url_search = "http://www.allrovi.com/search/ajax_more_results/movies/%s/0/100"
        self.translated_url_search = "http://www.allrovi.com/search/ajax_more_results/movies/%s/0/100"
        self.encode = 'utf-8'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        elements = re.split('<tr>', self.page)
        for index in range(1, len(elements), 1):
            element = elements[index]
            titleandid = gutils.trim(element, '<td class="title">', '</td>')
            title = gutils.clean(titleandid)
            id = gutils.trim(titleandid, 'href="', '"')
            idstart = string.rfind(id, '/')
            id = id[idstart + 1:]
            year = gutils.trim(element, '<td class="year">', '</td>')
            self.ids.append(id)
            self.titles.append(title + ' (' + gutils.clean(year)+ ')')

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky' : [ 100, 100 ],
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
        'rocky-balboa-v337682' : { 
            'title'               : 'Rocky Balboa',
            'o_title'             : 'Rocky Balboa',
            'director'            : 'Sylvester Stallone',
            'plot'                : True,
            'cast'                : 'Sylvester Stallone' + _(' as ') + ' Rocky Balboa\n\
Burt Young' + _(' as ') + ' Paulie\n\
Antonio Tarver' + _(' as ') + ' Mason "The Line" Dixon\n\
Geraldine Hughes' + _(' as ') + ' Marie\n\
Milo Ventimiglia' + _(' as ') + ' Rocky Balboa Jr.\n\
Tony Burton' + _(' as ') + ' Duke\n\
A.J. Benza' + _(' as ') + ' L.C.\n\
James Francis Kelly III' + _(' as ') + ' Steps\n\
Lou DiBella\n\
Mike Tyson' + _(' as ') + ' Himself\n\
Woodrow W. Paige\n\
Skip Bayless\n\
Jay Crawford\n\
Brian Kenny\n\
Dana Jacobson\n\
Chuck Johnson\n\
Jim Lampley\n\
Larry Merchant\n\
Max Kellerman\n\
Leroy Neiman\n\
Bert Randolph Sugar\n\
Bernard Fernandez\n\
Michael Buffer\n\
Talia Shire',
            'country'             : 'USA',
            'genre'               : 'Drama',
            'classification'      : False,
            'studio'              : 'Chartoff Winkler Productions, Columbia Pictures, MGM, Revolution Studios',
            'o_site'              : False,
            'site'                : 'http://www.allrovi.com/movies/movie/rocky-balboa-v337682',
            'trailer'             : False,
            'year'                : 2006,
            'notes'               : False,
            'runtime'             : False,
            'image'               : True,
            'rating'              : 6,
            'cameraman'           : 'Clark Mathis',
            'screenplay'          : 'Sylvester Stallone',
            'barcode'             : False
        },
    }
