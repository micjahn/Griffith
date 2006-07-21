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
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import csv
import gtk
import gutils
import os
from gettext import gettext as _

plugin_name = "CSV"
plugin_description = _("Full CSV list export plugin")
plugin_author = "Vasco Nunes"
plugin_author_email = "<vasco.m.nunes@gmail.com>"
plugin_version = "0.1"

class ExportPlugin:

    def __init__(self, database, locations, parent, debug):
        self.db = database
        self.locations = locations
        self.parent = parent
        self.export_csv()

    def export_csv(self):
        filename = gutils.file_chooser(_("Export a %s document")%"CSV", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='griffith_list.csv')
        if filename[0]:
            overwrite = None
            if os.path.isfile(filename[0]):
                response = gutils.question(self, _("File exists. Do you want to overwrite it?"), 1, self.parent)
                if response==-8:
                    overwrite = True
                else:
                    overwrite = False
                    
            if overwrite == True or overwrite == None:
                writer = csv.writer(file(filename[0], "w"), dialect=csv.excel)
                cursor = self.db.get_all_data(order_by="number ASC")
		while not cursor.EOF:
                    row = cursor.GetRowAssoc(0)
                    t = []
                    for s in row:
                        t.append(row[s])
                    writer.writerow(t)
                    cursor.MoveNext()
                gutils.info(self, _("%s file has been created.")%"CSV", self.parent)
