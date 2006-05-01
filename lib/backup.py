# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import config
import edit
import gtk
import gutils
import os.path
import sql
import zipfile

def backup(self):
	"""perform a compressed griffith database/posters/preferences backup"""
	filename = gutils.file_chooser(_("Save Griffith backup"), \
		action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons= \
		(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK), \
		name='griffith_backup.zip')
	if filename[0]:
		overwrite = None
		if os.path.isfile(filename[0]):
			response = gutils.question(self, \
				_("File exists. Do you want to overwrite it?"), \
				1, self.main_window)
			if response == -8:
				overwrite = True
			else:
				overwrite = False
				
		if overwrite == True or overwrite == None:
			try:
				mzip = zipfile.ZipFile(filename[0], 'w')
			except:
				gutils.error(self, _("Error creating backup"), self.main_window)
				return False
			mzip.write(os.path.join(self.griffith_dir, self.config["default_db"]))
			mzip.write(os.path.join(self.griffith_dir,'griffith.conf'))
			tmp_path=os.path.join(self.griffith_dir,'posters')
			for movie in self.db.Movie.select():
				if movie.image != None:
					filename = str(movie.image)+".jpg"
					filename = os.path.join(tmp_path, filename.encode('utf-8'))
					if os.path.isfile(filename):
						try:
							mzip.write(filename)
						except:
							self.debug.show("Can't compress %s" % filename)
			mzip.close()
			gutils.info(self, _("Backup has been created"), self.main_window)
	
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
			gutils.error(self, _("Can't read backup file"), self.main_window)
			return False
		mypath = os.path.join(self.griffith_dir,'posters')
		for each in zip.namelist():
			file_to_restore = os.path.split(each)
			if not os.path.isdir(file_to_restore[1]):
				if file_to_restore[1].endswith('.jpg'):
					myfile = os.path.join(mypath,file_to_restore[1])
				else:
					myfile = os.path.join(self.griffith_dir,file_to_restore[1])
				outfile = open(myfile, 'wb')
				outfile.write(zip.read(each))
				outfile.flush()
				outfile.close()
		zip.close()

		# restore config file
		old_default_db = self.config["default_db"]
		self.config = config.Config(file=os.path.join(self.griffith_dir,'griffith.conf'))
		filename = os.path.join(self.griffith_dir, self.config["default_db"])
		self.config["default_db"] = old_default_db
		self.config.save()

		# check if file needs conversion
		if os.path.isfile(filename) and  open(filename).readline()[:47] == "** This file contains an SQLite 2.1 database **":
			self.debug.show("RESTORE: SQLite2 database format detected. Converting...")
			if not self.db.convert_from_sqlite2(filename, os.path.join(self.griffith_dir, self.config["default_db"])):
				self.debug.show("RESTORE: Can't convert database, aborting.")
				return False

		self.db.conn.Close()
		self.db = sql.GriffithSQL(self.config, self.debug, self.griffith_dir)
		from initialize	import dictionaries, people_treeview
		dictionaries(self)
		people_treeview(self)
		# let's refresh the treeview
		self.clear_details()
		self.populate_treeview(self.db.get_all_data(order_by="number ASC"))
		self.total = self.db.count_records("movies")
		self.select_last_row(self.total)
		self.treeview_clicked()
		self.count_statusbar()
		gutils.info(self, _("Backup restored"), self.main_window)

def merge(self):
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
		
		tmp_dir = mkdtemp()
		tmp_config={}
		tmp_config["db_type"] = "sqlite"

		if filename.endswith('.zip'):
			try:
				zip = zipfile.ZipFile(filename, 'r')
			except:
				gutils.error(self, _("Can't read backup file"), self.main_window)
				return False
			for each in zip.namelist():
				file_to_restore = os.path.split(each)
				if not os.path.isdir(file_to_restore[1]):
					myfile = os.path.join(tmp_dir,file_to_restore[1])
					outfile = open(myfile, 'wb')
					outfile.write(zip.read(each))
					outfile.flush()
					outfile.close()
			# load stored database filename
			tmp_config = config.Config(file=os.path.join(tmp_dir,'griffith.conf'))
			filename = os.path.join(tmp_dir,tmp_config["default_db"])
			zip.close()

		# check if file needs conversion
		if filename.endswith(".gri"):
			if os.path.isfile(filename) and  open(filename).readline()[:47] == "** This file contains an SQLite 2.1 database **":
				self.debug.show("MERGE: SQLite2 database format detected. Converting...")
				if not self.db.convert_from_sqlite2(filename, os.path.join(tmp_dir, self.config["default_db"])):
					self.debug.show("MERGE: Can't convert database, aborting.")
					return False
		griffith_dir, tmp_config["default_db"] = os.path.split(filename)

		tmp_db = sql.GriffithSQL(tmp_config, self.debug, griffith_dir)

		merged=0
		movies=0
		cursor = tmp_db.get_all_data()
		while not cursor.EOF:
			movies+=1
			row = cursor.GetRowAssoc(0)
			old = self.db.get_value(table="movies", field="number", where="original_title='%s'" \
				% gutils.gescape(str(row['original_title'])))
			next = gutils.find_next_available(self)
			if old != None:
				#self.debug.show('MERGE: %s: Movie "%s" already present in database'%(old,row['original_title']))
				cursor.MoveNext()
				continue
			#self.debug.show('MERGE: Adding "%s" to database (new number: %s)'%(row['original_title'],next))
			t_movies = {}
			for key in row.keys():
				t_movies[key] = gutils.gescape(str(row[key]))
			t_movies['number'] = next	# replace number with new one

			# don't restore volume/collection/tag/language/loan data (it's dangerous)
			t_movies.pop('id')
			t_movies.pop('loaned')
			if t_movies.has_key('volume_id'):
				t_movies.pop('volume_id')
			if t_movies.has_key('collection_id'):
				t_movies.pop('collection_id')
			
			self.db.add_movie(t_movies)
			
			dest_file = os.path.join(self.griffith_dir,'posters',row['image']+'.jpg')
			if not os.path.isfile(dest_file):
				src_file = os.path.join(tmp_dir,row['image']+'.jpg')
				if os.path.isfile(src_file):
					move(src_file, dest_file)
			merged+=1
			cursor.MoveNext()
		tmp_db.conn.Close();

		rmtree(tmp_dir)

		from initialize	import dictionaries, people_treeview
		dictionaries(self)
		people_treeview(self)
		# let's refresh the treeview
		self.clear_details()
		self.populate_treeview(self.db.get_all_data(order_by="number ASC"))
		self.total = self.db.count_records("movies")
		self.select_last_row(self.total)
		self.treeview_clicked()
		self.count_statusbar()
		gutils.info(self, _("Databases merged!\n\nProcessed movies: %s\nMerged movies: %s"%(movies,merged)), self.main_window)

