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
import os

import logging
log = logging.getLogger("Griffith")


class ImportPlugin(IP):
    description  = 'MovieTrack (v3.4x)'
    author       = 'Michael Jahn'
    email        = 'griffith@griffith.cc'
    version      = '1.0'
    file_filters = '*.[dD][aA][tT]'
    mime_types   = None

    fileversion  = None
    openedfile   = None
    imdbfilename = None

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
            gutils.error(_('The format of the file is not supported.'))
            return False
        if self.filename:
            self.imdbfilename = os.path.join(os.path.dirname(self.filename), 'IMDb.dat')
        else:
            self.imdbfilename = None
        return True

    def count_movies(self):
        """Returns number of movies in file which is about to be imported"""
        count = 0
        fileforcount = open(self.filename)
        try:
            for line in fileforcount:
                count = count + 1
        except:
            log.exception('')
        finally:
            fileforcount.close()
        log.info('MovieTrack Import: %s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.openedfile:
            self.openedfile = open(self.filename)

        details = {}
        try:
            fields = []
            while len(fields) != 13:
                currentline = self.openedfile.readline()
                if not currentline:
                    return None
                fields = currentline[2:-2].split('||')

            if not fields[0] == 'NULL':
                details['title'] = unicode(fields[0])   # MovieName
            #details[''] = fields[1]    # SubEntry
            #details[''] = fields[2]    # Location
            if not fields[3] == 'NULL':
                details['genre'] = unicode(fields[3])   # Genre
            #details[''] = fields[4]    # Presence
            if not fields[5] == 'NULL':
                details['medium_id'] = fields[5]        # Medium
            if not fields[6] == 'NULL':
                try:
                    details['rating'] = int(gutils.before(fields[6], '/')) # Rating
                except:
                    pass
            if not fields[7] == 'NULL':
                filepath = fields[7]                    # FilePath
                if not os.path.exists(filepath):
                    filename = os.path.basename(filepath)
                    filepath = os.path.join('Covers', filename)
                    if not os.path.exists(filepath):
                        filepath = filename
                        if not os.path.exists(filepath):
                            filepath = None
                if filepath:
                    details['poster'] = filepath
            if not fields[8] == 'NULL':
                details['barcode'] = unicode(fields[8]) # Barcode
            #details[''] = fields[9]    # AKA
            if not fields[10] == 'NULL':
                details['notes'] = unicode(fields[10])  # Comments
            movieid = fields[11]                        # AGN
            #details[''] = fields[12]   # UGN

            # try to get some more details from imdb-file
            try:
                if self.imdbfilename:
                    openedimdb = open(self.imdbfilename)
                    while fields:
                        fields = []
                        while len(fields) != 17:
                            currentline = openedimdb.readline()
                            if not currentline:
                                fields = None
                                break
                            fields = currentline[2:-2].split('||')
                        if fields and fields[1] == movieid:
                            #details[''] = fields[0]     # MovieName
                            #details[''] = fields[1]     # AGN
                            #details[''] = fields[2]     # Title
                            #details[''] = fields[3]     # AKA
                            if not fields[4] == 'NULL':
                                details['year'] = fields[4]              # Year
                            if not fields[5] == 'NULL':
                                details['director'] = unicode(fields[5]) # Director
                            #details[''] = fields[6]     # Tagline
                            if not fields[7] == 'NULL':
                                details['plot'] = unicode(fields[7])     # Summary
                            if not fields[8] == 'NULL' and not 'genre' in details:
                                details['genre'] = unicode(fields[8])   # Genre
                            if not fields[9] == 'NULL':
                                details['cast'] = unicode(fields[9])    # Actors
                            if not fields[10] == 'NULL':
                                details['classification'] = unicode(fields[10]) # MPAA
                            #details[''] = fields[11]    # Language
                            if not fields[12] == 'NULL':
                                details['runtime'] = fields[12]         # Runtime
                            if not fields[13] == 'NULL' and not 'rating' in details:
                                try:
                                    details['rating'] = int(gutils.before(fields[13], '/')) # Rating
                                except:
                                    pass
                            #details[''] = fields[14]    # VoteCount
                            if not fields[15] == 'NULL':
                                details['site'] = unicode(fields[15])    # URL
                            #details[''] = fields[16]    # Exclude
            except:
                log.exception('')
            finally:
                openedimdb.close()

        except EOFError:
            details = None
        except Exception, e:
            log.exception('')
            details = None

        return details

    def clear(self):
        """clear plugin before next source file"""
        IP.clear(self)
        if self.openedfile:
            self.openedfile.close()
            self.openedfile = None
        self.fileversion = None

    def destroy(self):
        """close all resources"""
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        try:
            openfile = open(self.filename)
            try:
                firstline = openfile.readline()
                if firstline[0] == '~':
                    firstlineparts = string.split(firstline, '||')
                    if len(firstlineparts) == 13:
                        version = 3.4
            finally:
                openfile.close()
        except Exception, e:
            log.error(str(e))
        log.info('MovieTrack Import: Found file version %s' % version)
        return version
