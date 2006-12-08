# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

###########################################################################
#    Copyright (C) 2006 by Jessica Katharina Parth                         
#    <Jessica.K.P@women-at-work.org>                                                 
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

from gettext import gettext as _
from plugins.imp import ImportPlugin

def digits_only(s):
	import string, re
	_match = re.compile(r"\d+")
	try:
		s = reduce( string.join, _match.findall(s) )
	except:
		s = '0'
	return s
	
class ImportPlugin(ImportPlugin):
	description	= _("Full CSV list import plugin")
	author		= "Jessica Katharina Parth"
	email		= "Jessica.K.P@women-at-work.org"
	version		= "0.1"
	file_filters	= '*.[cC][sS][vV]'
	mime_types	= ('text/comma-separated-values', 'text/csv', 'application/csv',
			'application/excel', 'application/vnd.ms-excel', 'application/vnd.msexcel')

	def initialize(self):
		# build window, initialize widgets, source _independent_ initialization
		return True

	def set_source(self, name):
		# source _dependent_ initialization goes here
		import csv, codecs, os
		if name is None or not os.path.isfile(name):
			return False
		self.__source_name = name
		self.data = csv.reader(codecs.open(name, 'r', 'iso-8859-1'), dialect='excel', quotechar='"', delimiter=',')
		return True

	def count_movies(self):
		return len(open(self.__source_name).readlines()) # FIXME
	
	def get_movie_details(self, item):
		from add import validate_details
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
			'number'         : None,
			'o_site'         : None,
			'o_title'        : item[7],
			'rating'         : None,
			'region'         : None,
			'runtime'        : digits_only(item[3]),
			'seen'           : None, #bool(row[x]),
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
		
		# languages
#		from sets import Set as set # for python2.3 compatibility
#		t_movies['languages'] = set()
#		for lang in item[x]:
#			lang_id   = item[x]
#			lang_type = item[x]
#			acodec    = item[x]
#			achannel  = item[x]
#			subformat = item[x]
#			t_movies['languages'].add((lang_id, lang_type, acodec, achannel, subformat))
	
		# tags
#		t_movies['tags'] = {}
#		if item[x] == True:
#			t_movies['tags'][0] = 1
		
		validate_details(t_movies)

		return t_movies
	
