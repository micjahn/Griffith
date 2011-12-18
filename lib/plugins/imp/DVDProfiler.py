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
    description  = 'DVD Profiler (v3.x)'
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
                collectionElement = self.filedom.getElementsByTagName('Collection')[0]
                for element in collectionElement.childNodes:
                    if element.nodeType == Node.ELEMENT_NODE and element.nodeName == 'DVD':
                        count = count + 1
                log.info('DVDProfiler Import: %s movies for import' % count)
            except:
                log.exception('')
        else:
            log.error('No filedom object.')
        return count

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        if not self.filedom:
            self.filedom = minidom.parse(self.filename)
        if not self.items:
            collectionElement = self.filedom.getElementsByTagName('Collection')[0]
            self.items = collectionElement.childNodes
            self.itemindex = 0
        if not self.items or len(self.items) < 1:
            return None
        if len(self.items) <= self.itemindex:
            return None
        item = self.items[self.itemindex]
        while not (item.nodeType == Node.ELEMENT_NODE and item.nodeName == 'DVD') and len(self.items) > self.itemindex + 1:
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
                    elif node.nodeName == 'ProductionYear' and len(node.childNodes) > 0:
                        details['year'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'RunningTime' and len(node.childNodes) > 0:
                        details['runtime'] = node.childNodes[0].data.strip()
                        try:
                            details['runtime'] = int(details['runtime'])
                        except:
                            details['runtime'] = 0
                    elif node.nodeName == 'Notes' and len(node.childNodes) > 0:
                        details['notes'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Overview' and len(node.childNodes) > 0:
                        details['plot'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Rating' and len(node.childNodes) > 0:
                        if 'classification' in details and details['classification']:
                            details['classification'] = node.childNodes[0].data.strip() + '-' + details['classification']
                        else:
                            details['classification'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'RatingAge' and len(node.childNodes) > 0:
                        if 'classification' in details and details['classification']:
                            details['classification'] = details['classification'] + '-' + node.childNodes[0].data.strip()
                        else:
                            details['classification'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Review':
                        if self.fileversion == 2.0:
                            reviewFilmElements = node.getElementsByTagName('ReviewFilm')
                            if len(reviewFilmElements) and len(reviewFilmElements[0].childNodes) > 0:
                                try:
                                    details['rating'] = int(reviewFilmElements[0].childNodes[0].data)
                                except:
                                    details['rating'] = 0
                        else:
                            try:
                                details['rating'] = int(node.getAttribute('Film'))
                            except:
                                details['rating'] = 0
                    elif node.nodeName == 'CountryOfOrigin' and len(node.childNodes) > 0:
                        details['country'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'Credits':
                        details['director'] = ''
                        details['cameraman'] = ''
                        details['screenplay'] = ''
                        creditElements = node.getElementsByTagName('Credit')
                        for creditElement in creditElements:
                            if self.fileversion == 2.0:
                                creditTypeElements = creditElement.getElementsByTagName('CreditType')
                                if len(creditTypeElements) and creditTypeElements[0].childNodes[0].data == 'Direction':
                                    firstNameElements = creditElement.getElementsByTagName('FirstName')
                                    lastNameElements = creditElement.getElementsByTagName('LastName')
                                    if len(firstNameElements) and len(firstNameElements[0].childNodes) > 0 and len(lastNameElements) and len(lastNameElements[0].childNodes) > 0:
                                        details['director'] = details['director'] + firstNameElements[0].childNodes[0].data.strip() + ' ' + lastNameElements[0].childNodes[0].data.strip() + ', '
                                    elif len(lastNameElements) and len(lastNameElements[0].childNodes) > 0:
                                        details['director'] = details['director'] + lastNameElements[0].childNodes[0].data.strip() + ', '
                                    elif len(firstNameElements) and len(firstNameElements[0].childNodes) > 0:
                                        details['director'] = details['director'] + firstNameElements[0].childNodes[0].data.strip() + ', '
                                elif len(creditTypeElements) and creditTypeElements[0].childNodes[0].data == 'Cinematography':
                                    firstNameElements = creditElement.getElementsByTagName('FirstName')
                                    lastNameElements = creditElement.getElementsByTagName('LastName')
                                    if len(firstNameElements) and len(firstNameElements[0].childNodes) > 0 and len(lastNameElements) and len(lastNameElements[0].childNodes) > 0:
                                        details['cameraman'] = details['cameraman'] + firstNameElements[0].childNodes[0].data.strip() + ' ' + lastNameElements[0].childNodes[0].data.strip() + ', '
                                    elif len(lastNameElements) and len(lastNameElements[0].childNodes) > 0:
                                        details['cameraman'] = details['cameraman'] + lastNameElements[0].childNodes[0].data.strip() + ', '
                                    elif len(firstNameElements) and len(firstNameElements[0].childNodes) > 0:
                                        details['cameraman'] = details['cameraman'] + firstNameElements[0].childNodes[0].data.strip() + ', '
                                elif len(creditTypeElements) and creditTypeElements[0].childNodes[0].data == 'Writing':
                                    firstNameElements = creditElement.getElementsByTagName('FirstName')
                                    lastNameElements = creditElement.getElementsByTagName('LastName')
                                    if len(firstNameElements) and len(firstNameElements[0].childNodes) > 0 and len(lastNameElements) and len(lastNameElements[0].childNodes) > 0:
                                        details['screenplay'] = details['screenplay'] + firstNameElements[0].childNodes[0].data.strip() + ' ' + lastNameElements[0].childNodes[0].data.strip() + ', '
                                    elif len(lastNameElements) and len(lastNameElements[0].childNodes) > 0:
                                        details['screenplay'] = details['screenplay'] + lastNameElements[0].childNodes[0].data.strip() + ', '
                                    elif len(firstNameElements) and len(firstNameElements[0].childNodes) > 0:
                                        details['screenplay'] = details['screenplay'] + firstNameElements[0].childNodes[0].data.strip() + ', '
                            else:
                                creditType = creditElement.getAttribute('CreditType')
                                creditSubtype = creditElement.getAttribute('CreditSubtype')
                                if creditType == 'Direction' and creditSubtype == 'Director':
                                    firstName = creditElement.getAttribute('FirstName').strip()
                                    lastName = creditElement.getAttribute('LastName').strip()
                                    if firstName and lastName:
                                        details['director'] = details['director'] + firstName + ' ' + lastName + ', '
                                    elif lastName:
                                        details['director'] = details['director'] + lastName + ', '
                                    elif firstName:
                                        details['director'] = details['director'] + firstName + ', '
                                elif creditType == 'Cinematography' and creditSubtype == 'Director of Photography':
                                    firstName = creditElement.getAttribute('FirstName').strip()
                                    lastName = creditElement.getAttribute('LastName').strip()
                                    if firstName and lastName:
                                        details['cameraman'] = details['cameraman'] + firstName + ' ' + lastName + ', '
                                    elif lastName:
                                        details['cameraman'] = details['cameraman'] + lastName + ', '
                                    elif firstName:
                                        details['cameraman'] = details['cameraman'] + firstName + ', '
                                elif creditType == 'Writing' and creditSubtype == 'Writer':
                                    firstName = creditElement.getAttribute('FirstName').strip()
                                    lastName = creditElement.getAttribute('LastName').strip()
                                    if firstName and lastName:
                                        details['screenplay'] = details['screenplay'] + firstName + ' ' + lastName + ', '
                                    elif lastName:
                                        details['screenplay'] = details['screenplay'] + lastName + ', '
                                    elif firstName:
                                        details['screenplay'] = details['screenplay'] + firstName + ', '
                        if len(details['director']) > 2:
                            details['director'] = details['director'][:-2]
                        if len(details['cameraman']) > 2:
                            details['cameraman'] = details['cameraman'][:-2]
                        if len(details['screenplay']) > 2:
                            details['screenplay'] = details['screenplay'][:-2]
                    elif node.nodeName == 'Actors':
                        details['cast'] = ''
                        actorElements = node.getElementsByTagName('Actor')
                        for actorElement in actorElements:
                            if self.fileversion == 2.0:
                                firstNameElements = actorElement.getElementsByTagName('FirstName')
                                lastNameElements = actorElement.getElementsByTagName('LastName')
                                roleElements = actorElement.getElementsByTagName('Role')
                                actor = ''
                                if len(firstNameElements) and len(firstNameElements[0].childNodes) > 0:
                                    actor = actor + firstNameElements[0].childNodes[0].data.strip() + ' '
                                if len(lastNameElements) and len(lastNameElements[0].childNodes) > 0:
                                    actor = actor + lastNameElements[0].childNodes[0].data.strip() + ' '
                                if len(roleElements) and len(roleElements[0].childNodes) > 0:
                                    if len(actor) > 1:
                                        actor = actor[:-1] + _(' as ') + roleElements[0].childNodes[0].data.strip()
                                    else:
                                        actor = actor + _(' as ') + roleElements[0].childNodes[0].data.strip()
                                elif len(actor) > 1:
                                    actor = actor[:-1]
                                if actor:
                                    details['cast'] = details['cast'] + actor + "\n"
                            else:
                                firstName = actorElement.getAttribute('FirstName').strip()
                                middleName = actorElement.getAttribute('MiddleName').strip()
                                lastName = actorElement.getAttribute('LastName').strip()
                                role = actorElement.getAttribute('Role').strip()
                                actor = ''
                                if firstName:
                                    actor = firstName + ' '
                                if middleName:
                                    actor = actor + middleName + ' '
                                if lastName:
                                    actor = actor + lastName + ' '
                                if role:
                                    if len(actor) > 1:
                                        actor = actor[:-1] + _(' as ') + role
                                    else:
                                        actor = actor + _(' as ') + role
                                elif len(actor) > 0:
                                    actor = actor[:-1]
                                if actor:
                                    details['cast'] = details['cast'] + actor + "\n"
                    elif node.nodeName == 'Genres':
                        details['genre'] = ''
                        genreElements = node.getElementsByTagName('Genre')
                        for genreElement in genreElements:
                            if len(genreElement.childNodes) > 0:
                                details['genre'] = details['genre'] + genreElement.childNodes[0].data.strip() + ', '
                        if details['genre'] > 2:
                            details['genre'] = details['genre'][:-2]
                    elif node.nodeName == 'Studios':
                        details['studio'] = ''
                        studioElements = node.getElementsByTagName('Studio')
                        for studioElement in studioElements:
                            if len(studioElement.childNodes) > 0:
                                details['studio'] = details['studio'] + studioElement.childNodes[0].data.strip() + ', '
                        if details['studio'] > 2:
                            details['studio'] = details['studio'][:-2]
                    elif node.nodeName == 'Regions':
                        regionElements = node.getElementsByTagName('Region')
                        for regionElement in regionElements:
                            if len(regionElement.childNodes) > 0:
                                try:
                                    details['region'] = int(regionElement.childNodes[0].data)
                                except:
                                    pass
                                break
                    elif node.nodeName == 'UPC' and len(node.childNodes) > 0:
                        details['barcode'] = node.childNodes[0].data.strip()
                    elif node.nodeName == 'MediaTypes':
                        for mediumnode in node.childNodes:
                            if mediumnode.nodeType == Node.ELEMENT_NODE:
                                if len(mediumnode.childNodes) > 0 and mediumnode.childNodes[0].data == 'True':
                                    # setting medium_id to string mediumname; mapping is done in base class
                                    details['medium_id'] = mediumnode.nodeName
                                    break
                    elif node.nodeName == 'Discs':
                        discElements = node.getElementsByTagName('Disc')
                        details['media_num'] = len(discElements)
                    elif node.nodeName == 'Tags':
                        tagElements = node.getElementsByTagName('Tag')
                        if len(tagElements):
                            details['tags'] = []
                            for tagElement in tagElements:
                                details['tags'].append(tagElement.getAttribute('Name').strip())
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
            collectionElement = self.filedom.getElementsByTagName('Collection')[0]
            dvdElements = collectionElement.childNodes
            for dvdElement in dvdElements:
                if dvdElement.nodeType == dvdElement.ELEMENT_NODE and dvdElement.nodeName == 'DVD':
                    actorsElements = dvdElement.getElementsByTagName('Actors')
                    if len(actorsElements):
                        actorElements = actorsElements[0].getElementsByTagName('Actor')
                        if len(actorElements):
                            if actorElements[0].hasAttribute('FirstName'):
                                version = 3.0
                            if len(actorElements[0].getElementsByTagName('FirstName')):
                                version = 2.0
                            break
        except Exception, e:
            log.error(str(e))
            self.filedom.unlink()
            self.filedom = None
        return version
