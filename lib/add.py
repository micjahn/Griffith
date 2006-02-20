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
import gtk
import string
import shutil
import quick_filter
import widgets

def add_movie(self):
	quick_filter.clear_filter(self)
	next_number = gutils.find_next_available(self)
	initialize_add_dialog(self)
	self.am_number.set_text(str(next_number))
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
	for i in self.am_sub_vbox.get_children():
		i.destroy()
	self.am_languages = []
	self.am_subtitles = []
	# tags - clear tag selection
	for i in self.am_tag_vbox.get_children():
		i.set_active(False)

	handler = self.Image.set_from_file(image)
	gutils.garbage(handler)
	handler = self.am_picture.set_from_pixbuf(self.Image.get_pixbuf())
	gutils.garbage(handler)
	self.am_original_title.grab_focus()
	widgets.connect_add_signals(self)

def add_movie_db(self, close):
	if  len(self.am_original_title.get_text()) or len(self.am_title.get_text()):
		self.db.add_movie(self)
		if int(self.am_number.get_text()) >= 2:
			insert_after = self.treemodel.get_iter(int(self.am_number.get_text())-2)
		else:
			insert_after = None
		myiter = self.treemodel.insert_after(None, insert_after)
		tmp_dest = os.path.join(self.griffith_dir, "posters")
		if len(self.am_picture_name.get_text()):
			image_path = os.path.join(tmp_dest, \
				str(self.am_picture_name.get_text())+".jpg")
		else:
			image_path = os.path.join(self.locations['images'], "default.png")
		handler = self.Image.set_from_file(image_path)
		gutils.garbage(handler)
		pixbuf = self.Image.get_pixbuf()
		self.treemodel.set_value(myiter, 1, \
			'%004d' % int(self.am_number.get_text()))
		self.treemodel.set_value(myiter, 2, pixbuf.scale_simple(30,40,3))
		self.treemodel.set_value(myiter, \
			3, str(self.am_original_title.get_text()))
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
		gutils.garbage(pixbuf)
		if close:
			self.hide_add_movie()
	else:
		gutils.error(self.w_results, \
			_("You should fill the original title\nor the movie title."))
	
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
	gutils.garbage(handler)
			
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
	#self.am_with.set_text(gutils.convert_entities(self.movie.with))
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
	tmp_dest = os.path.join(self.griffith_dir, "posters")
	if self.movie.picture != "":
		image = os.path.join(tmp_dest, self.movie.picture)
		try:
			handler = self.Image.set_from_file(image)
			gutils.garbage(handler)
			pixbuf = self.Image.get_pixbuf()
			self.am_picture.set_from_pixbuf(pixbuf.scale_simple(100, 140, 3))
			self.am_picture_name.set_text(string.replace(self.movie.picture, ".jpg",""))
		except:
			image = os.path.join(self.locations['images'], "default.png")
			handler = self.Image.set_from_file(image)
			gutils.garbage(handler)
			self.am_picture.set_from_pixbuf(self.Image.get_pixbuf())
	else:
		image = os.path.join(self.locations['images'], "default.png")
		handler = self.Image.set_from_file(image)
		gutils.garbage(handler)
		Pixbuf = self.Image.get_pixbuf()
		self.am_picture.set_from_pixbuf(Pixbuf)
		gutils.garbage(Pixbuf)
		
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
		gutils.garbage(handler)
		
def clone_movie(self):
	treeselection = self.main_treeview.get_selection()
	(tmp_model, tmp_iter) = treeselection.get_selected()	
	m_id = tmp_model.get_value(tmp_iter, 1)
	data = self.db.select_movie_by_num(m_id)
	next_number = gutils.find_next_available(self)
	for row in data:
		self.db.cursor.execute(
			"INSERT INTO 'movies'('id','original_title','title','director', 'plot', 'image', 'year', 'runtime','actors','country','genre','media','classification','studio','site', 'color','region','layers','condition','imdb','trailer','obs','num_media','rating','loaned','seen','number') VALUES (Null,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','0','%s','%s')"% \
			(gutils.gescape(str(row['original_title'])), \
			gutils.gescape(str(row['title'])), \
			gutils.gescape(str(row['director'])), \
			gutils.gescape(str(row['plot'])), \
			gutils.gescape(str(row['image'])), \
			gutils.gescape(str(row['year'])), \
			gutils.gescape(str(row['runtime'])), \
			gutils.gescape(str(row['actors'])), \
			gutils.gescape(str(row['country'])), \
			gutils.gescape(str(row['genre'])), \
			gutils.gescape(str(row['media'])), \
			gutils.gescape(str(row['classification'])), \
			gutils.gescape(str(row['studio'])), \
			gutils.gescape(str(row['site'])), \
			gutils.gescape(str(row['color'])), \
			gutils.gescape(str(row['region'])), \
			gutils.gescape(str(row['layers'])), \
			gutils.gescape(str(row['condition'])), \
			gutils.gescape(str(row['imdb'])), \
			gutils.gescape(str(row['trailer'])), \
			gutils.gescape(str(row['obs'])), \
			str(row['num_media']), \
			str(row['rating']), \
			str(row['seen']), \
			str(next_number) \
			))

		myiter = self.treemodel.insert_after(None, self.treemodel.get_iter(next_number-2))
		tmp_dest = os.path.join(self.griffith_dir, "posters")
		if str(str(row['image'])) != '':
			image_path = os.path.join(tmp_dest, str(row['image'])+".jpg")
			clone_path = os.path.join(tmp_dest, str(next_number)+".jpg")
			# clone image
			shutil.copyfile(image_path, clone_path)
			image_path = clone_path
		else:
			if os.name == 'nt':
				image_path = "images/default.png"
			else:
				image_path = os.path.join(self.locations['images'], "default.png")
		handler = self.Image.set_from_file(image_path)
		gutils.garbage(handler)
		self.treemodel.set_value(myiter, 1, '%004d' % int(next_number))
		pixbuf = self.Image.get_pixbuf() 
		pixbuf = pixbuf.scale_simple(30, 40, 'bilinear')
		self.treemodel.set_value(myiter, 2, pixbuf)
		self.treemodel.set_value(myiter, 3, str(row['original_title']))
		self.treemodel.set_value(myiter, 4, str(row['title']))
		self.treemodel.set_value(myiter, 5, str(row['director']))
		gutils.garbage(pixbuf)
		
	#update statusbar
	self.total = self.total + 1
	self.total_filter = self.total
	self.clear_details()
	self.main_treeview.set_cursor(next_number-1)
	self.treeview_clicked()
	self.count_statusbar()
