#!/usr/bin/env python
# -*- coding: utf-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes
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
        "includes": "pygtk,cairo,pangocairo,gobject,cgi,PIL,pysqlite2,pysqlite2.*,pango,atk,gobject,tempfile,csv,xml.dom,xml.dom.ext,xml.dom.minidom,xml.sax,threading,htmlentitydefs,sqlalchemy,sqlalchemy.*,sqlalchemy.databases.*,sqlalchemy.engine.*,sqlalchemy.ext.*,sqlalchemy.orm.*,sqlalchemy.sql.*,zipfile,webbrowser,shutil,reportlab,reportlab.pdfgen,reportlab.pdfgen.canvas,reportlab.platypus,reportlab.pdfbase.ttfonts,smtplib,win32com,platform,winshell,psycopg2,MySQLdb,chardet,gzip,commands,encodings,encodings.*,ConfigParser,gtk.glade,xmlrpclib",
        "optimize": 2,
        "dist_dir": "dist",
    }
}

setup(
    name = "Griffith",
    version = "0.10-rc1",
    description = 'Griffith - A film manager',
    author = 'Vasco Nunes/Piotr Ozarowski',
    author_email = 'griffith-private@lists.berlios.de',
    url = 'http://www.griffith.cc/',
    license = 'GPL',
    windows = [
        {
            "script": "griffith",
            "icon_resources": [(1, "images\griffith.ico")]
        }],
    options = opts,
        data_files=[
        ("images", glob.glob("data\\*.png")),
        ("images/export_templates", glob.glob("export_templates\\*.dtd")),
        ("images/export_templates/csv",    glob.glob("export_templates\\csv\\*.*")),
        ("images/export_templates/xml",    glob.glob("export_templates\\xml\\*.*")),
        ("images/export_templates/latex", glob.glob("export_templates\\latex\\*.*")),
        ("images/export_templates/html_table", glob.glob("export_templates\\html_table\\*.*")),
        ("images/export_templates/html_tables",    glob.glob("export_templates\\html_tables\\*.*")),
        ("glade", glob.glob("glade\\*.*")),
        ("i18n/bg/LC_MESSAGES", glob.glob("i18n\\bg\\LC_MESSAGES\\*.mo")),
        ("i18n/ca/LC_MESSAGES",    glob.glob("i18n\\ca\\LC_MESSAGES\\*.mo")),
        ("i18n/cs/LC_MESSAGES",    glob.glob("i18n\\cs\\LC_MESSAGES\\*.mo")),
        ("i18n/da/LC_MESSAGES",    glob.glob("i18n\\da\\LC_MESSAGES\\*.mo")),
        ("i18n/de/LC_MESSAGES",    glob.glob("i18n\\de\\LC_MESSAGES\\*.mo")),
        ("i18n/el/LC_MESSAGES",    glob.glob("i18n\\el\\LC_MESSAGES\\*.mo")),
        ("i18n/en_GB/LC_MESSAGES", glob.glob("i18n\\en_GB\\LC_MESSAGES\\*.mo")),
        ("i18n/es/LC_MESSAGES",    glob.glob("i18n\\es\\LC_MESSAGES\\*.mo")),
        ("i18n/et/LC_MESSAGES",    glob.glob("i18n\\et\\LC_MESSAGES\\*.mo")),
        ("i18n/fa/LC_MESSAGES",    glob.glob("i18n\\fa\\LC_MESSAGES\\*.mo")),
        ("i18n/fi/LC_MESSAGES",    glob.glob("i18n\\fi\\LC_MESSAGES\\*.mo")),
        ("i18n/fr/LC_MESSAGES",    glob.glob("i18n\\fr\\LC_MESSAGES\\*.mo")),
        ("i18n/hu/LC_MESSAGES",    glob.glob("i18n\\hu\\LC_MESSAGES\\*.mo")),
        ("i18n/id/LC_MESSAGES",    glob.glob("i18n\\id\\LC_MESSAGES\\*.mo")),
        ("i18n/it/LC_MESSAGES",    glob.glob("i18n\\it\\LC_MESSAGES\\*.mo")),
        ("i18n/ja/LC_MESSAGES",    glob.glob("i18n\\ja\\LC_MESSAGES\\*.mo")),
        ("i18n/ko/LC_MESSAGES",    glob.glob("i18n\\ko\\LC_MESSAGES\\*.mo")),
        ("i18n/lv/LC_MESSAGES",    glob.glob("i18n\\lv\\LC_MESSAGES\\*.mo")),
        ("i18n/nb/LC_MESSAGES",    glob.glob("i18n\\nb\\LC_MESSAGES\\*.mo")),
        ("i18n/nds/LC_MESSAGES",    glob.glob("i18n\\nds\\LC_MESSAGES\\*.mo")),
        ("i18n/nl/LC_MESSAGES",    glob.glob("i18n\\nl\\LC_MESSAGES\\*.mo")),
        ("i18n/oc/LC_MESSAGES",    glob.glob("i18n\\oc\\LC_MESSAGES\\*.mo")),
        ("i18n/pl/LC_MESSAGES",    glob.glob("i18n\\pl\\LC_MESSAGES\\*.mo")),
        ("i18n/ps/LC_MESSAGES",    glob.glob("i18n\\ps\\LC_MESSAGES\\*.mo")),
        ("i18n/pt/LC_MESSAGES",    glob.glob("i18n\\pt\\LC_MESSAGES\\*.mo")),
        ("i18n/pt_BR/LC_MESSAGES", glob.glob("i18n\\pt_BR\\LC_MESSAGES\\*.mo")),
        ("i18n/ru/LC_MESSAGES",    glob.glob("i18n\\ru\\LC_MESSAGES\\*.mo")),
        ("i18n/sk/LC_MESSAGES",    glob.glob("i18n\\sk\\LC_MESSAGES\\*.mo")),
        ("i18n/sr/LC_MESSAGES",    glob.glob("i18n\\sr\\LC_MESSAGES\\*.mo")),
        ("i18n/sv/LC_MESSAGES",    glob.glob("i18n\\sv\\LC_MESSAGES\\*.mo")),
        ("i18n/tr/LC_MESSAGES",    glob.glob("i18n\\tr\\LC_MESSAGES\\*.mo")),
        ("i18n/uk/LC_MESSAGES",    glob.glob("i18n\\uk\\LC_MESSAGES\\*.mo")),
        ("i18n/zh_CN/LC_MESSAGES", glob.glob("i18n\\zh_CN\\LC_MESSAGES\\*.mo")),
        ("lib/plugins", glob.glob("lib\\plugins\\*.*")),
        ("lib/plugins/export", glob.glob("lib\\plugins\\export\\*.*")),
        ("lib/plugins/movie", glob.glob("lib\\plugins\\movie\\*.*")),
        ("lib/plugins/imp", glob.glob("lib\\plugins\\imp\\*.*")),
        ("images", glob.glob("images\\*.png")),
        ("lib", glob.glob("lib\\*.*"))],
)
