# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
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

from gettext import gettext as _
import gutils

def show_people_window(self):
	self.w_people.show()

def hide_people_window(self):
	self.w_people.hide()

def add_person(self):
	clear_person(self)
	self.w_add_person.show()

def add_person_cancel(self):
	self.w_add_person.hide()

def clear_person(self):
	self.ap_name.set_text("")
	self.ap_email.set_text("")
	self.ap_phone.set_text("")

def add_person_db(self):
	if (self.ap_name.get_text()<>''):
		p = self.db.Person()
		p.name = self.ap_name.get_text()
		p.email = self.ap_email.get_text()
		p.phone = self.ap_phone.get_text()
		self.w_add_person.hide()
		if p.add_to_db():
			myiter = self.p_treemodel.insert_after(None, None)
			self.p_treemodel.set_value(myiter,0,str(self.ap_name.get_text()))
			self.p_treemodel.set_value(myiter,1,str(self.ap_email.get_text()))
	else:
		gutils.error(self.w_results,_("You should fill the person name"))

def edit_person(self):
	try:
		treeselection = self.widgets['preferences']['treeview'].get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		name = tmp_model.get_value(tmp_iter,0)
	except:
		return
	p = self.db.Person.get_by(name=name)
	if p != None:
		self.ep_name.set_text(str(p.name))
		self.ep_email.set_text(str(p.email))
		self.ep_phone.set_text(str(p.phone))
		self.ep_id.set_text(str(p.person_id))
	self.w_edit_person.show()

def edit_person_cancel(self):
	self.w_edit_person.hide()

def update_person(self):
	p = self.db.Person.get_by(person_id=self.ep_id.get_text())
	if p == None:
		return False
	p.name = self.ep_name.get_text()
	p.email = self.ep_email.get_text()
	p.phone = self.ep_phone.get_text()
	if p.update_in_db():
		self.update_statusbar(_("Record updated"))
		edit_person_cancel(self)
		self.p_treemodel.clear()
		for p in self.db.Person.select(order_by='name ASC'):
			myiter = self.p_treemodel.insert_before(None, None)
			self.p_treemodel.set_value(myiter, 0, str(p.name))
			self.p_treemodel.set_value(myiter, 1, str(p.email))

def delete_person(self):
	response = None
	has_history = False
	has_history_msg = ''
	try:
		treeselection = self.widgets['preferences']['treeview'].get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		person = tmp_model.get_value(tmp_iter,0)
	except:
		return
	person = self.db.Person.get_by(name=person)
	if not person:
		return False
	data = self.db.Loan.select_by(person_id=person.person_id, return_date=None)
	if len(data)>0:
		gutils.info(self, _("This person has loaned films from you. Return them first."), self.widgets['window'])
		return False
	data = self.db.Loan.select_by(person_id=person.person_id)
	if len(data)>0:
		has_history = True
		has_history_msg = _("This person has data in the loan history. This data will be erased if you continue.")
	response = gutils.question(self,_("%s\nAre you sure you want to delete this person?" % has_history_msg), \
		1, self.widgets['window'])

	if response == -8:
		treeselection = self.widgets['preferences']['treeview'].get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		if person.remove_from_db():
			self.p_treemodel.remove(tmp_iter)
			self.treeview_clicked()

