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
from sqlalchemy import *
import os.path
import gutils
import gtk

class GriffithSQL:
	version = 2	# database format version, incrase after any changes in data structures
	engine = None
	class Movie(object):
		def __repr__(self):
			return "Movie:%s(num:%s)" % (self.id, self.number)
	class AChannel(object):
		def __repr__(self):
			return "Achannel:%s" % self.name
	class ACodec(object):
		def __repr__(self):
			return "Acodec:%s" % self.name
	class Collection(object):
		def __repr__(self):
			return "Collection:%s" % self.name
	class Configuration(object):
		def __repr__(self):
			return "Config:%s=%s" % (self.param, self.value)
	class Language(object):
		def __repr__(self):
			return "Language:%s" % self.name
	class Loan(object):
		def __repr__(self):
			return "Loan:%s" % self.id
	class Medium(object):
		def __repr__(self):
			return "Medium:%s" % self.name
	class MovieLanguage(object):
		def __repr__(self):
			return "Movie:%s_Lang:%s_Type:%s_ACodec:%s_AChannel:%s" % (self.movie_id, self.lang_id, self.type, self.acodec_id, self.achannel_id)
	class MovieTag(object):
		def __repr__(self):
			return "Movie-Tag:%s-%s" % (self.movie_id, self.tag_id)
	class Person(object):
		def __repr__(self):
			return "Person:%s" % self.name
	class Tag(object):
		def __repr__(self):
			return "Tag:%s" % self.name
	class VCodec(object):
		def __repr__(self):
			return "VCodec:%s" % self.name
	class Volume(object):
		def __repr__(self):
			return "Volume:%s" % self.name

	def __init__(self, config, debug, griffith_dir):	#{{{
		self.griffith_dir = griffith_dir
		self.config = config
		self.debug = debug
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
		else:
			if not config.has_key("db_host"):
				config["db_host"] = "127.0.0.1"
			if not config.has_key("db_user"):
				config["db_user"] = "griffith"
			if not config.has_key("db_passwd"):
				config["db_passwd"] = "gRiFiTh"
			if not config.has_key("db_name"):
				config["db_name"] = "griffith"

		# connect to database -----------------------------------------
		if config["db_type"] == "postgres":
			if not config.has_key("db_port"):
				config["db_port"] = "5432"
#			try:
			self.engine = create_engine('postgres', {
				'database' : config["db_name"],
				'host'     : config["db_host"],
				'user'     : config["db_user"],
				'password' : config["db_passwd"]})
#			except:
#				self.config["db_type"] = "sqlite"
#				self.config.save()
#				self.engine.Close()
#				self.engine = adodb.NewADOConnection("sqlite")
#				gutils.error(self, _("Can't connect to external database."))
		elif config["db_type"] == "mysql":
			if not config.has_key("db_port"):
				config["db_port"] = "3306"
#			try:
			self.engine = create_engine('mysql', {
				'db'     : config["db_name"],
				'host'   : config["db_host"],
				'user'   : config["db_user"],
				'passwd' : config["db_passwd"]})
#			except:
#				self.config["db_type"] = "sqlite"
#				self.config.save()
#				self.engine.Close()
#				self.engine = adodb.NewADOConnection("sqlite")
#				gutils.error(self, _("Can't connect to external database."))
		if config["db_type"] == "sqlite":
			self.engine = create_engine('sqlite', {'filename':os.path.join(griffith_dir, config["default_db"])})

		self.objectstore = objectstore

		# prepare tables interface ------------------------------------
		movies = Table("movies", self.engine,
			Column("id", Integer, primary_key = True),
			Column("number", Integer, nullable=False),
			Column("collection_id", Integer, ForeignKey("collections.id")),
			Column("volume_id", Integer, ForeignKey("volumes.id")),
			Column("media_id", Smallinteger, ForeignKey('media.id')),
			Column("vcodec_id", Smallinteger, ForeignKey('vcodecs.id')),
			Column("loaned", Boolean, nullable=False, default=False),
			Column("seen", Boolean, nullable=False, default=False),
			Column("rating", Smallinteger(2), nullable=False, default=0),
			Column("color", Smallinteger, default=3),
			Column("cond", Smallinteger, default=5),	# MySQL will not accept name "condition"
			Column("layers", Smallinteger, default=4),
			Column("region", Smallinteger, default=9),
			Column("num_media", Smallinteger),
			Column("runtime", Integer),
			Column("year", Integer),
			Column("o_title", VARCHAR(255), nullable=False),
			Column('title', VARCHAR(255)),
			Column("director", VARCHAR(255)),
			Column("o_site", VARCHAR(255)),
			Column("site", VARCHAR(255)),
			Column("trailer", VARCHAR(256)),
			Column("country", VARCHAR(128)),
			Column("genre", VARCHAR(128)),
			Column("image", VARCHAR(128)),
			Column("studio", VARCHAR(128)),
			Column("classification", VARCHAR(128)),
			Column("actors", TEXT),
			Column("plot", TEXT),
			Column("notes", TEXT))
		loans = Table("loans", self.engine,
			Column("id", Integer, primary_key=True),
			Column("person_id", Integer, ForeignKey("people.id"), nullable=False),
			Column("movie_id", Integer, ForeignKey("movies.id")),
			Column("volume_id", Integer, ForeignKey("volumes.id")),
			Column("collection_id", Integer, ForeignKey("collections.id")),
			Column("date", Date, nullable=False),
			Column("return_date", Date, nullable=True))
		people = Table("people", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(255), nullable=False),
			Column("email", VARCHAR(128)),
			Column("phone", VARCHAR(64)))
		volumes = Table("volumes", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False),
			Column("loaned", Boolean, nullable=False, default=False))
		collections = Table("collections", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False),
			Column("loaned", Boolean, nullable=False,default=False))
		media = Table("media", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False))
		languages = Table("languages", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False))
		vcodecs = Table("vcodecs", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False))
		acodecs = Table("acodecs", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False))
		achannels = Table("achannels", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False))
		tags = Table("tags", self.engine,
			Column("id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False))
		movie_lang = Table("movie_lang", self.engine,
			Column("id", Integer, primary_key=True),
			Column("movie_id", Integer, ForeignKey("movies.id"), nullable=False),
			Column("lang_id", Integer, ForeignKey("languages.id"), nullable=False),
			Column("acodec_id", Integer, ForeignKey('acodecs.id'), nullable=True),
			Column("achannel_id", Integer, ForeignKey('achannels.id'), nullable=True),
			Column("type", Smallinteger))
		movie_tag = Table("movie_tag", self.engine,
			Column("id", Integer, primary_key=True),
			Column("movie_id", Integer, ForeignKey("movies.id")),
			Column("tag_id", Integer, ForeignKey("tags.id")))
		configuration = Table("configuration", self.engine,
			Column("param", VARCHAR(16), primary_key=True),
			Column("value", VARCHAR(128), nullable=False))

		assign_mapper(self.Configuration,configuration)
		assign_mapper(self.Volume,volumes)
		assign_mapper(self.Collection, collections)
		assign_mapper(self.Medium, media)
		assign_mapper(self.VCodec, vcodecs)
		assign_mapper(self.Movie, movies, properties = {
				'volumes'     : relation(self.Volume.mapper),
				'collections' : relation(self.Collection.mapper),
				'media'       : relation(self.Medium.mapper),
				'vcodecs'     : relation(self.VCodec.mapper)})
		assign_mapper(self.Loan, loans)
		assign_mapper(self.Person, people)
		assign_mapper(self.Language, languages)
		assign_mapper(self.MovieLanguage, movie_lang)
		assign_mapper(self.ACodec, acodecs)
		assign_mapper(self.AChannel, achannels)
		assign_mapper(self.Tag, tags)
		assign_mapper(self.MovieTag, movie_tag)
		
		# check if database needs upgrade
		try:
			v = self.Configuration.mapper.get_by(param="version")	# returns None if table exists && param ISNULL
		except exceptions.SQLError:	# table doesn't exist
			try:
				self.Configuration.mapper.table.create()
			except:
				self.debug.show("Error during creating configuration table.")
				gutils.error(self, msg="Wrong permissions")
				return False
			v = None

		if v != None:
			v = v.value
		else:
			v = 1
			try:
				self.Movie.mapper.table.select().execute()
			except exceptions.SQLError:	# table doesn't exist
				v = 0 # new database
			except:
				raise
		if v<self.version:
			self.upgrade_database(v)
		
		# check if all tables exists
#                for table in self.engine.tables.keys():
#                        try:
#                                self.engine.tables[table].select().execute()
#                        except:
#                                self.engine.tables[table].create()
#                                self.engine.commit()

	#}}}

	def new_db(self, parent):	#{{{
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
				# delete db TODO: DROP CASCADE
				self.Loan.mapper.table.drop()
				self.Person.mapper.table.drop()
				self.Volume.mapper.table.drop()
				self.Collection.mapper.table.drop()
				self.VCodec.mapper.table.drop()
				self.ACodec.mapper.table.drop()
				self.AChannel.mapper.table.drop()
				self.Medium.mapper.table.drop()
				self.Language.mapper.table.drop()
				self.Movie.mapper.table.drop()
				self.MovieTag.mapper.table.drop()
				self.MovieLanguage.mapper.table.drop()
				self.Tag.mapper.table.drop()
		#				self.engine.tables['tags'].drop()
				self.config["version"] = 0
				parent.db.engine.close()
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
	#}}}

	def upgrade_database(self, version):	#{{{
		"""Create new db or update existing one to current format"""
		if version == 0:
			self.debug.show("Creating tables...")
			self.Configuration.mapper.table.insert().execute(param="version", value=2)
			self.Volume.mapper.table.create()
			self.Collection.mapper.table.create()
			self.Medium.mapper.table.create()
			self.Medium.mapper.table.insert().execute(id=1, name='DVD')
			self.Medium.mapper.table.insert().execute(id=2, name='DVD-R')
			self.Medium.mapper.table.insert().execute(id=3, name='DVD-RW')
			self.Medium.mapper.table.insert().execute(id=4, name='DVD+R')
			self.Medium.mapper.table.insert().execute(id=5, name='DVD+RW')
			self.Medium.mapper.table.insert().execute(id=6, name='DVD-RAM')
			self.Medium.mapper.table.insert().execute(id=7, name='CD')
			self.Medium.mapper.table.insert().execute(id=8, name='CD-RW')
			self.Medium.mapper.table.insert().execute(id=9, name='VCD')
			self.Medium.mapper.table.insert().execute(id=10, name='SVCD')
			self.Medium.mapper.table.insert().execute(id=11, name='VHS')
			self.Medium.mapper.table.insert().execute(id=12, name='BETACAM')
			self.Medium.mapper.table.insert().execute(id=13, name='LaserDisc')
			self.ACodec.mapper.table.create()
			self.ACodec.mapper.table.insert().execute(id=1, name='AC-3 Dolby audio')
			self.ACodec.mapper.table.insert().execute(id=2, name='OGG')
			self.ACodec.mapper.table.insert().execute(id=3, name='MP3')
			self.ACodec.mapper.table.insert().execute(id=4, name='MPEG-1')
			self.ACodec.mapper.table.insert().execute(id=5, name='MPEG-2')
			self.ACodec.mapper.table.insert().execute(id=6, name='AAC')
			self.ACodec.mapper.table.insert().execute(id=7, name='Windows Media Audio')
			self.VCodec.mapper.table.create()
			self.VCodec.mapper.table.insert().execute(id=1, name='MPEG-1')
			self.VCodec.mapper.table.insert().execute(id=2, name='MPEG-2')
			self.VCodec.mapper.table.insert().execute(id=3, name='XviD')
			self.VCodec.mapper.table.insert().execute(id=4, name='DivX')
			self.VCodec.mapper.table.insert().execute(id=5, name='H.264')
			self.VCodec.mapper.table.insert().execute(id=6, name='RealVideo')
			self.VCodec.mapper.table.insert().execute(id=7, name='QuickTime')
			self.VCodec.mapper.table.insert().execute(id=8, name='Windows Media Video')
			self.AChannel.mapper.table.create()
			self.AChannel.mapper.table.insert().execute(id=1, name='mono')
			self.AChannel.mapper.table.insert().execute(id=2, name='stereo')
			self.AChannel.mapper.table.insert().execute(id=3, name='5.1')
			self.AChannel.mapper.table.insert().execute(id=4, name='7.1')
			self.Person.mapper.table.create()
			self.Movie.mapper.table.create()
			self.Loan.mapper.table.create()
			self.Language.mapper.table.create()
			self.MovieLanguage.mapper.table.create()
			self.Tag.mapper.table.create()
			self.Tag.mapper.table.insert().execute(id=1, name=_("Favourite"))
			self.Tag.mapper.table.insert().execute(id=2, name=_("To buy"))
			self.MovieTag.mapper.table.create()
			self.engine.commit()
			self.Configuration.get_by(param="version").value = self.version
			return True
		if version == 1:	# fix changes between v1 and v2
			# TODO:
			# * ranames in movie table:
			#   + media => media_id
			#   + obs => notes
			#   + site => o_site
			#   + imdb => site
			#   + original_title => o_title
			# * upgrade media table (media_id = media +1 )
			# * upgrade old media if needed
			version+=1
			#self.Configuration.get_by(param="version").value = version
		#if version == 2:	# fix changes between v2 and v3
		#	version+=1
		#	self.Configuration.get_by(param="version").value = version

	def update_old_media(self):
		self.debug.show("Upgrading old media values...")
		self.engine.execute("UPDATE movies SET media = '1' WHERE media = 'DVD';")
		self.engine.execute("UPDATE movies SET media = '2' WHERE media = 'DVD-R';")
		self.engine.execute("UPDATE movies SET media = '3' WHERE media = 'DVD-RW';")
		self.engine.execute("UPDATE movies SET media = '4' WHERE media = 'DVD+R';")
		self.engine.execute("UPDATE movies SET media = '5' WHERE media = 'DVD+RW';")
		self.engine.execute("UPDATE movies SET media = '6' WHERE media = 'DVD-RAM';")
		self.engine.execute("UPDATE movies SET media = '7' WHERE media = 'DivX';")
		self.engine.execute("UPDATE movies SET media = '7' WHERE media = 'DIVX';")
		self.engine.execute("UPDATE movies SET media = '7' WHERE media = 'XviD';")
		self.engine.execute("UPDATE movies SET media = '7' WHERE media = 'XVID';")
		self.engine.execute("UPDATE movies SET media = '7' WHERE media = 'WMV';")
		self.engine.execute("UPDATE movies SET media = '7' WHERE media = 'WMV';")
		self.engine.execute("UPDATE movies SET media = '9' WHERE media = 'VCD';")
		self.engine.execute("UPDATE movies SET media = '10' WHERE media = 'SVCD'; 	")
		self.engine.execute("UPDATE movies SET media = '11' WHERE media = 'VHS';")
		self.engine.execute("UPDATE movies SET media = '12' WHERE media = 'BETACAM';")

	def fix_old_data(self):
		self.engine.execute("UPDATE movies SET collection_id=NULL WHERE collection_id=''")
		self.engine.execute("UPDATE movies SET volume_id=NULL WHERE volume_id=''")
		self.engine.execute("UPDATE loans SET return_date=NULL WHERE return_date=''")
		self.engine.execute("UPDATE movies SET year=NULL WHERE year<1900 or year>2020")
		self.engine.execute("UPDATE movies SET rating=0 WHERE rating ISNULL")
		try:
			self.update_old_media()
		except:
			pass
	#}}}

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
		self.engine.execute(query)

		movie_id = self.get_value(field="id", table="movies", where="number = '%s'" % t_movies['number'])

		# languages
		if t_languages != None:
			for lang in t_languages.keys():
				for type in t_languages[lang].keys():
					self.engine.execute("INSERT INTO movie_lang(movie_id, lang_id, type) \
							VALUES ('%s', '%s', '%s');" % (movie_id, lang, type) )
		# tags
		if t_tags != None:
			for i in t_tags.keys():
				self.engine.execute("INSERT INTO movie_tag(movie_id, tag_id) \
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
			self.engine.execute("INSERT INTO volumes(name) VALUES ('"+gutils.gescape(name)+"');")
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
			self.engine.execute("INSERT INTO collections(name) VALUES ('"+gutils.gescape(name)+"');")
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
			self.engine.execute("INSERT INTO languages(name) VALUES ('"+gutils.gescape(name)+"');")
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
		self.engine.execute("INSERT INTO tags(name) VALUES ('"+gutils.gescape(name)+"');")
#		except:
#			return False
		return True

	# }}}

	# select data ------------------------------------------------------{{{
	def get_loan_info(self, movie_id=None, volume_id=None, collection_id=None):
		query = "SELECT * FROM loans WHERE return_date ISNULL AND "
		if collection_id>0:
			query += "collection_id='%s'" % str(collection_id)
		elif volume_id>0:
			query += "volume_id='%s'" % str(volume_id)
		else:
			query += "movie_id='%s'" % str(movie_id)
		return self.engine.execute(query)

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
		return self.engine.execute(query)
	# }}}

	# remove data ------------------------------------------------------{{{
	def remove_movie_by_num(self,number):
		if self.is_movie_loaned(movie_number=number):
			self.debug.show("Movie (number=%s) is loaned. Can't delete!")
			return False
		id = self.get_value(field="id", table="movies", where="number = '%s'" % number)
		if id != None:
			self.engine.execute("DELETE FROM movie_lang WHERE movie_id = '%s'" % id)
			self.engine.execute("DELETE FROM movie_tag WHERE movie_id = '%s'" % id)
			self.engine.execute("DELETE FROM movies WHERE number = '"+number+"'")

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
			self.engine.execute("DELETE FROM volumes WHERE id = '%s'" % id)
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
			self.engine.execute("DELETE FROM collections WHERE id = '%s'" % id)
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
			self.engine.execute("DELETE FROM languages WHERE id = '%s'" % id)
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
			self.engine.execute("DELETE FROM tags WHERE id = '%s'" % id)
		except:
				return False
		return True

	def remove_person_by_name(self, number):
		self.engine.execute("DELETE FROM people WHERE name = '"+number+"'")
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
		self.engine.execute(query)

		self.engine.execute("DELETE FROM movie_lang WHERE movie_id = '%s';" % movie_id)	# remove old data
		# languages
		if t_languages != None:
			for lang in t_languages.keys():
				for type in t_languages[lang].keys():
					self.engine.execute("INSERT INTO movie_lang(movie_id, lang_id, type) \
							VALUES ('%s', '%s', '%s');" % (movie_id, lang, type) )
		self.engine.execute("DELETE FROM movie_tag WHERE movie_id = '%s';" % movie_id)
		# tags
		if t_tags != None:
			for i in t_tags.keys():
				self.engine.execute("INSERT INTO movie_tag(movie_id, tag_id) \
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
				self.engine.execute("UPDATE collections SET name = '%s' WHERE id = '%s';"%(name,id))
			except:
				self.debug.show("ERROR during updating collection's name!")
				return False
			return True
		if loaned==1:
			try:
				self.engine.execute("UPDATE collections SET loaned=1 WHERE id='%s';" % id)
				self.engine.execute("UPDATE movies SET loaned=1 WHERE collection_id='%s';" % id)
			except:
				self.debug.show("ERROR during updating collection's loan data!")
				return False
			if volume_id:
				try:
					self.engine.execute("UPDATE volumes SET loaned=1 WHERE id='%s';"%volume_id)
				except:
					self.debug.show("ERROR during updating collection's loan data!")
					return False
			return True
		elif loaned==0:
			try:
				self.engine.execute("UPDATE collections SET loaned=0 WHERE id='%s';" % id)
				self.engine.execute("UPDATE movies SET loaned=0 WHERE collection_id='%s';" % id)
			except:
				self.debug.show("ERROR during updating collection's loan data!")
				return False
			if volume_id:
				try:
					self.engine.execute("UPDATE volumes SET loaned=0 WHERE id='%s';"%volume_id)
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
				self.engine.execute("UPDATE volumes SET name = '%s' WHERE id = '%s';"%(name,id))
			except:
				self.debug.show("ERROR during updating volume's name!")
				return False
			return True
		if loaned==1:
			try:
				self.engine.execute("UPDATE volumes SET loaned=1 WHERE id='%s';" % id)
				self.engine.execute("UPDATE movies SET loaned=1 WHERE volume_id='%s';" % id)
			except:
				self.debug.show("ERROR during updating volume's loan data!")
				return False
			return True
		elif loaned==0:
			try:
				self.engine.execute("UPDATE volumes SET loaned=0 WHERE id='%s';" % id)
				self.engine.execute("UPDATE movies SET loaned=2 WHERE volume_id='%s';" % id)
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
			self.engine.execute("UPDATE languages SET name ='%s' WHERE id='%s';" % (name, id))
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
			self.engine.execute("UPDATE tags SET name ='%s' WHERE id='%s';" % (name,id))
		except:
			self.debug.show("ERROR during updating tag name!")
			return False
		return True
	#}}}

	def count_records(self,table_name, where=None):
		query = "SELECT COUNT(id) FROM %s" % (table_name)
		if where:
			query += " WHERE %s" % where
		return int(self.engine.execute(query)[0])

	def is_movie_loaned(self,movie_id=None, movie_number=None):
		if movie_id==None and movie_number == None:
			return None
		if movie_id:
			sql = "SELECT loaned FROM movies WHERE id = '%s'" % movie_id
		if movie_number:
			sql = "SELECT loaned FROM movies WHERE number = '%s'" % movie_number
		return self.engine.GetRow(sql)[0]

	def is_volume_loaned(self,volume):
		return self.engine.GetRow("SELECT loaned FROM volumes WHERE id = '%s'" % volume)[0]

	def is_collection_loaned(self,collection):
		return self.engine.GetRow("SELECT loaned FROM collections WHERE id = '%s'" % collection)[0]

	def convert_from_sqlite2(self, source_file, destination_file):	#{{{
		try:
			import sqlite
		except:
			self.debug.show("SQLite2 conversion: please install pysqlite legacy (v1.0)")
			return False

		def copy_table(sqlite2_cursor, adodb_engine, table_name):
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
				adodb_engine.execute(query)

		from tempfile import mkdtemp
		from shutil import rmtree, move
		tmp_dir=mkdtemp()

		sqlite2_con = sqlite.connect(source_file,autocommit=1)
		sqlite2_cursor = sqlite2_con.cursor()

		new_db = GriffithSQL(self.config, self.debug, tmp_dir)
		# remove default values
		new_db.engine.execute("DELETE FROM volumes")
		new_db.engine.execute("DELETE FROM collections")
		new_db.engine.execute("DELETE FROM media")
		new_db.engine.execute("DELETE FROM languages")
		new_db.engine.execute("DELETE FROM tags")

		copy_table(sqlite2_cursor, new_db.engine, "movies")
		copy_table(sqlite2_cursor, new_db.engine, "people")
		copy_table(sqlite2_cursor, new_db.engine, "media")
		copy_table(sqlite2_cursor, new_db.engine, "loans")
		try:
			copy_table(sqlite2_cursor, new_db.engine, "volumes")
			copy_table(sqlite2_cursor, new_db.engine, "collections")
			copy_table(sqlite2_cursor, new_db.engine, "languages")
			copy_table(sqlite2_cursor, new_db.engine, "movie_lang")
			copy_table(sqlite2_cursor, new_db.engine, "movie_tag")
			copy_table(sqlite2_cursor, new_db.engine, "tags")
		except:
			pass

		move(os.path.join(tmp_dir,self.config["default_db"]), destination_file)
		self.debug.show("Cnnvert from SQLite2: " + destination_file + " created")
		new_db.engine.Close();
		rmtree(tmp_dir)
		return True	#}}}

# for debugging (run: ipython sql.py)
if __name__ == "__main__":
	import config, gdebug, gglobals
	config = config.Config()
	debug = gdebug.GriffithDebug()
	db = GriffithSQL(config, debug, gglobals.griffith_dir)
	db.engine.echo = True # print SQL queries
	print "\nGriffithSQL test drive\n======================"
	print "Connection: %s %s" % (db.engine.name, db.engine.opts)
	print "Database object name: db\n"

# vim: fdm=marker
