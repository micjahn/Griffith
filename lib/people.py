# -*- coding: UTF-8 -*-

__revision__ = '$Id: people.py,v 1.11 2005/08/16 12:25:58 iznogoud Exp $'

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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

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
        self.db.cursor.execute(
            "INSERT INTO 'people'('id','name','email','phone') VALUES (Null,'"
            +gutils.gescape(self.ap_name.get_text())+"','"
            +gutils.gescape(self.ap_email.get_text())+"','"
            +gutils.gescape(self.ap_phone.get_text())+"')")
        self.db.con.commit()
        self.w_add_person.hide()
        myiter = self.p_treemodel.insert_after(None, None)
        self.p_treemodel.set_value(myiter,0,str(self.ap_name.get_text()))
        self.p_treemodel.set_value(myiter,1,str(self.ap_email.get_text()))
    else:
        gutils.error(self.w_results,_("You should fill the person name"))
        
def edit_person(self):
    try:
        treeselection = self.p_treeview.get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        name = tmp_model.get_value(tmp_iter,0)
    except:
        return
    data = self.db.select_person_by_name(name)
    for row in data:
        self.ep_name.set_text(str(row['name']))
        self.ep_email.set_text(str(row['email']))
        self.ep_phone.set_text(str(row['phone']))
        self.ep_id.set_text(str(row['id']))
    self.w_edit_person.show()
    
def edit_person_cancel(self):
    self.w_edit_person.hide()
    
def update_person(self):
    self.db.cursor.execute("UPDATE people SET name = '" + self.ep_name.get_text() +"', email='" + self.ep_email.get_text() +"', phone='" + self.ep_phone.get_text() +"' WHERE id = '" + self.ep_id.get_text() +"'") 
    self.db.con.commit()
    self.update_statusbar(_("Record updated"))
    self.db.con.commit()
    self.treeview_clicked()
    edit_person_cancel(self)
    self.p_treemodel.clear()
    data = self.db.get_all_data('people', 'name ASC')

    for row in data:
        myiter = self.p_treemodel.insert_before(None, None)
        self.p_treemodel.set_value(myiter, 0, str(row['name']))
        self.p_treemodel.set_value(myiter, 1, str(row['email']))
        
def delete_person(self):
    response = None
    past = 0
    past_msg = ""
    try:
        treeselection = self.p_treeview.get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        person = tmp_model.get_value(tmp_iter,0)
    except:
        return
    data_person=self.db.select_person_by_name(person)
    self.db.cursor.execute("SELECT * FROM loans WHERE person_id = '" + str(data_person[0]['id']) + "' AND return_date = ''")
    data = self.db.cursor.fetchall()
    if data:
        gutils.info(self, _("This person has loaned films from you. First return them."), self.main_window)
        return
    data_person=self.db.select_person_by_name(person)
    self.db.cursor.execute("SELECT * FROM loans WHERE person_id = '" + str(data_person[0]['id']) + "'")
    data_past = self.db.cursor.fetchall()
    if data_past:
        past = 1
        past_msg = _("This person has data in the loan history. This data will be erased if you continue.")
    try:
        response = gutils.question(self,_("%s\nAre you sure you want to delete this person?"%past_msg), \
            1, self.main_window)

        if response == -8:
            delete_person_from_db(self, past)
        else:
            pass
    except:
        pass
        
def delete_person_from_db(self, past):
    treeselection = self.p_treeview.get_selection()
    (tmp_model, tmp_iter) = treeselection.get_selected()
    name = tmp_model.get_value(tmp_iter, 0)
    data_person=self.db.select_person_by_name(name)
    if past:
        self.db.cursor.execute("DELETE FROM loans WHERE person_id = '"+str(data_person[0]['id'])+"'")
    self.db.remove_person_by_name(name)
    self.p_treemodel.remove(tmp_iter)
    self.treeview_clicked()
