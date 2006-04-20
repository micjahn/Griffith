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

from gettext import gettext as _
import gutils
import gtk
import os.path
import sql
import edit

def backup(self):
	"""perform a compressed griffith database/posters/preferences backup"""
	filename = gutils.file_chooser(_("Save Griffith backup"), \
		action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons= \
		(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK), \
		name='griffith_backup.zip')
	if filename[0]:
		overwrite = None
		if os.path.isfile(filename[0]):
			response = \
				gutils.question(self, \
				_("File exists. Do you want to overwrite it?"), \
				1, self.main_window)
			if response == -8:
				overwrite = True
			else:
				overwrite = False
				
		if overwrite == True or overwrite == None:
			response_zip = gutils.backup(self.griffith_dir, filename[0])
			if not response_zip:
				gutils.error(self, _("Error creating backup"), self.main_window)
			else:
				gutils.info(self, _("Backup has been created"), self.main_window)
	
def restore(self):
	"""restores a griffith compressed backup"""
	filename = gutils.file_chooser(_("Restore Griffith backup"), \
		action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons= \
		(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
		gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	if filename[0]:   
		response_unzip = gutils.restore(filename[0], self.griffith_dir)
		if not response_unzip:
			gutils.error(self, _("Can't read backup file"), self.main_window)
			return
		self.db.conn.close()
		self.db = sql.GriffithSQL(self.config, self.debug, self.griffith_dir)
		from initialize	import dictionaries
		dictionaries(self)
		gutils.info(self, _("Backup restored"), self.main_window)
		# let's refresh the treeview
		self.populate_treeview(self.db.get_all_data())
		self.total = self.db.count_records("movies")
		self.select_last_row(self.total)
		self.treeview_clicked()
		self.count_statusbar()

