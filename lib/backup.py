# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski
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

import gettext
gettext.install('griffith', unicode=1)
import gtk
import os.path
import zipfile
import logging
log = logging.getLogger("Griffith")
import config
import edit
import gutils
import sql

def backup(self):
    """perform a compressed griffith database/posters/preferences backup"""
    filename = gutils.file_chooser(_("Save Griffith backup"), \
        action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons= \
        (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK), \
        name=self.config.get('name','griffith', section='database') + '_backup.zip')
    if filename and filename[0]:
        overwrite = None
        zipfilename = filename[0].decode('utf-8')
        if os.path.isfile(zipfilename):
            response = gutils.question(self, \
                _("File exists. Do you want to overwrite it?"), \
                1, self.widgets['window'])
            if response == -8:
                overwrite = True
            else:
                overwrite = False

        if overwrite == True or overwrite is None:
            try:
                if zipfile.zlib is not None:
                    mzip = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
                else:
                    mzip = zipfile.ZipFile(zipfilename, 'w')
            except:
                gutils.error(self, _("Error creating backup"), self.widgets['window'])
                return False
            mzip.write(os.path.join(self.locations['home'],'griffith.cfg').encode('utf-8'))
            if self.db.session.bind.engine.name == 'sqlite':
                fileName = os.path.join(self.locations['home'], self.config.get('name','griffith', section='database') + '.db').encode('utf-8')
                mzip.write(fileName)
            else:
                gutils.error(self, _("Backup function is available only for SQLite engine for now"), self.widgets['window'])
                return False
                from tempfile import mkdtemp
                from shutil import rmtree, move
                from sqlalchemy import BoundMetaData
                import copy
                # if backup_to_sqlite:
                tmp_dir = mkdtemp()
                tmp_config = copy.deepcopy(self.config)
                tmp_config._file = os.path.join(tmp_dir,'griffith.cfg')
                tmp_config.get('type', 'sqlite', section='database') == 'sqlite'
                tmp_config.set('file', section='database') == "griffith.db"
                tmp_config.save()

#                tmp_db = sql.GriffithSQL(tmp_config, tmp_dir)
#                for i in self.db.metadata.tables
#                tmp_db.

                tmp_file = os.path.join(tmp_dir, tmp_config.get('file', 'griffith.db', section='database')).encode('utf-8')
                tmp_metadata = BoundMetaData("sqlite:///%s" % tmp_file)
                tmp_metadata.tables = self.db.metadata.tables
                tmp_metadata.create_all()
#                for table in self.db.metadata.tables.keys():
                for table in [t.name for t in self.db.metadata.table_iterator()]: # table_iterator() will return tables in *correct* order
                    data = self.db.metadata.tables[table].select().execute().fetchall()
                    tmp_metadata.tables[table].insert().execute(data)
#                    for item in data:
#                        tmp_metadata.tables[table].insert().execute(item)
                tmp_metadata.engine.commit()
                
                mzip.write(tmp_file)
                rmtree(tmp_dir)
            posters_dir = os.path.join(self.locations['posters'])
            for movie in self.db.Movie.query.all():
                if movie.image is not None:
                    filename = str(movie.image)+".jpg"
                    filename = os.path.join(posters_dir, filename).encode('utf-8')
                    if os.path.isfile(filename):
                        try:
                            mzip.write(filename)
                        except:
                            log.info("Can't compress %s" % filename)
            mzip.close()
            gutils.info(_("Backup has been created"), self.widgets['window'])

def restore(self):
    """restores a griffith compressed backup"""
    filename = gutils.file_chooser(_("Restore Griffith backup"), \
        action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons= \
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    if filename[0]:
        try:
            zip = zipfile.ZipFile(filename[0], 'r')
        except:
            gutils.error(self, _("Can't read backup file"), self.widgets['window'])
            return False
        mypath = os.path.join(self.locations['posters'])
        old_config_file = False
        for each in zip.namelist():
            file_to_restore = os.path.split(each)
            if not os.path.isdir(file_to_restore[1]):
                if file_to_restore[1] == '':
                    continue
                if file_to_restore[1].endswith('.jpg'):
                    myfile = os.path.join(mypath,file_to_restore[1])
                else:
                    myfile = os.path.join(self.locations['home'],file_to_restore[1])
                if file_to_restore[1].endswith('.conf'):
                    old_config_file = myfile
                outfile = open(myfile, 'wb')
                outfile.write(zip.read(each))
                outfile.flush()
                outfile.close()
        zip.close()

        # restore config file
        self.config = config.Config(file=os.path.join(self.locations['home'],'griffith.cfg'))
        if old_config_file:
            log.info('Old config file detected. Please note that it will not be used.')
            f = open(old_config_file, 'r')
            old_config_raw_data = f.read()
            f.close()
            if old_config_raw_data.find('griffith.gri') >= -1:
                self.config.set('file', 'griffith.gri', section='database')

        filename = os.path.join(self.locations['home'], self.config.get('name', 'griffith', section='database') + '.db')

        self.db.session.bind.engine.dispose() # close DB

        # check if file needs conversion
        if self.config.get('file', 'griffith.db', section='database').lower().endswith('.gri'):
            log.info('Old database format detected. Converting...')
            from dbupgrade  import convert_from_old_db
            from initialize import location_posters
            if convert_from_old_db(self, filename, os.path.join(self.locations['home'], 'griffith.db')):
                self.config.save()
                location_posters(self.locations, self.config)
            else:
                log.error('Cant convert old database, exiting.')
                import sys
                sys.exit(4)

        self.db = sql.GriffithSQL(self.config, self.locations['home'], self.locations)
        from initialize import dictionaries, people_treeview
        dictionaries(self)
        people_treeview(self)
        # let's refresh the treeview
        self.clear_details()
        self.populate_treeview()
        gutils.info(_("Backup restored"), self.widgets['window'])

def merge(self):    # FIXME
    """
        Merge database from:
        * compressed backup
        * SQLite2 *.gri file
        * SQLite3 *.db file
    """
    filename = gutils.file_chooser(_("Restore Griffith backup"), \
        action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons= \
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
        gtk.STOCK_OPEN, gtk.RESPONSE_OK))[0]
    if filename:
        from tempfile import mkdtemp
        from shutil import rmtree, move

        #tmp_config={}
        #tmp_config.get('type', 'sqlite', section='database')

        if filename.lower().endswith('.zip'):
            tmp_dir = mkdtemp()
            try:
                zip = zipfile.ZipFile(filename, 'r')
            except:
                gutils.error(self, _("Can't read backup file"), self.widgets['window'])
                return False
            for each in zip.namelist():
                file_to_restore = os.path.split(each)
                if not os.path.isdir(file_to_restore[1]):
                    myfile = os.path.join(tmp_dir, file_to_restore[1])
                    outfile = open(myfile, 'wb')
                    outfile.write(zip.read(each))
                    outfile.flush()
                    outfile.close()
            # load stored database filename
            tmp_config = config.Config(file=os.path.join(tmp_dir,'griffith.conf'))
            filename = os.path.join(tmp_dir, tmp_config('name', 'griffith', section='database') + '.db')
            zip.close()

        # check if file needs conversion
        if filename.lower().endswith(".gri"):
            if os.path.isfile(filename) and  open(filename).readline()[:47] == "** This file contains an SQLite 2.1 database **":
                log.info("MERGE: SQLite2 database format detected. Converting...")
                if not self.db.convert_from_sqlite2(filename, os.path.join(tmp_dir, self.config.get('file', 'griffith.db', section='database'))):
                    log.info("MERGE: Can't convert database, aborting.")
                    return False
        tmp_dir, tmp_file = os.path.split(filename)
        self.config.get('file', tmp_file, section='database') 

        tmp_db = sql.GriffithSQL(tmp_config, tmp_dir, self.locations)

        merged=0
        movies = tmp_db.Movie.count()
        for movie in tmp_db.Movie.query.all():
            if self.db.Movie.query.filter_by(o_title=movie.o_title).first() is not None:
                continue
            t_movies = {}
            for column in movie.mapper.c.keys():
                t_movies[column] = eval("movie.%s"%column)

            # replace number with new one
            t_movies["number"] = gutils.find_next_available(self.db)

            # don't restore volume/collection/tag/language/loan data (it's dangerous)
            t_movies.pop('movie_id')
            t_movies.pop('loaned')
            t_movies.pop('volume_id')
            t_movies.pop('collection_id')

            if self.db.add_movie(t_movies):
                print t_movies

            if movie.image is not None:
                dest_file = os.path.join(self.locations['posters'], movie.image+'.jpg')
                if not os.path.isfile(dest_file):
                    src_file = os.path.join(tmp_dir, movie.image+'.jpg')
                    if os.path.isfile(src_file):
                        move(src_file, dest_file)
            merged+=1
        rmtree(tmp_dir)

        from initialize    import dictionaries, people_treeview
        dictionaries(self)
        people_treeview(self)
        # let's refresh the treeview
        self.clear_details()
        self.populate_treeview(self.db.Movie.query.all())
        #gutils.info(_("Databases merged!\n\nProcessed movies: %s\nMerged movies: %s"%(movies, merged)), self.widgets['window'])

