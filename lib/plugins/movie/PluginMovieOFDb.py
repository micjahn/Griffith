# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieOFDb.py 1641 2013-01-30 12:24:47Z mikej06 $'

# Written by Christian Sagmueller <christian@sagmueller.net>
# based on PluginMovieIMDB.py, Copyright (c) 2005 Vasco Nunes
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import gutils
import movie,string,re

plugin_name         = "OFDb"
plugin_description  = "Online-Filmdatenbank"
plugin_url          = "www.ofdb.de"
plugin_language     = _("German")
plugin_author       = "Christian Sagmueller, Jessica Katharina Parth"
plugin_author_email = "Jessica.K.P@women-at-work.org"
plugin_version      = "0.13"

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode   = 'utf-8'
        self.movie_id = id
        self.url      = "https://www.ofdb.de/%s" % str(self.movie_id)

    def initialize(self):
        # OFDb didn't provide the runtime, studio and classification but it provide a link to the german imdb entry
        # lets use the imdb page, why not
        imdb_nr = gutils.trim(self.page, 'http://german.imdb.com/Title?', '"')
        if imdb_nr != '':
            self.imdb_page = self.open_page(url='http://www.imdb.com/title/tt' + imdb_nr)
            self.cert_page = self.open_page(url='http://www.imdb.com/title/tt' + imdb_nr + '/parentalguide')
            self.comp_page = self.open_page(url='http://www.imdb.com/title/tt' + imdb_nr + '/companycredits')
        else:
            imdb_nr = gutils.trim(self.page, 'http://www.imdb.com/Title?', '"')
            if imdb_nr != '':
                self.imdb_page = self.open_page(url='http://www.imdb.com/title/tt' + imdb_nr)
                self.cert_page = self.open_page(url='http://www.imdb.com/title/tt' + imdb_nr + '/parentalguide')
                self.comp_page = self.open_page(url='http://www.imdb.com/title/tt' + imdb_nr + '/companycredits')
            else:
                self.imdb_page = ''
                self.cert_page = ''
                self.comp_page = ''
        self.comp_page = gutils.convert_entities(self.comp_page)
        self.imdb_page = gutils.convert_entities(self.imdb_page)
        self.cert_page = gutils.convert_entities(self.cert_page)
        movie_id_elements = string.split(self.movie_id, ',')
        movie_id_elements[0] = string.replace(movie_id_elements[0], "film/", "")
        self.cast_page = self.open_page(url="https://www.ofdb.de/view.php?page=film_detail&fid=%s" % str(movie_id_elements[0]) )

    def get_image(self):
        self.image_url = "https://www.ofdb.de/images/film/" + gutils.trim(self.page, 'img src="images/film/', '"')

    def get_o_title(self):
        self.o_title = gutils.clean(gutils.trim(self.page, 'Originaltitel:', '</tr>'))
        if self.o_title == '':
            self.o_title = string.replace(self.o_title, '&nbsp;', '' )

    def get_title(self):
        self.title = gutils.trim(self.page,'size="3"><b>','<')

    def get_director(self):
        self.director = gutils.trim(self.page,"Regie:","</a><br>")

    def get_plot(self):
        self.plot = ''
        storyid = gutils.regextrim(self.page, '<a href="plot/', '(">|[&])')
        if not storyid is None:
            story_page = self.open_page(url="https://www.ofdb.de/plot/%s" % (storyid.encode('utf8')))
            if story_page:
                self.plot = gutils.trim(story_page, "</b><br><br>","</")

    def get_year(self):
        self.year = gutils.trim(self.page,"Erscheinungsjahr:","</a>")
        self.year = gutils.strip_tags(self.year)

    def get_runtime(self):
        # from imdb
        self.runtime = gutils.regextrim(self.imdb_page, 'Runtime:<[^>]+>', ' min')

    def get_genre(self):
        self.genre = gutils.trim(self.page,"Genre(s):","</table>")
        self.genre = string.replace(self.genre, "<br>", ", ")
        self.genre = gutils.strip_tags(self.genre)
        self.genre = string.replace(self.genre, "/", ", ")
        self.genre = gutils.clean(self.genre)
        self.genre = self.genre[0:-1]

    def get_cast(self):
        self.cast = ''
        self.cast = gutils.trim(self.cast_page, 'Darsteller</i>', '</table>')
        self.cast = re.sub('(\n|\t|&nbsp;)', '', self.cast)
        self.cast = string.replace(self.cast, '\t', '')
        self.cast = string.replace(self.cast, 'class="Daten">', '>\n')
        self.cast = string.strip(gutils.strip_tags(self.cast))
        self.cast = string.replace(self.cast, '... ', _(' as '))
        self.cast = gutils.clean(self.cast)

    def get_classification(self):
        # from imdb
        self.classification = gutils.regextrim(gutils.regextrim(self.cert_page, '(>Altersfreigabe:<|>Certification:<)', '</div>'), '(Deutschland:|Germany:)', '<')

    def get_studio(self):
        # from imdb
        self.studio = ''
        tmp = gutils.trim(self.comp_page, '>Production Companies</h4>', '</ul>')
        elements = string.split(tmp, '<a href')
        for element in elements[1:]:
            self.studio = self.studio + gutils.trim(element, '>', '<') + ', '
        self.studio = re.sub(', $', '', self.studio)

    def get_o_site(self):
        self.o_site = gutils.trim(gutils.regextrim(self.imdb_page, 'Official Sites:', '(<span|</span>)'), 'href="', '"')
        if self.o_site:
            self.o_site = 'http://www.imdb.com' + self.o_site

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ""

    def get_country(self):
        self.country = gutils.trim(self.page,"Herstellungsland:","</a>")

    def get_rating(self):
        self.rating = gutils.after(gutils.trim(self.page,">Note: <","</span>"), '>')
        if self.rating == '':
            self.rating = "0"
        if self.rating:
            try:
                self.rating = round(float(self.rating), 0)
            except Exception, e:
                self.rating = 0
        else:
            self.rating = 0

    def get_screenplay(self):
        self.screenplay = ''
        tmp = gutils.trim(self.cast_page, '>Drehbuchautor(in)<', '</table>')
        parts = re.split('<a href=', tmp)
        if len(parts) > 1:
            for part in parts[1:]:
                screenplay = gutils.clean(gutils.trim(part, '>', '</a>'))
                if screenplay:
                    self.screenplay = self.screenplay + screenplay + ', '
            if len(self.screenplay) > 2:
                self.screenplay = self.screenplay[0:len(self.screenplay) - 2]


class SearchPlugin(movie.SearchMovie):
    def __init__(self):
        self.original_url_search   = "https://www.ofdb.de/view.php?page=suchergebnis&Kat=OTitel&SText="
        self.translated_url_search = "https://www.ofdb.de/view.php?page=suchergebnis&Kat=DTitel&SText="
        self.encode                = 'utf-8'
        self.remove_accents        = False

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        print self.url
        self.page = gutils.trim(self.page,"</b><br><br>", "<br><br></font>");
        self.page = string.replace( self.page, "'", '"' )
        self.page = string.replace( self.page, '<font size="1">', '' )
        self.page = string.replace( self.page, '</font>', '' )
        return self.page

    def get_searches(self):
        elements = string.split(self.page,"<br>")
        if (elements[0]<>''):
            for element in elements:
                print element
                elementid = gutils.trim(element,'<a href="film','"')
                if not elementid is None and not elementid == '':
                    elementname = gutils.trim(element, '>', '<')
                    self.ids.append("film"+elementid)
                    p1 = string.find(elementname, '>')
                    if p1 == -1:
                        self.titles.append(elementname)
                    else:
                        self.titles.append(elementname[p1+1:])

#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa' : [ 1, 1 ],
        'Arahan'       : [ 3, 3 ],
        'glückliches'  : [ 4, 2 ]
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
        'film/103013,Rocky%20Balboa' : {
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
Lou DiBella' + _(' as ') + 'Himself\n\
Mike Tyson' + _(' as ') + 'Himself\n\
Henry G. Sanders' + _(' as ') + 'Martin\n\
Pedro Lovell' + _(' as ') + 'Spider Rico\n\
Ana Gerena' + _(' as ') + 'Isabel\n\
Angela Boyd' + _(' as ') + 'Angie\n\
Louis Giansante\n\
Maureen Schilling\n\
Lahmard J. Tate\n\
Woody Paige\n\
Skip Bayless\n\
Jay Crawford\n\
Brian Kenny\n\
Dana Jacobson\n\
Charles Johnson\n\
James Binns\n\
Johnnie Hobbs Jr.\n\
Barney Fitzpatrick\n\
Jim Lampley\n\
Larry Merchant\n\
Max Kellerman\n\
LeRoy Neiman\n\
Bert Randolph Sugar\n\
Bernard Fernández\n\
Gunnar Peterson\n\
Yahya\n\
Marc Ratner\n\
Anthony Lato Jr.\n\
Jack Lazzarado\n\
Michael Buffer' + _(' as ') + 'Ring Announcer\n\
Joe Cortez' + _(' as ') + 'Referee\n\
Carter Mitchell\n\
Vinod Kumar\n\
Fran Pultro\n\
Frank Stallone als Frank Stallone Jr.' + _(' as ') + 'Dinner Patron \n\
Jody Giambelluca\n\
Tobias Segal' + _(' as ') + 'Robert\'s Friend\n\
Tim Carr' + _(' as ') + 'Robert\'s Friend \n\
Matt Frack\n\
Paul Dion Monte' + _(' as ') + 'Robert\'s Friend\n\
Kevin King Templeton\n\
Robert Michael Kelly\n\
Rick Buchborn\n\
Nick Baker\n\
Don Sherman' + _(' as ') + 'Andy\n\
Gary Compton\n\
Vale Anoai\n\
Sikander Malik\n\
Michael Ahl\n\
Andrew Aninsman\n\
Ben Bachelder\n\
Lacy Bevis\n\
Tim Brooks\n\
D.T. Carney\n\
Ricky Cavazos' + _(' as ') + 'Boxing Spectator (uncredited)\n\
Rennie Cowan\n\
Deon Derrico\n\
Jacob \'Stitch\' Duran\n\
Simon P. Edwards\n\
Ruben Fischman' + _(' as ') + 'High-Roller in Las Vegas (uncredited)\n\
David Gere\n\
Noah Jacobs\n\
Mark J. Kilbane\n\
Zach Klinefelter\n\
David Kneeream\n\
Dan Montero\n\
Keith Moyer' + _(' as ') + 'Bar Patron (uncredited)\n\
Carol Anne Mueller\n\
Jacqueline Olivia\n\
Brian H. Scott\n\
Keyon Smith\n\
Frank Traynor\n\
Ryan Tygh\n\
Kimberly Villanova',
            'country'             : 'USA',
            'genre'               : 'Action, Drama, Sportfilm',
            'classification'      : False,
            'studio'              : 'Metro-Goldwyn-Mayer (MGM), Columbia Pictures, Revolution Studios',
            'o_site'              : False,
            'site'                : 'http://www.ofdb.de/film/103013,Rocky%20Balboa',
            'trailer'             : False,
            'year'                : 2006,
            'notes'               : False,
            'runtime'             : 102,
            'image'               : True,
            'rating'              : 8
        },
        'film/22489,Ein-Gl%C3%BCckliches-Jahr' : {
            'title'               : 'Glückliches Jahr, Ein',
            'o_title'             : 'Bonne année, La',
            'director'            : 'Claude Lelouch',
            'plot'                : False,
            'cast'                : 'Lino Ventura' + _(' as ') + 'Simon\n\
Françoise Fabian' + _(' as ') + 'Françoise\n\
Charles Gérard' + _(' as ') + 'Charlot\n\
André Falcon' + _(' as ') + 'Le bijoutier\n\
Mireille Mathieu\n\
Lilo\n\
Claude Mann\n\
Frédéric de Pasquale\n\
Gérard Sire\n\
Silvano Tranquilli' + _(' as ') + 'L\'amant italien\n\
André Barello\n\
Michel Bertay\n\
Norman de la Chesnaye\n\
Pierre Edeline\n\
Pierre Pontiche\n\
Michou\n\
Bettina Rheims\n\
Joseph Rythmann\n\
Georges Staquet\n\
Jacques Villedieu\n\
Harry Walter\n\
Elie Chouraqui',
            'country'             : 'Frankreich',
            'genre'               : 'Komödie, Krimi',
            'classification'      : False,
            'studio'              : 'Les Films 13, Rizzoli Film',
            'o_site'              : False,
            'site'                : 'http://www.ofdb.de/film/22489,Ein-Gl%C3%BCckliches-Jahr',
            'trailer'             : False,
            'year'                : 1973,
            'notes'               : False,
            'runtime'             : 115,
            'image'               : True,
            'rating'              : 6
        },
        'film/54088,Arahan' : {
            'title'               : 'Arahan',
            'o_title'             : 'Arahan jangpung daejakjeon',
            'director'            : 'Ryoo Seung-wan',
            'plot'                : True,
            'cast'                : 'Ryoo Seung-beom\n\
Yoon Soy' + _(' as ') + 'Wi-jin\n\
Ahn Seong-gi' + _(' as ') + 'Ja-woon\n\
Jeong Doo-hong' + _(' as ') + 'Heuk-Woon\n\
Yoon Joo-sang' + _(' as ') + 'Moo-woon \n\
Kim Ji-yeong\n\
Baek Chan-gi\n\
Kim Jae-man\n\
Lee Dae-yeon\n\
Kim Dong-ju\n\
Kim Su-hyeon\n\
Geum Dong-hyeon\n\
Lee Jae-goo\n\
Ahn Kil-kang\n\
Bong Tae-gyu' + _(' as ') + 'Cameo\n\
Im Ha-ryong' + _(' as ') + 'Cameo\n\
Yoon Do-hyeon\n\
Lee Choon-yeon' + _(' as ') + 'Cameo\n\
Kim Yeong-in\n\
Park Yoon-bae\n\
Lee Won\n\
Kim Kyeong-ae\n\
Yoo Soon-cheol\n\
Hwang Hyo-eun\n\
Lee Jae-ho\n\
Yang Ik-joon\n\
Kwon Beom-taek\n\
Min Hye-ryeong\n\
Oh Soon-tae\n\
Lee Oi-soo',
            'country'             : 'Südkorea',
            'genre'               : 'Action, Fantasy, Komödie',
            'classification'      : False,
            'studio'              : 'Fun and Happiness, Good Movie Company',
            'o_site'              : 'http://www.arahan.co.kr/',
            'site'                : 'http://www.ofdb.de/film/54088,Arahan',
            'trailer'             : False,
            'year'                : 2004,
            'notes'               : False,
            'runtime'             : 114,
            'image'               : True,
            'rating'              : 7
        }
    }
