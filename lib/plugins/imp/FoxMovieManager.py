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
    description  = 'Fox Movie Manager (v1.4)'
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
                curs.execute('SELECT COUNT(*) FROM tblMovie')
                count = curs.fetchone()[0]
                curs.close()
            except:
                log.exception('')
        else:
            log.error('Fox Movie Manager Import: No connection object.')
        log.info('Fox Movie Manager Import: %s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.cursor:
            self.cursor = self.connection.cursor()
            self.cursor.execute( \
                'SELECT fldIDtitle, fldTitle, fldSynopsis, fldActors, fldWriters, \
                        fldDirectors, fldStudio, fldYear, fldLength, fldDisks, \
                        fldPicPath, fldWatched, fldUserRating, fldRating, fldMedia, \
                        fldMoviePath, fldTrailerPath \
                 FROM tblMovie')

        currentrow = self.cursor.fetchone()
        if not currentrow:
            return None

        details = {}
        try:
            details['number'] = currentrow[0]
            if currentrow[1]:
                details['title'] = currentrow[1]
            if currentrow[2]:
                details['plot'] = currentrow[2]
            if currentrow[3]:
                cast = ''
                actors = currentrow[3].split(';')
                for actor in actors:
                    if actor:
                        actorandrole = actor.split('@')
                        if len(actorandrole) > 1 and actorandrole[1]:
                            cast = cast + actorandrole[0] + _(' as ') + actorandrole[1] + '\n'
                        else:
                            cast = cast + actorandrole[0] + '\n'
                details['cast'] = cast
            if currentrow[4]:
                details['screenplay'] = string.replace(currentrow[4], ';', ', ')
            if currentrow[5]:
                details['director'] = string.replace(currentrow[5], ';', ', ')
            if currentrow[6]:
                details['studio'] = currentrow[6]
            if currentrow[7]:
                details['year'] = currentrow[7]
            if currentrow[8]:
                details['runtime'] = currentrow[8]
            if currentrow[9]:
                details['media_num'] = currentrow[9]
            if currentrow[10]:
                details['poster'] = currentrow[10]
            if currentrow[11]:
                details['seen'] = currentrow[11]
            if currentrow[12]:
                if currentrow[12] > 10:
                    try:
                        details['rating'] = round(currentrow[12] / 10.0, 0)
                    except:
                        pass
                else:
                    details['rating'] = currentrow[12]
            if currentrow[13]:
                details['classification'] = currentrow[13]
            if currentrow[14]:
                # setting medium_id to string mediumname; mapping is done in base class
                details['medium_id'] = currentrow[14]
            if currentrow[15]:
                details['trailer'] = currentrow[15]
            elif currentrow[16]:
                details['trailer'] = currentrow[16]
            # looking for the genres
            cursgenre = self.connection.cursor()
            cursgenre.execute('SELECT fldGenre \
                FROM tblGenreTypes INNER JOIN tblGenre ON tblGenreTypes.fldIDgenre = tblGenre.fldGenreID \
                WHERE tblGenre.fldTitleID=' + str(currentrow[0]) + ';')
            currentrow = cursgenre.fetchone()
            if currentrow:
                genres = ''
                while currentrow:
                    genres = genres + currentrow[0] + ', '
                    currentrow = cursgenre.fetchone()
                details['genre'] = genres[:-2]
            cursgenre.close()
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
            tablerow = curs.tables(table='tblMovie').fetchone()
            if tablerow:
                version = 1.4
            curs.close()
        except Exception, e:
            log.error(str(e))
        log.info('Fox Movie Manager Import: Found file version %s' % version)
        return version
