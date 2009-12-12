# -*- coding: utf-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2009

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
import gutils

try:
    import sqlite3
except ImportError:
    from pysqlite2 import dbapi2 as sqlite3

import logging
log = logging.getLogger("Griffith")

class ImportPlugin(IP):
    description  = _('wintoolz Filmdatenbank (version 1.0.0.x)')
    author       = 'Michael Jahn'
    email        = 'griffith-private@lists.berlios.de'
    version      = '1.0'
    file_filters = '*.[dD][bB]'
    mime_types   = None

    fileversion  = None
    connection   = None
    cursor       = None

    def initialize(self):
        if not IP.initialize(self):
            return False
        self.edit = False
        return True
    
    def set_source(self, name):
        IP.set_source(self, name)
        self.filename = name
        self.fileversion = self.read_fileversion()
        if self.fileversion == None:
            gutils.error(self, _('The format of the file is not supported.'))
            return False
        return True

    def count_movies(self):
        """Returns number of movies in file which is about to be imported"""
        count = 0
        if self.connection:
            try:
                c = self.connection.execute('SELECT COUNT(*) FROM Main')
                count = c.fetchone()[0]
            except:
                log.exception('')
        else:
            log.error('wintoolz Filmdatenbank: No connection object.')
        log.info('wintoolz Filmdatenbank Import: %s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.cursor:
            self.cursor = self.connection.execute( \
                'SELECT Titel, Original, Produktionsjahr, Laufzeit,\
                 FSKZahl, Handlung, Ausstattung, EAN, Disks, Genre, Regie, Drehbuch,\
                 Kamera, Studio, Produktionsland, Darsteller, Rolle, Notiz, Cover,\
                 Mediendatei, BewertungHandlung, BewertungDarsteller, BewertungMusik,\
                 BewertungEmotionen, BewertungSpecialEffects, GesehenZahl, Farbdarstellung \
                 FROM Main')
        
        currentrow = self.cursor.fetchone()
        if not currentrow:
            return None
        
        details = {}
        try:
            if currentrow[0]:
                details['title'] = currentrow[0]
            if currentrow[1]:
                details['o_title'] = currentrow[1]
            if currentrow[2]:
                details['year'] = currentrow[2]
            if currentrow[3]:
                details['runtime'] = currentrow[3]
            if currentrow[4] and not currentrow[4] == 0:
                details['classification'] = currentrow[4]
            if currentrow[5]:
                details['plot'] = currentrow[5]
            if currentrow[6]:
                # setting medium_id to string mediumname; mapping is done in base class
                details['medium_id'] = currentrow[6]
            if currentrow[7]:
                details['barcode'] = currentrow[7]
            if currentrow[8]:
                details['media_num'] = currentrow[8]
            if currentrow[9]:
                details['genre'] = currentrow[9]
            if currentrow[10]:
                details['director'] = currentrow[10]
            if currentrow[11]:
                details['screenplay'] = currentrow[11]
            if currentrow[12]:
                details['cameraman'] = currentrow[12]
            if currentrow[13]:
                details['studio'] = currentrow[13]
            if currentrow[14]:
                details['country'] = currentrow[14]
            if currentrow[15] and currentrow[16]:
                cast = ''
                actors = currentrow[15].split('\r\n')
                roles = currentrow[16].split('\r\n')
                length = len(actors)
                if len(roles) > length:
                    length = len(roles)
                for index in range(0, length, 1):
                    actorrole = ''
                    if index < len(actors):
                        actorrole = actorrole + actors[index]
                    actorrole = actorrole + _(' as ')
                    if index < len(roles):
                        actorrole = actorrole + roles[index]
                    cast = cast + actorrole + '\n'
                details['cast'] = cast
            if currentrow[17]:
                details['notes'] = currentrow[17]
            if currentrow[18]:
                details['poster'] = currentrow[18]
            if currentrow[19]:
                details['trailer'] = currentrow[19]
            try:
                details['rating'] = round(0.4 * ( \
                    float(currentrow[20]) + float(currentrow[21]) + \
                    float(currentrow[22]) + float(currentrow[23]) + \
                    float(currentrow[24])), 0)
            except:
                pass
            if currentrow[25]:
                details['seen'] = currentrow[25]
            if currentrow[26] and currentrow[26] == 'Schwarz-Weiss':
                details['color'] = 2
        except Exception, e:
            log.exception('')
            details = None
        
        return details

    def clear(self):
        """clear plugin before next source file"""
        IP.clear(self)
        self.cursor = None
        self.connection = None
        self.fileversion = None

    def destroy(self):
        """close all resources"""
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        try:
            self.connection = sqlite3.connect(self.filename)
            if self.connection.execute('PRAGMA table_info(Main)').fetchone():
                version = 1.0
        except Exception, e:
            log.error(str(e))
        log.info('wintoolz Filmdatenbank Import: Found file version %s' % version)
        return version;

