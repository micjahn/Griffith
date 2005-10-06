# -*- coding: UTF-8 -*-

__revision__ = '$Id: delete.py,v 1.11 2005/08/13 09:59:58 iznogoud Exp $'

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

def delete_movie(self):
    m_id = None
    try:
        m_id, m_iter = self.get_maintree_selection()
        response = gutils.question(self,_("Are you sure you want to delete this movie?"), \
            1, self.main_window)
        if response == -8:
            delete_movie_from_db(self, m_id, m_iter)
        else:
            pass
    except:
        pass
        
def delete_movie_from_db(self, m_id, m_iter):
    self.total -= 1
    self.db.remove_movie_by_num(m_id)
    self.treemodel.remove(m_iter)
    self.clear_details()
    self.select_last_row(self.total)
    #update statusbar
    self.count_statusbar()
