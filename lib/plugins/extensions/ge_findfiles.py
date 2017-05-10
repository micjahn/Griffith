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
log = logging.getLogger('Griffith')

class GriffithExtension(Base):
    name = 'Find Files'
    description = _('Filters for movie entry doubles')
    author = 'Michael Jahn'
    email = 'mike@griffith.cc'
    version = 0.1
    api = 1
    enabled = False

    toolbar_icon = 'gtk-find-and-replace'

    def toolbar_icon_clicked(self, widget, movie):
        import kaa.metadata
        info = kaa.metadata.parse('D:\\test.flv')#
        print info
        disc = kaa.metadata.parse('/dev/dvd')
