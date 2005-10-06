# -*- coding: UTF-8 -*-

__revision__ = '$Id: loan.py,v 1.21 2005/10/04 19:43:24 pox Exp $'

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
import gtk
import os.path
import datetime
import update

def loan_movie(self):
	data = self.db.get_all_data("people","name ASC")
	model = gtk.ListStore(str)
	if data:
		for row in data:
			model.append([row['name']])
		self.loan_to.set_model(model)
		self.loan_to.set_text_column(0)
		self.loan_to.set_active(0)
		self.w_loan_to.show()
	else:
		gutils.info(self, _("No person is defined yet."), self.main_window)
		
def cancel_loan(self):
	self.w_loan_to.hide()
	
def commit_loan(self):
	person = gutils.on_combo_box_entry_changed(self.loan_to)
	if person == '' or person == None:
		return
	self.w_loan_to.hide()
	# add a flag on the list
	treeselection = self.main_treeview.get_selection()
	(tmp_model, tmp_iter) = treeselection.get_selected()
	self.Image.set_from_file(self.locations['images']  + "/loaned.png")
	Pixbuf = self.Image.get_pixbuf()
	self.treemodel.set_value(tmp_iter, 0, Pixbuf)
	
	# movie is now loaned. change db
	movie_id = self.e_number.get_text()
	self.db.cursor.execute("SELECT volume_id, collection_id FROM movies WHERE number='%s'"%movie_id)
	volume_id, collection_id = self.db.cursor.fetchall()[0]
	data_person = self.db.select_person_by_name(person)

	# ask if user wants to loan whole collection
	if collection_id>0:
		loan_whole_collection = False
		response = gutils.question(self, msg="Do you want to loan whole collection?", parent=self.main_window)
		if response == gtk.RESPONSE_YES:
			loan_whole_collection = True
		elif response == gtk.RESPONSE_CANCEL:
			return False

	if volume_id>0 and collection_id>0:
		if loan_whole_collection:
			update.update_collection(self, id=collection_id, volume_id=volume_id, loaned=1)
		else:
			update.update_volume(self, id=volume_id, loaned=1)
	elif collection_id>0:
		if loan_whole_collection:
			update.update_collection(self, id=collection_id, loaned=1)
		else:
			self.db.cursor.execute("UPDATE movies SET loaned='1' WHERE number='%s';" % movie_id)
	elif volume_id>0:
		update.update_volume(self, id=volume_id, loaned=1)
	else:
		self.db.cursor.execute("UPDATE movies SET loaned='1' WHERE number='%s';" % movie_id)
	self.update_statusbar(_("Movie loaned"))

	# next, we insert a new row on the loans table
	data_movie=self.db.select_movie_by_num(movie_id)
	query = "INSERT INTO 'loans'('id', 'person_id','"
	if collection_id>0:
		query +="collection_id"
	elif volume_id>0:
		query +="volume_id"
	else:
		query +="movie_id"
	query += "', 'date', 'return_date') VALUES (Null, '" + str(data_person[0]['id']) + "', '"
	if collection_id>0:
		query += str(collection_id)
	elif volume_id>0:
		query += str(volume_id)
	else:
		query += str(movie_id)
	query += "', '" + str(datetime.date.today()) + "', '');"
	self.db.cursor.execute(query)
	self.db.con.commit()
	# finally, force a refresh
	self.treeview_clicked()
	self.main_treeview.set_cursor(int(movie_id)-1, None, False)
	
def return_loan(self):
	movie_id = self.e_number.get_text()
	if movie_id:
		self.db.cursor.execute("SELECT volume_id, collection_id FROM movies WHERE number='%s'"%movie_id)
		volume_id, collection_id = self.db.cursor.fetchall()[0]
	
		collection_is_loaned = False
		if collection_id>0:
			# if all movies in collection are loaned, ask if whole collection was returned
			self.db.cursor.execute("SELECT loaned FROM collections WHERE id='%s'"%collection_id)
			collection_is_loaned = self.db.cursor.fetchall()[0][0]
		
		if volume_id>0 and collection_is_loaned == True:
			update.update_collection(self, id=collection_id, volume_id=volume_id, loaned=0)
		elif collection_is_loaned == True:
			update.update_collection(self, id=collection_id, loaned=0)
		elif volume_id>0:
			update.update_volume(self, id=volume_id, loaned=0)
		else:
			self.db.cursor.execute("UPDATE movies SET loaned='0' WHERE number='%s';" % movie_id)
		
		self.update_statusbar(_("Movie returned"))	
		
		data_movie=self.db.select_movie_by_num(movie_id)
		# fill return information on loans table
		query = "UPDATE loans SET return_date='%s' WHERE " % str(datetime.date.today())
		if collection_id>0:
			query +="collection_id='%s'" % collection_id
		elif volume_id>0:
			query +="volume_id"
		else:
			query +="movie_id"
		query += " AND return_date = ''"
		self.db.cursor.execute(query)
		self.db.con.commit()			
		
		# remove the flag on the list
		treeselection = self.main_treeview.get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		self.Image.set_from_file(self.locations['images']  + "/not_loaned.png")		
		Pixbuf = self.Image.get_pixbuf()
		self.treemodel.set_value(tmp_iter, 0, Pixbuf)
		self.treeview_clicked()
		self.main_treeview.set_cursor(int(movie_id)-1, None, False)
