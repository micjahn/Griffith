# -*- coding: ISO-8859-1 -*-

__revision__ = '$Id: $'

# Copyright (c) 2005-2006 Vasco Nunes
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
import getopt
import sys

def check_args(self):

	self.args = map(lambda i: i.replace('--', '').replace('-',''), sys.argv)			
	
	if self.args:	
		try:
			opts, args = getopt.getopt(sys.argv[1:], "hDo:s:d:w:y:", ["help", "debug", "search_original=", "search_title=", "director=", "with=", "year="])
		except getopt.GetoptError:
			# print help information and exit:
			con_usage()
			sys.exit(2)
		
		for o, a in opts:
			if o in ("-h", "--help"):
				con_usage()
				sys.exit()
			if o in ("-D"):
				self.debug.set_debug()
			if o in ("-o", "--search_original"):
				con_search_movie(self, a, 1)
			if o in ("-s", "--search_title"):
				con_search_movie(self, a, 2)
			if o in ("-d", "--director"):
				con_search_movie(self, a, 3)
			if o in ("-w", "--with"):
				con_search_movie(self, a, 4)
			if o in ("-y", "--year"):
				con_search_movie(self, a, 5)

def con_search_movie(self, arg, search_type):
	if search_type==1:
		data = self.db.select_movie_by_original_title(arg)
	elif search_type==2:
		data = self.db.select_movie_by_title(arg)
	elif search_type==3:
		data = self.db.select_movie_by_director(arg)
	elif search_type==4:
		data = self.db.select_movie_by_actors(arg)
	elif search_type==5:
		data = self.db.select_movie_by_year(arg)

	if data:
		for row in data:
			print "\033[35;1m[%s]\033[0m\t\033[34m%s\033[0m (%s), %s - \033[32m%s\033[0m"%(row['number'],row['title'], \
				row['original_title'], row['year'], row['director'])
	else:
		print _("No movie found")
	sys.exit()

def con_usage():
	print "USAGE:", sys.argv[0], "[-h|D|s|d|w|y]"
