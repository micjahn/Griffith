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
                data = self.db.get_all_data()
                for row in data:
                    t = []
                    for s in row:
                        try:
                            t.append(s.encode('latin-1'))
                        except:
                            t.append(s)
                    writer.writerow(t) 
                gutils.info(self, _("%s file has been created.")%"CSV", self.parent)
