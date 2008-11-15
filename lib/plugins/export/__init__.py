# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2008 Piotr Ożarowski
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

import glob
import os.path

import logging
log = logging.getLogger("Griffith.%s" % __name__)

from sqlalchemy import select, outerjoin
import db
from sql import update_whereclause

# detect all plugins:
__all__ = [os.path.basename(x)[:-3] for x in glob.glob("%s/PluginExport*.py" % os.path.dirname(__file__))]

class Base(object):
    description = None
    author = None
    email = None
    version = None
    fields_to_export = ('number', 'o_title', 'title', 'director', 'year')

    def __init__(self, database, locations, parent_window, search_conditions, config):
        self.db = database
        self.config = config
        self.locations = locations
        self.parent_window = parent_window
        self.search_conditions = search_conditions
    
    def initialize(self):
        """Initializes plugin (get all parameters from user, etc.)"""
        return True

    def cleanup(self):
        pass

    def run(self):
        raise NotImplemented
    
    def get_query(self):
        tables = set()
        columns = []

        for i in self.fields_to_export:
            table = 'movies'
            column = i.split('.')
            if len(column) > 1:
                table = column[0]
                column = column[1]
                if table not in db.tables:
                    log.warning("Wrong table name: %s", table)
                    continue
                tables.add(table) # will be used to generate JOIN
            else:
                column = column[0]

            if column in db.tables[table].columns:
                columns.append(db.tables[table].columns[column])
            else:
                log.warning("Wrong field name: %s", i)

        joins = []
        if 'media' in tables:
            joins.append((db.tables['media'], db.tables['movies'].c.medium_id==db.tables['media'].c.medium_id))
        if 'collections' in tables:
            joins.append((db.tables['collections'], db.tables['movies'].c.collection_id==db.tables['collections'].c.collection_id))
        if 'volumes' in tables:
            joins.append((db.tables['volumes'], db.tables['movies'].c.volume_id==db.tables['volumes'].c.volume_id))
        if 'vcodecs' in tables:
            joins.append((db.tables['vcodecs'], db.tables['movies'].c.vcodec_id==db.tables['vcodecs'].c.vcodec_id))

        if joins:
            from_obj = [ outerjoin(db.tables['movies'], *(joins[0])) ]
            for j in joins[1:]:
                from_obj.append(outerjoin(from_obj[-1], *j))
            query = select(columns=columns, bind=self.db.session.bind, from_obj=from_obj, use_labels=True)
        else:
            query = select(columns=columns, bind=self.db.session.bind)

        query = update_whereclause(query, self.search_conditions)

        # save column names (will contain 'movies_title' or 'title' depending on how many tables were requested)
        self.exported_columns = query.columns

        return query
