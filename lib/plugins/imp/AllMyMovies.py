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
    description  = _('All My Movies 5.7')
    author       = 'Michael Jahn'
    email        = 'griffith-private@lists.berlios.de'
    version      = '1.0'
    file_filters = '*.[aA][mM][mM]'
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
                curs.execute('SELECT COUNT(*) FROM movies')
                count = curs.fetchone()[0]
            except:
                log.exception('')
        else:
            log.error('AllMyMovies Import: No connection object.')
        log.info('AllMyMovies Import: %s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.cursor:
            self.cursor = self.connection.cursor()
            self.cursor.execute( \
                'SELECT MovieID, barcode, comments, description, length, mediacount, MediaTypeName, \
                        mpaa, Name, originaltitle, rating, seen, studio, url, year, Trailer \
                 FROM movies LEFT OUTER JOIN MediaType ON movies.MediaTypeID=MediaType.MediaTypeID;')
        
        currentrow = self.cursor.fetchone()
        if not currentrow:
            return None
        
        details = {}
        try:
            movieID = currentrow[0]
            if currentrow[1]:
                details['barcode'] = currentrow[1]
            if currentrow[2]:
                details['notes'] = currentrow[2]
            if currentrow[3]:
                details['plot'] = currentrow[3]
            if currentrow[4]:
                details['runtime'] = gutils.digits_only(currentrow[4])
            if currentrow[5]:
                details['media_num'] = currentrow[5]
            if currentrow[6]:
                details['medium_id'] = currentrow[6]
            if currentrow[7]:
                details['classification'] = currentrow[7]
            if currentrow[8]:
                details['title'] = currentrow[8]
            if currentrow[9]:
                details['o_title'] = currentrow[9]
            if currentrow[10]:
                details['rating'] = round(currentrow[10] / 10.0, 0)
            if currentrow[11]:
                details['seen'] = currentrow[11]
            if currentrow[12]:
                details['studio'] = currentrow[12]
            if currentrow[13]:
                details['url'] = currentrow[13]
            if currentrow[14]:
                details['year'] = currentrow[14]
            if currentrow[15]:
                details['trailer'] = currentrow[15]
            # loading other details
            curs = self.connection.cursor()
            curs.execute('SELECT Actors.Name, ActorsLink.Role \
                          FROM Actors INNER JOIN ActorsLink ON Actors.ActorID=ActorsLink.ActorID \
                          WHERE ActorsLink.MovieID=' + str(movieID))
            currentrow = curs.fetchone()
            if currentrow:
                if currentrow[1]:
                    cast = currentrow[0] + _(' as ') + currentrow[1]
                else:
                    cast = currentrow[0]
                currentrow = curs.fetchone()
                while currentrow:
                    if currentrow[1]:
                        cast = cast + '\n' + currentrow[0] + _(' as ') + currentrow[1]
                    else:
                        cast = cast + '\n' + currentrow[0]
                    currentrow = curs.fetchone()
                details['cast'] = cast
            
            curs.execute('SELECT Countries.Name \
                          FROM Countries INNER JOIN CountryLink ON Countries.CountryID=CountryLink.CountryID \
                          WHERE CountryLink.MovieID=' + str(movieID))
            currentrow = curs.fetchone()
            if currentrow:
                country = currentrow[0]
                currentrow = curs.fetchone()
                while currentrow:
                    country = country + ', ' + currentrow[0]
                    currentrow = curs.fetchone()
                details['country'] = country
            
            curs.execute('SELECT Actors.Name \
                          FROM Actors INNER JOIN DirectorLink ON Actors.ActorID=DirectorLink.ActorID \
                          WHERE DirectorLink.MovieID=' + str(movieID))
            currentrow = curs.fetchone()
            if currentrow:
                director = currentrow[0]
                currentrow = curs.fetchone()
                while currentrow:
                    director = director + ', ' + currentrow[0]
                    currentrow = curs.fetchone()
                details['director'] = director
            
            curs.execute('SELECT Genres.Name \
                          FROM Genres INNER JOIN GenresLink ON Genres.GenreID=GenresLink.GenreID \
                          WHERE GenresLink.MovieID=' + str(movieID))
            currentrow = curs.fetchone()
            if currentrow:
                genre = currentrow[0]
                currentrow = curs.fetchone()
                while currentrow:
                    genre = genre + ', ' + currentrow[0]
                    currentrow = curs.fetchone()
                details['genre'] = genre
            
            curs.execute('SELECT images.image \
                          FROM images \
                          WHERE cover=-1 AND images.MovieID=' + str(movieID))
            currentrow = curs.fetchone()
            if currentrow:
                details['poster'] = currentrow[0]
            
            curs.close()
        except Exception, e:
            log.exception('')
            details = None
        #print details
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
            tablerow = curs.tables(table='movies').fetchone()
            if tablerow:
                version = 1.0
            curs.close()
        except Exception, e:
            log.error(str(e))
        log.info('AllMyMovies Import: Found file version %s' % version)
        return version;

