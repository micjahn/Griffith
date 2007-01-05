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

from gettext import gettext as _

def filter_not_seen(self):
	self.populate_treeview()
	self.update_statusbar(_("Filter activated. Showing only not seen movies."))
	self.go_last()

def filter_loaned(self):
	self.populate_treeview()
	self.update_statusbar(_("Filter activated. Showing only loaned movies."))
	self.go_last()

def filter_all(self):
	self.populate_treeview()
	self.count_statusbar()
	self.go_last()

def filter_by_volume(self, volume_id):
	from quick_filter import clear_filter
	clear_filter(self)
	self.populate_treeview(where={'volume_id':volume_id})
	volume_name = self.db.Volume.get_by(volume_id=volume_id).name
	self.update_statusbar(_("Filter activated. Showing only movies from volume: %s")%volume_name)
	self.go_last()

def filter_by_collection(self, collection_id):
	from quick_filter import clear_filter
	clear_filter(self)
	self.populate_treeview(where={'collection_id':collection_id})
	collection_name = self.db.Collection.get_by(collection_id=collection_id).name
	self.update_statusbar(_("Filter activated. Showing only movies from collection: %s")%collection_name)
	self.go_last()

