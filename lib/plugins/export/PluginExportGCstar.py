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
import gutils
from plugins.export import XmlExportBase

class ExportPlugin(XmlExportBase):
    plugin_name         = "GCstar Database Export"
    plugin_description  = _("Full GCstar database export plugin")
    plugin_author       = "Michael Jahn"
    plugin_author_email = "griffith-private@lists.berlios.de"
    plugin_version      = "1.0"

    def __init__(self, database, locations, parent_window, search_conditions, config):
        XmlExportBase.__init__(self, database, locations, parent_window, search_conditions, config)
        self.config_section = 'export-gcstar'
        self.export_name    = 'GCstar database export'
        self.filename       = 'gcstar.xml'
        self.encoding       = 'utf-8'
        self.true_value     = '1'
        self.false_value    = '0'

    def export_to_document(self, document, mainelement):
        collelement = document.createElement('collection')
        collelement.setAttribute('type', 'GCfilms')
        document.appendChild(collelement)
        comment = document.createComment('Griffith Export in GCstar database format')
        document.insertBefore(comment, collelement)
        XmlExportBase.export_to_document(self, document, collelement)
        collelement.setAttribute('items', str(self.exported_movies))

    def process_movie(self, document, mainelement, movie, keys):
        # create node
        itemelement = document.createElement('item')
        itemelement.setAttribute('id', '')
        itemelement.setAttribute('title', '')
        itemelement.setAttribute('date', '')
        itemelement.setAttribute('time', '')
        itemelement.setAttribute('director', '')
        itemelement.setAttribute('country', '')
        itemelement.setAttribute('genre', '')
        itemelement.setAttribute('image', '')
        itemelement.setAttribute('actors', '')
        itemelement.setAttribute('original', '')
        itemelement.setAttribute('webPage', '')
        itemelement.setAttribute('seen', '')
        itemelement.setAttribute('added', '')
        itemelement.setAttribute('format', '')
        itemelement.setAttribute('number', '')
        itemelement.setAttribute('identifier', '')
        itemelement.setAttribute('place', '')
        itemelement.setAttribute('rating', '')
        itemelement.setAttribute('audio', '')
        itemelement.setAttribute('subt', '')
        itemelement.setAttribute('age', '')
        itemelement.setAttribute('video', '')
        itemelement.setAttribute('serie', '')
        itemelement.setAttribute('rank', '')
        itemelement.setAttribute('trailer', '')
        itemelement.setAttribute('borrower', '')
        itemelement.setAttribute('lendDate', '')
        itemelement.setAttribute('borrowings', '')
        itemelement.setAttribute('favourite', '')
        itemelement.setAttribute('tags', '')
        mainelement.appendChild(itemelement)
        XmlExportBase.process_movie(self, document, itemelement, movie, keys)
        if not itemelement.getAttribute('title'):
            itemelement.setAttribute('title', itemelement.getAttribute('original'))

    def process_movie_value(self, document, dvdelement, key, value):
        if key == 'movies_number':
            dvdelement.setAttribute('id', value)
        elif key == 'movies_loaned':
            pass
        elif key == 'movies_seen':
            dvdelement.setAttribute('seen', value)
        elif key == 'movies_rating':
            dvdelement.setAttribute('rating', value)
        elif key == 'movies_color':             # SmallInteger
            pass
        elif key == 'movies_cond':              # SmallInteger
            pass
        elif key == 'movies_layers':            # SmallInteger
            pass
        elif key == 'movies_media_num':         # SmallInteger
            dvdelement.setAttribute('number', value)
        elif key == 'movies_runtime':           # Integer
            dvdelement.setAttribute('time', value)
        elif key == 'movies_year':              # year
            dvdelement.setAttribute('date', value)
        elif key == 'movies_o_title':           # VARCHAR
            dvdelement.setAttribute('original', value)
        elif key == 'movies_title':             # VARCHAR
            dvdelement.setAttribute('title', value)
        elif key == 'movies_director':          # VARCHAR
            dvdelement.setAttribute('director', value)
        elif key == 'movies_o_site':            # VARCHAR
            pass
        elif key == 'movies_site':              # VARCHAR
            dvdelement.setAttribute('webPage', value)
        elif key == 'movies_trailer':           # VARCHAR
            if len(value.strip()) > 0:
                trailersplit = value.split('file://')
                if len(trailersplit) > 1:
                    if gutils.is_windows_system():
                        dvdelement.setAttribute('trailer', trailersplit[1].lstrip('/'))
                    else:
                        dvdelement.setAttribute('trailer', trailersplit[1])
                else:
                    dvdelement.setAttribute('trailer', trailersplit[0])
        elif key == 'movies_country':           # VARCHAR
            dvdelement.setAttribute('country', value)
        elif key == 'movies_genre':             # VARCHAR
            dvdelement.setAttribute('genre', value.replace('\n', ''))
        elif key == 'movies_region':            # SmallInteger
            pass
        elif key == 'movies_studio':            # VARCHAR
            pass
        elif key == 'movies_classification':    # VARCHAR
            dvdelement.setAttribute('age', str(gutils.digits_only(value)))
        elif key == 'movies_cast':              # VARCHAR
            if len(value.strip()) > 0:
                actors = value.split('\n')
                actorsstring = ''
                delim = ''
                for actor in actors:
                    actorsplit = actor.split(_(' as '))
                    actornames = actorsplit[0]
                    role = ''
                    if len(actorsplit) > 1:
                        role = actorsplit[1]
                    actorsstring += delim + actornames.strip() + ' (' + role.strip() + ')'
                    delim = ', '
                dvdelement.setAttribute('actors', actorsstring)
        elif key == 'movies_plot':              # VARCHAR
            elem = document.createElement('synopsis')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'movies_notes':             # VARCHAR
            elem = document.createElement('comment')
            dvdelement.appendChild(elem)
            t = document.createTextNode(value)
            elem.appendChild(t)
        elif key == 'volumes_name':             # VARCHAR
            dvdelement.setAttribute('place', value)
        elif key == 'collections_name':         # VARCHAR
            dvdelement.setAttribute('serie', value)
        elif key == 'vcodecs_name':             # VARCHAR
            dvdelement.setAttribute('video', value)
        elif key == 'media_name':               # VARCHAR
            dvdelement.setAttribute('format', value)

    def process_movie_image(self, document, dvdelement, imagedata, imagemd5sum):
        if imagemd5sum and imagedata:
            dvdelement.setAttribute('image', self.filename + '_pictures/' + imagemd5sum + '.jpg')
            self.save_image_to_file(imagedata, imagemd5sum, self.filename + '_pictures/')

    def process_tags(self, document, dvdelement, tagsquery):
        tagsstring = ''
        delim = ''
        for tag in tagsquery.execute().fetchall():
            tagsstring += delim + self.convert_value(tag['name'])
            delim = ','
        dvdelement.setAttribute('tags', tagsstring)

    def process_languages(self, document, movieelement, languagesquery):
        audioelement = None
        for language in languagesquery.execute().fetchall():
            if audioelement is None:
                audioelement = document.createElement('audio')
                movieelement.appendChild(audioelement)
            lineelement = document.createElement('line')
            audioelement.appendChild(lineelement)
            colelement = document.createElement('col')
            lineelement.appendChild(colelement)
            t = document.createTextNode(self.convert_value(language['languages_name']))
            colelement.appendChild(t)
            colelement = document.createElement('col')
            lineelement.appendChild(colelement)
            t = document.createTextNode(self.convert_value(language['acodecs_name']))
            colelement.appendChild(t)

    def process_subtitles(self, document, movieelement, subtitlesquery):
        # process movie subtitles by query
        subtelement = None
        for subtitle in subtitlesquery.execute().fetchall():
            if subtelement is None:
                subtelement = document.createElement('subt')
                movieelement.appendChild(subtelement)
            lineelement = document.createElement('line')
            subtelement.appendChild(lineelement)
            colelement = document.createElement('col')
            lineelement.appendChild(colelement)
            t = document.createTextNode(self.convert_value(subtitle['name']))
            colelement.appendChild(t)
