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
	# image
	if self.config.get('view_image', 'True')=='False':
		self.view_image.set_active(False)
	else:
		self.view_image.set_active(True)
	# original title
	if self.config.get('view_otitle', 'True')=='False':
		self.view_otitle.set_active(False)
	else:
		self.view_otitle.set_active(True)
	# title
	if self.config.get('view_title', 'True')=='False':
		self.view_title.set_active(False)
	else:
		self.view_title.set_active(True)
	# director
	if self.config.get('view_director', 'True')=='False':
		self.view_director.set_active(False)
	else:
		self.view_director.set_active(True)

	# email reminder
	if self.config.get('mail_use_auth', 'False') == 'False':
		self.mail_use_auth.set_active(False)
	else:
		self.mail_use_auth.set_active(True)

	self.mail_smtp_server.set_text(self.config.get('mail_smtp_server', 'localhost'))
	self.mail_username.set_text(self.config.get('mail_username', ''))
	self.mail_password.set_text(self.config.get('mail_password', ''))
	self.mail_email.set_text(self.config.get('mail_email', 'griffith'))

	# pdf reader
	self.epdf_reader.set_text(self.pdf_reader)

	# pdf font
	if self.config.get('font'):
		self.widgets['preferences']['font'].set_filename(self.config.get('font'))

	# defaults (for static data only)
	if self.config.get('condition'):
		self.widgets['preferences']['condition'].set_active(int(self.config.get('condition')))
	if self.config.get('region'):
		self.widgets['preferences']['region'].set_active(int(self.config.get('region')))
	if self.config.get('layers'):
		self.widgets['preferences']['layers'].set_active(int(self.config.get('layers')))
	if self.config.get('color'):
		self.widgets['preferences']['color'].set_active(int(self.config.get('color')))

	# search for:
	self.p_s_classification.set_active(bool(self.config.get('s_classification')))
	self.p_s_country.set_active(bool(self.config.get('s_country')))
	self.p_s_director.set_active(bool(self.config.get('s_director')))
	self.p_s_genre.set_active(bool(self.config.get('s_genre')))
	self.p_s_image.set_active(bool(self.config.get('s_image')))
	self.p_s_notes.set_active(bool(self.config.get('s_notes')))
	self.p_s_o_site.set_active(bool(self.config.get('s_o_site')))
	self.p_s_o_title.set_active(bool(self.config.get('s_o_title')))
	self.p_s_plot.set_active(bool(self.config.get('s_plot')))
	self.p_s_rating.set_active(bool(self.config.get('s_rating')))
	self.p_s_runtime.set_active(bool(self.config.get('s_runtime')))
	self.p_s_site.set_active(bool(self.config.get('s_site')))
	self.p_s_studio.set_active(bool(self.config.get('s_studio')))
	self.p_s_title.set_active(bool(self.config.get('s_title')))
	self.p_s_trailer.set_active(bool(self.config.get('s_trailer')))
	self.p_s_with.set_active(bool(self.config.get('s_with')))
	self.p_s_year.set_active(bool(self.config.get('s_year')))
	
	plugins = gutils.read_plugins('PluginMovie', \
		self.locations['movie_plugins'])
	plugins.sort()
	mcounter = 0
	for p in plugins:
		plugin_module = os.path.basename(p).replace('.py','')
		plugin_name = plugin_module.replace('PluginMovie','')
		if self.config.get('default_movie_plugin') == plugin_name:
			self.widgets['preferences']['default_plugin'].set_active(mcounter)
			self.d_plugin = mcounter
		mcounter = mcounter + 1

	# rating image
	try:
		rimage = int(str(self.config.get('rating_image', '0')))
	except:
		rimage = 0
	self.rating_image.set_active(rimage)

	# spellchecker
	if self.config.get('use_gtkspell', 'False')=='False':
		self.spellchecker.set_active(False)
	else:
		self.spellchecker.set_active(True)

	if self.config.get('spell_notes', 'True')=='False':
		self.spell_notes.set_active(False)
	else:
		self.spell_notes.set_active(True)

	if self.config.get('spell_plot', 'True')=='False':
		self.spell_plot.set_active(False)
	else:
		self.spell_plot.set_active(True)

	self.spell_lang.set_text(str(self.config.get('spell_lang', 'en')))

	self.w_preferences.show()

def save_preferences(self):

	global spell_support

	was_false = obs_was_false = plot_was_false = 1	

	if self.config.get('use_gtkspell', 'False') == 'True':
		was_false = 0

	if self.config.get('spell_notes', 'False') == 'True':
		obs_was_false = 0

	if self.config.get('spell_plot', 'False') == 'True':
		plot_was_false = 0

	# image
	if self.view_image.get_active():
		self.config['view_image'] = 'True'
	else:
		self.config['view_image'] = 'False'
	# original title
	if self.view_otitle.get_active():
		self.config['view_otitle'] = 'True'
	else:
		self.config['view_otitle'] = 'False'
	# title
	if self.view_title.get_active():
		self.config['view_title'] = 'True'
	else:
		self.config['view_title'] = 'False'
	# director
	if self.view_director.get_active():
		self.config['view_director'] = 'True'
	else:
		self.config['view_director'] = 'False'

	# pdf font
	if self.widgets['preferences']['font'].get_filename():
		self.config['font'] = self.widgets['preferences']['font'].get_filename()

	# spellchecker
	if self.spellchecker.get_active():
		self.config['use_gtkspell'] = 'True'
	else:
		self.config['use_gtkspell'] = 'False'		
	if self.spell_notes.get_active():
		self.config['spell_notes'] = 'True'
	else:
		self.config['spell_notes'] = 'False'
	if self.spell_plot.get_active():
		self.config['spell_plot'] = 'True'
	else:
		self.config['spell_plot'] = 'False'

	# rating image
	self.config['rating_image'] = str(self.rating_image.get_active())

	#defaults
	self.config['media'] = self.media_ids[self.widgets['preferences']['media'].get_active()]
	self.config['vcodec'] = self.vcodecs_ids[self.widgets['preferences']['vcodec'].get_active()]
	self.config['condition'] = str(self.widgets['preferences']['condition'].get_active())
	self.config['region'] = str(self.widgets['preferences']['region'].get_active())
	self.config['layers'] = str(self.widgets['preferences']['layers'].get_active())
	self.config['color'] = str(self.widgets['preferences']['color'].get_active())

	# email reminder
	if self.mail_use_auth.get_active():
		self.config['mail_use_auth'] = 'True'
	else:
		self.config['mail_use_auth'] = 'False'

	self.config['mail_smtp_server'] = self.mail_smtp_server.get_text()
	self.config['mail_username'] = self.mail_username.get_text()
	self.config['mail_password'] = self.mail_password.get_text()
	self.config['mail_email'] = self.mail_email.get_text()

	# default movie plugin
	if self.widgets['preferences']['default_plugin'].get_active():
		self.config['default_movie_plugin'] = \
			gutils.on_combo_box_entry_changed(self.widgets['preferences']['default_plugin'])
	# search for:
	self.config['s_classification'] = self.p_s_classification.get_active()
	self.config['s_country'] = self.p_s_country.get_active()
	self.config['s_director'] = self.p_s_director.get_active()
	self.config['s_genre'] = self.p_s_genre.get_active()
	self.config['s_image'] = self.p_s_image.get_active()
	self.config['s_notes'] = self.p_s_notes.get_active()
	self.config['s_o_site'] = self.p_s_o_site.get_active()
	self.config['s_o_title'] = self.p_s_o_title.get_active()
	self.config['s_plot'] = self.p_s_plot.get_active()
	self.config['s_rating'] = self.p_s_rating.get_active()
	self.config['s_runtime'] = self.p_s_runtime.get_active()
	self.config['s_site'] = self.p_s_site.get_active()
	self.config['s_studio'] = self.p_s_studio.get_active()
	self.config['s_title'] = self.p_s_title.get_active()
	self.config['s_trailer'] = self.p_s_trailer.get_active()
	self.config['s_with'] = self.p_s_with.get_active()
	self.config['s_year'] = self.p_s_year.get_active()
	
	mcounter = 0
	for p in self.plugins:
		plugin_module = os.path.basename(p).replace('.py','')
		plugin_name = plugin_module.replace('PluginMovie','')
		if gutils.on_combo_box_entry_changed(self.widgets['preferences']['default_plugin']) == plugin_name:
			self.d_plugin = mcounter
		mcounter = mcounter + 1
	self.widgets['add']['source'].set_active(self.d_plugin)

	if self.windows:
		save_reader = ''
	else:
		save_reader = self.epdf_reader.get_text()

	self.config['spell_lang'] = self.spell_lang.get_text()
	self.config['pdf_reader'] = save_reader
	
	if spell_support:
		if self.config.get('use_gtkspell', 'False') == 'False' and not was_false:
			self.obs_spell.detach()
			self.plot_spell.detach()
		elif self.config.get('use_gtkspell', 'False') == 'True' and was_false:
			initialize.initialize_gtkspell(self)
		else:
			pass

		if self.config.get('use_gtkspell', 'False') == 'True':
			if self.config.get('spell_plot', 'True') == 'False' and not plot_was_false:
				self.plot_spell.detach()
			elif self.config.get('spell_plot', 'True') == 'True' and plot_was_false:
				self.plot_spell = gtkspell.Spell(self.e_plot)
				self.plot_spell.set_language(self.config.get('spell_lang', 'en'))
			else:
				pass

			if self.config.get('spell_notes', 'True') == 'False' and not obs_was_false:
				self.obs_spell.detach()
			elif self.config.get('spell_notes', 'True') == 'True' and obs_was_false:
				self.obs_spell = gtkspell.Spell(self.e_obs)
				self.obs_spell.set_language(self.config.get('spell_lang', 'en'))
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
	self.config['db_host']   = self.widgets['preferences']['db_host'].get_text()
	self.config['db_port']   = int(self.widgets['preferences']['db_port'].get_value())
	self.config['db_name']   = self.widgets['preferences']['db_name'].get_text()
	self.config['db_user']   = self.widgets['preferences']['db_user'].get_text()
	self.config['db_passwd'] = self.widgets['preferences']['db_passwd'].get_text()
	db_type = int(self.widgets['preferences']['db_type'].get_active())
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
		from sqlalchemy.orm import clear_mappers
		clear_mappers()
		self.db = sql.GriffithSQL(self.config, self.debug, self.griffith_dir)
		self.debug.show("New database Engine: %s" % self.db.metadata.engine.name)
		self.total = int(self.db.Movie.count())
		self.count_statusbar()
		from initialize	import dictionaries, people_treeview
		dictionaries(self)
		people_treeview(self, False)
		self.initialized = True
	self.clear_details()
	self.populate_treeview(self.db.Movie.select())
	self.select_last_row(self.total)
