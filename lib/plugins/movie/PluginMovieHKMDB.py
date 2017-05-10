# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieHKMDB.py 1633 2012-12-28 23:11:42Z mikej06 $'

# Copyright (c) 2010 Michael Jahn
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

plugin_name         = 'Hong Kong Movie DataBase'
plugin_description  = 'HKMDB.COM'
plugin_url          = 'www.hkmdb.com'
plugin_language     = _('English')
plugin_author       = 'Michael Jahn'
plugin_author_email = 'griffith@griffith.cc'
plugin_version      = '1.0'

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode = 'big5'
        self.movie_id = id
        self.url = "http://www.hkmdb.com/db/movies/view.mhtml?display_set=eng&complete_credits=1&id=" + self.movie_id

    def get_image(self):
        self.image_url = '';

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, '<font size="+2">', '</font>')

    def get_title(self):
        self.title = re.sub('[(][0-9]+[)]', '', gutils.trim(self.page, '<font size="+1">', '</font>'))

    def get_director(self):
        self.director = ''
        tmp = gutils.trim(self.page, '>Director<', '</TABLE>')
        elements = re.split('(href|HREF)="/db/people', tmp)
        for element in elements:
            element = gutils.clean(gutils.trim(element, '>', '<'))
            if element:
                self.director = self.director + element + ', '
        if self.director:
            self.director = self.director[:-2]

    def get_plot(self):
        self.plot = ''

    def get_year(self):
        self.year = gutils.trim(gutils.trim(self.page, '<font size="+1">', '</font>'), '(', ')')

    def get_runtime(self):
        self.runtime = 0

    def get_genre(self):
        self.genre = gutils.trim(self.page, 'Genre:', '<')

    def get_cast(self):
        self.cast = ''
        tmp = gutils.trim(self.page, '>Cast<', '</TABLE>')
        elements = re.split('(href|HREF)="/db/people', tmp)
        for element in elements:
            actor = gutils.clean(gutils.trim(element, '>', '<'))
            if actor:
                role = gutils.clean(gutils.trim(element, '>...', '</TR>'))
                if role:
                    self.cast = self.cast + actor + _(' as ') + role + '\n'
                else:
                    self.cast = self.cast + actor + '\n'

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = ''
        tmp = gutils.regextrim(self.page, '>Production Company<', '(<B>|</TABLE>)')
        elements = re.split('(href|HREF)="/db/companies', tmp)
        for element in elements:
            element = gutils.clean(gutils.trim(element, '>', '<'))
            if element:
                self.studio = self.studio + element + ', '
        if self.studio:
            self.studio = self.studio[:-2]

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ""

    def get_country(self):
        self.country = gutils.trim(self.page, 'Country:', '<')

    def get_rating(self):
        self.rating = 0

    def get_notes(self):
        self.notes = ""

    def get_screenplay(self):
        self.screenplay = ''
        tmp = gutils.trim(self.page, '>Script<', '</TABLE>')
        elements = re.split('(href|HREF)="/db/people', tmp)
        for element in elements:
            element = gutils.clean(gutils.trim(element, '>', '<'))
            if element:
                self.screenplay = self.screenplay + element + ', '
        if self.screenplay:
            self.screenplay = self.screenplay[:-2]


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search   = "http://www.hkmdb.com/db/search/simple_search_results.mhtml?display_set=eng&search_for=movies&search_string="
        self.translated_url_search = "http://www.hkmdb.com/db/search/simple_search_results.mhtml?display_set=eng&search_for=movies&search_string="
        self.encode = 'big5'
        self.remove_accents = False

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        if string.find(self.page, '>Films<') < 0:
            self.ids.append(gutils.regextrim(self.page, '="/db/movies/view[.]mhtml[?]id=', '([&"])'))
            self.titles.append('')
        else:
            elements = string.split(self.page, '<a href="/db/movies/view.mhtml?id=')
            elements[0] = ''
            for element in elements:
                if element <> '' and string.find(element, 'display_set=eng') > -1:
                    id = gutils.before(gutils.before(element, '"'), '&')
                    if id <> '':
                        self.ids.append(id)
                        self.titles.append(gutils.trim(element, '>', '</a>'))

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky' : [ 2, 2 ]
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
        '8997' : {
            'title'             : 'Mar\'s Villa, The',
            'o_title'           : u'蟡',
            'director'          : 'Ting Chung (1)',
            'plot'              : False,
            'cast'              : 'John Liu Chung-Liang' + _(' as ') + 'Ma Tien Lang\n\
Stephen Tung Wai\n\
Tong Bo-Wan' + _(' as ') + 'Ma\'s wife\n\
Suen Yuet\n\
Phillip Ko Fei' + _(' as ') + 'Fang Kang and his brother\n\
Ga Hoi\n\
Wong Kwok-Fai (2)' + _(' as ') + 'Fei Hu\n\
Peng Kong' + _(' as ') + 'Fei Lung\n\
Wong Hoi (3)\n\
Wong Chi-Sang' + _(' as ') + 'Henchman\n\
Ho Szu-Yuan\n\
Hung Ji-Yue\n\
San Bao\n\
Cheung Chung-Kwai (1)\n\
Peter Chang Chi-Long\n\
Mark Lung Goon-Mo\n\
Fan Fung-San' + _(' as ') + '[Extra]\n\
Chan Jan (1)' + _(' as ') + '[Extra]\n\
Chen Chin-Hai' + _(' as ') + '[Extra]\n\
Mau Ging-Shun' + _(' as ') + '[Extra]\n\
Lui Wan-Biu' + _(' as ') + '[Extra]',
            'country'           : 'Taiwan',
            'genre'             : 'Martial Arts',
            'classification'    : False,
            'studio'            : 'Great China Film Company H. K.',
            'o_site'            : False,
            'site'              : 'http://www.hkmdb.com/db/movies/view.mhtml?display_set=eng&complete_credits=1&id=8997',
            'trailer'           : False,
            'year'              : 1979,
            'notes'             : False,
            'runtime'           : 0,
            'image'             : False,
            'rating'            : False,
            'screenplay'        : 'Wai San'
        }
    }
