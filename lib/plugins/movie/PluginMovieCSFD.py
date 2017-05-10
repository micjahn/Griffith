# -*- coding: utf-8 -*-
__revision__ = '$Id: PluginMovieCSFD.py 12 2011-05-22 08:37:14Z KamilHanus $'
# Copyright (c) 2011 Kamil Hanus
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
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import gutils
import movie
import string
import re

plugin_name = "CSFD"
plugin_description = "Cesko-Slovenska Filmova Databaze"
plugin_url = "www.csfd.cz"
plugin_language = _("Czech")
plugin_author = "Kamil Hanus"
plugin_author_email = "<kamilhanus@gmail.com>"
plugin_version = '1.2'


class Plugin(movie.Movie):
    def __init__(self, id):
        self.movie_id = id
        self.encode = "utf-8"
        self.url = "http://www.csfd.cz" + str(id)

    def get_image(self):
        self.image_url = re.search(r"content=\"http://img.csfd.cz/files/images/film/posters/([^\"]*)\"", self.page)
        if self.image_url:
            self.image_url = "http://img.csfd.cz/files/images/film/posters/" + gutils.strip_tags(self.image_url.group(1))
        else:
            self.image_url = ""

    def get_title(self, ret=False):
        data = re.search(r'<title>*>([^>]*)', self.page)
        if data:
            if len(data.group(1).split("/")) == 2:
                data = data.group(1).split(" | ")[0][:-7]
            else:
                data = data.group(1).split(" / ")[0]
        else:
            data = ""
        if ret is True:
            return data
        else:
            self.title = data

    def get_o_title(self):
        self.o_title = re.findall(r'/images/flags/flag_[\d]+.gif"[^<]*>([^/]*)', self.page)
        if len(self.o_title) > 0:
            self.o_title = self.o_title[0]
            self.o_title = self.o_title[11:-1]
        else:
            self.o_title = ""
        if self.o_title == "":
            self.o_title = self.get_title(True)

    def get_director(self):
        self.director = ''
        tmp = gutils.trim(self.page, '>Režie:<', '</div>')
        if tmp:
            tmp = string.split(tmp, "href=")
            for item in tmp:
                item = gutils.clean(gutils.trim(item, '>', '<'))
                if item:
                    self.director = self.director + item + ', '
            if self.director:
                self.director = self.director[:-2]

    def get_year(self):
        self.year = re.search(r'<p class="origin"[^<]*>([^>]*)', self.page)
        if self.year:
            try:
                self.year = self.year.group()[18:-7].split(", ")[-2]
            except:
                self.year = ""
        else:
            self.year = ""

    def get_runtime(self):
        self.runtime = re.search(r'<p class="origin"[^<]*>([^>]*)', self.page)
        if self.runtime:
            self.runtime = self.runtime.group()[18:-7].split(", ")[-1]
        else:
            self.runtime = ""

    def get_genre(self):
        try:
            self.genre = re.search(r'<p class="genre"[^<]*>([^>]*)', self.page).group()[17:-3]
        except:
            self.genre = ""

    def get_country(self):
        self.country = re.search(r'<p class="origin"[^<]*>([^>]*)', self.page)
        if self.country:
            self.country = self.country.group()[18:-7].split(", ")[0]
        else:
            self.country = ""

    def get_cast(self):
        self.cast = ''
        tmp = gutils.trim(self.page, '>Hrají:<', '</div>')
        if tmp:
            tmp = string.split(tmp, "href=")
            for item in tmp:
                item = gutils.clean(gutils.trim(item, '>', '<'))
                if item:
                    self.cast = self.cast + item + '\n'
            if self.cast:
                self.cast = self.cast[:-2]

    def get_plot(self):
        a = re.sub("\t", "", self.page)
        a = re.sub("\n", "", a)
        a = re.sub("<BR>", "", a)
        try:
            self.plot = gutils.after(re.search(r'ka"([^<]*)', a).group(0), '>')
        except:
            self.plot = ""

    def get_site(self):
        self.site = re.search(r"href=[\"'](http://.*imdb\.com/title/[^\"']*)", self.page)
        if self.site:
            self.site = gutils.strip_tags(self.site.group(1))
        else:
            self.site = ""

    def get_trailer(self):
        try:
            self.trailer = self.url + "/videa"
        except:
            self.trailer = ""

    def get_rating(self):
        a = re.sub("\t", "", self.page)
        a = re.sub("\n", "", a)
        self.rating = re.search(r"[\s]*([\d]+)%[\s]*</h2>", a).group()[:-6]

        if self.rating:
            self.rating = str(float(self.rating) / 10)
        else:
            self.rating = ""

    def get_o_site(self):
        self.o_site = ""
        try:
            index = string.rfind(self.page, u'title="oficiální web"')
            if index > 0:
                tmp = gutils.before(self.page, u'title="oficiální web"')
                index = string.rfind(tmp, 'href="')
                if index > 0:
                    self.o_site = gutils.trim(tmp[index:], '"', '"')
        except:
            pass

    def get_notes(self):
        self.notes = ""

    def get_studio(self):
        self.studio = ""

    def get_classification(self):
        self.classification = ""

    def get_screenplay(self):
        self.screenplay = ''
        tmp = gutils.trim(self.page, '>Scénář:<', '</div>')
        if tmp:
            tmp = string.split(tmp, "href=")
            for item in tmp:
                item = gutils.clean(gutils.trim(item, '>', '<'))
                if item:
                    self.screenplay = self.screenplay + item + ', '
            if self.screenplay:
                self.screenplay = self.screenplay[:-2]


class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.encode = "utf-8"
        self.original_url_search = "http://www.csfd.cz/hledat/?q="
        self.translated_url_search = "http://www.csfd.cz/hledat/?q="

    def search(self, parent_window):
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        tmp_id = self.re_items = re.search(r'form action="(/film/[^/"]*)', self.page)
        if tmp_id:
            self.ids.append(tmp_id.group(1))
        else:
            self.re_items = re.findall(r"href=\"(/film/[^/\"]+)[^>]*>([^<]+)</a>([^<]*)", self.page)
            self.number_results = len(self.re_items)
            if (self.number_results > 0):
                for item in self.re_items:
                    self.ids.append(item[0])
#                    self.titles.append(gutils.convert_entities(item[1])+' '+item[2])
                    self.titles.append(item[1] + ' ' + item[2])


#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> expected result count }
    #
    test_configuration = {
        'Cliffhanger' : [ 1, 1 ],
        'Rocky' : [ 41, 41 ]
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
        '/film/221900-rocky-balboa' : {
            'title'          : 'Rocky Balboa',
            'o_title'        : 'Rocky Balboa',
            'director'       : 'Sylvester Stallone',
            'plot'           : True,
            'cast'           : 'Sylvester Stallone\n\
Tony Burton\n\
Talia Shire\n\
Milo Ventimiglia\n\
Burt Young\n\
Antonio Tarver\n\
Geraldine Hughes\n\
Pedro Lovell\n\
Frank Stallone\n\
Mike Tyson\n\
Michael Ahl\n\
Dean Maur',
            'country'        : 'USA',
            'genre'          : 'Sportovní / Drama / Akční / Romantický',
            'classification' : False,
            'studio'         : False,
            'o_site'         : False,
            'site'           : 'http://www.imdb.com/title/tt0479143/',
            'trailer'        : 'http://www.csfd.cz/film/221900-rocky-balboa/videa',
            'year'           : 2006,
            'notes'          : False,
            'runtime'        : 97,
            'image'          : True,
            'rating'         : 7,
            'cameraman'      : False,
            'screenplay'     : False
        },
        '/film/4155-cliffhanger' : {
            'title'          : 'Cliffhanger',
            'o_title'        : 'Cliffhanger',
            'director'       : 'Renny Harlin',
            'plot'           : True,
            'cast'           : 'Sylvester Stallone\n\
John Lithgow\n\
Michael Rooker\n\
Janine Turner\n\
Rex Linn\n\
Caroline Goodall\n\
Leon\n\
Craig Fairbrass\n\
Gregory Scott Cummins\n\
Max Perlich\n\
Paul Winfield\n\
Ralph Waite\n\
Zach Grenier\n\
Don S. Davis\n\
Bruce McGill\n\
Jeff Blynn\n\
John Finn\n\
Rosemary Dunsmor',
            'country'        : 'USA / Itálie / Francie',
            'genre'          : 'Akční / Dobrodružný / Thriller',
            'classification' : False,
            'studio'         : False,
            'o_site'         : False,
            'site'           : 'http://www.imdb.com/title/tt0106582/',
            'trailer'        : 'http://www.csfd.cz/film/4155-cliffhanger/videa',
            'year'           : 1993,
            'notes'          : False,
            'runtime'        : 110,
            'image'          : True,
            'rating'         : 7,
            'cameraman'      : False,
            'screenplay'     : False
        }
    }
