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
	x = 0
	criteria = gutils.on_combo_box_entry_changed(self.filter_criteria)
	text = gutils.gescape(self.e_filter.get_text())
	if criteria == self._("Original Title") and text:
		data = self.db.select_movie_by_original_title(text)
	elif criteria == self._("Title")  and text:
		data = self.db.select_movie_by_title(text)
	elif criteria == self._("Director")  and text:
		data = self.db.select_movie_by_director(text)
	elif criteria == self._("Year")  and text:
		data = self.db.select_movie_by_year(text)
	elif criteria == self._("Number")  and text:
		data = self.db.select_movie_by_num(text)
	elif criteria == self._("Rating")  and text:
		data = self.db.select_movie_by_rating(text)
	elif criteria == self._("Genre")  and text:
		data = self.db.select_movie_by_genre(text)
	elif criteria == self._("With")  and text:
		data = self.db.select_movie_by_actors(text)
	else:
		data = self.db.get_all_data(order_by="number ASC")
	for row in data:
		x = x + 1	
	self.total_filter = x
	self.treemodel.clear()
	self.clear_details()
	self.populate_treeview(data)
		
def clear_filter(self):
	self.e_filter.set_text("")
	self.filter_criteria.set_active(1)
	self.total_filter = self.total
