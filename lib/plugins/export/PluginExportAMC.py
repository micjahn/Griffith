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
import datetime
from plugins.export import XmlExportBase

class ExportPlugin(XmlExportBase):
    plugin_name         = "Ant Movie Catalog Database XML Export"
    plugin_description  = _("Full Ant Movie Catalog database xml export plugin")
    plugin_author       = "Michael Jahn"
    plugin_author_email = "griffith-private@lists.berlios.de"
    plugin_version      = "1.0"

    def __init__(self, database, locations, parent_window, search_conditions, config):
        XmlExportBase.__init__(self, database, locations, parent_window, search_conditions, config)
        self.config_section = 'export-antmovie'
        self.export_name    = 'Ant Movie Catalog database export'
        self.filename       = 'ant-movie-catalog.xml'
        self.encoding       = 'iso-8859-1'

    def export_to_document(self, document, mainelement):
        collelement = document.createElement('AntMovieCatalog')
        collelement.setAttribute('Format', '35')
        collelement.setAttribute('Version', '3.5.1 (2007-09-22)')
        collelement.setAttribute('Date', datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        document.appendChild(collelement)
        comment = document.createComment('Griffith Export in Ant Movie Catalog database format')
        document.insertBefore(comment, collelement)
        catalogelement = document.createElement('Catalog')
        collelement.appendChild(catalogelement)
        propertieselement = document.createElement('Properties')
        catalogelement.appendChild(propertieselement)
        contentselement = document.createElement('Contents')
        catalogelement.appendChild(contentselement)
        XmlExportBase.export_to_document(self, document, contentselement)

    def process_movie(self, document, mainelement, movie, keys):
        # create node
        itemelement = document.createElement('Movie')
        itemelement.setAttribute('Checked', 'False')
        mainelement.appendChild(itemelement)
        XmlExportBase.process_movie(self, document, itemelement, movie, keys)

    def process_movie_value(self, document, dvdelement, key, value):
        if key == 'movies_number':
            dvdelement.setAttribute('Number', value)
        elif key == 'movies_loaned':
            pass
        elif key == 'movies_seen':
            dvdelement.setAttribute('Checked', value)
        elif key == 'movies_rating':
            dvdelement.setAttribute('Rating', value)
        elif key == 'movies_color':             # SmallInteger
            pass
        elif key == 'movies_cond':              # SmallInteger
            pass
        elif key == 'movies_layers':            # SmallInteger
            pass
        elif key == 'movies_media_num':         # SmallInteger
            dvdelement.setAttribute('Disks', value)
        elif key == 'movies_runtime':           # Integer
            dvdelement.setAttribute('Length', value)
        elif key == 'movies_year':              # year
            dvdelement.setAttribute('Year', value)
        elif key == 'movies_o_title':           # VARCHAR
            dvdelement.setAttribute('OriginalTitle', value)
            dvdelement.setAttribute('FormattedTitle', value)
        elif key == 'movies_title':             # VARCHAR
            dvdelement.setAttribute('TranslatedTitle', value)
        elif key == 'movies_director':          # VARCHAR
            dvdelement.setAttribute('Director', value)
        elif key == 'movies_o_site':            # VARCHAR
            pass
        elif key == 'movies_site':              # VARCHAR
            dvdelement.setAttribute('URL', value)
        elif key == 'movies_trailer':           # VARCHAR
            pass
        elif key == 'movies_country':           # VARCHAR
            dvdelement.setAttribute('Country', value)
        elif key == 'movies_genre':             # VARCHAR
            dvdelement.setAttribute('Category', value.replace('\n', ''))
        elif key == 'movies_region':            # SmallInteger
            pass
        elif key == 'movies_studio':            # VARCHAR
            pass
        elif key == 'movies_classification':    # VARCHAR
            pass
        elif key == 'movies_cast':              # VARCHAR
            if len(value.strip()) > 0:
                actors = value.split('\n')
                actorsstring = ''
                delim = ''
                for actor in actors:
                    actorsplit = actor.split(_(' as '))
                    actornames = actorsplit[0]
                    if len(actorsplit) > 1:
                        actorsstring += delim + actornames.strip() + ' (' + actorsplit[1].strip() + ')'
                    else:
                        actorsstring += delim + actornames.strip()
                    delim = ', '
                dvdelement.setAttribute('Actors', actorsstring)
        elif key == 'movies_plot':              # VARCHAR
            dvdelement.setAttribute('Description', value.replace('\n', '|'))
        elif key == 'movies_notes':             # VARCHAR
            dvdelement.setAttribute('Comments', value.replace('\n', '|'))
        elif key == 'vcodecs_name':             # VARCHAR
            dvdelement.setAttribute('VideoFormat', value)

    def process_movie_image(self, document, dvdelement, imagedata, imagemd5sum):
        if imagemd5sum and imagedata:
            dvdelement.setAttribute('Picture', self.filename + '_pictures/' + imagemd5sum + '.jpg')
            self.save_image_to_file(imagedata, imagemd5sum, self.filename + '_pictures/')

    def process_movie_tags(self, document, movieelement, movie):
        pass

    def process_acodecs(self, document, movieelement, acodecsquery):
        acodecsstring = ''
        delim = ''
        codecsused = []
        for acodec in acodecsquery.execute().fetchall():
            if acodec['name'] not in codecsused:
                acodecsstring += delim + self.convert_value(acodec['name'])
                delim = ', '
                codecsused.append(acodec['name'])
        movieelement.setAttribute('AudioFormat', acodecsstring)
        
    def process_languages(self, document, movieelement, languagesquery):
        languagesstring = ''
        delim = ''
        languagesused = []
        for language in languagesquery.execute().fetchall():
            if language['languages_name'] not in languagesused:
                languagesstring += delim + self.convert_value(language['languages_name'])
                delim = ', '
                languagesused.append(language['languages_name'])
        movieelement.setAttribute('Languages', languagesstring)

    def process_subtitles(self, document, movieelement, subtitlesquery):
        subtitlesstring = ''
        delim = ''
        for subtitle in subtitlesquery.execute().fetchall():
            subtitlesstring += delim + self.convert_value(subtitle['name'])
            delim = ', '
        movieelement.setAttribute('Subtitles', subtitlesstring)
