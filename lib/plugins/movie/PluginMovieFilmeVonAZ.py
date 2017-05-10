# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieFilmeVonAZ.py 1651 2013-09-27 19:48:00Z mikej06 $'

# Copyright (c) 2006-2013 Michael Jahn
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

plugin_name = "FilmeVonA-Z.de"
plugin_description = "FILMEvonA-Z.de"
plugin_url = "www.zweitausendeins.de"
plugin_language = _("German")
plugin_author = "Michael Jahn"
plugin_author_email = "<mikej06@hotmail.com>"
plugin_version = "1.6"

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode = 'utf-8'
        self.url = id

    def get_image(self):
        self.image_url = gutils.trim(gutils.trim(self.page, "class='cover-box'", '</div>'), 'src="', '"')

    def get_o_title(self):
        self.o_title = string.capwords(gutils.clean(gutils.regextrim(self.page, '<b>Originaltitel:', '(</p>|<b>)')))
        if not self.o_title:
            self.o_title = gutils.after(gutils.trim(self.page, 'class=\'film-titel\'', '</h1>'), '>')

    def get_title(self):
        self.title = gutils.before(gutils.trim(self.page, '<h1>', '</h1>'), '.')

    def get_director(self):
        self.director = gutils.trim(self.page, '<b>Regie:', '</p>')

    def get_plot(self):
        self.plot = gutils.after(gutils.trim(self.page, 'class="description"', '</p>'), '>')

    def get_year(self):
        self.year = gutils.after(gutils.trim(self.page, '<b>Produktionsjahr:', '<br/>'), '>')

    def get_runtime(self):
        self.runtime = '0'
        try:
            tmp = gutils.trim(self.page, 'style=\'text-transform:uppercase\'', '</p>')
            if tmp:
                match = re.search('([0-9]+) Min[.]', tmp)
                if match:
                    self.runtime = match.group(1)
        except:
            None

    def get_genre(self):
        self.genre = gutils.after(gutils.trim(self.page, 'class=\'film-angaben\'', '</p>'), '>')
        if ':' in self.genre:
            self.genre = ''

    def get_cast(self):
        self.cast = gutils.trim(self.page, '<b>Darsteller:', '</p>')
        self.cast = gutils.clean(self.cast)
        self.cast = self.cast.replace(' (', _(' as '))
        self.cast = self.cast.replace('), ', '\n')
        self.cast = self.cast.replace(')', '')

    def get_classification(self):
        self.classification = ''
        try:
            tmp = gutils.trim(self.page, 'style=\'text-transform:uppercase\'', '</p>')
            if tmp:
                match = re.search('FSK ([a-zA-Z0-9]+)[.]', tmp)
                if match:
                    self.classification = match.group(1)
        except:
            None

    def get_studio(self):
        self.studio = gutils.after(gutils.regextrim(self.page, '<b>Produktionsfirma:', '(<br/>|</p>)'), '>')
        self.studio = string.replace(self.studio, '/', ', ')
        self.studio = re.sub(',[ ]*$', '', self.studio)

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = gutils.after(gutils.trim(self.page, '<b>Produktionsland:', '<br/>'), '>')
        self.country = re.sub(',[ ]*$', '', self.country)
        self.country = string.replace(self.country, '/', ', ')

    def get_rating(self):
        self.rating = 0

    def get_screenplay(self):
        self.screenplay = gutils.trim(self.page, '<b>Drehbuch:', '</p>')
        self.screenplay = re.sub(',[ ]*$', '', self.screenplay)

    def get_cameraman(self):
        self.cameraman = gutils.trim(self.page, '<b>Kamera:', '</p>')
        self.cameraman = re.sub(',[ ]*$', '', self.cameraman)

class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.original_url_search   = "http://www.zweitausendeins.de/catalogsearch/result/?cat=22&t=1&limit=30&q="
        self.translated_url_search = "http://www.zweitausendeins.de/catalogsearch/result/?cat=22&t=1&limit=30&q="
        self.encode = 'utf-8'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        # used for looking for subpages
        tmp_page = gutils.trim(self.page, 'class="pages"', '</div>')
        elements = string.split(tmp_page, 'href="')
        # first results
        tmp_page = gutils.trim(self.page, 'class="category-products"', 'class="toolbar-bottom"')
        # look for subpages
        i = 1
        while i < len(elements):
            element = elements[i]
            i = i + 1
            p1 = string.find(element, 'title="Nächste"')
            if p1 >= 0:
                continue;
            element = gutils.before(element, '"')
            if element:
                self.title = ''
                self.o_title = ''
                self.url = element
                print self.url
                if self.open_search(parent_window):
                    tmp_page2 = gutils.trim(self.page, 'class="category-products"', 'class="toolbar-bottom"')
                    tmp_page = tmp_page + tmp_page2
        self.page = tmp_page

        return self.page

    def get_searches(self):
        elements = string.split(self.page, 'class="product-name"')
        i = 1
        while i < len(elements):
            element = elements[i]
            i = i + 1
            self.ids.append(gutils.trim(element, 'href="', '"'))
            self.titles.append(re.sub('Zweitausendeins Edition.*', '', gutils.trim(gutils.after(element, '>'), '>', '<')))


#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky'                : [ 17, 17 ],
        'Arahan'               : [ 1, 1 ],
        'Ein glückliches Jahr' : [ 1, 1 ]
    }

class PluginTest:
    #
    # Configuration for automated tests:
    # dict { movie_id -> dict { arribute -> value } }
    #
    # value: * True/False if attribute should only be tested for any value
    #        * or the expected value
    #
    test_configuration = {
        '528267' : { 
            'title'             : 'Rocky Balboa',
            'o_title'           : 'Rocky Balboa',
            'director'          : 'Sylvester Stallone',
            'plot'              : True,
            'cast'              : 'Sylvester Stallone' + _(' as ') + 'Rocky Balboa\n\
Burt Young' + _(' as ') + 'Paulie\n\
Antonio Tarver' + _(' as ') + 'Mason \'The Line\' Dixon\n\
Geraldine Hughes' + _(' as ') + 'Marie\n\
Milo Ventimiglia' + _(' as ') + 'Rocky jr.\n\
Tony Burton' + _(' as ') + 'Duke\n\
A.J. Benza' + _(' as ') + 'L.C.',
            'country'           : 'USA',
            'genre'             : 'Boxerfilm',
            'classification'    : 'ab 12',
            'studio'            : 'Columbia Pic., MGM, Rogue Marble, Revolution Studios, Chartoff-Winkler Prod.',
            'o_site'            : False,
            'site'              : 'http://www.zweitausendeins.de/filmlexikon/?sucheNach=titel&wert=528267',
            'trailer'           : False,
            'year'              : 2006,
            'notes'             : False,
            'runtime'           : 102,
            'image'             : True,
            'rating'            : False,
            'screenplay'        : 'Sylvester Stallone',
            'cameraman'         : 'Clark Mathis',
        },
        '26956' : { 
            'title'             : 'Bürgschaft für ein Jahr',
            'o_title'           : 'Bürgschaft für ein Jahr',
            'director'          : 'Herrmann Zschoche',
            'plot'              : True,
            'cast'              : 'Katrin Saß' + _(' as ') + 'Nina\n\
Monika Lennartz' + _(' as ') + 'Irmgard Behrend\n\
Jaecki Schwarz' + _(' as ') + 'Peter Müller\n\
Christian Steyer' + _(' as ') + 'Heiner Menk\n\
Jan Spitzer' + _(' as ') + 'Werner Horn\n\
Heide Kipp' + _(' as ') + 'Frau Braun\n\
Barbara Dittus' + _(' as ') + 'Heimleiterin\n\
Ursula Werner' + _(' as ') + 'Frau Müller',
            'country'           : 'DDR',
            'genre'             : 'Arbeiterfilm, Frauenfilm, Literaturverfilmung',
            'classification'    : 'ab 6',
            'studio'            : 'DEFA, Gruppe Berlin""',
            'o_site'            : False,
            'site'              : 'http://www.zweitausendeins.de/filmlexikon/?sucheNach=titel&wert=26956',
            'trailer'           : False,
            'year'              : 1981,
            'notes'             : False,
            'runtime'           : 93,
            'image'             : True,
            'rating'            : False,
            'screenplay'        : 'Gabriele Kotte',
            'cameraman'         : 'Günter Jaeuthe',
        },
        '524017' : { 
            'title'             : 'Arahan',
            'o_title'           : 'Arahan Jangpung Daejakjeon',
            'director'          : 'Ryoo Seung-wan',
            'plot'              : True,
            'cast'              : 'Ryu Seung-beom' + _(' as ') + 'Sang-hwan\n\
Yoon So-yi' + _(' as ') + 'Wi-jin\n\
Ahn Sung-kee' + _(' as ') + 'Ja-woon\n\
Jung Doo-hong' + _(' as ') + 'Heukwoon\n\
Yun Ju-sang' + _(' as ') + 'Mu-woon',
            'country'           : 'Südkorea',
            'genre'             : False,
            'classification'    : 'ab 16',
            'studio'            : 'Fun and Happiness, Good Movie',
            'o_site'            : False,
            'site'              : 'http://www.zweitausendeins.de/filmlexikon/?sucheNach=titel&wert=524017',
            'trailer'           : False,
            'year'              : 2004,
            'notes'             : False,
            'runtime'           : 108,
            'image'             : False,
            'rating'            : False,
            'screenplay'        : 'Eun Ji-hie, Ryoo Seung-wan, Yu Seon-dong',
            'cameraman'         : 'Lee Jun-gyu',
        }
    }
