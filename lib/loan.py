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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import gutils
import gtk
import datetime

def loan_movie(self):
	people = self.db.Person.select(order_by="name ASC")
	model = gtk.ListStore(str)
	if len(people)>0:
		for person in people:
			model.append([person.name])
		self.loan_to.set_model(model)
		self.loan_to.set_text_column(0)
		self.loan_to.set_active(0)
		self.w_loan_to.show()
	else:
		gutils.info(self, _("No person is defined yet."), self.main_window)

def cancel_loan(self):
	self.w_loan_to.hide()

def commit_loan(self):
	person_name = gutils.on_combo_box_entry_changed(self.loan_to)
	if person_name == '' or person_name == None:
		return False
	self.w_loan_to.hide()

	person = self.db.Person.get_by(name=person_name)
	if person==None:
		self.debug.show("commit_loan: wrong person")
		return False
	movie = self.db.Movie.get_by(movie_id=self.e_movie_id.get_text())

	# ask if user wants to loan whole collection
	loan_whole_collection = False
	if movie.collection_id>0:
		response = gutils.question(self, msg=_("Do you want to loan whole collection?"), parent=self.main_window)
		if response == gtk.RESPONSE_YES:
			loan_whole_collection = True
		elif response == gtk.RESPONSE_CANCEL:
			return False
	
	loan = self.db.Loan(movie_id=movie.movie_id, person_id=person.person_id)
	if loan_whole_collection:
		loan.collection_id = movie.collection_id
	if movie.volume_id>0:
		loan.volume_id = movie.volume_id
	loan.set_loaned()
	
	# finally, force a refresh
	self.update_statusbar(_("Movie loaned"))
	self.treeview_clicked()

def return_loan(self):
	movie_id = self.e_movie_id.get_text()
	if movie_id:
		loan = self.db.Loan.get_by(movie_id=movie_id, return_date=None)
		loan.set_returned()
		# force a refresh
		self.treeview_clicked()

