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

import xml.dom.minidom
import xml.dom.ext
import gtk
import gutils
import os
from gettext import gettext as _

plugin_name = "XML"
plugin_description = _("Full XML list export plugin")
plugin_author = "Vasco Nunes"
plugin_author_email = "<vasco.m.nunes@gmail.com>"
plugin_version = "0.1"

class ExportPlugin:

	def __init__(self, database, locations, parent_window, debug, **kwargs):
		self.db = database
		self.locations = locations
		self.parent = parent_window
		if kwargs.has_key('config'):
			self.persistent_config = kwargs['config']
		else:
			self.persistent_config = None
		self.export_xml()

	def export_xml(self):
		basedir = None
		if not self.persistent_config is None:
			basedir = self.persistent_config.get('export_dir', None, section='export-xml')
		if basedir is None:
			filename = gutils.file_chooser(_("Export a %s document")%"XML", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
				buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.xml')
		else:
			filename = gutils.file_chooser(_("Export a %s document")%"XML", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
				buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.xml',folder=basedir)
		if filename[0]:
			if not self.persistent_config is None and filename[1]:
				self.persistent_config.set('export_dir', filename[1], section='export-xml')
				self.persistent_config.save()
			overwrite = None
			if os.path.isfile(filename[0]):
				response = gutils.question(self, _("File exists. Do you want to overwrite it?"), 1, self.parent)
				if response==-8:
					overwrite = True
				else:
					overwrite = False
					
			if overwrite == True or overwrite is None:
				# create document
				impl = xml.dom.minidom.getDOMImplementation()
				doc  = impl.createDocument(None, "root", None)
				root = doc.documentElement
				
				# create object
				for movie in self.db.Movie.select():
					e = doc.createElement('movie')
					root.appendChild(e)
					for key in movie.c.keys():
						e2 = doc.createElement(key)
						if movie[key] is None:
							value = ''
						elif movie[key] in (True, False):
							value = str(int(movie[key]))
						else:
							value = str(movie[key])
						t = doc.createTextNode(value)
						e2.appendChild(t)
						e.appendChild(e2)
					
				# write XML to file
				fp = open(filename[0], "w")
				xml.dom.ext.PrettyPrint(doc, fp)
				fp.close()
				gutils.info(self, _("%s file has been created.")%"XML", self.parent)
