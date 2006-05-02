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
	class Movie(object):#{{{
		def __repr__(self):
			return "Movie:%s (number=%s)" % (self.movie_id, self.number)
		def __init__(self):
			# self.number = find_next_available() # TODO
			pass
		def remove(self):
			if int(self.loaned)==1:
				debug.show("You can't remove loaned movie!")
				return False
			for i in self.tags:
				i.delete()
			for i in self.languages:
				i.delete()
			self.delete()
			objectstore.commit()#}}}
	class Configuration(object):
		def __repr__(self):
			return "Config:%s=%s" % (self.param, self.value)
	class AChannel(object):#{{{
		def __repr__(self):
			return "Achannel:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("AChannel: name can't be empty")
				return False
			# check if achannel already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("AChannel: '%s' already exists"%self.name)
				return False
			debug.show("AChannel; adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.achannel_id<1:
				debug.show("AChannel: none selected => none removed")
				return False
			if len(self.assigned_movie_ids)>0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("AChannel: removing '%s' (id=%s) from database..."%(self.name, self.achannel_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.achannel_id<1:
				debug.show("AChannel: none selected => none updated")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("AChannel: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}
	class ACodec(object):#{{{
		def __repr__(self):
			return "Acodec:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("ACodec: name can't be empty")
				return False
			# check if acodec already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("ACodec: '%s' already exists"%self.name)
				return False
			debug.show("ACodec; adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.acodec_id<1:
				debug.show("ACodec: none selected => none removed")
				return False
			if len(self.assigned_movie_ids)>0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("ACodec: removing '%s' (id=%s) from database..."%(self.name, self.acodec_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.acodec_id<1:
				debug.show("ACodec: none selected => none updated")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("ACodec: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}
	class Collection(object):#{{{
		def __repr__(self):
			return "Collection:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("Collection: name can't be empty")
				return False
			# check if collection already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("Collection: '%s' already exists"%self.name)
				return False
			debug.show("Collection: adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.collection_id<1:
				debug.show("Collection: none selected => none removed")
				return False
			if self.loaned or len(self.assigned_movies)>0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("Collection: removing '%s' (id=%s) from database..."%(self.name, self.collection_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.collection_id<1:
				debug.show("Collection: none selected => none updated")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("Collection: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}
	class Language(object):#{{{
		def __repr__(self):
			return "Language:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("Language: name can't be empty")
				return False
			# check if language already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("Language: '%s' already exists"%self.name)
				return False
			debug.show("Language: adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.language_id<1:
				debug.show("Language: none selected => none removed")
				return False
			if len(self.assigned_movie_ids)>0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("Language: removing '%s' (id=%s) from database..."%(self.name, self.language_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.language_id<1:
				debug.show("Language: none selected => none removed")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("Language: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}
	class Loan(object):#{{{
		def __repr__(self):
			return "Loan:%s" % self.id
		def set_loaned(self):
			"""
			Set loaned=True for all movies in volume/collection and for movie itself
			Set loan's date to today's date
			"""
			if self.collection_id>0:
				for movie in self.movie.mapper.select_by(collection_id=self.collection_id):
					movie.loaned = True
				self.collection.loaned = True
			if self.volume_id>0:
				for movie in self.movie.mapper.select_by(volume_id=self.volume_id):
					movie.loaned = True
				self.volume.loaned = True
			if self.movie_id>0:
				self.movie.loaned = True
			self.date = func.current_date()	# update loan date
			self.return_date = None
			objectstore.commit()
		def set_returned(self):
			"""
			Set loaned=False for all movies in volume/collection and for movie itself.
			Set return_date to today's date
			"""
			if self.collection_id>0:
				for movie in self.movie.mapper.select_by(collection_id=self.collection_id):
					movie.loaned = False
				self.collection.loaned = False
			if self.volume_id>0:
				for movie in self.movie.mapper.select_by(volume_id=self.volume_id):
					movie.loaned = False
				self.volume.loaned = False
			if self.movie_id>0:
				self.movie.loaned = False
			self.return_date = func.current_date()
			objectstore.commit()#}}}
	class Medium(object):#{{{
		def __repr__(self):
			return "Medium:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("Medium: name can't be empty")
				return False
			# check if medium already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("Medium: '%s' already exists"%self.name)
				return False
			debug.show("Medium; adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.medium_id<1:
				debug.show("Medium: none selected => none removed")
				return False
			if len(self.assigned_movies)>0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("Medium: removing '%s' (id=%s) from database..."%(self.name, self.medium_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.medium_id<1:
				debug.show("Medium: none selected => none updated")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("Medium: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}
	class MovieLanguage(object):
		def __repr__(self):
			return "MovieLanguage:%s-%s (Type:%s ACodec:%s AChannel:%s)" % (self.movie_id, self.lang_id, self.type, self.acodec_id, self.achannel_id)
	class MovieTag(object):
		def __repr__(self):
			return "MovieTag:%s-%s" % (self.movie_id, self.tag_id)
	class Person(object):
		def __repr__(self):
			return "Person:%s" % self.name
	class Tag(object):#{{{
		def __repr__(self):
			return "Tag:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("Tag: name can't be empty")
				return False
			# check if tag already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("Tag: '%s' already exists"%self.name)
				return False
			debug.show("Tag: adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.tag_id<1:
				debug.show("Tag: none selected => none removed")
				return False
			if len(self.assigned_movies) > 0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("Tag: removing '%s' (id=%s) from database..."%(self.name, self.tag_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.tag_id<1:
				debug.show("Tag: none selected => none removed")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("Tag: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}
	class VCodec(object):#{{{
		def __repr__(self):
			return "VCodec:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("VCodec: name can't be empty")
				return False
			# check if tag already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("VCodec: '%s' already exists"%self.name)
				return False
			debug.show("VCodec: adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.tag_id<1:
				debug.show("VCodec: none selected => none removed")
				return False
			if len(self.assigned_movies)>0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("VCodec: removing '%s' (id=%s) from database..."%(self.name, self.tag_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.tag_id<1:
				debug.show("VCodec: none selected => none removed")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("VCodec: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}
	class Volume(object):#{{{
		def __repr__(self):
			return "Volume:%s" % self.name
		def add(self):
			if self.name==None or len(self.name)==0:
				debug.show("Volume: name can't be empty")
				return False
			# check if volume already exists
			if self.mapper.get_by(name=self.name) != None:
				debug.show("Volume: '%s' already exists"%self.name)
				return False
			debug.show("Volume: adding '%s' to database..."%self.name)
			self.commit()
			return True
		def remove(self):
			if self.volume_id<1:
				debug.show("Volume: none selected => none removed")
				return False
			if self.loaned or len(self.assigned_movies)>0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			debug.show("Volume: removing '%s' (id=%s) from database..."%(self.name, self.volume_id))
			self.delete()
			self.commit()
			return True
		def update(self):
			if self.volume_id<1:
				debug.show("Volume: none selected => none removed")
				return False
			if self.name==None or len(self.name)==0:
				debug.show("Volume: name can't be empty")
				return False
			if self.mapper.get_by(name=self.name) != None:
				gutils.warning(self, msg=_("This name is already in use!"))
				return False
			self.commit()
			return True#}}}

	def __init__(self, config, gdebug, griffith_dir):	#{{{
		self.griffith_dir = griffith_dir
		self.config = config
		global debug
		debug = gdebug
		if not config.has_key("db_type"):
			config["db_type"] = "sqlite"

		# detect SQLite2 and convert to SQLite3
		if config["db_type"] == "sqlite":
			filename = os.path.join(griffith_dir, config["default_db"])
			if os.path.isfile(filename) and open(filename).readline()[:47] == "** This file contains an SQLite 2.1 database **":
				debug.show("SQLite2 database format detected. Converting...")
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

		# connect to database --------------------------------------{{{
		if config["db_type"] == "sqlite":
			self.engine = create_engine('sqlite', {'filename':os.path.join(griffith_dir, config["default_db"])})
		elif config["db_type"] == "postgres":
			if not config.has_key("db_port"):
				config["db_port"] = "5432"
			self.engine = create_engine('postgres', {
				'database' : config["db_name"],
				'host'     : config["db_host"],
				'port'     : config["db_port"],
				'user'     : config["db_user"],
				'password' : config["db_passwd"]})
		elif config["db_type"] == "mysql":
			if not config.has_key("db_port"):
				config["db_port"] = "3306"
			self.engine = create_engine('mysql', {
				'db'     : config["db_name"],
				'host'   : config["db_host"],
				'port'   : config["db_port"],
				'user'   : config["db_user"],
				'passwd' : config["db_passwd"]})
		
		# try to establish a db connection
		try:
			self.engine.connection()
		except:
			gutils.error(self, _("Database connection failed."))
			self.config["db_type"] = "sqlite"
			self.engine = create_engine('sqlite', {'filename':os.path.join(griffith_dir, "griffith,db")})

		self.objectstore = objectstore#}}}

		# prepare tables inter0face ---------------------------------{{{
		movies = Table("movies", self.engine,
			Column("movie_id", Integer, primary_key = True),
			Column("number", Integer, nullable=False, unique="movie_number_key"),
			Column("collection_id", Integer, ForeignKey("collections.collection_id"), default=None),
			Column("volume_id", Integer, ForeignKey("volumes.volume_id"), default=None),
			Column("medium_id", Smallinteger, ForeignKey('media.medium_id'), default=None),
			Column("vcodec_id", Smallinteger, ForeignKey('vcodecs.vcodec_id'), default=None),
			Column("loaned", Boolean, nullable=False, default=False, index="movie_loaned_idx"),
			Column("seen", Boolean, nullable=False, default=False, index="movie_seen_idx"),
			Column("rating", Smallinteger(2), nullable=False, default=0),
			Column("color", Smallinteger, default=3),
			Column("cond", Smallinteger, default=5),	# MySQL will not accept name "condition"
			Column("layers", Smallinteger, default=4),
			Column("region", Smallinteger, default=9),
			Column("media_num", Smallinteger),
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
			Column("person_id", Integer, ForeignKey("people.person_id"), nullable=False),
			Column("movie_id", Integer, ForeignKey("movies.movie_id"), nullable=False),
			Column("volume_id", Integer, ForeignKey("volumes.volume_id")),
			Column("collection_id", Integer, ForeignKey("collections.collection_id")),
			Column("date", Date, nullable=False, default=func.current_date()),
			Column("return_date", Date, nullable=True))
		people = Table("people", self.engine,
			Column("person_id", Integer, primary_key=True),
			Column("name", VARCHAR(255), nullable=False, unique="person_name_key"),
			Column("email", VARCHAR(128)),
			Column("phone", VARCHAR(64)))
		volumes = Table("volumes", self.engine,
			Column("volume_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="volume_name_key"),
			Column("loaned", Boolean, nullable=False, default=False))
		collections = Table("collections", self.engine,
			Column("collection_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="collection_name_key"),
			Column("loaned", Boolean, nullable=False, default=False))
		media = Table("media", self.engine,
			Column("medium_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="medium_name_key"))
		languages = Table("languages", self.engine,
			Column("lang_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="language_name_key"))
		vcodecs = Table("vcodecs", self.engine,
			Column("vcodec_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="vcodec_name_key"))
		acodecs = Table("acodecs", self.engine,
			Column("acodec_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="acodec_name_key"))
		achannels = Table("achannels", self.engine,
			Column("achannel_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="achannel_name_key"))
		tags = Table("tags", self.engine,
			Column("tag_id", Integer, primary_key=True),
			Column("name", VARCHAR(64), nullable=False, unique="tag_name_key"))
		movie_lang = Table("movie_lang", self.engine,
			Column("id", Integer, primary_key=True),
			Column("movie_id", Integer, ForeignKey("movies.movie_id"), nullable=False),
			Column("lang_id", Integer, ForeignKey("languages.lang_id"), nullable=False),
			Column("acodec_id", Integer, ForeignKey('acodecs.acodec_id'), nullable=True),
			Column("achannel_id", Integer, ForeignKey('achannels.achannel_id'), nullable=True),
			Column("type", Smallinteger))
		movie_tag = Table("movie_tag", self.engine,
			Column("id", Integer, primary_key=True),
			Column("movie_id", Integer, ForeignKey("movies.movie_id")),
			Column("tag_id", Integer, ForeignKey("tags.tag_id")))
		configuration = Table("configuration", self.engine,
			Column("param", VARCHAR(16), primary_key=True),
			Column("value", VARCHAR(128), nullable=False))#}}}

		# mappers -------------------------------------------------#{{{
		assign_mapper(self.Configuration,configuration)
		assign_mapper(self.Volume,volumes, properties={
			'assigned_movies': relation(mapper(self.Movie, movies))})
		assign_mapper(self.Collection, collections, properties={
			'assigned_movies': relation(mapper(self.Movie, movies))})
		assign_mapper(self.Medium, media, properties={
			'assigned_movies': relation(mapper(self.Movie, movies))})
		assign_mapper(self.VCodec, vcodecs, properties={
			'assigned_movies': relation(mapper(self.Movie, movies))})
		assign_mapper(self.Person, people)
		assign_mapper(self.MovieLanguage, movie_lang)
		assign_mapper(self.ACodec, acodecs, properties={
			'assigned_movie_ids': relation(self.MovieLanguage.mapper)})
		assign_mapper(self.AChannel, achannels, properties={
			'assigned_movie_ids': relation(self.MovieLanguage.mapper)})
		assign_mapper(self.Language, languages, properties={
			'assigned_movie_ids': relation(self.MovieLanguage.mapper)})
		assign_mapper(self.MovieTag, movie_tag)
		assign_mapper(self.Tag, tags, properties={'assigned_movie_ids': relation(self.MovieTag.mapper)})
		assign_mapper(self.Movie, movies, order_by=movies.c.number , properties = {
			'volume'     : relation(self.Volume.mapper),
			'collection' : relation(self.Collection.mapper),
			'medium'     : relation(self.Medium.mapper),
			'languages'  : relation(self.MovieLanguage.mapper),
			'tags'       : relation(self.MovieTag.mapper),
			'vcodec'     : relation(self.VCodec.mapper)})
		assign_mapper(self.Loan, loans, properties = {
			'person'     : relation(self.Person.mapper),
			'movie'      : relation(self.Movie.mapper),
			'volume'     : relation(self.Volume.mapper),
			'collection' : relation(self.Collection.mapper)})#}}}
		
		# check if database needs upgrade
		try:
			v = self.Configuration.mapper.get_by(param="version")	# returns None if table exists && param ISNULL
		except exceptions.SQLError:	# table doesn't exist
			v = 1

		if v==1:
			#self.Person.mapper.table.select().execute()
			try:
				# NOTE: "people" table is common for all versions
				self.Person.mapper.table.select().execute()
			except exceptions.SQLError:	# table doesn't exist
				v=0
			except:
				raise
		if v!=None and v>1:
			v = v.value
		if v<self.version:
			self.upgrade_database(v)
		
		# check if all tables exists
#		for table in self.engine.tables.keys():
#		        try:
#				self.engine.tables[table].select().execute()
#		        except:
#				self.engine.tables[table].create()
#				self.engine.commit()

	#}}}

	# MOVIE ------------------------------------------------------------{{{
	def add_movie(self, t_movies, t_languages=None, t_tags=None):
		# remove empty fields (insert default value instead - mostly "NULL")
		for i in t_movies.keys():
			if t_movies[i] == '':
				t_movies.pop(i)
		for i in ["color","cond","layers","region","media_num"]:
			if t_movies[i] == -1:
				t_movies.pop(i)
		for i in ["volume_id","collection_id"]:
			if t_movies.has_key(i) and int(t_movies[i]) == 0:
				t_movies[i] = None
		if t_movies.has_key("year") and int(t_movies["year"]) < 1986:
			t_movies[i] = None

		self.objectstore.clear()
		self.Movie.mapper.table.insert().execute(t_movies)
		movie = self.Movie.mapper.get_by(number=t_movies['number'])

		# languages
		if t_languages != None:
			for lang in t_languages.keys():
				for type in t_languages[lang].keys():
					movie.languages.append(self.MovieLanguage(lang_id=lang, type=type))
		# tags
		if t_tags != None:
			for tag in t_tags.keys():
				movie.tags.append(self.MovieTag(tag_id=tag))
		self.objectstore.commit()
	
	def update_movie(self, t_movies, t_languages=None, t_tags=None):
		movie_id = t_movies.pop('movie_id')
		if movie_id == None:
			debug.show("Update movie: Movie ID is not set. Operation aborted!")
			return False
		# remove empty fields (insert default value instead - mostly "NULL")
		for i in t_movies.keys():
			if t_movies[i] == '':
				t_movies.pop(i)
		for i in ["color","cond","layers","region","media_num"]:
			if t_movies.has_key(i) and t_movies[i] == -1:
				t_movies.pop(i)
		for i in ["volume_id","collection_id"]:
			if t_movies.has_key(i) and int(t_movies[i]) == 0:
				t_movies[i] = None
		if t_movies.has_key("year") and int(t_movies["year"]) < 1986:
			t_movies[i] = None

		self.objectstore.clear()
		self.Movie.mapper.table.update(self.Movie.c.movie_id==movie_id).execute(t_movies)
		movie = self.Movie.mapper.get_by(movie_id=movie_id)

		# languages
		if t_languages != None:
			for lang in t_languages.keys():
				for type in t_languages[lang].keys():
					movie.languages.append(self.MovieLanguage(lang_id=lang, type=type))
		# tags
		if t_tags != None:
			for tag in t_tags.keys():
				movie.tags.append(self.MovieTag(tag_id=tag))
		self.objectstore.commit()
	# }}}

	# DATABASE ---------------------------------------------------------{{{
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
				posters_dir = os.path.join(self.griffith_dir, "posters")
				# NOTE: only used images are removed (posters are shared between various db)
				for movie in self.Movie.select():
					debug.show("NEW DB: Removing old images...")
					if movie.image != None:
						name = movie.image.encode('utf-8')
						p_file = os.path.join(posters_dir, name+".jpg")
						m_file = os.path.join(posters_dir, "m_"+name+".jpg")
						t_file = os.path.join(posters_dir, "t_"+name+"jpg")
						try:
							os.remove(p_file)
							os.remove(m_file)
							os.remove(t_file)
						except:
							pass
				parent.db.drop_database()
				if self.config["db_type"] == "sqlite":
					os.unlink(os.path.join(self.griffith_dir,self.config.get('default_db')))
					if self.config["default_db"] == "griffith.gri":
						self.config["default_db"] = "griffith.db"
				# create/connect db
				parent.db = GriffithSQL(self.config, debug, self.griffith_dir)
				parent.clear_details()
				parent.total = 0
				parent.count_statusbar()
				parent.treemodel.clear()
				from initialize	import dictionaries, people_treeview
				dictionaries(parent)
				people_treeview(parent)

	def drop_database(self):
		if self.engine.name == "postgres":
			self.engine.execute("DROP TABLE loans CASCADE;")
			self.engine.execute("DROP TABLE people CASCADE;")
			self.engine.execute("DROP TABLE configuration CASCADE;")
			self.engine.execute("DROP TABLE languages CASCADE;")
			self.engine.execute("DROP TABLE movies CASCADE;")
			self.engine.execute("DROP TABLE vcodecs CASCADE;")
			self.engine.execute("DROP TABLE volumes CASCADE;")
			self.engine.execute("DROP TABLE media CASCADE;")
			self.engine.execute("DROP TABLE collections CASCADE;")
			self.engine.execute("DROP TABLE acodecs CASCADE;")
			self.engine.execute("DROP TABLE achannels CASCADE;")
			self.engine.execute("DROP TABLE movie_tag CASCADE;")
			self.engine.execute("DROP TABLE movie_lang CASCADE;")
			self.engine.execute("DROP TABLE tags CASCADE;")
		else:
			objectstore.clear()
#			for table in self.engine.tables.keys():
#				self.engine.tables[table].drop()
			self.Loan.mapper.table.drop()
			self.Person.mapper.table.drop()
			self.Configuration.mapper.table.drop()
			self.VCodec.mapper.table.drop()
			self.ACodec.mapper.table.drop()
			self.AChannel.mapper.table.drop()
			self.Medium.mapper.table.drop()
			self.Language.mapper.table.drop()
			self.Volume.mapper.table.drop()
			self.Collection.mapper.table.drop()
			self.Movie.mapper.table.drop()
			self.MovieTag.mapper.table.drop()
			self.MovieLanguage.mapper.table.drop()
			self.Tag.mapper.table.drop()
			objectstore.commit()

	def upgrade_database(self, version):
		"""Create new db or update existing one to current format"""
		if version == 0:
			debug.show("Creating tables...")
			self.Configuration.mapper.table.create()
			self.Configuration.mapper.table.insert().execute(param="version", value=self.version)
			self.Volume.mapper.table.create()
			self.Collection.mapper.table.create()
			self.Medium.mapper.table.create()
			self.Medium.mapper.table.insert().execute(medium_id=1, name='DVD')
			self.Medium.mapper.table.insert().execute(medium_id=2, name='DVD-R')
			self.Medium.mapper.table.insert().execute(medium_id=3, name='DVD-RW')
			self.Medium.mapper.table.insert().execute(medium_id=4, name='DVD+R')
			self.Medium.mapper.table.insert().execute(medium_id=5, name='DVD+RW')
			self.Medium.mapper.table.insert().execute(medium_id=6, name='DVD-RAM')
			self.Medium.mapper.table.insert().execute(medium_id=7, name='CD')
			self.Medium.mapper.table.insert().execute(medium_id=8, name='CD-RW')
			self.Medium.mapper.table.insert().execute(medium_id=9, name='VCD')
			self.Medium.mapper.table.insert().execute(medium_id=10, name='SVCD')
			self.Medium.mapper.table.insert().execute(medium_id=11, name='VHS')
			self.Medium.mapper.table.insert().execute(medium_id=12, name='BETACAM')
			self.Medium.mapper.table.insert().execute(medium_id=13, name='LaserDisc')
			self.ACodec.mapper.table.create()
			self.ACodec.mapper.table.insert().execute(acodec_id=1, name='AC-3 Dolby audio')
			self.ACodec.mapper.table.insert().execute(acodec_id=2, name='OGG')
			self.ACodec.mapper.table.insert().execute(acodec_id=3, name='MP3')
			self.ACodec.mapper.table.insert().execute(acodec_id=4, name='MPEG-1')
			self.ACodec.mapper.table.insert().execute(acodec_id=5, name='MPEG-2')
			self.ACodec.mapper.table.insert().execute(acodec_id=6, name='AAC')
			self.ACodec.mapper.table.insert().execute(acodec_id=7, name='Windows Media Audio')
			self.VCodec.mapper.table.create()
			self.VCodec.mapper.table.insert().execute(vcodec_id=1, name='MPEG-1')
			self.VCodec.mapper.table.insert().execute(vcodec_id=2, name='MPEG-2')
			self.VCodec.mapper.table.insert().execute(vcodec_id=3, name='XviD')
			self.VCodec.mapper.table.insert().execute(vcodec_id=4, name='DivX')
			self.VCodec.mapper.table.insert().execute(vcodec_id=5, name='H.264')
			self.VCodec.mapper.table.insert().execute(vcodec_id=6, name='RealVideo')
			self.VCodec.mapper.table.insert().execute(vcodec_id=7, name='QuickTime')
			self.VCodec.mapper.table.insert().execute(vcodec_id=8, name='Windows Media Video')
			self.AChannel.mapper.table.create()
			self.AChannel.mapper.table.insert().execute(achannel_id=1, name='mono')
			self.AChannel.mapper.table.insert().execute(achannel_id=2, name='stereo')
			self.AChannel.mapper.table.insert().execute(achannel_id=3, name='5.1')
			self.AChannel.mapper.table.insert().execute(achannel_id=4, name='7.1')
			self.Person.mapper.table.create()
			self.Movie.mapper.table.create()
			self.Loan.mapper.table.create()
			self.Language.mapper.table.create()
			self.MovieLanguage.mapper.table.create()
			self.Tag.mapper.table.create()
			self.Tag.mapper.table.insert().execute(tag_id=1, name=_("Favourite"))
			self.Tag.mapper.table.insert().execute(tag_id=2, name=_("To buy"))
			self.MovieTag.mapper.table.create()
			self.engine.commit()
			return True
		if version == 1:	# fix changes between v1 and v2
			print 'not implemented yet'
			return False
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
		debug.show("Upgrading old media values...")
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

	# LOANS ------------------------------------------------------------{{{
	def get_loan_info(self, movie_id, volume_id=None, collection_id=None):
		"""Returns current collection/volume/movie loan data"""
		if collection_id>0 and volume_id>0:
			return self.Loan.select_by(
					and_(or_(self.Loan.c.collection_id==collection_id,
							self.Loan.c.volume_id==volume_id,
							self.Loan.c.movie_id==movie_id),
						self.Loan.c.return_date==None))
		elif collection_id>0:
			return self.Loan.select_by(
					and_(or_(self.Loan.c.collection_id==collection_id,
							self.Loan.c.movie_id==movie_id)),
						self.Loan.c.return_date==None,)
		elif volume_id>0:
			return self.Loan.select_by(and_(or_(self.Loan.c.volume_id==volume_id,
								self.Loan.c.movie_id==movie_id)),
							self.Loan.c.return_date==None)
		else:
			return self.Loan.select_by(self.Loan.c.movie_id==movie_id,self.Loan.c.return_date==None)

	def get_loan_history(self, movie_id=None, volume_id=None, collection_id=None):
		"""Returns collection/volume/movie loan history"""
		if collection_id>0 and volume_id>0:
			return self.Loan.select_by(and_(or_(self.Loan.c.collection_id==collection_id,
								self.Loan.c.volume_id==volume_id,
								self.Loan.c.movie_id==movie_id),
							not_(self.Loan.c.return_date==None)))
		elif collection_id>0:
			return self.Loan.select_by(and_(or_(self.Loan.c.collection_id==collection_id,
								self.Loan.c.movie_id==movie_id),
							not_(self.Loan.c.return_date==None)))
		elif volume_id>0:
			return self.Loan.select_by(and_(or_(self.Loan.c.volume_id==volume_id,
								self.Loan.c.movie_id==movie_id),
							not_(self.Loan.c.return_date==None)))
		else:
			return self.Loan.select_by(self.Loan.c.movie_id==movie_id,not_(self.Loan.c.return_date==None))
	# }}}

	# ---------------------------------------------------------------------
	def convert_from_sqlite2(self, source_file, destination_file):	#{{{ FIXME
		try:
			import sqlite
		except:
			debug.show("SQLite2 conversion: please install pysqlite legacy (v1.0)")
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

		new_db = GriffithSQL(self.config, debug, tmp_dir)
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
		debug.show("Cnnvert from SQLite2: " + destination_file + " created")
		new_db.engine.Close();
		rmtree(tmp_dir)
		return True	#}}}

# for debugging (run: ipython sql.py)
if __name__ == "__main__":
	import config, gdebug, gglobals
	db = GriffithSQL(config.Config(), gdebug.GriffithDebug(True), gglobals.griffith_dir)
	if db.engine.name == "sqlite":
		tmp = db.engine.filename
	else:
		tmp = db.engine.opts
	db.engine.echo = True # print SQL queries
	print "\nGriffithSQL test drive\n======================"
	print "Connection: %s %s" % (db.engine.name, tmp)
	print "Database object name: db\n"

# vim: fdm=marker
