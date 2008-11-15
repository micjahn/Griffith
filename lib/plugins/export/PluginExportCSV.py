# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes
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

import csv
import gtk
import os
import gutils
import db
from plugins.export import Base

class ExportPlugin(Base):
    name = "CSV"
    description = _("Full CSV list export plugin")
    author = "Vasco Nunes"
    email = "<vasco.m.nunes@gmail.com>"
    version = "0.3"

    fields_to_export = ('number', 'o_title', 'title', 'director', 'year', 'classification', 'country',
                        'genre', 'rating', 'runtime', 'studio', 'seen', 'loaned', 'o_site', 'site', 'trailer',
                        'plot', 'cast', 'notes', 'image', 'volumes.name', 'collections.name', 'media.name')

    def run(self):
        basedir = None
        if not self.config is None:
            basedir = self.config.get('export_dir', None, section='export-csv')
        if not basedir:
            filename = gutils.file_chooser(_("Export a %s document")%"CSV", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.csv')
        else:
            filename = gutils.file_chooser(_("Export a %s document")%"CSV", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.csv',folder=basedir)
        if filename and filename[0]:
            if not self.config is None and filename[1]:
                self.config.set('export_dir', filename[1], section='export-csv')
                self.config.save()
            overwrite = None
            if os.path.isfile(filename[0]):
                response = gutils.question(_("File exists. Do you want to overwrite it?"), True, self.parent_window)
                if response==-8:
                    overwrite = True
                else:
                    overwrite = False
            
            if overwrite == True or overwrite is None:
                movies = self.get_query().execute()

                writer = csv.writer(file(filename[0], 'w'), dialect=csv.excel)
                for movie in movies:
                    t = []
                    for s in self.exported_columns:
                        t.append(movie[s])
                    writer.writerow(t)
                gutils.info(_("%s file has been created.") % "CSV", self.parent_window)

