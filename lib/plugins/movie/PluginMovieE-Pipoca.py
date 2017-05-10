# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieE-Pipoca.py 1633 2012-12-28 23:11:42Z mikej06 $'

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


import gutils, movie, string

plugin_name         = "E-Pipoca"
plugin_description  = "E-Pipoca Brasil"
plugin_url          = "www.epipoca.com.br"
plugin_language     = _("Brazilian Portuguese")
plugin_author       = "Vasco Nunes"
plugin_author_email = "<vasco.m.nunes@gmail.com>"
plugin_version      = "0.6"

class Plugin(movie.Movie):
    "A movie plugin object"
    def __init__(self, id):
        self.encode   = 'iso-8859-1'
        self.movie_id = id
        self.url      = "http://www.epipoca.com.br/filmes_detalhes.php?idf=" + str(self.movie_id)

    def initialize(self):
        self.page_cast = self.open_page(url = 'http://www.epipoca.com.br/filmes_ficha.php?idf=' + str(self.movie_id))

    def get_image(self):
        "Find the film's poster image"
        tmp_pic = gutils.trim(self.page, "images/filmes/poster/poster_", "\"")
        self.image_url = \
            "http://www.epipoca.com.br/images/filmes/poster/poster_" + tmp_pic

    def get_o_title(self):
        "Find the film's original title"
        self.o_title = string.capwords(gutils.trim(self.page, "</font><br>(", ", "))

    def get_title(self):
        """Find the film's local title.
        Probably the original title translation"""
        self.title = gutils.trim(self.page, "<TITLE>", " (")

    def get_director(self):
        "Find the film's director"
        self.director = gutils.trim(self.page, "<b>Diretor(es): </b>", "</a></td>")

    def get_plot(self):
        "Find the film's plot"
        self.plot = gutils.trim(self.page, "<b>SINOPSE</b></font><br><br>", "</td></tr>")

    def get_year(self):
        "Find the film's year"
        self.year = gutils.trim(self.page, "<a href=\"busca_mais.php?opc=ano&busca=", "\">")

    def get_runtime(self):
        "Find the film's running time"
        self.runtime = gutils.trim(self.page, "<td><b>Dura", " min.</td>")
        self.runtime = self.runtime[9:]

    def get_genre(self):
        "Find the film's genre"
        self.genre = gutils.trim(self.page, "<a href=\"busca_mais.php?opc=genero&busca=", "\">")

    def get_cast(self):
        "Find the actors. Try to make it line separated."
        self.cast = ""
        tmp = gutils.trim(self.page_cast, '<b>Elenco / Cast</b>', '</table>')
        elements = tmp.split('<tr>')
        for index in range(1, len(elements), 1):
            element = elements[index]
            self.cast = self.cast + gutils.strip_tags(element.replace(' ... ', _(' as '))) + '\n'

    def get_classification(self):
        "Find the film's classification"
        self.classification = ""

    def get_studio(self):
        "Find the studio"
        self.studio = gutils.trim(self.page, "<b>Distribuidora(s): </b>", "</a></td>")

    def get_o_site(self):
        "Find the film's oficial site"
        self.o_site = "http://www.epipoca.com.br/filmes_web.php?idf=" + str(self.movie_id)

    def get_site(self):
        "Find the film's imdb details page"
        self.site = "http://www.epipoca.com.br/filmes_ficha.php?idf=" + str(self.movie_id)

    def get_trailer(self):
        "Find the film's trailer page or location"
        self.trailer = "http://www.epipoca.com.br/filmes_trailer.php?idf=" + str(self.movie_id)
            
    def get_country(self):
        "Find the film's country"
        self.country = gutils.trim(self.page, "<a href=\"busca_mais.php?opc=pais&busca=", "\">")

    def get_rating(self):
        """Find the film's rating. From 0 to 10.
        Convert if needed when assigning."""
        tmp_rating = gutils.trim(self.page, "<br><b>Cota", " (")
        tmp_rating = gutils.after(tmp_rating, "</b>")
        if tmp_rating <> "":
            tmp_rating = string.replace(tmp_rating,',','.')
            self.rating = str( float(string.strip(tmp_rating)) )
        else:
            self.rating = ""

    def get_screenplay(self):
        self.screenplay = gutils.trim(self.page_cast, '<b>Roteirista(s) / Writers</b>', '</table>').replace('</tr><tr>', ', ')

    def get_cameraman(self):
        self.cameraman = gutils.trim(self.page_cast, u'<b>Fotógrafo(s) / Cinematographers</b>', u'</table>').replace(u'</tr><tr>', u', ')

class SearchPlugin(movie.SearchMovie):
    "A movie search object"
    def __init__(self):
        self.original_url_search = \
            "http://www.epipoca.com.br/busca.php?opc=todos&busca="
        self.translated_url_search = \
            "http://www.epipoca.com.br/busca.php?opc=todos&busca="
        self.encode='iso-8859-1'

    def search(self, parent_window):
        "Perform the web search"
        if not self.open_search(parent_window):
            return None
        self.sub_search()
        return self.page

    def sub_search(self):
        "Isolating just a portion (with the data we want) of the results"
        self.page = gutils.trim(self.page, \
            "&nbsp;Resul","><b>Not") 

    def get_searches(self):
        "Try to find both id and film title for each search result"
        elements = string.split(self.page, "<td width=\"55\" align=\"center\" bgcolor=")
        self.number_results = elements[-1]

        if (elements[0] != ''):
            for element in elements:
                self.ids.append(gutils.trim(element, "<a href=\"filmes_detalhes.php?idf=", "\">"))
                self.titles.append(gutils.strip_tags(gutils.trim(element, "<font class=\"titulo\">", "<b>Adicionar aos meus filmes favoritos</b>") ))
        else:
            self.number_results = 0

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa' : [ 7, 7 ],
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
        '11521' : { 
            'title'               : 'Rocky Balboa',
            'o_title'             : 'Rocky Balboa',
            'director'            : 'Sylvester Stallone',
            'plot'                : True,
            'cast'                : 'Sylvester Stallone' + _(' as ') + 'Rocky Balboa\n\
Burt Young' + _(' as ') + 'Paulie\n\
Antonio Tarver' + _(' as ') + 'Mason \'The Line\' Dixon\n\
Geraldine Hughes' + _(' as ') + 'Marie\n\
Milo Ventimiglia' + _(' as ') + 'Robert Jr.\n\
Tony Burton' + _(' as ') + 'Duke\n\
A.J. Benza' + _(' as ') + 'L.C.\n\
James Francis Kelly III' + _(' as ') + 'Steps\n\
Talia Shire' + _(' as ') + 'Adrian (imagens de arquivo)\n\
Lou DiBella' + _(' as ') + 'Lou DiBella\n\
Mike Tyson (1)' + _(' as ') + 'Mike Tyson\n\
Henry G. Sanders' + _(' as ') + 'Martin\n\
Pedro Lovell' + _(' as ') + 'Spider Rico\n\
Ana Gerena' + _(' as ') + 'Isabel\n\
Angela Boyd' + _(' as ') + 'Angie\n\
Louis Giansante' + _(' as ') + 'Bandido do bar\n\
Maureen Schilling' + _(' as ') + 'Bartender do Lucky\n\
Lahmard Tate¹' + _(' as ') + 'X-Cell\n\
Woodrow W. Paige¹' + _(' as ') + 'Comentarista da ESPN\n\
Skip Bayless' + _(' as ') + 'Comentarista da ESPN\n\
Jay Crawford' + _(' as ') + 'Comentarista da ESPN\n\
Brian Kenny' + _(' as ') + 'Apresentador da ESPN\n\
Dana Jacobson' + _(' as ') + 'Apresentador da ESPN\n\
Chuck Johnson¹' + _(' as ') + 'Apresentador da ESPN\n\
James Binns' + _(' as ') + 'Comissário\n\
Johnnie Hobbs Jr.' + _(' as ') + 'Comissário\n\
Barney Fitzpatrick' + _(' as ') + 'Comissário\n\
Jim Lampley' + _(' as ') + 'Comentarista da HBO\n\
Larry Merchant' + _(' as ') + 'Comentarista da HBO\n\
Max Kellerman' + _(' as ') + 'Comentarista da HBO\n\
LeRoy Neiman' + _(' as ') + 'LeRoy Neiman\n\
Bert Randolph Sugar' + _(' as ') + 'Repórter da Ring Magazine\n\
Bernard Fernández' + _(' as ') + 'Articulista da Boxing Association of America\n\
Gunnar Peterson' + _(' as ') + 'Treinador de levantamento de peso\n\
Yahya' + _(' as ') + 'Oponente de Dixon\n\
Marc Ratner (1)' + _(' as ') + 'Oficial de luta\n\
Anthony Lato Jr.' + _(' as ') + 'Inspetor de Rocky\n\
Jack Lazzarado' + _(' as ') + 'Inspetor de Dixon\n\
Michael Buffer' + _(' as ') + 'Anunciador de luta\n\
Joe Cortez' + _(' as ') + 'Árbitro\n\
Carter Mitchell (1)' + _(' as ') + 'Shamrock Foreman\n\
Vinod Kumar (1)' + _(' as ') + 'Ravi\n\
Fran Pultro' + _(' as ') + 'Pai no restaurante\n\
Frank Stallone Jr.¹' + _(' as ') + 'Cliente do restaurante\n\
Jody Giambelluca' + _(' as ') + 'Cliente do restaurante\n\
Tobias Segal' + _(' as ') + 'Amigo de Robert\n\
Tim Carr' + _(' as ') + 'Amigo de Robert\n\
Matt Frack' + _(' as ') + 'Amigo de Robert\n\
Paul Dion Monte' + _(' as ') + 'Amigo de Robert\n\
Kevin King Templeton' + _(' as ') + 'Amigo de Robert\n\
Robert Michael Kelly' + _(' as ') + 'Senhor Tomilson\n\
Rick Buchborn' + _(' as ') + 'Fã de Rocky\n\
Nick Baker (1)' + _(' as ') + 'Bartender do pub irlandês\n\
Don Sherman' + _(' as ') + 'Andy\n\
Stu Nahan' + _(' as ') + 'Comentarista da luta pelo computador\n\
Gary Compton' + _(' as ') + 'Segurança\n\
Ricky Cavazos' + _(' as ') + 'Espectador da luta (não creditado)\n\
Dolph Lundgren' + _(' as ') + 'Capitão Ivan Drago (imagens de arquivo) (não creditado)\n\
Burgess Meredith' + _(' as ') + 'Mickey (imagens de arquivo) (não creditado)\n\
Mr. T' + _(' as ') + 'Clubber Lang (imagens de arquivo) (não creditado)\n\
Carl Weathers' + _(' as ') + 'Apollo Creed (imagens de arquivo) (não creditado)',
            'country'             : 'EUA',
            'genre'               : 'Ação',
            'classification'      : False,
            'studio'              : 'Fox Film',
            'o_site'              : 'http://www.epipoca.com.br/filmes_web.php?idf=11521',
            'site'                : 'http://www.epipoca.com.br/filmes_ficha.php?idf=11521',
            'trailer'             : 'http://www.epipoca.com.br/filmes_trailer.php?idf=11521',
            'year'                : 2006,
            'notes'               : False,
            'runtime'             : 102,
            'image'               : True,
            'rating'              : 9,
            'cameraman'           : 'J. Clark Mathis',
            'screenplay'          : 'Sylvester Stallone ... Escrito por, Sylvester Stallone ... Personagens',
            'barcode'             : False
        },
    }
