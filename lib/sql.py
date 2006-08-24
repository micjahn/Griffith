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
		if self.name==None or len(self.name)==0:
			debug.show("%s: name can't be empty" % self.__class__.__name__)
			return False
		# check if achannel already exists
		if self.get_by(name=self.name) != None:
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
		if hasattr(self,'assigned_movie_ids'):
			tmp = getattr(self,'assigned_movie_ids')
		elif hasattr(self,'assigned_movies'):
			tmp = getattr(self,'assigned_movies')
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
		if self.name==None or len(self.name)==0:
			debug.show("%s: name can't be empty" % self.__class__.__name__)
			return False
		if self.get_by(name=self.name) != None:
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
		pass
	class VCodec(DBTable):
		pass
	class Volume(DBTable):
		pass
	class Loan(object):#{{{
		def __repr__(self):
			return "Loan:%s (movie:%s person:%s)" % (self.loan_id, self.movie_id, self.person_id)
		def set_loaned(self):
			"""
			Set loaned=True for all movies in volume/collection and for movie itself
			Set loan's date to today's date
			"""
			if self.movie == None:
				debug.show("Loan: wrong movie_id. Aborting")
				return False
			if self.person == None:
				debug.show("Loan: wrong person_id. Aborting")
				return False
			if self.collection_id>0 and self.collection==None:
				debug.show("Loan: wrong collection_id. Aborting")
				return False
			if self.volume_id>0 and self.volume==None:
				debug.show("Loan: wrong volume_id. Aborting")
				return False
			if self.collection!=None:
				self.movie.mapper.mapped_table.update(self.movie.c.collection_id==self.collection_id).execute(loaned=True)
				self.collection.loaned = True
				self.collection.update()
			if self.volume!=None:
				self.movie.mapper.mapped_table.update(self.movie.c.volume_id==self.volume_id).execute(loaned=True)
				self.volume.loaned = True
				self.volume.update()
			self.movie.loaned = True
			self.movie.update()
			if self.date==None:
				self.date = func.current_date()	# update loan date
			self.return_date = None
			self.save_or_update()
			self.mapper.get_session().flush()
			self.refresh()
			return True
		def set_returned(self):
			"""
			Set loaned=False for all movies in volume/collection and for movie itself.
			Set return_date to today's date
			"""
			if self.movie == None:
				debug.show("Loan: wrong movie_id. Aborting")
				return False
			if self.person == None:
				debug.show("Loan: wrong person_id. Aborting")
				return False
			if self.collection_id>0 and self.collection==None:
				debug.show("Loan: wrong collection_id. Aborting")
				return False
			if self.volume_id>0 and self.volume==None:
				debug.show("Loan: wrong volume_id. Aborting")
				return False
			if self.collection!=None:
				self.movie.mapper.mapped_table.update(self.movie.c.collection_id==self.collection_id).execute(loaned=False)
				self.collection.loaned = False
				self.collection.update()
			if self.volume_id!=None:
				self.movie.mapper.mapped_table.update(self.movie.c.volume_id==self.volume_id).execute(loaned=False)
				self.volume.loaned = False
				self.volume.update()
			self.movie.loaned = False
			self.movie.update()
			if self.return_date==None:
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
		def remove_from_db(self):
			if int(self.loaned)==1:
				debug.show("You can't remove loaned movie!")
				return False
			# FIXME:
			if len(self.tags)>0:
				self.tags[0].mapper.mapped_table.delete(self.tags[0].c.movie_id==self.movie_id).execute()
			if len(self.languages)>0:
				self.languages[0].mapper.mapped_table.delete(self.languages[0].c.movie_id==self.movie_id).execute()
			self.delete()
			self.mapper.get_session().flush()
			return True#}}}

	def __init__(self, config, gdebug, griffith_dir):	#{{{
		from sqlalchemy.mods.threadlocal import assign_mapper
		self.griffith_dir = griffith_dir
		self.config = config
		global debug
		debug = gdebug
		if not config.has_key('db_type'):
			config['db_type'] = 'sqlite'

		# detect SQLite2 and convert to SQLite3
		if config['db_type'] == 'sqlite':
			filename = os.path.join(griffith_dir, config['default_db'])
			if os.path.isfile(filename) and open(filename).readline()[:47] == '** This file contains an SQLite 2.1 database **':
				debug.show('SQLite2 database format detected. Converting...')
				if self.convert_from_sqlite2(filename, os.path.join(griffith_dir, 'griffith.db')):
					self.config['default_db'] = 'griffith.db'
					self.config.save()
		else:
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
			Column('number', Integer, nullable=False, unique='movie_number_key'),
			Column('collection_id', Integer, ForeignKey('collections.collection_id'), default=None),
			Column('volume_id', Integer, ForeignKey('volumes.volume_id'), default=None),
			Column('medium_id', Smallinteger, ForeignKey('media.medium_id'), default=None),
			Column('vcodec_id', Smallinteger, ForeignKey('vcodecs.vcodec_id'), default=None),
			Column('loaned', Boolean, nullable=False, default=False, index='movie_loaned_idx'),
			Column('seen', Boolean, nullable=False, default=False, index='movie_seen_idx'),
			Column('rating', Smallinteger(2), nullable=False, default=0),
			Column('color', Smallinteger, default=3),
			Column('cond', Smallinteger, default=5),	# MySQL will not accept name "condition"
			Column('layers', Smallinteger, default=4),
			Column('region', Smallinteger, default=9),
			Column('media_num', Smallinteger),
			Column('runtime', Integer),
			Column('year', Integer),
			Column('o_title', VARCHAR(255), nullable=False),
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
			Column('actors', TEXT),
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
			Column('name', VARCHAR(255), nullable=False, unique='person_name_key'),
			Column('email', VARCHAR(128)),
			Column('phone', VARCHAR(64)))
		volumes = Table('volumes', self.metadata,
			Column('volume_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='volume_name_key'),
			Column('loaned', Boolean, nullable=False, default=False))
		collections = Table('collections', self.metadata,
			Column('collection_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='collection_name_key'),
			Column('loaned', Boolean, nullable=False, default=False))
		media = Table('media', self.metadata,
			Column('medium_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='medium_name_key'))
		languages = Table('languages', self.metadata,
			Column('lang_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='language_name_key'))
		vcodecs = Table('vcodecs', self.metadata,
			Column('vcodec_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='vcodec_name_key'))
		acodecs = Table('acodecs', self.metadata,
			Column('acodec_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='acodec_name_key'))
		achannels = Table('achannels', self.metadata,
			Column('achannel_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='achannel_name_key'))
		subformats = Table('subformats', self.metadata,
			Column('subformat_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='subformat_name_key'))
		tags = Table('tags', self.metadata,
			Column('tag_id', Integer, primary_key=True),
			Column('name', VARCHAR(64), nullable=False, unique='tag_name_key'))
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
		assign_mapper(self.Configuration, configuration, is_primary=True)
		assign_mapper(self.Volume,volumes, is_primary=True, properties={
			'assigned_movies': relation(self.Movie, backref='volume')})
		assign_mapper(self.Collection, collections, is_primary=True, properties={
			'assigned_movies': relation(self.Movie, backref='collection')})
		assign_mapper(self.Medium, media, is_primary=True, properties={
			'assigned_movies': relation(self.Movie, backref='medium')})
		assign_mapper(self.VCodec, vcodecs, is_primary=True, properties={
			'assigned_movies': relation(self.Movie, backref='vcodec')})
		assign_mapper(self.Person, people, is_primary=True)
		assign_mapper(self.MovieLang, movie_lang, is_primary=True)
		assign_mapper(self.ACodec, acodecs, is_primary=True, properties={
			'assigned_movie_ids': relation(self.MovieLang)})
		assign_mapper(self.AChannel, achannels, is_primary=True, properties={
			'assigned_movie_ids': relation(self.MovieLang)})
		assign_mapper(self.SubFormat, subformats, is_primary=True, properties={
			'assigned_movie_ids': relation(self.MovieLang)})
		assign_mapper(self.Lang, languages, is_primary=True, properties={
			'assigned_movie_ids': relation(self.MovieLang)})
		assign_mapper(self.MovieTag, movie_tag, is_primary=True)
		assign_mapper(self.Tag, tags, is_primary=True, properties={'assigned_movie_ids': relation(self.MovieTag)})
		assign_mapper(self.Loan, loans, is_primary=True, properties = {
			'person'     : relation(self.Person),
			'movie'      : relation(self.Movie),
			'volume'     : relation(self.Volume),
			'collection' : relation(self.Collection)})
		assign_mapper(self.Movie, movies, is_primary=True, order_by=movies.c.number , properties = {
			'languages'  : relation(self.MovieLang),
			'tags'       : relation(self.MovieTag)})#}}}
		
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
			except:
				raise
		if v!=None and v>1:
			v = v.value
		if v<self.version:
			self.upgrade_database(v)
		
		# check if all tables exists
#		for table in self.metadata.tables.keys():
#		        try:
#				self.metadata.tables[table].select().execute()
#		        except:
#				self.metadata.tables[table].create()
#				self.metadata.commit()

	#}}}

	# MOVIE ------------------------------------------------------------{{{
	def clean_t_movies(self, t_movies): # TODO: move outside GriffithSQL class
		for i in t_movies.keys():
			if t_movies[i] == '':
				t_movies[i]=None
		for i in ['color','cond','layers','region', 'media', 'vcodec']:
			if t_movies.has_key(i) and t_movies[i] == -1:
				t_movies[i]=None
		for i in ['volume_id','collection_id', 'runtime']:
			if t_movies.has_key(i) and (t_movies[i]==None or int(t_movies[i]) == 0):
				t_movies[i] = None
		if t_movies.has_key('year') and (t_movies['year']==None or int(t_movies['year']) < 1886):
			t_movies['year'] = None

	def add_movie(self, t_movies, t_languages=None, t_tags=None): # TODO: move to Movie class
		self.clean_t_movies(t_movies)
		self.Movie.mapper.mapped_table.insert().execute(t_movies)
		movie = self.Movie.get_by(number=t_movies['number'])
		# languages
		if t_languages != None:
			for lang in t_languages:
				if lang[0]>0:
					movie.languages.append(self.MovieLang(lang_id=lang[0], type=lang[1], acodec_id=lang[2], achannel_id=lang[3], subformat_id=lang[4]))
		# tags
		if t_tags != None:
			for tag in t_tags.keys():
				movie.tags.append(self.MovieTag(tag_id=tag))
		movie.save_or_update()
	
	def update_movie(self, t_movies, t_languages=None, t_tags=None): # TODO: move to Movie class
		movie_id = t_movies['movie_id']
		if movie_id == None:
			debug.show('Update movie: Movie ID is not set. Operation aborted!')
			return False
		self.clean_t_movies(t_movies)
		self.Movie.mapper.mapped_table.update(self.Movie.c.movie_id==movie_id).execute(t_movies)
		self.MovieLang.mapper.mapped_table.delete(self.MovieLang.c.movie_id==movie_id).execute()
		self.MovieTag.mapper.mapped_table.delete(self.MovieTag.c.movie_id==movie_id).execute()
		movie = self.Movie.get_by(movie_id=movie_id)
		# languages
		if t_languages != None:
			for lang in t_languages:
				if lang[0]>0:
					movie.languages.append(self.MovieLang(lang_id=lang[0], type=lang[1], acodec_id=lang[2], achannel_id=lang[3], subformat_id=lang[4]))
		# tags
		if t_tags != None:
			for tag in t_tags.keys():
				movie.tags.append(self.MovieTag(tag_id=tag))
		movie.update()
		movie.flush()
		movie.refresh()
	# }}}

	# DATABASE ---------------------------------------------------------{{{
	def new_db(self, parent):
		"""initializes a new griffith database file"""
		response = gutils.question(self, \
			_('Are you sure you want to create a new database?\nYou will lose ALL your current data!'), \
			1, parent.main_window)
		if response == gtk.RESPONSE_YES:
			response_sec = gutils.question(self, \
				_('Last chance!\nDo you confirm that you want\nto lose your current data?'), \
				1, parent.main_window)
			if response_sec == gtk.RESPONSE_YES:
				# delete images
				posters_dir = os.path.join(self.griffith_dir, 'posters')
				# NOTE: only used images are removed (posters are shared between various db)
				debug.show('NEW DB: Removing old images...')
				for movie in self.Movie.select():
					if movie.image != None:
						name = movie.image.encode('utf-8')
						p_file = os.path.join(posters_dir, name+'.jpg')
						m_file = os.path.join(posters_dir, 'm_'+name+'.jpg')
						t_file = os.path.join(posters_dir, 't_'+name+'jpg')
						try:
							os.remove(p_file)
							os.remove(m_file)
							os.remove(t_file)
						except:
							pass
				parent.db.drop_database()
				if self.config['db_type'] == 'sqlite':
					os.unlink(os.path.join(self.griffith_dir,self.config.get('default_db')))
					if self.config['default_db'] == 'griffith.gri':
						self.config['default_db'] = 'griffith.db'
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

	def upgrade_database(self, version):
		"""Create new db or update existing one to current format"""
		if version == 0:
			debug.show('Creating tables...')
			self.Configuration.mapper.mapped_table.create()
			self.Configuration.mapper.mapped_table.insert().execute(param='version', value=self.version)
			self.Volume.mapper.mapped_table.create()
			self.Collection.mapper.mapped_table.create()
			self.Medium.mapper.mapped_table.create()
			self.Medium.mapper.mapped_table.insert().execute(name='DVD')
			self.Medium.mapper.mapped_table.insert().execute(name='DVD-R')
			self.Medium.mapper.mapped_table.insert().execute(name='DVD-RW')
			self.Medium.mapper.mapped_table.insert().execute(name='DVD+R')
			self.Medium.mapper.mapped_table.insert().execute(name='DVD+RW')
			self.Medium.mapper.mapped_table.insert().execute(name='DVD-RAM')
			self.Medium.mapper.mapped_table.insert().execute(name='CD')
			self.Medium.mapper.mapped_table.insert().execute(name='CD-RW')
			self.Medium.mapper.mapped_table.insert().execute(name='VCD')
			self.Medium.mapper.mapped_table.insert().execute(name='SVCD')
			self.Medium.mapper.mapped_table.insert().execute(name='VHS')
			self.Medium.mapper.mapped_table.insert().execute(name='BETACAM')
			self.Medium.mapper.mapped_table.insert().execute(name='LaserDisc')
			self.ACodec.mapper.mapped_table.create()
			self.ACodec.mapper.mapped_table.insert().execute(name='AC-3 Dolby audio')
			self.ACodec.mapper.mapped_table.insert().execute(name='OGG')
			self.ACodec.mapper.mapped_table.insert().execute(name='MP3')
			self.ACodec.mapper.mapped_table.insert().execute(name='MPEG-1')
			self.ACodec.mapper.mapped_table.insert().execute(name='MPEG-2')
			self.ACodec.mapper.mapped_table.insert().execute(name='AAC')
			self.ACodec.mapper.mapped_table.insert().execute(name='Windows Media Audio')
			self.VCodec.mapper.mapped_table.create()
			self.VCodec.mapper.mapped_table.insert().execute(name='MPEG-1')
			self.VCodec.mapper.mapped_table.insert().execute(name='MPEG-2')
			self.VCodec.mapper.mapped_table.insert().execute(name='XviD')
			self.VCodec.mapper.mapped_table.insert().execute(name='DivX')
			self.VCodec.mapper.mapped_table.insert().execute(name='H.264')
			self.VCodec.mapper.mapped_table.insert().execute(name='RealVideo')
			self.VCodec.mapper.mapped_table.insert().execute(name='QuickTime')
			self.VCodec.mapper.mapped_table.insert().execute(name='Windows Media Video')
			self.AChannel.mapper.mapped_table.create()
			self.AChannel.mapper.mapped_table.insert().execute(name='mono')
			self.AChannel.mapper.mapped_table.insert().execute(name='stereo')
			self.AChannel.mapper.mapped_table.insert().execute(name='5.1')
			self.AChannel.mapper.mapped_table.insert().execute(name='7.1')
			self.SubFormat.mapper.mapped_table.create()
			self.SubFormat.mapper.mapped_table.insert().execute(name='DVD VOB')
			self.SubFormat.mapper.mapped_table.insert().execute(name='MPL2 (.txt)')
			self.SubFormat.mapper.mapped_table.insert().execute(name='MicroDVD (.sub)')
			self.SubFormat.mapper.mapped_table.insert().execute(name='SubRip (.srt)')
			self.SubFormat.mapper.mapped_table.insert().execute(name='SubViewer2 (.sub)')
			self.SubFormat.mapper.mapped_table.insert().execute(name='Sub Station Alpha (.ssa)')
			self.SubFormat.mapper.mapped_table.insert().execute(name='Advanced Sub Station Alpha (.ssa)')
			self.Person.mapper.mapped_table.create()
			self.Movie.mapper.mapped_table.create()
			self.Loan.mapper.mapped_table.create()
			self.Lang.mapper.mapped_table.create()
			self.Lang.mapper.mapped_table.insert().execute(name=_('English'))
			self.MovieLang.mapper.mapped_table.create()
			self.Tag.mapper.mapped_table.create()
			self.Tag.mapper.mapped_table.insert().execute(name=_('Favourite'))
			self.Tag.mapper.mapped_table.insert().execute(name=_('To buy'))
			self.MovieTag.mapper.mapped_table.create()
			#self.metadata.commit()
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
			#self.Configuration.get_by(param='version').value = version
		#if version == 2:	# fix changes between v2 and v3
		#	version+=1
		#	self.Configuration.get_by(param='version').value = version

	def update_old_media(self):
		debug.show('Upgrading old media values...')
		self.metadata.execute("UPDATE movies SET media = '1' WHERE media = 'DVD';")
		self.metadata.execute("UPDATE movies SET media = '2' WHERE media = 'DVD-R';")
		self.metadata.execute("UPDATE movies SET media = '3' WHERE media = 'DVD-RW';")
		self.metadata.execute("UPDATE movies SET media = '4' WHERE media = 'DVD+R';")
		self.metadata.execute("UPDATE movies SET media = '5' WHERE media = 'DVD+RW';")
		self.metadata.execute("UPDATE movies SET media = '6' WHERE media = 'DVD-RAM';")
		self.metadata.execute("UPDATE movies SET media = '7' WHERE media = 'DivX';")
		self.metadata.execute("UPDATE movies SET media = '7' WHERE media = 'DIVX';")
		self.metadata.execute("UPDATE movies SET media = '7' WHERE media = 'XviD';")
		self.metadata.execute("UPDATE movies SET media = '7' WHERE media = 'XVID';")
		self.metadata.execute("UPDATE movies SET media = '7' WHERE media = 'WMV';")
		self.metadata.execute("UPDATE movies SET media = '7' WHERE media = 'WMV';")
		self.metadata.execute("UPDATE movies SET media = '9' WHERE media = 'VCD';")
		self.metadata.execute("UPDATE movies SET media = '10' WHERE media = 'SVCD'; 	")
		self.metadata.execute("UPDATE movies SET media = '11' WHERE media = 'VHS';")
		self.metadata.execute("UPDATE movies SET media = '12' WHERE media = 'BETACAM';")

	def fix_old_data(self):
		self.metadata.execute("UPDATE movies SET collection_id=NULL WHERE collection_id=''")
		self.metadata.execute("UPDATE movies SET volume_id=NULL WHERE volume_id=''")
		self.metadata.execute("UPDATE loans SET return_date=NULL WHERE return_date=''")
		self.metadata.execute("UPDATE movies SET year=NULL WHERE year<1900 or year>2020")
		self.metadata.execute("UPDATE movies SET rating=0 WHERE rating ISNULL")
		try:
			self.update_old_media()
		except:
			pass
	#}}}

	# LOANS ------------------------------------------------------------{{{
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
				query += ') VALUES ('
				for value in row:
					if value == None:
						query += 'NULL,'
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
		new_db.engine.execute('DELETE FROM volumes')
		new_db.engine.execute('DELETE FROM collections')
		new_db.engine.execute('DELETE FROM media')
		new_db.engine.execute('DELETE FROM languages')
		new_db.engine.execute('DELETE FROM tags')

		copy_table(sqlite2_cursor, new_db.engine, 'movies')
		copy_table(sqlite2_cursor, new_db.engine, 'people')
		copy_table(sqlite2_cursor, new_db.engine, 'media')
		copy_table(sqlite2_cursor, new_db.engine, 'loans')
		try:
			copy_table(sqlite2_cursor, new_db.engine, 'volumes')
			copy_table(sqlite2_cursor, new_db.engine, 'collections')
			copy_table(sqlite2_cursor, new_db.engine, 'languages')
			copy_table(sqlite2_cursor, new_db.engine, 'movie_lang')
			copy_table(sqlite2_cursor, new_db.engine, 'movie_tag')
			copy_table(sqlite2_cursor, new_db.engine, 'tags')
		except:
			pass

		move(os.path.join(tmp_dir,self.config['default_db']), destination_file)
		debug.show("SQLite2 conversion: file %s created" % destination_file)
		new_db.engine.Close();
		rmtree(tmp_dir)
		return True	#}}}

# for debugging (run: ipython sql.py)
if __name__ == '__main__':
	import config, gdebug, gglobals
	import sys
	db = GriffithSQL(config.Config(), gdebug.GriffithDebug(True), gglobals.griffith_dir)
	if len(sys.argv)>1:
		if sys.argv[1] == 'echo':
			db.metadata.engine.echo = True # print SQL queries
	print '\nGriffithSQL test drive\n======================'
	print "Engine: %s" % (db.metadata.engine.name)
	print 'Database object name: db\n'

# vim: fdm=marker
