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
import update
import gtk

def change_poster(self):
	"""
	changes movie poster image to a custom one 
	showing a file chooser dialog to select it
	"""
	import shutil
	picture = self.e_picture
	m_id = self.get_maintree_selection()
	filename = gutils.file_chooser(_("Select image"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK), name="", folder=self.locations['desktop'], picture=True)
	if filename[0]:
		try:
			picture.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename[0]).scale_simple(100, 140, gtk.gdk.INTERP_BILINEAR))
			file_to_copy = os.path.basename(filename[0])
			shutil.copyfile(filename[0],'%s/posters/t_%s.jpg' % (self.griffith_dir,  os.path.splitext(file_to_copy)[0]))
			update.update_image(self, os.path.splitext(file_to_copy)[0], m_id[0])
			update_tree_thumbnail(self, '%s/posters/t_%s.jpg' % (self.griffith_dir,  os.path.splitext(file_to_copy)[0]))
		except:
			gutils.error(self, _("Image not valid."), self.main_window)
			
def delete_poster(self):
	response = gutils.question(self, _("Are you sure you want to delete this poster?"), 1, self.main_window)
	if response==-8:
		image_path = self.locations['images'] + "/default.png"
		self.e_picture.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image_path))
		update_tree_thumbnail(self, self.locations['images'] + "/default_thumbnail.png")
		m_id = self.get_maintree_selection()
		update.clear_image(self, m_id[0])
		self.delete_poster.set_sensitive(False)
		self.zoom_poster.set_sensitive(False)
	else:
		pass
		
def update_tree_thumbnail(self, t_image_path):
	treeselection = self.main_treeview.get_selection()
	(tmp_model, tmp_iter) = treeselection.get_selected()
	self.Image.set_from_file(t_image_path)
	pixbuf = self.Image.get_pixbuf()
	pixbuf = pixbuf.scale_simple(30, 40, 'bilinear')
	self.treemodel.set_value(tmp_iter, 2, pixbuf)
	
def change_rating_from_slider(self):
	rating = int(self.rating_slider.get_value())
	self.image_rating.show()
	try:
		rimage = int(str(self.config.get('rating_image')))
	except:
		rimage = 0
	if rimage:
		prefix = ""
	else:
		prefix = "meter"
		
	rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, rating)
	self.image_rating.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(rating_file))
	self.db.cursor.execute(
			"UPDATE movies SET rating = '" 
			+str(int(self.rating_slider.get_value()))+"' WHERE number = '" + self.e_number.get_text() +"'")
	
def toggle_seen(self):
	seen = '0'
	if self.e_seen.get_active():
		seen = '1'
	self.db.cursor.execute(
			"UPDATE movies SET seen = '" 
			+seen+"' WHERE number = '" + self.e_number.get_text() +"'")
	self.count_statusbar()
			
def clear_details(self):
	plot_buffer = self.e_plot.get_buffer()
	obs_buffer = self.e_obs.get_buffer()
	with_buffer = self.e_with.get_buffer()
	self.e_number.set_text("")
	self.e_original_title.set_text("")
	self.e_title.set_text("")
	self.e_director.set_text("")
	plot_buffer.set_text("")
	self.e_year.set_text("")
	self.e_runtime.set_text("")
	with_buffer.set_text("")
	self.e_country.set_text("")
	self.e_genre.set_text("")
	self.e_classification.set_text("")
	self.e_studio.set_text("")
	self.e_site.set_text("")
	obs_buffer.set_text("")
	self.e_imdb.set_text("")
	self.e_trailer.set_text("")
	self.e_discs.set_text("1")
	self.e_color.set_active(0)
	self.e_condition.set_active(0)
	self.e_layers.set_active(0)
	self.e_region.set_active(0)
	self.e_media.set_active(0)
	self.e_volume_combo.set_active(0)
	self.e_collection_combo.set_active(0)
	#self.e_picture.clear()
	self.e_picture.hide()
	self.e_picture.show()
	self.rating_slider.set_value(0)
	try:
		rimage = int(str(self.config.get('rating_image')))
	except:
		rimage = 0
	if rimage:
		prefix = ""
	else:
		prefix = "meter"
	image = self.locations['images'] + "/%s00.png"%prefix
	self.image_rating.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image))

def fill_volumes_combo(self, prefix='e', default=0):
	for tmp in 'e', "am":
		eval("self.%s_volume_combo.get_model().clear()"%tmp)
		for volume in self.db.get_all_volumes_data():
			eval("self.%s_volume_combo.insert_text(int(volume['id']), volume['name'])"%tmp)
		eval("self.%s_volume_combo.show_all()"%tmp)
	if prefix == 'e':
		self.e_volume_combo.set_active(int(default))
		self.am_volume_combo.set_active(0)
	else:
		self.am_volume_combo.set_active(int(default))

def fill_collections_combo(self, prefix='e', default=0):
	for tmp in 'e', "am":
		eval("self.%s_collection_combo.get_model().clear()"%tmp)
		for collection in self.db.get_all_collections_data():
			eval("self.%s_collection_combo.insert_text(int(collection['id']), collection['name'])"%tmp)
		eval("self.%s_collection_combo.show_all()"%tmp)
	if prefix == 'e':
		self.e_collection_combo.set_active(int(default))
		self.am_collection_combo.set_active(0)
	else:
		self.am_collection_combo.set_active(int(default))

