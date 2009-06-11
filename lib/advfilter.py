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
from gutils import info

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
    'loaned_to'       : set(), # list of person_ids     (search for movies loaned to these people)
    'loan_history'    : set(), # list of person_ids     (search for movies which were loaned by these people)
    'sort_by'         : set(("number",)), # "number DESC"
    'equals'          : {}, # {column1: set(value1, value2), column2: set(value3)}
    'equals_n'        : {}, # see above
    'startswith'      : {}, # see above
    'startswith_n'    : {}, # see above
    'contains'        : {}, # see above
    'contains_n'      : {}, # see above
    'like'            : {}, # see above
    'like_n'          : {}, # see above
    'ilike'           : {}, # see above
    'ilike_n'         : {}, # see above
    }

QUERY_FIELDS = ('title', 'o_title', 'director', 'plot', 'cast', 'notes', 'number',
                'runtime', 'year', 'screenplay', 'cameraman', 'country', 'genre',
                'studio', 'classification', 'o_site', 'site', 'trailer')
QUERY_COMMANDS = ('equals', 'equals_n', 'startswith', 'startswith_n', 'contains',
                  'contains_n', 'like', 'like_n', 'ilike', 'ilike_n')
QUERY_COMMAND_NAMES = {
    'equals'      : _('is equal to'),
    'equals_n'    : _('is not equal to'),
    'startswith'  : _('starts with'),
    'startswith_n': _("doesn't start with"),
    'contains'    : _('contains'),
    'contains_n'  : _("doesn't contain"),
    'like'        : _('like'),
    'like_n'      : _('not like'),
    'ilike'       : _('ilike'),
    'ilike_n'     : _('not ilike')}

# widgets -----------------------------------------------------{{{

def show_window(self):
    if getattr(self, '_advfilter_window_is_open', False):
        log.debug('advfilter window already opened')
        return False
    initialize(self.widgets['advfilter'], self.db, self.field_names)

    if getattr(self, '_search_conditions', None):
        set_conditions(self.widgets['advfilter'], self._search_conditions, self.field_names)

    self.widgets['advfilter']['window'].show()
    self._advfilter_window_is_open = True

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
    
    from initialize import fill_advfilter_combo
    fill_advfilter_combo(self)
    
    del self._advfilter_window_is_open

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
    items = gsql.session.query(db.Tag.tag_id, db.Tag.name).all()
    if len(items):
        options = (_('ignore'), _('with'), _('without'), _('require'))
        _fill_container(widgets["tags_vbox"], items, options, 'tag_id')
        widgets["tags_frame"].show()
    else:
        widgets["tags_frame"].hide()

    # volumes
    items = gsql.session.query(db.Volume.volume_id, db.Volume.name).all()
    options = (_('ignore'), _('in'), _('not in'))
    if len(items):
        _fill_container(widgets["volumes_vbox"], items, options, 'volume_id')
        widgets["volumes_frame"].show()
    else:
        widgets["volumes_frame"].hide()

    # collections
    items = gsql.session.query(db.Collection.collection_id, db.Collection.name).all()
    if len(items):
        # use volume's options
        _fill_container(widgets["collections_vbox"], items, options, 'collection_id')
        widgets["collections_frame"].show()
    else:
        widgets["collections_frame"].hide()

    # loans
    items = gsql.session.query(db.Person.person_id, db.Person.name).all()
    if len(items):
        options = (_('ignore'), _('loaned to '), _('loan history'))
        _fill_container(widgets["loans_vbox"], items, options, 'person_id')
        widgets["loans_frame"].show()
    else:
        widgets["loans_frame"].hide()

    widgets['cb_name'].get_model().clear()
    search_filters = gsql.session.query(db.Filter.name).all()
    for filter_ in search_filters:
        widgets['cb_name'].append_text(filter_[0])
    return True

def add_query_widget(container, field_names, sel_qf='title', sel_comm='equals', text='' ):
    hbox = gtk.HBox()

    cb = gtk.combo_box_new_text()
    select = 0
    for i, field in enumerate(QUERY_FIELDS):
        if sel_qf == field:
            select = i
        cb.append_text(field_names[field])
    cb.set_active(select)

    action_cb = gtk.combo_box_new_text()
    select = 0
    for i, command in enumerate(QUERY_COMMANDS):
        if sel_comm == command:
            select = i
        action_cb.append_text(QUERY_COMMAND_NAMES[command])
    action_cb.set_active(select)

    entry = gtk.Entry()
    entry.set_text(text)

    button = gtk.Button(stock=gtk.STOCK_DELETE)
    button.connect("clicked", lambda w: hbox.destroy())

    hbox.pack_start(cb, expand=False)
    hbox.pack_start(action_cb, expand=False)
    hbox.pack_start(entry, expand=True, padding=8)
    hbox.pack_start(button, expand=False, fill=False)
    hbox.show_all()

    container.pack_start(hbox)

def set_conditions(widgets, cond, field_names): #{{{
    widgets['name'].set_text('')

    # delete old widgets
    for i in widgets['dynamic_vbox'].get_children():
        i.destroy()

    if cond["seen"] is None:
        widgets["rb_seen"].set_active(True)
    elif cond["seen"] is True:
        widgets["rb_seen_only"].set_active(True)
    elif cond["seen"] is False:
        widgets["rb_seen_only_n"].set_active(True)

    if cond["loaned"] is None:
        widgets["rb_loaned"].set_active(True)
    elif cond["loaned"] is True:
        widgets["rb_loaned_only"].set_active(True)
    elif cond["loaned"] is False:
        widgets["rb_loaned_only_n"].set_active(True)

    for hbox in widgets["tags_vbox"]:
        hbox_items = hbox.get_children()
        id_ = int(hbox_items[0].get_text())
        if id_ in cond['tags']:
            hbox_items[2].set_active(True)
        elif id_ in cond['no_tags']:
            hbox_items[3].set_active(True)
        elif id_ in cond['required_tags']:
            hbox_items[4].set_active(True)
        else:
            hbox_items[1].set_active(True)

    for hbox in widgets["volumes_vbox"]:
        hbox_items = hbox.get_children()
        id_ = int(hbox_items[0].get_text())
        if id_ in cond['volumes']:
            hbox_items[2].set_active(True)
        elif id_ in cond['no_volumes']:
            hbox_items[3].set_active(True)
        else:
            hbox_items[1].set_active(True)

    for hbox in widgets["collections_vbox"]:
        hbox_items = hbox.get_children()
        id_ = int(hbox_items[0].get_text())
        if id_ in cond['collections']:
            hbox_items[2].set_active(True)
        elif id_ in cond['no_collections']:
            hbox_items[3].set_active(True)
        else:
            hbox_items[1].set_active(True)

    for hbox in widgets["loans_vbox"]:
        hbox_items = hbox.get_children()
        id_ = int(hbox_items[0].get_text())
        if id_ in cond['loaned_to']:
            hbox_items[2].set_active(True)
        elif id_ in cond['loan_history']:
            hbox_items[3].set_active(True)
        else:
            hbox_items[1].set_active(True)

    if not cond["equals"] and not cond["startswith"] and not cond["contains"] and not cond["like"] and not cond["ilike"]:
        for i in widgets['dynamic_vbox'].get_children():
            i.destroy()
        add_query_widget(widgets['dynamic_vbox'], field_names)
    else:
        vbox = widgets['dynamic_vbox']
        for rule in ('equals', 'startswith', 'contains', 'like', 'ilike'):
            for field in cond[rule]:
                for text in cond[rule][field]:
                    add_query_widget(vbox, field_names, field, rule, text)
    return True

    #}}}

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
        hbox_items = hbox.get_children()
        if hbox_items[2].get_active():
            cond["tags"].add(int(hbox_items[0].get_label()))
        elif hbox_items[3].get_active():
            cond["no_tags"].add(int(hbox_items[0].get_label()))
        elif hbox_items[4].get_active():
            cond["required_tags"].add(int(hbox_items[0].get_label()))

    for hbox in widgets["volumes_vbox"]:
        hbox_items = hbox.get_children()
        if hbox_items[2].get_active():
            cond["volumes"].add(int(hbox_items[0].get_label()))
        elif hbox_items[3].get_active():
            cond["no_volumes"].add(int(hbox_items[0].get_label()))

    for hbox in widgets["collections_vbox"]:
        hbox_items = hbox.get_children()
        if hbox_items[2].get_active():
            cond["collections"].add(int(hbox_items[0].get_label()))
        elif hbox_items[3].get_active():
            cond["no_collections"].add(int(hbox_items[0].get_label()))

    for hbox in widgets["loans_vbox"]:
        hbox_items = hbox.get_children()
        if hbox_items[2].get_active():
            cond["loaned_to"].add(int(hbox_items[0].get_label()))
        elif hbox_items[3].get_active():
            cond["loan_history"].add(int(hbox_items[0].get_label()))

    for hbox in widgets["dynamic_vbox"]:
        hbox_items = hbox.get_children()

        entry = hbox_items[2].get_text().strip().decode('utf-8')
        if not entry: # ignore if it's empty
            continue

        field = hbox_items[0].get_active()
        if 0 > field or field > len(QUERY_FIELDS):
            continue
        else:
            field = QUERY_FIELDS[field]

            command = hbox_items[1].get_active()
            if 0 > command or command > len(QUERY_COMMANDS):
                continue
            else:
                command = QUERY_COMMANDS[command]

        cond[command].setdefault(field, set()).add(entry)

    return cond # }}}

def save(gsql, widgets):
    """saves search conditions from current filter window"""

    cond = get_conditions(widgets)
    name = widgets['cb_name'].get_active_text().decode('utf-8')
    if not name:
        log.debug("search rule name is empty")
        info(_("Name is empty"), widgets['window'])
        return False

    if sql.save_conditions(gsql, name, cond):
        info(_("Search conditions saved"), widgets['window'])
    else:
        warning(_("Cannot save search conditions"), widgets['window'])

def load(gsql, widgets, field_names):
    name = widgets['cb_name'].get_active_text().decode('utf-8')
    if not name:
        log.debug("search rule name is empty")
        return False
    cond = sql.load_conditions(gsql, name)
    if cond:
        return set_conditions(widgets, cond, field_names)
    else:
        return False

#}}}

# database related --------------------------------------------{{{

def get_def_conditions():
    return deepcopy(__conditions)

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

    self._search_conditions = conditions # save for later
    # TODO: remove after debugging:
#    from pprint import pprint
#    pprint(conditions)

    return sql.update_whereclause(query, conditions)

#}}}
