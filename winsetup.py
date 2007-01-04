#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

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
        "includes": "pygtk,cairo,pangocairo,cgi,PIL,pysqlite2,pysqlite2.*,pango,atk,gobject,tempfile,csv,xml.dom,xml.dom.ext,xml.dom.minidom,xml.sax,threading,htmlentitydefs,sqlalchemy,sqlalchemy.*,sqlalchemy.mods.*,sqlalchemy.databases.*,sqlalchemy.engine.*,sqlalchemy.ext.*,sqlalchemy.orm.*,zipfile,webbrowser,shutil,reportlab,reportlab.pdfgen,reportlab.pdfgen.canvas,reportlab.platypus,reportlab.pdfbase.ttfonts,smtplib,win32com,platform,winshell,psycopg2,MySQLdb,chardet",
        "optimize": 2,
		"dist_dir": "dist",
    }
}

setup(
    name = "Griffith",
    version = "0.9-rc2",
	description = 'Griffith - A film manager',
    author = 'Vasco Nunes/Piotr Ozarowski',
    author_email = 'vasco.m.nunes@gmail.com',
    url = 'http://griffith.berlios.de',
    license = 'GPL',
    console = [
        {
            "script": "griffith",
            "icon_resources": [(1, "images\griffith.ico")]
        }],
		options = opts,
		data_files=[
		("images",
		glob.glob("data\\*.png")),
		("images/export_templates",
		glob.glob("data\\export_templates\\*.dtd")),
		("images/export_templates/csv",
		glob.glob("data\\export_templates\\csv\\*.*")),
		("images/export_templates/xml",
		glob.glob("data\\export_templates\\xml\\*.*")),
		("images/export_templates/latex",
		glob.glob("data\\export_templates\\latex\\*.*")),
		("images/export_templates/html_table",
		glob.glob("data\\export_templates\\html_table\\*.*")),
		("images/export_templates/html_tables",
		glob.glob("data\\export_templates\\html_tables\\*.*")),
		("glade",
		glob.glob("glade\\*.*")),
		("i18n/bg/LC_MESSAGES",
		glob.glob("i18n\\bg\\LC_MESSAGES\\*.mo")),
		("i18n/cs/LC_MESSAGES",
		glob.glob("i18n\\cs\\LC_MESSAGES\\*.mo")),
		("i18n/de/LC_MESSAGES",
		glob.glob("i18n\\de\\LC_MESSAGES\\*.mo")),
		("i18n/es/LC_MESSAGES",
		glob.glob("i18n\\es\\LC_MESSAGES\\*.mo")),
		("i18n/fr/LC_MESSAGES",
		glob.glob("i18n\\fr\\LC_MESSAGES\\*.mo")),
		("i18n/pl/LC_MESSAGES",
		glob.glob("i18n\\pl\\LC_MESSAGES\\*.mo")),
		("i18n/pt/LC_MESSAGES",
		glob.glob("i18n\\pt\\LC_MESSAGES\\*.mo")),
		("i18n/it/LC_MESSAGES",
		glob.glob("i18n\\it\\LC_MESSAGES\\*.mo")),
		("i18n/sv/LC_MESSAGES",
		glob.glob("i18n\\sv\\LC_MESSAGES\\*.mo")),
		("i18n/pt_BR/LC_MESSAGES",
		glob.glob("i18n\\pt_BR\\LC_MESSAGES\\*.mo")),
		("lib/plugins",
		glob.glob("lib\\plugins\\*.*")),
		("lib/plugins/export",
		glob.glob("lib\\plugins\\export\\*.*")),
		("lib/plugins/movie",
		glob.glob("lib\\plugins\\movie\\*.*")),
		("lib/plugins/imp",
		glob.glob("lib\\plugins\\imp\\*.*")),
		("images",
		glob.glob("images\\*.png")),
		("",
		glob.glob("lib\\*.*"))],
)
