# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes, Piotr Ożarowski
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
import os
import initialize
import gutils

try:
	import gtkspell
	spell_support = 1
except:
	spell_support = 0

def show_preferences(self):
	w = self.widgets['preferences']
	# number
	if self.config.get('view_number', 'True')=='False':
		w['view_number'].set_active(False)
	else:
		w['view_number'].set_active(True)
	# image
	if self.config.get('view_image', 'True')=='False':
		w['view_image'].set_active(False)
	else:
		w['view_image'].set_active(True)
	# original title
	if self.config.get('view_otitle', 'True')=='False':
		w['view_o_title'].set_active(False)
	else:
		w['view_o_title'].set_active(True)
	# title
	if self.config.get('view_title', 'True')=='False':
		w['view_title'].set_active(False)
	else:
		w['view_title'].set_active(True)
	# director
	if self.config.get('view_director', 'True')=='False':
		w['view_director'].set_active(False)
	else:
		w['view_director'].set_active(True)

	# email reminder
	if self.config.get('mail_use_auth', 'False') == 'False':
		w['mail_use_auth'].set_active(False)
	else:
		w['mail_use_auth'].set_active(True)

	w['mail_smtp_server'].set_text(self.config.get('mail_smtp_server', 'localhost'))
	w['mail_username'].set_text(self.config.get('mail_username', ''))
	w['mail_password'].set_text(self.config.get('mail_password', ''))
	w['mail_email'].set_text(self.config.get('mail_email', 'griffith'))

	# pdf reader
	w['epdf_reader'].set_text(self.pdf_reader)

	# pdf font
	if self.config.get('font'):
		w['font'].set_filename(self.config.get('font'))

	# defaults (for static data only)
	w['condition'].set_active( gutils.digits_only(self.config.get('condition', 0), 5) )
	w['region'].set_active( gutils.digits_only(self.config.get('region', 0), 8) )
	w['layers'].set_active( gutils.digits_only(self.config.get('layers', 0), 4) )
	w['color'].set_active( gutils.digits_only(self.config.get('color', 0), 3 ))
	if self.config.get('media', 0) in self.media_ids:
		if self.config.get('media', 0) > 0:
			w['media'].set_active( gutils.findKey(self.config.get('media', 0), self.media_ids) )
		else:
			w['media'].set_active(0)
	if self.config.get('vcodec', 0) in self.vcodecs_ids >- 1:
		if self.config.get('vcodec', 0) > 0:
			w['vcodec'].set_active(	int(gutils.findKey(self.config.get('vcodec', 0), self.vcodecs_ids)) )
		else:
			w['vcodec'].set_active(0)
	
	# search for:
	w['s_classification'].set_active(bool(self.config.get('s_classification', True)))
	w['s_country'].set_active(bool(self.config.get('s_country', True)))
	w['s_director'].set_active(bool(self.config.get('s_director', True)))
	w['s_genre'].set_active(bool(self.config.get('s_genre', True)))
	w['s_image'].set_active(bool(self.config.get('s_image', True)))
	w['s_notes'].set_active(bool(self.config.get('s_notes', True)))
	w['s_o_site'].set_active(bool(self.config.get('s_o_site', True)))
	w['s_o_title'].set_active(bool(self.config.get('s_o_title', True)))
	w['s_plot'].set_active(bool(self.config.get('s_plot', True)))
	w['s_rating'].set_active(bool(self.config.get('s_rating', True)))
	w['s_runtime'].set_active(bool(self.config.get('s_runtime', True)))
	w['s_site'].set_active(bool(self.config.get('s_site', True)))
	w['s_studio'].set_active(bool(self.config.get('s_studio', True)))
	w['s_title'].set_active(bool(self.config.get('s_title', True)))
	w['s_trailer'].set_active(bool(self.config.get('s_trailer', True)))
	w['s_cast'].set_active(bool(self.config.get('s_cast', True)))
	w['s_year'].set_active(bool(self.config.get('s_year', True)))
	
	if self.config.get('sortby'):
		tmp = self.sort_criteria.index(self.config.get('sortby'))
		w['sortby'].set_active(tmp)
	w['sortby_reverse'].set_active(bool(self.config.get('sortby_reverse', False)))
	
	w['s_limit'].set_value(gutils.digits_only(self.config.get('s_limit', 0)))
	
	plugins = gutils.read_plugins('PluginMovie', \
		self.locations['movie_plugins'])
	plugins.sort()
	mcounter = 0
	for p in plugins:
		plugin_module = os.path.basename(p).replace('.py','')
		plugin_name = plugin_module.replace('PluginMovie','')
		if self.config.get('default_movie_plugin') == plugin_name:
			w['default_plugin'].set_active(mcounter)
			self.d_plugin = mcounter
		mcounter = mcounter + 1

	# rating image
	try:
		rimage = int(str(self.config.get('rating_image', '0')))
	except:
		rimage = 0
	w['rating_image'].set_active(rimage)

	# spellchecker
	if self.config.get('use_gtkspell', 'False')=='False':
		w['spellchecker'].set_active(False)
	else:
		w['spellchecker'].set_active(True)

	if self.config.get('spell_notes', 'True')=='False':
		w['spell_notes'].set_active(False)
	else:
		w['spell_notes'].set_active(True)

	if self.config.get('spell_plot', 'True')=='False':
		w['spell_plot'].set_active(False)
	else:
		w['spell_plot'].set_active(True)

	w['spell_lang'].set_text(str(self.config.get('spell_lang', 'en')))

	w['amazon_locale'].set_active(self.config.get('amazon_locale', 0))

	w['window'].show()

def save_preferences(self):
	w = self.widgets['preferences']
	c = self.config
	global spell_support

	was_false = notes_was_false = plot_was_false = 1	

	if c.get('use_gtkspell', 'False') == 'True':
		was_false = 0

	if c.get('spell_notes', 'False') == 'True':
		notes_was_false = 0

	if c.get('spell_plot', 'False') == 'True':
		plot_was_false = 0

	# number
	if w['view_number'].get_active():
		c['view_number'] = 'True'
	else:
		c['view_number'] = 'False'
	# image
	if w['view_image'].get_active():
		c['view_image'] = 'True'
	else:
		c['view_image'] = 'False'
	# original title
	if w['view_o_title'].get_active():
		c['view_otitle'] = 'True'
	else:
		c['view_otitle'] = 'False'
	# title
	if w['view_title'].get_active():
		c['view_title'] = 'True'
	else:
		c['view_title'] = 'False'
	# director
	if w['view_director'].get_active():
		c['view_director'] = 'True'
	else:
		c['view_director'] = 'False'
	
	# sortby
	if w['sortby'].get_active():
		field = self.sort_criteria[w['sortby'].get_active()]
		if field:
			c['sortby'] = field
	else:
		c['sortby'] = 'number'
	c['sortby_reverse'] = w['sortby_reverse'].get_active()
	
	c['s_limit'] = str(int(w['s_limit'].get_value()))
	

	# pdf font
	if w['font'].get_filename():
		c['font'] = w['font'].get_filename()

	# spellchecker
	if w['spellchecker'].get_active():
		c['use_gtkspell'] = 'True'
	else:
		c['use_gtkspell'] = 'False'		
	if w['spell_notes'].get_active():
		c['spell_notes'] = 'True'
	else:
		c['spell_notes'] = 'False'
	if w['spell_plot'].get_active():
		c['spell_plot'] = 'True'
	else:
		c['spell_plot'] = 'False'

	# rating image
	c['rating_image'] = str(w['rating_image'].get_active())

	#defaults
	c['media'] = self.media_ids[w['media'].get_active()]
	c['vcodec'] = self.vcodecs_ids[w['vcodec'].get_active()]
	c['condition'] = str(w['condition'].get_active())
	c['region'] = str(w['region'].get_active())
	c['layers'] = str(w['layers'].get_active())
	c['color'] = str(w['color'].get_active())

	# email reminder
	if w['mail_use_auth'].get_active():
		c['mail_use_auth'] = 'True'
	else:
		c['mail_use_auth'] = 'False'

	c['mail_smtp_server'] = w['mail_smtp_server'].get_text()
	c['mail_username'] = w['mail_username'].get_text()
	c['mail_password'] = w['mail_password'].get_text()
	c['mail_email'] = w['mail_email'].get_text()

	# default movie plugin
	if w['default_plugin'].get_active():
		c['default_movie_plugin'] = \
			gutils.on_combo_box_entry_changed(w['default_plugin'])
	# search for:
	c['s_classification'] = w['s_classification'].get_active()
	c['s_country'] = w['s_country'].get_active()
	c['s_director'] = w['s_director'].get_active()
	c['s_genre'] = w['s_genre'].get_active()
	c['s_image'] = w['s_image'].get_active()
	c['s_notes'] = w['s_notes'].get_active()
	c['s_o_site'] = w['s_o_site'].get_active()
	c['s_o_title'] = w['s_o_title'].get_active()
	c['s_plot'] = w['s_plot'].get_active()
	c['s_rating'] = w['s_rating'].get_active()
	c['s_runtime'] = w['s_runtime'].get_active()
	c['s_site'] = w['s_site'].get_active()
	c['s_studio'] = w['s_studio'].get_active()
	c['s_title'] = w['s_title'].get_active()
	c['s_trailer'] = w['s_trailer'].get_active()
	c['s_cast'] = w['s_cast'].get_active()
	c['s_year'] = w['s_year'].get_active()
	
	mcounter = 0
	for p in self.plugins:
		plugin_module = os.path.basename(p).replace('.py','')
		plugin_name = plugin_module.replace('PluginMovie','')
		if gutils.on_combo_box_entry_changed(w['default_plugin']) == plugin_name:
			self.d_plugin = mcounter
		mcounter = mcounter + 1
	self.widgets['add']['source'].set_active(self.d_plugin)

	if self.windows:
		save_reader = ''
	else:
		save_reader = w['epdf_reader'].get_text()

	c['spell_lang'] = w['spell_lang'].get_text()
	c['pdf_reader'] = save_reader

	c['amazon_locale'] = w['amazon_locale'].get_active()
	
	if spell_support:
		if c.get('use_gtkspell', 'False') == 'False' and not was_false:
			self.notes_spell.detach()
			self.plot_spell.detach()
		elif c.get('use_gtkspell', 'False') == 'True' and was_false:
			initialize.initialize_gtkspell(self)
		else:
			pass

		if c.get('use_gtkspell', 'False') == 'True':
			if c.get('spell_plot', 'True') == 'False' and not plot_was_false:
				self.plot_spell.detach()
			elif c.get('spell_plot', 'True') == 'True' and plot_was_false:
				self.plot_spell = gtkspell.Spell(self.widgets['add']['plot'])
				self.plot_spell.set_language(c.get('spell_lang', 'en'))
			else:
				pass

			if c.get('spell_notes', 'True') == 'False' and not notes_was_false:
				self.notes_spell.detach()
			elif c.get('spell_notes', 'True') == 'True' and notes_was_false:
				self.notes_spell = gtkspell.Spell(self.widgets['add']['notes'])
				self.notes_spell.set_language(c.get('spell_lang', 'en'))
			else:
				pass
	self.pdf_reader = save_reader

	# database
	old = {
		'db_type':   c['db_type'],
		'db_host':   c['db_host'],
		'db_port':   c['db_port'],
		'db_name':   c['db_name'],
		'db_user':   c['db_user'],
		'db_passwd': c['db_passwd'],
	}
	c['db_host']   = w['db_host'].get_text()
	c['db_port']   = int(w['db_port'].get_value())
	c['db_name']   = w['db_name'].get_text()
	c['db_user']   = w['db_user'].get_text()
	c['db_passwd'] = w['db_passwd'].get_text()
	db_type = int(w['db_type'].get_active())
	if db_type == 1:
		c['db_type'] = 'postgres'
	elif db_type == 2:
		c['db_type'] = 'mysql'
	else:
		c['db_type'] = 'sqlite'

	if old['db_type'] != c['db_type'] or (old['db_type']!='sqlite' and (\
			old['db_host'] != c['db_host'] or \
			old['db_port'] != c['db_port'] or \
			old['db_name'] != c['db_name'] or \
			old['db_user'] != c['db_user'] or \
			old['db_passwd'] != c['db_passwd'])):
		self.debug.show('DATABASE: connecting to new db server...')
		
		# new database connection
		import sql
		self.initialized = False
		self.db.metadata.clear()
		from sqlalchemy.orm import clear_mappers
		clear_mappers()
		self.db = sql.GriffithSQL(c, self.debug, self.locations['home'])
		self.debug.show("New database Engine: %s" % self.db.metadata.engine.name)
		
		# initialize new database
		self.total = int(self.db.Movie.count())
		self.count_statusbar()
		from initialize	import dictionaries, people_treeview, location_posters
		c['posters'] = None # force update
		location_posters(self.locations, self.config)
		dictionaries(self)
		people_treeview(self, False)
		self.initialized = True
	self.clear_details()
	self.filter_txt(None)
	self.go_last()
	c.save()
