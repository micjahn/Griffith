# -*- coding: iso-8859-15 -*-

__revision__ = '$Id: PluginMovieCulturalia.py 389 2006-07-29 18:43:35Z piotrek $'

# Copyright (c) 2006 Pedro D. Sánchez
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

plugin_name         = 'Culturalia'
plugin_description  = 'Base de Datos de Peliculas'
plugin_url          = 'www.culturalianet.com'
plugin_language     = _('Spanish')
plugin_author       = 'Pedro D. Sánchez'
plugin_author_email = '<pedrodav@gmail.com>'
plugin_version      = '0.3'

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode   = 'iso-8859-1'
        self.movie_id = id
        self.url      = "http://www.culturalianet.com/art/ver.php?art=%s" % str(self.movie_id)

    def get_image(self):
        tmp = string.find(self.page, "<font class = 'titulo2'>")
        if tmp == -1:
            self.image_url = ''
        else:
            self.image_url = 'http://www.culturalianet.com/art/'+gutils.trim(self.page[tmp:], '<img src = "', '"')

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, "<font class = 'titulo2'>", '</i>')
        self.o_title = gutils.after(self.o_title, '<i>')

    def get_title(self):
        self.title = gutils.trim(self.page, "<font class = 'titulo2'>", '. (')

    def get_director(self):
        self.director = gutils.trim(self.page,"<font class = 'titulo3'>Director:", '<br><br>')

    def get_plot(self):
        self.plot = gutils.trim(self.page, '<b>Sinopsis:</b><br>', '<br><br>')

    def get_year(self):
        self.year = gutils.trim(self.page, "<font class = 'titulo2'>", ')</font>')
        self.year = gutils.after(self.year, '. (')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, u"<font class = 'titulo3'>Duración:</font> ", u' minutos')
        if self.runtime == '':
            self.runtime = gutils.trim(self.page, "<font class = 'titulo3'>Duraci&oacute;n:</font> ", ' minutos')

    def get_genre(self):
        self.genre = gutils.trim(self.page, u"<font class = 'titulo3'>Género:</font><br>", u'<br><br>')

    def get_cast(self):
        self.cast = ''
        self.cast = gutils.trim(self.page, "<font class = 'titulo3'>Actores:</font><br>", '<br><br>')
        self.cast = string.replace(self.cast, '<br>', "\n")
        self.cast = string.strip(gutils.strip_tags(self.cast))

    def get_classification(self):
        self.classification = gutils.trim(self.page, u"<font class = 'titulo3'>Calificación moral:</font> ", u'<br>')
        if self.classification == '':
            self.classification = gutils.trim(self.page, "<font class = 'titulo3'>Calificaci&oacute;n moral:</font> ", '<br>')

    def get_studio(self):
        self.studio = ''

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = "http://www.culturalianet.com/art/ver.php?art=%s" % str(self.movie_id)

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = gutils.trim(self.page, "<font class = 'titulo3'>Nacionalidad:</font><br>", '<br>')

    def get_rating(self):
        self.rating = gutils.trim(self.page, u"Puntuación: <font class = 'titulo3'>", u'</font>')
        if self.rating == '':
            self.rating = gutils.trim(self.page, "Puntuaci&oacute;n: <font class = 'titulo3'>", '</font>')
        if self.rating:
            self.rating = str(float(gutils.clean(self.rating)))

    def get_screenplay(self):
        self.screenplay = gutils.trim(self.page,u'>Guión:', u'<br><br>')

    def get_cameraman(self):
        self.cameraman = gutils.trim(self.page,u'>Fotografía:', u'<br><br>')

class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search   = 'http://www.culturalianet.com/bus/resu.php?donde=1&texto='
        self.translated_url_search = 'http://www.culturalianet.com/bus/resu.php?donde=1&texto='
        self.encode                = 'iso-8859-1'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        self.sub_search()
        return self.page

    def sub_search(self):
        self.page = gutils.trim(self.page, '<b>ARTICULOS ENCONTRADOS:</b>', '</table>')
        self.page = gutils.after(self.page, '</td></tr><tr><td><b>')
        #self.page = self.page.decode('iso-8859-15')

    def get_searches(self):
        elements = string.split(self.page, '<td><b>')

        if (elements[0]<>''):
            for element in elements:
                self.ids.append(gutils.trim(element, 'ver.php?art=',"'"))
                self.titles.append(gutils.strip_tags(gutils.convert_entities(gutils.trim(element, "target='_top'>", '</a>'))))

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa' : [ 11, 11 ],
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
        '27039' : { 
            'title'               : 'Rocky Balboa',
            'o_title'             : 'Rocky Balboa',
            'director'            : 'Sylvester Stallone',
            'plot'                : True,
            'cast'                : 'Sylvester Stallone\n\
Burt Young\n\
Milo Ventimiglia\n\
Geraldine Hughes\n\
James Francis Kelly III\n\
Tony Burton\n\
A.J. Benza\n\
Talia Shire\n\
Henry G. Sanders\n\
Antonio Tarver\n\
Pedro Lovell\n\
Ana Gerena\n\
Angela Boyd\n\
Louis Giansante\n\
Maureen Schilling',
            'country'             : 'USA',
            'genre'               : 'Drama / Deportes',
            'classification'      : u'No recom. menores de 7 años',
            'studio'              : False,
            'o_site'              : False,
            'site'                : 'http://www.culturalianet.com/art/ver.php?art=27039',
            'trailer'             : False,
            'year'                : 2006,
            'notes'               : False,
            'runtime'             : 99,
            'image'               : True,
            'rating'              : False,
            'cameraman'           : 'J. Clark Mathis',
            'screenplay'          : 'Sylvester Stallone',
            'barcode'             : False
        },
    }
