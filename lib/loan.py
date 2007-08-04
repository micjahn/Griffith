# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes, Piotr Ożarowski
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
import gtk
import datetime

def loan_movie(self):
	people = self.db.Person.select(order_by='name ASC')
	model = gtk.ListStore(str)
	if len(people)>0:
		for person in people:
			model.append([person.name])
		self.widgets['movie']['loan_to'].set_model(model)
		self.widgets['movie']['loan_to'].set_text_column(0)
		self.widgets['movie']['loan_to'].set_active(0)
		self.widgets['w_loan_to'].show()
	else:
		gutils.info(self, _("No person is defined yet."), self.widgets['window'])

def cancel_loan(self):
	self.widgets['w_loan_to'].hide()

def commit_loan(self):
	person_name = gutils.on_combo_box_entry_changed(self.widgets['movie']['loan_to'])
	if person_name == '' or person_name is None:
		return False
	self.widgets['w_loan_to'].hide()

	person = self.db.Person.get_by(name=person_name)
	if person is None:
		self.debug.show("commit_loan: person doesn't exist")
		return False
	if self._movie_id:
		movie = self.db.Movie.get_by(movie_id=self._movie_id)
		if not movie:
			self.debug.show("commit_loan: wrong movie_id")
			return False
	else:
		self.debug.show("commit_loan: movie not selected")
		return False

	# ask if user wants to loan whole collection
	loan_whole_collection = False
	if movie.collection_id>0:
		response = gutils.question(self, msg=_("Do you want to loan whole collection?"), parent=self.widgets['window'])
		if response == gtk.RESPONSE_YES:
			loan_whole_collection = True
		elif response == gtk.RESPONSE_CANCEL:
			return False
	
	loan = self.db.Loan(movie_id=movie.movie_id, person_id=person.person_id)
	if loan_whole_collection:
		loan.collection_id = movie.collection_id
	if movie.volume_id>0:
		loan.volume_id = movie.volume_id
	if loan.set_loaned():
		self.update_statusbar(_("Movie loaned"))
		self.treeview_clicked()

def return_loan(self):
	if self._movie_id:
		loan = self.db.Loan.get_by(movie_id=self._movie_id, return_date=None)
		if loan is None:
			movie = self.db.Movie.get_by(movie_id=self._movie_id)
			if movie.collection is not None and movie.collection.loaned:
				#print len(movie.loans) # FIXME: why it's == 0? (mappers problem?)
				loan = self.db.Loan.get_by(collection_id=movie.collection.collection_id, return_date=None)
			if movie.volume is not None and movie.volume.loaned:
				loan = self.db.Loan.get_by(volume_id=movie.volume.volume_id, return_date=None)
		if loan and loan.set_returned():
			self.treeview_clicked()

def get_loan_info(db, movie_id, volume_id=None, collection_id=None):
	"""Returns current collection/volume/movie loan data"""
	from sqlalchemy import and_, or_
	movie = db.Movie.get_by(movie_id=movie_id)
	if movie is None:
		return False
	
	# fix or add volume/collection data:
	if movie.collection_id is not None:
		collection_id = movie.collection_id
	if movie.volume_id is not None:
		volume_id = movie.volume_id
	
	if collection_id>0 and volume_id>0:
		return db.Loan.get_by(
				and_(or_(db.Loan.c.collection_id==collection_id,
						db.Loan.c.volume_id==volume_id,
						db.Loan.c.movie_id==movie_id),
					db.Loan.c.return_date==None))
	elif collection_id>0:
		return db.Loan.get_by(
				and_(or_(db.Loan.c.collection_id==collection_id,
						db.Loan.c.movie_id==movie_id)),
					db.Loan.c.return_date==None)
	elif volume_id>0:
		return db.Loan.get_by(and_(or_(db.Loan.c.volume_id==volume_id,
							db.Loan.c.movie_id==movie_id)),
						db.Loan.c.return_date==None)
	else:
		return db.Loan.get_by(db.Loan.c.movie_id==movie_id,db.Loan.c.return_date==None)

def get_loan_history(db, movie_id, volume_id=None, collection_id=None):
	"""Returns collection/volume/movie loan history"""
	from sqlalchemy import and_, or_, not_
	if collection_id>0 and volume_id>0:
		return db.Loan.select_by(and_(or_(db.Loan.c.collection_id==collection_id,
							db.Loan.c.volume_id==volume_id,
							db.Loan.c.movie_id==movie_id),
						not_(db.Loan.c.return_date==None)))
	elif collection_id>0:
		return db.Loan.select_by(and_(or_(db.Loan.c.collection_id==collection_id,
							db.Loan.c.movie_id==movie_id),
						not_(db.Loan.c.return_date==None)))
	elif volume_id>0:
		return db.Loan.select_by(and_(or_(db.Loan.c.volume_id==volume_id,
							db.Loan.c.movie_id==movie_id),
						not_(db.Loan.c.return_date==None)))
	else:
		return db.Loan.select_by(db.Loan.c.movie_id==movie_id,not_(db.Loan.c.return_date==None))

