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
import os
import db
import gutils
from plugins.export import Base

class ExportPlugin(Base):
    name = "XML"
    description = _("Full XML list export plugin")
    author = "Vasco Nunes"
    email = "<vasco.m.nunes@gmail.com>"
    version = "0.1"

    fields_to_export = ('number', 'o_title', 'title', 'director', 'year', 'classification', 'country',
                        'genre', 'rating', 'runtime', 'studio', 'seen', 'loaned', 'o_site', 'site', 'trailer',
                        'plot', 'cast', 'notes', 'image', 'volumes.name', 'collections.name', 'media.name')

    def run(self):
        basedir = None
        if self.config is not None:
            basedir = self.config.get('export_dir', None, section='export-xml')
        if basedir is None:
            filename = gutils.file_chooser(_("Export a %s document")%"XML", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.xml')
        else:
            filename = gutils.file_chooser(_("Export a %s document")%"XML", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.xml',folder=basedir)
        if filename and filename[0]:
            if self.config is not None and filename[1]:
                self.config.set('export_dir', filename[1], section='export-xml')
                self.config.save()
            overwrite = None
            if os.path.isfile(filename[0]):
                response = gutils.question(_("File exists. Do you want to overwrite it?"), True, self.parent_window)
                if response==-8:
                    overwrite = True
                else:
                    overwrite = False
                    
            if overwrite or overwrite is None:
                # create document
                impl = xml.dom.minidom.getDOMImplementation()
                doc  = impl.createDocument(None, "root", None)
                root = doc.documentElement
                
                movies = self.get_query().execute().fetchall()
                # create object
                for movie in movies:
                    e = doc.createElement('movie')
                    root.appendChild(e)
                    for key in self.exported_columns:
                        e2 = doc.createElement(str(key).replace('movies_', ''))
                        if movie[key] is None:
                            value = ''
                        elif movie[key] in (True, False):
                            value = str(int(movie[key]))
                        else:
                            if movie[key] is unicode:
                                value = movie[key].encode('utf-8')
                            else:
                                value = str(movie[key])
                        t = doc.createTextNode(value)
                        e2.appendChild(t)
                        e.appendChild(e2)
                    
                # write XML to file
                fp = open(filename[0], "w")
                xml.dom.ext.PrettyPrint(doc, fp)
                fp.close()
                gutils.info( _("%s file has been created.")%"XML", self.parent_window)

