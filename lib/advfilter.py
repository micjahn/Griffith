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

import gtk
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
    'required_tags'   : set(), # like in tags, but movie must contain all listed tags
    'loaned_to'       : set(), # list of person_ids	    (search for movies loaned to these people)
    'loan_history'    : set(), # list of person_ids	    (search for movies which were loaned by these people)
    'sort_by'         : set(("number",)), # "number DESC"
    'equals'          : {}, # {column1: set(value1, value2), column2: set(value3)}
    'startswith'      : {}, # see above
    'contains'        : {}, # see above
    'like'            : {}, # see above
    'ilike'           : {}, # see above
    }
    
QUERY_FIELDS = ('title', 'o_title', 'director', 'plot', 'cast', 'notes', 'number',
                'runtime', 'year', 'screenplay', 'cameraman', 'country', 'genre',
                'studio', 'classification', 'o_site', 'site', 'trailer')
QUERY_COMMANDS = ('equals', 'startswith', 'contains', 'like', 'ilike')

# widgets -----------------------------------------------------{{{

def show_window(self):
    initialize(self.widgets['advfilter'], self.db, self.field_names)
    self.widgets['advfilter']['window'].show()
    return True

def hide_window(self):
    widgets = self.widgets['advfilter']
    widgets['window'].hide()

    # clear the window
    for i in widgets['tags_vbox'].get_children():
        i.destroy()
    for i in widgets['volumes_vbox'].get_children():
        i.destroy()
    for i in widgets['collections_vbox'].get_children():
        i.destroy()
    for i in widgets['loans_vbox'].get_children():
        i.destroy()
    for i in widgets['dynamic_vbox'].get_children():
        i.destroy()

    return True

def _fill_container(container, items, options, id_name):
    for item in items:
        hbox = gtk.HBox()

        label_id = gtk.Label()
        label_id.set_text(str(getattr(item, id_name)))
        hbox.pack_start(label_id, expand=False)

        widget = gtk.RadioButton(label=options[0]) # first widget
        hbox.pack_start(widget, expand=False, padding=4)
        for option in options[1:]: # create rest of the widgets, use first one as a group
            next_widget = gtk.RadioButton(widget, label=option)
            hbox.pack_start(next_widget, expand=False, padding=4)
        
        label = gtk.Label()
        label.set_text(item.name)
        hbox.pack_start(label, padding=16, expand=False)

        hbox.show_all()
        label_id.hide()
        container.pack_start(hbox)

def initialize(widgets, gsql, field_names):
    # tags
    items = gsql.session.query(db.Tag).all()
    options = (_('ignore'), _('with'), _('without'), _('require'))
    _fill_container(widgets["tags_vbox"], items, options, 'tag_id')

    # volumes
    items = gsql.session.query(db.Volume).all()
    options = (_('ignore'), _('in'), _('not in'))
    _fill_container(widgets["volumes_vbox"], items, options, 'volume_id')
    
    # collections
    items = gsql.session.query(db.Collection).all()
    # use volume's options
    _fill_container(widgets["collections_vbox"], items, options, 'collection_id')

    # loans
    items = gsql.session.query(db.Person).all()
    options = (_('ignore'), _('loaned to '), _('loan history'))
    _fill_container(widgets["loans_vbox"], items, options, 'person_id')

    add_query_widget(widgets['dynamic_vbox'], gsql, field_names)

    return True

def add_query_widget(container, gsql, field_names):
    hbox = gtk.HBox()

    cb = gtk.combo_box_new_text()
    for field in QUERY_FIELDS:
        cb.append_text(field_names[field])
    cb.set_active(0)

    action_cb = gtk.combo_box_new_text()
    for command in QUERY_COMMANDS:
        action_cb.append_text(_(command))
    action_cb.set_active(0)

    entry = gtk.Entry()
    
    button = gtk.Button(stock=gtk.STOCK_DELETE)
    button.connect("clicked", lambda w: hbox.destroy())

    hbox.pack_start(cb, expand=False)
    hbox.pack_start(action_cb, expand=False)
    hbox.pack_start(entry, expand=True, padding=8)
    hbox.pack_start(button, expand=False, fill=False)
    hbox.show_all()

    container.pack_start(hbox)
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

    for hbox in widgets["tags_vbox"]:
        childs = hbox.get_children()
        if childs[2].get_active():
            cond["tags"].add(int(childs[0].get_label()))
        elif childs[3].get_active():
            cond["no_tags"].add(int(childs[0].get_label()))
        elif childs[4].get_active():
            cond["required_tags"].add(int(childs[0].get_label()))

    for hbox in widgets["volumes_vbox"]:
        childs = hbox.get_children()
        if childs[2].get_active():
            cond["volumes"].add(int(childs[0].get_label()))
        elif childs[3].get_active():
            cond["no_volumes"].add(int(childs[0].get_label()))
    
    for hbox in widgets["collections_vbox"]:
        childs = hbox.get_children()
        if childs[2].get_active():
            cond["collections"].add(int(childs[0].get_label()))
        elif childs[3].get_active():
            cond["no_collections"].add(int(childs[0].get_label()))
    
    for hbox in widgets["loans_vbox"]:
        childs = hbox.get_children()
        if childs[2].get_active():
            cond["loaned_to"].add(int(childs[0].get_label()))
        elif childs[3].get_active():
            cond["loan_history"].add(int(childs[0].get_label()))
    
    for hbox in widgets["dynamic_vbox"]:
        childs = hbox.get_children()

        entry = childs[2].get_text().strip().decode('utf-8')
        if not entry: # ignore if it's empty
            continue

        field = childs[0].get_active()
        if 0 < field > len(QUERY_FIELDS):
            continue
        else:
            field = QUERY_FIELDS[field]
            
            command = childs[1].get_active()
            if 0 < command > len(QUERY_COMMANDS):
                continue
            else:
                command = QUERY_COMMANDS[command]
            
        cond[command].setdefault(field, set()).add(entry)

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
