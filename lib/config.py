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

import os
import os.path
import pickle
import gglobals

class Config:
	def __init__ (self, file=os.path.join(gglobals.griffith_dir, 'griffith.conf')):
		"""A basic class for handling preferences with pickle"""
		self.file = file
		self.config = {}
		if not self.load():
			self.make_defaults()
		self.set_hooks = []

	def get (self, key, default=None):
		"""Return a key's value, or default if the key isn't set."""
		if not self.config.has_key(key):
			return default
		else:
			return self.config[key]

	def has_key (self, k):
		return self.config.has_key(k)

	def __setitem__ (self, k, v):
		self.config[k] = v
		for hook in self.set_hooks: hook(k, v)

	def __getitem__ (self, k):
		return self.config[k]

	def keys (self):
		return self.config.keys()
	def values (self):
		return self.config.values()
	def items (self):
		return self.config.items()

	def save (self):
		if not os.path.exists(os.path.split(self.file)[0]):
			os.makedirs(os.path.split(self.file)[0])
		ofi=open(self.file, 'w')
		pickle.dump(self.config, ofi)
		ofi.close()

	def load (self):
		if os.path.isfile(self.file):
			ifi=open(self.file, 'r')
			self.config=pickle.load(ifi)
			ifi.close()
			return True
		else:
			return False
			
	def make_defaults(self):
		self.config['pdf_reader']           = "xpdf"
		self.config['default_db']           = "griffith.db"
		self.config['height']               = "None"
		self.config['width']                = "None"
		self.config['top']                  = "None"
		self.config['left']                 = "None"
		self.config['view_director']        = "True"
		self.config['view_otitle']          = "True"
		self.config['view_title']           = "True"
		self.config['view_image']           = "True"
		self.config['view_toolbar']         = "True"
		self.config['use_gtkspell']         = "True"
		self.config['spell_plot']           = "True"
		self.config['spell_notes']          = "True"
		self.config['spell_lang']           = "en"
		self.config['default_movie_plugin'] = "IMDB"
		self.config['rating']               = "0" # 0 = meter; 1 = stars
		self.config['mail_smtp_server']     = "localhost"
		self.config['mail_use_auth']        = "False"
		self.config['mail_username']        = ""
		self.config['mail_password']        = ""
		self.config['mail_email']           = "griffith"
		self.config['media']                = "0"
		self.config['font']                 = ""
		self.config['db_type']              = "sqlite"
		self.config['db_host']              = "localhost"
		self.config['db_port']              = "5433"
		self.config['db_name']              = "griffith"
		self.config['db_user']              = "griffith"
		self.config['db_passwd']            = "gRiFiTh"
		self.save()
