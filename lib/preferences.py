# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes, Piotr Ożarowski
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
	if self.config.get('condition'):
		w['condition'].set_active(int(self.config.get('condition')))
	if self.config.get('region'):
		w['region'].set_active(int(self.config.get('region')))
	if self.config.get('layers'):
		w['layers'].set_active(int(self.config.get('layers')))
	if self.config.get('color'):
		w['color'].set_active(int(self.config.get('color')))

	# search for:
	w['s_classification'].set_active(bool(self.config.get('s_classification')))
	w['s_country'].set_active(bool(self.config.get('s_country')))
	w['s_director'].set_active(bool(self.config.get('s_director')))
	w['s_genre'].set_active(bool(self.config.get('s_genre')))
	w['s_image'].set_active(bool(self.config.get('s_image')))
	w['s_notes'].set_active(bool(self.config.get('s_notes')))
	w['s_o_site'].set_active(bool(self.config.get('s_o_site')))
	w['s_o_title'].set_active(bool(self.config.get('s_o_title')))
	w['s_plot'].set_active(bool(self.config.get('s_plot')))
	w['s_rating'].set_active(bool(self.config.get('s_rating')))
	w['s_runtime'].set_active(bool(self.config.get('s_runtime')))
	w['s_site'].set_active(bool(self.config.get('s_site')))
	w['s_studio'].set_active(bool(self.config.get('s_studio')))
	w['s_title'].set_active(bool(self.config.get('s_title')))
	w['s_trailer'].set_active(bool(self.config.get('s_trailer')))
	w['s_cast'].set_active(bool(self.config.get('s_cast')))
	w['s_year'].set_active(bool(self.config.get('s_year')))
	
	if self.config.get('sortby'):
		tmp = self.sort_criteria.index(self.config.get('sortby'))
		w['sortby'].set_active(tmp)
	
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

	w['window'].show()

def save_preferences(self):
	w = self.widgets['preferences']
	global spell_support

	was_false = notes_was_false = plot_was_false = 1	

	if self.config.get('use_gtkspell', 'False') == 'True':
		was_false = 0

	if self.config.get('spell_notes', 'False') == 'True':
		notes_was_false = 0

	if self.config.get('spell_plot', 'False') == 'True':
		plot_was_false = 0

	# image
	if w['view_image'].get_active():
		self.config['view_image'] = 'True'
	else:
		self.config['view_image'] = 'False'
	# original title
	if w['view_o_title'].get_active():
		self.config['view_otitle'] = 'True'
	else:
		self.config['view_otitle'] = 'False'
	# title
	if w['view_title'].get_active():
		self.config['view_title'] = 'True'
	else:
		self.config['view_title'] = 'False'
	# director
	if w['view_director'].get_active():
		self.config['view_director'] = 'True'
	else:
		self.config['view_director'] = 'False'
	
	# sortby
	if w['sortby'].get_active():
		field = self.sort_criteria[w['sortby'].get_active()]
		if field:
			self.config['sortby'] = field
	else:
		self.config['sortby'] = 'number'
	

	# pdf font
	if w['font'].get_filename():
		self.config['font'] = w['font'].get_filename()

	# spellchecker
	if w['spellchecker'].get_active():
		self.config['use_gtkspell'] = 'True'
	else:
		self.config['use_gtkspell'] = 'False'		
	if w['spell_notes'].get_active():
		self.config['spell_notes'] = 'True'
	else:
		self.config['spell_notes'] = 'False'
	if w['spell_plot'].get_active():
		self.config['spell_plot'] = 'True'
	else:
		self.config['spell_plot'] = 'False'

	# rating image
	self.config['rating_image'] = str(w['rating_image'].get_active())

	#defaults
	self.config['media'] = self.media_ids[w['media'].get_active()]
	self.config['vcodec'] = self.vcodecs_ids[w['vcodec'].get_active()]
	self.config['condition'] = str(w['condition'].get_active())
	self.config['region'] = str(w['region'].get_active())
	self.config['layers'] = str(w['layers'].get_active())
	self.config['color'] = str(w['color'].get_active())

	# email reminder
	if w['mail_use_auth'].get_active():
		self.config['mail_use_auth'] = 'True'
	else:
		self.config['mail_use_auth'] = 'False'

	self.config['mail_smtp_server'] = w['mail_smtp_server'].get_text()
	self.config['mail_username'] = w['mail_username'].get_text()
	self.config['mail_password'] = w['mail_password'].get_text()
	self.config['mail_email'] = w['mail_email'].get_text()

	# default movie plugin
	if w['default_plugin'].get_active():
		self.config['default_movie_plugin'] = \
			gutils.on_combo_box_entry_changed(w['default_plugin'])
	# search for:
	self.config['s_classification'] = w['s_classification'].get_active()
	self.config['s_country'] = w['s_country'].get_active()
	self.config['s_director'] = w['s_director'].get_active()
	self.config['s_genre'] = w['s_genre'].get_active()
	self.config['s_image'] = w['s_image'].get_active()
	self.config['s_notes'] = w['s_notes'].get_active()
	self.config['s_o_site'] = w['s_o_site'].get_active()
	self.config['s_o_title'] = w['s_o_title'].get_active()
	self.config['s_plot'] = w['s_plot'].get_active()
	self.config['s_rating'] = w['s_rating'].get_active()
	self.config['s_runtime'] = w['s_runtime'].get_active()
	self.config['s_site'] = w['s_site'].get_active()
	self.config['s_studio'] = w['s_studio'].get_active()
	self.config['s_title'] = w['s_title'].get_active()
	self.config['s_trailer'] = w['s_trailer'].get_active()
	self.config['s_cast'] = w['s_cast'].get_active()
	self.config['s_year'] = w['s_year'].get_active()
	
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

	self.config['spell_lang'] = w['spell_lang'].get_text()
	self.config['pdf_reader'] = save_reader
	
	if spell_support:
		if self.config.get('use_gtkspell', 'False') == 'False' and not was_false:
			self.notes_spell.detach()
			self.plot_spell.detach()
		elif self.config.get('use_gtkspell', 'False') == 'True' and was_false:
			initialize.initialize_gtkspell(self)
		else:
			pass

		if self.config.get('use_gtkspell', 'False') == 'True':
			if self.config.get('spell_plot', 'True') == 'False' and not plot_was_false:
				self.plot_spell.detach()
			elif self.config.get('spell_plot', 'True') == 'True' and plot_was_false:
				self.plot_spell = gtkspell.Spell(self.widgets['add']['plot'])
				self.plot_spell.set_language(self.config.get('spell_lang', 'en'))
			else:
				pass

			if self.config.get('spell_notes', 'True') == 'False' and not notes_was_false:
				self.notes_spell.detach()
			elif self.config.get('spell_notes', 'True') == 'True' and notes_was_false:
				self.notes_spell = gtkspell.Spell(self.widgets['add']['notes'])
				self.notes_spell.set_language(self.config.get('spell_lang', 'en'))
			else:
				pass
	self.pdf_reader = save_reader

	# database
	old = {}
	old['db_type']   = self.config['db_type']
	old['db_host']   = self.config['db_host']
	old['db_port']   = self.config['db_port']
	old['db_name']   = self.config['db_name']
	old['db_user']   = self.config['db_user']
	old['db_passwd'] = self.config['db_passwd']
	self.config['db_host']   = w['db_host'].get_text()
	self.config['db_port']   = int(w['db_port'].get_value())
	self.config['db_name']   = w['db_name'].get_text()
	self.config['db_user']   = w['db_user'].get_text()
	self.config['db_passwd'] = w['db_passwd'].get_text()
	db_type = int(w['db_type'].get_active())
	if db_type == 1:
		self.config['db_type'] = 'postgres'
	elif db_type == 2:
		self.config['db_type'] = 'mysql'
	else:
		self.config['db_type'] = 'sqlite'
	self.config.save()

	if old['db_type'] != self.config['db_type'] or (old['db_type']!='sqlite' and (\
			old['db_host'] != self.config['db_host'] or \
			old['db_port'] != self.config['db_port'] or \
			old['db_name'] != self.config['db_name'] or \
			old['db_user'] != self.config['db_user'] or \
			old['db_passwd'] != self.config['db_passwd'])):
		self.debug.show('DATABASE: connecting to new db server...')
		# NEW DB CONNECTION
		import sql
		self.initialized = False
		self.db.metadata.clear()
		self.db = sql.GriffithSQL(self.config, self.debug, self.griffith_dir)
		self.debug.show("New database Engine: %s" % self.db.metadata.engine.name)
		self.total = int(self.db.Movie.count())
		self.count_statusbar()
		from initialize	import dictionaries, people_treeview
		dictionaries(self)
		people_treeview(self, False)
		self.initialized = True
	self.clear_details()
	self.populate_treeview()
	self.go_last()
