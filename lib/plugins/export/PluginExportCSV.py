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
import gettext
gettext.install('griffith', unicode=1)
import gutils
import db

plugin_name = "CSV"
plugin_description = _("Full CSV list export plugin")
plugin_author = "Vasco Nunes"
plugin_author_email = "<vasco.m.nunes@gmail.com>"
plugin_version = "0.2"

class ExportPlugin:

    def __init__(self, database, locations, parent, **kwargs):
        self.db = database
        self.locations = locations
        self.parent = parent
        if kwargs.has_key('config'):
            self.persistent_config = kwargs['config']
        else:
            self.persistent_config = None
        self.export_csv()

    def export_csv(self):
        basedir = None
        if not self.persistent_config is None:
            basedir = self.persistent_config.get('export_dir', None, section='export-csv')
        if basedir is None:
            filename = gutils.file_chooser(_("Export a %s document")%"CSV", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.csv')
        else:
            filename = gutils.file_chooser(_("Export a %s document")%"CSV", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.csv',folder=basedir)
        if filename[0]:
            if not self.persistent_config is None and filename[1]:
                self.persistent_config.set('export_dir', filename[1], section='export-csv')
                self.persistent_config.save()
            overwrite = None
            if os.path.isfile(filename[0]):
                response = gutils.question(_("File exists. Do you want to overwrite it?"), True, self.parent)
                if response==-8:
                    overwrite = True
                else:
                    overwrite = False
                    
            if overwrite == True or overwrite is None:
                writer = csv.writer(file(filename[0], 'w'), dialect=csv.excel)
                for movie in self.db.session.query(db.Movie).all():
                    t = []
                    for s in ('number', 'o_title', 'title', 'director', 'year', 'classification', 'country',
                            'genre', 'rating', 'runtime', 'studio', 'seen', 'loaned', 'o_site', 'site', 'trailer',
                            'plot', 'cast', 'notes','image'):
                        t.append(movie[s])
                    writer.writerow(t)
                gutils.info(_("%s file has been created.")%"CSV", self.parent)
