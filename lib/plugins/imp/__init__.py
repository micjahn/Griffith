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
		self._abort	= False

	def initialize(self):
		"""Initializes plugin (get all parameters from user, etc.)"""
		self.imported = 0
		return True

	def abort(self, *args):
		"""called after abort button clicked"""
		self._abort = True

	def set_source(self, name):
		"""Prepare source (open file, etc.)"""

	def count_movies(self):
		"""Returns number of movies in file which is about to be imported"""
		pass

	def get_movie_details(self):
		"""Returns dictionary with movie details"""
		pass

	def run(self, name):
		"""Import movies, function called in a loop over source files"""
		from add import validate_details, edit_movie
		from gutils import find_next_available
		from sqlalchemy import Select, func
		import gtk
		
		if not self.set_source(name):
			self.debug.show("Can't read data from file %s" % name)
			return False
		
		self.widgets['pwindow'].show()
		for i in range(0,40):	# give GTK some time for updates
			gtk.main_iteration()

		# progressbar
		update_on = []
		count = self.count_movies()
		if count > 0:
			for i in range(0,100):
				update_on.append(int(float(i)/100*count))

		statement = Select( [ func.max(self.db.Movie.c.number) ] )
		number = statement.execute().fetchone()[0]
		if number is None:
			number = 1
		else:
			number += 1

		statement = Select(self.db.Movie.c)

		processed = 0
		while self._abort is False:
			details = self.get_movie_details()
			if details is None:
				break

			processed += 1
			if processed in update_on:
				self.widgets['progressbar'].set_fraction(float(processed)/float(count))
				gtk.main_iteration()
				self.widgets['progressbar'].set_text("%s (%s/%s)" % (str(self.imported), str(processed), str(count)))
				gtk.main_iteration()
				gtk.main_iteration() # extra iteration for abort button

			if (details.has_key('o_title') and details['o_title']) or (details.has_key('title') and details['title']):
				if details.has_key('o_title') and details['o_title']:
					statement.whereclause = self.db.Movie.c.o_title==details['o_title']
					tmp = statement.execute().fetchone()
					if tmp is not None:
						self.debug.show("movie already exists (o_title=%s)" % details['o_title'])
						continue
				if details.has_key('title') and details['title']:
					statement.whereclause = self.db.Movie.c.o_title==details['title']
					tmp = statement.execute().fetchone()
					if tmp is not None:
						self.debug.show("movie already exists (title=%s)" % details['title'])
						continue
				validate_details(details, self.fields_to_import)
				if self.edit is True:
					response = edit_movie(self.parent, details)	# FIXME: wait until save or cancel button pressed
					if response == 1:
						self.imported += 1
				else:
					if not details.has_key('number') or (details.has_key('number') and details['number'] is None):
						#details['number'] = find_next_available(self.db)
						details['number'] = number
						number += 1
					#movie = self.db.Movie()
					#movie.add_to_db(details)
					try:
						self.db.Movie.mapper.mapped_table.insert().execute(details)
						self.imported += 1
					except Exception, e:
						self.debug.show("movie details are not unique, skipping: %s" % str(e))
			else:
				self.debug.show('skipping movie without title or original title')
		self.widgets['pwindow'].hide()
		return True

	def clear(self):
		"""clear plugin before next source file"""
		self.data = None
		self.imported = 0
		self.__source_name = None
		self._abort = False
	
	def destroy(self):
		"""close all resources"""
		pass


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
	filenames = self.widgets['import']['fcw'].get_filenames()
	
	fields = []
	w = self.widgets['import']['fields']
	for i in w:
		if w[i].get_active():
			fields.append(i)

	__import__("plugins.imp.%s" % plugin_name)
	ip = eval("plugins.imp.%s.ImportPlugin(self, fields)" % plugin_name)
	if ip.initialize():
		self.widgets['window'].set_sensitive(False)
		self.widgets['import']['window'].hide()
		self.widgets['import']['pabort'].connect('clicked', ip.abort, ip)
		for filename in filenames:
			self.widgets['import']['progressbar'].set_fraction(0)
			self.widgets['import']['progressbar'].set_text('')
			if ip.run(filename):
				gutils.info(self, _("%s file has been imported. %s movies added.") \
					% (plugin_name, ip.imported), self.widgets['window'])
				self.populate_treeview()
			ip.clear()
		ip.destroy()
		self.widgets['import']['pwindow'].hide()
		self.widgets['window'].set_sensitive(True)

def on_abort_button_clicked(button, self, *args):
	self.widgets['import']['window'].hide()
	self.widgets['import']['pwindow'].hide()
	self.widgets['window'].set_sensitive(True)

