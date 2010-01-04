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
    description  = 'MyDVDs (v1.6x)'
    author       = 'Michael Jahn'
    email        = 'griffith-private@lists.berlios.de'
    version      = '1.0'
    file_filters = '*.[mM][dD][bB]'
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
                curs.execute('SELECT COUNT(*) FROM dvd')
                count = curs.fetchone()[0]
            except:
                log.exception('')
        else:
            log.error('MyDVDs Import: No connection object.')
        log.info('MyDVDs Import: %s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.cursor:
            self.cursor = self.connection.cursor()
            self.cursor.execute( \
                'SELECT id, title, year, rating, stars, director, synop, \
                        cover, runtime, genre, notes, trailer, star5 \
                 FROM dvd;')

        currentrow = self.cursor.fetchone()
        if not currentrow:
            return None

        details = {}
        try:
            if currentrow[1]:
                details['title'] = currentrow[1]
            if currentrow[2]:
                details['year'] = currentrow[2]
            if currentrow[3]:
                details['classification'] = currentrow[3]
            if currentrow[4]:
                details['cast'] = currentrow[4]
            if currentrow[5]:
                details['director'] = currentrow[5]
            if currentrow[6]:
                details['plot'] = currentrow[6]
            if currentrow[7]:
                details['poster'] = currentrow[7]
            if currentrow[8]:
                details['runtime'] = gutils.digits_only(currentrow[8])
            if currentrow[9]:
                genre = string.replace(currentrow[9], '~', ', ')
                if len(genre) > 2:
                    details['genre'] = genre[2:]
            if currentrow[10]:
                details['notes'] = currentrow[10]
            if currentrow[11]:
                details['trailer'] = currentrow[11]
            if currentrow[12]:
                try:
                    details['rating'] = 2 * int(currentrow[12])
                except:
                    pass
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
            tablerow = curs.tables(table='dvd').fetchone()
            if tablerow:
                version = 1.6
            curs.close()
        except Exception, e:
            log.error(str(e))
        log.info('MyDVDs Import: Found file version %s' % version)
        return version
