# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes
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

def change_filter(self):
	try:
		tmp = self.initialized
	except:
		print "not initialized" # TODO: return False
	x = 0
	self.all_movies.set_active(2)
	col_id = self.collection_combo_ids[self.f_col.get_active()]
	text = gutils.gescape(self.e_filter.get_text())
	if(len(text)==0):
		if col_id != 0:
			movies = self.db.Movie.select(order_by="number ASC", collection_id=col_id)
		else:
			movies = self.db.Movie.select(order_by="number ASC")
	else:
		criteria = self.sort_criteria[self.filter_criteria.get_active()]
		if {"year":None, "runtime":None, "num_media":None, "rating":None}.has_key(criteria):
			movies = self.db.Movie.select(self.db.Movie.c[criteria]==text, order_by="number ASC")
		else:
			movies = self.db.Movie.select(self.db.Movie.c[criteria].like='%'+text+'%', order_by="number ASC")
			where_clause = criteria + " LIKE '%" + text + "%'"
		if col_id != 0:
			where_clause += " AND collection_id = '%s'" % col_id
	cursor = self.db.get_all_data(where=where_clause, order_by="number ASC")
	#self.total_filter = cursor.RecordCount()
	# TODO: replace "while" loop with "RecordCount()" when it will be available for SQLite
	self.total_filter = 0
	while not cursor.EOF:
		self.total_filter += 1
		cursor.MoveNext()
	cursor = self.db.get_all_data(where=where_clause, order_by="number ASC") # FIXME: python-adodb doesn't have MoveFirst()
	self.populate_treeview(cursor)
	self.go_last()

def clear_filter(self):
	self.e_filter.set_text("")
	self.filter_criteria.set_active(0)
	self.total_filter = self.total
	self.go_last()
