# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2008-2009 Piotr Ożarowski
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published byp
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

import glob
import os.path
import gutils
import gtk
import xml.dom.minidom
import xml.dom.ext
import os

import logging
log = logging.getLogger("Griffith.%s" % __name__)

from sqlalchemy import select, join, outerjoin, and_, or_
import db
from sql import update_whereclause

# detect all plugins:
__all__ = [os.path.basename(x)[:-3] for x in glob.glob("%s/PluginExport*.py" % os.path.dirname(__file__))]

class Base(object):
    description = None
    author = None
    email = None
    version = None
    fields_to_export = ('number', 'o_title', 'title', 'director', 'year')

    def __init__(self, database, locations, parent_window, search_conditions, config):
        self.db = database
        self.config = config
        self.locations = locations
        self.parent_window = parent_window
        self.search_conditions = search_conditions
    
    def initialize(self):
        """Initializes plugin (get all parameters from user, etc.)"""
        return True

    def cleanup(self):
        pass

    def run(self):
        raise NotImplemented
    
    def get_query(self):
        t = db.metadata.tables
        tables = set()
        columns = []

        for i in self.fields_to_export:
            table = 'movies'
            column = i.split('.')
            if len(column) > 1:
                table = column[0]
                column = column[1]
                if table not in t:
                    log.warning("Wrong table name: %s", table)
                    continue
                tables.add(table) # will be used to generate JOIN
            else:
                column = column[0]

            if column in t[table].columns:
                columns.append(t[table].columns[column])
            else:
                log.warning("Wrong field name: %s", i)

        joins = []
        if 'media' in tables:
            joins.append((t['media'], t['movies'].c.medium_id==t['media'].c.medium_id))
        if 'collections' in tables:
            joins.append((t['collections'], t['movies'].c.collection_id==t['collections'].c.collection_id))
        if 'volumes' in tables:
            joins.append((t['volumes'], t['movies'].c.volume_id==t['volumes'].c.volume_id))
        if 'vcodecs' in tables:
            joins.append((t['vcodecs'], t['movies'].c.vcodec_id==t['vcodecs'].c.vcodec_id))

        if joins:
            from_obj = [ outerjoin(t['movies'], *(joins[0])) ]
            for j in joins[1:]:
                from_obj.append(outerjoin(from_obj[-1], *j))
            query = select(columns=columns, bind=self.db.session.bind, from_obj=from_obj, use_labels=True)
        else:
            query = select(columns=columns, bind=self.db.session.bind)

        query = update_whereclause(query, self.search_conditions)

        # save column names (will contain 'movies_title' or 'title' depending on how many tables were requested)
        self.exported_columns = query.columns

        return query

class XmlExportBase(Base):

    def __init__(self, database, locations, parent_window, search_conditions, config):
        self.db              = database
        self.locations       = locations
        self.parent          = parent_window
        self.config_section  = None
        self.export_name     = ''
        self.filepath        = ''
        self.dirpath         = ''
        self.filename        = 'export.xml'
        self.encoding        = 'windows-1252'
        self.exported_movies = 0
        self.true_value      = 'True'
        self.false_value     = 'False'
        self.config          = config

    def run(self):
        if self.show_dialog() == True:
            # create xml document
            impl = xml.dom.minidom.getDOMImplementation()
            doc  = impl.createDocument(None, None, None)
            self.export_to_document(doc, doc.documentElement)
            # write xml document to file
            self.export_document_to_file(doc, self.filepath)
            gutils.info(_('%s file has been created.') % self.export_name, self.parent)

    def show_dialog(self):
        # shows a file dialog and sets self.filepath
        # derived classes which overwrite this method have also to set self.filepath
        basedir = None
        if not self.config is None and not self.config_section is None:
            basedir = self.config.get('export_dir', None, section=self.config_section)
        if basedir is None:
            filenames = gutils.file_chooser(_('Export a %s document') % self.export_name, action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), name=self.filename)
        else:
            filenames = gutils.file_chooser(_('Export a %s document') % self.export_name, action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK), name=self.filename, folder=basedir)
        if filenames[0]:
            self.filepath = filenames[0]
            if len(filenames) > 1:
                self.dirpath = filenames[1]
            else:
                self.dirpath = os.path.dirname(self.filepath)
            self.filename = os.path.basename(self.filepath)
            if not self.config is None and self.dirpath and not self.config_section is None:
                self.config.set('export_dir', self.dirpath, section=self.config_section)
                self.config.save()
            overwrite = None
            if os.path.isfile(self.filepath):
                response = gutils.question(_('File exists. Do you want to overwrite it?'), 1, self.parent)
                if response==-8:
                    overwrite = True
                else:
                    overwrite = False
                    
            if overwrite == True or overwrite is None:
                return True
        return False

    def export_document_to_file(self, document, filename):
        # write XML to file
        fp = open(filename, 'w')
        xml.dom.ext.PrettyPrint(document, fp, encoding=self.encoding)
        fp.close()

    def export_to_document(self, document, mainelement):
        table_movies = db.metadata.tables['movies']
        # create object
        columns = [table_movies.c.movie_id, table_movies.c.number,
            table_movies.c.title, table_movies.c.o_title,
            table_movies.c.country, table_movies.c.year,
            table_movies.c.runtime, table_movies.c.classification,
            table_movies.c.genre, table_movies.c.region, table_movies.c.studio,
            table_movies.c.cast, table_movies.c.director,
            table_movies.c.plot, table_movies.c.notes,
            table_movies.c.loaned, table_movies.c.rating,
            table_movies.c.trailer, table_movies.c.image,
            table_movies.c.seen, table_movies.c.media_num,
            table_movies.c.poster_md5, table_movies.c.screenplay,
            table_movies.c.cameraman, table_movies.c.barcode]
        # use outer join to media table to get the name of the media
        columns.append(db.metadata.tables['media'].c.name)
        media_join = outerjoin(db.metadata.tables['movies'], \
            db.metadata.tables['media'], \
            db.metadata.tables['movies'].c.medium_id==db.metadata.tables['media'].c.medium_id)
        # use outer join to collections table to get the name of the collection
        columns.append(db.metadata.tables['collections'].c.name)
        collection_join = media_join.outerjoin( \
            db.metadata.tables['collections'], \
            db.metadata.tables['movies'].c.collection_id==db.metadata.tables['collections'].c.collection_id)
        # use outer join to volumes table to get the name of the volume
        columns.append(db.metadata.tables['volumes'].c.name)
        volume_join = collection_join.outerjoin( \
            db.metadata.tables['volumes'], \
            db.metadata.tables['movies'].c.volume_id==db.metadata.tables['volumes'].c.volume_id)
        # use outer join to volumes table to get the name of the video codec
        columns.append(db.metadata.tables['vcodecs'].c.name)
        vcodec_join = volume_join.outerjoin( \
            db.metadata.tables['vcodecs'], \
            db.metadata.tables['movies'].c.vcodec_id==db.metadata.tables['vcodecs'].c.vcodec_id)
        # use outer join to posters table to get the poster image
        columns.append(db.metadata.tables['posters'].c.data)
        posters_join = vcodec_join.outerjoin( \
            db.metadata.tables['posters'], \
            db.metadata.tables['movies'].c.poster_md5==db.metadata.tables['posters'].c.md5sum)
        # fetch movie data
        moviesquery = select(columns=columns, from_obj=[media_join, collection_join, volume_join, vcodec_join, posters_join], bind=self.db.session.bind, use_labels = True)
        self.process_movies(document, mainelement, moviesquery)

    def process_movies(self, document, mainelement, moviesquery):
        # process all movies by query
        self.exported_movies = 0
        keys = moviesquery.c.keys
        for movie in moviesquery.execute().fetchall():
            self.process_movie(document, mainelement, movie, keys)
            self.exported_movies += 1

    def process_movie(self, document, movieelement, movie, keys):
        # process the movie itself
        self.process_movie_values(document, movieelement, movie, keys)
        # process tags
        self.process_movie_tags(document, movieelement, movie)
        # process audio codecs
        self.process_movie_acodecs(document, movieelement, movie)
        # process languages
        self.process_movie_languages(document, movieelement, movie)
        # process subtitles
        self.process_movie_subtitles(document, movieelement, movie)

    def process_movie_values(self, document, movieelement, movie, keys):
        # process movie properties by key
        for key in keys():
            if not key == 'posters_data':
                value = self.convert_value(movie[key])
                self.process_movie_value(document, movieelement, key, value)
        self.process_movie_image(document, movieelement, movie['posters_data'], movie['movies_poster_md5'])

    def process_movie_value(self, document, movieelement, key, value):
        pass

    def process_movie_image(self, document, movieelement, imagedata, imagemd5sum):
        pass

    #
    # export movie tags
    #
    def process_movie_tags(self, document, movieelement, movie):
        # build query for movie tags processing
        tagsquerycolumns = [db.metadata.tables['movie_tag'].c.movie_id,
            db.metadata.tables['movie_tag'].c.tag_id,
            db.metadata.tables['tags'].c.name]
        tag_join = join(db.metadata.tables['movie_tag'], \
            db.metadata.tables['tags'], \
            db.metadata.tables['movie_tag'].c.tag_id==db.metadata.tables['tags'].c.tag_id)
        tagsquery = select(\
            bind=self.db.session.bind, \
            columns = tagsquerycolumns, \
            from_obj = [tag_join], \
            whereclause = db.metadata.tables['movie_tag'].c.movie_id==movie['movies_movie_id'])
        self.process_tags(document, movieelement, tagsquery)
        
    def process_tags(self, document, movieelement, tagsquery):
        # process movie tags by query
        pass

    #
    # export movie audio codecs
    #
    def process_movie_acodecs(self, document, movieelement, movie):
        # build query for audio codec processing
        acodecscolumns = [db.metadata.tables['movie_lang'].c.movie_id,
            db.metadata.tables['movie_lang'].c.type,
            db.metadata.tables['movie_lang'].c.acodec_id,
            db.metadata.tables['acodecs'].c.name]
        acodec_join = join(db.metadata.tables['movie_lang'], \
            db.metadata.tables['acodecs'], \
            db.metadata.tables['movie_lang'].c.acodec_id==db.metadata.tables['acodecs'].c.acodec_id)
        acodecsquery = select(\
            bind=self.db.session.bind, \
            columns = acodecscolumns, \
            from_obj = [acodec_join], \
            whereclause = db.metadata.tables['movie_lang'].c.movie_id==movie['movies_movie_id'])
        self.process_acodecs(document, movieelement, acodecsquery)
        
    def process_acodecs(self, document, movieelement, acodecs):
        # process audio codecs by query
        pass

    #
    # export movie languages
    #
    def process_movie_languages(self, document, movieelement, movie):
        # build query for movie languages processing
        languagecolumns = [db.metadata.tables['movie_lang'].c.movie_id,
            db.metadata.tables['movie_lang'].c.type,
            db.metadata.tables['movie_lang'].c.lang_id,
            db.metadata.tables['movie_lang'].c.acodec_id,
            db.metadata.tables['languages'].c.name,
            db.metadata.tables['acodecs'].c.name]
        language_join = join(db.metadata.tables['movie_lang'], \
            db.metadata.tables['languages'], \
            db.metadata.tables['movie_lang'].c.lang_id==db.metadata.tables['languages'].c.lang_id)
        acodec_join = language_join.join( \
            db.metadata.tables['acodecs'], \
            db.metadata.tables['movie_lang'].c.acodec_id==db.metadata.tables['acodecs'].c.acodec_id)
        languagesquery = select(\
            bind=self.db.session.bind, \
            columns = languagecolumns, \
            from_obj = [language_join, acodec_join], \
            whereclause = and_(db.metadata.tables['movie_lang'].c.movie_id==movie['movies_movie_id'], \
                or_(db.metadata.tables['movie_lang'].c.type==0, or_(db.metadata.tables['movie_lang'].c.type==2, db.metadata.tables['movie_lang'].c.type==None))), \
            use_labels = True)
        self.process_languages(document, movieelement, languagesquery)
        
    def process_languages(self, document, movieelement, languages):
        # process movie languages by query
        pass

    #
    # export movie subtitles
    #
    def process_movie_subtitles(self, document, movieelement, movie):
        # build query for movie subtitles processing
        languagescolumns = [db.metadata.tables['movie_lang'].c.movie_id,
            db.metadata.tables['movie_lang'].c.type,
            db.metadata.tables['movie_lang'].c.lang_id,
            db.metadata.tables['languages'].c.name]
        language_join = join(db.metadata.tables['movie_lang'], \
            db.metadata.tables['languages'], \
            db.metadata.tables['movie_lang'].c.lang_id==db.metadata.tables['languages'].c.lang_id)
        languagesquery = select(\
            bind=self.db.session.bind, \
            columns = languagescolumns, \
            from_obj = [language_join], \
            whereclause = and_(db.metadata.tables['movie_lang'].c.movie_id==movie['movies_movie_id'], db.metadata.tables['movie_lang'].c.type==3))
        self.process_subtitles(document, movieelement, languagesquery)
        
    def process_subtitles(self, document, movieelement, subtitlesquery):
        # process movie subtitles by query
        pass

    #
    # helper methods
    #

    def save_image_to_file(self, imagedata, imagebasename, destinationdir):
        # save image image to destination directory
        # build absolute path from current export directory if necessary
        # create picture directory if necessary
        if not os.path.isabs(destinationdir):
            dst_directory = os.path.abspath(os.path.join(self.dirpath, destinationdir))
        else:
            dst_directory = os.path.abspath(destinationdir)
        if not os.path.exists(dst_directory):
            try:
                os.mkdir(dst_directory)
            except:
                log.error("Can't create %s" % dst_directory)
        dst_filename = os.path.join(dst_directory, imagebasename + '.jpg')
        try:
            f = file(dst_filename, 'wb')
            try:
                f.write(imagedata)
            finally:
                f.close()
        except:
            log.error("Can't save image data to %s" % dst_filename)

    def convert_value(self, value):
        if value is None:
            result = ''
        elif value is True:
            result = self.true_value
        elif value is False:
            result = self.false_value
        else:
            try:
                result = str(value).encode(self.encoding).decode(self.encoding)
            except:
                log.error('Can''t convert value ' + value + ' to codepage ' + self.encoding + '.')
                result = ''
        return result
