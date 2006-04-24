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
import os

def delete_movie(self):
	m_id = None
	m_id, m_iter = self.get_maintree_selection()
	if self.db.is_movie_loaned(movie_number=m_id):
		gutils.warning(self, msg=_("You can't delete movie while it is loaned."))
		return False
	response = gutils.question(self,_("Are you sure you want to delete this movie?"), \
		1, self.main_window)
	if response == -8:	# gtk.RESPONSE_YES == -8
		# try to delete poster image as well
		poster = self.db.get_value('image', table="movies", where="number='%s'"%m_id)
		if poster != None:
			delete_poster(self, poster)
		delete_movie_from_db(self, m_id, m_iter)
		self.main_treeview.set_cursor_on_cell(self.total_filter-1)
	else:
		return False

def delete_poster(self, poster):
	posters_dir = os.path.join(self.griffith_dir, "posters")
	image_thumbnail = os.path.join(posters_dir, "t_" + poster + ".jpg")
	image_mini = os.path.join(posters_dir, "m_" + poster + ".jpg")
	image_full = os.path.join(posters_dir, poster + ".jpg")
	if os.path.isfile(image_mini):
		try:
			os.remove(image_mini)
		except:
			self.debug.show("Can't remove %s file"%image_mini)
	if os.path.isfile(image_full):
		try:
			os.remove(image_full)
		except:
			self.debug.show("Can't remove %s file"%image_full)
	if os.path.isfile(image_thumbnail):
		try:
			os.remove(image_thumbnail)
		except:
			self.debug.show("Can't remove %s file"%image_thumbnail)

def delete_movie_from_db(self, m_id, m_iter):
	self.total -= 1
	self.total_filter -= 1
	self.db.remove_movie_by_num(m_id)
	self.treemodel.remove(m_iter)
	self.clear_details()
	self.count_statusbar()

