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
	def __init__ (self, file):
		"""A basic class for handling preferences with pickle"""
		self.file = file
		if not self.load():
			self.make_defaults()
		#self.set_hooks = []

	def get (self, key, default=None, section='main'):
		"""Return a key's value, or default if the key isn't set."""
		if not self.cfg.has_option(section,key):
			return default
		else:
			tmp = self.cfg.get(section, key)
			if tmp == 'True':
				tmp = True
			elif tmp == 'False':
				tmp = False
			elif tmp == 'None':
				tmp = None
			return tmp

	def has_key (self, key, section='main'):
		return self.cfg.has_option(section,key)

	def __setitem__ (self, k, v):
		if not isinstance(v, str):
			v = str(v)
		self.cfg.set('main', k, v)
		#for hook in self.set_hooks: hook(k, v)

	def __getitem__ (self, key):
		return self.get(key)

	def keys (self):
		return [ i[0] for i in self.cfg.items('main') ]
	def values (self):
		return [ i[1] for i in self.cfg.items('main') ]
	def items (self):
		return self.cfg.items('main')

	def save (self):
		if not os.path.exists(os.path.split(self.file)[0]):
			os.makedirs(os.path.split(self.file)[0])
		self.cfg.write(open(self.file, 'w'))

	def load (self):
		if os.path.isfile(self.file):
			self.cfg = ConfigParser.SafeConfigParser()
			try:
				self.cfg.read(self.file)
			except:
				print 'Cannot parse config file'
				return False
			for i in self.cfg.items('main'):
				self[i[0]] = i[1]
			return True
		else:
			return False
			
	def make_defaults(self):
		self.cfg = ConfigParser.SafeConfigParser()
		self.cfg.read(self.file)
		self.cfg.add_section('main')
		self.cfg.set('main', 'pdf_reader', 'xpdf')
		self.cfg.set('main', 'default_db', 'griffith.db')
		self.cfg.set('main', 'height', 'None')
		self.cfg.set('main', 'width', 'None')
		self.cfg.set('main', 'top', 'None')
		self.cfg.set('main', 'left', 'None')
		self.cfg.set('main', 'view_director', 'True')
		self.cfg.set('main', 'view_number', 'True')
		self.cfg.set('main', 'view_otitle', 'True')
		self.cfg.set('main', 'view_title', 'True')
		self.cfg.set('main', 'view_image', 'True')
		self.cfg.set('main', 'view_toolbar', 'True')
		self.cfg.set('main', 'use_gtkspell', 'True')
		self.cfg.set('main', 'spell_plot', 'True')
		self.cfg.set('main', 'spell_notes', 'True')
		self.cfg.set('main', 'spell_lang', 'en')
		self.cfg.set('main', 'default_movie_plugin', 'IMDB')
		self.cfg.set('main', 'rating', '0') # 0       = meter; 1 = stars
		self.cfg.set('main', 'color', '0')
		self.cfg.set('main', 'condition', '0')
		self.cfg.set('main', 'layers', '0')
		self.cfg.set('main', 'media', '0')
		self.cfg.set('main', 'region', '0')
		self.cfg.set('main', 'vcodec', '0')
		self.cfg.set('main', 'mail_smtp_server', 'localhost')
		self.cfg.set('main', 'mail_use_auth', 'False')
		self.cfg.set('main', 'mail_username', '')
		self.cfg.set('main', 'mail_password', '')
		self.cfg.set('main', 'mail_email', 'griffith')
		self.cfg.set('main', 'posters', 'posters')
		self.cfg.set('main', 'font', '')
		self.cfg.set('main', 'db_type', 'sqlite')
		self.cfg.set('main', 'db_host', 'localhost')
		self.cfg.set('main', 'db_port', '5432')
		self.cfg.set('main', 'db_name', 'griffith')
		self.cfg.set('main', 'db_user', 'griffith')
		self.cfg.set('main', 'db_passwd', 'gRiFiTh')
		self.cfg.set('main', 's_classification', 'True')
		self.cfg.set('main', 's_country', 'True')
		self.cfg.set('main', 's_director', 'True')
		self.cfg.set('main', 's_genre', 'True')
		self.cfg.set('main', 's_image', 'True')
		self.cfg.set('main', 's_notes', 'True')
		self.cfg.set('main', 's_o_site', 'True')
		self.cfg.set('main', 's_o_title', 'True')
		self.cfg.set('main', 's_plot', 'True')
		self.cfg.set('main', 's_rating', 'True')
		self.cfg.set('main', 's_runtime', 'True')
		self.cfg.set('main', 's_site', 'True')
		self.cfg.set('main', 's_studio', 'True')
		self.cfg.set('main', 's_title', 'True')
		self.cfg.set('main', 's_trailer', 'True')
		self.cfg.set('main', 's_cast', 'True')
		self.cfg.set('main', 's_year', 'True')
		self.cfg.set('main', 's_limit', '0') # limit search results to x items (0 -> no limits)
		self.save()
