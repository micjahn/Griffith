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

from gutils import is_windows_system
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

    preferences = {'command': {'name': _('Command'),
                               'hint': _('{1} (if given) will be replaced with file path'),
                               'default': 'mplayer {1}',
                               'type': unicode}}
    if is_windows_system():
        preferences['command']['default'] = ''

    toolbar_icon = 'gtk-open'

    def toolbar_icon_clicked(self, widget, movie):
        if not movie or not movie.trailer:
            return False

        useShell = True
        command = self.get_config_value('command', self.preferences['command']['default'])
        if is_windows_system():
            useShell = False # Popen with shell=True doesn't work under windows with spaces in filenames
            if not command:
                import win32api
                log.debug('try ShellExecute with trailer %s' % movie.trailer)
                win32api.ShellExecute(0, None, movie.trailer, None, None, 0)
                return

        if '{1}' in command:
            command = command.replace('{1}', movie.trailer)
        else:
            # make a sequence results in Popen calls list2cmdline
            command = [command, movie.trailer]

        log.debug(command)
        Popen(command, shell=useShell)

    def maintree_clicked(self, selection, movie):
        if movie and movie.trailer:
            self.toolbar_icon_widget.set_sensitive(True)
        else:
            self.toolbar_icon_widget.set_sensitive(False)
