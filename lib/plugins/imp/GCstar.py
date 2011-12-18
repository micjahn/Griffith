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
from xml.dom import minidom

import logging
log = logging.getLogger("Griffith")


class ImportPlugin(IP):
    description  = 'GCstar (v1.4.x)'
    author       = 'Michael Jahn'
    email        = 'griffith@griffith.cc'
    version      = '1.0'
    file_filters = '*.[gG][cC][sS]'
    mime_types   = None

    fileversion  = None
    filedom      = None
    items        = None
    itemindex    = 0

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
        return True

    def count_movies(self):
        """Returns number of movies in file which is about to be imported"""
        count = 0
        if self.filedom:
            try:
                collectionElement = self.filedom.getElementsByTagName('collection')[0]
                count = int(collectionElement.getAttribute('items'))
            except Exception, e:
                log.error(str(e))
        else:
            log.error('No filedom object.')
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.filedom:
            self.filedom = minidom.parse(self.filename)
        if not self.items:
            self.items = self.filedom.getElementsByTagName('item')
            self.itemindex = 0
        if not self.items or len(self.items) < 1:
            return None
        if len(self.items) <= self.itemindex:
            return None

        details = {}
        try:
            item = self.items[self.itemindex]

            details['title']          = item.getAttribute('title')
            details['o_title']        = item.getAttribute('original')
            details['year']           = item.getAttribute('date')
            details['runtime']        = item.getAttribute('time')
            details['country']        = item.getAttribute('country')
            details['site']           = item.getAttribute('webPage')
            details['seen']           = item.getAttribute('seen') == '1'
            details['director']       = item.getAttribute('director')
            # image filenames are mostly a absolute path at the original system
            # which should be now a relative path to the xml database file
            imagefilename             = item.getAttribute('image')
            previoustail = ''
            previoushead = imagefilename
            while not os.path.exists(imagefilename) and previoushead:
                (head, tail) = os.path.split(previoushead)
                imagefilename = os.path.join(os.path.join(os.path.dirname(self.filename), tail), previoustail)
                previoustail = tail
                previoushead = head
            if os.path.exists(imagefilename):
                details['poster'] = imagefilename
            try:
                details['number']     = int(item.getAttribute('id'))
            except:
                pass
            try:
                details['media_num']  = int(item.getAttribute('number'))
            except:
                pass
            details['trailer']        = item.getAttribute('trailer')
            details['classification'] = item.getAttribute('age')
            details['rating']         = item.getAttribute('rating')
            synopsis = item.getElementsByTagName('synopsis')
            if len(synopsis) and len(synopsis[0].childNodes):
                details['plot'] = synopsis[0].childNodes[0].data
            comment = item.getElementsByTagName('comment')
            if len(comment) and len(comment[0].childNodes):
                details['notes'] = comment[0].childNodes[0].data
            genres = item.getElementsByTagName('genre')
            if len(genres):
                genrelines = genres[0].getElementsByTagName('line')
                genre = ''
                try:
                    for genreline in genrelines:
                        genrecols = genreline.getElementsByTagName('col')
                        if len(genrecols) and len(genrecols[0].childNodes):
                            genre = genre + genrecols[0].childNodes[0].data + ', '
                except:
                    log.error(str(e))
                if len(genre) > 2:
                    details['genre'] = genre[:-2]
            actors = item.getElementsByTagName('actors')
            if len(actors):
                actorlines = actors[0].getElementsByTagName('line')
                cast = ''
                try:
                    for actorline in actorlines:
                        actorcols = actorline.getElementsByTagName('col')
                        if len(actorcols):
                            if len(actorcols) > 1 and len(actorcols[0].childNodes) and len(actorcols[1].childNodes):
                                cast = cast + actorcols[0].childNodes[0].data + _(' as ') + actorcols[1].childNodes[0].data + "\n"
                            else:
                                if len(actorcols[0].childNodes):
                                    cast = cast + actorcols[0].childNodes[0].data + "\n"
                except:
                    log.error(str(e))
                if len(cast):
                    details['cast'] = cast
        except EOFError:
            details = None
        except Exception, e:
            log.error(str(e))
            details = None
        self.itemindex = self.itemindex + 1
        return details

    def clear(self):
        """clear plugin before next source file"""
        IP.clear(self)
        if self.filedom:
            self.filedom.unlink()
            self.filedom = None
            self.fileversion = None
            self.items = None
            self.itemindex = 0

    def destroy(self):
        """close all resources"""
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        self.filedom = minidom.parse(self.filename)
        try:
            collectionElement = self.filedom.getElementsByTagName('collection')[0]
            type = collectionElement.getAttribute('type')
            if type == 'GCfilms':
                version = collectionElement.getAttribute('version')
        except Exception, e:
            log.error(str(e))
            self.filedom.unlink()
            self.filedom = None
        return version
