# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ożarowski
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

import gtk

import db
import gutils

log = logging.getLogger("Griffith")

def loan_movie(self):
    people = self.db.session.query(db.Person.name).order_by(db.Person.name.asc()).all()
    model = gtk.ListStore(str)
    if len(people)>0:
        for person in people:
            model.append([person.name])
        self.widgets['movie']['loan_to'].set_model(model)
        self.widgets['movie']['loan_to'].set_text_column(0)
        self.widgets['movie']['loan_to'].set_active(0)
        self.widgets['w_loan_to'].show()
    else:
        gutils.info(_("No person is defined yet."), self.widgets['window'])

def cancel_loan(self):
    self.widgets['w_loan_to'].hide()

def commit(self):
    person_name = gutils.on_combo_box_entry_changed(self.widgets['movie']['loan_to'])
    if not person_name:
        return False
    self.widgets['w_loan_to'].hide()

    session = self.db.Session()

    person = session.query(db.Person.person_id).filter_by(name=person_name).first()
    if not person:
        log.warn("loan_commit: person doesn't exist")
        return False
    if self._movie_id:
        movie = session.query(db.Movie).filter_by(movie_id=self._movie_id).first()
        if not movie:
            log.warn("loan_commit: movie doesn't exist")
            return False
    else:
        log.warn("loan_commit: movie not selected")
        return False

    # ask if user wants to loan whole collection
    loan_whole_collection = False
    if movie.collection_id > 0:
        if gutils.question(_('Do you want to loan whole collection?'), window=self.widgets['window']):
            loan_whole_collection = True
        else:
            return False
    
    try:
        if movie.loan_to(person, whole_collection=loan_whole_collection):
            session.commit()
    except Exception, e:
        session.rollback()
        if e.message == 'loaned movies in the collection already':
            gutils.warning(_("Collection contains loaned movie.\nLoan aborted!"))
            return False
        else:
            raise e

    self.update_statusbar(_("Movie loaned"))
    self.treeview_clicked()

def return_loan(self):
    if not self._movie_id:
        log.warn('return_loan: movie not selected')
        return False

    session = self.db.Session()

    movie = session.query(db.Movie).filter_by(movie_id=self._movie_id).first()
    if not movie or not movie.loan_details:
        log.warn("return_loan: movie or loan doesn't exist (id=%s)", self._movie_id)
        return False
    movie.loan_details.returned_on() # current date will be used be default
    session.commit()
    self.treeview_clicked()

