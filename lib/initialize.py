# -*- coding: UTF-8 -*-

__revision__ = '$Id $'

# Copyright (c) 2005-2006 Vasco Nunes
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
import sys
import os
import string
import gtk
import gutils
import gobject
import gettext

try:
	import gtkspell
	spell_support = 1
except:
	spell_support = 0

def locations(self=None):
	if self:
		debug = self.debug
	else:
		class Debug:
			def show(self, text):
				print text
		debug = Debug()
	locations = {}
	locations['exec'] = os.path.abspath(os.path.dirname(sys.argv[0])) # deprecated
	locations['lib']  = os.path.dirname(__file__)

	if os.name == 'nt' or os.name == 'win32':
		import winshell
		mydocs = winshell.my_documents()
		locations['home']           = os.path.join(mydocs, 'griffith')
		locations['movie_plugins']  = "%s\\lib\\plugins\\movie" % locations['exec']
		locations['export_plugins'] = "%s\\lib\\plugins\\export" % locations['exec']
		locations['images']         = "%s\\images" % locations['exec']
		locations['share']          = locations['images']
		locations['glade']          = "%s\\glade\\" % locations['exec']
		locations['desktop']        = ''
		locations['i18n']           = "%s\\i18n" % locations['exec']
		os.environ['PATH'] += ";lib;"
	elif os.name == 'posix':
		locations['home']  = os.path.join(os.path.expanduser('~'), ".griffith")
		locations['share'] = os.path.abspath(os.path.join(locations['lib'], '..'))
		locations['glade'] = os.path.join(locations['share'], 'glade')
		locations['i18n']  = os.path.abspath(os.path.join(locations['share'], '..', 'locale'))
		if not os.path.isdir(locations['i18n']):
			locations['i18n'] = os.path.join(locations['share'], 'i18n')
		#some locations
		if os.path.isdir(os.path.join(locations['share'], 'plugins')):
			locations['movie_plugins']  = os.path.join(locations['share'], 'plugins', 'movie')
			locations['export_plugins'] = os.path.join(locations['share'], 'plugins', 'export')
		else:
			locations['movie_plugins']  = os.path.join(locations['lib'], 'plugins', 'movie')
			locations['export_plugins'] = os.path.join(locations['lib'], 'plugins', 'export')
		locations['images']  = os.path.join(locations['share'], 'images')
		locations['desktop'] = os.path.join(os.path.expanduser('~'), 'Desktop')
	else:
		print 'Operating system not supported'
		sys.exit()
	
	# force different home directory (last argument)
	if len(sys.argv)>1:
		last = sys.argv[len(sys.argv)-1]
		if not last.startswith('-') and os.path.exists(last):
			locations['home'] = sys.argv[len(sys.argv)-1]
			del sys.argv[len(sys.argv)-1] # for gconsole.check_args

	try:
		if not os.path.exists(locations['home']):
			debug.show('Creating %s' % locations['home'])
			os.makedirs(locations['home'])
		else:
			debug.show("Using Griffith directory: %s" % locations['home'])
	except OSError:
		debug.show('Unable to create griffith directory.')
		raise
		sys.exit()

	if not os.access(locations['home'], os.W_OK):
		debug.show('Cannot write to griffith directory, %s' % locations['home'])
		sys.exit()

	if not os.path.exists(os.path.join(locations['home'], 'posters')):
		debug.show('Creating poster directory')
		os.makedirs(os.path.join(locations['home'], 'posters'))

	# includes plugins in system path for easier importing
	sys.path.append(locations['lib'])
	sys.path.append(locations['movie_plugins'])
	sys.path.append(locations['export_plugins'])
	
	if self:
		self.locations = locations
	else:
		return locations

def gui(self):
	self._ = None
	self.debug.show("running on %s" % os.name)
	
	if os.name == 'win32' or os.name == 'nt':
		self.windows = True
	else:
		self.windows = False
	self.posix = (os.name == 'posix')
	
	self.griffith_dir = self.locations['home']	# deprecated
	
	if self.windows:
		gtk.rc_parse('%s\\gtkrc' % self.locations['exec'])

	# i18n
	self._ = gettext.gettext
	gettext.bindtextdomain('griffith', self.locations['i18n'])
	gettext.textdomain('griffith')
	gtk.glade.bindtextdomain('griffith', self.locations['i18n'])
	gtk.glade.textdomain('griffith')

	gf = os.path.join(self.locations['glade'], 'griffith.glade')
	from widgets import define_widgets
	define_widgets(self, gtk.glade.XML(gf))

	self.pdf_reader = self.config.get('pdf_reader')


def toolbar(self):
	"""if toolbar is hide in config lets hide the widget"""
	if not self.config.get('view_toolbar'):
		self.toolbar.hide()
		self.menu_toolbar.set_active(False)

def treeview(self):
	self.treemodel = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, str, str)
	self.main_treeview.set_model(self.treemodel)
	self.main_treeview.set_headers_visible(True)
	# number column
	renderer=gtk.CellRendererText()
	column=gtk.TreeViewColumn(_('N.'), renderer, text=0)
	column.set_resizable(True)
	column.set_sort_column_id(0)
	self.main_treeview.append_column(column)
	# pic column
	renderer=gtk.CellRendererPixbuf()
	self.image_column=gtk.TreeViewColumn(_('Image'), renderer, pixbuf=1)
	self.image_column.set_resizable(False)
	self.main_treeview.append_column(self.image_column)
	# original title column
	renderer=gtk.CellRendererText()
	self.otitle_column=gtk.TreeViewColumn(_('Original Title'), renderer, text=2)
	self.otitle_column.set_resizable(True)
	self.otitle_column.set_sort_column_id(2)
	self.main_treeview.append_column(self.otitle_column)
	# title column
	renderer=gtk.CellRendererText()
	self.title_column=gtk.TreeViewColumn(_('Title'), renderer, text=3)
	self.title_column.set_resizable(True)
	self.title_column.set_sort_column_id(3)
	self.main_treeview.append_column(self.title_column)
	# director column
	renderer=gtk.CellRendererText()
	self.director_column=gtk.TreeViewColumn(_('Director'), renderer, text=4)
	self.director_column.set_sort_column_id(4)
	self.director_column.set_resizable(True)
	self.main_treeview.append_column(self.director_column)
	# add data to treeview
	self.total = int(self.db.Movie.count())
	self.main_treeview.show()

def loans_treeview(self):
	self.loan_history.set_model(self.loans_treemodel)
	self.loan_history.set_headers_visible(True)
	# loan date
	renderer=gtk.CellRendererText()
	self.date_column=gtk.TreeViewColumn(_('Loan Date'), renderer, text=0)
	self.date_column.set_resizable(True)
	self.loan_history.append_column(self.date_column)
	self.date_column.set_sort_column_id(0)
	# return date
	renderer=gtk.CellRendererText()
	self.return_column=gtk.TreeViewColumn(_('Return Date'), renderer, text=1)
	self.return_column.set_resizable(True)
	self.loan_history.append_column(self.return_column)
	# loan to
	renderer=gtk.CellRendererText()
	self.loaner_column=gtk.TreeViewColumn(_('Loaned To'), renderer, text=2)
	self.loaner_column.set_resizable(True)
	self.loan_history.append_column(self.loaner_column)

def lang_treeview(self):
	treeview = self.lang['treeview']
	self.lang['model'] = gtk.TreeStore(str, str, str, str, str)
	treeview.set_model(self.lang['model'])
	treeview.set_headers_visible(True)

	model = self.lang['lang'] = gtk.ListStore(int, str)
	for i in self.db.Lang.select():
		model.append([i.lang_id, i.name])
	combo = gtk.CellRendererCombo()
	combo.set_property('model', model)
	combo.set_property('text-column', 1)
	combo.set_property('editable', True)
	combo.set_property('has-entry', False)
	combo.connect('edited', self.on_tv_lang_combo_edited, 0)
	column=gtk.TreeViewColumn('Language', combo, text=0)
	column.set_sort_column_id(0)
	treeview.append_column(column)
	
	model = self.lang['type'] = gtk.ListStore(int, str)
	model.append([0, ''])
	model.append([1, _('lector')])
	model.append([2, _('dubbing')])
	model.append([3, _('subtitles')])
	combo = gtk.CellRendererCombo()
	combo.set_property('model', model)
	combo.set_property('text-column', 1)
	combo.set_property('editable', True)
	combo.set_property('has-entry', False)
	combo.connect('edited', self.on_tv_lang_combo_edited, 1)
	column=gtk.TreeViewColumn('Type', combo, text=1)
	column.set_sort_column_id(1)
	treeview.append_column(column)

	model = self.lang['acodec'] = gtk.ListStore(int, str)
	for i in self.db.ACodec.select():
		model.append([i.acodec_id, i.name])
	combo = gtk.CellRendererCombo()
	combo.set_property('model', model)
	combo.set_property('text-column', 1)
	combo.set_property('editable', True)
	combo.set_property('has-entry', False)
	combo.connect('edited', self.on_tv_lang_combo_edited, 2)
	column=gtk.TreeViewColumn('Codec', combo, text=2)
	column.set_sort_column_id(2)
	treeview.append_column(column)
	
	model = self.lang['achannel'] = gtk.ListStore(int, str)
	for i in self.db.AChannel.select():
		model.append([i.achannel_id, i.name])
	combo = gtk.CellRendererCombo()
	combo.set_property('model', model)
	combo.set_property('text-column', 1)
	combo.set_property('editable', True)
	combo.set_property('has-entry', False)
	combo.connect('edited', self.on_tv_lang_combo_edited, 3)
	column=gtk.TreeViewColumn('Channels', combo, text=3)
	column.set_sort_column_id(3)
	treeview.append_column(column)
	
	model = self.lang['subformat'] = gtk.ListStore(int, str)
	for i in self.db.SubFormat.select():
		model.append([i.subformat_id, i.name])
	combo = gtk.CellRendererCombo()
	combo.set_property('model', model)
	combo.set_property('text-column', 1)
	combo.set_property('editable', True)
	combo.set_property('has-entry', False)
	combo.connect('edited', self.on_tv_lang_combo_edited, 4)
	column=gtk.TreeViewColumn('Subtitle format', combo, text=4)
	column.set_sort_column_id(4)
	treeview.append_column(column)
	
	treeview.show_all()

def movie_plugins(self):
	"""
	dinamically finds the movie source information plugins
	and fills the plugins drop down list
	"""
	self.plugins = gutils.read_plugins('PluginMovie', \
		self.locations['movie_plugins'])
	self.plugins.sort()
	self.d_plugin = 0
	mcounter = 0
	for p in self.plugins:
		plugin_module = os.path.basename(p).replace('.py','')
		plugin_name = plugin_module.replace('PluginMovie','')
		self.am_source.append_text(plugin_name)
		self.default_plugin.append_text(plugin_name)
		if self.config.get('default_movie_plugin') == plugin_name:
			self.default_plugin.set_active(mcounter)
			self.d_plugin = mcounter
		mcounter = mcounter + 1
	self.am_source.set_active(self.d_plugin)

def export_plugins(self):
	"""
	dinamically finds the available export plugins
	and fills the export menu entry
	"""
	plugins = gutils.read_plugins('PluginExport', \
		self.locations['export_plugins'])
	plugins.sort()
	for p in plugins:
		plugin_module = os.path.basename(p).replace('.py', '')
		plugin_name = plugin_module.replace('PluginExport', '')
		menu_items = gtk.MenuItem(plugin_name)
		self.export_menu.append(menu_items)
		menu_items.connect('activate', self.on_export_activate, plugin_name)
		menu_items.show()

def people_treeview(self, create=True):
	row = None
	self.p_treemodel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
	self.p_treeview.set_model(self.p_treemodel)
	self.p_treeview.set_headers_visible(True)

	if create==True:
		# name column
		renderer=gtk.CellRendererText()
		column=gtk.TreeViewColumn(_('Name'), renderer, text=0)
		column.set_resizable(True)
		column.set_sort_column_id(0)
		self.p_treeview.append_column(column)
		# email column
		renderer=gtk.CellRendererText()
		column=gtk.TreeViewColumn(_('E-mail'),renderer, text=1)
		column.set_resizable(True)
		column.set_sort_column_id(1)
		self.p_treeview.append_column(column)
	# add data to treeview
	self.p_treemodel.clear()
	for person in self.db.Person.select(order_by='name ASC'):
		myiter = self.p_treemodel.insert_before(None, None)
		self.p_treemodel.set_value(myiter, 0, str(person.name))
		self.p_treemodel.set_value(myiter, 1, str(person.email))
	self.p_treeview.show()

def combos(self):
	i = 0
	for cond in self._conditions:
		self.p_condition.insert_text(i, cond)
		self.am_condition.insert_text(i, cond)
		i += 1
	i = 0
	for color in self._colors:
		self.p_color.insert_text(i, color)
		self.am_color.insert_text(i, color)
		i += 1
	i = 0
	for region in self._regions:
		self.p_region.insert_text(i, region)
		self.am_region.insert_text(i, region)
		i += 1
	i = 0
	for layer in self._layers:
		self.p_layers.insert_text(i, layer)
		i += 1
	i = 0
	for criteria in self.sort_criteria:
		self.filter_criteria.insert_text(i, self.field_names[criteria])
		i += 1
	self.filter_criteria.set_active(0)

def dictionaries(self):
	"""initializes data filled dynamically by users"""
	import initialize, update
	self.am_tags = {} # dictionary for tag CheckBoxes
	update.update_volume_combo_ids(self)
	update.update_collection_combo_ids(self)
	initialize.fill_volumes_combo(self)
	initialize.fill_collections_combo(self)
	initialize.fill_preferences_tags_combo(self)
	initialize.language_combos(self)
	initialize.acodec_combos(self)
	initialize.achannel_combos(self)
	initialize.subformat_combos(self)
	initialize.vcodec_combos(self)
	initialize.media_combos(self)
	initialize.create_tag_vbox(self, widget=self.am_tag_vbox, tab=self.am_tags)
	self.sort_criteria = (
		'o_title', 'title', 'number', 'director',
		'plot', 'cast', 'notes', 'year', 'runtime', 'country',
		'genre', 'studio', 'media_num', 'rating')
	self.field_names = {
		'number'         : _('Number'),
		'o_title'        : _('Original Title'),
		'title'          : _('Title'),
		'year'           : _('Year'),
		'cast'           : _('Cast'),
		'classification' : _('Classification'),
		'country'        : _('Country'),
		'genre'          : _('Genre'),
		'director'       : _('Director'),
		'o_site'         : _('Official site'),
		'site'           : _('Site'),
		'trailer'        : _('Trailer'),
		'loaned'         : _('Loaned'),
		'rating'         : _('Rating'),
		'runtime'        : _('Runtime'),
		'studio'         : _('Studio'),
		'seen'           : _('Seen it'),
		'region'         : _('Region'),
		'layers'         : _('Layers'),
		'cond'           : _('Condition'),
		'color'          : _('Color'),
		'volume_id'      : _('Volume'),
		'collection_id'  : _('Collection'),
		'plot'           : _('Plot'),
		'media_num'      : _('Discs'),
		'notes'          : _('Notes')}
	self._conditions = [_('Damaged'), _('Poor'),  _('Fair'), _('Good'), _('Excellent'), _('N/A')]
	self._colors = [_('Color'), _('Black and White'), _('Mixed'), _('N/A')]
	self._layers = [_('Single Side, Single Layer'), _('Single Side, Dual Layer'), _('Dual Side, Single Layer'), _('Dual Side, Dual Layer'), _('N/A')]
	self._regions = [_('Region 0 (No Region Coding)'),
			_('Region 1 (United States of America, Canada)'),
			_('Region 2 (Europe,including France, Greece, Turkey, Egypt, Arabia, Japan and South Africa)'),
			_('Region 3 (Korea, Thailand, Vietnam, Borneo and Indonesia)'),
			_('Region 4 (Australia and New Zealand, Mexico, the Caribbean, and South America)'),
			_('Region 5 (India, Africa, Russia and former USSR countries)'),
			_('Region 6 (Popular Republic of China)'),
			_('Region 8 (Airlines/Cruise Ships)'),
			_('Region 9 (Often used as region free)'),
			_('N/A')]

def web_results(self):
	self.treemodel_results = gtk.TreeStore(str, str)
	self.results_treeview.set_model(self.treemodel_results)
	self.results_treeview.set_headers_visible(False)
	# column ids
	renderer=gtk.CellRendererText()
	self.column1=gtk.TreeViewColumn(None, renderer, text=0)
	self.column1.set_visible(False)
	self.results_treeview.append_column(self.column1)
	# column titles
	renderer=gtk.CellRendererText()
	self.column2=gtk.TreeViewColumn(None, renderer, text=1)
	self.column2.set_resizable(True)
	self.column2.set_sort_column_id(1)
	self.results_treeview.append_column(self.column2)

def initialize_gtkspell(self):
	global spell_support
	spell_error = False
	if self.posix and spell_support:
		if self.config.get('use_gtkspell', False) == 'True':
			if self.config.get('spell_notes', True) == 'True' and \
				self.config.get('spell_lang')!='':
				try:
					self.obs_spell = gtkspell.Spell(self.m_cast, self.config.get('spell_lang'))
				except:
					spell_error = True
			if self.config.get('spell_plot', True)=='True' and \
				self.config.get('spell_lang')!='':
				try:
					self.plot_spell = gtkspell.Spell(self.m_plot, self.config.get('spell_lang'))
				except:
					spell_error = True
			if spell_error:
				gutils.info(self, _("Dictionary not available. Spellcheck will be disabled. \n" + \
					"Please install the aspell-%s package or adjust the spellchekcer preferences.")%self.config.get('spell_lang'), \
					self.w_preferences)
	else:
		self.debug.show('Spellchecker is not available')

def preferences(self):
	self.p_db_type.insert_text(0,'SQLite3 (internal)')
	self.p_db_type.insert_text(1,'PostgreSQL')
	self.p_db_type.insert_text(2,'MySQL')
	if self.config.has_key('db_host'):
		self.p_db_host.set_text(self.config['db_host'])
	if self.config.has_key('db_port'):
		self.p_db_port.set_value(int(self.config['db_port']))
	if self.config.has_key('db_user'):
		self.p_db_user.set_text(self.config['db_user'])
	if self.config.has_key('db_passwd'):
		self.p_db_passwd.set_text(self.config['db_passwd'])
	if self.config.has_key('db_name'):
		self.p_db_name.set_text(self.config['db_name'])
	if self.config.has_key('db_type') and self.config['db_type'] != 'sqlite':
		self.p_db_details.set_sensitive(True)
		if self.config['db_type'] == 'postgres':
			self.p_db_type.set_active(1)
		elif self.config['db_type'] == 'mysql':
			self.p_db_type.set_active(2)
	else:
		self.p_db_type.set_active(0)
		self.p_db_details.set_sensitive(False)

def fill_volumes_combo(self, prefix='e', default=0):
	self.am_volume_combo.get_model().clear()
	for i in self.volume_combo_ids:
		vol_id = self.volume_combo_ids[i]
		if vol_id>0:
			name = self.db.Volume.get_by(volume_id=vol_id).name
		else:
			name = ''
		self.am_volume_combo.insert_text(int(i), str(name))
	self.am_volume_combo.show_all()
	i = gutils.findKey(default, self.volume_combo_ids)
	if i!=None:
		if prefix == 'e':
			self.am_volume_combo.set_active(0)
		else:
			self.am_volume_combo.set_active(int(i))
	self.am_volume_combo.set_wrap_width(3)

def fill_collections_combo(self, prefix='e', default=0):
	self.am_collection_combo.get_model().clear()
	self.f_col.get_model().clear()
	for i in self.collection_combo_ids:
		col_id = self.collection_combo_ids[i]
		if col_id>0:
			name = self.db.Collection.get_by(collection_id=col_id).name
		else:
			name = ''
		self.am_collection_combo.insert_text(int(i), str(name))
		self.f_col.insert_text(int(i), str(name))
	self.am_collection_combo.show_all()
	self.f_col.show_all()
	self.f_col.set_active(0)
	i = gutils.findKey(default, self.collection_combo_ids)
	if i!=None:
		if prefix == 'e':
			self.am_collection_combo.set_active(0)
		else:
			self.am_collection_combo.set_active(int(i))
	self.am_collection_combo.set_wrap_width(2)

def fill_preferences_tags_combo(self):
	self.tag_name_combo.get_model().clear()
	self.tags_ids = {}
	i = 0
	for tag in self.db.Tag.select():
		self.tags_ids[i] = tag.tag_id
		self.tag_name_combo.insert_text(int(i), str(tag.name))
		i += 1
	self.tag_name_combo.show_all()

def language_combos(self):
	self.lang_name_combo.get_model().clear()
	self.languages_ids = {}
	self.languages_ids[0] = 0	# empty one
	self.lang_name_combo.insert_text(0, '')
	i = 1
	for lang in self.db.Lang.select():
		self.languages_ids[i] = lang.lang_id
		self.lang_name_combo.insert_text(int(i), str(lang.name))
		i += 1
	self.lang_name_combo.show_all()
def acodec_combos(self):
	self.acodec_name_combo.get_model().clear()
	self.acodecs_ids = {}
	self.acodecs_ids[0] = 0	# empty one
	self.acodec_name_combo.insert_text(0, '')
	i = 1
	for acodec in self.db.ACodec.select():
		self.acodecs_ids[i] = acodec.acodec_id
		self.acodec_name_combo.insert_text(int(i), str(acodec.name))
		i += 1
	self.acodec_name_combo.show_all()
def achannel_combos(self):
	self.achannel_name_combo.get_model().clear()
	self.achannels_ids = {}
	self.achannels_ids[0] = 0	# empty one
	self.achannel_name_combo.insert_text(0, '')
	i = 1
	for achannel in self.db.AChannel.select():
		self.achannels_ids[i] = achannel.achannel_id
		self.achannel_name_combo.insert_text(int(i), str(achannel.name))
		i += 1
	self.achannel_name_combo.show_all()
def subformat_combos(self):
	self.subformat_name_combo.get_model().clear()
	self.subformats_ids = {}
	self.subformats_ids[0] = 0	# empty one
	self.subformat_name_combo.insert_text(0, '')
	i = 1
	for subformat in self.db.SubFormat.select():
		self.subformats_ids[i] = subformat.subformat_id
		self.subformat_name_combo.insert_text(int(i), str(subformat.name))
		i += 1
	self.subformat_name_combo.show_all()

def media_combos(self):
	# clear data
	self.medium_name_combo.get_model().clear()
	self.p_media.get_model().clear()
	self.am_media.get_model().clear()
	self.media_ids = {}
	i = 0
	for medium in self.db.Medium.select():
		self.media_ids[i] = medium.medium_id
		self.medium_name_combo.insert_text(int(i), str(medium.name))
		self.am_media.insert_text(int(i), str(medium.name))
		self.p_media.insert_text(int(i), str(medium.name))
		i += 1
	self.medium_name_combo.show_all()
	self.am_media.show_all()
	self.p_media.show_all()
	if self.config.has_key('media'):
		pos = gutils.findKey(self.config['media'], self.media_ids)
		if pos !=None:
			self.p_media.set_active(int(pos))
		else:
			self.p_media.set_active(0)

def vcodec_combos(self):
	# clear data
	self.vcodec_name_combo.get_model().clear()
	self.p_vcodec.get_model().clear()
	self.am_vcodec.get_model().clear()
	self.vcodecs_ids = {}
	i = 0
	for vcodec in self.db.VCodec.select():
		self.vcodecs_ids[i] = vcodec.vcodec_id
		self.vcodec_name_combo.insert_text(int(i), str(vcodec.name))
		self.am_vcodec.insert_text(int(i), str(vcodec.name))
		self.p_vcodec.insert_text(int(i), str(vcodec.name))
		i += 1
	self.vcodec_name_combo.show_all()
	self.am_vcodec.show_all()
	self.p_vcodec.show_all()
	if self.config.has_key('vcodec'):
		pos = gutils.findKey(int(self.config['vcodec']), self.vcodecs_ids)
		if pos!=None:
			self.p_vcodec.set_active(int(pos))
		else:
			self.p_vcodec.set_active(0)

def create_tag_vbox(self, widget, tab):
	for i in widget.get_children():
		i.destroy()
	for i in self.tags_ids:
		tag_id = self.tags_ids[i]
		tag_name = self.db.Tag.get_by(tag_id=tag_id).name
		tab[i] = gtk.CheckButton(str(tag_name))
		tab[i].set_active(False)
		widget.pack_start(tab[i])
	widget.show_all()

def remove_hbox(self, widget, tab):
	number = len(widget.get_children())-1	# last box number
	try:
		tab.pop()
		widget.remove(widget.get_children().pop())
	except:
		self.debug.show('List is empty')
	widget.show_all()

