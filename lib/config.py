# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes, Piotr Ożarowski
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

import os
import os.path
import ConfigParser
#import cPickle as pickle

class Config:
	subst = {'True': True, 'False': False, 'None': None}
	def __init__ (self, file):
		self._file = file
		if not self.load():
			self.make_defaults()

		#self.set_hooks = []

	def get(self, option, default=None, section='main'):
		if not isinstance(option, str):
			option = str(option)
		if not self._cfg.has_option(section, option):
			return default
		else:
			value = self._cfg.get(section, option, False)
			if value in self.subst.keys():
				value = self.subst[value]
			return value

	def set(self, option, value, section='main'):
		if not isinstance(option, str):
			option = str(option)
		if not isinstance(value, str):
			value = str(value)
		if not self._cfg.has_section(section):
			self._cfg.add_section(section)
		self._cfg.set(section, option, value)

	def has_key(self, key, section='main'):
		return self._cfg.has_option(section,key)

	def __setitem__(self, k, v):
		self.set(k,v, section='main')

	def __getitem__(self, key):
		return self.get('main', key)

	def keys(self, section='main'):
		return [ i[0] for i in self._cfg.items(section) ]
	def values(self, section='main'):
		return [ i[1] for i in self._cfg.items(section) ]
	def items(self, section='main'):
		return self._cfg.items(section)
	def toDict(self, section='main'):
		d = {}
		for i,j in self._cfg.items(section):
			d[i] = j
		return d

	def save(self):
		if not os.path.exists(os.path.split(self._file)[0]):
			os.makedirs(os.path.split(self._file)[0])
		self._cfg.write(open(self._file, 'w'))

	def load(self):
		if os.path.isfile(self._file):
			self._cfg = ConfigParser.SafeConfigParser()
			try:
				self._cfg.read(self._file)
			except:
				print 'Cannot parse config file'
				return False
			return True
		else:
			return False
			
	def make_defaults(self):
		self._cfg = ConfigParser.SafeConfigParser()
		self._cfg.read(self._file)
		self._cfg.add_section('database')
		self._cfg.add_section('defaults')
		self._cfg.add_section('window')
		self._cfg.add_section('mainlist')
		self._cfg.add_section('mail')
		self._cfg.add_section('spell')
		self._cfg.add_section('add')
		self._cfg.add_section('main')
		self._cfg.set('add', 's_cast', 'True')
		self._cfg.set('add', 's_classification', 'True')
		self._cfg.set('add', 's_country', 'True')
		self._cfg.set('add', 's_director', 'True')
		self._cfg.set('add', 's_genre', 'True')
		self._cfg.set('add', 's_image', 'True')
		self._cfg.set('add', 's_notes', 'True')
		self._cfg.set('add', 's_o_site', 'True')
		self._cfg.set('add', 's_o_title', 'True')
		self._cfg.set('add', 's_plot', 'True')
		self._cfg.set('add', 's_rating', 'True')
		self._cfg.set('add', 's_runtime', 'True')
		self._cfg.set('add', 's_site', 'True')
		self._cfg.set('add', 's_studio', 'True')
		self._cfg.set('add', 's_title', 'True')
		self._cfg.set('add', 's_trailer', 'True')
		self._cfg.set('add', 's_year', 'True')
		self._cfg.set('database', 'file', 'griffith.db')
		self._cfg.set('database', 'host', 'localhost')
		self._cfg.set('database', 'name', 'griffith')
		self._cfg.set('database', 'passwd', 'gRiFiTh')
		self._cfg.set('database', 'port', '5432')
		self._cfg.set('database', 'type', 'sqlite')
		self._cfg.set('database', 'user', 'griffith')
		self._cfg.set('defaults', 'color', '0')
		self._cfg.set('defaults', 'condition', '0')
		self._cfg.set('defaults', 'layers', '0')
		self._cfg.set('defaults', 'media', '0')
		self._cfg.set('defaults', 'region', '0')
		self._cfg.set('defaults', 'vcodec', '0')
		self._cfg.set('mail', 'email', 'griffith')
		self._cfg.set('mail', 'password', '')
		self._cfg.set('mail', 'smtp_server', 'localhost')
		self._cfg.set('mail', 'use_auth', 'False')
		self._cfg.set('mail', 'username', '')
		self._cfg.set('main', 'default_movie_plugin', 'IMDB')
		self._cfg.set('main', 'font', '')
		self._cfg.set('main', 'pdf_reader', 'xpdf')
		self._cfg.set('main', 'posters', 'posters')
		self._cfg.set('main', 'rating_image', '0')	# 0 = meter; 1 = stars
		self._cfg.set('mainlist', 'director', 'True')
		self._cfg.set('mainlist', 'image', 'True')
		self._cfg.set('mainlist', 'limit', '0')		# limit search results to x items (0 -> no limits)
		self._cfg.set('mainlist', 'number', 'True')
		self._cfg.set('mainlist', 'otitle', 'True')
		self._cfg.set('mainlist', 'sortby', 'number')
		self._cfg.set('mainlist', 'sortby_reverse', 'False')
		self._cfg.set('mainlist', 'title', 'True')
		self._cfg.set('spell', 'gtkspell', 'True')
		self._cfg.set('spell', 'lang', 'en')
		self._cfg.set('spell', 'notes', 'True')
		self._cfg.set('spell', 'plot', 'True')
		self._cfg.set('window', 'height', '700')
		self._cfg.set('window', 'left', 'None')
		self._cfg.set('window', 'top', 'None')
		self._cfg.set('window', 'view_toolbar', 'True')
		self._cfg.set('window', 'width', '500')
		self.save()
