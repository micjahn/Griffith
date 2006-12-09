# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes, Piotr Ożarowski
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

from gettext import gettext as _
from sqlalchemy import *
import os.path
import gutils
import gtk

class DBTable(object):
	def __repr__(self):
		return "%s:%s" % (self.__class__.__name__, self.name)
	def add_to_db(self):
		if self.name is None or len(self.name)==0:
			debug.show("%s: name can't be empty" % self.__class__.__name__)
			return False
		# check if achannel already exists
		if self.get_by(name=self.name) is not None:
			debug.show("%s: '%s' already exists" % (self.__class__.__name__, self.name))
			return False
		debug.show("%s: adding '%s' to database..." % (self.__class__.__name__, self.name))
		self.save()
		self.flush()
		self.refresh()
		return True
	def remove_from_db(self):
		dbtable_id = self.__dict__[self.__class__.__name__.lower() + '_id']
		if dbtable_id<1:
			debug.show("%s: none selected => none removed" % self.__class__.__name__)
			return False
		tmp = None
		if hasattr(self,'movies'):
			tmp = getattr(self,'movies')
		elif hasattr(self,'movielangs'):
			tmp = getattr(self,'movielangs')
		if tmp and len(tmp)>0:
			gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
			return False
		debug.show("%s: removing '%s' (id=%s) from database..."%(self.__class__.__name__, self.name, dbtable_id))
		self.delete()
		self.flush()
		#self.refresh()
		return True
	def update_in_db(self):
		dbtable_id = self.__dict__[self.__class__.__name__.lower() + '_id']
		if dbtable_id<1:
			debug.show("%s: none selected => none updated" % self.__class__.__name__)
			return False
		if self.name is None or len(self.name)==0:
			debug.show("%s: name can't be empty" % self.__class__.__name__)
			return False
		if self.get_by(name=self.name) is not None:
			gutils.warning(self, msg=_("This name is already in use!"))
			return False
		self.update()
		self.flush()
		self.refresh()
		return True

class GriffithSQL:
	version = 2	# database format version, incrase after any changes in data structures
	metadata = None
	class Configuration(object):
		def __repr__(self):
			return "Config:%s=%s" % (self.param, self.value)
	class AChannel(DBTable):
		pass
	class ACodec(DBTable):
		pass
	class Collection(DBTable):
		pass
	class Lang(DBTable):
		pass
	class Medium(DBTable):
		pass
	class MovieLang(object):
		def __repr__(self):
			return "MovieLang:%s-%s (Type:%s ACodec:%s AChannel:%s SubFormat:%s)" % (self.movie_id, self.lang_id, self.type, self.acodec_id, self.achannel_id, self.subformat_id)
	class MovieTag(object):
		def __repr__(self):
			return "MovieTag:%s-%s" % (self.movie_id, self.tag_id)
	class Person(DBTable):
		pass
	class SubFormat(DBTable):
		pass
	class Tag(DBTable):
		def remove_from_db(self):
			if len(self.movietags) > 0:
				gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
				return False
			return DBTable.remove_from_db(self)
	class VCodec(DBTable):
		pass
	class Volume(DBTable):
		pass
	class Loan(object):#{{{
		def __repr__(self):
			return "Loan:%s (movie:%s person:%s)" % (self.loan_id, self.movie_id, self.person_id)
		def __setitem__(self, key, value):
			if key == 'movie_id' and value:
				if GriffithSQL.Movie.get_by(movie_id=value) is None:
					raise Exception('wrong movie_id')
			elif key == 'person_id' and value:
				if GriffithSQL.Person.get_by(person_id=value) is None:
					raise Exception('wrong movie_id')
			self[key] = value
		def _validate(self):
			if self.movie_id is None:
				raise Exception('movie_id is not set')
			if self.person_id is None:
				raise Exception('person_id is not set')
			if self.movie is None:
				self.movie = GriffithSQL.Movie.get_by(movie_id=self.movie_id)
				if self.movie is None:
					raise Exception('wrong movie_id')
			if self.person is None:
				self.person = GriffithSQL.Person.get_by(person_id=self.person_id)
				if self.person is None:
					raise Exception('wrong person_id')
			if self.collection_id>0 and self.collection is None:
				self.collection = GriffithSQL.Collection.get_by(collection_id=self.collection_id)
				if self.collection is None:
					raise Exception('wrong collection_id')
			if self.volume_id>0 and self.volume is None:
				self.volume = GriffithSQL.Volume.get_by(volume_id=self.volume_id)
				if self.volume is None:
					raise Exception('wrong volume_id')
			return True
		def set_loaned(self):
			"""
			Set loaned=True for all movies in volume/collection and for movie itself
			Set loan's date to today's date
			"""
			self._validate()

			if self.collection is not None:
				self.movie.mapper.mapped_table.update(self.movie.c.collection_id==self.collection_id).execute(loaned=True)
				self.collection.loaned = True
				self.collection.update()
			if self.volume is not None:
				self.movie.mapper.mapped_table.update(self.movie.c.volume_id==self.volume_id).execute(loaned=True)
				self.volume.loaned = True
				self.volume.update()
			if self.movie is None:
				self.movie = Movie.get_by(movie_id=self.movie_id)
			self.movie.loaned = True
			self.movie.update()
			if self.date is None:
				self.date = func.current_date()	# update loan date
			self.return_date is None
			self.save_or_update()
			self.mapper.get_session().flush()
			self.refresh()
			return True
		def set_returned(self):
			"""
			Set loaned=False for all movies in volume/collection and for movie itself.
			Set return_date to today's date
			"""
			self._validate()
			if self.collection is not None:
				self.movie.mapper.mapped_table.update(self.movie.c.collection_id==self.collection_id).execute(loaned=False)
				self.collection.loaned = False
				self.collection.update()
			if self.volume_id is not None:
				self.movie.mapper.mapped_table.update(self.movie.c.volume_id==self.volume_id).execute(loaned=False)
				self.volume.loaned = False
				self.volume.update()
			self.movie.loaned = False
			self.movie.update()
			if self.return_date is None:
				self.return_date = func.current_date()
			self.save_or_update()
			self.mapper.get_session().flush()
			self.refresh()
			return True
			#}}}
	class Movie(object):#{{{
		def __repr__(self):
			return "Movie:%s (number=%s)" % (self.movie_id, self.number)
		def __init__(self):
			# self.number = find_next_available() # TODO
			pass
		def __setitem__(self, key, value):
			setattr(self,key,value)
		def __getitem__(self, key):
			return getattr(self,key)
		def has_key(self, key):
			if key in ('volume','collection','medium','vcodec','loans','tags','languages','lectors','dubbings','subtitles'):
				return True
			else:
				return self.c.has_key(key)
		def remove_from_db(self):
			if self.loaned == True:
				debug.show("You can't remove loaned movie!")
				return False
			self.delete()
			self.flush()
			return True
		def update_in_db(self, t_movies=None):
			if self.movie_id < 1:
				raise Exception('movie_id is not set')
			if t_movies is not None:
				self.languages.clear()
				self.tags.clear()
				#self.mapper.mapped_table.update(self.c.movie_id==t_movies['movie_id']).execute(t_movies)
			return self.add_to_db(t_movies)
		def add_to_db(self, t_movies=None):
			if t_movies is not None:
				t_tags = t_languages = None
				if t_movies.has_key('tags'):
					t_tags = t_movies.pop('tags')
				if t_movies.has_key('languages'):
					t_languages = t_movies.pop('languages')
				for i in self.c.keys():
					if t_movies.has_key(i):
						self[i] = t_movies[i]
				# languages
				if t_languages is not None:
					for lang in t_languages:
						if lang[0]>0:
							ml = GriffithSQL.MovieLang(lang_id=lang[0], type=lang[1],
								acodec_id=lang[2], achannel_id=lang[3], subformat_id=lang[4])
							self.languages.append(ml)
				# tags
				if t_tags is not None:
					for tag in t_tags.keys():
						self.tags.append(GriffithSQL.Tag(tag_id=tag))
			self.update()
			self.flush()
			self.refresh()
			return True
		#}}}

	def __init__(self, config, gdebug, griffith_dir):	#{{{
		from sqlalchemy.mods.threadlocal import assign_mapper
		global debug
		debug = gdebug
		if not config.has_key('db_type'):
			config['db_type'] = 'sqlite'

		if config['db_type'] != 'sqlite':
			if not config.has_key('db_host'):
				config['db_host'] = '127.0.0.1'
			if not config.has_key('db_user'):
				config['db_user'] = 'griffith'
			if not config.has_key('db_passwd'):
				config['db_passwd'] = 'gRiFiTh'
			if not config.has_key('db_name'):
				config['db_name'] = 'griffith'

		# connect to database --------------------------------------{{{
		if config['db_type'] == 'sqlite':
			url = "sqlite:///%s" % os.path.join(griffith_dir, config['default_db'])
		elif config['db_type'] == 'postgres':
			if not config.has_key('db_port') or config['db_port']==0:
				config['db_port'] = 5432
			url = "postgres://%s:%s@%s:%d/%s" % (
				config['db_user'],
				config['db_passwd'],
				config['db_host'],
				int(config['db_port']),
				config['db_name'])
		elif config['db_type'] == 'mysql':
			if not config.has_key('db_port') or config['db_port']==0:
				config['db_port'] = 3306
			url = "mysql://%s:%s@%s:%d/%s" % (
				config['db_user'],
				config['db_passwd'],
				config['db_host'],
				int(config['db_port']),
				config['db_name'])
		self.metadata = BoundMetaData(url)
		# try to establish a db connection
		try:
			self.metadata.engine.connect()
		except:
			gutils.error(self, _('Database connection failed.'))
			self.config['db_type'] = 'sqlite'
			url = "sqlite:///%s" % os.path.join(griffith_dir, 'griffith.db')
			self.metadata = BoundMetaData(url)
			self.metadata.engine.connect()
		#}}}

		# prepare tables interface ---------------------------------{{{
		movies = Table('movies', self.metadata,
			Column('movie_id', Integer, primary_key = True),
			Column('number', Integer, nullable=False, unique=True),
			Column('collection_id', Integer, ForeignKey('collections.collection_id'), default=None),
			Column('volume_id', Integer, ForeignKey('volumes.volume_id'), default=None),
			Column('medium_id', Smallinteger, ForeignKey('media.medium_id'), default=None),
			Column('vcodec_id', Smallinteger, ForeignKey('vcodecs.vcodec_id'), default=None),
			Column('loaned', Boolean, nullable=False, default=False),
			Column('seen', Boolean, nullable=False, default=False),
			Column('rating', Smallinteger(2), nullable=False, default=0),
			Column('color', Smallinteger, default=3),
			Column('cond', Smallinteger, default=5),	# MySQL will not accept name "condition"
			Column('layers', Smallinteger, default=4),
			Column('region', Smallinteger, default=9),
			Column('media_num', Smallinteger),
			Column('runtime', Integer),
			Column('year', Integer),
			Column('o_title', VARCHAR(255)),
			Column('title', VARCHAR(255)),
			Column('director', VARCHAR(255)),
			Column('o_site', VARCHAR(255)),
			Column('site', VARCHAR(255)),
			Column('trailer', VARCHAR(256)),
			Column('country', VARCHAR(128)),
			Column('genre', VARCHAR(128)),
			Column('image', VARCHAR(128)),
			Column('studio', VARCHAR(128)),
			Column('classification', VARCHAR(128)),
			Column('cast', TEXT),
			Column('plot', TEXT),
			Column('notes', TEXT))
		loans = Table('loans', self.metadata,
			Column('loan_id', Integer, primary_key=True),
			Column('person_id', Integer, ForeignKey('people.person_id'), nullable=False),
			Column('movie_id', Integer, ForeignKey('movies.movie_id'), nullable=False),
			Column('volume_id', Integer, ForeignKey('volumes.volume_id')),
			Column('collection_id', Integer, ForeignKey('collections.collection_id')),
			Column('date', Date, nullable=False, default=func.current_date()),
			Column('return_date', Date, nullable=True))
		people = Table('people', self.metadata,
			Column('person_id', Integer, primary_key=True),
			Column('name', VARCHAR(255), nullable=False, unique=True),
			Column('email', VARCHAR(128)),
			Column('phone', VARCHAR(64)))
		volumes = Table('volumes', self.metadata,
			Column('volume_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True),
			Column('loaned', Boolean, nullable=False, default=False))
		collections = Table('collections', self.metadata,
			Column('collection_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True),
			Column('loaned', Boolean, nullable=False, default=False))
		media = Table('media', self.metadata,
			Column('medium_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True))
		languages = Table('languages', self.metadata,
			Column('lang_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True))
		vcodecs = Table('vcodecs', self.metadata,
			Column('vcodec_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True))
		acodecs = Table('acodecs', self.metadata,
			Column('acodec_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True))
		achannels = Table('achannels', self.metadata,
			Column('achannel_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True))
		subformats = Table('subformats', self.metadata,
			Column('subformat_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True))
		tags = Table('tags', self.metadata,
			Column('tag_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique=True))
		movie_lang = Table('movie_lang', self.metadata,
			Column('ml_id', Integer, primary_key=True),
			Column('type', Smallinteger), # 0: Original, 1:lector, 2:dubbing, 3:subtitle 
			Column('movie_id', Integer, ForeignKey('movies.movie_id'), nullable=False),
			Column('lang_id', Integer, ForeignKey('languages.lang_id'), nullable=False),
			Column('acodec_id', Integer, ForeignKey('acodecs.acodec_id'), nullable=True),
			Column('achannel_id', Integer, ForeignKey('achannels.achannel_id'), nullable=True),
			Column('subformat_id', Integer, ForeignKey('subformats.subformat_id'), nullable=True))
		movie_tag = Table('movie_tag', self.metadata,
			Column('mt_id', Integer, primary_key=True),
			Column('movie_id', Integer, ForeignKey('movies.movie_id')),
			Column('tag_id', Integer, ForeignKey('tags.tag_id')))
		configuration = Table('configuration', self.metadata,
			Column('param', VARCHAR(16), primary_key=True),
			Column('value', VARCHAR(128), nullable=False))#}}}

		# mappers -------------------------------------------------#{{{
		assign_mapper(self.Configuration, configuration)
		assign_mapper(self.Volume,volumes, properties={
			'movies': relation(self.Movie, backref='volume')})
		assign_mapper(self.Collection, collections, properties={
			'movies': relation(self.Movie, backref='collection')})
		assign_mapper(self.Medium, media, properties={
			'movies': relation(self.Movie, backref='medium')})
		assign_mapper(self.VCodec, vcodecs, properties={
			'movies': relation(self.Movie, backref='vcodec')})
		assign_mapper(self.Person, people)
		assign_mapper(self.MovieLang, movie_lang, primary_key=[movie_lang.c.ml_id], properties = {
			'movie'    : relation(self.Movie, lazy=False),
			'language' : relation(self.Lang, lazy=False),
			'achannel' : relation(self.AChannel),
			'acodec'   : relation(self.ACodec),
			'subformat': relation(self.SubFormat)})
		assign_mapper(self.ACodec, acodecs, properties={
			'movielangs': relation(self.MovieLang, lazy=False)})
		assign_mapper(self.AChannel, achannels, properties={
			'movielangs': relation(self.MovieLang, lazy=False)})
		assign_mapper(self.SubFormat, subformats, properties={
			'movielangs': relation(self.MovieLang, lazy=False)})
		assign_mapper(self.Lang, languages, properties={
			'movielangs': relation(self.MovieLang, lazy=False)})
		assign_mapper(self.MovieTag, movie_tag)
		assign_mapper(self.Tag, tags, properties={'movietags': relation(self.MovieTag, backref='tag')})
		assign_mapper(self.Loan, loans, properties = {
			'person'     : relation(self.Person),
			'volume'     : relation(self.Volume),
			'collection' : relation(self.Collection)})
		assign_mapper(self.Movie, movies, order_by=movies.c.number , properties = {
			'loans'      : relation(self.Loan, backref='movie', cascade='all, delete-orphan'),
			#'tags'       : relation(self.Tag, cascade='all, delete-orphan', secondary=movie_tag,
			'tags'       : relation(self.Tag, secondary=movie_tag,
					primaryjoin=movies.c.movie_id==movie_tag.c.movie_id,
					secondaryjoin=movie_tag.c.tag_id==tags.c.tag_id),
			'languages'  : relation(self.MovieLang, cascade='all, delete-orphan')})#}}}
		
		# check if database needs upgrade
		try:
			v = self.Configuration.get_by(param='version')	# returns None if table exists && param ISNULL
		except exceptions.SQLError:	# table doesn't exist
			v = 1

		if v==1:
			#self.Person.select().execute()
			try:
				# NOTE: "people" table is common for all versions
				self.Person.select().execute()
			except exceptions.SQLError:	# table doesn't exist
				v=0
		if v is not None and v>1:
			v = v.value
		if v<self.version:
			from dbupgrade import upgrade_database
			upgrade_database(self, v)
		
		# check if all tables exists
#		for table in self.metadata.tables.keys():
#		        try:
#				self.metadata.tables[table].select().execute()
#		        except:
#				self.metadata.tables[table].create()
#			self.metadata.commit()

	#}}}

	# DATABASE ---------------------------------------------------------{{{
	def drop_database(self):
		if self.metadata.name == 'postgres':
			self.metadata.execute('DROP TABLE loans CASCADE;')
			self.metadata.execute('DROP TABLE people CASCADE;')
			self.metadata.execute('DROP TABLE configuration CASCADE;')
			self.metadata.execute('DROP TABLE languages CASCADE;')
			self.metadata.execute('DROP TABLE movies CASCADE;')
			self.metadata.execute('DROP TABLE vcodecs CASCADE;')
			self.metadata.execute('DROP TABLE volumes CASCADE;')
			self.metadata.execute('DROP TABLE media CASCADE;')
			self.metadata.execute('DROP TABLE collections CASCADE;')
			self.metadata.execute('DROP TABLE acodecs CASCADE;')
			self.metadata.execute('DROP TABLE achannels CASCADE;')
			self.metadata.execute('DROP TABLE subformats CASCADE;')
			self.metadata.execute('DROP TABLE movie_tag CASCADE;')
			self.metadata.execute('DROP TABLE movie_lang CASCADE;')
			self.metadata.execute('DROP TABLE tags CASCADE;')
		else:
#			for table in self.metadata.tables.keys():
#				self.metadata.tables[table].drop()
			self.Loan.mapper.mapped_table.drop()
			self.Person.mapper.mapped_table.drop()
			self.Configuration.mapper.mapped_table.drop()
			self.VCodec.mapper.mapped_table.drop()
			self.ACodec.mapper.mapped_table.drop()
			self.AChannel.mapper.mapped_table.drop()
			self.SubFormat.mapper.mapped_table.drop()
			self.Medium.mapper.mapped_table.drop()
			self.Lang.mapper.mapped_table.drop()
			self.Volume.mapper.mapped_table.drop()
			self.Collection.mapper.mapped_table.drop()
			self.Movie.mapper.mapped_table.drop()
			self.MovieTag.mapper.mapped_table.drop()
			self.MovieLang.mapper.mapped_table.drop()
			self.Tag.mapper.mapped_table.drop()
			#objectstore.commit()
	#}}}

	# LOANS ------------------------------------------------------------{{{
	# TODO: move to loan.py
	def get_loan_info(self, movie_id, volume_id=None, collection_id=None):
		"""Returns current collection/volume/movie loan data"""
		if collection_id>0 and volume_id>0:
			return self.Loan.get_by(
					and_(or_(self.Loan.c.collection_id==collection_id,
							self.Loan.c.volume_id==volume_id,
							self.Loan.c.movie_id==movie_id),
						self.Loan.c.return_date==None))
		elif collection_id>0:
			return self.Loan.get_by(
					and_(or_(self.Loan.c.collection_id==collection_id,
							self.Loan.c.movie_id==movie_id)),
						self.Loan.c.return_date==None)
		elif volume_id>0:
			return self.Loan.get_by(and_(or_(self.Loan.c.volume_id==volume_id,
								self.Loan.c.movie_id==movie_id)),
							self.Loan.c.return_date==None)
		else:
			return self.Loan.get_by(self.Loan.c.movie_id==movie_id,self.Loan.c.return_date==None)

	def get_loan_history(self, movie_id, volume_id=None, collection_id=None):
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

# for debugging (run: ipython sql.py)
if __name__ == '__main__':
	import sys
	import config, gdebug
	from initialize import locations, location_posters
	locations = locations()
	conf = config.Config(os.path.join(locations['home'], 'griffith.conf'))
	location_posters(locations, conf)
	db = GriffithSQL(conf, gdebug.GriffithDebug(True), locations['home'])
	if len(sys.argv)>1:
		if sys.argv[1] == 'echo':
			db.metadata.engine.echo = True # print SQL queries
	print '\nGriffithSQL test drive\n======================'
	print "Engine: %s" % (db.metadata.engine.name)
	print 'Database object name: db\n'

# vim: fdm=marker
