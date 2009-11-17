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
                        'plot', 'cast', 'notes', 'poster_md5', 'volumes.name', 'collections.name', 'media.name')

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
                if gutils.question(_("File exists. Do you want to overwrite it?"), self.parent_window):
                    overwrite = True
                else:
                    overwrite = False
            
            posterdir = os.path.join(os.path.dirname(filename[0]), 'posters')
            if not os.path.exists(posterdir):
                os.mkdir(posterdir)
            
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
                    # create image file in ./posters/...
                    md5sum = None
                    posterfilepath = ''
                    if 'poster_md5' in self.exported_columns and movie['poster_md5']:
                        md5sum = movie['poster_md5']
                    if 'movies_poster_md5' in self.exported_columns and movie['movies_poster_md5']:
                        md5sum = movie['movies_poster_md5']
                    if md5sum:
                        if gutils.create_imagefile(posterdir, md5sum, self.db):
                            posterfilepath = os.path.join('.', 'posters', md5sum + '.jpg')
                    e2 = doc.createElement('image')
                    # relative path to image related to xml file
                    t = doc.createTextNode(posterfilepath)
                    e2.appendChild(t)
                    e.appendChild(e2)
                    
                # write XML to file
                xmldata = doc.toprettyxml(encoding='utf-8')
                fp = open(filename[0], "w")
                try:
                    fp.write(xmldata)
                finally:
                    fp.close()
                gutils.info( _("%s file has been created.")%"XML", self.parent_window)

