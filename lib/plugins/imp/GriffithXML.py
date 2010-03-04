# -*- coding: utf-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2010

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
    description  = 'Griffith XML'
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
                rootElement = self.filedom.getElementsByTagName('root')[0]
                for element in rootElement.childNodes:
                    if element.nodeType == Node.ELEMENT_NODE and element.nodeName == 'movie':
                        count = count + 1
                log.info('GriffithXML Import: %s movies for import' % count)
            except:
                log.exception('')
        else:
            log.error('GriffithXML Import: No filedom object.')
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.filedom:
            self.filedom = minidom.parse(self.filename)
        if not self.items:
            rootElement = self.filedom.getElementsByTagName('root')[0]
            self.items = rootElement.childNodes
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
                    if node.nodeName == 'number':
                        details['number'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'collection_id' or node.nodeName == 'collection_name':
                        details['collection_id'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'volume_id' or node.nodeName == 'volume_name':
                        details['volume_id'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'medium_id' or node.nodeName == 'medium_name':
                        details['medium_id'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'vcodec_id' or node.nodeName == 'vcodec_name':
                        details['vcodec_id'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'loaned':
                        details['loaned'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'seen':
                        details['seen'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'rating':
                        details['rating'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'color':
                        details['color'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'cond':
                        details['cond'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'layers':
                        details['layers'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'region':
                        details['region'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'media_num':
                        details['media_num'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'runtime':
                        details['runtime'] = node.childNodes[0].data.strip()
                        try:
                            details['runtime'] = int(details['runtime'])
                        except:
                            details['runtime'] = 0
                    elif node.nodeName == 'year':
                        details['year'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'o_title':
                        details['o_title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'title':
                        details['title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'director':
                        details['director'] = string.replace(node.childNodes[0].data.strip(), '\n', '')
                    elif node.nodeName == 'o_site':
                        details['o_site'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'site':
                        details['site'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'trailer':
                        details['trailer'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'country':
                        details['country'] = string.replace(node.childNodes[0].data.strip(), '\n', '')
                    elif node.nodeName == 'genre':
                        details['genre'] = string.replace(node.childNodes[0].data.strip(), '\n', '')
                    elif node.nodeName == 'image':
                        details['poster'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'studio':
                        details['studio'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'classification':
                        details['classification'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'cast':
                        details['cast'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'plot':
                        details['plot'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'notes':
                        details['notes'] = node.childNodes[0].data.strip()
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
            rootElement = self.filedom.getElementsByTagName('root')[0]
            movieElements = rootElement.getElementsByTagName('movie')
            version = 1.0
        except Exception, e:
            log.error(str(e))
            self.filedom.unlink()
            self.filedom = None
        return version
