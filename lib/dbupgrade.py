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


def upgrade_database(self, version):
	"""Create new db or update existing one to current format"""
	if version == 0:
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
		self.Lang.mapper.mapped_table.insert().execute(name=_('Brazilian Portuguese'))
		self.Lang.mapper.mapped_table.insert().execute(name=_('Czech'))
		self.Lang.mapper.mapped_table.insert().execute(name=_('French'))
		self.Lang.mapper.mapped_table.insert().execute(name=_('German'))
		self.Lang.mapper.mapped_table.insert().execute(name=_('Italian'))
		self.Lang.mapper.mapped_table.insert().execute(name=_('Portuguese'))
		self.Lang.mapper.mapped_table.insert().execute(name=_('Polish'))
		self.Lang.mapper.mapped_table.insert().execute(name=_('Spanish'))
		self.MovieLang.mapper.mapped_table.create()
		self.Tag.mapper.mapped_table.create()
		self.Tag.mapper.mapped_table.insert().execute(name=_('Favourite'))
		self.MovieTag.mapper.mapped_table.create()
		#self.metadata.commit()
		return True # upgrade process finished
	if version == 1: # fix changes between v1 and v2
		pass # v2 is not yet released
		#version+=1
		#self.Configuration.get_by(param='version').value = version
	#if version == 2:	# fix changes between v2 and v3
	#	version+=1
	#	self.Configuration.get_by(param='version').value = version


# ---------------------------------------------------
# for Griffith <= 0.6.2 compatibility
# ---------------------------------------------------

def convert_from_old_db(self, source_file, destination_file):	#{{{
	print 'Converting old database - it can take several minutes...'
	gutils.info(self,_("Griffith will now convert your database to the new format. This can take several minutes if you have a large database."))
	from sqlalchemy.orm import clear_mappers
	from sql import GriffithSQL
	from gutils import digits_only
	import os

	if not os.path.isfile(source_file):
		return False
	if open(source_file).readline()[:47] == '** This file contains an SQLite 2.1 database **':
		try:
			import sqlite
			from sqlite import DatabaseError
		except:
			print 'Old DB conversion: please install pysqlite legacy (v1.0)'
			gutils.warning(self,_("Old DB conversion: please install pysqlite legacy (v1.0)"))
			return False
	else:
		from pysqlite2 import dbapi2 as sqlite
		from pysqlite2.dbapi2 import DatabaseError

	if os.path.isfile(destination_file):
		# rename destination_file if it already exist
		i = 1
		while True:
			if os.path.isfile("%s_%s" % (destination_file, i)):
				i += 1
			else:
				break
		os.rename(destination_file, "%s_%s" % (destination_file, i))

	try:
		old_db = sqlite.connect(source_file)
	except DatabaseError, e:
		if str(e) == 'file is encrypted or is not a database':
			print 'Your database is most probably in wrong SQLite format, please convert it to SQLite3:'
			print '$ sqlite ~/.griffith/griffith.gri .dump | sqlite3 ~/.griffith/griffith.gri3'
			print '$ mv ~/.griffith/griffith.gri{,2}'
			print '$ mv ~/.griffith/griffith.gri{3,}'
			print 'or install pysqlite in version 1.0'
			gutils.warning(self,_("Your database is most probably in SQLite2 format, please convert it to SQLite3"))
		else:
			raise
		return False

	old_cursor = old_db.cursor()

	# fix old database
	old_cursor.execute("UPDATE movies SET media = '1' WHERE media = 'DVD';")
	old_cursor.execute("UPDATE movies SET media = '2' WHERE media = 'DVD-R';")
	old_cursor.execute("UPDATE movies SET media = '3' WHERE media = 'DVD-RW';")
	old_cursor.execute("UPDATE movies SET media = '4' WHERE media = 'DVD+R';")
	old_cursor.execute("UPDATE movies SET media = '5' WHERE media = 'DVD+RW';")
	old_cursor.execute("UPDATE movies SET media = '6' WHERE media = 'DVD-RAM';")
	old_cursor.execute("UPDATE movies SET media = '7' WHERE media = 'DivX';")
	old_cursor.execute("UPDATE movies SET media = '7' WHERE media = 'DIVX';")
	old_cursor.execute("UPDATE movies SET media = '7' WHERE media = 'XviD';")
	old_cursor.execute("UPDATE movies SET media = '7' WHERE media = 'XVID';")
	old_cursor.execute("UPDATE movies SET media = '7' WHERE media = 'WMV';")
	old_cursor.execute("UPDATE movies SET media = '9' WHERE media = 'VCD';")
	old_cursor.execute("UPDATE movies SET media = '10' WHERE media = 'SVCD'; 	")
	old_cursor.execute("UPDATE movies SET media = '11' WHERE media = 'VHS';")
	old_cursor.execute("UPDATE movies SET media = '12' WHERE media = 'BETACAM';")
	old_cursor.execute("UPDATE movies SET collection_id=0 WHERE collection_id<1")
	old_cursor.execute("UPDATE movies SET volume_id=0 WHERE volume_id<1")
	old_cursor.execute("UPDATE movies SET color=NULL WHERE color<1 OR color='' OR color>3")
	old_cursor.execute("UPDATE movies SET condition=NULL WHERE condition<0 OR condition='' OR condition>5")
	old_cursor.execute("UPDATE movies SET layers=NULL WHERE layers<0 OR layers='' OR layers>4")
	old_cursor.execute("UPDATE movies SET region=NULL WHERE region='' OR region=2 OR region<0 OR region>8")
	old_cursor.execute("UPDATE movies SET year=NULL WHERE year<1900 or year>2007")
	old_cursor.execute("UPDATE movies SET rating = 0 WHERE rating NOT IN (0,1,2,3,4,5,6,7,8,9,10);") # rating>10 doesn't work with some DB
	old_cursor.execute("UPDATE movies SET runtime = NULL WHERE runtime > 10000;") # remove strings
	old_cursor.execute("UPDATE loans SET return_date=NULL WHERE return_date=''")
	old_cursor.execute("DELETE FROM loans WHERE date='' OR date ISNULL")
	old_cursor.execute("DELETE FROM volumes WHERE name = ''")
	old_cursor.execute("DELETE FROM volumes WHERE name = 'None'")
	old_cursor.execute("DELETE FROM collections WHERE name = ''")
	old_cursor.execute("DELETE FROM collections WHERE name = 'None'")
	old_cursor.execute("DELETE FROM languages WHERE name = ''")
	
	self.config['db_type'] = 'sqlite'
	self.config['default_db'] = 'griffith.db'
	self.config['posters'] = 'posters'
	self.config['color'] = 0
	self.config['condition'] = 0
	self.config['layers'] = 0
	self.config['media'] = 0
	self.config['region'] = 0
	self.config['vcodec'] = 0
	self.locations['posters'] = os.path.join(self.locations['home'], 'posters')
	new_db = GriffithSQL(self.config, self.debug, self.locations['home'])

	# collections
	collection_mapper = {0:None, u'':None}
	old_cursor.execute("SELECT id, name FROM collections;") # loaned status will be set later - buggy databases :-(
	for i in old_cursor.fetchall():
		o = new_db.Collection(name=i[1])
		try:
			o.save(); o.flush()
		except Exception, e:
			self.debug.show(str(e))
			continue
		collection_mapper[i[0]] = o.collection_id
	
	# volumes
	volume_mapper = {0:None, u'':None}
	old_cursor.execute("SELECT id, name FROM volumes;") # loaned status will be set later - buggy databases :-(
	for i in old_cursor.fetchall():
		o = new_db.Volume(name=i[1])
		try:
			o.save(); o.flush()
		except Exception, e:
			self.debug.show(str(e))
			continue
		volume_mapper[i[0]] = o.volume_id

	# people
	person_mapper = {}
	old_cursor.execute("SELECT id, name, email, phone FROM people;")
	for i in old_cursor.fetchall():
		o = new_db.Person(name=i[1], email=i[2], phone=i[3])
		try:
			o.save(); o.flush()
		except Exception, e:
			self.debug.show(str(e))
			continue
		person_mapper[i[0]] = o.person_id
	
	# languages
	language_mapper = {}
	old_cursor.execute("SELECT id, name FROM languages;")
	for i in old_cursor.fetchall():
		o = new_db.Lang.get_by(name=i[1])
		if o is not None:
			language_mapper[i[0]] = o.lang_id
		else:
			o = new_db.Lang(name=i[1])
			try:
				o.save(); o.flush()
			except Exception, e:
				self.debug.show(str(e))
				continue
			language_mapper[i[0]] = o.lang_id

	# media
	medium_mapper = {'0':None}
	old_cursor.execute("SELECT id, name FROM media;")
	for i in old_cursor.fetchall():
		o = new_db.Medium.get_by(name=i[1])
		if o is not None:
			medium_mapper[i[0]] = o.medium_id
		else:
			o = new_db.Medium(name=i[1])
			try:
				o.save(); o.flush()
			except Exception, e:
				self.debug.show(str(e))
				continue
			medium_mapper[i[0]] = o.medium_id
	
	# tags
	tag_mapper = {}
	old_cursor.execute("SELECT id, name FROM tags;")
	for i in old_cursor.fetchall():
		o = new_db.Tag.get_by(name=i[1])
		if o is not None:
			tag_mapper[i[0]] = o.tag_id
		else:
			o = new_db.Tag(name=i[1])
			try:
				o.save(); o.flush()
			except Exception, e:
				self.debug.show(str(e))
				continue
			tag_mapper[i[0]] = o.tag_id
	
	# movies
	movie_mapper = {}
	old_cursor.execute("""
		SELECT id, volume_id, collection_id, original_title, title, director,
			number, image, plot, country, year, runtime, classification,
			genre, studio, site, imdb, actors, trailer, rating, loaned,
			media, num_media, obs, seen, region, condition, color, layers
		FROM movies ORDER BY number;""")
	for i in old_cursor.fetchall():
		o = new_db.Movie()
		o.number = digits_only(i[6])
		o.volume_id = volume_mapper[i[1]]
		o.collection_id = collection_mapper[i[2]]
		o.o_title = i[3][:255]
		o.title = i[4][:255]
		o.director = i[5][:255]
		o.image = i[7][:128]
		o.plot = i[8]
		o.country = i[9][:128]
		o.year = digits_only(i[10])
		o.runtime = digits_only(i[11])
		o.classification = i[12][:128]
		o.genre = i[13][:128]
		o.studio = i[14][:128]
		o.o_site = i[15][:255]
		o.site = i[16][:255]
		o.cast = i[17]
		o.trailer = i[18][:255]
		o.rating = digits_only(i[19])
		#o.loaned = bool(i[20]) # updated later
		o.medium_id = medium_mapper[int(i[21])]
		o.media_num = digits_only(i[22])
		o.notes = i[23]
		o.seen = bool(i[24])
		o.region = digits_only(i[25])
		o.cond = digits_only(i[26], 5)
		o.color = digits_only(i[27], 3)
		o.layers = digits_only(i[28], 4)
		
		try:
			o.save(); o.flush()
		except Exception, e:
			self.debug.show(str(e))
			continue
		movie_mapper[i[0]] = o.movie_id

	# movie tag
	old_cursor.execute("SELECT movie_id, tag_id FROM movie_tag WHERE movie_id IN (SELECT id FROM movies);")
	for i in old_cursor.fetchall():
		o = new_db.MovieTag.get_by(movie_id=movie_mapper[i[0]], tag_id=tag_mapper[i[1]])
		if o is None:
			m = new_db.Movie.get_by(movie_id=movie_mapper[i[0]])
			t = new_db.Tag.get_by(tag_id=tag_mapper[i[1]])
			t.save()
			m.tags.append(t)
			try:
				m.save(); m.flush()
			except Exception, e:
				self.debug.show(str(e))
				continue
	
	# movie lang
	old_cursor.execute("SELECT movie_id, lang_id, type FROM movie_lang WHERE movie_id IN (SELECT id FROM movies);")
	for i in old_cursor.fetchall():
		o = new_db.MovieLang.get_by(movie_id=movie_mapper[i[0]], lang_id=language_mapper[i[1]], type=i[2])
		if o is None:
			m = new_db.Movie.get_by(movie_id=movie_mapper[i[0]])
			l = new_db.MovieLang(lang_id=language_mapper[i[1]], type=i[2])
			l.save()
			m.languages.append(l)
			try:
				m.save(); m.flush()
			except Exception, e:
				self.debug.show(str(e))
				continue

	# loans
	old_cursor.execute("SELECT person_id, movie_id, volume_id, collection_id, date, return_date FROM loans;")
	for i in old_cursor.fetchall():
		vol = col = None
		not_returned = i[5] is not None

		if int(i[2]) > 0:
			try:
				vol = new_db.Volume.get_by(volume_id=volume_mapper[i[2]])
			except Exception, e:
				self.debug.show(str(e))
				continue
		if int(i[3]) > 0:
			try:
				col = new_db.Collection.get_by(collection_id=collection_mapper[i[3]])
			except Exception, e:
				self.debug.show(str(e))
				continue
		if int(i[1]) == 0:
			if vol is not None and len(vol.movies)>0:
				m = vol.movies[0]
			elif col is not None and len(col.movies)>0:
				m = col.movies[0]
			else:
				self.debug.show("Cannot find associated movie for this loan (%s)" % i)
				continue
		else:
			try:
				m = new_db.Movie.get_by(movie_id=movie_mapper[i[1]])
			except Exception, e:
				self.debug.show(str(e))
				continue
		
		l = new_db.Loan()
		l.person_id = person_mapper[i[0]]
		l.date = str(i[4])[:10]
		if not_returned:
			m.loaned = True
		else:
			l.return_date = str(i[5])[:10]
		
		# update volume / collection status
		if int(i[2]) > 0:
			l.volume_id = volume_mapper[i[2]]
			if not_returned:
				vol.loaned = True
				vol.save()
		if int(i[3]) > 0:
			l.collection_id = collection_mapper[i[3]]
			if not_returned:
				col.loaned = True
				col.save()
		l.save();
		m.loans.append(l)
		try:
			m.flush()
		except Exception, e:
			self.debug.show(str(e))
			continue
	clear_mappers()
	return True
#}}}
# vim: fdm=marker
