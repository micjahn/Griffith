#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

__revision__ = '$Id: $'

# Copyright (c) 2005 Vasco Nunes
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

# don't forget to copy lib and etc from gtk to dist dir

import time
import sys

# ModuleFinder can't handle runtime changes to __path__, but win32com uses them

try:
    import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

from distutils.core import setup
import glob
import py2exe

opts = { 
    "py2exe": { 
        "includes": "pango,atk,gobject,threading,htmlentitydefs,sqlite,zipfile,webbrowser,shutil,reportlab,reportlab.pdfgen,reportlab.pdfgen.canvas,reportlab.platypus,smtplib,win32com,winshell", 
        "dist_dir": "dist", 
    } 
} 

setup(
    name = "Griffith",
    description = "A movie collection manager.",
    version = "0.4.3",
    console = [ 
        { 
            "script": "griffith", 
            "icon_resources": [(1, "images\griffith.ico")] 
        }],
		options = opts,
		data_files=[
		("data",
		glob.glob("data\\*.png")),
		("data/export_templates",
		glob.glob("data\\export_templates\\*.dtd")),
		("data/export_templates/csv",
		glob.glob("data\\export_templates\\csv\\*.*")),
		("data/export_templates/xml",
		glob.glob("data\\export_templates\\xml\\*.*")),
		("data/export_templates/html_table",
		glob.glob("data\\export_templates\\html_table\\*.*")),
		("data/export_templates/html_tables",
		glob.glob("data\\export_templates\\html_tables\\*.*")),
		("fonts",
		glob.glob("fonts\\*.TTF")),
		("glade",
		glob.glob("glade\\*.*")),
		("i18n/bg/LC_MESSAGES",
		glob.glob("i18n\\pt\\LC_MESSAGES\\*.mo")),
		("i18n/bg/LC_MESSAGES",
		glob.glob("i18n\\pt\\LC_MESSAGES\\*.mo")),
		("i18n/pl/LC_MESSAGES",
		glob.glob("i18n\\pl\\LC_MESSAGES\\*.mo")),
		("i18n/de/LC_MESSAGES",
		glob.glob("i18n\\de\\LC_MESSAGES\\*.mo")),
		("lib/plugins/export",
		glob.glob("lib\\plugins\\export\\*.*")),
		("lib/plugins/movie",
		glob.glob("lib\\plugins\\movie\\*.*")),
		("images",
		glob.glob("images\\*.png")),
		("",
		glob.glob("lib\\*.*"))],
)
