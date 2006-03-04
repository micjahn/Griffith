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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import sys
import os
import string
import gtk
import widgets
import gutils
import gobject
import gettext

try:
	import gtkspell
	spell_support = 1
except:
	print "gtkspell support not available - please install python-gnome-extras"
	spell_support = 0

def locations(self):
	self.locations = {}
	self._ = None
	self.APP = "griffith"
	self.debug.show("running on %s" % os.name)
	if os.name == "win32" or os.name == "nt":
		self.windows = True
	else:
		self.windows = False
	self.posix = (os.name == "posix")
	self.locations['exec'] = os.path.abspath(os.path.dirname(sys.argv[0]))

	if os.name == 'nt' or os.name == 'win32':
		# default to My Documents
		import winshell
		mydocs = winshell.my_documents()
		griffith_dir = os.path.join(mydocs, 'griffith')
		
	else:
		griffith_dir = os.path.join(os.path.expanduser('~'), \
			'.griffith')
	try:
		if not os.path.exists(griffith_dir):
			self.debug.show('Creating %s' % griffith_dir)
			os.makedirs(griffith_dir)
		else:
			self.debug.show('Using Griffith directory: %s'%griffith_dir)
	except OSError:
		self.debug.show("Unable to create griffith directory.")
		raise
		sys.exit()

	if not os.access(griffith_dir, os.W_OK):
		self.debug.show('Cannot write to griffith directory, %s' % griffith_dir)
		sys.exit()
		
	if not os.path.exists(os.path.join(griffith_dir, "posters")):
		self.debug.show("Creating poster directory")
		os.makedirs(os.path.join(griffith_dir, "posters"))

	self.griffith_dir = griffith_dir

	if self.windows:
		#win32 platform, add the "lib" folder to the system path
		os.environ['PATH'] += ";lib;"
		self.locations['lib'] = "%s\\lib" % self.locations['exec']
		self.DIR = "%s\\i18n" % self.locations['exec']
		gtk.rc_parse('%s\\gtkrc' % self.locations['exec'])
		#some locations
		self.locations['movie_plugins'] = "%s\\lib\\plugins\\movie" % self.locations['exec']
		self.locations['export_plugins'] = "%s\\lib\\plugins\\export" % self.locations['exec']
		self.locations['images'] = "%s\\images" % self.locations['exec']
		self.locations['desktop'] = ""
	elif self.posix:
		self.locations['share'] = string.replace(self.locations['exec'], "/bin","/share/griffith")
		self.locations['lib'] = self.locations['share'] + "/lib"
		self.DIR = "/usr/share/locale"
		sys.path.append('/usr/share') # for debian
		#some locations
		self.locations['movie_plugins'] = self.locations['share'] + "/plugins/movie"
		self.locations['export_plugins'] = self.locations['share'] + "/plugins/export"
		self.locations['images'] = self.locations['share'] + "/images"
		self.locations['desktop'] = os.path.join(os.path.expanduser('~'), 'Desktop')
	else:
		print "Operating system not supported"
		sys.exit()		
				
	# includes plugins in system path for easier impor		
	sys.path.append(self.locations['lib'])
	sys.path.append(self.locations['movie_plugins'])
	sys.path.append(self.locations['export_plugins'])

	#socket.setdefaulttimeout(30)

	gettext.bindtextdomain(self.APP, self.DIR)
	gettext.textdomain(self.APP)
	self._ = gettext.gettext
	gtk.glade.bindtextdomain(self.APP, self.DIR)
	gtk.glade.textdomain(self.APP)
	
	# glade
	if self.windows:
		gf = '%s\glade\griffith.glade' % self.locations['exec']
	else:
		gf = self.locations['share'] + "/glade/griffith.glade"
	self.gladefile = gtk.glade.XML(gf)
	
	widgets.define_widgets(self, self.gladefile)
	self.pdf_reader = self.config.get('pdf_reader')
	
def toolbar(self):
	"""if toolbar is hide in config lets hide the widget"""
	if not self.config.get("view_toolbar"):
		self.toolbar.hide()
		self.menu_toolbar.set_active(False)
		
def treeview(self):
	self.treemodel = gtk.TreeStore(gtk.gdk.Pixbuf, str, gtk.gdk.Pixbuf, str, str, str)
	self.main_treeview.set_model(self.treemodel)
	self.main_treeview.set_headers_visible(True)
	# number column
	renderer=gtk.CellRendererText()
	column=gtk.TreeViewColumn(_("N."), renderer, text=1)
	column.set_resizable(True)
	column.set_sort_column_id(1)
	self.main_treeview.append_column(column)
	# pic column
	renderer=gtk.CellRendererPixbuf()
	self.image_column=gtk.TreeViewColumn(_("Image"), renderer, pixbuf=2)
	self.image_column.set_resizable(False)
	self.main_treeview.append_column(self.image_column)
	# original title column
	renderer=gtk.CellRendererText()
	self.otitle_column=gtk.TreeViewColumn(_("Original Title"), renderer, text=3)
	self.otitle_column.set_resizable(True)
	self.otitle_column.set_sort_column_id(3)
	self.main_treeview.append_column(self.otitle_column)
	# title column
	renderer=gtk.CellRendererText()
	self.title_column=gtk.TreeViewColumn(_("Title"), renderer, text=4)
	self.title_column.set_resizable(True)
	self.title_column.set_sort_column_id(4)
	self.main_treeview.append_column(self.title_column)
	# director column
	renderer=gtk.CellRendererText()
	self.director_column=gtk.TreeViewColumn(_("Director"), renderer, text=5)
	self.director_column.set_sort_column_id(5)
	self.director_column.set_resizable(True)
	self.main_treeview.append_column(self.director_column)
	# add data to treeview
	self.total = int(self.db.count_records('movies'))
	self.main_treeview.show()
	
def loans_treeview(self):
	self.loan_history.set_model(self.loans_treemodel)
	self.loan_history.set_headers_visible(True)
	# loan date
	renderer=gtk.CellRendererText()
	self.date_column=gtk.TreeViewColumn(_("Loan Date"), renderer, text=0)
	self.date_column.set_resizable(True)
	self.loan_history.append_column(self.date_column)
	self.date_column.set_sort_column_id(0)
	# return date
	renderer=gtk.CellRendererText()
	self.return_column=gtk.TreeViewColumn(_("Return Date"), renderer, text=1)
	self.return_column.set_resizable(True)
	self.loan_history.append_column(self.return_column)
	# loan to
	renderer=gtk.CellRendererText()
	self.loaner_column=gtk.TreeViewColumn(_("Loaned To"), renderer, text=2)
	self.loaner_column.set_resizable(True)
	self.loan_history.append_column(self.loaner_column)
	
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
		plugin_module = os.path.basename(p).replace(".py","")
		plugin_name = plugin_module.replace("PluginMovie","")
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
		plugin_module = os.path.basename(p).replace(".py", "")
		plugin_name = plugin_module.replace("PluginExport", "")
		menu_items = gtk.MenuItem(plugin_name)
		self.export_menu.append(menu_items)
		menu_items.connect("activate", self.on_export_activate, plugin_name)
		menu_items.show()
		
def people_treeview(self):
	row = None
	self.p_treemodel = gtk.TreeStore(gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING,
						gobject.TYPE_STRING)
	self.p_treeview.set_model(self.p_treemodel)
	self.p_treeview.set_headers_visible(True)

	# number column
	renderer=gtk.CellRendererText()
	column=gtk.TreeViewColumn(_("Name"), renderer, text=0)
	column.set_resizable(True)
	column.set_sort_column_id(0)
	self.p_treeview.append_column(column)
	# original title column
	renderer=gtk.CellRendererText()
	column=gtk.TreeViewColumn(_("E-mail"),renderer, text=1)
	column.set_resizable(True)
	column.set_sort_column_id(1)
	self.p_treeview.append_column(column)
	# add data to treeview
	data = self.db.get_all_data('people', 'name ASC')

	for row in data:
		myiter = self.p_treemodel.insert_before(None, None)
		self.p_treemodel.set_value(myiter, 0, str(row['name']))
		self.p_treemodel.set_value(myiter, 1, str(row['email']))
	
	self.p_treeview.show()
	
def combos(self):
	self.e_condition.insert_text(0, _("Damaged"))
	self.e_condition.insert_text(1, _("Poor"))
	self.e_condition.insert_text(2, _("Fair"))
	self.e_condition.insert_text(3, _("Good"))
	self.e_condition.insert_text(4, _("Excellent"))
	self.e_condition.insert_text(5, _("N/A"))
	
	self.p_condition.insert_text(0, _("Damaged"))
	self.p_condition.insert_text(1, _("Poor"))
	self.p_condition.insert_text(2, _("Fair"))
	self.p_condition.insert_text(3, _("Good"))
	self.p_condition.insert_text(4, _("Excellent"))
	self.p_condition.insert_text(5, _("N/A"))
	
	self.e_color.insert_text(0, _("Color"))
	self.e_color.insert_text(1, _("Black and White"))
	self.e_color.insert_text(2, _("Mixed"))
	self.e_color.insert_text(3, _("N/A"))
	
	self.p_color.insert_text(0, _("Color"))
	self.p_color.insert_text(1, _("Black and White"))
	self.p_color.insert_text(2, _("Mixed"))
	self.p_color.insert_text(3, _("N/A"))
	
	self.e_region.insert_text(0, _("Region 0 (No Region Coding)"))
	self.e_region.insert_text(1, _("Region 1 (United States of America, Canada)"))
	self.e_region.insert_text(2, _("Region 2 (Europe,including France, Greece, Turkey, Egypt, Arabia, Japan and South Africa)"))
	self.e_region.insert_text(3, _("Region 3 (Korea, Thailand, Vietnam, Borneo and Indonesia)"))	
	self.e_region.insert_text(4, _("Region 4 (Australia and New Zealand, Mexico, the Caribbean, and South America)"))
	self.e_region.insert_text(5, _("Region 5 (India, Africa, Russia and former USSR countries)"))
	self.e_region.insert_text(6, _("Region 6 (Popular Republic of China)"))
	self.e_region.insert_text(7, _("Region 8 (Airlines/Cruise Ships)"))
	self.e_region.insert_text(8, _("Region 9 (Often used as region free)"))
	self.e_region.insert_text(9, _("N/A"))
	
	self.p_region.insert_text(0, _("Region 0 (No Region Coding)"))
	self.p_region.insert_text(1, _("Region 1 (United States of America, Canada)"))
	self.p_region.insert_text(2, _("Region 2 (Europe,including France, Greece, Turkey, Egypt, Arabia, Japan and South Africa)"))
	self.p_region.insert_text(3, _("Region 3 (Korea, Thailand, Vietnam, Borneo and Indonesia)"))	
	self.p_region.insert_text(4, _("Region 4 (Australia and New Zealand, Mexico, the Caribbean, and South America)"))
	self.p_region.insert_text(5, _("Region 5 (India, Africa, Russia and former USSR countries)"))
	self.p_region.insert_text(6, _("Region 6 (Popular Republic of China)"))
	self.p_region.insert_text(7, _("Region 8 (Airlines/Cruise Ships)"))
	self.p_region.insert_text(8, _("Region 9 (Often used as region free)"))
	self.p_region.insert_text(9, _("N/A"))
	
	self.e_layers.insert_text(0, _("Single Side, Single Layer"))
	self.e_layers.insert_text(1, _("Single Side, Dual Layer"))
	self.e_layers.insert_text(2, _("Dual Side, Single Layer"))
	self.e_layers.insert_text(3, _("Dual Side, Dual Layer"))
	self.e_layers.insert_text(4, _("N/A"))
	
	self.p_layers.insert_text(0, _("Single Side, Single Layer"))
	self.p_layers.insert_text(1, _("Single Side, Dual Layer"))
	self.p_layers.insert_text(2, _("Dual Side, Single Layer"))
	self.p_layers.insert_text(3, _("Dual Side, Dual Layer"))
	self.p_layers.insert_text(4, _("N/A"))
	
	self.am_condition.insert_text(0, _("Damaged"))
	self.am_condition.insert_text(1, _("Poor"))
	self.am_condition.insert_text(2, _("Fair"))
	self.am_condition.insert_text(3, _("Good"))
	self.am_condition.insert_text(4, _("Excellent"))
	self.am_condition.insert_text(5, _("N/A"))
	
	self.am_color.insert_text(0, _("Color"))
	self.am_color.insert_text(1, _("Black and White"))
	self.am_color.insert_text(2, _("Mixed"))
	self.am_color.insert_text(3, _("N/A"))
	
	self.am_region.insert_text(0, _("Region 0 (No Region Coding)"))
	self.am_region.insert_text(1, _("Region 1 (United States of America, Canada)"))
	self.am_region.insert_text(2, _("Region 2 (Europe,including France, Greece, Turkey, Egypt, Arabia, Japan and South Africa)"))
	self.am_region.insert_text(3, _("Region 3 (Korea, Thailand, Vietnam, Borneo and Indonesia)"))	
	self.am_region.insert_text(4, _("Region 4 (Australia and New Zealand, Mexico, the Caribbean, and South America)"))
	self.am_region.insert_text(5, _("Region 5 (India, Africa, Russia and former USSR countries)"))
	self.am_region.insert_text(6, _("Region 6 (Popular Republic of China)"))
	self.am_region.insert_text(7, _("Region 8 (Airlines/Cruise Ships)"))
	self.am_region.insert_text(8, _("Region 9 (Often used as region free)"))
	self.am_region.insert_text(9, _("N/A"))
	
	self.am_layers.insert_text(0, _("Single Side, Single Layer"))
	self.am_layers.insert_text(1, _("Single Side, Dual Layer"))
	self.am_layers.insert_text(2, _("Dual Side, Single Layer"))
	self.am_layers.insert_text(3, _("Dual Side, Dual Layer"))
	self.am_layers.insert_text(4, _("N/A"))
	
	media = self.db.get_all_data(table_name="media", order_by="id ASC")
	for i in media:
		self.e_media.insert_text(i['id'], i['name'])
		self.p_media.insert_text(i['id'], i['name'])
		self.am_media.insert_text(i['id'], i['name'])
		
	self.e_tags = {} # dictionary for tag CheckBoxes
	self.am_tags = {} # dictionary for tag CheckBoxes
	import update
	update.update_language_ids(self)
	update.update_tag_ids(self)
	update.update_volume_combo_ids(self)
	update.update_collection_combo_ids(self)
	
	import initialize
	initialize.fill_volumes_combo(self)
	initialize.fill_collections_combo(self)
	initialize.fill_preferences_languages_combo(self)
	initialize.fill_preferences_tags_combo(self)
	initialize.create_tag_vbox(self, widget=self.e_tag_vbox, tab=self.e_tags)
	initialize.create_tag_vbox(self, widget=self.am_tag_vbox, tab=self.am_tags)
	
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
					self.obs_spell = gtkspell.Spell(self.e_obs, self.config.get('spell_lang'))
				except:
					spell_error = True
			if self.config.get('spell_plot', True)=='True' and \
				self.config.get('spell_lang')!='':		
				try:
					self.plot_spell = gtkspell.Spell(self.e_plot, self.config.get('spell_lang'))
				except:
					spell_error = True
			if spell_error:
				gutils.info(self, _("Dictionary not available. Spellcheck will be disabled. \n" + \
					"Please install the aspell-%s package or adjust the spellchekcer preferences.")%self.config.get('spell_lang'), \
					self.w_preferences)
	else:
		self.debug.show("Spellchecker is not available")


def fill_volumes_combo(self, prefix='e', default=0):
	self.am_volume_combo.get_model().clear()
	self.e_volume_combo.get_model().clear()
	for i in self.volume_combo_ids:
		id = self.volume_combo_ids[i]
		name = self.db.get_value(field='name', table_name="volumes", where="id='%s'"%id)
		self.am_volume_combo.insert_text(int(i), str(name))
		self.e_volume_combo.insert_text(int(i), str(name))
	self.am_volume_combo.show_all()
	self.e_volume_combo.show_all()
	i = gutils.findKey(default, self.volume_combo_ids)
	if prefix == 'e':
		self.e_volume_combo.set_active(int(default))
		self.am_volume_combo.set_active(0)
	else:
		self.am_volume_combo.set_active(int(i))

def fill_collections_combo(self, prefix='e', default=0):
	self.am_collection_combo.get_model().clear()
	self.e_collection_combo.get_model().clear()
	self.f_col.get_model().clear()
	for i in self.collection_combo_ids:
		id = self.collection_combo_ids[i]
		name = self.db.get_value(field='name', table_name="collections", where="id='%s'"%id)
		self.am_collection_combo.insert_text(int(i), str(name))
		self.e_collection_combo.insert_text(int(i), str(name))
		self.f_col.insert_text(int(i), str(name))
	self.am_collection_combo.show_all()
	self.e_collection_combo.show_all()
	self.f_col.show_all()
	self.f_col.set_active(0)
	i = gutils.findKey(default, self.collection_combo_ids)
	if prefix == 'e':
		self.e_collection_combo.set_active(int(i))
		self.am_collection_combo.set_active(0)
	else:
		self.am_collection_combo.set_active(int(i))

def fill_preferences_languages_combo(self):
	self.lang_name_combo.get_model().clear()
	for i in self.languages_ids.keys():
		id = self.languages_ids[i]
		name = self.db.get_value(field='name', table_name="languages", where="id='%s'"%id)
		self.lang_name_combo.insert_text(int(i), str(name))
	self.lang_name_combo.show_all()

def fill_preferences_tags_combo(self):
	self.tag_name_combo.get_model().clear()
	for i in self.tags_ids.keys():
		id = self.tags_ids[i]
		name = self.db.get_value(field='name', table_name="tags", where="id='%s'"%id)
		self.tag_name_combo.insert_text(int(i), str(name))
	self.tag_name_combo.show_all()

def fill_language_combo(self, widget, default=None):
	try:
		widget.get_model().clear()
	except:
		pass
	for i in self.languages_ids:
		id = self.languages_ids[i]
		name = self.db.get_value(field='name', table_name="languages", where="id='%s'"%id)
		widget.insert_text(int(i), str(name))
	if default != None and default!=0:
		i = gutils.findKey(default, self.languages_ids)
		widget.set_active(int(i))

def create_language_hbox(self, widget, tab, default=None, type=None):
	if len(self.languages_ids) == 1:
		if len(widget.get_children()) == 0:
			widget.add(gtk.Label(_('You have to fill in languages list in preferences window')))
	else:
		from initialize import fill_language_combo
		number = len(widget.get_children())	# new box number
		tab.append({})				# creates new tab[number][]
		box = gtk.HBox(spacing=2)
		tab[number]['id'] = gtk.combo_box_new_text()
		fill_language_combo(self, widget=tab[number]['id'], default=default)
		tab[number]['type'] = gtk.combo_box_new_text()
		tab[number]['type'].insert_text(0, '')
		tab[number]['type'].insert_text(1, _("lector"))
		tab[number]['type'].insert_text(2, _("dubbing"))
		tab[number]['type'].insert_text(3, _("subtitles"))
		if type != None:
			tab[number]['type'].set_active(type)
		else:
			tab[number]['type'].set_active(0)
		box.add(tab[number]['id'])
		box.add(tab[number]['type'])
		widget.pack_start(box, expand=False, fill=False, padding=1)
	widget.show_all()

def create_tag_vbox(self, widget, tab):
	for i in widget.get_children():
		i.destroy()
	for i in self.tags_ids:
		tag_id = self.tags_ids[i]
		tag_name = self.db.get_value(field='name', table_name="tags", where="id='%s'"%tag_id)
		tab[i] = gtk.CheckButton(tag_name)
		tab[i].set_active(False)
		widget.pack_start(tab[i])
	widget.show_all()

def remove_hbox(self, widget, tab):
	number = len(widget.get_children())-1	# last box number
	try:
		tab.pop()
		widget.remove(widget.get_children().pop())
	except:
		self.debug.show("List is empty")
	widget.show_all()

