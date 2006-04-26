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
#from pysqlite2 import dbapi2 as sqlite
import adodb
import os.path
import gutils
import gtk

class GriffithSQL:
	conn = None

	def __init__(self, config, debug, griffith_dir):
		self.griffith_dir = griffith_dir
		self.config = config
		self.debug = debug
#		config["db_type"] = "postgres" # TODO: just testing, remove it leter
		if not config.has_key("db_type"):
			config["db_type"] = "sqlite"

		# detect SQLite2 and convert to SQLite3
		if config["db_type"] == "sqlite":
			filename = os.path.join(griffith_dir, config["default_db"])
			if os.path.isfile(filename) and open(filename).readline()[:47] == "** This file contains an SQLite 2.1 database **":
				self.debug.show("SQLite2 database format detected. Converting...")
				if self.convert_from_sqlite2(filename, os.path.join(griffith_dir, "griffith.db")):
					self.config["default_db"] = "griffith.db"
					self.config.save()

		self.conn = adodb.NewADOConnection(config["db_type"])

		if config["db_type"] == "sqlite":
			self.pkey = "INTEGER PRIMARY KEY"
			self.conn.Connect(database=os.path.join(griffith_dir, config["default_db"]))
		elif config["db_type"] == "postgres":
			self.pkey = "SERIAL NOT NULL PRIMARY KEY"
			if not config.has_key("db_server"):
				config["db_server"] = "localhost"
			if not config.has_key("db_port"):
				config["db_port"] = "5432"
			if not config.has_key("db_user"):
				config["db_user"] = "griffith"
			if not config.has_key("db_passwd"):
				config["db_passwd"] = "gRiFiTh"
			if not config.has_key("db_name"):
				config["db_name"] = "griffith"
			self.conn.Connect("host=%s user=%s password=%s dbname=%s port=%s" % \
				(config["db_server"], config["db_user"], config["db_passwd"], config["db_name"], config["db_port"]))

		self.check_if_table_exists()

	def new_db(self, parent): #{{{
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
				parent.db.conn.Execute("DROP TABLE collections;")
				parent.db.conn.Execute("DROP TABLE languages;")
				parent.db.conn.Execute("DROP TABLE loans;")
				parent.db.conn.Execute("DROP TABLE media;")
				parent.db.conn.Execute("DROP TABLE movie_lang;")
				parent.db.conn.Execute("DROP TABLE movie_tag;")
				parent.db.conn.Execute("DROP TABLE movies;")
				parent.db.conn.Execute("DROP TABLE people;")
				parent.db.conn.Execute("DROP TABLE tags;")
				parent.db.conn.Execute("DROP TABLE volumes;")
				parent.db.conn.Close()
				if self.config["default_db"] == "sqlite":
					os.unlink(os.path.join(self.griffith_dir,self.config.get('default_db')))
				# create/connect db
				parent.db = GriffithSQL(self.config, self.debug, self.griffith_dir)
				parent.clear_details()
				parent.total = 0
				parent.count_statusbar()
				parent.treemodel.clear()
				from initialize	import dictionaries, people_treeview
				dictionaries(parent)
				people_treeview(parent)
			else:
				pass
		else:
			pass
	#}}}

	# create tables ----------------------------------------------------{{{
	def create_db(self):
		self.create_table_movies()
		self.create_table_volumes()
		self.create_table_collections()
		self.create_table_loans()
		self.create_table_people()
		self.create_table_media()
		self.create_table_languages()
		self.create_table_movie_lang()
		self.create_table_movie_tag()
		self.create_table_tags()

	def create_table_movies(self, backup=False):
		if backup:
			self.debug.show("Creating 'movies' temporary table...")
			query = "CREATE TEMPORARY TABLE movies_backup ("
		else:
			self.debug.show("Creating 'movies' table...")
			query = "CREATE TABLE movies ("
		query += """
			"id" %s,
			"volume_id" INTEGER NOT NULL DEFAULT 0,
			"collection_id" INTEGER NOT NULL DEFAULT 0,
			"original_title" VARCHAR(255) NOT NULL,
			"title" VARCHAR(255),
			"director" VARCHAR(100),
			"number" INTEGER NOT NULL,
			"image" VARCHAR,
			"plot" TEXT,
			"country" VARCHAR(100),
			"year" INTEGER,
			"runtime" INTEGER,
			"classification" VARCHAR(50),
			"genre" VARCHAR(100),
			"studio" VARCHAR(50),
			"site" VARCHAR(100),
			"imdb" VARCHAR(100),
			"actors" TEXT,
			"trailer" VARCHAR(100),
			"rating" SMALLINT NOT NULL DEFAULT 0,
			"loaned" SMALLINT NOT NULL DEFAULT 0, -- TODO: change it to BOOLEAN
			"media" SMALLINT NOT NULL DEFAULT 0,
			"num_media" SMALLINT,
			"obs" TEXT,
			"seen" SMALLINT NOT NULL DEFAULT 0, -- TODO: change it to BOOLEAN
			"region" SMALLINT DEFAULT 9,
			"condition" SMALLINT DEFAULT 5,
			"color" SMALLINT DEFAULT 3,
			"layers" SMALLINT DEFAULT 4
		)""" % self.pkey
		self.conn.Execute(query)

	def create_table_loans(self, backup=False):
		query = ''
		if backup:
			self.debug.show("Creating 'loans' temporary table...")
			query = "CREATE TEMPORARY TABLE loans_backup"
		else:
			self.debug.show("Creating 'loans' table...")
			query = "CREATE TABLE loans"
		query += """(
			"id" %s,
			"person_id" INTEGER NOT NULL DEFAULT 0,
			"movie_id" BIGINT DEFAULT 0,
			"volume_id" INTEGER DEFAULT 0,
			"collection_id" INTEGER DEFAULT 0,
			"date" DATE NOT NULL,
			"return_date" DATE DEFAULT NULL
		)""" % self.pkey
		self.conn.Execute(query)

	def create_table_people(self, backup=False):
		if backup:
			self.debug.show("Creating 'people' temporary table...")
			query = "CREATE TEMPORARY TABLE people_backup"
		else:
			self.debug.show("Creating 'people' table...")
			query = "CREATE TABLE people"
		query += """(
			"id" %s,
			"name" VARCHAR(200) NOT NULL,
			"email" VARCHAR(150),
			"phone" VARCHAR(50)
		)""" % self.pkey
		self.conn.Execute(query)

	def create_table_volumes(self):
		self.debug.show("Creating 'volumes' table...")
		self.conn.Execute ("""
			CREATE TABLE volumes
			(
				"id" %s,
				"name" VARCHAR NOT NULL,
				"loaned" SMALLINT NOT NULL DEFAULT 0
			);
		""" % self.pkey)
		self.conn.Execute("INSERT INTO volumes VALUES (0,'',0);")

	def create_table_collections(self):
		self.debug.show("Creating 'collections' table...")
		self.conn.Execute ("""
			CREATE TABLE collections
			(
				"id" %s,
				"name" VARCHAR NOT NULL,
				"loaned" SMALLINT NOT NULL DEFAULT 0
			);
		""" % self.pkey)
		self.conn.Execute('INSERT INTO collections VALUES (0,\'\',0);')

	def create_table_media(self):
		self.debug.show("Creating 'media' table...")
		self.conn.Execute ("""
			CREATE TABLE media
			(
				"id" %s,
				"name" VARCHAR NOT NULL
			);
		""" % self.pkey)
		self.conn.Execute("INSERT INTO media VALUES (0, 'DVD');")
		self.conn.Execute("INSERT INTO media VALUES (1, 'DVD-R');")
		self.conn.Execute("INSERT INTO media VALUES (2, 'DVD-RW');")
		self.conn.Execute("INSERT INTO media VALUES (3, 'DVD+R');")
		self.conn.Execute("INSERT INTO media VALUES (4, 'DVD+RW');")
		self.conn.Execute("INSERT INTO media VALUES (5, 'DVD-RAM');")
		self.conn.Execute("INSERT INTO media VALUES (6, 'CD');")
		self.conn.Execute("INSERT INTO media VALUES (7, 'CD-RW');")
		self.conn.Execute("INSERT INTO media VALUES (8, 'VCD');")
		self.conn.Execute("INSERT INTO media VALUES (9, 'SVCD');")
		self.conn.Execute("INSERT INTO media VALUES (10, 'VHS');")
		self.conn.Execute("INSERT INTO media VALUES (11, 'BETACAM');")

	def create_table_languages(self):
		self.debug.show("Creating 'languages' table...")
		self.conn.Execute ("""
			CREATE TABLE languages
			(
				"id" %s,
				"name" VARCHAR NOT NULL
			);
		""" % self.pkey)
		self.conn.Execute("INSERT INTO languages VALUES (0,'');")

	def create_table_movie_lang(self):
		self.debug.show("Creating 'movie_lang' table...")
		self.conn.Execute ("""
			CREATE TABLE movie_lang
			(
				"movie_id" BIGINT NOT NULL,
				"lang_id" INTEGER NOT NULL,
				"type" SMALLINT
			);
		""")

	def create_table_tags(self):
		self.debug.show("Creating 'tags' table...")
		self.conn.Execute ("""
			CREATE TABLE tags
			(
				"id" %s,
				"name" VARCHAR NOT NULL
			);
		""" % self.pkey)
		self.conn.Execute("INSERT INTO tags VALUES (0, '" + _("Favourite") + "');")

	def create_table_movie_tag(self):
		self.debug.show("Creating 'movie_tag' table...")
		self.conn.Execute ("""
			CREATE TABLE movie_tag
			(
				"movie_id" INTEGER NOT NULL,
				"tag_id" SMALLINT NOT NULL
			);
		""")

	# }}}

	# upgrade tables ---------------------------------------------------{{{
	def check_if_table_exists(self):
		try:
			self.conn.Execute("SELECT id FROM movies LIMIT 1")
		except:
			self.create_db()
			return True
		try:
			self.conn.Execute("SELECT id FROM volumes LIMIT 1")
		except:
			self.create_table_volumes()
		try:
			self.conn.Execute("SELECT id FROM collections LIMIT 1")
		except:
			self.create_table_collections()
		try:
			self.conn.Execute("SELECT id FROM media LIMIT 1")
		except:
			self.create_table_media()
		try:
			self.conn.Execute("SELECT id FROM languages LIMIT 1")
		except:
			self.create_table_languages()
		try:
			self.conn.Execute("SELECT movie_id FROM movie_lang LIMIT 1")
		except:
			self.create_table_movie_lang()
		try:
			self.conn.Execute("SELECT id FROM tags LIMIT 1")
		except:
			self.create_table_tags()
		try:
			self.conn.Execute("SELECT movie_id FROM movie_tag LIMIT 1")
		except:
			self.create_table_movie_tag()

		# "empty" language is needed
		if self.get_value(field="name", table="languages", where="id = '0'") == None:
			self.conn.Execute("INSERT INTO languages VALUES(0, '')")

		# check old media
		if self.config['db_type']== "sqlite":
			if self.count_records("movies", 'media="DVD"') > 0:
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
				self.conn.Execute("SELECT %s FROM movies LIMIT 1"%column)
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
				self.conn.Execute("SELECT %s FROM loans LIMIT 1"%column)
			except:
				columns[column] = 0	# column is missing
				need_upgrade = True
		if need_upgrade:
			self.upgrade_table("loans", columns)

	def upgrade_table(self, table, columns):
		self.debug.show("Upgrading database: processing %s table..." % table)
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
				sql_query += '""'
			if i == len(columns):
				sql_query += ' '
			else:
				sql_query += ', '

		sql_query += " FROM %s" % table
		self.conn.Execute(sql_query)
		self.conn.Execute("DROP TABLE %s" % table)
		eval("self.create_table_%s()"%table)
		self.conn.Execute("INSERT INTO %s SELECT * FROM %s_backup" % (table, table))
		self.conn.Execute("DROP TABLE %s_backup"%table)

	def update_old_media(self):
		self.debug.show("Upgrading old media values...")
		self.conn.Execute("UPDATE movies SET media = '0' WHERE media = 'DVD';")
		self.conn.Execute("UPDATE movies SET media = '1' WHERE media = 'DVD-R';")
		self.conn.Execute("UPDATE movies SET media = '2' WHERE media = 'DVD-RW';")
		self.conn.Execute("UPDATE movies SET media = '3' WHERE media = 'DVD+R';")
		self.conn.Execute("UPDATE movies SET media = '4' WHERE media = 'DVD+RW';")
		self.conn.Execute("UPDATE movies SET media = '5' WHERE media = 'DVD-RAM';")
		self.conn.Execute("UPDATE movies SET media = '6' WHERE media = 'DivX';")
		self.conn.Execute("UPDATE movies SET media = '6' WHERE media = 'DIVX';")
		self.conn.Execute("UPDATE movies SET media = '6' WHERE media = 'XviD';")
		self.conn.Execute("UPDATE movies SET media = '6' WHERE media = 'XVID';")
		self.conn.Execute("UPDATE movies SET media = '6' WHERE media = 'WMV';")
		self.conn.Execute("UPDATE movies SET media = '6' WHERE media = 'WMV';")
		self.conn.Execute("UPDATE movies SET media = '8' WHERE media = 'VCD';")
		self.conn.Execute("UPDATE movies SET media = '9' WHERE media = 'SVCD'; 	")
		self.conn.Execute("UPDATE movies SET media = '10' WHERE media = 'VHS';")
		self.conn.Execute("UPDATE movies SET media = '11' WHERE media = 'BETACAM';")

	def fix_old_data(self):
		self.conn.Execute("UPDATE movies SET collection_id=0 WHERE collection_id=''")
		self.conn.Execute("UPDATE movies SET volume_id=0 WHERE volume_id=''")
		self.conn.Execute("UPDATE loans SET return_date=NULL WHERE return_date=''")
		self.conn.Execute("UPDATE collections SET name='', loaned=0 WHERE id = 0;")
		self.conn.Execute("UPDATE volumes SET name='', loaned=0 WHERE id = 0;")
		self.conn.Execute("UPDATE movies SET year=NULL WHERE year<1900 or year>2020")
		try:
			self.update_old_media()
		except:
			pass

	# }}}

	# add data ---------------------------------------------------------{{{
	def add_movie(self, t_movies, t_languages=None, t_tags=None):
		query = "INSERT INTO movies ("
		for field in t_movies.keys():
			query += "%s," % field
		query = query[:len(query)-1]	# remove last comma
		query += ") VALUES ("
		for field in t_movies:
			if t_movies[field] == "":
				query += "NULL,"
			elif str(t_movies[field]) == 'None':
				query += "NULL,"
			else:
				query += "'%s'," % t_movies[field]
		query = query[:len(query)-1] + ");" # remove last comma
		self.conn.Execute(query)

		movie_id = self.get_value(field="id", table="movies", where="number = '%s'" % t_movies['number'])

		# languages
		if t_languages != None:
			for lang in t_languages.keys():
				for type in t_languages[lang].keys():
					self.conn.Execute("INSERT INTO movie_lang(movie_id, lang_id, type) \
							VALUES ('%s', '%s', '%s');" % (movie_id, lang, type) )
		# tags
		if t_tags != None:
			for i in t_tags.keys():
				self.conn.Execute("INSERT INTO movie_tag(movie_id, tag_id) \
						VALUES ('%s', '%s');" % (movie_id, i) )

	def add_volume(self, name):
		# check if volume already exists
		cursor = self.get_all_data("volumes", what="name")
		while not cursor.EOF:
			if str(name) == str(cursor.fields[0]):
				self.debug.show("Volume '%s' already exists"%name)
				return False
			cursor.MoveNext()
		self.debug.show("Adding '%s' volume to database..."%name)
		try:
			self.conn.Execute("INSERT INTO volumes(name) VALUES ('"+gutils.gescape(name)+"');")
		except:
			return False
		return True

	def add_collection(self, name):
		# check if volume already exists
		cursor = self.get_all_data("collections", what="name")
		while not cursor.EOF:
			if str(name) == str(cursor.fields[0]):
				self.debug.show("Collection '%s' already exists"%name)
				return False
			cursor.MoveNext()
		self.debug.show("Adding '%s' collection to database..."%name)
		try:
			self.conn.Execute("INSERT INTO collections(name) VALUES ('"+gutils.gescape(name)+"');")
		except:
			return False
		return True

	def add_language(self, name):
		if name == None or name == '':
			self.debug.show("You didn't write name for new language")
			return False
		name = gutils.gescape(name)
		# check if language already exists
		cursor = self.get_all_data("languages", what="name")
		while not cursor.EOF:
			if str(name) == str(cursor.fields[0]):
				self.debug.show("Language '%s' already exists"%name)
				return False
			cursor.MoveNext()
		self.debug.show("Adding '%s' language to database..."%name)
		try:
			self.conn.Execute("INSERT INTO languages(name) VALUES ('"+gutils.gescape(name)+"');")
		except:
			return False
		return True

	def add_tag(self, name):
		if name == None or name == '':
			self.debug.show("You didn't write name for new tag")
			return False
		# check if tag already exists
		cursor = self.get_all_data("tags", what="name")
		while not cursor.EOF:
			if str(name) == str(cursor.fields[0]):
				self.debug.show("Tag '%s' already exists"%name)
				return False
			cursor.MoveNext()
		self.debug.show("Adding '%s' tag to database..."%name)
#		try:
		self.conn.Execute("INSERT INTO tags(name) VALUES ('"+gutils.gescape(name)+"');")
#		except:
#			return False
		return True

	# }}}

	# select data ------------------------------------------------------{{{
	def get_all_data(self, table_name="movies", order_by=None, where=None, what=None):
		if what == None:
			what = "*"
		sql = "SELECT %s FROM %s" % (what, table_name)
		if where:
			sql += " WHERE %s" % where
		if order_by != None:
			sql += " ORDER BY %s" % order_by
		return self.conn.Execute(sql)

	def get_value(self, field, table, where=None):
		query = "SELECT %s FROM %s" % (field, table)
		if where:
			query += " WHERE %s" % where
		cursor = self.conn.Execute(query)
		if not cursor.EOF:
			return cursor.fields[0]
		else:
			return None

	def select_movie_by_num(self,number):
		return self.conn.Execute("SELECT * FROM movies WHERE number = '%s' ORDER BY number ASC" % number)

	def select_movies_by_volume(self,volume_id):
		return self.conn.Execute("SELECT * FROM movies WHERE volume_id = '%s' ORDER BY number ASC" % volume_id)

	def select_movies_by_collection(self,collection):
		return self.conn.Execute("SELECT * FROM movies WHERE collection_id = '%s' ORDER BY number ASC" % collection)

	def select_person_by_name(self, name):
		return self.conn.Execute("SELECT * FROM people WHERE name = '%s'" % name)

	def select_person_by_id(self, p_id):
		return self.conn.Execute("SELECT * FROM people WHERE id = '%s'" % str(p_id) )

	def get_loaned_movies(self):
		return self.conn.Execute("SELECT * FROM movies WHERE loaned=1 ORDER BY number")

	def get_not_seen_movies(self):
		return self.conn.Execute("SELECT * FROM movies WHERE seen=0 ORDER BY number")

	def get_loan_info(self, movie_id=None, volume_id=None, collection_id=None):
		query = "SELECT * FROM loans WHERE return_date ISNULL AND "
		if collection_id>0:
			query += "collection_id='%s'" % str(collection_id)
		elif volume_id>0:
			query += "volume_id='%s'" % str(volume_id)
		else:
			query += "movie_id='%s'" % str(movie_id)
		return self.conn.Execute(query)

	def get_loan_history(self, movie_id=None, volume_id=None, collection_id=None):
		query = "SELECT * FROM loans WHERE NOT return_date ISNULL AND ("
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
		return self.conn.Execute(query)
	# }}}

	# remove data ------------------------------------------------------{{{
	def remove_movie_by_num(self,number):
		if self.is_movie_loaned(movie_number=number):
			self.debug.show("Movie (number=%s) is loaned. Can't delete!")
			return False
		id = self.get_value(field="id", table="movies", where="number = '%s'" % number)
		if id != None:
			self.conn.Execute("DELETE FROM movie_lang WHERE movie_id = '%s'" % id)
			self.conn.Execute("DELETE FROM movie_tag WHERE movie_id = '%s'" % id)
			self.conn.Execute("DELETE FROM movies WHERE number = '"+number+"'")

	def remove_volume(self, id=None, name=None):
		if id != None:
			name = self.get_value(field="name", table="volumes", where=" id = '%s'" % id)
		elif name != None and name != '' and id == None:
			name =	gutils.gescape(name)
			id = self.get_value(field="id", table="volumes", where="name = '%s'" % name)
			if id != None:
				id = str(int(id))
		if str(id) == '0' or id == None:
			self.debug.show("You have to select volume first")
			return False
		movies = int(self.get_value(field="count(id)", table="movies", where="volume_id = '%s'" % id))
		if movies > 0:
			gutils.warning(self, msg="%s movie(s) in this volume.\nRemoval is possible only if there is no movie assigned to volume"%str(movies))
			return False
		self.debug.show("Removing '%s' volume (id=%s) from database..."%(name, id))
		try:
			self.conn.Execute("DELETE FROM volumes WHERE id = '%s'" % id)
		except:
				return False
		return True

	def remove_collection(self, id=None, name=None):
		if id != None:
			name = self.get_value(field="name", table="collections", where="id = '%s'" % id)
		elif name != None and name != '' and id == None:
			name =	gutils.gescape(name)
			id = self.get_value(field="id", table="collections", where="name = '%s'" % name)
			id = str(int(id))
		if str(id) == '0' or id == None:
			self.debug.show("You have to select collection first")
			return False
		movies = int(self.get_value(field="count(id)", table="movies", where="collection_id = '%s'" % id))
		if movies > 0:
			gutils.warning(self, msg="%s movie(s) in this collection.\nRemoval is possible only if there is no movie assigned to collection"%str(movies))
			return False
		self.debug.show("Removing '%s' collection (id=%s) from database..."%(name, id))
		try:
			self.conn.Execute("DELETE FROM collections WHERE id = '%s'" % id)
		except:
				return False
		return True

	def remove_language(self, id=None, name=None):
		if id != None:
			name = self.get_value(field="name", table="languages", where="id = '%s'"%id)
		elif name != None and name != '' and id == None:
			name =	gutils.gescape(name)
			id = self.get_value(field="id", table="languages", where="name = '%s'"%name)
			id = str(int(id))
		if str(id) == '0' or id == None:
			self.debug.show("You have to select language first")
			return False

		movies = int(self.get_value(field="count(movie_id)", table="movie_lang", where="lang_id = '%s'" % id))
		if movies > 0:
			gutils.warning(self, msg="%s movie(s) are assigned to this language.\nChange movie details first!"%str(movies))
			return False

		self.debug.show("Removing '%s' language (id=%s) from database..."%(name, id))
		try:
			self.conn.Execute("DELETE FROM languages WHERE id = '%s'" % id)
		except:
				return False
		return True

	def remove_tag(self, id=None, name=None):
		if id != None:
			name = self.get_value(field="name", table="tags", where="id = '%s'"%id)
		elif name != None and name != '' and id == None:
			name =	gutils.gescape(name)
			id = self.get_value(field="id", table="tags", where="name = '%s'"%name)
			id = str(int(id))
		if str(id) == '0' or id == None:
			self.debug.show("You have to select tag first")
			return False

		movies = int(self.get_value(field="count(movie_id)", table="movie_tag", where="tag_id = '%s'" % id))
		if movies > 0:
			gutils.warning(self, msg="%s movie(s) are assigned to this tag.\nChange movie details first!"%str(movies))
			return False

		self.debug.show("Removing '%s' tag (id=%s) from database..."%(name, id))
		try:
			self.conn.Execute("DELETE FROM tags WHERE id = '%s'" % id)
		except:
				return False
		return True

	def remove_person_by_name(self, number):
		self.conn.Execute("DELETE FROM people WHERE name = '"+number+"'")
	# }}}

	# update data ------------------------------------------------------{{{
	def update_movie(self, t_movies, t_languages=None, t_tags=None):
		movie_id = t_movies.pop('id')
		if movie_id == None:
			self.debug.show("Update movie: Movie ID is not set, can't update!")
			return False
		query = "UPDATE movies SET "
		for field in t_movies.keys():
			if t_movies[field] == "" or str(t_movies[field]) == 'None':
				query += "%s=NULL," % field
			else:
				query += "%s='%s'," % (field, t_movies[field])
		query = query[:len(query)-1]	# remove last comma
		query += " WHERE id='%s'"%movie_id
		self.conn.Execute(query)

		self.conn.Execute("DELETE FROM movie_lang WHERE movie_id = '%s';" % movie_id)	# remove old data
		# languages
		if t_languages != None:
			for lang in t_languages.keys():
				for type in t_languages[lang].keys():
					self.conn.Execute("INSERT INTO movie_lang(movie_id, lang_id, type) \
							VALUES ('%s', '%s', '%s');" % (movie_id, lang, type) )
		self.conn.Execute("DELETE FROM movie_tag WHERE movie_id = '%s';" % movie_id)
		# tags
		if t_tags != None:
			for i in t_tags.keys():
				self.conn.Execute("INSERT INTO movie_tag(movie_id, tag_id) \
						VALUES ('%s', '%s');" % (movie_id, i) )

	def update_collection(self, id, name=None, volume_id=None, loaned=None):
		if str(id) == '0':
			self.debug.show("You have to select collection first")
			return False
		if name!=None:
			tmp = self.get_value(field="id", table="collections", where="name='%s'"%name)
			if tmp != None:
				self.debug.show("This name is already in use (id=%s)"%tmp)
				gutils.warning(self, msg="This name is already in use!")
				return False
			try:
				self.conn.Execute("UPDATE collections SET name = '%s' WHERE id = '%s';"%(name,id))
			except:
				self.debug.show("ERROR during updating collection's name!")
				return False
			return True
		if loaned==1:
			try:
				self.conn.Execute("UPDATE collections SET loaned=1 WHERE id='%s';" % id)
				self.conn.Execute("UPDATE movies SET loaned=1 WHERE collection_id='%s';" % id)
			except:
				self.debug.show("ERROR during updating collection's loan data!")
				return False
			if volume_id:
				try:
					self.conn.Execute("UPDATE volumes SET loaned=1 WHERE id='%s';"%volume_id)
				except:
					self.debug.show("ERROR during updating collection's loan data!")
					return False
			return True
		elif loaned==0:
			try:
				self.conn.Execute("UPDATE collections SET loaned=0 WHERE id='%s';" % id)
				self.conn.Execute("UPDATE movies SET loaned=0 WHERE collection_id='%s';" % id)
			except:
				self.debug.show("ERROR during updating collection's loan data!")
				return False
			if volume_id:
				try:
					self.conn.Execute("UPDATE volumes SET loaned=0 WHERE id='%s';"%volume_id)
				except:
					self.debug.show("ERROR during updating volume's loan data!")
					return False
			return True
		return False

	def update_volume(self, id, name=None, loaned=None):
		if str(id) == '0':
			self.debug.show("You have to select volume first")
			return False
		if name!=None:
			tmp = self.get_value(field="id", table="volumes", where="name='%s'"%name)
			if tmp != None:
				self.debug.show("This name is already in use (id=%s)"%tmp)
				gutils.warning(self, msg="This name is already in use!")
				return False
			try:
				self.conn.Execute("UPDATE volumes SET name = '%s' WHERE id = '%s';"%(name,id))
			except:
				self.debug.show("ERROR during updating volume's name!")
				return False
			return True
		if loaned==1:
			try:
				self.conn.Execute("UPDATE volumes SET loaned=1 WHERE id='%s';" % id)
				self.conn.Execute("UPDATE movies SET loaned=1 WHERE volume_id='%s';" % id)
			except:
				self.debug.show("ERROR during updating volume's loan data!")
				return False
			return True
		elif loaned==0:
			try:
				self.conn.Execute("UPDATE volumes SET loaned=0 WHERE id='%s';" % id)
				self.conn.Execute("UPDATE movies SET loaned=2 WHERE volume_id='%s';" % id)
			except:
				self.debug.show("ERROR during updating volume's loan data!")
				return False
			return True
		return False

	def update_language(self, id, name):
		if str(id) == '0':
			self.debug.show("You have to select language first")
			return False
		tmp = self.get_value(field="id", table="languages", where="name='%s'"%name)
		if tmp != None:
			self.debug.show("This name is already in use (id=%s)"%tmp)
			gutils.warning(self, msg="This name is already in use!")
			return False
		try:
			self.conn.Execute("UPDATE languages SET name ='%s' WHERE id='%s';" % (name, id))
		except:
			self.debug.show("ERROR during updating language name!")
			return False
		return True

	def update_tag(self, id, name):
		if id == None:
			self.debug.show("You have to select tag first")
			return False
		if name == '':
			self.debug.show("Tag's name is empty")
			return False
		tmp = self.get_value(field="id", table="tags", where="name='%s'"%name)
		if tmp != None:
			self.debug.show("This name is already in use (id=%s)"%tmp)
			gutils.warning(self, msg="This name is already in use!")
			return False
		try:
			self.conn.Execute("UPDATE tags SET name ='%s' WHERE id='%s';" % (name,id))
		except:
			self.debug.show("ERROR during updating tag name!")
			return False
		return True
	#}}}

	def count_records(self,table_name, where=None):
		query = "SELECT COUNT(id) FROM %s" % (table_name)
		if where:
			query += " WHERE %s" % where
		return int(self.conn.GetRow(query)[0])

	def is_movie_loaned(self,movie_id=None, movie_number=None):
		if movie_id==None and movie_number == None:
			return None
		if movie_id:
			sql = "SELECT loaned FROM movies WHERE id = '%s'" % movie_id
		if movie_number:
			sql = "SELECT loaned FROM movies WHERE number = '%s'" % movie_number
		return self.conn.GetRow(sql)[0]

	def is_volume_loaned(self,volume):
		return self.conn.GetRow("SELECT loaned FROM volumes WHERE id = '%s'" % volume)[0]

	def is_collection_loaned(self,collection):
		return self.conn.GetRow("SELECT loaned FROM collections WHERE id = '%s'" % collection)[0]

	def convert_from_sqlite2(self, source_file, destination_file):	#{{{
		try:
			import sqlite
		except:
			self.debug.show("SQLite2 conversion: please install pysqlite legacy (v1.0) - more info in README file")
			return False

		def copy_table(sqlite2_cursor, adodb_conn, table_name):
			sqlite2_cursor.execute("SELECT * FROM %s"%table_name)
			data = sqlite2_cursor.fetchall()
			for row in data:
				query = "INSERT INTO %s("%table_name
				for column in row.keys():
					query += column+','
				query = query[:len(query)-1]
				query += ") VALUES ("
				for value in row:
					if value == None:
						query += "NULL,"
					else:
						query += "'%s'"%gutils.gescape(str(value)) + ','
				query = query[:len(query)-1] + ');'
				adodb_conn.Execute(query)

		from tempfile import mkdtemp
		from shutil import rmtree, move
		tmp_dir=mkdtemp()

		sqlite2_con = sqlite.connect(source_file,autocommit=1)
		sqlite2_cursor = sqlite2_con.cursor()

		new_db = GriffithSQL(self.config, self.debug, tmp_dir)
		# remove default values
		new_db.conn.Execute("DELETE FROM volumes")
		new_db.conn.Execute("DELETE FROM collections")
		new_db.conn.Execute("DELETE FROM media")
		new_db.conn.Execute("DELETE FROM languages")
		new_db.conn.Execute("DELETE FROM tags")

		copy_table(sqlite2_cursor, new_db.conn, "movies")
		copy_table(sqlite2_cursor, new_db.conn, "people")
		copy_table(sqlite2_cursor, new_db.conn, "media")
		copy_table(sqlite2_cursor, new_db.conn, "loans")
		try:
			copy_table(sqlite2_cursor, new_db.conn, "volumes")
			copy_table(sqlite2_cursor, new_db.conn, "collections")
			copy_table(sqlite2_cursor, new_db.conn, "languages")
			copy_table(sqlite2_cursor, new_db.conn, "movie_lang")
			copy_table(sqlite2_cursor, new_db.conn, "movie_tag")
			copy_table(sqlite2_cursor, new_db.conn, "tags")
		except:
			pass

		move(os.path.join(tmp_dir,self.config["default_db"]), destination_file)
		self.debug.show("Cnnvert from SQLite2: " + destination_file + " created")
		new_db.conn.Close();
		rmtree(tmp_dir)
		return True	#}}}
# vim: fdm=marker
