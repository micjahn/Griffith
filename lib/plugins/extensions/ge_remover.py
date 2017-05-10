# -*- coding: UTF-8 -*-

__revision__ = '$Id: ge_remover.py 1576 2011-08-23 20:20:12Z mikej06 $'

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

from sqlalchemy.sql import delete, select

from db.tables import movies as movies_table
from db.tables import movie_tag as movie_tag_table
from db.tables import movie_lang as movie_lang_table
from gutils import question
from plugins.extensions import GriffithExtensionBase as Base
from sql import update_whereclause
from quick_filter import change_filter_update_whereclause

log = logging.getLogger('Griffith')

class GriffithExtension(Base):
    name = 'Remover'
    description = _('Removes all currently filtered movies')
    author = 'Piotr Ożarowski'
    email = 'piotr@griffith.cc'
    version = 0.2
    api = 1
    enabled = True # TODO: disable it by default

    toolbar_icon = 'ge_remover.png'

    def toolbar_icon_clicked(self, widget, movie):
        if question(_('Are you sure you want to remove %d movies?') % self.app.total):
            session = self.db.Session()

            # first: remove all dependend data (associated tags, languages, ...)
            query = select([movies_table.c.movie_id])
            # add conditions from simple filter
            change_filter_update_whereclause(self.app, query)
            # add conditions from adv filter
            query = update_whereclause(query, self.app._search_conditions)
            query = query.where(movies_table.c.loaned==False) # don't delete loaned movies
            log.debug(query)
            movie_ids = []
            for movie_entry in session.execute(query):
                movie_ids.append(movie_entry.movie_id)
                # tags
                query_movie_tags = delete(movie_tag_table)
                query_movie_tags = query_movie_tags.where(movie_tag_table.c.movie_id==movie_entry.movie_id)
                log.debug(query_movie_tags)
                session.execute(query_movie_tags)
                # languages
                query_movie_lang = delete(movie_lang_table)
                query_movie_lang = query_movie_lang.where(movie_lang_table.c.movie_id==movie_entry.movie_id)
                log.debug(query_movie_lang)
                session.execute(query_movie_lang)
                # TODO: removing posters if no longer used by another movie?

            # second: remove the movie entries
            if len(movie_ids):
                query = delete(movies_table)
                # use the collected movie ids because other conditions are not true anymore
                # (f.e. tags are already deleted)
                query = query.where(movies_table.c.movie_id.in_(movie_ids))

                log.debug(query)
                session.execute(query)
            session.commit()

            self.app.populate_treeview()
