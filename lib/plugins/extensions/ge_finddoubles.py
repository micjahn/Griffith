# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright © 2010
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

import logging

from sqlalchemy.sql import select, func

from db.tables import movies as movies_table
from plugins.extensions import GriffithExtensionBase as Base
from advfilter import get_select_columns
log = logging.getLogger('Griffith')

class GriffithExtension(Base):
    name = 'Find Doubles'
    description = _('Filters for movie entry doubles')
    author = 'Michael Jahn'
    email = 'mike@griffith.cc'
    version = 0.1
    api = 1
    enabled = False

    toolbar_icon = 'gtk-find-and-replace'

    def toolbar_icon_clicked(self, widget, movie):
        query = select(get_select_columns(self.app.config), \
                       movies_table.c.title.in_(select([movies_table.c.title], bind=self.app.db.session.bind).group_by(movies_table.c.title).having(func.count(movies_table.c.movie_id)>1).correlate(None)), \
                       bind=self.app.db.session.bind)

        self.app.populate_treeview(query)
