# -*- coding: utf-8 -*-

__revision__ = '$Id: $'

# Copyright (c) 2015-2016 Elan Ruusamäe <glen@pld-linux.org>

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

from plugins.imp import ImportPlugin as IP
import os
import gutils
from lxml import etree
import tempfile
import requests
from movie import TempFileCleanup
import logging

log = logging.getLogger("Griffith")

"""
Supports importing videodb.xml exported as single file from Kodi/XBMC.

http://kodi.wiki/view/Import-export_library
http://kodi.wiki/view/HOW-TO:Backup_the_video_library

See lib/plugins/imp/__init__.py for workflow how importer invokes methods from importer plugins
"""
class ImportPlugin(IP):
    description  = 'Kodi/XBMC MovieDB importer'
    author       = 'Elan Ruusamäe'
    email        = 'glen@pld-linux.org'
    version      = '1.0'
    file_filters = 'videodb.xml'
    mime_types   = None

    fileversion  = None
    xml          = None
    items        = None
    itemindex    = 0
    poster_file  = None

    # used by get_movie_details method
    # griffith field => kodi field
    # griffith field is actual SQL column in 'movies' table
    field_map = {
        'title': 'title',
        'o_title': 'originaltitle',
        'year': 'year',
        'runtime': 'runtime',
        'rating': 'rating',
        'plot': 'plot',
        'director': 'director',
        'studio': 'studio',
        'country': 'country',
        'classification': 'mpaa',
        # while the trailer field exists, it is not useful for griffith
        # as it's something like: "plugin://plugin.video.youtube/?action=play_video&videoid=..."
        # however youtube urls can be probably fixed.
        'trailer': 'trailer',
    }

    # rest of the stuff to insert into notes field
    notes_map = {
        _('Id') : 'id',
        _('Play count'): 'playcount',
        _('Date added'): 'dateadded',
        _('Last played'): 'lastplayed',
        _('Collection'): 'set',
        _('Premiered'): 'premiered',
        _('Aired'): 'aired',
    }

    def initialize(self):
        if not IP.initialize(self):
            return False
        self.edit = False
        self.tempfiles = TempFileCleanup()

        return True

    def set_source(self, name):
        IP.set_source(self, name)
        self.filename = name
        self.fileversion = self.read_fileversion()
        if self.fileversion == None:
            gutils.error(_('The format of the file is not supported.'))
            return False
        return True

    def clear(self):
        """clear plugin state before next source file"""
        IP.clear(self)
        if self.xml:
            self.xml = None
            self.fileversion = None
            self.items = None
            self.itemindex = 0
            if self.poster_file:
                os.unlink(self.poster_file)
                self.poster_file = None

    def destroy(self):
        """close all resources"""
        self.tempfiles = None
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        try:
            self.xml = etree.parse(self.filename)
            version = self.xml.xpath('/videodb/version')[0].text
        except Exception, e:
            log.error(str(e))
        log.info('Found file version %s' % version)
        return version

    def count_movies(self):
        """Returns number of movies in file which is about to be imported"""
        if not self.xml:
            log.error('No XML object')
            return 0

        count = 0

        try:
            count = int(self.xml.xpath('count(/videodb/movie)'))
        except Exception, e:
            log.exception(e)

        log.info('%s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.xml:
            log.error('XML not opened')
            return None

        if not self.items:
            self.items = self.xml.xpath('/videodb/movie')
            self.itemindex = 0

        # don't bother for empty db (shouldn't happen really)
        if not self.items or len(self.items) < 1:
            return None

        # no more items
        if self.itemindex >= len(self.items):
            return None

        item = self.items[self.itemindex]

        # fill details
        details = {}

        # if playcount set, means it's seen
        details['seen'] = int(item.find('playcount').text) > 0

        # import only "seen" movies
        if not details['seen']:
            # increment for next iteration
            self.itemindex = self.itemindex + 1
            # importer will skip movie without title and original title
            return details

        for k,v in self.field_map.items():
            details[k] = item.findtext(v)

        # genre can be multiple items, join by comma
        details['genre'] = ', '.join(n.text for n in item.findall('genre'))

        # build text for 'cast' field
        cast = []
        for actor in item.findall('actor'):
            cast.append('%s as %s' % (actor.findtext('name'), actor.findtext('role')))

        if cast:
            details['cast'] = "\n".join(cast)

        # put rest of information into notes field
        notes = []
        for k,v in self.notes_map.items():
            v = item.findtext(v)
            if v:
                notes.append('%s: %s' % (k, v))

        # credits can have multiple values, handle separately
        credits = ', '.join(n.text for n in item.findall('credits'))
        if credits:
            notes.append(_('Credits: %s') % credits)

        if notes:
            details['notes'] = "\n".join(notes)

        # rating needs to be int or tellico will show it as 0 until movie is saved over
        if details['rating']:
            details['rating'] = int(float(details['rating']))

        # handle poster
        # take first <thumb aspect="poster"> element
        posters = item.xpath('thumb[@aspect="poster"]')
        if posters:
            self.poster_file = self.grab_url(posters[0].get('preview'), prefix = 'poster_', suffix = '.jpg')
            details['image'] = self.poster_file

        # increment for next iteration
        self.itemindex = self.itemindex + 1

        return details

    # grab url, return temp filename with remote file contents
    # XXX could not figure out how to use griffith own downloader with ui interaction, etc
    # XXX: grabbing urls while processing import xml blocks the ui
    def grab_url(self, url, prefix = None, suffix=None):
        (fd, local_file) = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        log.debug("Downloading: %s as %s" % (url, local_file))
        try:
            # http://stackoverflow.com/a/13137873/2314626
            r = requests.get(url, stream=True, timeout=0.1)
            if r.status_code == 200:
                for chunk in r.iter_content(1024):
                    os.write(fd, chunk)
            os.close(fd)

        except requests.exceptions.RequestException as e:
            log.error("HTTP Error: %s: %s" % (e, url))
            return None
        else:
            log.debug("Downloaded: %s" % url)
            self.tempfiles._tempfiles.append(local_file)
            return local_file

        # we get here with an exception, cleanup and return None
        os.unlink(local_file)
        return None
