# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieE-Pipoca.py 1467 2010-10-14 18:16:49Z mikej06 $'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ożarowski
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

# Updated on 04/29/2007 by Djohnson "Joe" Lima
# joe1310@terra.com.br - São Paulo/Brasil


import gutils
import movie
import string

plugin_name         = "Interfilmes"
plugin_description  = "Interfilmes Brasil"
plugin_url          = "www.interfilmes.com"
plugin_language     = _("Brazilian Portuguese")
plugin_author       = "Elencarlos Soares"
plugin_author_email = "<elencarlos@gmail.com>"
plugin_version      = "0.3"

class Plugin(movie.Movie):

    def __init__(self, id):
        self.encode   = 'iso-8859-1'
        self.movie_id = id
        self.url      = "http://www.interfilmes.com/filme_" + str(self.movie_id) + "_.html"
        print(self.url)

    def get_image(self):
        """Finds the film's poster image"""
        tmp_pic = gutils.trim(self.page, "content=\"http://www.interfilmes.com/FILMES/", "\"")
        self.image_url = "http://www.interfilmes.com/FILMES/" + tmp_pic
        print(self.image_url)

    def get_o_title(self):
        self.o_title = string.capwords(gutils.trim(self.page, "<u>Título Original:</u>&nbsp;", "<br>"))
        print(self.o_title)
        
    def get_title(self):
        self.title = gutils.trim(self.page, "<u>Título no Brasil:</u>&nbsp;", "<br><u>")
        print(self.title)

    def get_director(self):
        self.director = gutils.strip_tags(gutils.trim(self.page, "<u>Direção:</u>&nbsp;", "<br></font>"))
        print(self.director)

    def get_plot(self):
        self.plot = gutils.trim(self.page, "<div align=\"justify\">", "</div>")
        print(self.plot)

    def get_year(self):
        self.year = gutils.trim(self.page, "<u>Ano de Lançamento:</u>&nbsp;", "<br>")

    def get_runtime(self):
        "Find the film's running time"
        self.runtime = gutils.trim(self.page, "<u>Tempo de Duração:</u>", " minutos<br>")
        print(self.runtime)
        self.runtime = self.runtime[4:]
        print(self.runtime)

    def get_genre(self):
        self.genre = gutils.trim(self.page, "nero:</u>&nbsp;", "<br>")

    def get_cast(self):
        self.cast = ""

    def get_classification(self):
        self.classification = ""

    def get_studio(self):
        self.studio = gutils.trim(self.page, "<u>Estúdio/Distrib.:</u>&nbsp;", "<br>")

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        tmp_site = gutils.trim(self.page, "content=\"http://www.interfilmes.com/filme_", "\"")
        self.site = "http://www.interfilmes.com/filme_" + tmp_site
        print(self.site)

    def get_trailer(self):        
        self.trailer = ""
            
    def get_country(self):  
        self.country = gutils.trim(self.page, "<u>País de Origem:</u>&nbsp;", "<br>")

    def get_rating(self):
        self.rating = ""

    def get_screenplay(self):
        self.screenplay = ""

    def get_cameraman(self):
        self.cameraman = ""

class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.original_url_search = "http://interfilmes.com/busca.%s.html"
        self.translated_url_search = self.original_url_search
        self.encode = 'iso-8859-1'        
        
    def search(self, parent_window):
	    
        if not self.open_search(parent_window):
            return None
        self.sub_search()
        return self.page

    def sub_search(self):
        "Isolating just a portion (with the data we want) of the results"
        self.page = gutils.trim(self.page, "<td bgcolor=#DEFEE6 width=100% height=1 colspan=3>", "</tr></table>    </td>")

    def get_searches(self):

        elements = string.split(self.page, "<td width=100% height=18")
        self.number_results = elements[-1]

        if (elements[0] != ''):
            for element in elements:
                print (gutils.trim(element, "align=center valign=top><a href=\"filme_", "_"))
                self.ids.append(gutils.trim(element, "align=center valign=top><a href=\"filme_", "_"))
                print(gutils.strip_tags(gutils.trim(element, "<font color=#FFFFFF face=Verdana size=2>", "</font></a></b></td>")+' - '+gutils.trim(element, "Ano de Lançamento:", "<br>")))
                self.titles.append(gutils.strip_tags(gutils.trim(element, "<font color=#FFFFFF face=Verdana size=2>", "</font></a></b></td>")+' - '+gutils.trim(element, "Ano de Lançamento:", "<br>")))
        else:
            self.number_results = 0

			
