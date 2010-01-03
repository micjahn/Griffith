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
import string

try:
    import pyodbc
except ImportError:
    pass

import logging
log = logging.getLogger("Griffith")


class ImportPlugin(IP):
    description  = _('WenSoftware The Movie Library 1.4.x')
    author       = 'Michael Jahn'
    email        = 'griffith-private@lists.berlios.de'
    version      = '1.0'
    file_filters = '*.[dD][mM][vV]'
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
                curs = self.connection.cursor()
                curs.execute('SELECT COUNT(*) FROM Movie')
                count = curs.fetchone()[0]
                curs.close()
            except:
                log.exception('')
        else:
            log.error('The Movie Library Import: No connection object.')
        log.info('The Movie Library Import: %s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.cursor:
            self.cursor = self.connection.cursor()
            self.cursor.execute( \
                'SELECT MovieID, Title, Format, Genre, Subgenre, Year, \
                        UPC, Country, Studio, AudienceRating, URL, Region, \
                        Length, Director, Writer, Photographer, Plot, \
                        FrontCover, Seen, Comment, Actor, Trailer, Color, Rating \
                 FROM Movie')

        currentrow = self.cursor.fetchone()
        if not currentrow:
            return None

        details = {}
        try:
            if currentrow[1]:
                details['title'] = currentrow[1]
            if currentrow[2]:
                # setting medium_id to string mediumname; mapping is done in base class
                details['medium_id'] = currentrow[2]
            if currentrow[3]:
                details['genre'] = currentrow[3]
            if currentrow[4]:
                details['genre'] = details['genre'] + ', ' + currentrow[4]
            if currentrow[5]:
                details['year'] = currentrow[5]
            if currentrow[6]:
                details['barcode'] = currentrow[6]
            if currentrow[7]:
                details['country'] = currentrow[7]
            if currentrow[8]:
                details['studio'] = currentrow[8]
            if currentrow[9]:
                details['classification'] = currentrow[9]
            if currentrow[10]:
                details['site'] = currentrow[10]
            if currentrow[11]:
                region = string.replace(currentrow[11], 'Region ', '')
                try:
                    details['region'] = int(region)
                except:
                    pass
            if currentrow[12]:
                details['runtime'] = currentrow[12]
            if currentrow[13]:
                details['director'] = currentrow[13]
            if currentrow[14]:
                details['screenplay'] = currentrow[14]
            if currentrow[15]:
                details['cameraman'] = currentrow[15]
            if currentrow[16]:
                details['plot'] = currentrow[16]
            if currentrow[17]:
                # TODO: fetching poster from www if an url is given?
                if not currentrow[17][0:4] == 'http':
                    details['image'] = currentrow[17]
            if currentrow[18]:
                details['seen'] = currentrow[18]
            if currentrow[19]:
                details['notes'] = currentrow[19]
            if currentrow[20]:
                cast = ''
                actors = currentrow[20].split('	')
                for actor in actors:
                    actorandrole = actor.split('|')
                    if len(actorandrole) > 1 and actorandrole[1]:
                        cast = cast + actorandrole[0] + _(' as ') + actorandrole[1] + '\n'
                    else:
                        cast = cast + actorandrole[0] + '\n'
                details['cast'] = cast
            if currentrow[21]:
                trailers = currentrow[21].split('	')
                if len(trailers) > 0:
                    nameandurl = trailers[0].split('|')
                    if len(nameandurl) > 1 and nameandurl[1]:
                        details['trailer'] = nameandurl[1]
            if currentrow[22]:
                if currentrow[22] == 0:
                    details['color'] = 1
                elif currentrow[22] == 1:
                    details['color'] = 2
            if currentrow[23]:
                details['rating'] = currentrow[23]
        except Exception, e:
            log.exception('')
            details = None

        return details

    def clear(self):
        """clear plugin before next source file"""
        IP.clear(self)
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
        self.fileversion = None

    def destroy(self):
        """close all resources"""
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        try:
            log.debug('Connecting with: DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s' % string.replace(self.filename, '\\', '\\\\'))
            self.connection = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s' % string.replace(self.filename, '\\', '\\\\'))
            curs = self.connection.cursor()
            tablerow = curs.tables(table='Movie').fetchone()
            if tablerow:
                version = 1.4
            curs.close()
        except Exception, e:
            log.error(str(e))
        log.info('The Movie Library Import: Found file version %s' % version)
        return version
