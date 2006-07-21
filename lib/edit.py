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
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import gutils
import os
import update
import gtk
import amazon
from urllib import urlcleanup
import tempfile
import movie
import delete
import widgets
from PIL import Image

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
			shutil.copyfile(filename[0],'%s/posters/%s.jpg' % (self.griffith_dir,  os.path.splitext(file_to_copy)[0]))
			gutils.make_thumbnail(self, '%s.jpg' % os.path.splitext(file_to_copy)[0])
			gutils.make_medium_image(self, '%s.jpg' % os.path.splitext(file_to_copy)[0])
			update.update_image(self, os.path.splitext(file_to_copy)[0], m_id[0])
			update_tree_thumbnail(self, '%s/posters/t_%s.jpg' % (self.griffith_dir,  os.path.splitext(file_to_copy)[0]))
		except:
			gutils.error(self, _("Image not valid."), self.main_window)

def delete_poster(self):
	m_id, m_iter = self.get_maintree_selection()
	poster = self.db.get_value(field="image", table="movies", where="number='%s'"%m_id)
	response = gutils.question(self, _("Are you sure you want to delete this poster?"), 1, self.main_window)
	if response==-8:
		image_path = self.locations['images'] + "/default.png"
		handler = self.e_picture.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image_path))
		gutils.garbage(handler)
		update_tree_thumbnail(self, self.locations['images'] + "/default_thumbnail.png")
		m_id = self.get_maintree_selection()
		update.clear_image(self, m_id[0])
		self.delete_poster.set_sensitive(False)
		self.zoom_poster.set_sensitive(False)
		delete.delete_poster(self, poster)
	else:
		pass

def update_tree_thumbnail(self, t_image_path):
	treeselection = self.main_treeview.get_selection()
	(tmp_model, tmp_iter) = treeselection.get_selected()
	self.Image.set_from_file(t_image_path)
	pixbuf = self.Image.get_pixbuf()
	self.treemodel.set_value(tmp_iter, 2, pixbuf)
	gutils.garbage(pixbuf)

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
	handler = self.image_rating.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(rating_file))
	gutils.garbage(handler)

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
	self.rating_slider.set_value(0)
	# languages - remove old widgets
	for i in self.e_lang_vbox.get_children():
		i.destroy()
	# tags - clear tag selection
	for i in self.e_tag_vbox.get_children():
		i.set_active(False)

	try:
		rimage = int(str(self.config.get('rating_image')))
	except:
		rimage = 0
	if rimage:
		prefix = ""
	else:
		prefix = "meter"
	image = self.locations['images'] + "/%s00.png"%prefix
	handler = self.image_rating.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image))
	gutils.garbage(handler)

def fetch_bigger_poster(self):
	match = 0
	self.debug.show("fetching poster from amazon")
	movie = self.db.Movie.get_by(movie_id=self.e_movie_id.get_text())
	current_poster = movie.image
	amazon.setLicense("04GDDMMXX8X9CJ1B22G2")

	try:
		result = amazon.searchByKeyword(self.e_original_title.get_text(), \
						type="lite", product_line="dvd")
		self.debug.show("Posters found on amazon: %s posters" % len(result))
	except:
		gutils.warning(self, _("No posters found for this movie."))
		return

	widgets.connect_poster_signals(self, get_poster_select_dc, result, current_poster)

	if not len(result):
		gutils.warning(self, _("No posters found for this movie."))
		return

	for f in range(len(result)):
		if self.e_original_title.get_text() == result[f].ProductName:
			get_poster(self, f, result, current_poster)
			return

	self.treemodel_results.clear()

	for f in range(len(result)):

		if (len(result[f].ImageUrlLarge)):
			title = result[f].ProductName
			self.debug.show(title)
			myiter = self.treemodel_results.insert_before(None, None)
			self.treemodel_results.set_value(myiter, 0, str(f))
			self.treemodel_results.set_value(myiter, 1, title)

	self.w_results.show()
	self.w_results.set_keep_above(True)

def get_poster_select_dc(self, event, mself, result, current_poster):
	if event.type == gtk.gdk._2BUTTON_PRESS:
		get_poster(mself, None, result, current_poster)

def get_poster_select(self, mself, result, current_poster):
	get_poster(mself, None, result, current_poster)

def get_poster(self, f, result, current_poster):
	if f == None:
		treeselection = self.results_treeview.get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		f = int(tmp_model.get_value(tmp_iter, 0))
		self.w_results.hide()

	file_to_copy = tempfile.mktemp(suffix=self.e_number.get_text(), prefix='poster_', \
		dir=os.path.join(self.griffith_dir, "posters"))
	file_to_copy += ".jpg"
	try:
		progress = movie.Progress(self.main_window,_("Fetching poster"),_("Wait a moment"))
		retriever = movie.Retriever(result[f].ImageUrlLarge, self.main_window, progress, file_to_copy)
		retriever.start()
		while retriever.isAlive():
			progress.pulse()
			if progress.status:
				retriever.suspend()
			while gtk.events_pending():
				gtk.main_iteration()
		progress.close()
		urlcleanup()
	except:
		gutils.warning(self, _("Sorry. A connection error was occurred."))

	self.debug.show(file_to_copy)

	if  os.path.isfile(file_to_copy):
		handler = self.big_poster.set_from_file(file_to_copy)
		gutils.garbage(handler)

		try:
			im = Image.open(file_to_copy)
		except IOError:
			self.debug.show("failed to identify %s"%file_to_copy)
		else:
			if im.format == "GIF":
				gutils.warning(self, _("Sorry. This poster image format is not supported."))
				os.remove(file_to_copy)
				return
		self.poster_window.show()
		self.poster_window.move(0,0)
		response = gutils.question(self, \
				_("Do you want to use this poster instead?"), \
				1, self.main_window)
		if response == -8:
			self.debug.show("Using new fetched poster, updating and removing old one from disk.")
			update.update_image(self, os.path.basename(file_to_copy), self.e_number.get_text())
			gutils.make_thumbnail(self, '%s' % os.path.basename(file_to_copy))
			gutils.make_medium_image(self, '%s' % os.path.basename(file_to_copy))
			update_tree_thumbnail(self, '%s/posters/t_%s' % (self.griffith_dir, \
				os.path.basename(file_to_copy)))
			self.e_picture.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(os.path.join(self.griffith_dir, "posters/m_%s"%os.path.basename(file_to_copy))))
			delete.delete_poster(self, current_poster)

		else:
			self.debug.show("Reverting to previous poster and deleting new one from disk.")
			try:
                            os.remove(file_to_copy)
                        except:
                            self.debug.show("no permission for %s"%file_to_copy)

		self.poster_window.hide()
	else:
		gutils.warning(self, _("Sorry. This movie is listed but have no poster available at Amazon.com."))

