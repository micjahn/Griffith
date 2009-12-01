# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2009 Vasco Nunes, Piotr Ożarowski
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
import sys
import string
import os
import logging
log = logging.getLogger("Griffith")

#
# some special classes for better debugging support on windows platforms
# py2exe redirects stdout to /dev/null and writes stderr in a file in the
# installation directory which is a bad idea since windows vista.
#
# the argument --debug now shows a debug window on windows so that the debug
# output is not written to the (black hole windows) console.
#
class GriffithDebug:
    def __init__(self, mode = False):
        self.debugWindow = None
        self.windowredirector = None
        self.blackholebuffer = None
        self.set_debug(mode)

    def set_debug(self, mode = True, logdir = None):
        self.initialize_debug_mode(mode, logdir)
        if self.debugWindow:
            if mode:
                self.debugWindow.show()
            else:
                self.debugWindow.hide()

    def set_logdir(self, logdir):
        if self.windowredirector:
            self.windowredirector.set_logdir(logdir)
        if self.blackholebuffer:
            self.blackholebuffer.set_logdir(logdir)

    def initialize_debug_mode(self, mode, logdir = None):
        # on windows systems all output to stdout goes to a black hole
        # if py2exe is used.
        # so we use a normal window and redirect output from sys.stderr
        # and sys.stdout. it is easier to use for windows users.
        #
        # but we have to do a second trick to get the output from the logging
        # module WITHOUT (!) writing the output twice, one in the window, one
        # to stderr/console/py2exe:
        # removing the handlers from the root logger and reinitialized via
        # logging.basicConfig
        # there is no other way to prevent py2exe showing a error message and
        # generating the .log file in the installation directory
        try:
            if os.name == 'nt' or os.name.startswith('win'): # win32, win64
                if mode:
                    if self.debugWindow is None:
                        self.debugWindow = DebugWindow(None)
                    if not self.windowredirector:
                        self.windowredirector = DebugWindowRedirector(self.debugWindow, logdir)
                    else:
                        self.windowredirector.set_logdir(logdir)
                    sys.stderr = sys.stdout = self.windowredirector
                    # resetting default logging configuration
                    logging.getLogger().handlers = []
                    logging.basicConfig(stream = sys.stderr, format='%(asctime)s: %(levelname)s: %(name)s(%(module)s:%(lineno)d): %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
                elif hasattr(sys, 'frozen') and sys.frozen == 'windows_exe':
                    # if a windows exe is build via py2exe, redirect all output
                    if not self.blackholebuffer:
                        self.blackholebuffer = DebugBlackholeBufferRedirector(sys.stderr, logdir)
                    else:
                        self.blackholebuffer.set_logdir(logdir)
                    sys.stderr = sys.stdout = self.blackholebuffer
                    # resetting default logging configuration
                    logging.getLogger().handlers = []
                    logging.basicConfig(stream = sys.stderr, format='%(asctime)s: %(levelname)s: %(name)s(%(module)s:%(lineno)d): %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        except:
            log.exception('')

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
        if txt is not None:
            buffer = self.textview.get_buffer()
            buffer.insert(buffer.get_end_iter(), txt, -1)

#
# used on windows system
# redirects sys.stderr and sys.stdout to a debug window and 
# a program-defined log-file (py2exe independent)
#
class DebugWindowRedirector(object):
    softspace = 0
    def __init__(self, debugWindow, logdir = None):
        self.debugWindow = debugWindow
        self.set_logdir(logdir)
    def set_logdir(self, logdir):
        #
        # redirected output to a debug file in the log dir/home dir because
        # users with restricted system rights can't write to the installation directory
        # which is the default if py2exe is used
        #
        if logdir:
            from locale import getdefaultlocale
            defaultLang, defaultEnc = getdefaultlocale()
            if defaultEnc is None:
                defaultEnc = 'UTF-8'
            self.debugFileName = os.path.join(logdir, 'griffith.log').decode(defaultEnc)
            try:
                # create the file to show that debug is running
                f = open(self.debugFileName, 'w')
                f.close()
            except:
                self.debugFileName = None
        else:
            self.debugFileName = None
    def write(self, text):
        self.debugWindow.add(text)
        if self.debugFileName:
            try:
                f = open(self.debugFileName, 'at')
                try:
                    f.write(text)
                finally:
                    f.close()
            except:
                pass
    def flush(self):
        pass

#
# a sys.stderr and sys.stdout replacement stream to collect all
# outputs in a local buffer. That prevents the generation of
# a log file and message box when py2exe is used
# the buffer is flushed to a program-defined log file (py2exe independent)
#
class DebugBlackholeBufferRedirector(object):
    softspace = 0
    buffer = ''
    def __init__(self, oldstream, logdir = None):
        self.oldstream = oldstream
        self.set_logdir(logdir)
    def set_logdir(self, logdir):
        #
        # redirected output to a debug file in the log dir/home dir because
        # users with restricted system rights can't write to the installation directory
        # which is the default if py2exe is used
        #
        if logdir:
            from locale import getdefaultlocale
            defaultLang, defaultEnc = getdefaultlocale()
            if defaultEnc is None:
                defaultEnc = 'UTF-8'
            self.debugFileName = os.path.join(logdir, 'griffith.log').decode(defaultEnc)
        else:
            self.debugFileName = None
    def write(self, text):
        try:
            log.info(text)
            self.buffer = string.join([self.buffer, text])
        except Exception, e:
            # resetting to old output streams as last hope
            sys.stdout = sys.stderr = self.oldstream
            print str(e)
    def flush(self):
        if self.debugFileName and self.buffer:
            logfile = open(self.debugFileName, 'at')
            try:
                logfile.write(self.buffer)
                self.buffer = ''
            finally:
                logfile.close()

GriffithDebug = GriffithDebug()