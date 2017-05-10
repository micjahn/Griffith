# -*- coding: utf-8 -*-

__revision__ = '$Id: PluginMovieAniDB.py 1633 2012-12-28 23:11:42Z mikej06 $'

# Copyright © 2005-2011 Piotr Ożarowski
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

import urllib2
import logging
from datetime import datetime, timedelta
from locale import getdefaultlocale
from os.path import getmtime, isfile, join

from lxml import etree

from gutils import decompress
from movie import Movie, SearchMovie

log = logging.getLogger("Griffith")

plugin_name         = 'AnimeDB'
plugin_description  = 'Anime DataBase'
plugin_url          = 'www.anidb.net'
plugin_language     = _('English')
plugin_author       = 'Piotr Ożarowski'
plugin_author_email = 'piotr@griffith.cc'
plugin_version      = '3.0'

ANIME_TITLES_URL = 'http://anidb.net/api/animetitles.xml.gz'
ANIME_IMG_URL = 'http://img7.anidb.net/pics/anime/'
#ANIME_WEB_URL = 'http://anidb.net/perl-bin/animedb.pl?show=anime&aid='
ANIME_WEB_URL = 'http://anidb.net/a'
REQUEST = "http://api.anidb.net:9001/httpapi?request=anime&client=%(client)s&clientver=%(version)s&protover=%(protocol)s&aid="
REQUEST %= dict(client='griffith', version=1, protocol=1)

lang = getdefaultlocale()[0][:2]  # TODO: get it from settings


class Plugin(Movie):
    def __init__(self, aid):
        self.encode = None
        self.useurllib2 = True
        self._aid = aid
        self.url = REQUEST + aid

    def initialize(self):
        if not self.page.startswith('<?xml'):
            raise Exception('page not in XML format')
        self._xml = etree.fromstring(self.page)

    def get_image(self):
        self.image_url = ''
        node = self._xml.find('picture')
        if node is not None:
            self.image_url = ANIME_IMG_URL + node.text

    def get_o_title(self):
        self.o_title = ''
        node = self._xml.find('titles/title[@type="main"]')
        if node is not None:
            self.o_title = node.text

    def get_title(self):
        node = self._xml.xpath("titles/title[@xml:lang='%s' and @type='official']" % lang)
        if node:
            self.title = node[0].text
        else:
            node = self._xml.xpath("titles/title[@type='official']")
            if node:
                self.title = node[0].text

    def get_director(self):
        self.director = ', '.join(n.text for n in self._xml.xpath('creators/name[@type="Direction"]'))

    def get_plot(self):
        self.plot = ''
        node = self._xml.find('description')
        if node is not None:
            self.plot = node.text

    def get_year(self):
        self.year = 0
        node = self._xml.xpath('episodes/episode[title="Complete Movie"]')
        if node:
            node = node[0].find('airdate')
            if node is not None:
                self.year = node.text[:4]
        else:
            node = self._xml.find('startdate')
            if node is not None:
                self.year = node.text[:4]
        # XXX: should we take the first child if "Complete Movie" is missing?

    def get_runtime(self):
        self.runtime = 0
        node = self._xml.xpath('episodes/episode[title="Complete Movie"]')
        if node:
            self.runtime = node[0].find('length').text

    def get_genre(self):
        nodes = self._xml.xpath('categories/category/name')
        self.genre = ', '.join(n.text for n in nodes)

    def get_cast(self):
        nodes = self._xml.xpath('characters/character[@type="main character in"]')
        self.cast = ''
        for node in nodes:
            name = node.find('name').text
            actor = node.find('seiyuu').text
            self.cast += "[%s] voiced by %s\n" % (name, actor)

    def get_studio(self):
        self.studio = ', '.join(n.text for n in self._xml.xpath('creators/name[@type="Animation Production"]'))

    def get_o_site(self):
        self.o_site = ''
        node = self._xml.find('url')
        if node is not None:
            self.o_site = node.text

    def get_site(self):
        self.site = ANIME_WEB_URL + self._aid

    def get_rating(self):
        rating = self._xml.find('ratings/permanent')
        if rating is not None:
            self.rating = str(round(float(rating.text)))

    def get_notes(self):
        self.notes = ''
        # ...type and episodes
        type_ = self._xml.find('type')
        if type_ is not None:
            self.notes += "Type: %s\n" % type_.text
        episodes = {}
        for node in self._xml.xpath('episodes/episode'):
            try:
                key = int(node.find('epno').text)
            except:
                key = node.find('epno').text
            titles = {}
            for tnode in node.xpath('title'):
                titles[tnode.attrib['{http://www.w3.org/XML/1998/namespace}lang']] = tnode.text
            duration = node.find('length').text
            airdate = node.find('airdate')
            airdate = airdate.text if airdate is not None else None
            episodes[key] = dict(titles=titles, duration=duration, airdate=airdate)
        for key, details in sorted(episodes.iteritems()):
            self.notes += "\n%s: " % key
            self.notes += details['titles'].get(lang, details['titles']['en'])
            self.notes += " (%s" % details['duration']
            self.notes += _(' min')
            if details['airdate']:
                self.notes += ", %s)" % details['airdate']
            else:
                self.notes += ')'


class SearchPlugin(SearchMovie):
    original_url_search = 'http://anidb.net/'
    translated_url_search = 'http://anidb.net/'

    def load_titles(self, fpath, parent_window):
        # animetitles.xml.gz is updated once a day
        remote = None
        download = True
        if isfile(fpath):
            cache_last_modified = datetime.fromtimestamp(getmtime(fpath))
            if cache_last_modified > datetime.now() - timedelta(days=1):
                download = False
            else:
                remote = urllib2.urlopen(ANIME_TITLES_URL)
                last_modified = datetime(*remote.info().getdate('Last-Modified')[:7])
                if cache_last_modified >= last_modified:
                    download = False
                remote.close()

        if download:
            log.info('downloading title list from %s' % ANIME_TITLES_URL)
            self.url = ''
            self.title = ANIME_TITLES_URL
            self.open_search(parent_window, fpath)

        return etree.fromstring(decompress(open(fpath, 'rb').read()))

    def search(self, parent_window):
        self._search_results = []
        exml = self.load_titles(join(self.locations['home'], 'animetitles.xml.gz'), parent_window)
        for node in exml.xpath("anime[contains(., '%s')]" % self.title.replace("'", r"\'")):
            aid = node.attrib['aid']
            title = node.xpath("title[@xml:lang='%s']" % lang)
            # XXX: how about xpath with both cases and sorting results later?
            if not title:
                title = node.xpath('title[@type="main"]')[0].text
            else:
                title = title[0].text
            self._search_results.append((aid, title))

        return self._search_results

    def get_searches(self):
        del self.ids[:]
        del self.titles[:]
        self.number_results = len(self._search_results)
        for aid, title in self._search_results:
            self.ids.append(aid)
            self.titles.append(title)

#
# Plugin Test
#


class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Hellsing': [ 1, 1 ]
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
        '32': {
            'title'               : 'Hellsing',
            'o_title'             : 'Hellsing',
            'director'            : 'Urata Yasunori',
            'plot'                : True,
            'cast'                : u'[Alucard] voiced by Nakata Jouji\n\
[Sir Integral Fairbrook Wingates Hellsing] voiced by Sakakibara Yoshiko\n\
[Seras Victoria] voiced by Orikasa Fumiko\n\
[Incognito] voiced by Yamazaki Takumi',
            'country'             : False,
            'genre'               : 'Law and Order, Alternative Present, Horror, Vampires, Gunfights, Action, Contemporary Fantasy, United Kingdom, Earth, Europe, Special Squads, Cops, Manga, Seinen, Violence, Fantasy, Present, London, Zombies',
            'classification'      : False,
            'studio'              : False,
            'o_site'              : 'http://www.gonzo.co.jp/works/0102.html',
            'site'                : 'http://anidb.net/a32',
            'trailer'             : False,
            'year'                : 2001,
            'notes'               : True,
            'runtime'             : 0,
            'image'               : True,
            'rating'              : 6,
            'cameraman'           : False,
            'screenplay'          : False
        },
    }
