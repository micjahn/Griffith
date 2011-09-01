# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright © 2011
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

import os
import logging
import gutils
from sqlalchemy.sql import delete, exists, and_, not_
from db.tables import movies as movies_table
from db.tables import posters as posters_table

from plugins.extensions import GriffithExtensionBase as Base

log = logging.getLogger('Griffith')

class GriffithExtension(Base):
    name = 'Database Cleanup and Maintenance'
    description = _('Removes unused posters, executes the VACUUM command and corrects a wrong page size if possible (SQLite)')
    author = 'Michael Jahn'
    email = 'mike@griffith.cc'
    version = 0.1
    api = 1
    enabled = False

    toolbar_icon = 'gtk-goto-bottom'

    def toolbar_icon_clicked(self, widget, movie):
        #
        # remove unused posters
        #
        session = self.db.Session()
        delete_posters = delete(posters_table)
        delete_posters = delete_posters.where(not_(exists([movies_table.c.movie_id], and_(posters_table.c.md5sum==movies_table.c.poster_md5)).correlate(posters_table)))
        log.debug(delete_posters)
        session.execute(delete_posters)
        session.commit()
        #
        # compressing sqlite databases
        #
        if self.app.config.get('type', 'sqlite', section='database') == 'sqlite':
            databasefilename = "%s.db" % os.path.join(self.app.locations['home'], self.app.config.get('name', section='database'))
            pagesize = gutils.get_filesystem_pagesize(databasefilename)

            # works since sqlite 3.5.8
            # python 2.5 doesn't include 3.x but perhaps in future versions
            # another way is the installation of pysqlite2 with 2.5.6/2.6.0 or higher
            try:
                from pysqlite2 import dbapi2 as sqlite3

                con = sqlite3.connect(databasefilename)
                try:
                    con.isolation_level = None
                    cur = con.cursor()
                    cur.execute('PRAGMA page_size=' + str(pagesize))
                    cur.execute('VACUUM;')
                finally:
                    con.close()
            except:
                log.error('fallback to default driver')
                self.app.db.engine.execute('PRAGMA page_size=' + str(pagesize))
                self.app.db.engine.execute('VACUUM;')
        gutils.info(_("Finished"))

