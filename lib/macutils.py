# -*- coding: UTF-8 -*-

__revision__ = '$Id: macutils.py 1519 2011-02-05 15:32:36Z iznogoud $'

# Copyright (c) 2005-2011 Vasco Nunes, Piotr Ożarowski
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

from Cocoa import *

# ================
# Save file dialog
# ================

def saveDialog(filetypes=[]):
    panel = NSSavePanel.savePanel()
    panel.setCanCreateDirectories_(True)
    panel.setCanChooseDirectories_(False)
    panel.setCanChooseFiles_(True)
    panel.setAllowsOtherFileTypes_(False)
    result = panel.runModalForDirectory_file_types_(
        NSHomeDirectory() + '/Desktop',None,filetypes)
    if result:
        return True, panel.filename(), panel.directory()
    else:
        return False, None, None
    return
    
# ================
# Open file dialog
# ================

def openDialog(filetypes=[]):
    panel = NSOpenPanel.openPanel()
    panel.setCanCreateDirectories_(False)
    panel.setCanChooseDirectories_(False)
    panel.setCanChooseFiles_(True)
    result = panel.runModalForDirectory_file_types_(
        NSHomeDirectory() + '/Desktop',None,filetypes)
    if result:
        return True, panel.filename(), panel.directory()
    else:
        return False, None, None
    return
    
# ================
# Alert dialog
# ================  
    
def createAlert(msg):
    alert = NSAlert.alloc().init()
    alert.setMessageText_(msg)
    alert.setInformativeText_("")
    alert.setAlertStyle_(NSInformationalAlertStyle)
    alert.runModal()
        
# ================
# Question dialog
# ================
        
def question(msg, window=None):
    alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
        msg, "Yes", "No", None, "")
    buttonPressed=alert.runModal()
    if buttonPressed == 0:
        return False
    else:
        return True