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

def filter_not_seen(self):
	cursor = self.db.get_not_seen_movies()
	self.update_statusbar(_("Filter activated. Showing only not seen movies."))
	self.populate_treeview(cursor)
	self.total_filter = self.db.count_records('movies', 'seen=0')
	self.go_last()

def filter_loaned(self):
	cursor = self.db.get_loaned_movies()
	self.update_statusbar(_("Filter activated. Showing only loaned movies."))
	self.populate_treeview(cursor)
	self.total_filter = self.db.count_records('movies', 'loaned=1')
	self.go_last()

def filter_all(self):
	cursor = self.db.get_all_data(order_by="number ASC")
	self.count_statusbar()
	self.populate_treeview(cursor)
	argum = self.total
	self.total_filter = self.total
	self.go_last()

def filter_by_volume(self, volume_id):
	cursor = self.db.conn.Execute("SELECT name FROM volumes WHERE id = '%s'" % volume_id)
	volume_name = cursor.fields[0]
	self.update_statusbar(_("Filter activated. Showing only movies from volume: %s")%volume_name)
	cursor = self.db.select_movies_by_volume(volume_id)
	self.populate_treeview(cursor)
	self.total_filter = self.db.count_records('movies', 'volume_id="%s"'%volume_id)
	self.go_last()

def filter_by_collection(self, collection_id):
	cursor = self.db.conn.Execute("SELECT name FROM collections WHERE id = '%s'" % collection_id)
	collection_name = cursor.fields[0]
	self.update_statusbar(_("Filter activated. Showing only movies from collection: %s")%collection_name)
	cursor = self.db.select_movies_by_collection(collection_id)
	self.populate_treeview(cursor)
	self.total_filter = self.db.count_records('movies', 'collection_id="%s"'%collection_id)
	self.go_last()

