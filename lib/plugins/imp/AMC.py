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
import os
import gutils
import string
import struct

import logging
log = logging.getLogger("Griffith")

# format:
#  LFFNR -> length field for next record
# field name        size in bytes
#--------------------------------
# Number            4
# Date              4
# Rating            4
# Year              4
# Length            4
# VideoBitrate      4
# AudioBitrate      4
# Disks             4
# Checked           1
# LFFNR             4
# Media             LFFNR
# LFFNR             4       # since V 3.3
# MediaType         LFFNR   # since V 3.3
# LFFNR             4       # since V 3.3
# MediaSource       LFFNR   # since V 3.3
# LFFNR             4
# Borrower          LFFNR
# LFFNR             4
# OriginalTitle     LFFNR
# LFFNR             4
# TranslatedTitle   LFFNR
# LFFNR             4
# Director          LFFNR
# LFFNR             4
# Producer          LFFNR
# LFFNR             4
# Country           LFFNR
# LFFNR             4
# Category          LFFNR
# LFFNR             4
# Actors            LFFNR
# LFFNR             4
# URL               LFFNR
# LFFNR             4
# Description       LFFNR
# LFFNR             4
# Comments          LFFNR
# LFFNR             4
# VideoFormat       LFFNR
# LFFNR             4
# AudioFormat       LFFNR
# LFFNR             4
# Resolution        LFFNR
# LFFNR             4
# Framerate         LFFNR
# LFFNR             4
# Languages         LFFNR
# LFFNR             4
# Subtitles         LFFNR
# LFFNR             4
# Size              LFFNR
# LFFNR             4
# Picture           LFFNR
# LFFNR             4
# PictureData       LFFNR


class ImportPlugin(IP):
    description  = _('Ant Movie Catalog (version 3.5)')
    author       = 'Michael Jahn'
    email        = 'griffith-private@lists.berlios.de'
    version      = '1.1'
    file_filters = '*.[aA][mM][cC]'
    mime_types   = None

    fileHeader   = ' AMC_?.? Ant Movie Catalog         www.buypin.com  www.ant.be.tf '
    fileHeader31 = ' AMC_3.1 Ant Movie Catalog 3.1.x   www.buypin.com  www.ant.be.tf '
    fileHeader33 = ' AMC_3.3 Ant Movie Catalog 3.3.x   www.buypin.com  www.ant.be.tf '
    fileHeader35 = ' AMC_3.5 Ant Movie Catalog 3.5.x   www.buypin.com    www.antp.be '

    fileversion  = 0
    openfile     = None # for get_movie_details

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
        nroffields = 23 # since V 3.3
        ifile = open(self.filename, 'rb')
        try:
            # seek to first record
            ifile.seek(len(self.fileHeader) + 16)
            # count records
            while True:
                ifile.seek(33, os.SEEK_CUR)
                i = 0
                while i < nroffields:
                    self.seekfield(ifile)
                    i = i + 1
                count = count + 1
        except EOFError:
            pass
        except Exception, e:
            log.error(str(e))
        finally:
            ifile.close()
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if self.openfile == None:
            self.openfile = open(self.filename, 'rb')
            # seek to first record
            self.openfile.seek(len(self.fileHeader) + 16)
        details = {}
        try:
            details['number'] = self.readintfield(self.openfile)        # Number            4
            self.openfile.seek(4, os.SEEK_CUR)                          # Date              4
            details['rating'] = self.readintfield(self.openfile)        # Rating            4
            details['year'] = self.readintfield(self.openfile)          # Year              4
            details['runtime'] = self.readintfield(self.openfile)       # Length            4
            self.openfile.seek(4, os.SEEK_CUR)                          # VideoBitrate      4
            self.openfile.seek(4, os.SEEK_CUR)                          # AudioBitrate      4
            details['media_num'] = self.readintfield(self.openfile)     # Disks             4
            details['seen'] = self.readboolfield(self.openfile)         # Checked           1
            self.seekfield(self.openfile)                               # Media             LFFNR
            if self.fileversion >= 3.3:
                # setting medium_id to string mediumname; mapping is done in base class
                details['medium_id'] = self.readstringfield(self.openfile) # MediaType         LFFNR   # since V 3.3
                self.seekfield(self.openfile)                           # MediaSource       LFFNR   # since V 3.3
            self.seekfield(self.openfile)                               # Borrower          LFFNR
            details['o_title'] = self.readstringfield(self.openfile)    # OriginalTitle     LFFNR
            details['title'] = self.readstringfield(self.openfile)      # TranslatedTitle   LFFNR
            details['director'] = self.readstringfield(self.openfile)   # Director          LFFNR
            self.seekfield(self.openfile)                               # Producer          LFFNR
            details['country'] = self.readstringfield(self.openfile)    # Country           LFFNR
            details['genre'] = self.readstringfield(self.openfile)      # Category          LFFNR
            details['cast'] = self.readstringfield(self.openfile)       # Actors            LFFNR
            details['o_site'] = self.readstringfield(self.openfile)     # URL               LFFNR
            details['plot'] = self.readstringfield(self.openfile)       # Description       LFFNR
            details['notes'] = self.readstringfield(self.openfile)      # Comments          LFFNR
            self.seekfield(self.openfile)                               # VideoFormat       LFFNR
            self.seekfield(self.openfile)                               # AudioFormat       LFFNR
            self.seekfield(self.openfile)                               # Resolution        LFFNR
            self.seekfield(self.openfile)                               # Framerate         LFFNR
            self.seekfield(self.openfile)                               # Languages         LFFNR
            self.seekfield(self.openfile)                               # Subtitles         LFFNR
            self.seekfield(self.openfile)                               # Size              LFFNR
            posterfilename = self.readstringfield(self.openfile)        # Picture           LFFNR
            posterdata = self.readbinaryfield(self.openfile)            # PictureData       LFFNR
            if posterdata:
                details['poster'] = posterdata
            elif posterfilename and len(posterfilename) > 4:
                details['poster'] = posterfilename

            if details['title'] == None:
                details['title'] = details['o_title']
            if details['o_title'] == None:
                details['o_title'] = details['title']
            if not details['cast'] == None:
                details['cast'] = string.replace(details['cast'], ', ', '\n')
            if self.fileversion >= 3.5:
                if not details['rating'] == None:
                    details['rating'] = round(float(details['rating']) / 10.0, 0)
        except EOFError:
            details = None
        except Exception, e:
            log.error(str(e))
            details = None
        return details

    def clear(self):
        """clear plugin before next source file"""
        IP.clear(self)
        if self.openfile:
            self.openfile.close()
            self.openfile = None
            self.fileversion = 0

    def destroy(self):
        """close all resources"""
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        header = ''
        ifile = open(self.filename, 'rb')
        try:
            header = ifile.read(len(self.fileHeader))
        finally:
            ifile.close()
        # no support for other versions at the moment
        if header == self.fileHeader35:
            version = 3.5
        elif header == self.fileHeader33:
            version = 3.3
        elif header == self.fileHeader31:
            version = 3.1
        return version

    def seekfield(self, ifile):
        lenStr = ifile.read(4)
        if len(lenStr) < 4:
            raise EOFError
        lenTuple = struct.unpack('i', lenStr)
        if lenTuple[0]:
            ifile.seek(lenTuple[0], os.SEEK_CUR)

    def readstringfield(self, ifile):
        field = None
        lenStr = ifile.read(4)
        if len(lenStr) < 4:
            raise EOFError
        lenTuple = struct.unpack('i', lenStr)
        if lenTuple[0]:
            field = ifile.read(lenTuple[0]).decode('iso8859-1')
        return field

    def readintfield(self, ifile):
        intStr = ifile.read(4)
        if len(intStr) < 4:
            raise EOFError
        intTuple = struct.unpack('i', intStr)
        if intTuple[0] == -1:
            return None
        return intTuple[0]

    def readboolfield(self, ifile):
        byteStr = ifile.read(1)
        intValue = ord(byteStr[0])
        if intValue == -1:
            return None
        return intValue != 0

    def readbinaryfield(self, ifile):
        field = None
        lenStr = ifile.read(4)
        if len(lenStr) < 4:
            raise EOFError
        lenTuple = struct.unpack('i', lenStr)
        if lenTuple[0]:
            field = ifile.read(lenTuple[0])
        return field
