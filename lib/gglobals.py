# -*- coding: UTF-8 -*-

__revision__ = '$Id: gglobals.py,v 1.19 2005/09/21 10:41:45 iznogoud Exp $'

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

import os
import sys
import gdebug

if os.name == 'nt' or os.name == 'win32':
    # default to My Documents
    # lets check if an older griffith dir exists
    old_dir = os.path.join(os.environ.get('APPDATA', \
    os.path.join(os.path.expanduser('~'), \
        'Application Data')), 'griffith')
    import winshell
    griffith_dir = os.path.join(winshell.my_documents (), 'griffith')
    if os.path.exists(old_dir):
        os.move(old_dir, winshell.my_documents ())
	
else:
    griffith_dir = os.path.join(os.path.expanduser('~'), \
        '.griffith')
try:
    if not os.path.exists(griffith_dir):
        gdebug.debug('Creating %s' % griffith_dir)
        os.makedirs(griffith_dir)
    else:
    	gdebug.debug('Using Griffith directory: %s'%griffith_dir)
except OSError:
		gdebug.debug("Unable to create griffith directory.")
		raise
		sys.exit()

if not os.access(griffith_dir, os.W_OK):
    gdebug.debug('Cannot write to griffith directory, %s' % griffith_dir)
    sys.exit()
    
if not os.path.exists(os.path.join(griffith_dir, "posters")):
        gdebug.debug("Creating poster directory")
        os.makedirs(os.path.join(griffith_dir, "posters"))
