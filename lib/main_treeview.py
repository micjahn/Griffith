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
import gtk

def treeview_clicked(self):
	if self.initialized is False:
		return False
	if self.total:
		treeselection = self.main_treeview.get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		number = tmp_model.get_value(tmp_iter,0)
		movie = self.db.Movie.get_by(number=number)
		if movie == None:
			self.debug.show("Treeview: movie doesn't exists (number=%s)"%number)
		set_details(self, movie)

def set_details(self, item=None):
	if item==None:
		item = {}
	if item.has_key('movie_id') and item['movie_id']:
		self._movie_id = item['movie_id']
	else:
		self._movie_id = None

	plot_buffer = self.plot.get_buffer()
	notes_buffer = self.notes.get_buffer()
	cast_buffer = self.cast.get_buffer()
	cast_iter = cast_buffer.get_start_iter()

	if item.has_key('number') and item['number']:
		self.number.set_text(str(int(item['number'])))
	else:
		self.number.set_text('')
	if item.has_key('title') and item['title']:
		self.title.set_markup("<b><span size='large'>%s</span></b>" % str(item['title']))
	else:
		self.title.set_text('')
	if item.has_key('o_title') and item['o_title']:
		self.o_title.set_markup("<span size='medium'><i>%s</i></span>" % str(item['o_title']))
	else:
		self.o_title.set_text('')
	if item.has_key('director') and item['director']:
		self.director.set_markup("<i>%s</i>" % str(item['director']))
	else:
		self.director.set_text('')
	if item.has_key('plot') and item['plot']:
		plot_buffer.set_text(str(item['plot']))
	else:
		plot_buffer.set_text('')
	if item.has_key('year') and item['year']:
		self.year.set_text(str(item['year']))
	else:
		self.year.set_text('')
	if item.has_key('runtime') and item['runtime']:
		self.runtime.set_text(str(int(item['runtime'])))
	else:
		self.runtime.set_text('x')
	if item.has_key('cast') and item['cast']:
		cast_buffer.set_text(str(item['cast']))
	else:
		cast_buffer.set_text('')
	if item.has_key('country') and item['country']:
		self.country.set_markup("<i>%s</i>" % str(item['country']))
	else:
		self.country.set_text('')
	if item.has_key('genre') and item['genre']:
		self.genre.set_markup("<i>%s</i>" % str(item['genre']))
	else:
		self.genre.set_text('')
	if item.has_key('cond') and item['cond']:
		self.condition.set_markup("<i>%s</i>" % self._conditions[item['cond']])
	else:
		self.condition.set_markup("<i>%s</i>" % self._conditions[5]) # 5 == N/A
	if item.has_key('region') and item['region']:
		self.region.set_markup("<i>%s</i>" % str(item['region']))
		self.tooltips.set_tip(self.region, self._regions[item['region']])
	else:
		self.region.set_text('')
		self.tooltips.set_tip(self.region, self._regions[9]) # N/A
	if item.has_key('layers') and item['layers']:
		self.layers.set_markup("<i>%s</i>" % self._layers[item['layers']])
	else:
		self.layers.set_markup("<i>%s</i>" % self._layers[4]) # N/A
	if item.has_key('color') and item['color']:
		self.color.set_markup("<i>%s</i>" % self._colors[item['color']])
	else:
		self.color.set_markup("<i>%s</i>" % self._colors[3]) # N/A
	if item.has_key('classification') and item['classification']:
		self.classification.set_markup("<i>%s</i>" % str(item['classification']))
	else:
		self.classification.set_text('')
	if item.has_key('studio') and item['studio']:
		self.studio.set_markup("<i>%s</i>" % str(item['studio']))
	else:
		self.studio.set_text('')
	if item.has_key('o_site') and item['o_site']:
		self._o_site_url = str(item['o_site'])
		self.go_o_site_button.set_sensitive(True)
	else:
		self._o_site_url = None
		self.go_o_site_button.set_sensitive(False)
	if item.has_key('site') and item['site']:
		self._site_url = str(item['site'])
		self.go_site_button.set_sensitive(True)
	else:
		self._site_url = None
		self.go_site_button.set_sensitive(False)
	if item.has_key('trailer') and item['trailer']:
		self._trailer_url = str(item.trailer)
		self.go_trailer_button.set_sensitive(True)
	else:
		self._trailer_url = None
		self.go_trailer_button.set_sensitive(False)
	if item.has_key('seen') and item['seen'] == True:
		self.seen_icon.set_from_stock('gtk-yes', 2)
	else:
		self.seen_icon.set_from_stock('gtk-no', 2)
	if item.has_key('notes') and item['notes']:
		notes_buffer.set_text(str(item.notes))
	else:
		notes_buffer.set_text('')
	tmp = ''
	if item.has_key('media_num') and item['media_num']:
		tmp = str(item.media_num)
	else:
		tmp = '0'
	if item.has_key('medium_id') and item['medium_id']:
		try:
			tmp += ' x ' + item['medium'].name
		except:
			pass
	self.medium.set_markup("<i>%s</i>" % tmp)
	if item.has_key('vcodec_id'):
		try:
			self.vcodec.set_markup("<i>%s</i>" % str(item['vcodec'].name))
		except:
			self.vcodec.set_text('')
	else:
		self.vcodec.set_text('')

	# poster
	if item.has_key('image') and item['image']:
		tmp_dest = os.path.join(self.griffith_dir, 'posters')
		tmp_img = os.path.join(tmp_dest, "m_%s.jpg"%item['image'])
		tmp_img2 = os.path.join(tmp_dest, "%s.jpg"%item['image'])
		if os.path.isfile(tmp_img2):
			image_path = tmp_img
			self.delete_poster.set_sensitive(True)
			self.t_delete_poster.set_sensitive(True)
			self.picture_button.set_sensitive(True)
		else:
			image_path = os.path.join(self.locations['images'], 'default.png')
			self.delete_poster.set_sensitive(False)
			self.t_delete_poster.set_sensitive(False)
			self.picture_button.set_sensitive(False)
		# lets see if we have a scaled down medium image already created
		if os.path.isfile(image_path):
			pass
		else:
			# if not, lets make one for future use :D
			original_image = os.path.join(tmp_dest, "%s.jpg"%item.image)
			if os.path.isfile(original_image):
				gutils.make_medium_image(self, "%s.jpg"%item.image)
			else:
				self.Image.set_from_file(os.path.join(self.locations['images'], "default.png"))
				pixbuf = self.Image.get_pixbuf()
		handler = self.picture.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image_path))
	# ratig
	try:
		rimage = int(str(self.config.get('rating_image')))
	except:
		rimage = 0
	if rimage:
		prefix = ''
	else:
		prefix = 'meter'
	if item.has_key('rating') and item['rating']:
		rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, item['rating'])
	else:
		rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, 0)
	handler = self.image_rating.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(rating_file))
	gutils.garbage(handler)

	# check loan status and adjust buttons and history box
	if item.has_key('loaned') and item['loaned'] == True:
		self.popup_loan.set_sensitive(False)
		self.popup_email.set_sensitive(True)
		self.popup_return.set_sensitive(True)
		self.loan_button.set_sensitive(False)
		self.b_email_reminder.set_sensitive(True)
		self.return_button.set_sensitive(True)
		
		data_loan = self.db.get_loan_info(collection_id=item['collection_id'], volume_id=item['volume_id'], movie_id=item['movie_id'])
		data_person = self.db.Person.get_by(person_id=data_loan.person.person_id)
		self.person_name = str(data_person.name)
		self.person_email = str(data_person.email)
		self.loan_date = str(data_loan.date)
		self.loan_info.set_label(self._("This movie has been loaned to ") + self.person_name + self._(" on ") + self.loan_date[:10])
		self.loaned_icon.set_from_stock('gtk-no', 2) # "is movie available?"
	else:
		self.popup_loan.set_sensitive(True)
		self.popup_email.set_sensitive(False)
		self.popup_return.set_sensitive(False)
		self.return_button.set_sensitive(False)
		self.b_email_reminder.set_sensitive(False)
		self.loan_button.set_sensitive(True)
		self.loan_info.set_markup("<b>%s</b>" % self._("Movie not loaned"))
		self.loaned_icon.set_from_stock('gtk-yes', 2) # "is movie available?"

	# loan history	
	self.loans_treemodel.clear()
	if item.has_key('collection_id') or item.has_key('volume_id') or item.has_key('movie_id'):
		loans = self.db.get_loan_history(collection_id=item['collection_id'], volume_id=item['volume_id'], movie_id=item['movie_id'])
		for loan in loans:
			myiter = self.loans_treemodel.append(None)
			self.loans_treemodel.set_value(myiter, 0,'%s' % str(loan.date)[:10])
			if loan.return_date and  loan.return_date != '':
				self.loans_treemodel.set_value(myiter, 1, str(loan.return_date)[:10])
			else:
				self.loans_treemodel.set_value(myiter, 1, "---")
			person = self.db.Person.get_by(person_id=loan.person.person_id)
			self.loans_treemodel.set_value(myiter, 2, person.name)

	# volumes/collections
	if item.has_key('volume_id') and item['volume_id']>0:
		if item.has_key('volume') and item['volume']:
			self.volume.set_markup("<b>%s</b>" % item['volume'].name)
			self.show_volume_button.set_sensitive(True)
		else:
			self.volume.set_text('')
			self.show_volume_button.set_sensitive(False)
	else:
			self.volume.set_text('')
			self.show_volume_button.set_sensitive(False)
	if item.has_key('collection_id') and item['collection_id']>0:
		if item.has_key('collection') and item['collection']:
			self.collection.set_markup("<b>%s</b>" % item['collection'].name)
			self.show_collection_button.set_sensitive(True)
		else:
			self.collection.set_text('')
			self.show_collection_button.set_sensitive(False)
	else:
		self.collection.set_text('')
		self.show_collection_button.set_sensitive(False)

	# languages
	for i in self.audio_vbox.get_children():
		i.destroy()
	for i in self.subtitle_vbox.get_children():
		i.destroy()
	if item.has_key('languages') and len(item['languages'])>0:
		for i in item['languages']:
			if i.type == 3: # subtitles
				if i.subformat:
					tmp = "%s - %s" % (i.language.name, i.subformat.name)
				else:
					tmp = "%s" % i.language.name
				self.subtitle_vbox.pack_start(gtk.Label(tmp))
			else:
				language = i.language.name
				if i.type is not None:
					language += " <i>%s</i>" % self._lang_types[i.type]
				tmp = ''
				if i.achannel:
					tmp = i.achannel.name
				if i.acodec:
					if len(tmp)>0:
						tmp += ", %s" % i.acodec.name
					else:
						tmp = i.acodec.name
				if len(tmp)>0:
					tmp = "%s (%s)" % (language, tmp)
				else:
					tmp = language
				widget = gtk.Label(tmp)
				widget.set_use_markup(True)
				self.audio_vbox.pack_start(widget)
	self.audio_vbox.show_all()
	self.subtitle_vbox.show_all()
	#tags
	if item.has_key('tags'):
		tmp = ''
		for tag in item['tags']:
			tmp += "%s, " % tag.name
		tmp = tmp[:-2] # cut last comma
		self.tags.set_text(tmp)

def populate(self, movies):
	self.treemodel.clear()
	for movie in movies:
		myiter = self.treemodel.append(None)
		self.treemodel.set_value(myiter,0,'%004d' % int(movie.number))

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
				original_image = os.path.join(tmp_dest, "%s.jpg"%movie.image)
				if os.path.isfile(original_image):
					gutils.make_thumbnail(self, "%s.jpg"%movie.image)
				else:
					self.Image.set_from_file("%s/default_thumbnail.png"%self.locations['images'])
					pixbuf = self.Image.get_pixbuf()
			self.Image.set_from_file(image_path)
			pixbuf = self.Image.get_pixbuf()
			self.treemodel.set_value(myiter, 1, pixbuf)

		else:
			# let's hide image column from main treeview since we don't want it to be visible
			self.image_column.set_visible(False)
		self.treemodel.set_value(myiter,2,movie.o_title)
		self.treemodel.set_value(myiter,3,movie.title)
		self.treemodel.set_value(myiter,4,movie.director)
