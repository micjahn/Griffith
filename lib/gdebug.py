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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import getopt, sys

debug_mode = False

try:
	opts, args = getopt.getopt(sys.argv[1:], "hds:", ["help", "debug", "search="])
except getopt.GetoptError:
	# print help information and exit:
	usage()
	sys.exit(2)

for o, a in opts:
	if o in ("-d", "--debug"):
		debug_mode = True

def usage():
	print "USAGE:", sys.argv[0], "[-h|d|s]"

def debug(txt):
	if debug_mode:
		print txt.encode('utf8')
