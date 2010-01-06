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
from xml.dom import minidom, Node

import logging
log = logging.getLogger("Griffith")


class ImportPlugin(IP):
    description  = 'Personal Video Database (v0.9.9.x)'
    author       = 'Michael Jahn'
    email        = 'griffith-private@lists.berlios.de'
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
                xmlElement = self.filedom.getElementsByTagName('xml')[0]
                for element in xmlElement.childNodes:
                    if element.nodeType == Node.ELEMENT_NODE and element.nodeName == 'viddb':
                        for viddbElement in element.childNodes:
                            if viddbElement.nodeType == Node.ELEMENT_NODE and viddbElement.nodeName == 'movies':
                                count = int(viddbElement.childNodes[0].data.strip())
                                break
                        break
            except:
                log.exception('')
        else:
            log.error('Personal Video Database Import: No filedom object.')
        log.info('Personal Video Database Import: %s movies for import' % count)
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.filedom:
            self.filedom = minidom.parse(self.filename)
        if not self.items:
            xmlElement = self.filedom.getElementsByTagName('xml')[0]
            viddbElement = self.filedom.getElementsByTagName('viddb')[0]
            self.items = viddbElement.childNodes
            self.itemindex = 0
        if not self.items or len(self.items) < 1:
            return None
        if len(self.items) <= self.itemindex:
            return None
        item = self.items[self.itemindex]
        while not (item.nodeType == Node.ELEMENT_NODE and item.nodeName == 'movie') and len(self.items) > self.itemindex + 1:
            self.itemindex = self.itemindex + 1
            item = self.items[self.itemindex]
        if len(self.items) <= self.itemindex:
            return None
        if not len(item.childNodes):
            return None

        details = {}
        try:
            for node in item.childNodes:
                if node.nodeType == Node.ELEMENT_NODE and len(node.childNodes) > 0:
                    if node.nodeName == 'title':
                        details['title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'origtitle':
                        details['o_title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'year':
                        details['year'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'genre':
                        details['genre'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'country':
                        details['country'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'studio':
                        details['studio'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'director':
                        details['director'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'actors':
                        details['cast'] = string.replace(node.childNodes[0].data.strip(), ', ', '\n')
                    elif node.nodeName == 'description':
                        details['plot'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'length':
                        details['runtime'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'type':
                        # setting medium_id to string mediumname; mapping is done in base class
                        details['medium_id'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'count':
                        details['media_num'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'videocodec':
                        # setting vcodec_id to string codecname; mapping is done in base class
                        details['vcodec_id'] = node.childNodes[0].data
                    elif node.nodeName == 'comment':
                        details['notes'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'mpaa':
                        details['classification'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'scenario':
                        details['screenplay'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'tags':
                        details['tags'] = string.split(node.childNodes[0].data.strip(), ', ')
                    elif node.nodeName == 'url':
                        details['o_site'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'path':
                        details['trailer'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'barcode':
                        details['barcode'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'poster':
                        details['poster'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'num':
                        details['number'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'rating':
                        try:
                            details['rating'] = round(float(node.childNodes[0].data.strip().replace(',', '.')), 0)
                        except:
                            pass
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
        IP.destroy(self)

    def read_fileversion(self):
        version = None
        self.filedom = minidom.parse(self.filename)
        try:
            xmlElement = self.filedom.getElementsByTagName('xml')[0]
            viddbElement = self.filedom.getElementsByTagName('viddb')[0]
            version = 0.9
        except Exception, e:
            log.error(str(e))
            self.filedom.unlink()
            self.filedom = None
        log.info('Personal Video Database Import: Found file version %s' % version)
        return version
