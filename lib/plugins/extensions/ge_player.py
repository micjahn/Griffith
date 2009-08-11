# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright © 2009 Piotr Ożarowski
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published byp
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

import logging
from subprocess import Popen

from plugins.extensions import GriffithExtensionBase as Base

log = logging.getLogger('Griffith')

class GriffithExtension(Base):
    name = 'Player'
    description = _('Plays movie trailer')
    author = 'Piotr Ożarowski'
    email = 'piotr@griffith.cc'
    version = 1
    api = 1
    enabled = False # disabled by default
    enabled = True

    preferences = {'command': {'name': _('Command'),
                               'hint': _('%s (if given) will be replaced with file path'),
                               'default': 'mplayer %s',
                               'type': unicode}}
    toolbar_icon = 'gtk-open'

    def toolbar_icon_clicked(self, widget, movie):
        if not movie or not movie.trailer:
            
            return False

        command = self.get_config_value('command', self.preferences['command']['default']).lower()
        if '%s' in command:
            command %= movie.trailer
        else:
            command = "%s %s" % (command, movie.trailer)
        Popen(command, shell=True)

    def maintree_clicked(self, selection, movie):
        if movie and movie.trailer:
            self.toolbar_icon_widget.set_sensitive(True)
        else:
            self.toolbar_icon_widget.set_sensitive(False)
