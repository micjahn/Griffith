# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright © 2009 Piotr Ożarowski
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published byp
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

from sqlalchemy.sql import select, update

from db.tables import movies as movies_table
from plugins.extensions import GriffithExtensionBase as Base
from sql import update_whereclause

log = logging.getLogger('Griffith')

class GriffithExtension(Base):
    name = 'Mark as seen'
    description = _('Marks all currently filtered movies as seen')
    author = 'Piotr Ożarowski'
    email = 'piotr@griffith.cc'
    version = 0.1
    api = 1
    enabled = False # disabled by default

    toolbar_icon = 'seen.png'

    def toolbar_icon_clicked(self, widget, movie):
        log.info('marking %d movies as seen', self.app.total)
        #TODO: 'are you sure?'
        session = self.db.Session()
        update_query = update(movies_table, values={'seen': True})

        update_whereclause(update_query, self.app._search_conditions)

        session.execute(update_query)
        session.commit()

        self.app.populate_treeview() # update seen widget in the list
