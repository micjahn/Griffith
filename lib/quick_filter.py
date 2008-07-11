# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski

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
	text = gutils.gescape(self.widgets['filter']['text'].get_text())
	
	from sqlalchemy import select
	statement = select(self.db.Movie.c)
	
	if text:
		criteria = self.search_criteria[self.widgets['filter']['criteria'].get_active()]
		if criteria in ('year', 'runtime', 'media_num', 'rating'):
			statement.append_whereclause(self.db.Movie.c[criteria]==text)
		else:
			statement.append_whereclause(self.db.Movie.c[criteria].like('%'+text+'%'))
	if self.widgets['filter']['text'].is_focus():
		if len(text)<4: # filter mode
			limit = int(self.config.get('limit', 0, section='mainlist'))
			if limit > 0:
				statement.limit = limit
	self.populate_treeview(statement)

def clear_filter(self):
	# prevent multiple treeview updates
	self.initialized = False
	self.widgets['filter']['text'].set_text('')
	self.widgets['filter']['criteria'].set_active(0)
	self.widgets['filter']['collection'].set_active(0)
	self.widgets['filter']['volume'].set_active(0)
	self.widgets['filter']['tag'].set_active(0)
	self.initialized = True
	self.populate_treeview()

