# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieMyMoviesIt.py 1577 2011-08-30 21:13:26Z mikej06 $'

# Copyright (c) 2007-2011
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

from gettext import gettext as _
import gutils
import movie
import string
import re

plugin_name = "MyMoviesIt"
plugin_description = "mymovies.it"
plugin_url = "www.mymovies.it"
plugin_language = _("Italian")
plugin_author = "Giovanni Sposito, Filippo Valsorda"
plugin_author_email = "<giovanni.sposito@gmail.com>, <filosottile.wiki@gmail.com>"
plugin_version = "0.3"

class Plugin(movie.Movie):

    def __init__(self, id):
        self.encode = 'iso-8859-1'
        self.movie_id = id
        self.url = "http://www.mymovies.it/dizionario/recensione.asp?id=%s" % self.movie_id

    def initialize(self):
        self.castpage = self.open_page(self.parent_window, url='http://www.mymovies.it/cast/?id=' + self.movie_id)

    def get_image(self):
        tmp_image = string.find(self.page, '<img style="float:left; border:solid 1px gray; padding:3px; margin:5px;" src="')
        if tmp_image == -1:
            self.image_url = ''
        else:
            self.image_url = gutils.trim(self.page[tmp_image:], 'src="', '"')

    def get_o_title(self):
        tmp = gutils.trim(self.page, 'Titolo originale <em>', '</em>')
        if not tmp:
            self.o_title = gutils.trim(self.page, '<h1 style="margin-bottom:3px;">', '</h1>')
        else:
            self.o_title = tmp

    def get_title(self):
        self.title = gutils.trim(self.page, '<h1 style="margin-bottom:3px;">', '</h1>')

    def get_director(self):
        self.director = self._find_actor('>Regista', ', ')

    def get_plot(self):
        pos_iniziale = string.find(self.page, '<div id="recensione">')
        self.plot = gutils.trim(self.page[pos_iniziale:],'<p>','</p>')
        self.plot = self.plot.replace(u'\x91', u"'")
        self.plot = self.plot.replace(u'\x93', u'"')
        self.plot = self.plot.replace(u'\x94', u'"')
        self.plot = self.plot.replace(u'\x96', u'-')

    def get_year(self):
        self.year = gutils.regextrim(self.page,'<strong> <a title="Film [0-9]+" href="http://www.mymovies.it/film/[0-9]+/">', '</a></strong>')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, 'durata ', ' min.')

    def get_genre(self):
        self.genre = gutils.regextrim(self.page,'<a title="Film [a-zA-Z]+" href="http://www.mymovies.it/film/[a-zA-Z]+/">', '</a>')

    def get_cast(self):
        self.cast = ''
        elements = string.split(gutils.before(self.castpage, 'Filmmakers</div>'), '<div class="linkblu"')
        i = 3
        while i < len(elements):
            actorandrole = gutils.after(gutils.trim(elements[i], '<div', '</div>'), '>')
            actorandrole = string.replace(actorandrole, '</a>', _(' as '))
            actorandrole = gutils.clean(actorandrole)
            actorandrole = re.sub('(\n|\r)', '', actorandrole)
            actorandrole = re.sub('[ \t]+', ' ', actorandrole)
            self.cast = self.cast + actorandrole + '\n'
            i += 1

    def get_classification(self):
        self.classification = ''

    def get_studio(self):
        self.studio = ''

    def get_o_site(self):
        self.o_site = gutils.rtrim(self.page, '<a href="', '">Sito italiano</a>')
        if not self.o_site:
            self.o_site = gutils.rtrim(self.page, '<a href="', '">Sito ufficiale</a>')

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = "http://www.mymovies.it/trailer/?id=%s" % self.movie_id

    def get_country(self):
        obj = re.search('<strong> <a title="Film [0-9]+" href="http://www.mymovies.it/film/[0-9]+/">', self.page)
        if obj:
            pos = self.page[:obj.start()].rfind('- ')
            self.country = self.page[pos+2:obj.start()]

    def get_rating(self):
        rat = gutils.trim(self.page, '<span itemprop="average">', '</span>')
        if rat != '':
            self.rating = int(round(float(rat.replace(',', '.'))*2, 0))
        else:
            self.rating = 0

    def get_notes(self):
        self.notes = ''

    def get_screenplay(self):
        self.screenplay = self._find_actor('>Sceneggiatura', ', ')

    def get_cameraman(self):
        self.cameraman = self._find_actor('>Fotografia', ', ')
        
    def _find_actor(self, type, delimiter):
        elements = string.split(self.castpage, '<div class="linkblu"')
        result = ''
        i = 1
        while i < len(elements):
            actorandrole = gutils.after(gutils.trim(elements[i], '<div', '</div>'), '>')
            if string.find(actorandrole, type) > 0:
                result = result + gutils.before(actorandrole, '</a>') + delimiter
            i += 1
        if result:
            result = result[:-len(delimiter)]
            result = re.sub('[\n\r\t ]+', ' ', result)
        return result


class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search = "http://www.mymovies.it/database/ricerca/?q="
        self.translated_url_search = "http://www.mymovies.it/database/ricerca/?q="
        self.encode = 'iso-8859-1'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        #self.sub_search()
        return self.page

    def sub_search(self):
        self.page = gutils.trim(self.page, "ho trovato i seguenti risultati:", "Altri risultati tra i film con la parola")

    def get_searches(self):
        elements = string.split(self.page,"<h3 style=\"margin:0px;\">")
        self.number_results = len(elements) - 1

        if self.number_results > 0:
            i = 1
            while i < len(elements):
                element = gutils.trim(elements[i],"<a","</a>")
#                print "******* elemento "+str(i)+" **********\n\n\n\n\n"+element+"\n******fine*******\n\n\n\n\n\n"
#                print "id = "+gutils.trim(element,"recensione.asp?id=","\"")
#                print "title = "+gutils.convert_entities(gutils.strip_tags(gutils.trim(element,'" title="', '"')))

                self.ids.append(gutils.trim(element,"recensione.asp?id=","\""))
                self.titles.append(gutils.convert_entities(gutils.strip_tags(gutils.trim(element,'" title="', '"'))))
                i += 1
        else:
            self.number_results = 0


#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> expected result count }
    #
    test_configuration = {
        'Rocky' : [ 11, 11 ]
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
        '44566' : {
            'title'          : 'Rocky Balboa',
            'o_title'        : 'Rocky Balboa',
            'director'       : 'Sylvester Stallone',
            'plot'           : True,
            'cast'           :'Sylvester Stallone' + _(' as ') + 'Rocky Balboa\n\
Burt Young' + _(' as ') + 'Paulie\n\
Antonio Tarver' + _(' as ') + 'Mason Dixon\n\
Milo Ventimiglia' + _(' as ') + 'Rocky Balboa jr\n\
Geraldine Hughes' + _(' as ') + 'Marie\n\
Mike Tyson' + _(' as ') + 'Se stesso\n\
Tony Burton' + _(' as ') + 'Duke\n\
A.J. Benza' + _(' as ') + 'L.C.\n\
James Francis Kelly III' + _(' as ') + 'Steps\n\
Talia Shire' + _(' as ') + 'Adriana Balboa (materiale d\'archivio)\n\
Lou DiBella' + _(' as ') + 'Se stesso\n\
Henry G. Sanders' + _(' as ') + 'Martin\n\
Pedro Lovell' + _(' as ') + 'Spider Rico\n\
Ana Gerena' + _(' as ') + 'Isabel\n\
Angela Boyd' + _(' as ') + 'Angie',
            'country'        : 'USA',
            'genre'          : 'Sportivo',
            'classification' : False,
            'studio'         : False,
            'o_site'         : 'http://www.mgm.com/rocky_balboa/',
            'site'           : 'http://www.mymovies.it/dizionario/recensione.asp?id=44566',
            'trailer'        : 'http://www.mymovies.it/trailer/?id=44566',
            'year'           : 2006,
            'notes'          : False,
            'runtime'        : 102,
            'image'          : True,
            'rating'         : 6,
            'cameraman'      : 'J. Clark Mathis',
            'screenplay'     : 'Sylvester Stallone'
        }
    }
