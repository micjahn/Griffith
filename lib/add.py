# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published byp
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
import string
import shutil
import quick_filter
import widgets

def add_movie(self):
	quick_filter.clear_filter(self)
	next_number = gutils.find_next_available(self)
	initialize_add_dialog(self)
	self.am_number.set_value(int(next_number))
	self.add_movie_window.show()
	self.active_plugin = ""

def initialize_add_dialog(self):
	"""clears all fields in dialog"""
	self.am_original_title.set_text("")
	self.am_title.set_text("")
	self.am_year.set_text("")
	self.am_runtime.set_text("")
	self.am_country.set_text("")
	self.am_studio.set_text("")
	self.am_site.set_text("")
	self.am_director.set_text("")
	self.am_imdb.set_text("")
	self.am_trailer.set_text("")
	self.am_title.set_text("")
	self.am_picture.set_from_file("")
	self.am_picture_name.set_text("")
	with_buffer = self.am_with.get_buffer()
	with_buffer.set_text("")
	obs_buffer = self.am_obs.get_buffer()
	obs_buffer.set_text("")
	self.am_genre.set_text("")
	self.am_discs.set_text("1")
	# define defaults
	self.rating_slider_add.set_value(0)
	self.am_seen.set_active(False)
	if self.config.get('media'):
		self.am_media.set_active(int(self.config.get('media')))
	if self.config.get('color'):
		self.am_color.set_active(int(self.config.get('color')))
	if self.config.get('layers'):
		self.am_layers.set_active(int(self.config.get('layers')))
	if self.config.get('region'):
		self.am_region.set_active(int(self.config.get('region')))
	if self.config.get('condition'):
		self.am_condition.set_active(int(self.config.get('condition')))
	self.am_volume_combo.set_active(0)
	self.am_collection_combo.set_active(0)
	plot_buffer = self.am_plot.get_buffer()
	plot_buffer.set_text("")
	self.am_original_title.grab_focus()
	# ensure we are at the first page of the notebook
	self.nb_add.set_current_page(0)
	self.am_source.set_active(self.d_plugin)
	image = os.path.join(self.locations['images'], "default.png")
	# languages - remove old widgets
	for i in self.am_lang_vbox.get_children():
		i.destroy()
	self.am_languages = []
	# tags - clear tag selection
	for i in self.am_tag_vbox.get_children():
		i.set_active(False)

	handler = self.Image.set_from_file(image)
	handler = self.am_picture.set_from_pixbuf(self.Image.get_pixbuf())
	self.am_original_title.grab_focus()
	widgets.connect_add_signals(self)

def add_movie_db(self, close):
	if  len(self.am_original_title.get_text()) or len(self.am_title.get_text()):
		plot_buffer = self.am_plot.get_buffer()
		with_buffer = self.am_with.get_buffer()
		obs_buffer = self.am_obs.get_buffer()
		number = self.am_number.get_text()
		(filepath, filename) = os.path.split(self.am_picture_name.get_text())
		t_movies = {
			'actors'         : gutils.gescape(with_buffer.get_text(with_buffer.get_start_iter(), with_buffer.get_end_iter())),
			'classification' : gutils.gescape(self.am_classification.get_text()),
			'color'          : self.am_color.get_active(),
			'cond'           : self.am_condition.get_active(),
			'country'        : gutils.gescape(self.am_country.get_text()),
			'director'       : gutils.gescape(self.am_director.get_text()),
			'genre'          : gutils.gescape(self.am_genre.get_text()),
			'image'          : filename,
			'layers'         : self.am_layers.get_active(),
			'loaned'         : False,
			'media_num'      : self.am_discs.get_text(),
			'notes'          : gutils.gescape(obs_buffer.get_text(obs_buffer.get_start_iter(), obs_buffer.get_end_iter())),
			'number'         : number,
			'o_site'         : self.am_site.get_text(),
			'o_title'        : gutils.gescape(self.am_original_title.get_text()),
			'plot'           : gutils.gescape(plot_buffer.get_text(plot_buffer.get_start_iter(), plot_buffer.get_end_iter())),
			'rating'         : self.rating_slider_add.get_value(),
			'region'         : self.am_region.get_active(),
			'runtime'        : self.am_runtime.get_text(),
			'site'           : self.am_imdb.get_text(),
			'studio'         : gutils.gescape(self.am_studio.get_text()),
			'title'          : gutils.gescape(self.am_title.get_text()),
			'trailer'        : self.am_trailer.get_text(),
			'year'           : self.am_year.get_text()
		}
		vol_id = self.am_volume_combo.get_active()
		if vol_id>0:
			t_movies['volume_id'] = self.volume_combo_ids[vol_id]
		col_id = self.am_collection_combo.get_active()
		if col_id>0:
			t_movies['collection_id'] = self.collection_combo_ids[col_id]
		medium_id = self.am_media.get_active()
		if medium_id>0:
			t_movies['medium_id'] = medium_id
		seen = int(self.am_seen.get_active())
		if seen == 1:
			t_movies['seen'] = True
		else:
			t_movies['seen'] = False
		# languages
		t_languages = {}
		for i in self.am_languages:
			if i['id'].get_active() > 0:
				lang_id = self.languages_ids[i['id'].get_active()]
				type = i['type'].get_active()
				if not t_languages.has_key(lang_id):
					t_languages[lang_id] = {}
				t_languages[lang_id][type] = True
		# tags
		t_tags = {}
		for i in self.tags_ids:
			if self.am_tags[i].get_active() == True:
				t_tags[self.tags_ids[i]] = 1

		# add movie data to database
		self.db.add_movie(t_movies, t_languages, t_tags)

		# lets move poster from tmp to posters dir
		tmp_dest = os.path.join(self.griffith_dir, "posters")

		if self.windows:
			temp_dir = "C:\\windows\\temp\\"
		else:
			temp_dir = "/tmp/"

		pic = string.replace(self.am_picture_name.get_text()+".jpg",temp_dir,"")

		if len(self.am_picture_name.get_text()):
			if os.path.isfile(os.path.join(temp_dir, pic)):
				shutil.move(os.path.join(temp_dir, pic), tmp_dest)

		if int(self.am_number.get_text()) >= 2:
			insert_after = self.treemodel.get_iter(int(self.am_number.get_text())-2)
		else:
			insert_after = None
		myiter = self.treemodel.insert_after(None, insert_after)

		if len(self.am_picture_name.get_text()):
			image_path = os.path.join(tmp_dest, pic)
			#lets make the thumbnail and medium image from poster for future use
			gutils.make_thumbnail(self, image_path)
			gutils.make_medium_image(self, image_path)
		else:
			image_path = os.path.join(self.locations['images'], "default.png")
		handler = self.Image.set_from_file(image_path)
		pixbuf = self.Image.get_pixbuf()
		self.treemodel.set_value(myiter, 1, '%004d' % int(self.am_number.get_text()))
		self.treemodel.set_value(myiter, 2, pixbuf.scale_simple(30,40,3))
		self.treemodel.set_value(myiter, 3, str(self.am_original_title.get_text()))
		self.treemodel.set_value(myiter, 4, str(self.am_title.get_text()))
		self.treemodel.set_value(myiter, 5, str(self.am_director.get_text()))
		#update statusbar
		self.total += 1
		self.total_filter = self.total
		self.count_statusbar()
		#select new entry from main treelist
		treeselection = self.main_treeview.get_selection()
		treeselection.select_iter(myiter)
		self.main_treeview.set_cursor(int(self.am_number.get_text())-1)
		self.treeview_clicked()
		next_number=gutils.find_next_available(self)
		initialize_add_dialog(self)
		self.am_number.set_text(str(next_number))

		if close:
			self.hide_add_movie()
	else:
		gutils.error(self.w_results, _("You should fill the original title\nor the movie title."))

def change_rating_from_slider(self):
	rating = int(self.rating_slider_add.get_value())
	self.image_add_rating.show()
	try:
		rimage = int(str(self.config.get('rating_image')))
	except:
		rimage = 0
	if rimage:
		prefix = ""
	else:
		prefix = "meter"
	rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, rating)
	handler = self.image_add_rating.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(rating_file))

def populate_with_results(self):
	m_id = None
	if self.founded_results_id:
		self.debug.show("self.founded:results_id: %s" % self.founded_results_id)
		m_id = self.founded_results_id
	else:
		self.founded_results_id = 0
		treeselection = self.results_treeview.get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		m_id = tmp_model.get_value(tmp_iter, 0)
	self.hide_results()

	try:
		self.debug.show("m_id: %s" % m_id)
	except:
		self.debug.show("m_id: Bad UNICODE character")

	plugin_name = 'PluginMovie' + self.active_plugin
	plugin = __import__(plugin_name)
	self.movie = plugin.Plugin(m_id)
	self.movie.open_page(self.add_movie_window)
	self.movie.parse_movie()
	self.am_original_title.set_text(gutils.convert_entities(self.movie.original_title))
	self.am_title.set_text(gutils.convert_entities(self.movie.title))
	self.am_director.set_text(gutils.convert_entities(self.movie.director))
	plot_buffer = self.am_plot.get_buffer()
	plot_buffer.set_text(gutils.convert_entities(self.movie.plot))
	with_buffer = self.am_with.get_buffer()
	with_buffer.set_text(gutils.convert_entities(self.movie.with))
	self.am_country.set_text(gutils.convert_entities(self.movie.country))
	self.am_genre.set_text(gutils.convert_entities(self.movie.genre))
	self.am_classification.set_text(gutils.convert_entities(self.movie.classification))
	self.am_studio.set_text(gutils.convert_entities(self.movie.studio))
	self.am_site.set_text(gutils.remove_accents(self.movie.site))
	self.am_imdb.set_text(gutils.remove_accents(self.movie.imdb))
	self.am_trailer.set_text(gutils.remove_accents(self.movie.trailer))
	self.am_year.set_text(self.movie.year)
	notes_buffer = self.am_obs.get_buffer()
	notes_buffer.set_text(gutils.convert_entities(self.movie.notes))
	self.am_runtime.set_text(self.movie.running_time)
	if self.movie.rating:
		self.rating_slider_add.set_value(float(self.movie.rating))
	# poster
	if self.windows:
		temp_dir = "C:\\windows\\temp\\"
	else:
		temp_dir = "/tmp/"
	if self.movie.picture != "":
		image = os.path.join(temp_dir, self.movie.picture)
		try:
			handler = self.Image.set_from_file(image)
			pixbuf = self.Image.get_pixbuf()
			self.am_picture.set_from_pixbuf(pixbuf.scale_simple(100, 140, 3))
			self.am_picture_name.set_text(string.replace(self.movie.picture, ".jpg",""))
		except:
			image = os.path.join(self.locations['images'], "default.png")
			handler = self.Image.set_from_file(image)
			self.am_picture.set_from_pixbuf(self.Image.get_pixbuf())
	else:
		image = os.path.join(self.locations['images'], "default.png")
		handler = self.Image.set_from_file(image)
		Pixbuf = self.Image.get_pixbuf()
		self.am_picture.set_from_pixbuf(Pixbuf)

def show_websearch_results(self):
	total = self.founded_results_id = 0
	for g in self.search_movie.ids:
		if ( str(g) != '' ):
			total += 1
	if total > 1:
		self.w_results.show()
		self.w_results.set_keep_above(True)
		row = None	
		key = 0
		self.treemodel_results.clear()
		for row in self.search_movie.ids:
			if (str(row)!=''):
				title = str(self.search_movie.titles[key]).decode(self.search_movie.encode)
				myiter = self.treemodel_results.insert_before(None, None)
				self.treemodel_results.set_value(myiter, 0, str(row))
				self.treemodel_results.set_value(myiter, 1, title)
			key +=1
		self.results_treeview.show()
	elif total==1:
		self.results_treeview.set_cursor(total-1)
		for row in self.search_movie.ids:
			if ( str(row) != '' ):
				self.founded_results_id = str(row)
				populate_with_results(self)
	else:
		gutils.error(self.w_results, _("No results"), self.add_movie_window)

def get_from_web(self):
	"""search the movie in web using the active plugin"""
	if len(self.am_original_title.get_text()) \
		or len(self.am_title.get_text()):
		option = gutils.on_combo_box_entry_changed_name(self.am_source)
		self.active_plugin = option
		plugin_name = 'PluginMovie%s' % option
		plugin = __import__(plugin_name)
		self.search_movie = plugin.SearchPlugin()
		if len(self.am_original_title.get_text()):
			self.search_movie.url = self.search_movie.original_url_search
			self.search_movie.title = \
				gutils.remove_accents(self.am_original_title.get_text(), 'utf-8')
		elif len(self.am_title.get_text()) \
			and not len(self.am_original_title.get_text()):
			self.search_movie.url = self.search_movie.translated_url_search
			self.search_movie.title = \
				gutils.remove_accents(self.am_title.get_text(), 'utf-8')
		self.search_movie.search(self.add_movie_window)
		self.search_movie.get_searches()
		self.show_search_results(self.search_movie)
	else:
		gutils.error(self.w_results, \
			_("You should fill the original title\nor the movie title."))

def source_changed(self):
	option = gutils.on_combo_box_entry_changed_name(self.am_source)
	self.active_plugin = option
	plugin_name = 'PluginMovie' + option
	plugin = __import__(plugin_name)
	self.am_plugin_desc.set_text(plugin.plugin_name+"\n" \
		+plugin.plugin_description+"\n"+_("Url: ") \
		+plugin.plugin_url+"\n"+_("Language: ")+plugin.plugin_language)
	image = os.path.join(self.locations['images'], plugin_name + ".png")
	# if movie plugin logo exists lets use it
	if os.path.exists(image):
		handler = self.am_plugin_image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image))

def clone_movie(self):
	treeselection = self.main_treeview.get_selection()
	(tmp_model, tmp_iter) = treeselection.get_selected()
	number = tmp_model.get_value(tmp_iter, 1)
	movie = self.db.Movie.get_by(number=number)

	if movie == None:
		return false

	next_number = gutils.find_next_available(self)
	new_image = str(movie.image) + '_' + str(next_number)
	
	# integer problem workaround
	if int(movie.seen)==1:
		seen = True
	else:
		seen = False
	t_movies = {
		'actors'         : movie.actors,
		'classification' : movie.classification,
		'color'          : movie.color,
		'cond'           : movie.cond,
		'country'        : movie.country,
		'director'       : movie.director,
		'genre'          : movie.genre,
		'image'          : new_image,
		'site'           : movie.site,
		'layers'         : movie.layers,
		'medium_id'      : movie.medium_id,
		'number'         : next_number,
		'media_num'      : movie.media_num,
		'notes'          : movie.notes,
		'o_title'        : movie.o_title,
		'plot'           : movie.plot,
		'rating'         : movie.rating,
		'region'         : movie.region,
		'runtime'        : movie.runtime,
		'seen'           : seen,
		'o_site'         : movie.o_site,
		'studio'         : movie.studio,
		'title'          : movie.title,
		'trailer'        : movie.trailer,
		'year'           : movie.year
	}
	# tags
	t_tags = {}
	for tag in movie.tags:
		t_tags[tag.tag_id] = 1
	# languages
	t_languages = {}
	for lang in movie.languages:
		if not t_languages.has_key(lang.lang_id):
			t_languages[lang.lang_id] = {}
		t_languages[lang.lang_id][lang.type] = True

	self.db.add_movie(t_movies, t_languages, t_tags)

	# WARNING: loan problems (don't copy volume/collection data until resolved)

	tmp_dest = os.path.join(self.griffith_dir, "posters")
	if movie.image != None:
		image_path = os.path.join(tmp_dest, str(movie.image)+".jpg")
		clone_path = os.path.join(tmp_dest, new_image+".jpg")
		# clone image
		shutil.copyfile(image_path, clone_path)
		image_path = clone_path
	else:
		if self.windows:
			image_path = "images/default.png"
		else:
			image_path = os.path.join(self.locations['images'], "default.png")
	handler = self.Image.set_from_file(image_path)

	#update statusbar
	self.total = self.total + 1
	self.total_filter = self.total
	self.count_statusbar()
	self.populate_treeview(self.db.Movie.select())
	self.main_treeview.set_cursor(next_number-1)
	self.treeview_clicked()

