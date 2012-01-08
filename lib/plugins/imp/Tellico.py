# -*- coding: utf-8 -*-

__revision__ = '$Id: $'

# Copyright (c) 2011, 2012

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
from xml.dom import minidom, Node
import zipfile
from shutil import rmtree
from tempfile import mkdtemp

import logging
log = logging.getLogger("Griffith")


class ImportPlugin(IP):
    description  = 'Tellico'
    author       = 'Elan Ruusamäe'
    email        = 'glen@delfi.ee'
    version      = '1.1'
    file_filters = '*.[tT][cC]'
    mime_types   = None

    fileversion  = None
    filedom      = None
    items        = None
    itemindex    = 0
    zipdir       = None

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
                for element in collectionElement.childNodes:
                    if element.nodeType == Node.ELEMENT_NODE and element.nodeName == 'entry':
                        count = count + 1
                log.info('Tellico Import: %s movies for import' % count)
            except:
                log.exception('')
        else:
            log.error('Tellico Import: No filedom object.')
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.filedom:
            log.error('Tellico Import: filedom not open')
            return None

        if not self.items:
            collectionElement = self.filedom.getElementsByTagName('collection')[0]
            self.items = collectionElement.childNodes
            self.itemindex = 0
        if not self.items or len(self.items) < 1:
            return None
        if len(self.items) <= self.itemindex:
            return None
        item = self.items[self.itemindex]
        while not (item.nodeType == Node.ELEMENT_NODE and item.nodeName == 'entry') and len(self.items) > self.itemindex + 1:
            self.itemindex = self.itemindex + 1
            item = self.items[self.itemindex]
        if len(self.items) <= self.itemindex:
            return None
        if not len(item.childNodes):
            return None

        details = {}
        try:
            details['number'] = item.getAttribute('id')
            for node in item.childNodes:
                if node.nodeType == Node.ELEMENT_NODE and len(node.childNodes) > 0:
                    if node.nodeName == 'color':
                        value = node.childNodes[0].data.strip()
                        if value == 'Color':
                            details['color'] = 1
                        elif value == 'Black & White':
                            details['color'] = 2
                    elif node.nodeName == 'region':
                        details['region'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'running-time':
                        details['runtime'] = node.childNodes[0].data.strip()
                        try:
                            details['runtime'] = int(details['runtime'])
                        except:
                            details['runtime'] = 0
                    elif node.nodeName == 'year':
                        details['year'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'orig-title':
                        details['o_title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'title':
                        details['title'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'directors':
                        details['director'] = self._joinXmlNodes(node.getElementsByTagName('director'))
                    elif node.nodeName == 'writers':
                        details['screenplay'] = self._joinXmlNodes(node.getElementsByTagName('writer'))
                    elif node.nodeName == 'o_site':
                        details['o_site'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'url':
                        details['site'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'nationalitys':
                        details['country'] = self._joinXmlNodes(node.getElementsByTagName('nationality'))
                    elif node.nodeName == 'genres':
                        details['genre'] = self._joinXmlNodes(node.getElementsByTagName('genre'))
                    elif node.nodeName == 'certification':
                        details['classification'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'casts':
                        details['cast'] = self._joinCastNodes(node.getElementsByTagName('cast'), separator = "\n")
                    elif node.nodeName == 'plot':
                        details['plot'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'comments':
                        details['notes'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'cover':
                        imgfile = node.childNodes[0].data.strip()
                        # use 'image' field, 'poster' field is buggy, bug #913283
                        # https://bugs.launchpad.net/griffith/+bug/913283
                        details['image'] = os.path.join(self.zipdir, 'images', imgfile)
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
            rmtree(self.zipdir)
            self.zipdir = None
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
        try:
            self.zipdir = self._extractZip(self.filename)
            self.filedom = minidom.parse(os.path.join(self.zipdir, 'tellico.xml'))
            rootElement = self.filedom.getElementsByTagName('tellico')[0]
            version = rootElement.getAttribute('syntaxVersion')
        except Exception, e:
            log.error(str(e))
            if self.filedom:
                self.filedom.unlink()
                self.filedom = None
        log.info('Tellico: Found file version %s' % version)
        return version

    def _extractZip(self, filename):
        zf = zipfile.ZipFile(filename, 'r')
        tmpdir = mkdtemp(prefix = 'griffit2tellico')
        zf.extractall(path = tmpdir)
        return tmpdir

    def _joinXmlNodes(self, elements, separator = ', '):
        ret = ''
        for element in elements:
            if len(element.childNodes) > 0:
                ret = ret + element.childNodes[0].data.strip() + separator

        # chop off last separator
        if len(elements) > 0:
            ret = ret[:-len(separator)]
        return ret

    # join nodes for cast
    def _joinCastNodes(self, elements, separator = ', '):
        """
        we assume that this format:
            <cast>
            <column>Actor/Actress</column>
            <column>Role</column>
            </cast>

        ideally the columns likely came from header, which may differ:
            <field flags="3" title="Cast" category="Cast" format="2" type="8" name="cast" description="...">
                <prop name="column1" >Actor/Actress</prop>
                <prop name="column2" >Role</prop>
                <prop name="columns" >2</prop>
            </field>
        """

        ret = ''
        for element in elements:
            actor = None
            columns = element.getElementsByTagName('column')
            actor = columns[0].childNodes[0].data.strip()
            if len(columns) > 1 and len(columns[1].childNodes) > 0:
                actor = actor + _(' as ') + columns[1].childNodes[0].data.strip()

            if actor:
                ret = ret + actor + separator

        # chop off last separator
        if len(elements) > 0:
            ret = ret[:-len(separator)]

        return ret
