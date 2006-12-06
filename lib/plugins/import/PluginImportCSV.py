# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

###########################################################################
#    Copyright (C) 2006 by Jessica Katharina Parth                         
#    <skorpion@slyclan.de>                                                 
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

import csv
import gtk
import gutils
import os
import movie, string
import re
import codecs
from gettext import gettext as _

import plugin

def digits_only(s):
	_match = re.compile(r"\d+")
	try:
		s = reduce( string.join, _match.findall(s) )
	except:
		s = '0'
	return s
	
class ImportPlugin(plugin.ImportPlugin):
	name = "CSV"
	description = _("Full CSV list import plugin")
	author = "Jessica Katharina Parth"
	author_email = "deepfly@gmx.net"
	version = "0.1"

	def initialize(self):
		# TODO: configure csv.reader
		filename = gutils.file_chooser(_("Import a %s document")%"CSV", action=gtk.FILE_CHOOSER_ACTION_OPEN, \
			buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK),name='')
		if filename[0]:
			self.set_source(filename[0])
		else:
			return False
		return True

	def set_source(self, name):
		self.__source_name = name
		self.data = csv.reader(codecs.open(name, 'r', 'iso-8859-1'), dialect='excel', quotechar='"', delimiter=',')

	def count_movies(self):
		return len(open(self.__source_name).readlines())
	
	def get_movie_details(self, item):
		x = 0
		
		t_movies = {
			'classification' : item[8],
			'color'          : None,
			'cond'           : None,
			'country'        : None,
			'director'       : None,
			'genre'          : item[4],
			'image'          : None,
			'layers'         : None,
			'media_num'      : int(digits_only(item[0])),
			'number'         : gutils.find_next_available(self),
			'o_site'         : None,
			'o_title'        : item[7],
			'rating'         : None,
			'region'         : None,
			'runtime'        : digits_only(item[3]),
			'site'           : None,
			'studio'         : None,
			'title'          : item[1],
			'trailer'        : None,
			'year'           : digits_only(item[2]),
			'collection_id'  : None, #self.collection_combo_ids[],
			'volume_id'      : None, #self.volume_combo_ids[],
			'cast'           : item[6],
			'notes'          : None,
			'plot'           : item[5],
		}
#		t_movies['movie_id'] = 
	
		medium_id = 0
		if medium_id>0:
			t_movies['medium_id'] = self.media_ids[medium_id]
		vcodec_id = 0
		if vcodec_id>0:
			t_movies['vcodec_id'] = self.vcodecs_ids[vcodec_id]
		if item[x]:
			t_movies['seen'] = True
		else:
			t_movies['seen'] = False
		
		# languages
		from sets import Set as set # for python2.3 compatibility
		t_movies['languages'] = set()
#		for lang in item[x]:
#			lang_id   = get_id(item[x], lang[0])
#			lang_type = get_id(item[x], lang[1])
#			acodec    = get_id(item[x], lang[2])
#			achannel  = get_id(item[x], lang[3])
#			subformat = get_id(item[x], lang[4])
#			t_movies['languages'].add((lang_id, lang_type, acodec, achannel, subformat))
	
		# tags
		t_movies['tags'] = {}
		if item[x] == True:
			t_movies['tags'][0] = 1
			
		# validate data
		for i in t_movies.keys():
			if t_movies[i] == '':
				t_movies[i] = None
		for i in ['color','cond','layers','region', 'media', 'vcodec']:
			if t_movies.has_key(i) and t_movies[i] == -1:
				t_movies[i]=None
		for i in ['volume_id','collection_id', 'runtime']:
			if t_movies.has_key(i) and (t_movies[i] is None or int(t_movies[i]) == 0):
				t_movies[i] = None
		if t_movies.has_key('year') and (t_movies['year'] is None or int(t_movies['year']) < 1886):
			t_movies['year'] = None
	
		return t_movies
	
