# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski
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

import gtk
import pygtk

class GriffithDebug:
    debug_mode = None
    
    def __init__(self, mode=False):
        self.debugWindow = None
        self.set_debug(mode)

    def set_debug(self, mode=True):
        self.debug_mode = mode
        self.check_for_window()
        if not (self.debugWindow is None or self.debugWindow == False):
            if mode:
                self.debugWindow.show()
            else:
                self.debugWindow.hide()

    def check_for_window(self):
        # on windows systems all output to stdout goes to a black hole
        # if py2exe is used.
        # so we use a normal window and redirect output from sys.stderr
        # and sys.stdout. it is easier to use for windows users.
        try:
            if self.debug_mode and self.debugWindow is None:
                import gutils, sys
                if gutils.is_windows_system():
                    self.debugWindow = DebugWindow(None)
                    sys.stderr = sys.stdout = DebugWindowRedirector(self.debugWindow)
                else:
                    self.debugWindow = False
        except:
            pass

    def show(self, txt):
        if self.debug_mode:
            print txt.encode('utf8')

#
# used on windows systems
# shows a windows with a text view which displays the
# debug output provided by DebugWindowRedirector
#
class DebugWindow:
    def __init__(self, window):
        self.dialog = gtk.Dialog('Debug Window', window, gtk.DIALOG_MODAL, ())
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_transient_for(window)
        self.dialog.set_modal(False)
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.textview.set_scroll_adjustments(gtk.Adjustment(1.0, 1.0, 100.0, 1.0, 10.0, 10.0), gtk.Adjustment(1.0, 1.0, 100.0, 1.0, 10.0, 10.0))
        self.scrolledwindow = gtk.ScrolledWindow(None, None)
        self.scrolledwindow.add(self.textview)
        self.dialog.vbox.pack_start(self.scrolledwindow)
        self.dialog.set_default_size(640, 480)
    def show(self):
        self.dialog.show_all()
    def hide(self):
        self.dialog.hide_all()
    def close(self):
        self.dialog.destroy()
    def add(self, txt):
        buffer = self.textview.get_buffer()
        buffer.insert(buffer.get_end_iter(), txt, -1)

#
# used on windows system
# redirects sys.stderr and sys.stdout to a debug window and a file
# 'griffith_debug.txt' in the home directory (My documents)
#
class DebugWindowRedirector(object):
    softspace = 0
    def __init__(self, debugWindow):
        self.debugWindow = debugWindow
        #
        # redirected output to a debug file in the home directory because
        # users with restricted system rights can't write to the installation directory
        # which is the default if py2exe is used
        #
        import winshell, os
        from win32com.shell import shellcon, shell
        from locale import getdefaultlocale
        defaultLang, defaultEnc = getdefaultlocale()
        if defaultEnc is None:
            defaultEnc = 'UTF-8'
        self.debugFileName = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, 0, 0), 'griffith_debug.txt').decode(defaultEnc)
        try:
            f = open(self.debugFileName, 'w')
            f.close()
        except:
            pass
    def write(self, text):
        self.debugWindow.add(text)
        try:
            f = open(self.debugFileName, 'a')
            try:
                f.write(text)
            finally:
                f.close()
        except:
            pass
    def flush(self):
        pass
