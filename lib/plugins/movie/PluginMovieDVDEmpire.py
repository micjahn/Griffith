# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieDVDEmpire.py 1650 2013-06-26 20:59:58Z mikej06 $'

# Copyright (c) 2007-2009
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
import re
import string

plugin_name         = "DVD Empire"
plugin_description  = "International Retailer of DVD Movies"
plugin_url          = "www.dvdempire.com"
plugin_language     = _("English")
plugin_author       = "Michael Jahn"
plugin_author_email = "<mikej06@hotmail.com>"
plugin_version      = "1.2"

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode   = 'iso-8859-1'
        self.movie_id = id
        self.url      = "http://www.dvdempire.com" + str(self.movie_id)

    def get_image(self):
        tmp_page = gutils.trim(self.page, 'id="Boxcover"', '</div>')
        self.image_url = gutils.trim(tmp_page, 'href="', '"')

    def get_o_title(self):
        self.o_title = gutils.strip_tags(gutils.trim(self.page, '<title>', '('))

    def get_title(self):
        self.title = gutils.strip_tags(gutils.trim(self.page, '<title>', '('))

    def get_director(self):
        self.director = gutils.trim(self.page, '<h3>Director</h3>', '</div>')
        self.director = self.director.replace('</li><li', '</li>, <li')
        self.director = self.director.replace('&nbsp;', '')
        self.director = self.director.replace('&#149;', '')

    def get_plot(self):
        self.plot = gutils.strip_tags(gutils.trim(self.page, 'Synopsis</h2>', '</div>'))
        self.plot = self.plot.replace(u'\x93', '"')
        self.plot = self.plot.replace(u'\x84', '"')

    def get_year(self):
        self.year = gutils.strip_tags(gutils.after(gutils.trim(self.page, 'Production Year', '<br'), '>'))

    def get_runtime(self):
        self.runtime = ''
        tmp = gutils.strip_tags(gutils.trim(self.page, 'Length', '<br'))
        #1 hrs. 59 mins.
        try:
            self.runtime = int(gutils.before(tmp, 'hrs')) * 60 + int(gutils.trim(tmp, '.', 'mins'))
        except:
            self.runtime = ''

    def get_genre(self):
        tmp = gutils.strip_tags(gutils.trim(self.page, '<h2>Categories</h2>', '</p>'))
        tmp = tmp.replace('\r\n', '')
        self.genre = re.sub('[ \t]+', ' ', tmp)

    def get_cast(self):
        self.cast = gutils.trim(self.page, '<h3>Cast</h3>', '</div>')
        self.cast = self.cast.replace('<br>', '\n')
        self.cast = self.cast.replace('<br />', '\n')
        self.cast = self.cast.replace('&nbsp;', '')
        self.cast = self.cast.replace('&#8226;', '')
        self.cast = self.cast.replace('&#149;', '')
        self.cast = self.cast.replace('</li><li', '</li>\n<li')
        self.cast = self.cast.replace('</li><!-- non-headliners --><li', '</li>\n<li')
        self.cast = gutils.strip_tags(self.cast)

    def get_classification(self):
        self.classification = gutils.strip_tags(gutils.trim(self.page, 'Rating</strong>', '<br'))

    def get_studio(self):
        self.studio = gutils.strip_tags(gutils.trim(self.page, 'Studio</strong>', '<br'))

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ""

    def get_country(self):
        self.country = ""

    def get_rating(self):
        self.rating = gutils.clean(gutils.trim(self.page, 'Overall Rating:', ' out of'))
        try:
            tmp_float = float(self.rating)
            tmp_float = round(2 * tmp_float, 0)
            self.rating = str(tmp_float)
        except:
            self.rating = '0'

    def get_notes(self):
        self.notes = ''
        tmp_page = gutils.trim(self.page, '<h3>Features</h3>', '</p>')
        tmp_page = tmp_page.replace('<br>', '\n')
        tmp_page = tmp_page.replace('<br />', '\n')
        tmp_page = gutils.strip_tags(tmp_page)
        if tmp_page <> '':
            self.notes = self.notes + 'Features:\n' + tmp_page + '\n\n'
        tmp_page = gutils.trim(self.page, 'Video</strong>', '<strong>')
        tmp_page = tmp_page.replace('\r\n', '')
        tmp_page = re.sub('[ \t]+', ' ', tmp_page)
        tmp_page = tmp_page.replace('<br>', '\n')
        tmp_page = tmp_page.replace('<br />', '\n')
        tmp_page = gutils.strip_tags(tmp_page)
        if tmp_page <> '':
            self.notes = self.notes + 'Video:' + tmp_page
        tmp_page = gutils.trim(self.page, 'Audio</strong>', '</div>')
        tmp_page = tmp_page.replace('\r\n', '')
        tmp_page = re.sub('[ \t]+', ' ', tmp_page)
        tmp_page = tmp_page.replace('<br>', '\n')
        tmp_page = tmp_page.replace('<br />', '\n')
        tmp_page = tmp_page.replace('(more info)', '\n')
        tmp_page = gutils.strip_tags(tmp_page)
        if tmp_page <> '':
            self.notes = self.notes + 'Audio:' + tmp_page

    def get_screenplay(self):
        self.screenplay = gutils.strip_tags(gutils.trim(self.page, 'Writers</strong>', '<br'))
        self.screenplay = self.screenplay.replace('&nbsp;', '')
        self.screenplay = self.screenplay.replace('&#149;', '')

    def get_barcode(self):
        self.barcode = gutils.trim(self.page, 'UPC Code</strong>', '<br')


class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.original_url_search   = "http://www.dvdempire.com/allsearch/search?pageSize=100&q="
        self.translated_url_search = "http://www.dvdempire.com/allsearch/search?pageSize=100&q="
        self.encode                = 'iso-8859-1'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        split_pattern = re.compile('class="title"')
        elements = split_pattern.split(self.page)
        for index in range(1, len(elements), 1):
            title_element = elements[index]
            tmp_title = gutils.clean(gutils.strip_tags(gutils.trim(title_element, '>', '</a>')))
            tmp_title = string.replace(tmp_title, '&nbsp;', ' ')
            tmp_title = string.replace(tmp_title, '&amp;', '&')
            tmp_title = string.replace(tmp_title, '&quot;', '"')
            if tmp_title <> '':
                self.ids.append(gutils.trim(elements[index], 'href="', '"'))
                type = re.search('>Blu-ray</span>', title_element)
                if type:
                    tmp_title = tmp_title + ' (Blu-ray)'
                type = re.search('>DVD-Video</span>', title_element)
                if type:
                    tmp_title = tmp_title + ' (DVD)'
                self.titles.append(tmp_title)

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa' : [ 30, 30 ],
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
        '/1402424/meet-the-spartans-unrated-pit-of-death-edition-blu-ray.html' : { 
            'title'               : 'Meet The Spartans: Unrated Pit Of Death Edition',
            'o_title'             : 'Meet The Spartans: Unrated Pit Of Death Edition',
            'director'            : 'Jason Friedberg, Aaron Seltzer',
            'plot'                : True,
            'cast'                : 'Carmen Electra\n\
Sean Maguire\n\
Ken Davitian',
            'country'             : False,
            'genre'               : 'Blu-ray, Comedy, Movies, Spoofs & Parodies',
            'classification'      : 'NR',
            'studio'              : '20th Century Fox',
            'o_site'              : False,
            'site'                : 'http://www.dvdempire.com/1402424/meet-the-spartans-unrated-pit-of-death-edition-blu-ray.html',
            'trailer'             : False,
            'year'                : 2008,
            'notes'               : 'Features:\n\
Audio Commentary By Cast And Crew\n\
Prepare For Thrusting Featurette\n\
Tour The Set With Ike Barinholtz Featurette\n\
Gag Reel\n\
Know Your Spartans Pop Culture Trivia Game\n\
Celebrity Kickoff Game\n\
Super Pit-Of-Death Ultimate Tactical Battle Challange Game\n\
Meet The Spartans: The Music\n\
Trivial Track\n\
Theatrical Trailers\n\
\n\
Video:\n\
 Widescreen 1.85:1 Color \n\
\n\
Audio:\n\
 French Dolby Digital Surround \n\
 Spanish Dolby Digital Surround \n\
 English DTS-HD MA 5.1',
            'runtime'             : 87,
            'image'               : True,
            'rating'              : 5,
            'screenplay'          : False,
            'barcode'             : '024543522614'
        },
    }
