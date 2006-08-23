# -*- coding: UTF-8 -*-
# vim: fdm=marker

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

import os
import sys
import gtk, gtk.glade
import gutils
import glob, shutil
import version
import math
from xml.dom import minidom
from gettext import gettext as _

plugin_name         = 'HTML'
plugin_description  = _('Plugin exports data using templates')
plugin_author       = 'Piotr Ozarowski'
plugin_author_email = 'ozarow@gmail.com'
plugin_version      = '3.6'

class ExportPlugin(gtk.Window):
	#==[ configuration - default values ]==========={{{
	config = {
		'sorting'           : 'title',
		'sorting2'          : 'ASC',
		'exported_dir'      : 'griffith_movies',
		'template'          : 0,
		'title'             : _("Griffith's movies list"),
		'style'             : 0,
		'custom_style'      : False,
		'custom_style_file' : None,
		'split_num'         : 50,		# split into x files/pages
		'split_by'          : 1,		# 0==files, 1==movies
		'seen_only'         : 0,		# 0==all movies; 1==seen only;   2==unseen only
		'loaned_only'       : 0,		# 0==all movies; 1==loaned only; 2==not loaned only
		'poster_convert'    : False,		# dont convert
		'poster_height'     : 200,
		'poster_width'      : 150,
		'poster_mode'       : 'RGB',		# RGB == color, L == black and white
		'poster_format'     : 'jpg'
	}
	fields = {
		'actors'         : False,
		'classification' : False,
		'country'        : True,
		'genre'          : True,
		'director'       : True,
		'image'          : True,
		'o_site'         : True,
		'site'           : True,
		'trailer'        : True,
		'loaned'         : False,
		'medium_id'      : True,
		'number'         : True,
		'o_title'        : True,
		'plot'           : False,
		'rating'         : True,
		'runtime'        : True,
		'studio'         : False,
		'seen'           : True,
		'title'          : True,
		'year'           : True,
		'notes'            : False,
#		'region'         : False,
#		'layers'         : False,
#		'condition'      : False,
#		'color'          : False,
#		'volume_id'      : False,
#		'collection_id'  : False,
	}
	
	names = {
		_('Actors')         : 'actors',
		_('Classification') : 'classification',
		_('Country')        : 'country',
		_('Director')       : 'director',
		_('Genre')          : 'genre',
		_('Image')          : 'image',
		_('Official site')  : 'o_site',
		_('IMDb page')      : 'site',
		_('Trailer')        : 'trailer',
		_('Loaned')         : 'loaned',
		_('Media')          : 'medium_id',
		_('Number')         : 'number',
		_('Original Title') : 'o_title',
		_('Plot')           : 'plot',
		_('Rating')         : 'rating',
		_('Runtime')        : 'runtime',
		_('Studio')         : 'studio',
		_('Seen it')        : 'seen',
		_('Title')          : 'title',
		_('Year')           : 'year',
		_('Notes')          : 'notes',
#		_('Region')         : 'region',
#		_('Layers')         : 'layers',
#		_('Condition')      : 'condition',
#		_('Color')          : 'color',
#		_('Volume')         : 'volume_id',
#		_('Collection')     : 'collection_id',
	}
	#}}}

	def __init__(self, database, locations, parent, debug):#{{{
		self.db = database
		self.debug = debug
		self.share_dir = locations['share']
		self.widgets = {}
		self.style_list = {}
		self.templates = self.make_template_list()
		# glade
		gf = os.path.join(locations['glade'], 'exporthtml.glade')
		self.define_widgets(gtk.glade.XML(gf))
		self.fill_widgets()
	#}}}

	def get_node_value_by_language(self, parent, name, language="en"):#{{{
		nodes = parent.getElementsByTagName(name)
		for node in nodes:
			if node.parentNode != parent:
				continue
			elif node.attributes.get('xml:lang') is not None:
				if node.attributes.get('xml:lang').value == language:
					return node.firstChild.nodeValue
			else:	# if node has no xml:lang attribute - it must be default value
				value = node.firstChild.nodeValue
		return value
	#}}}		
		
	def make_template_list(self):#{{{
		language = 'en'
		if os.environ.has_key('LANG'):
			language = os.environ['LANG'][:2]
		templates = {}
		j=0 # number of templates
		dir = os.path.join(self.share_dir, 'export_templates')
		for i in os.listdir(dir):
			fileName = os.path.join(dir, i)
			if not os.path.islink(fileName) and os.path.isdir(fileName):
				# delete previous values
				doc = None; styles = {};
				tpl_name=None; tpl_author=None; tpl_email=None; tpl_version=None; tpl_ext=None; tpl_desc=None
				try:
					doc = minidom.parse(os.path.join(fileName, 'config.xml'))
				except:
					self.debug.show("Can't parse configuration file for template: %s"%fileName)
					continue
				for template in doc.getElementsByTagName('template'):
					tpl_name    = self.get_node_value_by_language(template, 'name', language)
					tpl_author  = template.getElementsByTagName('author')[0].firstChild.nodeValue
					tpl_email   = template.getElementsByTagName('email')[0].firstChild.nodeValue
					tpl_version = template.getElementsByTagName('version')[0].firstChild.nodeValue
					tpl_ext     = template.getElementsByTagName('extension')[0].firstChild.nodeValue
					tpl_desc    = self.get_node_value_by_language(template, 'description', language)
					k=0	# number of styles
					try:
						styles_list = template.getElementsByTagName('styles')[0].getElementsByTagName('style')
						for style in styles_list:
							tpl_style_name = self.get_node_value_by_language( style, 'name', language )
							tpl_style_file = style.getElementsByTagName('file')[0].firstChild.nodeValue
							# get preview if available
							try:
								tpl_style_preview = style.getElementsByTagName('preview')[0].firstChild.nodeValue
							except:
								tpl_style_preview = None
							styles[k] = {
								'name': tpl_style_name,
								'file': tpl_style_file,
								'preview': tpl_style_preview
							}
							k=k+1
					except:
						styles = None
				if tpl_name=='':
					continue
				templates[j]= {
					'dir'     : i,
					'name'    : tpl_name,
					'author'  : tpl_author,
					'email'   : tpl_email,
					'version' : tpl_version,
					'ext'     : tpl_ext,
					'desc'    : tpl_desc,
					'styles'  : styles
				}
				j=j+1
		return templates
	#}}}

	#==[ widgets ]=================================={{{
	def define_widgets(self, glade_file):
		# main window
		self.widgets['w_eh']                  = glade_file.get_widget('w_eh')
		self.widgets['fcw']                   = glade_file.get_widget('fcw')
		self.widgets['box_include_1']         = glade_file.get_widget('box_include_1')
		self.widgets['box_include_2']         = glade_file.get_widget('box_include_2')
		self.widgets['box_include_3']         = glade_file.get_widget('box_include_3')
		self.widgets['sb_split_num']          = glade_file.get_widget('sb_split_num')
		self.widgets['rb_split_files']        = glade_file.get_widget('rb_split_files')
		self.widgets['rb_split_movies']       = glade_file.get_widget('rb_split_movies')
		self.widgets['rb_seen']               = glade_file.get_widget('rb_seen')
		self.widgets['rb_seen_only']          = glade_file.get_widget('rb_seen_only')
		self.widgets['rb_seen_only_n']        = glade_file.get_widget('rb_seen_only_n')
		self.widgets['rb_loaned']             = glade_file.get_widget('rb_loaned')
		self.widgets['rb_loaned_only']        = glade_file.get_widget('rb_loaned_only')
		self.widgets['rb_loaned_only_n']      = glade_file.get_widget('rb_loaned_only_n')
		self.widgets['entry_header']          = glade_file.get_widget('entry_header')
		self.widgets['cb_custom_style']       = glade_file.get_widget('cb_custom_style')
		self.widgets['cb_reverse']            = glade_file.get_widget('cb_reverse')
		self.widgets['combo_style']           = glade_file.get_widget('combo_style')
		self.widgets['combo_sortby']          = glade_file.get_widget('combo_sortby')
		self.widgets['combo_theme']           = glade_file.get_widget('combo_theme')
		self.widgets['fcb_custom_style_file'] = glade_file.get_widget('fcb_custom_style_file')
		self.widgets['l_tpl_author']          = glade_file.get_widget('l_tpl_author')
		self.widgets['l_tpl_email']           = glade_file.get_widget('l_tpl_email')
		self.widgets['l_tpl_version']         = glade_file.get_widget('l_tpl_version')
		self.widgets['l_tpl_desc']            = glade_file.get_widget('l_tpl_desc')
		self.widgets['image_preview']         = glade_file.get_widget('image_preview')
		self.widgets['vb_posters']            = glade_file.get_widget('vb_posters')
		self.widgets['sb_height']             = glade_file.get_widget('sb_height')
		self.widgets['sb_width']              = glade_file.get_widget('sb_width')
		self.widgets['cb_black']              = glade_file.get_widget('cb_black')
		self.widgets['combo_format']          = glade_file.get_widget('combo_format')

		# define handlers for general events
		dic = {
			'on_export_button_clicked'           : self.export_data,
			'on_rb_split_files_toggled'          : self.on_rb_split_files_toggled,
			'on_rb_split_movies_toggled'         : self.on_rb_split_movies_toggled,
			'on_rb_seen_toggled'                 : self.on_rb_seen_toggled,
			'on_rb_seen_only_toggled'            : self.on_rb_seen_only_toggled,
			'on_rb_seen_only_n_toggled'          : self.on_rb_seen_only_n_toggled,
			'on_rb_loaned_toggled'               : self.on_rb_loaned_toggled,
			'on_rb_loaned_only_toggled'          : self.on_rb_loaned_only_toggled,
			'on_rb_loaned_only_n_toggled'        : self.on_rb_loaned_only_n_toggled,
			'on_cancel_button_clicked'           : self.on_quit,
			'on_cb_data_toggled'                 : self.on_cb_data_toggled,
			'on_cb_custom_style_toggled'         : self.on_cb_custom_style_toggled,
			'on_fcb_custom_style_file_activated' : self.on_fcb_custom_style_file_activated,
			'on_combo_style_changed'             : self.on_combo_style_changed,
			'on_combo_theme_changed'             : self.on_combo_theme_changed,
			'on_cb_convert_toggled'              : self.on_cb_convert_toggled,
		}
		glade_file.signal_autoconnect(dic)

	def fill_widgets(self):
		# themes
		#self.combo_theme = {}	# to recognize entry later
		for i in self.templates:
			self.widgets['combo_theme'].insert_text(i, self.templates[i]['name'])	# template name

		# sortby combo
		for i in self.names:
			self.widgets['combo_sortby'].append_text(i)
		self.widgets['combo_sortby'].set_wrap_width(3)

		# include data
		j = 0
		k = math.ceil( len(self.names) / float(3) )
		for i in self.names:
			j = j + 1
			field = self.names[i]
			self.widgets['cb_'+field] = gtk.CheckButton(i)
			self.widgets['cb_'+field].set_name('cb_'+field)
			self.widgets['cb_'+field].connect("toggled", self.on_cb_data_toggled)
			self.widgets['cb_'+field].set_active(self.fields[field])
			if j <= k:
				self.widgets['box_include_1'].add(self.widgets['cb_'+field])
			elif j<= 2*k:
				self.widgets['box_include_2'].add(self.widgets['cb_'+field])
			else:
				self.widgets['box_include_3'].add(self.widgets['cb_'+field])
		self.widgets['box_include_1'].show_all()
		self.widgets['box_include_2'].show_all()
		self.widgets['box_include_3'].show_all()

		# set defaults --------------------------------
		self.widgets['entry_header'].set_text(self.config['title'])
		self.widgets['combo_theme'].set_active(3)	# html_tables
		self.widgets['combo_sortby'].set_active(17)	# orginal title
		# spliting
		self.widgets['sb_split_num'].set_value(self.config['split_num'])
		if self.config['split_by'] == 0:
			self.widgets['rb_split_files'].set_active(True)
		else:
			self.widgets['rb_split_movies'].set_active(True)
		# limiting
		if self.config['seen_only'] == 2:
			self.widgets['rb_seen_only_n'].set_active(True)
		elif self.config['seen_only'] == 1:
			self.widgets['rb_seen_only'].set_active(True)
		else:
			self.widgets['rb_seen'].set_active(True)
		if self.config['loaned_only'] == 2:
			self.widgets['rb_loaned_only_n'].set_active(True)
		elif self.config['loaned_only'] == 1:
			self.widgets['rb_loaned_only'].set_active(True)
		else:
			self.widgets['rb_loaned'].set_active(True)
		# posters
		self.widgets['combo_format'].set_active(0)
		if self.config['poster_convert']:
			self.widgets['vb_posters'].set_sensitive(True)
		else:
			self.widgets['vb_posters'].set_sensitive(False)
	#}}}

	#==[ callbacks ]================================{{{
	# buttons:
	def on_quit(self, widget=None):
		self.widgets['w_eh'].destroy()

	# data tab -------------------------------------#{{{
	def on_rb_split_files_toggled(self, widget):
		self.config['split_by'] = 0	# files

	def on_rb_split_movies_toggled(self, widget):
		self.config['split_by'] = 1	# movies
	
	# export frame
	def on_cb_data_toggled(self, widget):
		self.fields[gutils.after(widget.get_name(), 'cb_')] = widget.get_active()

	# limit frame
	def on_rb_seen_toggled(self, widget):
		if widget.get_active():
			self.config['seen_only'] = 0	# export all movies

	def on_rb_seen_only_toggled(self, widget):
		if widget.get_active():
			self.config['seen_only'] = 1	# export only seen movies
	
	def on_rb_seen_only_n_toggled(self, widget):
		if widget.get_active():
			self.config['seen_only'] = 2	# export only unseen movies
	
	def on_rb_loaned_toggled(self, widget):
		if widget.get_active():
			self.config['loaned_only'] = 0	# export all movies

	def on_rb_loaned_only_toggled(self, widget):
		if widget.get_active():
			self.config['loaned_only'] = 1	# export only loaned movies
	
	def on_rb_loaned_only_n_toggled(self, widget):
		if widget.get_active():
			self.config['loaned_only'] = 2	# export only not loaned movies
	
	# posters frame
	def on_cb_convert_toggled(self, widget):
		active = widget.get_active()
		self.config['poster_convert'] = active
		if not active:
			self.widgets['vb_posters'].set_sensitive(False)
		else:
			self.widgets['vb_posters'].set_sensitive(True)
	#}}}

	# template tab ---------------------------------#{{{
	def on_combo_theme_changed(self, widget):
		old_id = self.config['template']
		tpl_id = widget.get_active()
		self.config['template'] = tpl_id
		# fill authors data
		self.widgets['l_tpl_author'].set_markup('<i>'+self.templates[tpl_id]['author']+'</i>')
		self.widgets['l_tpl_email'].set_markup('<i>'+self.templates[tpl_id]['email']+'</i>')
		self.widgets['l_tpl_email'].set_selectable(True)
		self.widgets['l_tpl_version'].set_markup('<i>'+self.templates[tpl_id]['version']+'</i>')
		self.widgets['l_tpl_desc'].set_markup('<i>'+self.templates[tpl_id]['desc']+'</i>')
		# remove old style list
		self.widgets['combo_style'].get_model().clear()
		# ... and add new
		if self.templates[tpl_id]['styles'] != None:
			for i in self.templates[tpl_id]['styles']:
				self.widgets['combo_style'].insert_text(i, self.templates[tpl_id]['styles'][i]['name'])	# template name
			self.widgets['combo_style'].set_active(0)
		else:
			self.config['style'] = None
			self.widgets['image_preview'].set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_LARGE_TOOLBAR)

	def on_combo_style_changed(self, widget):
		self.config['style'] = widget.get_active()
		self.widgets['cb_custom_style'].set_active(False)

		tpl_id = self.config['template']
		template_dir = os.path.join(self.share_dir, 'export_templates', self.templates[tpl_id]['dir'])
		preview_file = self.templates[self.config['template']]['styles'][self.config['style']]['preview']
		if preview_file != None:
			preview_file = os.path.join(template_dir, preview_file)
		if preview_file != None and not os.path.isfile(preview_file):
			preview_file = os.path.join(template_dir, 'preview.jpg')	# try default preview image
			if not os.path.isfile(preview_file):
				preview_file = None
		if preview_file != None:
			self.widgets['image_preview'].set_from_file(preview_file)
		else:
			self.widgets['image_preview'].set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_LARGE_TOOLBAR)
		self.widgets['image_preview'].show()

	def on_cb_custom_style_toggled(self, widget):
		if widget.get_active():
			self.config['custom_style'] = True
			self.widgets['image_preview'].hide()
		else:
			self.config['custom_style'] = False
			self.widgets['image_preview'].show()

	def on_fcb_custom_style_file_activated(self, widget):
		self.config['custom_style_file'] = widget.get_filename()
		self.widgets['cb_custom_style'].set_active(True)
	#}}}
	#}}}

	def make_navigation(self, pages, current):#{{{
		if pages > 1:				# navigation needed
			tpl_id = self.config['template']
			t = '<div class="navi">\n\t<p id="prev">'
			if current > 1:
				t +='<a href="./page_' + str(current-1) + '.' + \
					self.templates[tpl_id]['ext'] + '">' + _('previous') + '</a>'
			else:				# first page
				t += _('previous')
			t += '</p>\n'
			for i in range(1, pages+1):
				if i == current:
					t +='\t<p id="current">' + str(i) + '</p>\n'
				else:
					t +='\t<p><a href="./page_' + str(i) + '.' + \
						self.templates[tpl_id]['ext'] + '">' + str(i) + '</a></p>\n'
			t += '\t<p id="next">'
			if pages > current:
				t +='<a href="./page_' + str(current+1) + '.' + \
						self.templates[tpl_id]['ext'] + '">' + _('next') + '</a>'
			else:				# last page
				t += _('next')
			t +='</p>\n</div>'
			return t
		else:
			return ''
	#}}}

	def fill_template(self, template, field, data='', title='', remove=False):	#{{{
		start = template.find('<@'+ field +'>')
		end = template.find('</@'+ field +'>', start+1)
		if start > -1 and end > -1:
			if remove == True:
				return template[:start] + template[end+4+len(field):]
			else:
				tmp = gutils.trim(template,'<@'+field+'>', '</@'+field+'>')
				tmp = tmp.replace("@DATA@", data)
				tmp = tmp.replace("@TITLE@", title)
				tmp = template[:start] + tmp + template[end+4+len(field):]
				if tmp.find('<@'+ field +'>') != -1:
					tmp = self.fill_template(tmp, field, data, title, remove)
				return tmp
		else:
			return template
	#}}}

	def select(self):	#{{{
		from sqlalchemy import select
		config = self.config
		
		# columns to select
		columns = []
		for i in self.fields:
			columns.append(self.db.Movie.c[i])
		
		# sort order	TODO: more than one sort column
		sort_columns = []
		if config['sorting2'] == 'ASC':
			from sqlalchemy import asc
			sort_columns.append(asc(self.db.Movie.c[config['sorting']]))
		elif config['sorting2'] == 'DESC':
			from sqlalchemy import desc
			sort_columns.append(desc(self.db.Movie.c[config['sorting']]))

		statement = select(columns=columns, order_by=sort_columns)

		# where clause
		if config['seen_only'] == 1:
				statement.append_whereclause(self.db.Movie.c.seen==True)
		elif config['seen_only'] == 2:
				statement.append_whereclause(self.db.Movie.c.seen!=True)
		if config['loaned_only'] == 1:
				statement.append_whereclause(self.db.Movie.c.loaned==True)
		elif config['loaned_only'] == 2:
				statement.append_whereclause(self.db.Movie.c.loaned!=True)
		
		return statement.execute()
	#}}}

	#==[ main function ]============================{{{
	def export_data(self, widget):
		'''Main exporting function'''

		config = self.config
		fields = self.fields
		tid = config['template']
		
		# get data from widgets
		self.config['exported_dir'] = self.widgets['fcw'].get_filename()
		self.config['title']        = self.widgets['entry_header'].get_text()
		self.config['sorting']      = self.names[self.widgets['combo_sortby'].get_active_text()]
		if self.widgets['cb_reverse'].get_active():
			self.config['sorting2'] = 'DESC'
		else:
			self.config['sorting2'] = 'ASC'
		self.config['split_num']     = self.widgets['sb_split_num'].get_value_as_int()
		self.config['poster_height'] = self.widgets['sb_height'].get_value_as_int()
		self.config['poster_width']  = self.widgets['sb_width'].get_value_as_int()
		if self.widgets['cb_black'].get_active():
			self.config['poster_mode'] = 'L'
		else:
			self.config['poster_mode'] = 'RGB'
		self.config['poster_format'] = self.widgets['combo_format'].get_active_text()

		# create directories
		if not config['exported_dir']:
			self.debug.show("Error: Folder name not set!")
			return 1
		
		if not os.path.isdir(config['exported_dir']):
			try:
				os.mkdir(config['exported_dir'])
			except:
				gutils.error(self,_("Can't create %s!") % config['exported_dir'])
				return 2

		if fields['image']:
			# import modules needed later
			import gglobals
			if config['poster_convert']:
				from PIL import Image
				# py2exe problem workaround:
				# if self.windows:
				from PIL import PngImagePlugin
				from PIL import GifImagePlugin
				from PIL import JpegImagePlugin
				Image._initialized=2
				# end if
			else:
				config['poster_format'] = 'jpg' # replace 'jpeg'
			
			posters_dir = os.path.join(config['exported_dir'], 'posters')
			if os.path.isdir(posters_dir):
				if gutils.question(self, _("Directory %s already exists.\nDo you want to overwrite it?") % posters_dir,1,self) == gtk.RESPONSE_YES:
					try:
						shutil.rmtree(posters_dir)
					except:
						gutils.error(self,_("Can't remove %s!") % config['exported_dir'])
						return 3
				else:
					return 4
			try:
				os.mkdir(posters_dir)
			except:
				gutils.error(self,_("Can't create %s!") % posters_dir)
				return 5

		if config['custom_style']:
			if config['custom_style_file']!=None and os.path.isfile(config['custom_style_file']):
				try:
					shutil.copy(config['custom_style_file'],config['exported_dir'])
				except:
					gutils.warning(self,_("Can't copy %s!")%style_file)
					config['custom_style'] = False
				style = os.path.split(self.config['custom_style_file'])[1]
			else:
				config['custom_style'] = False


		if config['style'] != None and config['custom_style']==False:
			style = self.templates[tid]['styles'][config['style']]['file']
			style_path = os.path.join(self.share_dir, 'export_templates', self.templates[tid]['dir'], style)
			try:
				shutil.copy(style_path,config['exported_dir'])
			except:
				gutils.warning(self,_("Can't copy %s!")%style_path)

		# select exported movies
		exported_movies = self.select().fetchall()
		number_of_exported_movies = len(exported_movies)

		if config['split_by'] == 1:	# split by number of movies per page
			self.entries_per_page = config['split_num']
		else:				# split by number of pagess
			if number_of_exported_movies < config['split_num']:
				self.entries_per_page = 1
			else:
				self.entries_per_page = int(number_of_exported_movies / config['split_num'])

		# calculate number of files to be created (pages)
		self.pages = int(math.ceil(float(number_of_exported_movies) / self.entries_per_page))

		template_dir = os.path.join(self.share_dir, 'export_templates', self.templates[tid]['dir'])
		try:
			filename = 'page.tpl'
			tpl_header = file(os.path.join(template_dir,filename), "r").read()
		except:
			gutils.error(self,_("Can't open %s!")%filename)
			return False

		tpl_header = self.fill_template(tpl_header, 'header', config['title'])
		try:
			tpl_header = self.fill_template(tpl_header, 'style', style)
		except:
			pass
		tmp = _('Document generated by Griffith v') + version.pversion + \
				' - Copyright (C) ' + version.pyear + ' ' + version.pauthor + ' - ' + \
				_('Released Under the GNU/GPL License')
		tmp = tmp.replace('<', '&lt;')
		tmp = tmp.replace('>', '&gt;')
		tmp = tmp.replace('@', ' at ')	# prevent spam
		tmp.encode('utf-8')
		tpl_header = self.fill_template(tpl_header, 'copyright', tmp)
		tmp = None
		
		tpl_header = self.fill_template(tpl_header, 'pages', self.pages)
		
		# count exported fields
		rowspan = 0
		for i in fields:
			if fields[i] == True:
				rowspan = rowspan + 1
		rowspan = str(rowspan)
		tpl_header = self.fill_template(tpl_header, 'rowspan', rowspan)

		# split template
		tpl_tail = gutils.after(tpl_header, '<!-- /ITEMS -->')
		tpl_item = gutils.trim(tpl_header, '<!-- ITEMS -->','<!-- /ITEMS -->')
		tpl_header = gutils.before(tpl_header, '<!-- ITEMS -->')

		# fill header
		for j in self.names:
			if self.fields[self.names[j]] == True:
				tpl_header = self.fill_template(tpl_header, self.names[j], '', j)
			else:
				tpl_header = self.fill_template(tpl_header, self.names[j], remove=True)

		item=1	# item's position on page (1 - first, ...)
		i = 1
		page=1	# page number
		for row in exported_movies:	# fill items {{{
			# check if new file has to be created
			if item==1:
				filename = os.path.join(config['exported_dir'],'page_%s.' % page + self.templates[tid]['ext'])
				try:
					exported_file = file(filename, 'w')
				except:
					gutils.error(self,_("Can't create %s!")%filename)
					return False
				tmp2 = tpl_header + ''
				exported_file.write(self.fill_template(tmp2, 'page', str(page)))
				tmp2 = None

			# ---------------------------------------------
			tmp = tpl_item + '' # a copy (not referennce!)
			tmp = self.fill_template(tmp, 'id', str(item))
			tmp = self.fill_template(tmp, 'item', str(i))
			for j in self.names:
				if self.fields[self.names[j]] == True:
					if self.names[j] == 'image':
						if row['image']:
							image = row['image'] + '.' + config['poster_format'].lower()
							tmp = self.fill_template(tmp, self.names[j], image, j)
						else:
							tmp = self.fill_template(tmp, self.names[j], '', j)
					elif row[self.names[j]] is None:
						tmp = self.fill_template(tmp, self.names[j], '', j)
					elif row[self.names[j]] is True:
						tmp = self.fill_template(tmp, self.names[j], _('Yes'), j)
					elif row[self.names[j]] is False:
						tmp = self.fill_template(tmp, self.names[j], _('No'), j)
					else:
						try:
							tmp = self.fill_template(tmp, self.names[j], str(row[self.names[j]]).encode('utf-8'), j)
						except UnicodeDecodeError:
							self.debug.show("Unicode Decode Error occurred while decoding %s (movie number: %s)" % (self.names[j], row['number']))
							tmp = self.fill_template(tmp, self.names[j], str(row[self.names[j]]), j)
						except Exception, ex:
							self.debug.show("Error occurred while decoding %s (movie number: %s)" % (self.names[j], row['number']))
				else:
					tmp = self.fill_template(tmp, self.names[j], remove=True)
				tmp = gutils.convert_entities(tmp)
			exported_file.write(tmp)
			tmp = None
			# ---------------------------------------------
			
			# copy poster
			if fields['image']:
				if row['image'] != None:
					image_file = os.path.join(gglobals.griffith_dir, 'posters', str(row['image']) + '.jpg')
					if not config['poster_convert']:	# copy file
						try:
							shutil.copy(image_file,	posters_dir)
						except:
							self.debug.show("Can't copy %s" % image_file)
					else:	# convert posters
						try:
							im = Image.open(image_file, 'r').convert(config['poster_mode'])
							im.thumbnail((config['poster_width'], config['poster_height']), Image.ANTIALIAS)
							im.save(os.path.join(posters_dir, row['image']) + '.' + config['poster_format'].lower(), config['poster_format'])
						except:
							self.debug.show("Can't convert %s" % image_file)

			# close file if last item
			if ((page-1)*self.entries_per_page)+item == number_of_exported_movies:
				tmp2 = tpl_tail + ''
				exported_file.write(self.fill_template(tmp2, 'navigation', self.make_navigation(self.pages, page)))
				exported_file.close()
				tmp2 = None
			
			# close file if last item in page
			elif item == self.entries_per_page:
				tmp2 = tpl_tail + ''
				exported_file.write(self.fill_template(tmp2, 'navigation', self.make_navigation(self.pages, page)))
				exported_file.close()
				page = page+1
				item=1
				tmp2 = None
			else:
				item=item+1
			i=i+1
		#}}}
		gutils.info(self, _("Document has been generated."), self)
		self.on_quit()
	#}}}

