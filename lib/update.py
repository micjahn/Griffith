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
	id = self.e_movie_id.get_text()

	number = self.e_number.get_text()
	self.db.cursor.execute("SELECT id, title FROM movies WHERE number='%s'" % number)
	tmp = self.db.cursor.fetchall()
	if len(tmp) > 0:
		if (int(tmp[0]['id']) != int(id)):
			gutils.error(self, msg=_("This number is already assigned to:\n %s!") % tmp[0]['title'])
			return False
	
	self.db.cursor.execute("SELECT loaned, volume_id, collection_id FROM movies WHERE id='%s'" % id)
	loaned, volume_id, collection_id = self.db.cursor.fetchall()[0]
	new_volume_id = gutils.findKey(self.e_volume_combo.get_active(), self.volume_combo_ids)
	new_collection_id = gutils.findKey(self.e_collection_combo.get_active(), self.collection_combo_ids)
	if loaned:
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
		self.db.cursor.execute(
			"UPDATE movies SET original_title = '"
			+gutils.gescape(self.e_original_title.get_text())+"', title ='"
			+gutils.gescape(self.e_title.get_text())+"', director='"
			+gutils.gescape(self.e_director.get_text())+"', plot ='"
			+gutils.gescape(plot_buffer.get_text(plot_buffer.get_start_iter(),plot_buffer.get_end_iter()))+"', year='"
			+self.e_year.get_text()+"', runtime ='"
			+self.e_runtime.get_text()+"',actors = '"
			+gutils.gescape(with_buffer.get_text(with_buffer.get_start_iter(),with_buffer.get_end_iter()))+"', country='"
			+self.e_country.get_text()+"', genre ='"
			+self.e_genre.get_text()+"', rating ='"
			+str(int(self.rating_slider.get_value()))+"', classification ='"
			+self.e_classification.get_text()+"', studio = '"
			+self.e_studio.get_text()+"', site ='"
			+self.e_site.get_text()+"', condition ="
		
			+str(self.e_condition.get_active())+", color ="
			+str(self.e_color.get_active())+", region ="
			+str(self.e_region.get_active())+", layers ="
			+str(self.e_layers.get_active())+", imdb ='"
			
			+self.e_imdb.get_text()+"', seen ='"
			+seen+"', obs ='"
			+gutils.gescape(obs_buffer.get_text(obs_buffer.get_start_iter(),obs_buffer.get_end_iter()))+"', trailer='"
			+self.e_trailer.get_text()
			+"', media ='" + str(self.e_media.get_active())
			+"', num_media ='" + self.e_discs.get_text()
			+"', volume_id='" + str(new_volume_id)
			+"', collection_id='" + str(new_collection_id)
			+"', number = '" + number
		
			+"' WHERE id = '" + id +"'"
		)
		
		# languages
		selected = {}
		self.db.cursor.execute("DELETE FROM movie_lang WHERE movie_id = '%s';" % id)	# remove old data
		for i in self.e_languages:
			if i['id'].get_active() != None:
				lang_id = self.languages_ids[i['id'].get_active()]
				type = i['type'].get_active()
				if not selected.has_key(lang_id):
					selected[lang_id] = {}
				selected[lang_id][type] = True
		for lang in selected.keys():
			for type in selected[lang].keys():
				self.db.cursor.execute("INSERT INTO movie_lang(movie_id, lang_id, type) VALUES ('%s', '%s', '%s');" % (id, lang, type) )

		# tags
		selected = {}
		self.db.cursor.execute("DELETE FROM movie_tag WHERE movie_id = '%s';" % id)
		for i in self.tags_ids:
			if self.e_tags[i].get_active() == True:
				selected[self.tags_ids[i]] = 1
		for i in selected.keys():
			self.db.cursor.execute("INSERT INTO movie_tag(movie_id, tag_id) VALUES ('%s', '%s');" % (id, i) )

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
	self.db.cursor.execute(
		"UPDATE movies SET image = '"
		+os.path.splitext(image)[0]+"' WHERE number = '"+id+"'")
	self.db.con.commit()
	self.update_statusbar(_("Image has been updated"))
	
def clear_image(self,id):
	self.db.cursor.execute(
		"UPDATE movies SET image = '' WHERE number = '"+id+"'")
	self.db.con.commit()
	self.update_statusbar(_("Image has been updated"))

def update_language_ids(self):
	self.languages_ids = {}
	i = 0
	for lang in self.db.get_all_data(table_name="languages", order_by=None):
		self.languages_ids[i] = lang['id']
		i += 1

def update_tag_ids(self):
	self.tags_ids = {}
	i = 0
	for tag in self.db.get_all_data(table_name="tags", order_by=None):
		self.tags_ids[i] = tag['id']
		i += 1
