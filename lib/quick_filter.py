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
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import gutils

def change_filter(self):
	x = 0
	self.widgets['menu']['all_movies'].set_active(2)
	col_id = self.collection_combo_ids[self.widgets['filter']['column'].get_active()]
	text = gutils.gescape(self.widgets['filter']['text'].get_text())
	
	# sort column
	sort_column_name = self.config.get('sortby', 'number')
	if self.db.Movie.c.has_key(sort_column_name):
		order_column = self.db.Movie.c[sort_column_name]
	else:
		order_column = self.db.Movie.c.number
	
	if(len(text)==0):
		if col_id != 0:
			movies = self.db.Movie.select(self.db.Movie.c.collection_id==col_id, order_by=[order_column])
		else:
			movies = self.db.Movie.select(order_by=[order_column])
	else:
		from sqlalchemy import select
		movies = select(self.db.Movie.c, order_by=[order_column])
		criteria = self.search_criteria[self.widgets['filter']['criteria'].get_active()]
		if {'year':None, 'runtime':None, 'media_num':None, 'rating':None}.has_key(criteria):
			movies.append_whereclause(self.db.Movie.c[criteria]==text)
		else:
			movies.append_whereclause(self.db.Movie.c[criteria].like('%'+text+'%'))
		if col_id != 0:
			movies.append_whereclause(self.db.Movie.c.collection_id==col_id)
		movies = movies.execute().fetchall()
	self.total_filter = len(movies)
	self.populate_treeview(movies)
	self.go_last()

def clear_filter(self):
	self.widgets['filter']['text'].set_text("")
	self.widgets['filter']['criteria'].set_active(0)
	self.total_filter = self.total
	self.go_last()
