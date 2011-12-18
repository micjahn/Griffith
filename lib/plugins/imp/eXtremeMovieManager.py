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
from xml.dom import minidom, Node

import logging
log = logging.getLogger("Griffith")


class ImportPlugin(IP):
    description  = 'eXtreme Movie Manager (v6.x / 7.x)'
    author       = 'Michael Jahn'
    email        = 'griffith@griffith.cc'
    version      = '1.0'
    file_filters = '*.[xX][mM][lL]'
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
                collectionElement = self.filedom.getElementsByTagName('XMM_Movie_Database')[0]
                for element in collectionElement.childNodes:
                    if element.nodeType == Node.ELEMENT_NODE and element.nodeName == 'Movie':
                        count = count + 1
                log.info('eXtreme Movie Manager Import: %s movies for import' % count)
            except:
                log.exception('')
        else:
            log.error('eXtreme Movie Manager Import: No filedom object.')
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.filedom:
            self.filedom = minidom.parse(self.filename)
        if not self.items:
            databaseElement = self.filedom.getElementsByTagName('XMM_Movie_Database')[0]
            self.items = databaseElement.childNodes
            self.itemindex = 0
        if not self.items or len(self.items) < 1:
            return None
        if len(self.items) <= self.itemindex:
            return None
        item = self.items[self.itemindex]
        while not (item.nodeType == Node.ELEMENT_NODE and item.nodeName == 'Movie') and len(self.items) > self.itemindex + 1:
            self.itemindex = self.itemindex + 1
            item = self.items[self.itemindex]
        if len(self.items) <= self.itemindex:
            return None
        if not len(item.childNodes):
            return None

        details = {}
        try:
            for node in item.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    if node.nodeName == 'Title' and len(node.childNodes) > 0:
                        details['title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'OriginalTitle' and len(node.childNodes) > 0:
                        details['o_title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Year' and len(node.childNodes) > 0:
                        details['year'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'URL' and len(node.childNodes) > 0:
                        details['o_site'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'WebLinkScript' and len(node.childNodes) > 0:
                        details['site'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'TrailerFile1' and len(node.childNodes) > 0:
                        details['trailer'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'MPAA' and len(node.childNodes) > 0:
                        details['classification'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Country' and len(node.childNodes) > 0:
                        details['country'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Genre' and len(node.childNodes) > 0:
                        details['genre'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Studio' and len(node.childNodes) > 0:
                        details['studio'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'UPC' and len(node.childNodes) > 0:
                        details['barcode'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Region' and len(node.childNodes) > 0:
                        details['region'] = node.childNodes[0].data[0]
                    elif node.nodeName == 'Length' and len(node.childNodes) > 0:
                        details['runtime'] = node.childNodes[0].data.strip()
                        try:
                            details['runtime'] = int(details['runtime'])
                        except:
                            details['runtime'] = 0
                    elif node.nodeName == 'Director' and len(node.childNodes) > 0:
                        details['director'] = node.childNodes[0].data.strip().replace('|', ', ')
                    elif node.nodeName == 'Writer' and len(node.childNodes) > 0:
                        details['screenplay'] = node.childNodes[0].data.strip().replace('|', ', ')
                    elif node.nodeName == 'Photographer' and len(node.childNodes) > 0:
                        details['cameraman'] = node.childNodes[0].data.strip().replace('|', ', ')
                    elif node.nodeName == 'Notes' and len(node.childNodes) > 0:
                        details['notes'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Plot' and len(node.childNodes) > 0:
                        details['plot'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Cover' and len(node.childNodes) > 0:
                        details['poster'] = os.path.join('images', node.childNodes[0].data.strip())
                    elif node.nodeName == 'Rating' and len(node.childNodes) > 0:
                        if not 'rating' in details:
                            try:
                                details['rating'] = int(node.childNodes[0].data)
                            except:
                                details['rating'] = 0
                    elif node.nodeName == 'PersonalRating' and len(node.childNodes) > 0:
                        try:
                            details['rating'] = int(node.childNodes[0].data)
                        except:
                            details['rating'] = 0
                    elif node.nodeName == 'Seen' and len(node.childNodes) > 0:
                        details['seen'] = (node.childNodes[0].data == 'True')
                    elif node.nodeName == 'Actors' and len(node.childNodes) > 0:
                        details['cast'] = ''
                        for actor in node.childNodes:
                            if actor.nodeType == Node.ELEMENT_NODE and actor.nodeName == 'Actor':
                                actorname = None
                                actorrole = None
                                for actorDetail in actor.childNodes:
                                    if actorDetail.nodeType == Node.ELEMENT_NODE and len(actorDetail.childNodes) > 0:
                                        if actorDetail.nodeName == 'ActorName':
                                            actorname = actorDetail.childNodes[0].data.strip()
                                        elif actorDetail.nodeName == 'ActorRole':
                                            actorrole = actorDetail.childNodes[0].data.strip()
                                if actorname:
                                    if actorrole:
                                        details['cast'] = details['cast'] + actorname + _(' as ') + actorrole + '\n'
                                    else:
                                        details['cast'] = details['cast'] + actorname + '\n'
                    elif node.nodeName == 'Disks' and len(node.childNodes) > 0:
                        try:
                            details['media_num'] = int(node.childNodes[0].data)
                        except:
                            pass
                    elif node.nodeName == 'Media' and len(node.childNodes) > 0:
                        details['medium_id'] = node.childNodes[0].data
                    elif node.nodeName == 'Color' and len(node.childNodes) > 0:
                        if node.childNodes[0].data == 'False':
                            details['color'] = 2
                        else:
                            details['color'] = 1
        except EOFError:
            details = None
        except Exception, e:
            log.exception('')
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
        self.clear()
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        self.filedom = minidom.parse(self.filename)
        try:
            collectionElement = self.filedom.getElementsByTagName('XMM_Movie_Database')[0]
            movieElements = collectionElement.childNodes
            for movieElement in movieElements:
                if movieElement.nodeType == Node.ELEMENT_NODE and movieElement.nodeName == 'Movie':
                    version = 6.0
                    for movieDetailElement in movieElement.childNodes:
                        if movieDetailElement.nodeType == Node.ELEMENT_NODE and movieDetailElement.nodeName == 'TVShow':
                            version = 7.0
                            break
                    if version == 7.0:
                        break
        except Exception, e:
            log.error(str(e))
            self.filedom.unlink()
            self.filedom = None
        log.info('eXtreme Movie Manager Import: Found file version %s' % version)
        return version
