# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ozarowski
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

plugin_name         = "Cineteka"
plugin_description  = "O seu Clube de Video Online"
plugin_url          = "cineteka.com"
plugin_language     = _("Portuguese")
plugin_author       = "Vasco Nunes"
plugin_author_email = "<vasco.m.nunes@gmail.com>"
plugin_version      = "0.4"

class Plugin(movie.Movie):
    """A movie plugin object"""
    def __init__(self, id):
        self.encode   = 'iso-8859-1'
        self.movie_id = id
        self.url      = "http://www.cineteka.com/index.php?op=Movie&id=" + str(self.movie_id)

    def get_image(self):
        """Finds the film's poster image"""
        self.image_url = "http://www.cineteka.com/img/filmes/" + str(self.movie_id) + "_big.jpg"

    def get_o_title(self):
        """Finds the film's original title"""
        self.o_title = gutils.trim(self.page, u'<nobr><span class="txt11">(', u')')

    def get_title(self):
        """Finds the film's local title.
        Probably the original title translation"""
        self.title = gutils.trim(self.page, u'<td class="movieT"><b>', u'</b>')

    def get_director(self):
        """Finds the film's director"""
        self.director = gutils.strip_tags(gutils.trim(self.page, u'<div><b>Realização:</b><br>', u'</div>'))
        self.director = string.replace(self.director, u'<br>', u', ')
        self.director = gutils.strip_tags(self.director)

    def get_plot(self):
        """Finds the film's plot"""
        self.plot = gutils.trim(self.page, u'<div class="txt-normal" style="margin-top: 10px;">', u'</td></tr></table>')
        self.plot = self.plot.replace(u'\x93', u'"')
        self.plot = self.plot.replace(u'\x94', u'"')
        self.plot = self.plot.replace(u'\x96', u'-')

    def get_year(self):
        """Finds the film's year"""
        self.year = gutils.trim(self.page, u'<b>Ano:</b> ', u'</div>')

    def get_runtime(self):
        """Finds the film's running time"""
        self.runtime = gutils.trim(self.page, u'<td><b>Duração:</b> ', u' min.</td>')

    def get_genre(self):
        """Finds the film's genre"""
        self.genre = gutils.trim(self.page, u'<b>Género:</b><br>', u'</div>')
        self.genre = string.replace(self.genre, u'<br>', u', ')
        self.genre = gutils.strip_tags(self.genre)

    def get_cast(self):
        self.cast = gutils.trim(self.page, u'<b>Elenco:</b>', u'</td>')
        self.cast = string.replace(self.cast, u'<br>', u'\n')
        self.cast = string.replace(self.cast, u', ', u'')
        self.cast = string.replace(self.cast, u'\t', u'')
        self.cast = string.replace(self.cast, u'\n ', u'\n')
        self.cast = gutils.clean(self.cast)
        self.cast = re.sub('[ \t]*[\n]+[ \t]*' , '\n', self.cast)

    def get_classification(self):
        """Find the film's classification"""
        self.classification = gutils.trim(self.page, u'<b>Idade:</b> ', u'</div>')

    def get_studio(self):
        """Find the studio"""
        self.studio = ''

    def get_o_site(self):
        """Find the film's oficial site"""
        self.o_site = gutils.trim(self.page, \
            u'<a class="button" href="', \
            u'" title="Consultar título no Internet Movie Data Base"')

    def get_site(self):
        """Find the film's imdb details page"""
        self.site = self.url

    def get_trailer(self):
        """Find the film's trailer page or location"""
        self.trailer = ""

    def get_country(self):
        """Find the film's country"""
        self.country = gutils.trim(self.page, u'<b>País:</b><br>', u'</div>')
        self.country = string.replace(self.country, u'<br>', u', ')
        self.country = gutils.strip_tags(self.country)

    def get_rating(self):
        """Find the film's rating. From 0 to 10.
        Convert if needed when assigning."""
        self.rating = gutils.clean(gutils.trim(self.page, u'IMDB: ', u'</span>'))
        try:
            self.rating = round(float(self.rating), 0)
        except Exception, e:
            self.rating = 0

    def get_screenplay(self):
        self.screenplay = gutils.strip_tags(gutils.trim(self.page, u'<b>Argumento:</b><br>', u'</div>'))
        self.screenplay = string.replace(self.screenplay, u'<br>', u', ')
        self.screenplay = gutils.strip_tags(self.screenplay)

class SearchPlugin(movie.SearchMovie):
    """A movie search object"""
    def __init__(self):
        self.original_url_search   = "http://www.cineteka.com/index.php?op=MovieSearch&perfil_display=0&ordby=3&s="
        self.translated_url_search = self.original_url_search
        self.encode                = 'iso-8859-1'

    def search(self, parent_window):
        """Perform the web search"""
        if not self.open_search(parent_window):
            return None
        self.page = gutils.after(self.page, '"Resultados Ordenados por:"')
        return self.page

    def get_searches(self):
        """Try to find both id and film title for each search result"""
        elements = re.split('index[.]php[?]op=Movie&id=([0-9]+)" ', self.page)
        
        for index in range(2, len(elements), 2):
            id = elements[index - 1]
            title = gutils.clean(gutils.trim(elements[index], '>', '</'))
            if id and title:
                self.ids.append(id)
                self.titles.append(gutils.strip_tags(gutils.convert_entities(title)))

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa' : [ 3, 3 ],
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
        '002551' : { 
            'title'               : 'Rocky Balboa',
            'o_title'             : 'Rocky Balboa',
            'director'            : 'Sylvester Stallone',
            'plot'                : True,
            'cast'                : 'Sylvester Stallone\n\
Burt Young\n\
Antonio Tarver\n\
Geraldine Hughes\n\
Milo Ventimiglia\n\
Tony Burton\n\
A.J. Benza\n\
James Francis Kelly III\n\
Talia Shire\n\
Lou DiBella\n\
Mike Tyson\n\
Henry G. Sanders',
            'country'             : 'EUA',
            'genre'               : 'Acção, Desporto, Drama',
            'classification'      : 'M/12',
            'studio'              : False,
            'o_site'              : 'http://www.imdb.com/title/tt0479143/',
            'site'                : 'http://www.cineteka.com/index.php?op=Movie&id=002551',
            'trailer'             : False,
            'year'                : 2006,
            'notes'               : False,
            'runtime'             : 102,
            'image'               : True,
            'rating'              : 8,
            'cameraman'           : False,
            'screenplay'          : 'Sylvester Stallone',
            'barcode'             : False
        },
    }
