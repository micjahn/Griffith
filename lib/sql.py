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
import sqlite
import os.path
import gdebug
import gutils
import gtk

class GriffithSQL:

	con = None
	cursor = None
	
	def __init__(self, config, griffith_dir):
		self.griffith_dir = griffith_dir
		self.config = config
		try:
			self.con = sqlite.connect(os.path.join(griffith_dir, \
				config.get('default_db')), autocommit=1)
			self.cursor = self.con.cursor()
		except:
			gdebug.debug("Error reading database file")
			import sys
			sys.exit()
			
		self.check_if_table_exists()
			
	def check_if_table_exists(self):
		try:
			self.cursor.execute("SELECT id FROM movies LIMIT 1")
		except:
			self.create_db()
		try:
			self.cursor.execute("SELECT id FROM volumes LIMIT 1")
		except:
			self.create_table_volumes()
		try:
			self.cursor.execute("SELECT id FROM collections LIMIT 1")
		except:
			self.create_table_collections()
		try:
			self.cursor.execute("SELECT id FROM media LIMIT 1")
		except:
			self.create_table_media()
			self.update_old_media()

		# check old media
		if self.count_records("movies", "media='DVD'") > 0:
			self.update_old_media()
			
		# see if a db update is needed...
		# a) movie table
		columns = {
			'id'             : 1,
			'volume_id'      : 1,
			'collection_id'  : 1,
			'original_title' : 1,
			'title'          : 1,
			'director'       : 1,
			'number'         : 1,
			'image'          : 1,
			'plot'           : 1,
			'country'        : 1,
			'year'           : 1,
			'runtime'        : 1,
			'classification' : 1,
			'genre'          : 1,
			'studio'         : 1,
			'site'           : 1,
			'imdb'           : 1,
			'actors'         : 1,
			'trailer'        : 1,
			'rating'         : 1,
			'loaned'         : 1,
			'media'          : 1,
			'num_media'      : 1,
			'obs'            : 1,
			'seen'           : 1,
			'region'         : 1,
			'condition'      : 1,
			'color'          : 1,
			'layers'         : 1
		}
		need_upgrade = False
		for column in columns:
			try:
				self.cursor.execute("SELECT %s FROM movies LIMIT 1"%column)
			except:
				columns[column] = 0	# column is missing
				need_upgrade = True
		if need_upgrade:
			self.upgrade_table("movies", columns)

		# b) loans table
		columns = {
			'id'            : 1,
			'movie_id'      : 1,
			'volume_id'     : 1,
			'collection_id' : 1,
			'person_id'     : 1,
			'date'          : 1,
			'return_date'   : 1 
		}
		need_upgrade = False
		for column in columns:
			try:
				self.cursor.execute("SELECT %s FROM loans LIMIT 1"%column)
			except:
				columns[column] = 0	# column is missing
				need_upgrade = True
		if need_upgrade:
			self.upgrade_table("loans", columns)
			
	def upgrade_table(self, table, columns):
		gdebug.debug("Upgrading database: processing %s table..." % table)
		eval("self.create_table_%s(backup=True)"%table)
		sql_query = "INSERT INTO %s_backup ("%table
		i = 0
		for column in columns:
			i = i+1
			sql_query += column
			if i == len(columns):
				sql_query += ' '
			else:
				sql_query += ', '
		sql_query += ") SELECT "
		i = 0
		for column in columns:
			i = i+1
			if columns[column] == 1:
				sql_query += column
			else:
				sql_query += "''"
			if i == len(columns):
				sql_query += ' '
			else:
				sql_query += ', '
				
		sql_query += " FROM %s" % table
		self.cursor.execute (sql_query)
		self.cursor.execute ("DROP TABLE %s" % table)
		eval("self.create_table_%s()"%table)
		self.cursor.execute ("INSERT INTO %s SELECT * FROM %s_backup" % (table, table))
		self.cursor.execute ("DROP TABLE %s_backup"%table)
		self.con.commit()
		
	def create_db(self):
		self.create_table_movies()
		self.create_table_volumes()
		self.create_table_loans()
		self.create_table_people()
		self.create_table_media()

	def create_table_movies(self, backup=False):
		if backup:
			gdebug.debug("Creating 'movies' temporary table...")
			query = "CREATE TEMPORARY TABLE movies_backup"
		else:
			gdebug.debug("Creating 'movies' table...")
			query = "CREATE TABLE movies"
		query += """
			(
				'id' INTEGER PRIMARY KEY,
				'volume_id' INT NOT NULL DEFAULT '0',
				'collection_id' INT NOT NULL DEFAULT '0',
				'original_title' VARCHAR(255) NOT NULL,
				'title' VARCHAR(255),
				'director' VARCHAR(100),
				'number' INT(11) NOT NULL,
				'image' TEXT,
				'plot' TEXT,
				'country' VARCHAR(100),
				'year' INT(4),
				'runtime' INT(4),
				'classification' VARCHAR(50),
				'genre' VARCHAR(100),
				'studio' VARCHAR(50),
				'site' VARCHAR(100),
				'imdb' VARCHAR(100),
				'actors' TEXT,
				'trailer' VARCHAR(100),
				'rating' VARCHAR(50),
				'loaned' INT(1) NOT NULL DEFAULT '0',
				'media' INT(1) DEFAULT='0',
				'num_media' INT(2),
				'obs' TEXT,
				'seen' INT(1) NOT NULL DEFAULT '0',
				'region' INT DEFAULT 2,
				'condition' INT DEFAULT 3,
				'color' INT DEFAULT 0,
				'layers' INT DEFAULT 4
			)
		"""
		self.cursor.execute(query)

	def create_table_loans(self, backup=False):
		if backup:
			gdebug.debug("Creating 'loans' temporary table...")
			query = "CREATE TEMPORARY TABLE loans_backup"
		else:
			gdebug.debug("Creating 'loans' table...")
			query = "CREATE TABLE loans"
		query += """
			(
				id INTEGER PRIMARY KEY,
				person_id INT(11) NOT NULL default '0',
				movie_id INTEGER default '0',
				volume_id INTEGER default '0',
				collection_id INTEGER default '0',
				date DATE NOT NULL default '0000-00-00',
				return_date DATE
			)
		"""
		self.cursor.execute(query)
			
	def create_table_people(self, backup=False):
		if backup:
			gdebug.debug("Creating 'people' temporary table...")
			query = "CREATE TEMPORARY TABLE people_backup"
		else:
			gdebug.debug("Creating 'people' table...")
			query = "CREATE TABLE people"
		query += """
			(
				id INTEGER PRIMARY KEY,
				name VARCHAR(200) NOT NULL,
				email VARCHAR(150),
				phone VARCHAR(50)
			)
		"""
		self.cursor.execute(query)


	def get_all_data(self, table_name="movies", order_by="number ASC",where=None):
		sql="SELECT * FROM %s" % table_name
		if where:
			sql = sql + " WHERE %s" % where
		sql = sql + " ORDER BY %s" % order_by
		self.cursor.execute(sql)
		return self.cursor.fetchall()
	
	def get_loaned_movies(self):
		self.cursor.execute("SELECT * FROM movies WHERE loaned='1' ORDER BY number")
		return self.cursor.fetchall()
		
	def get_not_seen_movies(self):
		self.cursor.execute("SELECT * FROM movies WHERE seen='0' ORDER BY number")
		return self.cursor.fetchall()

	def get_loan_info(self, movie_id=None, volume_id=None, collection_id=None):
		query = "SELECT * FROM loans WHERE "
		if collection_id>0:
			query += "collection_id='%s'" % str(collection_id)
		elif volume_id>0:
			query += "volume_id='%s'" % str(volume_id)
		else:
			query += "movie_id='%s'" % str(movie_id)
		query +=  " AND return_date = ''"
		self.cursor.execute(query)
		return self.cursor.fetchall()

	def get_loan_history(self, movie_id=None, volume_id=None, collection_id=None):
		query = "SELECT * FROM loans WHERE return_date <> '' AND ("
		if collection_id>0:
			query += "collection_id='%s'" % str(collection_id)
		if volume_id>0:
			if collection_id>0:
				query += " OR "
			query += "volume_id='%s'" % str(volume_id)
		if movie_id>0:
			if collection_id>0 or volume_id>0:
				query += " OR "
			query += " movie_id='%s'" % str(movie_id)
		query +=  ")"
		self.cursor.execute(query)
		return self.cursor.fetchall()

	def count_records(self,table_name, where='1'):
		self.cursor.execute("SELECT COUNT(id) FROM %s" % (table_name) + " WHERE %s" % (where))
		return int(self.cursor.fetchone()[0])
		
	def remove_movie_by_num(self,number):
		self.cursor.execute("DELETE FROM movies WHERE number = '"+number+"'")
		self.con.commit()
		
	def select_movie_by_num(self,number):
		self.cursor.execute("SELECT * FROM movies WHERE number = '"+number+"' ORDER BY number ASC")
		return self.cursor.fetchall()
	
	def select_movie_by_original_title(self,txt):
		self.cursor.execute("SELECT * FROM movies WHERE original_title LIKE '%"+txt+"%' ORDER BY number ASC")
		return self.cursor.fetchall()
		
	def select_movie_by_title(self,txt):
		self.cursor.execute("SELECT * FROM movies WHERE title LIKE '%"+txt+"%' ORDER BY number ASC")
		return self.cursor.fetchall()
		
	def select_movie_by_director(self,txt):
		self.cursor.execute("SELECT * FROM movies WHERE director LIKE '%"+txt+"%' ORDER BY number ASC")
		return self.cursor.fetchall()

	def select_movie_by_rating(self,txt):
		self.cursor.execute("SELECT * FROM movies WHERE rating LIKE '"+txt+"' ORDER BY number ASC")
		return self.cursor.fetchall()
		
	def select_movie_by_year(self,txt):
		self.cursor.execute("SELECT * FROM movies WHERE year = '"+txt+"' ORDER BY number ASC")
		return self.cursor.fetchall()

	def select_movie_by_genre(self,txt):
		self.cursor.execute("SELECT * FROM movies WHERE genre LIKE '%"+txt+"%' ORDER BY number ASC")
		return self.cursor.fetchall()
		
	def select_movie_by_actors(self,txt):
		self.cursor.execute("SELECT * FROM movies WHERE actors LIKE '%"+txt+"%' ORDER BY number ASC")
		return self.cursor.fetchall()

	def remove_person_by_name(self, number):
		self.cursor.execute("DELETE FROM people WHERE name = '"+number+"'")
		
	def select_person_by_name(self, name):
		self.cursor.execute("SELECT * FROM people WHERE name = '"+name+"'")
		return self.cursor.fetchall()
		
	def select_person_by_id(self, p_id):
		self.cursor.execute("SELECT * FROM people WHERE id = '"+str(p_id)+"'")
		return self.cursor.fetchall()
		
	def add_movie(self, data):
		media = gutils.on_combo_box_entry_changed(data.am_media)
		plot_buffer = data.am_plot.get_buffer()
		with_buffer = data.am_with.get_buffer()
		obs_buffer = data.am_obs.get_buffer()
		(filepath, filename) = os.path.split(data.am_picture_name.get_text())
		query = """
			INSERT INTO 'movies' ('id', 'original_title', 'title', 'director', 'plot', 'image', 'year',
			'runtime', 'actors', 'country', 'genre', 'media', 'classification', 'studio', 'site', 'color',
			'region', 'layers', 'condition', 'imdb', 'trailer', 'obs', 'num_media', 'loaned', 'rating', 'seen',
			'number', 'volume_id', 'collection_id')
			VALUES (Null,'""" + gutils.gescape(data.am_original_title.get_text()) + "','" +\
			gutils.gescape(data.am_title.get_text())+"','" +\
			gutils.gescape(data.am_director.get_text())+"','" +\
			gutils.gescape(plot_buffer.get_text(plot_buffer.get_start_iter(), plot_buffer.get_end_iter()))+"','" +\
			filename+"','" +\
			data.am_year.get_text()+"','" +\
			data.am_runtime.get_text()+"','" +\
			gutils.gescape(with_buffer.get_text(with_buffer.get_start_iter(), with_buffer.get_end_iter()))+"','" +\
			gutils.gescape(data.am_country.get_text())+"','" +\
			gutils.gescape(data.am_genre.get_text())+"','" +\
			str(media)+"','" +\
			gutils.gescape(data.am_classification.get_text())+"','" +\
			gutils.gescape(data.am_studio.get_text())+"','" +\
			data.am_site.get_text()+"','" +\
			str(int(data.am_color.get_active()))+"','" +\
			str(int(data.am_region.get_active()))+"','" +\
			str(int(data.am_layers.get_active()))+"','" +\
			str(int(data.am_condition.get_active()))+"','" +\
			data.am_imdb.get_text()+"','" +\
			data.am_trailer.get_text()+"','" +\
			gutils.gescape(obs_buffer.get_text(obs_buffer.get_start_iter(), obs_buffer.get_end_iter()))+"','" +\
			data.am_discs.get_text()+"','0','" +\
			str(int(data.rating_slider_add.get_value()))+"','" +\
			str(int(data.am_seen.get_active()))+"','" +\
			data.am_number.get_text()+"', '" +\
			str(data.am_volume_combo.get_active()) + "', '"+\
			str(data.am_collection_combo.get_active()) + "')"
		self.cursor.execute(query)
				
	def new_db(self, parent):
		"""initializes a new griffith database file"""
		response = gutils.question(self, \
			_("Are you sure you want to create a new database?\nYou will lose ALL your current data!"), \
			1, parent.main_window)
		if response == gtk.RESPONSE_YES:
			response_sec = gutils.question(self, \
				_("Last chance!\nDo you confirm that you want\nto lose your current data?"), \
				1, parent.main_window)
			if response_sec == gtk.RESPONSE_YES:
				# delete images
				for root, dirs, files in os.walk(os.path.join(self.griffith_dir,"posters"), topdown=False):
					for name in files:
						os.remove(os.path.join(root, name))
				# delete db
				parent.db.con.close()
				os.unlink(os.path.join(self.griffith_dir,self.config.get('default_db')))
				# create/connect db
				parent.db = GriffithSQL(self.config, self.griffith_dir)
				parent.clear_details()
				parent.total = 0
				parent.count_statusbar()
				parent.treemodel.clear()
				import edit
				edit.fill_volumes_combo(parent)
				edit.fill_collections_combo(parent)
			else:
				pass
		else:
			pass

	# volumes/collections
	def create_table_volumes(self):
		gdebug.debug("Creating 'volumes' table...")
		self.cursor.execute ("""
			CREATE TABLE volumes
			(
				'id' INTEGER PRIMARY KEY,
				'name' STRING NOT NULL,
				'loaned' INT(1) NOT NULL default '0'
			);
			INSERT INTO 'volumes' VALUES (0,'None','0');
			""")
			
	def create_table_collections(self):
		gdebug.debug("Creating 'collections' table...")
		self.cursor.execute ("""
			CREATE TABLE collections
			(
				'id' INTEGER PRIMARY KEY,
				'name' STRING NOT NULL,
				'loaned' INT(1) NOT NULL default '0'
			);
			INSERT INTO 'collections' VALUES (0,'None','0');
			""")

	def get_all_volumes_data(self):
		self.cursor.execute("SELECT * FROM volumes ORDER BY name")
		return self.cursor.fetchall()
		
	def get_all_collections_data(self):
		self.cursor.execute("SELECT * FROM collections ORDER BY name")
		return self.cursor.fetchall()
	
	def select_movies_by_volume(self,volume_id):
		self.cursor.execute("SELECT * FROM movies WHERE volume_id = '%s' ORDER BY number ASC" % volume_id)
		return self.cursor.fetchall()

	def select_movies_by_collection(self,collection):
		self.cursor.execute("SELECT * FROM movies WHERE collection_id = '%s' ORDER BY number ASC" % collection)
		return self.cursor.fetchall()
	
	def is_volume_loaned(self,volume):
		self.cursor.execute("SELECT loaned FROM volumes WHERE id = '%s'" % volume)
		return self.cursor.fetchone()[0]

	def is_collection_loaned(self,collection):
		self.cursor.execute("SELECT loaned FROM collections WHERE id = '%s'" % collection)
		return self.cursor.fetchone()[0]

	def add_volume(self, name):
		# check if volume already exists
		for volume in self.get_all_volumes_data():
			if name == volume['name']:
				gdebug.debug("Volume '%s' already exists"%name)
				return False
		gdebug.debug("Adding '%s' volume to database..."%name)
		try:
			self.cursor.execute("INSERT INTO 'volumes'('id', 'name', 'loaned') VALUES (Null,'"+
			gutils.gescape(name)+"','0');")
		except:
			return False
		return True

	def add_collection(self, name):
		# check if volume already exists
		for collection in self.get_all_collections_data():
			if name == collection['name']:
				gdebug.debug("Collection '%s' already exists"%name)
				return False
		gdebug.debug("Adding '%s' collection to database..."%name)
		try:
			self.cursor.execute("INSERT INTO 'collections'('id', 'name', 'loaned') VALUES (Null,'"+
			gutils.gescape(name)+"','0');")
		except:
			return False
		return True

	def remove_volume(self, id=None, name=None):
		if id != None:
			id = gutils.gescape(id)
			self.cursor.execute("SELECT name FROM volumes WHERE id = '%s'" % id)
			name = self.cursor.fetchone()[0]
		elif name != None and id == None:
			name =	gutils.gescape(name)
			self.cursor.execute("SELECT id FROM volumes WHERE name = '%s'" % name)
			id = str(int(self.cursor.fetchone()[0]))
		if str(id) == '0':
			gdebug.debug("You have to select volume first")
			return False
		self.cursor.execute("SELECT count(id) FROM movies WHERE volume_id = '%s'" % id)
		movies = int(self.cursor.fetchone()[0])
		if movies > 0:
			gutils.warning(self, msg="%s movie(s) in this volume.\nRemoval is possible only if there is no movie assigned to volume"%str(movies))
			return False
		gdebug.debug("Removing '%s' volume (id=%s) from database..."%(name, id))
		try:
			self.cursor.execute("DELETE FROM volumes WHERE id = '%s'" % id)
		except:
				return False
		return True
	
	def remove_collection(self, id=None, name=None):
		if id != None:
			id = gutils.gescape(id)
			self.cursor.execute("SELECT name FROM collections WHERE id = '%s'" % id)
			name = self.cursor.fetchone()[0]
		elif name != None and id == None:
			name =	gutils.gescape(name)
			self.cursor.execute("SELECT id FROM collections WHERE name = '%s'" % name)
			id = str(int(self.cursor.fetchone()[0]))
		if str(id) == '0':
			gdebug.debug("You have to select collection first")
			return False
		self.cursor.execute("SELECT count(id) FROM movies WHERE collection_id = '%s'" % id)
		movies = int(self.cursor.fetchone()[0])
		if movies > 0:
			gutils.warning(self, msg="%s movie(s) in this collection.\nRemoval is possible only if there is no movie assigned to collection"%str(movies))
			return False
		gdebug.debug("Removing '%s' collection (id=%s) from database..."%(name, id))
		try:
			self.cursor.execute("DELETE FROM collections WHERE id = '%s'" % id)
		except:
				return False
		return True

	# media
	def create_table_media(self):
		gdebug.debug("Creating 'media' table...")
		self.cursor.execute ("""
			CREATE TABLE media
			(
				'id' INTEGER PRIMARY KEY,
				'name' STRING NOT NULL
			);
			INSERT INTO 'media' VALUES (0, "DVD"); 
			INSERT INTO 'media' VALUES (1, "DVD-R"); 
			INSERT INTO 'media' VALUES (2, "DVD-RW"); 
			INSERT INTO 'media' VALUES (3, "DVD+R"); 
			INSERT INTO 'media' VALUES (4, "DVD+RW"); 
			INSERT INTO 'media' VALUES (5, "DVD-RAM"); 
			INSERT INTO 'media' VALUES (6, "CD"); 
			INSERT INTO 'media' VALUES (7, "CD-RW"); 
			INSERT INTO 'media' VALUES (8, "VCD"); 
			INSERT INTO 'media' VALUES (9, "SVCD"); 
			INSERT INTO 'media' VALUES (10, "VHS"); 
			INSERT INTO 'media' VALUES (11, "BETACAM"); 
			""")

	def update_old_media(self):
		gdebug.debug("Upgrading old media values...")
		self.cursor.execute("""
			UPDATE movies SET media = '0' WHERE media = 'DVD'; 
			UPDATE movies SET media = '1' WHERE media = 'DVD-R'; 
			UPDATE movies SET media = '2' WHERE media = 'DVD-RW'; 
			UPDATE movies SET media = '3' WHERE media = 'DVD+R'; 
			UPDATE movies SET media = '4' WHERE media = 'DVD+RW'; 
			UPDATE movies SET media = '5' WHERE media = 'DVD-RAM'; 
			UPDATE movies SET media = '6' WHERE media = 'DivX'; 
			UPDATE movies SET media = '6' WHERE media = 'DIVX'; 
			UPDATE movies SET media = '6' WHERE media = 'XviD'; 
			UPDATE movies SET media = '6' WHERE media = 'XVID'; 
			UPDATE movies SET media = '6' WHERE media = 'WMV'; 
			UPDATE movies SET media = '6' WHERE media = 'WMV'; 
			UPDATE movies SET media = '8' WHERE media = 'VCD'; 
			UPDATE movies SET media = '9' WHERE media = 'SVCD'; 	
			UPDATE movies SET media = '10' WHERE media = 'VHS'; 
			UPDATE movies SET media = '11' WHERE media = 'BETACAM'; 
		""")
		self.con.commit()
