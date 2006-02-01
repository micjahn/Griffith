#!/usr/bin/env python
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
			opts, args = getopt.getopt(sys.argv[1:], "hds:", ["help", "debug", "search"])
		except getopt.GetoptError:
			# print help information and exit:
			con_usage()
			sys.exit(2)
		
		for o, a in opts:
			if o in ("-h", "--help"):
				con_usage()
				sys.exit()
			if o in ("-d"):
				self.debug.set_debug()
			if o in ("-s"):
				con_search_movie(self, a)

def con_search_movie(self, arg):
	data = self.db.select_movie_by_original_title(arg)
	if data:
		for row in data:
			print 5*"-"
			print "\033[35;1m[%s]\033[0m %s (%s), %s - %s"%(row['number'],row['title'], \
				row['original_title'], row['year'], row['director'])
	else:
		print _("No movie found")
	sys.exit()

def con_usage():
	print "USAGE:", sys.argv[0], "[-h|d|s]"
