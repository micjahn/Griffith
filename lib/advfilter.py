# -*- coding: UTF-8 -*-
# vim: fdm=marker et ts=4 sw=4
__revision__ = '$Id$'

# Copyright (c) 2008 Vasco Nunes, Piotr Ożarowski
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

from copy       import deepcopy
from sqlalchemy import select
import logging
log = logging.getLogger("Griffith")
import db
import sql
    
__conditions = { # default
    'loaned'          : None,  # None, True, False
    'seen'            : None,  # None, True, False
    'collections'     : set(), # list of collection_ids (search for movies in these collections only)
    'no_collections'  : set(), # list of collection_ids (search for movies outside these collections)
    'volumes'         : set(), # list of volume_ids     (search for movies in these volumes only)
    'no_volumes'      : set(), # list of volume_ids     (search for movies outside these volumes)
    'tags'            : set(), # list of tag_ids        (search for movies with these tags)
    'no_tags'         : set(), # list of tag_ids        (search for movies without these tags)
    'loaned_to'       : set(), # list of person_ids	    (search for movies loaned to these people)
    'sort_by'         : set(("number",)), # "number DESC"
    'equals'          : {}, # {column1: [value1, value2, ...], column2: []}
    'startswith'      : {}, # see above
    'contains'        : {}, # see above
    'like'            : {}, # see above
    'ilike'           : {}, # see above
    }

# widgets -----------------------------------------------------{{{

def show_window(self):
    self.widgets['advfilter']['window'].show()
    return True

def hide_window(self):
    self.widgets['advfilter']['window'].hide()
    return True
#}}}

# database related --------------------------------------------

def get_def_conditions():
    return deepcopy(__conditions)

def get_conditions(widgets): #{{{
    cond = get_def_conditions()

    if widgets["rb_seen"].get_active():
        cond["seen"] = None
    elif widgets["rb_seen_only"].get_active():
        cond["seen"] = True
    elif widgets["rb_seen_only_n"].get_active():
        cond["seen"] = False
    
    if widgets["rb_loaned"].get_active():
        cond["loaned"] = None
    elif widgets["rb_loaned_only"].get_active():
        cond["loaned"] = True
    elif widgets["rb_loaned_only_n"].get_active():
        cond["loaned"] = False

    # TODO: remove after tests
    cond.update({
        #'tags'      : [1],
        #'no_tags'   : [1],
        #'collections'   : set((1,)),
        'sort_by'   : set(("title", "year", "number DESC")),
        'equals'    : {"year": [2003, 2004]},
        #'startswith': {"o_title": [u"Ma", u"Ani"] }
        #'contains'  : {"o_title": [u"ma", u"ani"] },
        })
    return cond # }}}

def get_select_columns(config): # {{{
    # TODO: get them from config
    columns_to_select = [db.Movie.number,
        db.Movie.o_title, db.Movie.title,
        db.Movie.director, db.Movie.poster_md5,
        db.Movie.genre, db.Movie.seen,
        db.Movie.year, db.Movie.runtime,
        db.Movie.rating]
    return columns_to_select # }}}

def create_select_query(self, columns, conditions, query):
    if not conditions:
        conditions = get_conditions(self.widgets["advfilter"])

    if not query: # initial query not set so create one
        if not columns:
            columns = get_select_columns(self.config)
        query = select(columns, bind=self.db.session.bind)

    # TODO: remove after debugging:
    from pprint import pprint
    pprint(conditions)

    return sql.update_whereclause(query, conditions)

def save_conditions(cond, name, qsql):
    raise NotImplemented
def load_conditions(name, qsql):
    raise NotImplemented
