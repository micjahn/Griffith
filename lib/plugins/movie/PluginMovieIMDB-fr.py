# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2012 CinéphOli
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

plugin_name         = 'IMDb-fr'
plugin_description  = 'Internet Movie Database en français'
plugin_url          = 'www.imdb.fr'
plugin_language     = _('French')
plugin_author       = 'CinéphOli'
plugin_author_email = 'cinepholi@gmail.com'
plugin_version      = '0.1' # based on PluginMovieIMDB.py

class Plugin(movie.Movie):
    def __init__(self, id): # OK v0.1
        self.encode   = 'iso8859-1'
        self.movie_id = id
        self.url      = "http://www.imdb.fr/title/tt%s" % self.movie_id

    def initialize(self): # OK v0.1
        self.cast_page = self.open_page(url=self.url + '/fullcredits')
        self.plot_page = self.open_page(url=self.url + '/plotsummary')
        self.comp_page = self.open_page(url=self.url + '/companycredits')
        self.tech_page = self.open_page(url=self.url + '/technical')
        # Taglines not available on IMDb.fr.
        # self.tagl_page = self.open_page(url=self.url + '/taglines')

    def get_image(self): # OK v0.1
        self.image_url = gutils.trim(gutils.trim(self.page, 'id="primary-poster"', '</a>'), 'src="', '"')

    def get_o_title(self): # OK v0.1
        #~ self.o_title = gutils.trim(self.page, 'class="title-extra">', '<')
        self.o_title = gutils.trim(gutils.trim(self.page, '<h5>Alias:</h5><div class="info-content">', '</div>'), '"', '"')
        if not self.o_title: # same conditions as title
            self.o_title = gutils.regextrim(self.page, '<h1>', '([ ]|[&][#][0-9]+[;])<span')
        if not self.o_title:
            self.o_title = re.sub(' [(].*', '', gutils.trim(self.page, '<title>', '</title>'))

    def get_title(self): # OK v0.1
        self.title = gutils.regextrim(self.page, '<h1>', '([ ]|[&][#][0-9]+[;])<span')
        if not self.title:
            self.title = re.sub(' [(].*', '', gutils.trim(self.page, '<title>', '</title>'))

    def get_director(self): # OK v0.1
        self.director = ''
        parts = re.split('<a href=', gutils.trim(self.cast_page, '>R&#xE9;alis&#xE9; par<', '</table>'))
        if len(parts) > 1:
            for part in parts[1:]:
                director = gutils.trim(part, '>', '<')
                self.director = self.director + director + ', '
            self.director = self.director[:-2]

    def get_plot(self): # OK v0.1
        self.plot = ''
        self.plot = gutils.trim(self.plot_page, '<div id="swiki.2.1">', '</div>')

    def get_year(self): # OK v0.1
        self.year = ''
        self.year = gutils.regextrim(self.page, '<div id="tn15title">[^(]*[(]', '[)].*<span class="pro-link">')

    def get_runtime(self): # OK v0.1
        self.runtime = ''
        self.runtime = gutils.trim(self.page, '<h5>Dur&#xE9;e:</h5><div class="info-content">', ' min')

    def get_genre(self): # OK v0.1
        self.genre = ''
        self.genre = gutils.trim(self.page, '<h5>Genre:</h5>', '<div class="info">')
        self.genre = gutils.trim(self.genre, '<div class="info-content">', '</div')
        self.genre = self.genre.replace(" |", ",")

    def get_cast(self): # OK v0.1
        self.cast = ''
        self.cast = gutils.trim(self.cast_page, '<table class="cast">', '</table>')
        if self.cast == '': # else take table from main page
            self.cast = gutils.trim(self.page, '<table class="cast">', '</table>')
        self.cast = string.replace(self.cast, ' ... ', _(' as '))
        self.cast = string.replace(self.cast, '...', _(' as '))
        self.cast = string.replace(self.cast, '</tr><tr>', "\n")
        self.cast = string.replace(self.cast, 'reste de la distribution par ordre alphab&#xE9;tique:', '')
        self.cast = re.sub('</tr>[ \t]*<tr[ \t]*class="even">', "\n", self.cast)
        self.cast = re.sub('</tr>[ \t]*<tr[ \t]*class="odd">', "\n", self.cast)
        # remove (comme xyz) and (non crédité)
        self.cast = re.sub('[(](comme [^)]*|non cr&#xE9;dit&#xE9;)[)]', '', self.cast)
        self.cast = self.__before_more(self.cast)

    def get_classification(self): # OK v0.1
        self.classification = ''
        # Too many classifications from too many countries to chose from. Discarded.
        #~ self.classification = gutils.trim(self.page, '(<a href="/mpaa">MPAA</a>)', '</div>')
        #~ self.classification = gutils.trim(self.classification, 'Rated ', ' ')

    def get_studio(self): # OK v0.1
        self.studio = ''
        tmp = gutils.regextrim(self.comp_page, 'Soci&#xE9;t&#xE9;s de Production<[^>]+', '</ul>')
        tmp = string.split(tmp, 'href="')
        for entry in tmp:
            entry = gutils.trim(entry, '>', '<')
            if entry:
                self.studio = self.studio + entry + ', '
        if self.studio:
            self.studio = self.studio[:-2]

    def get_o_site(self): # OK v0.1
        self.o_site = ''
        self.o_site = "http://www.imdb.fr/title/tt%s/officialsites" % self.movie_id 

    def get_site(self): # OK v0.1
        self.site = ''
        self.site = "http://www.imdb.fr/title/tt%s" % self.movie_id

    def get_trailer(self): # OK v0.1
        self.trailer = ''
        # No trailers on imdb.fr, get them from imdb.com (uses same ref)
        self.trailer = "http://www.imdb.com/title/tt%s/trailers" % self.movie_id

    def get_country(self): # OK v0.1
        self.country = ''
        self.country = '<' + gutils.trim(self.page, 'Pays:<', '</div>')
        self.country = self.country.replace(" |", ",")

    def get_rating(self): # OK v0.1
        self.rating = 0
        result = re.search('<b>(10|[0-9](,[0-9])?)/10</b>', self.page) # eg. <b>7,5/10</b>
        if result:
            result = re.sub('(<b>|</b>|/10)', '', result.group(0))
            result = result.replace(',', '.') # decimal dot
            if result:
                try:
                    self.rating = round(float(result), 0)
                except Exception, e:
                    self.rating = 0
        else:
            self.rating = 0

    def get_notes(self): # OK v0.1
        self.notes = ''
        language = gutils.regextrim(self.page, 'Langue:<[^>]+>', '</div>')
        language = gutils.strip_tags(language)
        language = re.sub('[\n]+', '', language)
        language = re.sub('[ ]+', ' ', language)
        language = language.strip()
        color = gutils.regextrim(self.page, 'Couleur:<[^>]+>', '</div>')
        color = gutils.strip_tags(color)
        color = re.sub('[\n]+', '', color)
        color = re.sub('[ ]+', ' ', color)
        color = color.strip()
        sound = gutils.regextrim(self.page, 'Son:<[^>]+>', '</div>')
        sound = gutils.strip_tags(sound)
        sound = re.sub('[\n]+', '', sound)
        sound = re.sub('[ ]+', ' ', sound)
        sound = sound.strip()
        if len(language)>0:
            self.notes = "%s: %s\n" %(_('Language'), language)
        if len(sound)>0:
            self.notes += "%s: %s\n" %(_('Audio'), sound)
        if len(color)>0:
            self.notes += "%s: %s\n" %(_('Color'), color)

    def get_screenplay(self): # OK V0.1
        self.screenplay = ''
        parts = re.split('<a href=', gutils.trim(self.cast_page, '>Sc&#xE9;naristes<', '</table>'))
        if len(parts) > 1:
            for part in parts[1:]:
                screenplay = gutils.trim(part, '>', '<')
                if screenplay == 'WGA':
                    continue
                screenplay = screenplay.replace(' (written by)', '')
                screenplay = screenplay.replace(' and<', '<')
                self.screenplay = self.screenplay + screenplay + ', '
            if len(self.screenplay) > 2:
                self.screenplay = self.screenplay[:-2]

    def get_cameraman(self): # OK v0.1
        self.cameraman = ''
        tmp = gutils.regextrim(self.cast_page, 'Image<[^>]+', '</table>')
        tmp = string.split(tmp, 'href="')
        for entry in tmp:
            entry = gutils.trim(entry, '>', '<')
            if entry:
                self.cameraman = self.cameraman + entry + ', '
        if self.cameraman:
            self.cameraman = self.cameraman[:-2]

    def __before_more(self, data):
        for element in ['>See more<', '>more<', '>Full summary<', '>Full synopsis<']:
            tmp = string.find(data, element)
            if tmp>0:
                data = data[:tmp] + '>'
        return data

class SearchPlugin(movie.SearchMovie):
    PATTERN = re.compile(r"""<A HREF=['"]/title/tt([0-9]+)/["']>(.*?)</LI>""")
    PATTERN2 = re.compile(r"""<a href=['"]/title/tt([0-9]+)/["'](.*?)</tr>""")

    def __init__(self):
        # http://www.imdb.com/List?words=
        # finds every title sorted alphabetically, first results are with a quote at
        # the beginning (episodes from tv series), no popular results at first
        # http://www.imdb.com/find?more=tt&q=
        # finds a whole bunch of results. if you look for "Rocky" you will get 903 results.
        # http://www.imdb.com/find?s=tt;q=
        # seems to give the best results. 88 results for "Rocky", popular titles first.
        self.original_url_search   = 'http://www.imdb.fr/find?s=tt&q='
        self.translated_url_search = 'http://www.imdb.fr/find?s=tt&q='
        self.encode                = 'iso8859-1'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        tmp_page = gutils.trim(self.page, 'Titres Populaires', '</table>')
        if not tmp_page:
            has_results = re.search('[(]Affichant [1-9][0-9]* R&#xE9;sultats[)]', self.page)
            if not has_results:
                # nothing or one result found, try another url which looks deeper in the imdb database
                # example: Adventures of Falcon -> one result, jumps directly to the movie page
                # which isn't supported by this plugin
                self.url = 'http://www.imdb.fr/find?more=tt&q='
                if not self.open_search(parent_window):
                    return None
            self.page = gutils.trim(self.page, '(Affichant', '>Suggestions pour am&#xE9;liorer')
        else:
            self.page = tmp_page
        self.page = self.page.decode('iso-8859-1')
        # correction of all &#xxx entities
        self.page = gutils.convert_entities(self.page)
        return self.page

    def get_searches(self):
        elements = re.split('<LI>', self.page)
        if len(elements) < 2:
            elements = string.split(self.page, '<tr>')
            if len(elements):
                for element in elements[1:]:
                    match = self.PATTERN2.findall(element)
                    if len(match):
                        tmp = re.sub('^[0-9]+[.]', '', gutils.clean(gutils.after(match[0][1], '>')))
                        self.ids.append(match[0][0])
                        self.titles.append(tmp)
        else:
            for element in elements[1:]:
                match = self.PATTERN.findall(element)
                if len(match):
                    tmp = gutils.clean(match[0][1])
                    self.ids.append(match[0][0])
                    self.titles.append(tmp)
#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa'         : [ 25, 25 ],
        'Ein glückliches Jahr' : [ 47, 47 ]
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
        '0138097' : {
            'title'             : 'Shakespeare in Love',
            'o_title'           : 'Shakespeare in Love',
            'director'          : 'John Madden',
            'plot'              : True,
            'cast'              : 'Geoffrey Rush' + _(' as ') + 'Philip Henslowe\n\
Tom Wilkinson' + _(' as ') + 'Hugh Fennyman\n\
Steven O\'Donnell' + _(' as ') + 'Lambert\n\
Tim McMullan' + _(' as ') + 'Frees (as Tim McMullen)\n\
Joseph Fiennes' + _(' as ') + 'Will Shakespeare\n\
Steven Beard' + _(' as ') + 'Makepeace - the Preacher\n\
Antony Sher' + _(' as ') + 'Dr. Moth\n\
Patrick Barlow' + _(' as ') + 'Will Kempe\n\
Martin Clunes' + _(' as ') + 'Richard Burbage\n\
Sandra Reinton' + _(' as ') + 'Rosaline\n\
Simon Callow' + _(' as ') + 'Tilney - Master of the Revels\n\
Judi Dench' + _(' as ') + 'Queen Elizabeth\n\
Bridget McConnell' + _(' as ') + 'Lady in Waiting (as Bridget McConnel)\n\
Georgie Glen' + _(' as ') + 'Lady in Waiting\n\
Nicholas Boulton' + _(' as ') + 'Henry Condell\n\
Gwyneth Paltrow' + _(' as ') + 'Viola De Lesseps\n\
Imelda Staunton' + _(' as ') + 'Nurse\n\
Colin Firth' + _(' as ') + 'Lord Wessex\n\
Desmond McNamara' + _(' as ') + 'Crier\n\
Barnaby Kay' + _(' as ') + 'Nol\n\
Jim Carter' + _(' as ') + 'Ralph Bashford\n\
Paul Bigley' + _(' as ') + 'Peter - the Stage Manager\n\
Jason Round' + _(' as ') + 'Actor in Tavern\n\
Rupert Farley' + _(' as ') + 'Barman\n\
Adam Barker' + _(' as ') + 'First Auditionee\n\
Joe Roberts' + _(' as ') + 'John Webster\n\
Harry Gostelow' + _(' as ') + 'Second Auditionee\n\
Alan Cody' + _(' as ') + 'Third Auditionee\n\
Mark Williams' + _(' as ') + 'Wabash\n\
David Curtiz' + _(' as ') + 'John Hemmings\n\
Gregor Truter' + _(' as ') + 'James Hemmings\n\
Simon Day' + _(' as ') + 'First Boatman\n\
Jill Baker' + _(' as ') + 'Lady De Lesseps\n\
Amber Glossop' + _(' as ') + 'Scullery Maid\n\
Robin Davies' + _(' as ') + 'Master Plum\n\
Hywel Simons' + _(' as ') + 'Servant\n\
Nicholas Le Prevost' + _(' as ') + 'Sir Robert De Lesseps\n\
Ben Affleck' + _(' as ') + 'Ned Alleyn\n\
Timothy Kightley' + _(' as ') + 'Edward Pope\n\
Mark Saban' + _(' as ') + 'Augustine Philips\n\
Bob Barrett' + _(' as ') + 'George Bryan\n\
Roger Morlidge' + _(' as ') + 'James Armitage\n\
Daniel Brocklebank' + _(' as ') + 'Sam Gosse\n\
Roger Frost' + _(' as ') + 'Second Boatman\n\
Rebecca Charles' + _(' as ') + 'Chambermaid\n\
Richard Gold' + _(' as ') + 'Lord in Waiting\n\
Rachel Clarke' + _(' as ') + 'First Whore\n\
Lucy Speed' + _(' as ') + 'Second Whore\n\
Patricia Potter' + _(' as ') + 'Third Whore\n\
John Ramm' + _(' as ') + 'Makepeace\'s Neighbor\n\
Martin Neely' + _(' as ') + 'Paris / Lady Montague (as Martin Neeley)\n\
The Choir of St. George\'s School in Windsor' + _(' as ') + 'Choir (as The Choir of St. George\'s School, Windsor) rest of cast listed alphabetically:\n\
Jason Canning' + _(' as ') + 'Nobleman (uncredited)\n\
Kelley Costigan' + _(' as ') + 'Theatregoer (uncredited)\n\
Rupert Everett' + _(' as ') + 'Christopher Marlowe (uncredited)\n\
John Inman' + _(' as ') + 'Character player (uncredited)',
            'country'           : 'USA | UK',
            'genre'             : 'Comedy | Drama | Romance',
            'classification'    : 'R',
            'studio'            : 'Universal Pictures, Miramax Films, Bedford Falls Productions',
            'o_site'            : False,
            'site'              : 'http://www.imdb.com/title/tt0138097',
            'trailer'           : 'http://www.imdb.com/title/tt0138097/trailers',
            'year'              : 1998,
            'notes'             : _('Language') + ': English\n'\
+ _('Audio') + ': Dolby Digital\n'\
+ _('Color') + ': Color\n\
Tagline: ...A Comedy About the Greatest Love Story Almost Never Told...\n\
Love is the only inspiration',
            'runtime'           : 123,
            'image'             : True,
            'rating'            : 7,
            'screenplay'        : 'Marc Norman, Tom Stoppard',
            'cameraman'         : 'Richard Greatrex',
            'barcode'           : False
        },
    }

