# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
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
import os
import gtk

def treeview_clicked(self):
	try:
		tmp = self.initialized # if Griffith is not initialized, return false
	except:
		return
	if self.total:
		self.clear_details()
		treeselection = self.main_treeview.get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		m_id = tmp_model.get_value(tmp_iter,1)
		movie = self.db.Movie.select_by(id=m_id)

		plot_buffer = self.e_plot.get_buffer()
		obs_buffer = self.e_obs.get_buffer()
		with_buffer = self.e_with.get_buffer()
		with_iter = with_buffer.get_start_iter()

		self.e_movie_id.set_text(str(int(movie.id)))
		self.e_number.set_text(str(int(movie.number)))
		self.e_original_title.set_text(str(movie.original_title))
		if movie.title:
			self.e_title.set_text(str(movie.title))
		if movie.director:
			self.e_director.set_text(str(movie.director))
		if movie.plot:
			plot_buffer.set_text(str(movie.plot))
		if movie.num_media:
			self.e_discs.set_value(int(movie.num_media))
		if movie.year:
			self.e_year.set_text(str(movie.year))
		if movie.runtime:
			self.e_runtime.set_text(str(int(movie.runtime)))
		if movie.actors:
			with_buffer.set_text(str(movie.actors))
		if movie.country:
			self.e_country.set_text(str(movie.country))
		if movie.genre:
			self.e_genre.set_text(str(movie.genre))
		if movie.condition != None and movie.condition != '':
			self.e_condition.set_active(int(str(movie.condition)))
		else:
			self.e_condition.set_active(5) # N/A
		if movie.region != None and movie.region != '':
			self.e_region.set_active(int(str(movie.region)))
		else:
			self.e_condition.set_active(9) # N/A
		if movie.layers != None and movie.layers != '':
			self.e_layers.set_active(int(str(movie.layers)))
		else:
			self.e_condition.set_active(4) # N/A
		if movie.color != None and movie.color != '':
			self.e_color.set_active(int(str(movie.color)))
		else:
			self.e_condition.set_active(3) # N/A
		if movie.classification:
			self.e_classification.set_text(str(movie.classification))
		if movie.studio:
			self.e_studio.set_text(str(movie.studio))
		if movie.site:
			self.e_site.set_text(str(movie.site))
		if movie.imdb:
			self.e_imdb.set_text(str(movie.imdb))
		if movie.seen:
			self.e_seen.set_active(True)
		else:
			self.e_seen.set_active(False)
		if movie.rating:
			self.image_rating.show()
			self.rating_slider.set_value(int(movie.rating))
		else:
			self.image_rating.hide()
		if movie.trailer:
			self.e_trailer.set_text(str(movie.trailer))
		if movie.obs<>None:
			obs_buffer.set_text(str(movie.obs))
		if movie.media:
			self.e_media.set_active(int(movie.media))

		# check loan status and adjust buttons and history box
		if int(movie.loaned)==1:
			self.popup_loan.set_sensitive(False)
			self.popup_email.set_sensitive(True)
			self.popup_return.set_sensitive(True)
			self.loan_button.set_sensitive(False)
			self.b_email_reminder.set_sensitive(True)
			self.return_button.set_sensitive(True)
		else:
			self.popup_loan.set_sensitive(True)
			self.popup_email.set_sensitive(False)
			self.popup_return.set_sensitive(False)
			self.return_button.set_sensitive(False)
			self.b_email_reminder.set_sensitive(False)
			self.loan_button.set_sensitive(True)

		# poster
		tmp_dest = os.path.join(self.griffith_dir, "posters")
		tmp_img = os.path.join(tmp_dest, "m_%s.jpg"%movie.image)
		tmp_img2 = os.path.join(tmp_dest, "%s.jpg"%movie.image)

		if movie.image and os.path.isfile(tmp_img2):
			image_path = tmp_img
			self.delete_poster.set_sensitive(True)
			self.zoom_poster.set_sensitive(True)
		else:
			image_path = os.path.join(self.locations['images'], "default.png")
			self.delete_poster.set_sensitive(False)
			self.zoom_poster.set_sensitive(False)
		# lets see if we have a scaled down medium image already created
		if os.path.isfile(image_path):
			pass
		else:
			# if not, lets make one for future use :D
			original_image = os.path.join(tmp_dest, "%s.jpg"%movie.image)
			if os.path.isfile(original_image):
				gutils.make_medium_image(self, "%s.jpg"%movie.image)
			else:
				self.Image.set_from_file(os.path.join(self.locations['images'], "default.png"))
				pixbuf = self.Image.get_pixbuf()
		handler = self.e_picture.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image_path))
		if int(movie.loaned) == 1:
			if movie.collection_id > 0 and self.db.is_collection_loaned(row['collection_id']) == 1:
				data_loan = self.db.get_loan_info(collection_id=movie.collection_id)
			elif movie.volume_id > 0 and self.db.is_volume_loaned(movie.volume_id) == 1:
				data_loan = self.db.get_loan_info(volume_id=movie.volume_id)
			else:
				data_loan = self.db.get_loan_info(movie_id=movie.number)
			data_loan = data_loan.GetRowAssoc(0)
			data_person = self.db.select_person_by_id(int(data_loan['person_id'])).GetRowAssoc(0)
			self.person_name = str(data_person['name'])
			self.person_email = str(data_person['email'])
			self.loan_date = str(data_loan['date'])
			self.loan_info.set_label(self._("This movie has been loaned to ") + self.person_name + self._(" on ") + self.loan_date[:10])
		else:
			self.loan_info.set_label(self._("Movie not loaned"))

		#loan history	
		self.loans_treemodel.clear()
		return 
		loans = self.db.get_loan_history(collection_id=movie.collection_id, volume_id=movie.volume_id, movie_id=movie.id)
		for loan in loans:
			myiter = self.loans_treemodel.append(None)
			self.loans_treemodel.set_value(myiter, 0,'%s' % str(loan.date)[:10])
			if loan.return_date and  loan.return_date != '':
				self.loans_treemodel.set_value(myiter, 1, str(loan.return_date)[:10])
			else:
				self.loans_treemodel.set_value(myiter, 1, "---")
			person = self.db.select_person_by_id(int(loan.person_id))
			person = person.GetRowAssoc(0)
			self.loans_treemodel.set_value(myiter, 2, person['name'])
			cursor.MoveNext()

		#volumes/collections
		i = gutils.findKey(movie.volume_id, self.volume_combo_ids)
		if not i:
			i = 0
		self.e_volume_combo.set_active(i)
		i = gutils.findKey(movie.collection_id, self.collection_combo_ids)
		if not i:
			i = 0
		self.e_collection_combo.set_active(i)
		self.e_volume_id.set_text(str(movie.volume_id))
		self.e_collection_id.set_text(str(movie.collection_id))
		self.e_volume_id.hide()
		self.e_collection_id.hide()

		#languages
		cursor = self.db.get_all_data("movie_lang", where="movie_id='%s'" % movie.id)
		self.e_languages = []	# language widgets
		if not cursor.EOF:
			from initialize import create_language_hbox
			while not cursor.EOF:
				i = cursor.GetRowAssoc(0)
				create_language_hbox(self, widget=self.e_lang_vbox, tab=self.e_languages, default=i['lang_id'], type=i['type'])
				cursor.MoveNext()

		#tags
		cursor = self.db.get_all_data("movie_tag", where="movie_id='%s'" % movie.id, what="tag_id")
		while not cursor.EOF:
			tag = cursor.fields[0]
			i = gutils.findKey(tag, self.tags_ids)
			self.e_tags[i].set_active(True)
			cursor.MoveNext()

def populate(self, movies):
	self.treemodel.clear()
	for movie in movies:
		myiter = self.treemodel.append(None)
		self.treemodel.set_value(myiter,1,'%004d' % int(movie.number))

		# check preferences to hide or show columns
		if self.config.get('view_otitle') == 'True':
			self.otitle_column.set_visible(True)
		else:
			self.otitle_column.set_visible(False)
		if self.config.get('view_title') == 'True':
			self.title_column.set_visible(True)
		else:
			self.title_column.set_visible(False)
		if self.config.get('view_director') == 'True':
			self.director_column.set_visible(True)
		else:
			self.director_column.set_visible(False)
		if self.config['view_image'] == 'True':
			self.image_column.set_visible(True)
			tmp_dest = os.path.join(self.griffith_dir, "posters")
			tmp_img = os.path.join(tmp_dest, "t_"+str(movie.image)+".jpg")
			if movie.image and os.path.isfile(tmp_img):
				image_path = tmp_img
			else:
				image_path = os.path.join(self.locations['images'], "default_thumbnail.png")
			# lets see if we have a scaled down thumbnail already created
			if os.path.isfile(os.path.join(tmp_dest, "t_"+str(movie.image)+".jpg")):
				pass
			else:
				# if not, lets make one for future use :D
				original_image = os.path.join(tmp_dest, "%s.jpg"%str(movie.image))
				if os.path.isfile(original_image):
					gutils.make_thumbnail(self, "%s.jpg"%str(movie.image))
				else:
					self.Image.set_from_file("%s/default_thumbnail.png"%self.locations['images'])
					pixbuf = self.Image.get_pixbuf()
			self.Image.set_from_file(image_path)
			pixbuf = self.Image.get_pixbuf()
			self.treemodel.set_value(myiter, 2, pixbuf)

		else:
			# let's hide image column from main treeview since we don't want it to be visible
			self.image_column.set_visible(False)
		self.treemodel.set_value(myiter,3,str(movie.o_title))
		self.treemodel.set_value(myiter,4,str(movie.title))
		self.treemodel.set_value(myiter,5,str(movie.director))
