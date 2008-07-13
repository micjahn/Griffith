# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski

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
		treeselection = self.widgets['treeview'].get_selection()
		(tmp_model, tmp_iter) = treeselection.get_selected()
		if tmp_iter is None:
			self.debug.show('Treeview: no selection')
			return False
		number = tmp_model.get_value(tmp_iter,0)
		movie = self.db.Movie.query.filter_by(number=number).first()
        # FIXME
		#movie.refresh() # loan data can be obsolete in cache
		if movie is None:
			self.debug.show("Treeview: movie doesn't exists (number=%s)"%number)
		set_details(self, movie)
	else:
		set_details(self, {})

def set_details(self, item=None):#{{{
	from loan import get_loan_info, get_loan_history
	if item is None:
		item = {}
	if item.has_key('movie_id') and item['movie_id']:
		self._movie_id = item['movie_id']
	else:
		self._movie_id = None
	w = self.widgets['movie']

	if item.has_key('number') and item['number']:
		w['number'].set_text(str(int(item['number'])))
	else:
		w['number'].set_text('')
	if item.has_key('title') and item['title']:
		w['title'].set_markup("<b><span size='large'>%s</span></b>" % gutils.html_encode(item['title']))
	else:
		w['title'].set_text('')
	if item.has_key('o_title') and item['o_title']:
		w['o_title'].set_markup("<span size='medium'><i>%s</i></span>" % gutils.html_encode(item['o_title']))
	else:
		w['o_title'].set_text('')
	if item.has_key('director') and item['director']:
		w['director'].set_markup("<i>%s</i>" % gutils.html_encode(item['director']))
	else:
		w['director'].set_text('')
	if item.has_key('plot') and item['plot']:
		w['plot'].set_text(str(item['plot']))
	else:
		w['plot'].set_text('')
	if item.has_key('year') and item['year']:
		w['year'].set_text(str(item['year']))
	else:
		w['year'].set_text('')
	if item.has_key('runtime') and item['runtime']:
		w['runtime'].set_text(str(int(item['runtime'])))
	else:
		w['runtime'].set_text('x')
	if item.has_key('cast') and item['cast']:
		w['cast'].set_text(str(item['cast']))
	else:
		w['cast'].set_text('')
	if item.has_key('country') and item['country']:
		w['country'].set_markup("<i>%s</i>" % gutils.html_encode(item['country']))
	else:
		w['country'].set_text('')
	if item.has_key('genre') and item['genre']:
		w['genre'].set_markup("<i>%s</i>" % gutils.html_encode(item['genre']))
	else:
		w['genre'].set_text('')
	if item.has_key('cond') and item['cond']:
		if str(item['cond']) in [ str(i) for i in range(len(self._conditions)) ]:
			w['condition'].set_markup("<i>%s</i>" % self._conditions[item['cond']])
		else:
			w['condition'].set_text('')
			self.debug.show("Wrong value in 'condition' field (movie_id=%s, cond=%s)" % (item['movie_id'], item['cond']))
	else:
		w['condition'].set_text('')
	if item.has_key('region') and item['region']:
		if str(item['region']) in [ str(i) for i in range(len(self._regions)) ]:
			w['region'].set_markup("<i>%s</i>" % gutils.html_encode(item['region']))
			if int(item['region']) < 9:
				self.widgets['tooltips'].set_tip(w['region'], self._regions[int(item['region'])])
		else:
			self.debug.show("Wrong value in 'region' field (movie_id=%s, region=%s)" % (item['movie_id'], item['region']))
			w['region'].set_text('')
			self.widgets['tooltips'].set_tip(w['region'], self._regions[0]) # N/A
	else:
		w['region'].set_text('')
		self.widgets['tooltips'].set_tip(w['region'], self._regions[0]) # N/A
	if item.has_key('layers') and item['layers']:
		if str(item['layers']) in [ str(i) for i in range(len(self._layers)) ]:
			w['layers'].set_markup("<i>%s</i>" % self._layers[item['layers']])
		else:
			self.debug.show("Wrong value in 'layers' field (movie_id=%s, layers=%s)" % (item['movie_id'], item['layers']))
			w['layers'].set_text('')
	else:
		w['layers'].set_text('')
	if item.has_key('color') and item['color']:
		if str(item['color']) in [ str(i) for i in range(len(self._colors)) ]:
			w['color'].set_markup("<i>%s</i>" % self._colors[item['color']])
		else:
			self.debug.show("Wrong value in 'color' field (movie_id=%s, color=%s)" % (item['movie_id'], item['color']))
			w['color'].set_markup('')
	else:
		w['color'].set_markup('')
	if item.has_key('classification') and item['classification']:
		w['classification'].set_markup("<i>%s</i>" % gutils.html_encode(item['classification']))
	else:
		w['classification'].set_text('')
	if item.has_key('studio') and item['studio']:
		w['studio'].set_markup("<i>%s</i>" % gutils.html_encode(item['studio']))
	else:
		w['studio'].set_text('')
	if item.has_key('o_site') and item['o_site']:
		self._o_site_url = str(item['o_site'])
		w['go_o_site_button'].set_sensitive(True)
	else:
		self._o_site_url = None
		w['go_o_site_button'].set_sensitive(False)
	if item.has_key('site') and item['site']:
		self._site_url = str(item['site'])
		w['go_site_button'].set_sensitive(True)
	else:
		self._site_url = None
		w['go_site_button'].set_sensitive(False)
	if item.has_key('trailer') and item['trailer']:
		self._trailer_url = str(item.trailer)
		w['go_trailer_button'].set_sensitive(True)
	else:
		self._trailer_url = None
		w['go_trailer_button'].set_sensitive(False)
	if item.has_key('seen') and item['seen'] == True:
		w['seen_icon'].set_from_file(os.path.join(self.locations['images'], 'seen.png'))
	else:
		w['seen_icon'].set_from_file(os.path.join(self.locations['images'], 'unseen.png'))
	if item.has_key('notes') and item['notes']:
		w['notes'].set_text(str(item.notes))
	else:
		w['notes'].set_text('')
	tmp = ''
	if item.has_key('media_num') and item['media_num']:
		tmp = str(item.media_num)
	else:
		tmp = '0'
	if item.has_key('medium_id') and item['medium_id']:
		if item.medium is not None:
			tmp += ' x ' + item.medium.name
		else:
			pass
	w['medium'].set_markup("<i>%s</i>" % gutils.html_encode(tmp))
	if item.has_key('vcodec_id'):
		if item.vcodec is not None:
			w['vcodec'].set_markup("<i>%s</i>" % gutils.html_encode(item.vcodec.name))
		else:
			w['vcodec'].set_text('')
	else:
		w['vcodec'].set_text('')

	# poster
	if item.has_key('image') and item['image']:
		tmp_dest = self.locations['posters']
		tmp_img = os.path.join(tmp_dest, "m_%s.jpg"%item['image'])
		tmp_img2 = os.path.join(tmp_dest, "%s.jpg"%item['image'])
		if os.path.isfile(tmp_img2):
			image_path = tmp_img
			self.widgets['add']['delete_poster'].set_sensitive(True)
			self.widgets['menu']['delete_poster'].set_sensitive(True)
			w['picture_button'].set_sensitive(True)
		else:
			image_path = os.path.join(self.locations['images'], 'default.png')
			self.widgets['add']['delete_poster'].set_sensitive(False)
			self.widgets['menu']['delete_poster'].set_sensitive(False)
			w['picture_button'].set_sensitive(False)
		# lets see if we have a scaled down medium image already created
		if not os.path.isfile(image_path):
			# if not, lets make one for future use :D
			original_image = os.path.join(tmp_dest, "%s.jpg"%item.image)
			if os.path.isfile(original_image):
				gutils.make_medium_image(self, "%s.jpg"%item.image)
	else:
		image_path = os.path.join(self.locations['images'], 'default.png')
		w['picture_button'].set_sensitive(False)
	w['picture'].set_from_file(image_path)
	# ratig
	rimage = int(self.config.get('rating_image', 0))
	if rimage:
		prefix = ''
	else:
		prefix = 'meter'
	if item.has_key('rating') and item['rating']:
		rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, item['rating'])
	else:
		rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, 0)
	handler = w['image_rating'].set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(rating_file))
	gutils.garbage(handler)

	# check loan status and adjust buttons and history box
	if item.has_key('loaned') and item['loaned'] == True:
		self.widgets['popups']['loan'].set_sensitive(False)
		self.widgets['popups']['email'].set_sensitive(True)
		self.widgets['popups']['return'].set_sensitive(True)
		self.widgets['menu']['loan'].set_sensitive(False)
		self.widgets['menu']['email'].set_sensitive(True)
		self.widgets['menu']['return'].set_sensitive(True)
		w['loan_button'].set_sensitive(False)
		w['email_reminder_button'].set_sensitive(True)
		w['return_button'].set_sensitive(True)
		
		data_loan = get_loan_info(self.db, collection_id=item['collection_id'], volume_id=item['volume_id'], movie_id=item['movie_id'])
		if data_loan is None:
			item.loaned = False
		else:
			data_person = self.db.Person.query.filter_by(person_id=data_loan.person.person_id).first()
			self.person_name = str(data_person.name)
			self.person_email = str(data_person.email)
			self.loan_date = str(data_loan.date)
			w['loan_info'].set_use_markup(False)
			w['loan_info'].set_label(_("This movie has been loaned to ") + self.person_name + _(" on ") + self.loan_date[:10])
	if item.has_key('loaned') and item['loaned'] != True: # "loaned" status can be changed above, so don't use "else:" in this line
		self.widgets['popups']['loan'].set_sensitive(True)
		self.widgets['popups']['email'].set_sensitive(False)
		self.widgets['popups']['return'].set_sensitive(False)
		self.widgets['menu']['loan'].set_sensitive(True)
		self.widgets['menu']['email'].set_sensitive(False)
		self.widgets['menu']['return'].set_sensitive(False)
		w['return_button'].set_sensitive(False)
		w['email_reminder_button'].set_sensitive(False)
		w['loan_button'].set_sensitive(True)
		w['loan_info'].set_markup("<b>%s</b>" % _("Movie not loaned"))

	# loan history	
	self.loans_treemodel.clear()
	if item.has_key('collection_id') or item.has_key('volume_id') or item.has_key('movie_id'):
		loans = get_loan_history(self.db, collection_id=item['collection_id'], volume_id=item['volume_id'], movie_id=item['movie_id'])
		for loan in loans:
			myiter = self.loans_treemodel.append(None)
			self.loans_treemodel.set_value(myiter, 0,'%s' % str(loan.date)[:10])
			if loan.return_date and  loan.return_date != '':
				self.loans_treemodel.set_value(myiter, 1, str(loan.return_date)[:10])
			else:
				self.loans_treemodel.set_value(myiter, 1, "---")
			person = self.db.Person.query.filter_by(person_id=loan.person.person_id).first()
			self.loans_treemodel.set_value(myiter, 2, person.name)

	# volumes/collections
	if item.has_key('volume_id') and item['volume_id']>0:
		if item.has_key('volume') and item['volume']:
			w['volume'].set_markup("<b>%s</b>" % gutils.html_encode(item['volume'].name))
			w['show_volume_button'].set_sensitive(True)
		else:
			w['volume'].set_text('')
			w['show_volume_button'].set_sensitive(False)
	else:
			w['volume'].set_text('')
			w['show_volume_button'].set_sensitive(False)
	if item.has_key('collection_id') and item['collection_id']>0:
		if item.has_key('collection') and item['collection']:
			w['collection'].set_markup("<b>%s</b>" % gutils.html_encode(item['collection'].name))
			w['show_collection_button'].set_sensitive(True)
		else:
			w['collection'].set_text('')
			w['show_collection_button'].set_sensitive(False)
	else:
		w['collection'].set_text('')
		w['show_collection_button'].set_sensitive(False)

	# languages
	for i in w['audio_vbox'].get_children():
		i.destroy()
	for i in w['subtitle_vbox'].get_children():
		i.destroy()
	if item.has_key('languages') and len(item['languages'])>0:
		for i in item['languages']:
			if i.type == 3: # subtitles
				if i.subformat:
					tmp = "%s - %s" % (i.language.name, i.subformat.name)
				else:
					tmp = "%s" % i.language.name
				w['subtitle_vbox'].pack_start(gtk.Label(tmp))
			else:
				language = i.language.name
				if i.type is not None and len(self._lang_types[i.type])>0:
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
				w['audio_vbox'].pack_start(widget)
	w['audio_vbox'].show_all()
	w['subtitle_vbox'].show_all()
	#tags
	if item.has_key('tags'):
		tmp = ''
		for tag in item['tags']:
			tmp += "%s, " % tag.name
		tmp = tmp[:-2] # cut last comma
		w['tags'].set_text(tmp)
	#}}}
	
def populate(self, movies=None, where=None):#{{{
	if self.initialized is False:
		return False
	from sqlalchemy import select, desc
	
	if movies is None:
		movies = select([self.db.Movie.c.number,
			self.db.Movie.c.o_title, self.db.Movie.c.title,
			self.db.Movie.c.director, self.db.Movie.c.image,
			self.db.Movie.c.genre, self.db.Movie.c.seen,
			self.db.Movie.c.year, self.db.Movie.c.runtime])

	#if isinstance(movies, Select):
	if 1==1: # FIXME
		if not where: # because of possible 'seen', 'loaned', 'collection_id' in where
			# seen / loaned
			loaned_only = self.widgets['menu']['loaned_movies'].get_active()
			not_seen_only = self.widgets['menu']['not_seen_movies'].get_active()
			if loaned_only:
				movies.append_whereclause(self.db.Movie.c.loaned==True)
			if not_seen_only:
				movies.append_whereclause(self.db.Movie.c.seen==False)
			# collection
			pos = self.widgets['filter']['collection'].get_active()
			if pos >= 0:
				col_id = self.collection_combo_ids[pos]
				if col_id > 0:
					movies.append_whereclause(self.db.Movie.c.collection_id==col_id)
			# volume
			pos = self.widgets['filter']['volume'].get_active()
			if pos >= 0:
				vol_id = self.volume_combo_ids[pos]
				if vol_id > 0:
					movies.append_whereclause(self.db.Movie.c.volume_id==vol_id)
			# loaned to
			pos = self.widgets['filter']['loanedto'].get_active()
			if pos >= 0:
				per_id = self.loanedto_combo_ids[pos]
				if per_id > 0:
					from sqlalchemy import join, exists, and_
					loan_exists = exists([self.db.Loan.c.movie_id], \
						and_(self.db.Movie.c.movie_id==self.db.Loan.c.movie_id, self.db.Loan.c.person_id==per_id, self.db.Loan.c.return_date==None))
					movies.append_whereclause(loan_exists)
					#loan_join = join(self.db.metadata.tables['movies'], \
					#	self.db.metadata.tables['loans'], \
					#	self.db.metadata.tables['movies'].c.movie_id==self.db.metadata.tables['loans'].c.movie_id)
					#movies = movies.select_from(loan_join)
			# tag
			pos = self.widgets['filter']['tag'].get_active()
			if pos >= 0:
				tag_id = self.bytag_combo_ids[pos]
				if tag_id > 0:
					from sqlalchemy import join, exists, and_
					tag_exists = exists([self.db.MovieTag.c.movie_id], \
						and_(self.db.Movie.c.movie_id==self.db.MovieTag.c.movie_id, self.db.MovieTag.c.tag_id==tag_id))
					movies.append_whereclause(tag_exists)
		
		# select sort column
		sort_column_name = self.config.get('sortby', 'number', section='mainlist')
		sort_reverse = self.config.get('sortby_reverse', False, section='mainlist')
		for i in sort_column_name.split(','):
			if self.db.Movie.c.has_key(i):
				if sort_reverse:
					movies.append_order_by(desc(self.db.Movie.c[i]))
				else:
					movies.append_order_by(self.db.Movie.c[i])
		
		# additional whereclause (volume_id, collection_id, ...)
		if where:
			for i in where:
				if self.db.Movie.c.has_key(i):
					movies.append_whereclause(self.db.Movie.c[i]==where[i])
		movies = movies.execute().fetchall()

	self.total = len(movies)
	# disable refreshing while inserting
	self.widgets['treeview'].freeze_child_notify()
	self.widgets['treeview'].set_model(None)

	# save user sort column
	sort_column_id, order = self.treemodel.get_sort_column_id()

	# new treemodel (faster and prevents some problems)
	self.treemodel = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, str, str, str, bool, str, str)

	# check preferences to hide or show columns
	if self.config.get('number', True, 'mainlist') == True:
		self.number_column.set_visible(True)
	else:
		self.number_column.set_visible(False)
	if self.config.get('otitle', True, 'mainlist') == True:
		self.otitle_column.set_visible(True)
	else:
		self.otitle_column.set_visible(False)
	if self.config.get('title', True, 'mainlist') == True:
		self.title_column.set_visible(True)
	else:
		self.title_column.set_visible(False)
	if self.config.get('director', True, 'mainlist') == True:
		self.director_column.set_visible(True)
	else:
		self.director_column.set_visible(False)
	if self.config.get('image', True, 'mainlist') == True:
		self.image_column.set_visible(True)
	else:
		self.image_column.set_visible(False)
	if self.config.get('genre', True, 'mainlist') == True:
		self.genre_column.set_visible(True)
	else:
		self.genre_column.set_visible(False)
	if self.config.get('seen', True, 'mainlist') == True:
		self.seen_column.set_visible(True)
	else:
		self.seen_column.set_visible(False)
	if self.config.get('year', True, 'mainlist') == True:
		self.year_column.set_visible(True)
	else:
		self.year_column.set_visible(False)
	if self.config.get('runtime', True, 'mainlist') == True:
		self.runtime_column.set_visible(True)
	else:
		self.runtime_column.set_visible(False)
		
	for movie in movies:
		myiter = self.treemodel.append(None)
		
		self.treemodel.set_value(myiter,0,'%004d' % int(movie.number))

		if self.config.get('image', True, section='mainlist') == True:
			tmp_dest = self.locations['posters']
			tmp_img = os.path.join(tmp_dest, "t_%s.jpg" % str(movie.image))
			if movie.image and os.path.isfile(tmp_img):
				image_path = tmp_img
			else:
				image_path = os.path.join(self.locations['images'], 'default_thumbnail.png')
			# lets see if we have a scaled down thumbnail already created
			if os.path.isfile(os.path.join(tmp_dest, "t_%s.jpg" % str(movie.image))):
				pass
			else:
				# if not, lets make one for future use :D
				original_image = os.path.join(tmp_dest, "%s.jpg" % movie.image)
				if os.path.isfile(original_image):
					gutils.make_thumbnail(self, "%s.jpg" % movie.image)
				else:
					self.Image.set_from_file("%s/default_thumbnail.png" % self.locations['images'])
					pixbuf = self.Image.get_pixbuf()
			self.Image.set_from_file(image_path)
			pixbuf = self.Image.get_pixbuf()
			self.treemodel.set_value(myiter, 1, pixbuf)
		self.treemodel.set_value(myiter,2,movie.o_title)
		self.treemodel.set_value(myiter,3,movie.title)
		self.treemodel.set_value(myiter,4,movie.director)
		self.treemodel.set_value(myiter,5,movie.genre)
		self.treemodel.set_value(myiter,6,movie.seen)
		self.treemodel.set_value(myiter,7,movie.year)
		if movie.runtime is not None:
			self.treemodel.set_value(myiter,8, '%003d' % movie.runtime + _(' min'))
		
	# restore user sort column
	if sort_column_id is not None:
		self.treemodel.set_sort_column_id(sort_column_id, gtk.SORT_ASCENDING)
	
	# add new treemodel and allow refreshs again
	self.widgets['treeview'].set_model(self.treemodel)
	self.widgets['treeview'].thaw_child_notify()
	self.widgets['treeview'].set_cursor_on_cell(0)
	self.count_statusbar()
#}}}

# vim: fdm=marker
