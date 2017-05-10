# -*- coding: iso-8859-15 -*-

__revision__ = '$Id: PluginMovieIMDB-es.py 389 2006-07-29 18:43:35Z piotrek $'

# Copyright (c) 2006-2011 Pedro D. Sánchez
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

plugin_name         = 'IMDb-es'
plugin_description  = 'Internet Movie Database Spanish'
plugin_url          = 'www.imdb.es'
plugin_language     = _('Spanish')
plugin_author       = 'Pedro D. Sánchez'
plugin_author_email = '<pedrodav@gmail.com>'
plugin_version      = '0.4'

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode='iso-8859-15'
        self.movie_id = id
        self.url = "http://www.imdb.es/title/tt%s" % str(self.movie_id)

    def initialize(self):
        self.cast_page = self.open_page(url=self.url + '/fullcredits')
        self.plot_page = self.open_page(url=self.url + '/plotsummary')
        self.comp_page = self.open_page(url=self.url + '/companycredits')
        # looking for the original imdb page
        self.imdb_page = self.open_page(url="http://www.imdb.com/title/tt%s" % str(self.movie_id))
        self.imdb_plot_page = self.open_page(url="http://www.imdb.com/title/tt%s/plotsummary" % str(self.movie_id))
        # correction of all &#xxx entities
        self.page = gutils.convert_entities(self.page)
        self.cast_page = gutils.convert_entities(self.cast_page)
        self.plot_page = gutils.convert_entities(self.plot_page)
        self.comp_page = gutils.convert_entities(self.comp_page)
        self.imdb_page = gutils.convert_entities(self.imdb_page)
        self.imdb_plot_page = gutils.convert_entities(self.imdb_plot_page)

    def get_image(self):
        tmp = string.find(self.page, 'a name="poster"')
        if tmp == -1:        # poster not available
            self.image_url = ''
        else:
            self.image_url = gutils.trim(self.page[tmp:], 'src="', '"')

    def get_o_title(self):
        self.o_title = gutils.trim(self.page, '<h1>', '<')

    def get_title(self):
        tmp = 0
        tmpTot = 0
        while (tmp <> -1):
            auxTitle = ''
            tmp = string.find(self.page[tmpTot:], '<i class="transl">')
            if tmp <> -1:
                auxTitle = gutils.trim(self.page[tmpTot:], '<i class="transl">', '</i>')
                if string.find(auxTitle, '(Spain)') <> -1:
                    auxTitle = string.replace(auxTitle, '&#32;', ' ')
                    auxTitle = string.replace(auxTitle, ' (Argentina) ', '')
                    auxTitle = string.replace(auxTitle, ' (Spain) ', '')
                    auxTitle = string.replace(auxTitle, ' (Mexico) ', '')
                    auxTitle = string.replace(auxTitle, '  [es]', '')
                    tmp = -1
                tmpTot = tmpTot + tmp + 1
        if auxTitle <> '':
            self.title = auxTitle
        else:
            self.title = self.o_title

    def get_director(self):
        self.director = '<' + gutils.trim(self.cast_page,'>Dirigida por<', '</table>')

    def get_plot(self):
        self.plot = gutils.trim(self.page, '<b class="ch">Resumen', '<a href="/rg/title-tease/plot')
        self.plot = gutils.after(self.plot, ':</b> ')

        self.plot = gutils.trim(self.page, '<h5>Trama:</h5>', '</div>')
        self.plot = self.__before_more(self.plot)
        tmp = gutils.trim(self.plot_page, '<div id="swiki.2.1">', '</div>')
        if tmp:
            self.plot = tmp
        elements = string.split(self.plot_page, '<p class="plotpar">')
        if len(elements) > 1:
            self.plot = self.plot + '\n\n'
            elements[0] = ''
            for element in elements:
                if element != '':
                    self.plot = self.plot + gutils.strip_tags(gutils.before(element, '</a>')) + '\n'
        if not self.plot:
            # nothing in spanish found, try original
            self.plot = gutils.regextrim(self.imdb_page, '<h5>Plot:</h5>', '(</div>|<a href.*)')
            self.plot = self.__before_more(self.plot)
            elements = string.split(self.imdb_plot_page, '<p class="plotpar">')
            if len(elements) > 1:
                self.plot = self.plot + '\n\n'
                elements[0] = ''
                for element in elements:
                    if element <> '':
                        self.plot = self.plot + gutils.strip_tags(gutils.before(element, '</a>')) + '\n\n'

    def get_year(self):
        self.year = gutils.trim(self.page, '<h1>', ' <span class')
        self.year = gutils.trim(self.year, '(', ')')

    def get_runtime(self):
        self.runtime = gutils.trim(self.page, u'<h5>Duración:</h5>', ' min')
        if self.runtime == '':
            self.runtime = gutils.trim(self.page, '<h5>Duraci&oacute;n:</h5>', ' min')

    def get_genre(self):
        self.genre = gutils.trim(self.page, u'<h5>Género:</h5>', '</div>')
        self.genre = string.replace(self.genre, u'(más)', '')
        self.genre = string.replace(self.genre, '(m&aacute;s)', '')

    def get_cast(self):
        self.cast = ''
        self.cast = gutils.trim(self.cast_page, '<table class="cast">', '</table>')
        if self.cast == '':
            self.cast = gutils.trim(self.page, '<table class="cast">', '</table>')
        self.cast = string.replace(self.cast, ' ... ', _(' as ').encode('utf8'))
        self.cast = string.replace(self.cast, '...', _(' as ').encode('utf8'))
        self.cast = string.replace(self.cast, '</tr><tr>', "\n")
        self.cast = re.sub('</tr>[ \t]*<tr[ \t]*class="even">', "\n", self.cast)
        self.cast = re.sub('</tr>[ \t]*<tr[ \t]*class="odd">', "\n", self.cast)
        self.cast = self.__before_more(self.cast)
        self.cast = re.sub('[ ]+', ' ', self.cast)

    def get_classification(self):
        self.classification = gutils.trim(self.page, u'<h5>Clasificación:</h5>', '</div>')

    def get_studio(self):
        self.studio = gutils.trim(self.comp_page, u'<h2>Compañías Productores</h2>', '</ul>')
        self.studio = string.replace(self.studio, '</li><li>', ', ')

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = "http://www.imdb.es/title/tt%s" % self.movie_id

    def get_trailer(self):
        self.trailer = "http://www.imdb.es/title/tt%s/trailers" % self.movie_id

    def get_country(self):
        self.country = gutils.trim(self.page, u'<h5>País:</h5>', '</div>')
        if self.country == '':
            self.country = gutils.trim(self.page, '<h5>Pa&iacute;s:</h5>', '</a>')
        self.country = self.__before_more(self.country)
        self.country = re.sub('[\n]+', '', self.country)
        self.country = re.sub('[ ]+', ' ', self.country)

    def get_rating(self):
        self.rating = gutils.trim(self.page, u'<h5>Calificación:</h5>', '/10</b>')
        if self.rating == '':
            self.rating = gutils.trim(self.page, '<h5>Calificaci&oacute;n de los usuarios:</h5>', '/10</b>')
        if self.rating:
            try:
                tmp = re.findall('[0-9.,]+', gutils.clean(self.rating))
                if tmp and len(tmp) > 0:
                    self.rating = round(float(tmp[0].replace(',', '.')))
            except:
                self.rating = 0
        else:
            self.rating = 0

    def get_screenplay(self):
        self.screenplay = ''
        parts = re.split('<a href=', gutils.trim(self.cast_page, u'>Créditos del guión<', '</table>'))
        if len(parts) > 1:
            for part in parts[1:]:
                screenplay = gutils.trim(part, '>', '<')
                if screenplay == 'WGA':
                    continue
                screenplay = screenplay.replace(' (escrito por)', '')
                screenplay = screenplay.replace(' and<', '<')
                self.screenplay = self.screenplay + screenplay + ', '
            if len(self.screenplay) > 2:
                self.screenplay = self.screenplay[0:len(self.screenplay) - 2]

    def get_cameraman(self):
        self.cameraman = string.replace('<' + gutils.trim(self.cast_page, u'>Fotografía por<', '</table>'), u'(director de fotografía) ', '')

    def __before_more(self, data):
        for element in [u'>Ver más<', '>Full summary<', '>Full synopsis<']:
            tmp = string.find(data, element)
            if tmp>0:
                data = data[:tmp] + '>'
        return data

class SearchPlugin(movie.SearchMovie):
    PATTERN = re.compile(r"""<a href=['"]/title/tt([0-9]+)/[^>]+[>](.*?)</td>""")
    PATTERN_DIRECT = re.compile(r"""value="/title/tt([0-9]+)""")

    def __init__(self):
        self.original_url_search = 'http://www.imdb.es/find?s=tt&q='
        self.translated_url_search = 'http://www.imdb.es/find?s=tt&q='
        self.encode = 'utf8'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        elements = string.split(self.page, '<tr')
        if len(elements):
            for element in elements[1:]:
                match = self.PATTERN.findall(element)
                if len(match) > 1:
                    tmp = re.sub('^[0-9]+[.]', '', gutils.clean(match[1][1]))
                    self.ids.append(match[1][0])
                    self.titles.append(tmp)
        if len(self.ids) < 2:
            # try to find a direct result
            match = self.PATTERN_DIRECT.findall(self.page)
            if len(match) > 0:
                self.ids.append(match[0])


#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa'         : [ 10, 10 ]
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
        '0479143' : {
            'title'             : 'Rocky Balboa',
            'o_title'           : 'Rocky Balboa',
            'director'          : 'Sylvester Stallone',
            'plot'              : True,
            'cast'              : 'Sylvester Stallone' + _(' as ') + 'Rocky Balboa\n\
Burt Young' + _(' as ') + 'Paulie\n\
Antonio Tarver' + _(' as ') + 'Mason \'The Line\' Dixon\n\
Geraldine Hughes' + _(' as ') + 'Marie\n\
Milo Ventimiglia' + _(' as ') + 'Robert Balboa Jr.\n\
Tony Burton' + _(' as ') + 'Duke\n\
A.J. Benza' + _(' as ') + 'L.C.\n\
James Francis Kelly III' + _(' as ') + 'Steps\n\
Talia Shire' + _(' as ') + 'Adrian (tomas de archivo)\n\
Lou DiBella' + _(' as ') + u'Él Mismo\n\
Mike Tyson' + _(' as ') + u'Él Mismo\n\
Henry G. Sanders' + _(' as ') + 'Martin\n\
Pedro Lovell' + _(' as ') + 'Spider Rico\n\
Ana Gerena' + _(' as ') + 'Isabel\n\
Angela Boyd' + _(' as ') + 'Angie\n\
Louis Giansante' + _(' as ') + 'Bar Thug\n\
Maureen Schilling' + _(' as ') + 'Lucky\'s Bartender\n\
Lahmard J. Tate' + _(' as ') + 'X-Cell (como Lahmard Tate)\n\
Woody Paige' + _(' as ') + 'ESPN Commentator (como Woodrow W. Paige)\n\
Skip Bayless' + _(' as ') + 'ESPN Commentator\n\
Jay Crawford' + _(' as ') + 'ESPN Commentator\n\
Brian Kenny' + _(' as ') + 'ESPN Host\n\
Dana Jacobson' + _(' as ') + 'ESPN Host\n\
Charles Johnson' + _(' as ') + 'ESPN Host (como Chuck Johnson)\n\
James Binns' + _(' as ') + 'Commissioner (como James J. Binns)\n\
Johnnie Hobbs Jr.' + _(' as ') + 'Commissioner\n\
Barney Fitzpatrick' + _(' as ') + 'Commissioner\n\
Jim Lampley' + _(' as ') + 'HBO Commentator\n\
Larry Merchant' + _(' as ') + 'HBO Commentator\n\
Max Kellerman' + _(' as ') + 'HBO Commentator\n\
LeRoy Neiman' + _(' as ') + u'Él Mismo\n\
Bert Randolph Sugar' + _(' as ') + u'Ring Magazine Reporter\n\
Bernard Fernández' + _(' as ') + 'Boxing Association of America Writer (como Bernard Fernandez)\n\
Gunnar Peterson' + _(' as ') + 'Weightlifting Trainer\n\
Yahya' + _(' as ') + 'Dixon\'s Opponent\n\
Marc Ratner' + _(' as ') + 'Weigh-In Official\n\
Anthony Lato Jr.' + _(' as ') + 'Rocky\'s Inspector\n\
Jack Lazzarado' + _(' as ') + 'Dixon\'s Inspector\n\
Michael Buffer' + _(' as ') + 'Ring Announcer\n\
Joe Cortez' + _(' as ') + u'Árbitro\n\
Carter Mitchell' + _(' as ') + 'Shamrock Foreman\n\
Vinod Kumar' + _(' as ') + 'Ravi\n\
Fran Pultro' + _(' as ') + 'Father at Restaurant\n\
Frank Stallone' + _(' as ') + 'Dinner Patron (como Frank Stallone Jr.)\n\
Jody Giambelluca' + _(' as ') + 'Dinner Patron\n\
Tobias Segal' + _(' as ') + 'Robert\'s Friend\n\
Tim Carr' + _(' as ') + 'Robert\'s Friend\n\
Matt Frack' + _(' as ') + 'Robert\'s Friend #3\n\
Paul Dion Monte' + _(' as ') + 'Robert\'s Friend\n\
Kevin King Templeton' + _(' as ') + 'Robert\'s Friend (como Kevin King-Templeton)\n\
Robert Michael Kelly' + _(' as ') + 'Mr. Tomilson\n\
Rick Buchborn' + _(' as ') + 'Rocky Fan\n\
Nick Baker' + _(' as ') + 'Irish Pub Bartender\n\
Don Sherman' + _(' as ') + 'Andy\n\
Stu Nahan' + _(' as ') + 'Computer Fight Commentator (voz)\n\
Gary Compton' + _(' as ') + u'Oficial de Seguridad listado alfabético del resto del reparto:\n\
Vale Anoai' + _(' as ') + 'Shopper in Italian Market\n\
Sikander Malik' + _(' as ') + 'Boxer\n\
Michael Ahl' + _(' as ') + 'Restaurant Patron (sin acreditar)\n\
Andrew Aninsman' + _(' as ') + 'Promoter (sin acreditar)\n\
Ben Bachelder' + _(' as ') + 'The Arm (sin acreditar)\n\
Lacy Bevis' + _(' as ') + 'Boxing Spectator (sin acreditar)\n\
Tim Brooks' + _(' as ') + 'Boxing Spectator (sin acreditar)\n\
D.T. Carney' + _(' as ') + 'High Roller (sin acreditar)\n\
Ricky Cavazos' + _(' as ') + 'Boxing Spectator (sin acreditar)\n\
Rennie Cowan' + _(' as ') + 'Boxing Spectator (sin acreditar)\n\
Kevin Deon' + _(' as ') + 'Jeno (sin acreditar)\n\
Deon Derrico' + _(' as ') + 'High Roller at Limo (sin acreditar)\n\
Jacob \'Stitch\' Duran' + _(' as ') + 'Dixon\'s Trainer (sin acreditar)\n\
Simon P. Edwards' + _(' as ') + 'Crowd Member (sin acreditar)\n\
Ruben Fischman' + _(' as ') + 'High-Roller in Las Vegas (sin acreditar)\n\
David Gere' + _(' as ') + 'Patron at Adrian\'s (sin acreditar)\n\
Noah Jacobs' + _(' as ') + 'Boxing Fan (sin acreditar)\n\
Mark J. Kilbane' + _(' as ') + 'Businessman (sin acreditar)\n\
Zach Klinefelter' + _(' as ') + 'Boxing Spectator (sin acreditar)\n\
David Kneeream' + _(' as ') + 'Adrian\'s Patron (sin acreditar)\n\
Dolph Lundgren' + _(' as ') + 'Captain Ivan Drago (tomas de archivo) (sin acreditar)\n\
Dean Mauro' + _(' as ') + 'Sports Journalist (sin acreditar) (sin confirmar)\n\
Burgess Meredith' + _(' as ') + 'Mickey Goldmill (tomas de archivo) (sin acreditar)\n\
Dan Montero' + _(' as ') + 'Boxing Spectator (sin acreditar)\n\
Babs Moran' + _(' as ') + 'Obnoxious Fan (sin acreditar)\n\
Keith Moyer' + _(' as ') + 'Administrador del Bar (sin acreditar)\n\
Mr. T' + _(' as ') + 'Clubber Lang (tomas de archivo) (sin acreditar)\n\
Carol Anne Mueller' + _(' as ') + 'Restaurant Patron (sin acreditar)\n\
Jacqueline Olivia' + _(' as ') + 'Chica (sin acreditar)\n\
Brian H. Scott' + _(' as ') + 'Ringside Cop #1 (sin acreditar)\n\
Keyon Smith' + _(' as ') + 'Boxing Spectator (sin acreditar)\n\
Frank Traynor' + _(' as ') + 'Abogado (sin acreditar)\n\
Ryan Tygh' + _(' as ') + 'Ring Photographer (sin acreditar)\n\
Kimberly Villanova' + _(' as ') + 'Businesswoman (sin acreditar)',
            'country'           : 'Estados Unidos',
            'genre'             : u'Drama | Deporte',
            'classification'    : u'Estados Unidos:PG  | Singapur:PG  | Finlandia:K-11  | Reino Unido:12A  | Canadá:G (British Columbia) | Australia:M  | Irlanda:PG  | Hong Kong:IIA  | México:A  | Noruega:11  | Suiza:12 (canton of Vaud) | Suiza:12 (canton of Geneva) | Brasil:12  | Argentina:Atp  | Malasia:U  | Filipinas:PG-13 (MTRCB) | Portugal:M/12  | Corea del Sur:12  | Suecia:11  | Nueva Zelanda:M  | Italia:T  | Alemania:12  | Francia:U',
            'studio'            : 'Metro-Goldwyn-Mayer (MGM) (presents) (copyright owner), Columbia Pictures (presents) (copyright owner), Revolution Studios (presents) (copyright owner), Rogue Marble',
            'o_site'            : False,
            'site'              : 'http://www.imdb.es/title/tt0479143',
            'trailer'           : 'http://www.imdb.es/title/tt0479143/trailers',
            'year'              : 2006,
            'notes'             : False,
            'runtime'           : 102,
            'image'             : True,
            'rating'            : 7,
            'screenplay'        : 'Sylvester Stallone, Sylvester Stallone',
            'cameraman'         : 'Clark Mathis',
        },
    }
