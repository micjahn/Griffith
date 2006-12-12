# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes, Piotr Ożarowski

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
from PIL import Image

def change_poster(self):
	"""
	changes movie poster image to a custom one
	showing a file chooser dialog to select it
	"""
	import shutil
	picture = self.widgets['movie']['picture']
	number = self.get_maintree_selection()[0]
	filename = gutils.file_chooser(_("Select image"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK), name="", folder=self.locations['desktop'], picture=True)
	if filename and filename[0]:
		try:
			picture.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename[0]).scale_simple(100, 140, gtk.gdk.INTERP_BILINEAR))
			file_to_copy = os.path.basename(filename[0])
			shutil.copyfile(filename[0], os.path.join(self.locations['posters'], '%s.jpg' % os.path.splitext(file_to_copy)[0]))
			gutils.make_thumbnail(self, '%s.jpg' % os.path.splitext(file_to_copy)[0])
			gutils.make_medium_image(self, '%s.jpg' % os.path.splitext(file_to_copy)[0])
			update.update_image(self, os.path.splitext(file_to_copy)[0], number)
			update_tree_thumbnail(self, os.path.join(self.locations['posters'], 't_%s.jpg' % os.path.splitext(file_to_copy)[0]))
		except:
			gutils.error(self, _("Image not valid."), self.widgets['window'])

def delete_poster(self):
	movie = self.db.Movie.get_by(movie_id=self._movie_id)
	if not movie:
		self.debug.show("Can't delete unknown movie's poster!")
		return False
	response = gutils.question(self, _("Are you sure you want to delete this poster?"), 1, self.widgets['window'])
	if response==-8:
		image_path = self.locations['images'] + "/default.png"
		handler = self.widgets['movie']['picture'].set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image_path))
		gutils.garbage(handler)
		update_tree_thumbnail(self, os.path.join(self.locations['images'], 'default_thumbnail.png'))
		# update in database
		old_image = movie.image
		movie.image = None
		movie.update()
		movie.flush()
		self.update_statusbar(_("Image has been updated"))

		self.widgets['add']['delete_poster'].set_sensitive(False)
		self.widgets['menu']['delete_poster'].set_sensitive(False)
		self.widgets['movie']['picture_button'].set_sensitive(False)
		if old_image:
			delete.delete_poster(self, old_image)
	else:
		pass

def update_tree_thumbnail(self, t_image_path):
	treeselection = self.widgets['treeview'].get_selection()
	(tmp_model, tmp_iter) = treeselection.get_selected()
	self.Image.set_from_file(t_image_path)
	pixbuf = self.Image.get_pixbuf()
	self.treemodel.set_value(tmp_iter, 1, pixbuf)
	gutils.garbage(pixbuf)

def fetch_bigger_poster(self):
	match = 0
	self.debug.show("fetching poster from amazon")
	movie = self.db.Movie.get_by(movie_id=self._movie_id)
	current_poster = movie.image
	amazon.setLicense("04GDDMMXX8X9CJ1B22G2")

	locale = self.config.get('amazon_locale', 0)
	if locale == 1:
		locale = 'uk'
	elif locale == 2:
		locale = 'de'
	elif locale == 3:
		locale = 'uk'
	else:
		locale = None

	try:
		result = amazon.searchByKeyword(self.widgets['movie']['o_title'].get_text(), \
						type="lite", product_line="dvd", locale=locale)
		self.debug.show("Posters found on amazon: %s posters" % len(result))
	except:
		gutils.warning(self, _("No posters found for this movie."))
		return

	from widgets import connect_poster_signals
	connect_poster_signals(self, get_poster_select_dc, result, current_poster)

	if not len(result):
		gutils.warning(self, _("No posters found for this movie."))
		return

	for f in range(len(result)):
		if self.widgets['movie']['o_title'].get_text() == result[f].ProductName:
			get_poster(self, f, result, current_poster)
			return

	self.treemodel_results.clear()

	for f in range(len(result)):

		if (len(result[f].ImageUrlLarge)):
			title = result[f].ProductName
			myiter = self.treemodel_results.insert_before(None, None)
			self.treemodel_results.set_value(myiter, 0, str(f))
			self.treemodel_results.set_value(myiter, 1, title)

	self.widgets['results']['window'].show()
	self.widgets['results']['window'].set_keep_above(True)

def get_poster_select_dc(self, event, mself, result, current_poster):
	if event.type == gtk.gdk._2BUTTON_PRESS:
		get_poster(mself, None, result, current_poster)

def get_poster_select(self, mself, result, current_poster):
	get_poster(mself, None, result, current_poster)

def get_poster(self, f, result, current_poster):
	if f is None:
		treeselection = self.widgets['results']['treeview'].get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		f = int(tmp_model.get_value(tmp_iter, 0))
		self.widgets['results']['window'].hide()

	file_to_copy = tempfile.mktemp(suffix=self.widgets['movie']['number'].get_text(), \
		dir=self.locations['posters'])
	file_to_copy += ".jpg"
	try:
		progress = movie.Progress(self.widgets['window'],_("Fetching poster"),_("Wait a moment"))
		retriever = movie.Retriever(result[f].ImageUrlLarge, self.widgets['window'], progress, file_to_copy)
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

	if  os.path.isfile(file_to_copy):
		handler = self.widgets['big_poster'].set_from_file(file_to_copy)
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
		self.widgets['poster_window'].show()
		self.widgets['poster_window'].move(0,0)
		response = gutils.question(self, \
				_("Do you want to use this poster instead?"), \
				1, self.widgets['window'])
		if response == -8:
			self.debug.show("Using new fetched poster, updating and removing old one from disk.")
			update.update_image(self, os.path.basename(file_to_copy), self.widgets['movie']['number'].get_text())
			gutils.make_thumbnail(self, '%s' % os.path.basename(file_to_copy))
			gutils.make_medium_image(self, '%s' % os.path.basename(file_to_copy))
			update_tree_thumbnail(self, os.path.join(self.locations['posters'], 't_%s' % os.path.basename(file_to_copy)))
			self.widgets['movie']['picture'].set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(os.path.join(self.locations['posters'], "m_%s" % os.path.basename(file_to_copy))))
			delete.delete_poster(self, current_poster)
			self.widgets['add']['delete_poster'].set_sensitive(True)
			self.widgets['menu']['delete_poster'].set_sensitive(True)

		else:
			self.debug.show("Reverting to previous poster and deleting new one from disk.")
			try:
                            os.remove(file_to_copy)
                        except:
                            self.debug.show("no permission for %s"%file_to_copy)

		self.widgets['poster_window'].hide()
	else:
		gutils.warning(self, _("Sorry. This movie is listed but have no poster available at Amazon.com."))

