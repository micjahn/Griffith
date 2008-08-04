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

from sqlalchemy import *
from copy import deepcopy
import sqlalchemy
import logging
log = logging.getLogger("Griffith")
import db
    
__conditions = { # default
    'loaned_only'     : False,
    'not_loaned_only' : False,
    'seen_only'       : False,
    'not_seen_only'   : False,
    'collections'     : [], # list of collection_ids
    'volumes'         : [], # list of volume_ids
    'tags'            : [], # list of tag_ids
    'loaned_to'       : [], # list of person_ids
    'sort_by'         : ["number"], # "number DESC"
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

    # TODO: get these from advfilter window
    cond.update({
            'seen_only' : True,
            #'tags'      : [1],
            'sort_by'   : ["title", "year", "number"],
            'equals'    : {"year": [2003, 2004]},
            #'startswith': {"o_title": [u"Ma", u"Ani"] }
            'contains'  : {"o_title": [u"ma", u"ani"] }
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

def create_select_query(self, query=None, conditions=None, columns=None):
    if not conditions: cond = get_conditions(self.widgets["advfilter"])
    else: cond = conditions

    if not query: # initial query not set so create one
        if not columns: columns = get_select_columns(self.config)
        query = select(columns, bind=self.db.session.bind)

    # TODO: remove after debugging:
    from pprint import pprint
    pprint(cond)

    if cond['loaned_only']:
        query.append_whereclause(db.Movie.loaned==True)
    if cond['not_loaned_only']:
        query.append_whereclause(db.Movie.loaned==False)
    if cond['seen_only']:
        query.append_whereclause(db.Movie.seen==True)
    if cond['not_seen_only']:
        query.append_whereclause(db.Movie.seen==False)

    if cond["collections"]:
        query.append_whereclause(db.Movie.collection_id.in_(cond["collections"]))

    if cond["volumes"]:
        query.append_whereclause(db.Movie.volume_id.in_(cond["volumes"]))
    
    loaned_to = []
    for per_id in cond["loaned_to"]:
        loaned_to.append(exists([db.loans_table.c.movie_id],\
                and_(db.Movie.movie_id==db.loans_table.c.movie_id, db.loans_table.c.person_id==per_id, db.loans_table.c.return_date==None)))
    if loaned_to:
        query.append_whereclause(or_(*loaned_to))
    
    tags = []
    for tag_id in cond["tags"]:
        tags.append(exists([db.MovieTag.movie_id], \
            and_(db.Movie.movie_id==db.MovieTag.movie_id, db.MovieTag.tag_id==tag_id)))
    if tags:
        query.append_whereclause(or_(*tags))

    for field in cond["equals"]:
        values = [ db.movies_table.columns[field]==value for value in cond["equals"][field] ]
        query.append_whereclause(or_(*values))
    
    for field in cond["startswith"]:
        values = [ db.movies_table.columns[field].startswith(value) for value in cond["startswith"][field] ]
        query.append_whereclause(or_(*values))

    for field in cond["like"]:
        values = [ db.movies_table.columns[field].like(value) for value in cond["like"][field] ]
        query.append_whereclause(or_(*values))
    
    for field in cond["ilike"]:
        values = [ db.movies_table.columns[field].ilike(value) for value in cond["ilike"][field] ]
        query.append_whereclause(or_(*values))
    
    for field in cond["contains"]: # XXX: it's not the SQLAlchemy's .contains() i.e. not for one-to-many or many-to-many collections
        values = [ db.movies_table.columns[field].like('%'+value+'%') for value in cond["contains"][field] ]
        query.append_whereclause(or_(*values))
    
    # sorting
    for rule in cond["sort_by"]:
        if rule.endswith(" DESC"):
            reverse = True
            rule = rule.replace(" DESC", '')
        else:
            reverse = False

        if reverse:
            query.append_order_by(desc(db.movies_table.columns[rule]))
        else:
            query.append_order_by(asc(db.movies_table.columns[rule]))

    return query

def save_conditions(cond, name, qsql):
    raise NotImplemented
def load_conditions(name, qsql):
    raise NotImplemented
