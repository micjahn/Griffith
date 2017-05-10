# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieIMDB-de.py 1638 2013-01-29 21:36:08Z mikej06 $'

# Copyright (c) 2007-2012 Michael Jahn
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

import gutils, movie
import string, re

plugin_name         = 'IMDb-de'
plugin_description  = 'Internet Movie Database German'
plugin_url          = 'www.imdb.de'
plugin_language     = _('German')
plugin_author       = 'Michael Jahn'
plugin_author_email = 'mikej06@hotmail.com'
plugin_version      = '1.9'

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode   = 'iso8859-1'
        self.movie_id = id
        self.url      = "http://www.imdb.com/title/tt%s" % str(self.movie_id)

    def initialize(self):
        self.cast_page = self.open_page(url=self.url + '/fullcredits')
        self.plot_page = self.open_page(url=self.url + '/plotsummary')
        self.comp_page = self.open_page(url=self.url + '/companycredits')
        self.tagl_page = self.open_page(url=self.url + '/taglines')
        self.cert_page = self.open_page(url=self.url + '/parentalguide')
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
        self.image_url = ''
        tmp = gutils.trim(self.page, '<div class="poster">', '</div>')
        if tmp:
            self.image_url = gutils.trim(tmp, 'src="', '"')

    def get_o_title(self):
        self.o_title = gutils.regextrim(self.page, 'class="title-extra"[^>]*>', '<')
        if not self.o_title:
            self.o_title = gutils.regextrim(self.page, '<h1>', '([ ]|[&][#][0-9]+[;])<span')
        if not self.o_title:
            self.o_title = re.sub(' [(].*', '', gutils.trim(self.page, '<title>', '</title>'))
        self.o_title = re.sub('"', '', self.o_title)

    def get_title(self):    # same as get_o_title()
        self.title = gutils.regextrim(self.page, '<h1>', '([ ]|[&][#][0-9]+[;])<span')
        if not self.title:
            self.title = re.sub(' [(].*', '', gutils.trim(self.page, '<title>', '</title>'))

    def get_director(self):
        self.director = gutils.trim(self.cast_page,'>Directed by', '</table>')
        tmpelements = re.split('href="', self.director)
        delimiter = ''
        self.director = ''
        for index in range(1, len(tmpelements), 1):
            tmpelement = gutils.before(gutils.after(tmpelements[index], '>'), '<')
            self.director = self.director + tmpelement + delimiter
            delimiter =', '

    def get_plot(self):
        self.plot = gutils.before(gutils.after(gutils.trim(self.page, 'name="description"', '/>'), 'content="'), '"')
        germanplotelements = string.split(self.plot_page, 'class="plotSummary"')
        if len(germanplotelements) > 1:
            self.plot = self.plot + '\n\n'
            germanplotelements[0] = ''
            for element in germanplotelements:
                if element <> '':
                    self.plot = self.plot + gutils.strip_tags(gutils.before(gutils.after(element, '>'), '</a>')) + '\n\n'
        if self.plot == '':
            # nothing in german found, try original
            self.plot = gutils.before(gutils.after(gutils.trim(self.imdb_page, 'name="description"', '/>'), 'content="'), '"')
            elements = string.split(self.imdb_plot_page, 'class="plotSummary"')
            if len(elements) > 1:
                self.plot = self.plot + '\n\n'
                elements[0] = ''
                for element in elements:
                    if element <> '':
                        self.plot = self.plot + gutils.strip_tags(gutils.before(gutils.after(element, '>'), '</a>')) + '\n\n'

    def get_year(self):
        self.year = gutils.trim(self.page, 'href="/year/', '/')

    def get_runtime(self):
        self.runtime = gutils.regextrim(self.page, 'Runtime:<[^>]+>', ' min')

    def get_genre(self):
        self.genre = gutils.after(gutils.trim(self.page, '>Genres:<', '</div>'), '>')
        self.genre = string.replace(self.genre, '|', ',')

    def get_cast(self):
        self.cast = ''
        self.cast = gutils.trim(self.cast_page, '<table class="cast_list">', '</table>')
        if self.cast == '':
            self.cast = gutils.trim(self.page, '<table class="cast">', '</table>')
        self.cast = string.replace(self.cast, ' ... ', _(' as '))
        self.cast = string.replace(self.cast, '...', _(' as '))
        self.cast = string.replace(self.cast, "\n", '')
        self.cast = string.replace(self.cast, '</tr>', "\n")
        self.cast = self.__before_more(self.cast)
        self.cast = gutils.clean(self.cast)
        self.cast = re.sub('[ \t]+', ' ', self.cast)
        self.cast = re.sub(' \n ', '\n', self.cast)

    def get_classification(self):
        self.classification = gutils.regextrim(gutils.regextrim(self.cert_page, '(>Altersfreigabe:<|>Certification:<)', '</div>'), '(Deutschland:|Germany:)', '<')

    def get_studio(self):
        self.studio = ''
        tmp = gutils.trim(self.comp_page, '>Production Companies</h4>', '</ul>')
        elements = string.split(tmp, '<a href')
        for element in elements[1:]:
            self.studio = self.studio + gutils.trim(element, '>', '<') + ', '
        self.studio = re.sub(', $', '', self.studio)

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = "http://www.imdb.com/title/tt%s" % self.movie_id

    def get_trailer(self):
        self.trailer = "http://www.imdb.com/title/tt%s/trailers" % self.movie_id

    def get_country(self):
        self.country = gutils.after(gutils.regextrim(self.page, '(>Country:<|>Land:<)', '</div>'), '>')
        self.country = self.__before_more(self.country)
        self.country = re.sub('[\n]+', '', self.country)
        self.country = re.sub('[ ]+', ' ', self.country)

    def get_rating(self):
        self.rating = gutils.trim(self.page, 'Users rated this ', '/')
        if self.rating:
            try:
                self.rating = round(float(self.rating), 0)
            except Exception, e:
                self.rating = 0
        else:
            self.rating = 0

    def get_notes(self):
        self.notes = ''
        language = gutils.regextrim(self.page, 'Language:<[^>]+>', '</div>')
        language = gutils.strip_tags(language)
        language = re.sub('[\n]+', '', language)
        language = re.sub('[ ]+', ' ', language)
        language = language.strip()
        color = gutils.regextrim(self.page, 'Color:<[^>]+>', '</div>')
        color = gutils.strip_tags(color)
        color = re.sub('[\n]+', '', color)
        color = re.sub('[ ]+', ' ', color)
        color = color.strip()
        sound = gutils.regextrim(self.page, 'Sound Mix:<[^>]+>', '</div>')

        sound = gutils.strip_tags(sound)
        sound = re.sub('[\n]+', '', sound)
        sound = re.sub('[ ]+', ' ', sound)
        sound = sound.strip()
        tagline = gutils.regextrim(self.tagl_page, '>Taglines', '>See also')
        taglines = re.split('<div[^>]+class="soda[^>]*>', tagline)
        tagline = ''
        if len(taglines)>1:
            for entry in taglines[1:]:
                entry = gutils.clean(gutils.before(entry, '</div>'))
                if entry:
                    tagline = tagline + entry + '\n'





        if len(language)>0:
            self.notes = "%s: %s\n" %(_('Language'), language)
        if len(sound)>0:
            self.notes += "%s: %s\n" %(gutils.strip_tags(_('<b>Audio</b>')), sound)
        if len(color)>0:
            self.notes += "%s: %s\n" %(_('Color'), color)
        if len(tagline)>0:
            self.notes += "%s: %s\n" %('Tagline', tagline)

    def get_screenplay(self):
        self.screenplay = ''
        parts = re.split('<a href=', gutils.trim(self.cast_page, 'Writing Credits', '</table>'))
        if len(parts) > 1:
            for part in parts[1:]:
                screenplay = gutils.trim(part, '>', '<')
                if screenplay == 'WGA':
                    continue
                screenplay = screenplay.replace(' (geschrieben von)', '')
                screenplay = screenplay.replace(' (written by)', '')
                screenplay = screenplay.replace(' (characters)', '')
                screenplay = screenplay.replace(' (original scenario)', '')
                screenplay = screenplay.replace(' und<', '<')
                self.screenplay = self.screenplay + screenplay + ', '
            if len(self.screenplay) > 2:
                self.screenplay = self.screenplay[0:len(self.screenplay) - 2]

    def get_cameraman(self):
        self.cameraman = gutils.trim(self.cast_page, '>Cinematography by', '</table>')
        self.cameraman = string.replace(self.cameraman, '(Kamera)', '')
        self.cameraman = string.replace(self.cameraman, '(nicht im Abspann)', '')
        self.cameraman = string.replace(self.cameraman, '</a>', ', ')
        self.cameraman = gutils.clean(self.cameraman)
        self.cameraman = re.sub(',[ \t]*$', '', self.cameraman)
        self.cameraman = re.sub('[ ]+', ' ', self.cameraman)

    def __before_more(self, data):
        for element in ['>Mehr ansehen<', '>mehr<', '>Full summary<', '>Full synopsis<']:
            tmp = string.find(data, element)
            if tmp>0:
                data = data[:tmp] + '>'
        return data

class SearchPlugin(movie.SearchMovie):
    PATTERN = re.compile(r"""<a href=['"]/title/tt([0-9]+)/[^>]+[>](.*?)</td>""")
    PATTERN_DIRECT = re.compile(r"""value="/title/tt([0-9]+)""")

    def __init__(self):
        self.original_url_search   = 'http://www.imdb.com/find?s=tt&q='
        self.translated_url_search = 'http://www.imdb.com/find?s=tt&q='
        self.encode                = 'utf8'
        self.remove_accents        = False

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
        'Rocky Balboa'         : [ 10, 10 ],
        'Ein glückliches Jahr' : [ 3, 3 ]
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
Talia Shire' + _(' as ') + 'Adrian (Archivmaterial)\n\
Lou DiBella' + _(' as ') + 'als er selbst\n\
Mike Tyson' + _(' as ') + 'als er selbst\n\
Henry G. Sanders' + _(' as ') + 'Martin\n\
Pedro Lovell' + _(' as ') + 'Spider Rico\n\
Ana Gerena' + _(' as ') + 'Isabel\n\
Angela Boyd' + _(' as ') + 'Angie\n\
Louis Giansante' + _(' as ') + 'Bar Thug\n\
Maureen Schilling' + _(' as ') + 'Lucky\'s Bartender\n\
Lahmard J. Tate' + _(' as ') + 'X-Cell (als Lahmard Tate)\n\
Woody Paige' + _(' as ') + 'ESPN Commentator (als Woodrow W. Paige)\n\
Skip Bayless' + _(' as ') + 'ESPN Commentator\n\
Jay Crawford' + _(' as ') + 'ESPN Commentator\n\
Brian Kenny' + _(' as ') + 'ESPN Host\n\
Dana Jacobson' + _(' as ') + 'ESPN Host\n\
Charles Johnson' + _(' as ') + 'ESPN Host (als Chuck Johnson)\n\
James Binns' + _(' as ') + 'Commissioner (als James J. Binns)\n\
Johnnie Hobbs Jr.' + _(' as ') + 'Commissioner\n\
Barney Fitzpatrick' + _(' as ') + 'Commissioner\n\
Jim Lampley' + _(' as ') + 'HBO Commentator\n\
Larry Merchant' + _(' as ') + 'HBO Commentator\n\
Max Kellerman' + _(' as ') + 'HBO Commentator\n\
LeRoy Neiman' + _(' as ') + 'als er selbst\n\
Bert Randolph Sugar' + _(' as ') + 'Ring Magazine Reporter\n\
Bernard Fernández' + _(' as ') + 'Boxing Association of America Writer (als Bernard Fernandez)\n\
Gunnar Peterson' + _(' as ') + 'Weightlifting Trainer\n\
Yahya' + _(' as ') + 'Dixon\'s Opponent\n\
Marc Ratner' + _(' as ') + 'Weigh-In Official\n\
Anthony Lato Jr.' + _(' as ') + 'Rocky\'s Inspector\n\
Jack Lazzarado' + _(' as ') + 'Dixon\'s Inspector\n\
Michael Buffer' + _(' as ') + 'Ring Announcer\n\
Joe Cortez' + _(' as ') + 'Schiedsrichter\n\
Carter Mitchell' + _(' as ') + 'Shamrock Foreman\n\
Vinod Kumar' + _(' as ') + 'Ravi\n\
Fran Pultro' + _(' as ') + 'Father at Restaurant\n\
Frank Stallone' + _(' as ') + 'Dinner Patron (als Frank Stallone Jr.)\n\
Jody Giambelluca' + _(' as ') + 'Dinner Patron\n\
Tobias Segal' + _(' as ') + 'Robert\'s Friend\n\
Tim Carr' + _(' as ') + 'Robert\'s Friend\n\
Matt Frack' + _(' as ') + 'Robert\'s Friend #3\n\
Paul Dion Monte' + _(' as ') + 'Robert\'s Friend\n\
Kevin King Templeton' + _(' as ') + 'Robert\'s Friend (als Kevin King-Templeton)\n\
Robert Michael Kelly' + _(' as ') + 'Mr. Tomilson\n\
Rick Buchborn' + _(' as ') + 'Rocky Fan\n\
Nick Baker' + _(' as ') + 'Irish Pub Bartender\n\
Don Sherman' + _(' as ') + 'Andy\n\
Stu Nahan' + _(' as ') + 'Computer Fight Commentator (Sprechrolle)\n\
Gary Compton' + _(' as ') + 'Sicherheitsbediensteter übrige Besetzung in alphabetischer Reihenfolge:\n\
Vale Anoai' + _(' as ') + 'Shopper in Italian Market\n\
Sikander Malik' + _(' as ') + 'Boxer\n\
Michael Ahl' + _(' as ') + 'Restaurant Patron (nicht im Abspann)\n\
Andrew Aninsman' + _(' as ') + 'Promoter (nicht im Abspann)\n\
Ben Bachelder' + _(' as ') + 'The Arm (nicht im Abspann)\n\
Lacy Bevis' + _(' as ') + 'Boxing Spectator (nicht im Abspann)\n\
Tim Brooks' + _(' as ') + 'Boxing Spectator (nicht im Abspann)\n\
D.T. Carney' + _(' as ') + 'High Roller (nicht im Abspann)\n\
Ricky Cavazos' + _(' as ') + 'Boxing Spectator (nicht im Abspann)\n\
Rennie Cowan' + _(' as ') + 'Boxing Spectator (nicht im Abspann)\n\
Kevin Deon' + _(' as ') + 'Jeno (nicht im Abspann)\n\
Deon Derrico' + _(' as ') + 'High Roller at Limo (nicht im Abspann)\n\
Jacob \'Stitch\' Duran' + _(' as ') + 'Dixon\'s Trainer (nicht im Abspann)\n\
Simon P. Edwards' + _(' as ') + 'Crowd Member (nicht im Abspann)\n\
Ruben Fischman' + _(' as ') + 'High-Roller in Las Vegas (nicht im Abspann)\n\
David Gere' + _(' as ') + 'Patron at Adrian\'s (nicht im Abspann)\n\
Noah Jacobs' + _(' as ') + 'Boxing Fan (nicht im Abspann)\n\
Mark J. Kilbane' + _(' as ') + 'Businessman (nicht im Abspann)\n\
Zach Klinefelter' + _(' as ') + 'Boxing Spectator (nicht im Abspann)\n\
David Kneeream' + _(' as ') + 'Adrian\'s Patron (nicht im Abspann)\n\
Dolph Lundgren' + _(' as ') + 'Captain Ivan Drago (Archivmaterial) (nicht im Abspann)\n\
Dean Mauro' + _(' as ') + 'Sports Journalist (nicht im Abspann) (unbestätigt)\n\
Burgess Meredith' + _(' as ') + 'Mickey Goldmill (Archivmaterial) (nicht im Abspann)\n\
Dan Montero' + _(' as ') + 'Boxing Spectator (nicht im Abspann)\n\
Babs Moran' + _(' as ') + 'Obnoxious Fan (nicht im Abspann)\n\
Keith Moyer' + _(' as ') + 'Bargast (nicht im Abspann)\n\
Mr. T' + _(' as ') + 'Clubber Lang (Archivmaterial) (nicht im Abspann)\n\
Carol Anne Mueller' + _(' as ') + 'Restaurant Patron (nicht im Abspann)\n\
Jacqueline Olivia' + _(' as ') + 'Mädchen (nicht im Abspann)\n\
Brian H. Scott' + _(' as ') + 'Ringside Cop #1 (nicht im Abspann)\n\
Keyon Smith' + _(' as ') + 'Boxing Spectator (nicht im Abspann)\n\
Frank Traynor' + _(' as ') + 'Rechtsanwalt (nicht im Abspann)\n\
Ryan Tygh' + _(' as ') + 'Ring Photographer (nicht im Abspann)\n\
Kimberly Villanova' + _(' as ') + 'Businesswoman (nicht im Abspann)',
            'country'           : 'USA',
            'genre'             : 'Drama | Sport',
            'classification'    : '12',
            'studio'            : 'Metro-Goldwyn-Mayer (MGM) (presents) (copyright owner), Columbia Pictures (presents) (copyright owner), Revolution Studios (presents) (copyright owner), Rogue Marble',
            'o_site'            : False,
            'site'              : 'http://www.imdb.de/title/tt0479143',
            'trailer'           : 'http://www.imdb.com/title/tt0479143/trailers',
            'year'              : 2006,
            'notes'             : _('Language') + ': Englisch | Spanisch\n'\
+ _('Audio') + ': DTS | Dolby Digital | SDDS\n'\
+ _('Color') + ': Farbe',
            'runtime'           : 102,
            'image'             : True,
            'rating'            : 7,
            'screenplay'        : 'Sylvester Stallone, Sylvester Stallone',
            'cameraman'         : 'Clark Mathis'
        },
        '0069815' : {
            'title'             : 'Ein glückliches Jahr',
            'o_title'           : 'La bonne année',
            'director'          : 'Claude Lelouch',
            'plot'              : True,
            'cast'              : 'Lino Ventura' + _(' as ') + 'Simon\n\
Françoise Fabian' + _(' as ') + 'Françoise\n\
Charles Gérard' + _(' as ') + 'Charlot\n\
André Falcon' + _(' as ') + 'Le bijoutier\n\
Mireille Mathieu' + _(' as ') + 'als sie selbst / Elle-même\n\
Lilo' + _(' as ') + 'Madame Félix\n\
Claude Mann' + _(' as ') + 'L\'intellectuel\n\
Frédéric de Pasquale' + _(' as ') + 'L\'amant parisien\n\
Gérard Sire' + _(' as ') + 'Le directeur de la prison\n\
Silvano Tranquilli' + _(' as ') + 'L\'amant italien\n\
André Barello\n\
Michel Bertay\n\
Norman de la Chesnaye\n\
Pierre Edeline\n\
Pierre Pontiche\n\
Michou' + _(' as ') + 'als er selbst\n\
Bettina Rheims' + _(' as ') + 'La jeune vendeuse\n\
Joseph Rythmann\n\
Georges Staquet\n\
Jacques Villedieu\n\
Harry Walter übrige Besetzung in alphabetischer Reihenfolge:\n\
Anouk Aimée' + _(' as ') + 'Une femme (Archivmaterial) (nicht im Abspann)\n\
Élie Chouraqui' + _(' as ') + ' (nicht im Abspann)\n\
Rémy Julienne' + _(' as ') + 'Chauffeur de taxi (nicht im Abspann)\n\
Jean-Louis Trintignant' + _(' as ') + 'Un homme (Archivmaterial) (nicht im Abspann)',
            'country'            : 'Frankreich | Italien',
            'genre'              : 'Komödie',
            'classification'     : '12 (f)',
            'studio'             : 'Les Films 13, Rizzoli Film',
            'o_site'             : False,
            'site'               : 'http://www.imdb.de/title/tt0069815',
            'trailer'            : 'http://www.imdb.com/title/tt0069815/trailers',
            'year'               : 1973,
            'notes'              : _('Language') + ': Französisch\n'\
+ _('Audio') + ': Mono\n'\
+ _('Color') + ': Farbe (Eastmancolor)',
            'runtime'            : 90,
            'image'              : True,
            'rating'             : 7,
            'screenplay'         : 'Claude Lelouch, Pierre Uytterhoeven, Claude Lelouch',
            'cameraman'          : 'Claude Lelouch'
        },
    }
