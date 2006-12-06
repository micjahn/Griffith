# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes, Piotr Ożarowski
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published byp
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

class ImportPlugin:
	name = None
	description = None
	author = None
	email = None
	version = None

	edit = False # should plugin open add window for every movie?
	renumber = True # should imported number filed be ignored?

	imported = 0
	data = None

	def __init__(self, parent):
		self.db = parent.db
		self.locations = parent.locations
		self.parent = parent
		global debug
		debug = self.debug = self.parent.debug

	def initialize(self):
		"""
		Initializes plugin (get all parameters from user, etc.)
		"""
		self.imported = 0
		return True

	def set_source(self, name):
		"""
		Prepare source (open file, etc.)

		this function will prepare self.data for processing
		"""

	def count_movies(self):
		"""
		Returns number of movies in file which is about to be imported
		"""
		pass

	def get_movie_details(self, item):
		"""
		Returns dictionary with movie details (process data item)
		"""
		pass

	def run(self):
		"""
		Import movies
		"""
		
		if self.edit is True:
			from add import edit_movie
		else:
			from gutils import find_next_available
		
		for item in self.data:
			details = self.get_movie_details(item)
			if details is None:
				continue
			if details['o_title'] or details['title']:
				if details['o_title']:
					tmp_movie = self.db.Movie.get_by(o_title=details['o_title'])
					if tmp_movie is not None:
						debug.show("movie already exists (o_title=%s)" % details['o_title'])
						continue
				if details['title']:
					tmp_movie = self.db.Movie.get_by(title=details['title'])
					if tmp_movie is not None:
						debug.show("movie already exists (title=%s)" % details['title'])
						continue
				if details.has_key('number') and self.renumber is True:
					details['number'] = None
				if self.edit is True:
					edit_movie(self.parent, details)	# FIXME: wait until save or cancel button pressed
				else:
					if details['number'] is None:
						details['number'] = find_next_available(self.parent)
					movie = self.db.Movie()
					movie.add_to_db(details)
				self.imported += 1 # FIXME: what about cancel button in edit window
			else:
				debug('skipping movie without title or original title')

	def clear(self):
		self.data = None
		self.imported = 0
		self.__source_name = None
