# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2006 Piotr Ożarowski
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

# detect all plugins:
import glob, os.path
from gettext import gettext as _

__all__ = [os.path.basename(x)[:-3] for x in glob.glob("%s/*.py" % os.path.dirname(__file__))]
__all__.remove('__init__')

class ImportPlugin:
	description = None
	author = None
	email = None
	version = None
	# file chooser:
	file_filters = None
	mime_types = None

	edit = False		# open add window for every movie?

	imported = 0
	data = None

	def __init__(self, parent, fields_to_import):
		self.db		= parent.db
		self.debug	= parent.debug
		self.locations	= parent.locations
		self.fields	= parent.field_names
		self.conditions	= parent._conditions
		self.colors	= parent._colors
		self.lang_types	= parent._lang_types
		self.layers	= parent._layers
		self.regions	= parent._regions
		self.widgets	= parent.widgets['import']
		self.fields_to_import = fields_to_import

	def initialize(self, filename):
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

	def run(self, name):
		"""
		Import movies
		"""
		
		if self.edit is True:
			from add import edit_movie
		else:
			from gutils import find_next_available
		
		if not self.set_source(name):
			self.debug.show("Can't read data from file %s" % name)
			return False
		
		for item in self.data:
			details = self.get_movie_details(item)
			if details is None:
				continue
			if (details.has_key('o_title') and details['o_title']) or (details.has_key('title') and details['title']):
				if details.has_key('o_title') and details['o_title']:
					tmp_movie = self.db.Movie.get_by(o_title=details['o_title'])
					if tmp_movie is not None:
						self.debug.show("movie already exists (o_title=%s)" % details['o_title'])
						continue
				if details.has_key('title') and details['title']:
					tmp_movie = self.db.Movie.get_by(title=details['title'])
					if tmp_movie is not None:
						self.debug.show("movie already exists (title=%s)" % details['title'])
						continue
				if details.has_key('number') and 'number' in self.fields_to_import:
					details['number'] = None
				if self.edit is True:
					edit_movie(self.parent, details)	# FIXME: wait until save or cancel button pressed
				else:
					if not details.has_key('number') or (details.has_key('number') and details['number'] is None):
						details['number'] = find_next_available(self.db)
					movie = self.db.Movie()
					movie.add_to_db(details)
					#self.db.Movie.mapper.mapped_table.insert().execute(details) # faster, but details are not checked
				self.imported += 1 # FIXME: what about cancel button in edit window
			else:
				self.debug.show('skipping movie without title or original title')
		return True

	def clear(self):
		self.data = None
		self.imported = 0
		self.__source_name = None


def on_import_plugin_changed(combobox, widgets, *args):
	from gtk import FileFilter
	import plugins.imp
	plugin_name = widgets['plugin'].get_active_text()
	__import__("plugins.imp.%s" % plugin_name)
	ip = eval("plugins.imp.%s.ImportPlugin" % plugin_name)
	widgets['author'].set_markup("<i>%s</i>" % ip.author)
	widgets['email'].set_markup("<i>%s</i>" % ip.email)
	widgets['version'].set_markup("<i>%s</i>" %ip.version)
	widgets['description'].set_markup("<i>%s</i>" %ip.description)
	# file filters
	for i in widgets['fcw'].list_filters():
		widgets['fcw'].remove_filter(i)
	f = FileFilter()
	f.set_name(plugin_name)
	if ip.file_filters is not None:
		if isinstance(ip.file_filters, tuple) or isinstance(ip.file_filters, list):
			for i in ip.file_filters:
				f.add_pattern(i)
		else:
			f.add_pattern(ip.file_filters)
	if ip.mime_types is not None:
		if isinstance(ip.mime_types, tuple) or isinstance(ip.mime_types, list):
			for i in ip.mime_types:
				f.add_mime_type(i)
		else:
			f.add_mime_type(ip.mime_types)
	widgets['fcw'].add_filter(f)
	f = FileFilter()
	f.set_name(_("All files"))
	f.add_pattern("*")
	widgets['fcw'].add_filter(f)

def on_import_button_clicked(button, self, *args):
	import plugins.imp, gutils
	plugin_name = self.widgets['import']['plugin'].get_active_text()
	filename = self.widgets['import']['fcw'].get_filename() # TODO: multiple files
	
	fields = []
	w = self.widgets['import']['fields']
	for i in w:
		if w[i].get_active():
			fields.append(i)

	__import__("plugins.imp.%s" % plugin_name)
	ip = eval("plugins.imp.%s.ImportPlugin(self, fields)" % plugin_name)
	if ip.initialize():
		# TODO: show progres bar
		# for file in selected_files:
		if ip.run(filename):
			gutils.info(self, _("%s file has been imported. %s movies added.") \
				% (plugin_name, ip.imported), self.widgets['window'])
			self.populate_treeview()
			self.widgets['import']['window'].hide()
		ip.clear()

