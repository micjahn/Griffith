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
import os

def update(self):
	movie_id = self.e_movie_id.get_text()
	if self.db.get_value(field="id", table="movies", where="id='%s'"%str(movie_id)) == None:
		self.debug.show("Trying to update not existing movie. Aborting")
		return False

	number = self.e_number.get_text()
	if number == None or number == '':
		gutils.error(self, msg=_("Number is not set!"))
		return False
	cursor = self.db.get_all_data(what="id, title", where="number='%s'" % number)
	if not cursor.EOF:
		cursor = cursor.FetchRow()
		old_id = cursor[0]
		old_title = cursor[1]
		if int(old_id) != int(movie_id):
			gutils.error(self, msg=_("This number is already assigned to:\n %s!") % old_title)
			return False

	data = self.db.get_all_data(what="loaned, volume_id, collection_id", where="id='%s'" % movie_id).FetchRow()
	loaned = data[0]
	volume_id = data[1]
	collection_id = data[2]
	new_volume_id = self.volume_combo_ids[self.e_volume_combo.get_active()]
	new_collection_id = self.collection_combo_ids[self.e_collection_combo.get_active()]
	if int(loaned)==1:
		if collection_id>0 and collection_id != new_collection_id:
			gutils.error(self, msg=_("You can't change collection while it is loaned!"))
			return False
		if volume_id>0 and volume_id != new_volume_id:
			gutils.error(self, msg=_("You can't change volume while it is loaned!"))
			return False
	plot_buffer = self.e_plot.get_buffer()
	with_buffer = self.e_with.get_buffer()
	obs_buffer = self.e_obs.get_buffer()
	seen = '0'
	if self.e_seen.get_active():
		seen = '1'
	if (self.e_original_title.get_text()<>''):
		t_movies = {
			'actors'         : gutils.gescape(with_buffer.get_text(with_buffer.get_start_iter(),with_buffer.get_end_iter())),
			'classification' : self.e_classification.get_text(),
			'collection_id'  : str(new_collection_id),
			'color'          : str(self.e_color.get_active()),
			'condition'      : str(self.e_condition.get_active()),
			'country'        : self.e_country.get_text(),
			'director'       : gutils.gescape(self.e_director.get_text()),
			'genre'          : self.e_genre.get_text(),
			'imdb'           : self.e_imdb.get_text(),
			'layers'         : str(self.e_layers.get_active()),
			'media'          : str(self.e_media.get_active()),
			'number'         : number,
			'num_media'      : self.e_discs.get_text(),
			'obs'            : gutils.gescape(obs_buffer.get_text(obs_buffer.get_start_iter(),obs_buffer.get_end_iter())),
			'original_title' : gutils.gescape(self.e_original_title.get_text()),
			'plot'           : gutils.gescape(plot_buffer.get_text(plot_buffer.get_start_iter(),plot_buffer.get_end_iter())),
			'rating'         : str(int(self.rating_slider.get_value())),
			'region'         : str(self.e_region.get_active()),
			'runtime'        : self.e_runtime.get_text(),
			'seen'           : seen,
			'site'           : self.e_site.get_text(),
			'studio'         : self.e_studio.get_text(),
			'title'          : gutils.gescape(self.e_title.get_text()),
			'trailer'        : self.e_trailer.get_text(),
			'volume_id'      : str(new_volume_id),
			'year'           : self.e_year.get_text(),
			'id'             : movie_id
		}
		# languages
		t_languages = {}
		for i in self.e_languages:
			if i['id'].get_active() > 0:
				lang_id = self.languages_ids[i['id'].get_active()]
				type = i['type'].get_active()
				if not t_languages.has_key(lang_id):
					t_languages[lang_id] = {}
				t_languages[lang_id][type] = True
		# tags
		t_tags = {}
		for i in self.tags_ids:
			if self.e_tags[i].get_active() == True:
				t_tags[self.tags_ids[i]] = 1

		# add movie data to database
		self.db.update_movie(t_movies, t_languages, t_tags)

		self.update_statusbar(_("Movie information has been updated"))
		# update main treelist
		treeselection = self.main_treeview.get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		tmp_model.set_value(tmp_iter,3,self.e_original_title.get_text())
		tmp_model.set_value(tmp_iter,4,self.e_title.get_text())
		tmp_model.set_value(tmp_iter,5,self.e_director.get_text())
		tmp_model.set_value(tmp_iter,5,self.e_director.get_text())
		tmp_model.set_value(tmp_iter,1,'%004d' % int(number))

		# update volume/collection combo
		self.e_volume_combo.set_active(int(new_volume_id))
		self.e_collection_combo.set_active(int(new_collection_id))
		self.e_volume_id.set_text(str(new_volume_id))
		self.e_collection_id.set_text(str(new_collection_id))
		self.e_volume_id.hide()
		self.e_collection_id.hide()

		# refresh winbdow
		self.treeview_clicked()
	else:
		gutils.error(self.w_results,_("You should fill the original title"))

def update_image(self,image,id):
	self.db.conn.Execute("UPDATE movies SET image = '" + os.path.splitext(image)[0]+"' WHERE number = '"+id+"'")
	self.update_statusbar(_("Image has been updated"))

def clear_image(self,id):
	self.db.conn.Execute("UPDATE movies SET image = '' WHERE number = '"+id+"'")
	self.update_statusbar(_("Image has been updated"))

def update_language_ids(self):
	self.languages_ids = {}
	i = 0
	for lang in self.db.Language.select():
		self.languages_ids[i] = lang.id
		i += 1

def update_tag_ids(self):
	self.tags_ids = {}
	i = 0
	for tag in self.db.Tag.select():
		self.tags_ids[i] = tag.id
		i += 1

def update_volume_combo_ids(self):
	self.volume_combo_ids = {}
	i = 0
	for volume in self.db.Tag.select():
		self.volume_combo_ids[i] = volume.id
		i += 1

def update_collection_combo_ids(self):
	self.collection_combo_ids = {}
	i = 0
	for collection in self.db.Collection.select():
		self.collection_combo_ids[i] = collection.id
		i += 1

