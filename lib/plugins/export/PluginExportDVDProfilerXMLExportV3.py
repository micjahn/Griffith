# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2009 Michael Jahn
#
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

import xml.dom.minidom
import xml.dom.ext
from plugins.export import XmlExportBase

class ExportPlugin(XmlExportBase):
    plugin_name         = "DVD Profiler XML Export"
    plugin_description  = _("Full DVD Profiler XML Export V3 plugin")
    plugin_author       = "Michael Jahn"
    plugin_author_email = "griffith-private@lists.berlios.de"
    plugin_version      = "1.0"

    def __init__(self, database, locations, parent_window, search_conditions, config):
        XmlExportBase.__init__(self, database, locations, parent_window, search_conditions, config)
        self.config_section = 'export-dvdprofilerxml'
        self.export_name    = 'DVD Profiler XML Export V3'
        self.filename       = 'CollectionV3.xml'

    def export_to_document(self, document, mainelement):
        collelement = document.createElement('Collection')
        document.appendChild(collelement)
        comment = document.createComment('Griffith Export in DVD Profiler Collection Export Format V3')
        document.insertBefore(comment, collelement)
        XmlExportBase.export_to_document(self, document, collelement)

    def process_movie(self, document, mainelement, movie, keys):
        # create node
        dvdelement = document.createElement('DVD')
        mainelement.appendChild(dvdelement)
        tmpelem = document.createElement('ProfileTimestamp')
        dvdelement.appendChild(tmpelem)
        tmpelem = document.createElement('ID')
        dvdelement.appendChild(tmpelem)
        tmpelem = document.createElement('UPC')
        dvdelement.appendChild(tmpelem)
        XmlExportBase.process_movie(self, document, dvdelement, movie, keys)

    def process_movie_value(self, document, dvdelement, key, value):
        if key == 'movies_number':
            elem = document.createElement('CollectionNumber')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
            tmpelem = document.createElement('CollectionType')
            dvdelement.appendChild(tmpelem)
            t = document.createTextNode('Owned')
            tmpelem.appendChild(t)
        elif key == 'movies_loaned':
            loaninfoelem = document.createElement('LoanInfo')
            dvdelement.appendChild(loaninfoelem)
            loanedelem = document.createElement('Loaned')
            loaninfoelem.appendChild(loanedelem)
            t = document.createTextNode(value)
            loanedelem.appendChild(t)
        elif key == 'movies_seen':
            pass
        elif key == 'movies_rating':
            reviewelem = document.createElement('Review')
            dvdelement.appendChild(reviewelem)
            reviewelem.setAttribute('Film', value)
            reviewelem.setAttribute('Video', '0')
            reviewelem.setAttribute('Audio', '0')
            reviewelem.setAttribute('Extras', '0')
        elif key == 'movies_color':             # SmallInteger
            pass
        elif key == 'movies_cond':              # SmallInteger
            pass
        elif key == 'movies_layers':            # SmallInteger
            pass
        elif key == 'movies_media_num':         # SmallInteger
            pass
        elif key == 'movies_runtime':           # Integer
            elem = document.createElement('RunningTime')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_year':              # year
            elem = document.createElement('ProductionYear')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_o_title':           # VARCHAR
            elem = document.createElement('OriginalTitle')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_title':             # VARCHAR
            elem = document.createElement('Title')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_director':          # VARCHAR
            directors = value.split(',')
            directorselem = document.createElement('Credits')
            dvdelement.appendChild(directorselem)
            for director in directors:
                directorsplit = director.split(' ')
                firstname = ''
                lastname = ''
                if len(directorsplit) > 1:
                    firstname = directorsplit[0]
                    directorsplit.pop(0)
                    for directorname in directorsplit:
                        lastname = lastname + directorname + ' '
                directorelem = document.createElement('Credit')
                directorselem.appendChild(directorelem)
                directorelem.setAttribute('FirstName', firstname)
                directorelem.setAttribute('LastName', lastname)
                directorelem.setAttribute('BirthYear', '0')
                directorelem.setAttribute('CreditType', 'Direction')
                directorelem.setAttribute('CreditSubtype', 'Director')
                directorelem.setAttribute('CreditedAs', '')
        elif key == 'movies_o_site':            # VARCHAR
            pass
        elif key == 'movies_site':              # VARCHAR
            pass
        elif key == 'movies_trailer':           # VARCHAR
            pass
        elif key == 'movies_country':           # VARCHAR
            elem = document.createElement('CountryOfOrigin')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_genre':             # VARCHAR
            genres = value.split(',')
            genreselem = document.createElement('Genres')
            dvdelement.appendChild(genreselem)
            for genre in genres:
                genreelem = document.createElement('Genre')
                genreselem.appendChild(genreelem)
                t = document.createTextNode(genre.strip())
                genreelem.appendChild(t)
        elif key == 'movies_region':            # SmallInteger
            regionselem = document.createElement('Regions')
            dvdelement.appendChild(regionselem)
            regionelem = document.createElement('Region')
            regionselem.appendChild(regionelem)
            t = document.createTextNode(value)
            regionelem.appendChild(t)
        elif key == 'movies_image':             # VARCHAR
            pass
        elif key == 'movies_studio':            # VARCHAR
            studios = value.split(',')
            studioselem = document.createElement('Studios')
            dvdelement.appendChild(studioselem)
            for studio in studios:
                studioelem = document.createElement('Studio')
                studioselem.appendChild(studioelem)
                t = document.createTextNode(studio.strip())
                studioelem.appendChild(t)
        elif key == 'movies_classification':    # VARCHAR
            elem = document.createElement('Rating')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_cast':              # VARCHAR
            actors = value.split('\n')
            actorselem = document.createElement('Actors')
            dvdelement.appendChild(actorselem)
            for actor in actors:
                actorsplit = actor.split(_(' as '))
                actornames = actorsplit[0].split(' ')
                role = ''
                firstname = ''
                lastname = ''
                if len(actorsplit) > 1:
                    role = actorsplit[1]
                if len(actornames) > 1:
                    firstname = actornames[0]
                    actornames.pop(0)
                    for actorname in actornames:
                        lastname = lastname + actorname + ' '
                actorelem = document.createElement('Actor')
                actorselem.appendChild(actorelem)
                actorelem.setAttribute('FirstName', firstname)
                actorelem.setAttribute('LastName', lastname)
                actorelem.setAttribute('Role', role)
                actorelem.setAttribute('BirthYear', '0')
                actorelem.setAttribute('CreditedAs', '')
                actorelem.setAttribute('Voice', 'False')
                actorelem.setAttribute('Uncredited', 'False')
                actorelem.setAttribute('MiddleName', '')
        elif key == 'movies_plot':              # VARCHAR
            elem = document.createElement('Overview')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_notes':             # VARCHAR
            elem = document.createElement('Notes')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)

    def process_tags(self, document, dvdelement, tagsquery):
        tagselem = document.createElement('Tags')
        dvdelement.appendChild(tagselem)
        for tag in tagsquery.execute().fetchall():
            value = self.convert_value(tag['name'])
            tagelem = document.createElement('Tag')
            tagselem.appendChild(tagelem)
            tagelem.setAttribute('Name', value)
            tagelem.setAttribute('FullName', value)
