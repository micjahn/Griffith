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
import os

def update(self):
	movie_id = self._movie_id()
	movie = self.db.Movie.get_by(movie_id=movie_id)
	if movie == None:
		self.debug.show('Trying to update not existing movie. Aborting')
		return False

	number = self.widgets['movie']['number'].get_text()
	if number == None or number == '':
		gutils.error(self, msg=_('Number is not set!'))
		return False
	if int(number) != int(movie.number):
		old_movie = self.db.Movie.get_by(number=number)
		if old_movie != None and int(old_movie.movie_id) != int(movie_id):
			gutils.error(self, msg=_("This number is already assigned to:\n %s!") % old_movie.title)
			return False

	new_volume_id = self.volume_combo_ids[self.e_volume_combo.get_active()]
	new_collection_id = self.collection_combo_ids[self.e_collection_combo.get_active()]
	if int(movie.loaned)==1:
		if movie.collection_id>0 and movie.collection_id != new_collection_id:
			gutils.error(self, msg=_("You can't change collection while it is loaned!"))
			return False
		if movie.volume_id>0 and movie.volume_id != new_volume_id:
			gutils.error(self, msg=_("You can't change volume while it is loaned!"))
			return False
	plot_buffer = self.e_plot.get_buffer()
	with_buffer = self.e_with.get_buffer()
	obs_buffer = self.e_obs.get_buffer()
	if self.widgets['movie']['o_title'].get_text() != '':
		t_movies = {
			'cast'           : with_buffer.get_text(with_buffer.get_start_iter(),with_buffer.get_end_iter()),
			'classification' : self.widgets['movie']['classification'].get_text(),
			'collection_id'  : new_collection_id,
			'color'          : self.widgets['movie']['color'].get_active(),
			'cond'           : self.widgets['movie']['color'].get_active(),
			'country'        : self.widgets['movie']['country'].get_text(),
			'director'       : self.widgets['movie']['director'].get_text(),
			'genre'          : self.widgets['movie']['genre'].get_text(),
			'site'           : self.widgets['movie']['site'].get_text(),
			'layers'         : self.widgets['movie']['layers'].get_active(),
			'number'         : number,
			'media_num'      : self.widgets['movie']['discs'].get_text(),
			'notes'          : obs_buffer.get_text(obs_buffer.get_start_iter(),obs_buffer.get_end_iter()),
			'o_title'        : self.widgets['movie']['o_title'].get_text(),
			'plot'           : plot_buffer.get_text(plot_buffer.get_start_iter(),plot_buffer.get_end_iter()),
			'rating'         : self.rating_slider.get_value(),
			'region'         : self.e_region.get_active(),
			'runtime'        : self.e_runtime.get_text(),
			'o_site'         : self.widgets['movie']['o_site'].get_text(),
			'studio'         : self.e_studio.get_text(),
			'title'          : self.widgets['movie']['title'].get_text(),
			'trailer'        : self.e_trailer.get_text(),
			'volume_id'      : new_volume_id,
			'year'           : self.e_year.get_text(),
			'movie_id'       : movie_id
		}
		medium_id = self.e_media.get_active()
		if medium_id>0:
			t_movies['medium_id'] = self.media_ids[medium_id]
		vcodec_id = self.e_vcodec.get_active()
		if vcodec_id>0:
			t_movies['vcodec_id'] = self.vcodecs_ids[vcodec_id]
		seen = int(self.e_seen.get_active())
		if seen == 1:
			t_movies['seen'] = True
		else:
			t_movies['seen'] = False

		def get_id(model, text):
			for i in model:
				if i[1] == text:
					return i[0]
			return None
		# languages
		from sets import Set as set # for python2.3 compatibility
		t_languages = set()
		for row in self.lang['model']:
			lang_id   = get_id(self.lang['lang'], row[0])
			lang_type = get_id(self.lang['type'], row[1])
			acodec    = get_id(self.lang['acodec'], row[2])
			achannel  = get_id(self.lang['achannel'], row[3])
			subformat = get_id(self.lang['subformat'], row[4])
			t_languages.add((lang_id, lang_type, acodec, achannel, subformat))

		# tags
		t_tags = {}
		for i in self.tags_ids:
			if self.e_tags[i].get_active() == True:
				t_tags[self.tags_ids[i]] = 1

		# add movie data to database
		if self.db.update_movie(t_movies, t_languages, t_tags):
			self.update_statusbar(_("Movie information has been updated"))
			# update main treelist
			treeselection = self.widgets['treeview'].get_selection()
			(tmp_model, tmp_iter) = treeselection.get_selected()
			tmp_model.set_value(tmp_iter,0,'%004d' % int(number))
			tmp_model.set_value(tmp_iter,2,self.widgets['movie']['o_title'].get_text())
			tmp_model.set_value(tmp_iter,3,self.widgets['movie']['title'].get_text())
			tmp_model.set_value(tmp_iter,4,self.widgets['movie']['director'].get_text())
			# update volume/collection combo
			self.e_volume_combo.set_active(int(new_volume_id))
			self.e_collection_combo.set_active(int(new_collection_id))
			# refresh winbdow
			self.treeview_clicked()
	else:
		gutils.error(self.widgets['results']['window'],_("You should fill the original title"))

def update_image(self,image,number):
	movie = self.db.Movie.get_by(number=number)
	movie.image = os.path.splitext(image)[0]
	movie.update()
	movie.flush()
	self.widgets['movie']['picture_button'].set_sensitive(True)
	self.update_statusbar(_("Image has been updated"))

def update_volume_combo_ids(self):
	self.volume_combo_ids = {}
	self.volume_combo_ids[0] = 0
	i = 1
	for volume in self.db.Volume.select():
		self.volume_combo_ids[i] = volume.volume_id
		i += 1

def update_collection_combo_ids(self):
	self.collection_combo_ids = {}
	self.collection_combo_ids[0] = 0
	i = 1
	for collection in self.db.Collection.select():
		self.collection_combo_ids[i] = collection.collection_id
		i += 1

