# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski
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

import gutils
import db
import logging
log = logging.getLogger("Griffith")

def show_people_window(self):
    self.widgets['people']['window'].show()

def hide_people_window(self):
    self.widgets['people']['window'].hide()

def add_person(self):
    clear_person(self)
    self.widgets['person']['window'].show()

def add_person_cancel(self):
    self.widgets['person']['window'].hide()
    self.widgets['people']['window'].present()

def clear_person(self):
    self.widgets['person']['name'].set_text('')
    self.widgets['person']['email'].set_text('')
    self.widgets['person']['phone'].set_text('')

def add_person_db(self):
    name = self.widgets['person']['name'].get_text().decode('utf-8')
    if name:
        p = db.Person()
        try:
            p.name = self.widgets['person']['name'].get_text().decode('utf-8')
            p.email = self.widgets['person']['email'].get_text().decode('utf-8')
            p.phone = gutils.digits_only(self.widgets['person']['phone'].get_text().decode('utf-8'))
        except ValueError, e:
            gutils.warning(self, e.message)
            return False
        self.widgets['person']['window'].hide()
        self.db.session.add(p)
        try:
            self.db.session.commit()
        except Exception, e:
            log.info(str(e))
        else:
            myiter = self.p_treemodel.insert_after(None, None)
            self.p_treemodel.set_value(myiter, 0, p.name)
            self.p_treemodel.set_value(myiter, 1, p.email)
        self.widgets['people']['window'].present()
    else:
        gutils.error(self.widgets['results']['window'],_("You should fill the person name"))

def edit_person(self):
    try:
        treeselection = self.widgets['people']['treeview'].get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        name = tmp_model.get_value(tmp_iter,0).decode('utf-8')
    except:
        return
    p = self.db.session.query(db.Person).filter_by(name=name).first()
    if p:
        self.widgets['person']['e_name'].set_text(p.name)
        self.widgets['person']['e_email'].set_text(p.email)
        self.widgets['person']['e_phone'].set_text(p.phone)
        self.widgets['person']['e_id'].set_text(str(p.person_id))
    self.widgets['person']['e_window'].show()

def edit_person_cancel(self):
    self.widgets['person']['e_window'].hide()
    self.widgets['people']['window'].present()

def update_person(self):
    p = self.db.session.query(db.Person).filter_by(person_id=self.widgets['person']['e_id'].get_text().decode('utf-8')).first()
    if not p:
        log.warning('Person not found')
        return False
    try:
        p.name = self.widgets['person']['e_name'].get_text().decode('utf-8')
        p.email = self.widgets['person']['e_email'].get_text().decode('utf-8')
        p.phone = self.widgets['person']['e_phone'].get_text().decode('utf-8')
    except ValueError, e:
        gutils.warning(self, e.message)
        return False
    self.db.session.add(p)
    try:
        self.db.session.commit()
    except Exception, e:
        log.info(str(e))
    else:
        self.update_statusbar(_("Record updated"))
        edit_person_cancel(self)
        self.p_treemodel.clear()
        for p in self.db.session.query(db.Person.name, db.Person.email).order_by(db.Person.name.asc()).all():
            myiter = self.p_treemodel.insert_before(None, None)
            self.p_treemodel.set_value(myiter, 0, p.name)
            self.p_treemodel.set_value(myiter, 1, p.email)

def delete_person(self):
    response = None
    has_history = False
    has_history_msg = ''
    try:
        treeselection = self.widgets['people']['treeview'].get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        person = tmp_model.get_value(tmp_iter,0).decode('utf-8')
    except:
        return
    person = self.db.session.query(db.Person).filter_by(name=person).first()
    if not person:
        return False
    if person.loaned_movies_count > 0:
        gutils.info(_("This person has loaned films from you. Return them first."), self.widgets['people']['window'])
        return False
    if person.returned_movies_count > 0:
        has_history = True
        has_history_msg = _("This person has data in the loan history. This data will be erased if you continue.")
    response = gutils.question(_("%s\nAre you sure you want to delete this person?" % has_history_msg), \
                               True, self.widgets['people']['window'])

    if response == -8:
        treeselection = self.widgets['people']['treeview'].get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        self.db.session.delete(person)
        try:
            self.db.session.commit()
        except Exception, e:
            log.info(str(e))
        else:
            self.p_treemodel.remove(tmp_iter)
            self.treeview_clicked()
    self.widgets['people']['window'].present()

