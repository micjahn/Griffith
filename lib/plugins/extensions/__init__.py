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

import glob
import logging
import os.path
import sys

import db

log = logging.getLogger('Griffith')

# minimum and maximum supported extension API
COMPAT = (1, 1)


class GriffithExtensionBase(object):
    """Griffith Extension

    :attr config: configuration
    :attr db: database
    :attr locations: dictionary with Griffth locations
    :attr widgets: dictionary with GUI widgets
    :attr preferences: dictionary used to generate new widgets in preferences window
        every key points to another dictionary that contains:
        * name: will be shown to user
        * type: int, unicode (type) or list, tuple, dict (instance)
        * min: minimum value (int) or length (unicode)
        * max: maximum value (int) or length (unicode)
    :attr app: application reference (use only if really needed)
    """
    name = None
    description = None
    author = None
    email = None
    version = None
    api = 1 # required Griffith Extension API

    enabled = True # default state (can be changed in preferences later)
    toolbar_icon = None # None or stock icon name
    preferences = {}

    toolbar_icon_widget = None # will be constructed from toolbar_icon

    def __new__(class_, *args, **kwargs):
        if class_.api < COMPAT[0]:
            raise DeprecationWarning("Extension is using API that is no longer supported: %s (api=%d)" % (class_.name, class_.api))
        if class_.api > COMPAT[1]:
            raise NotImplementedError("Extension is using API that is not yet supported: %s (api=%d)" % (class_.name, class_.api))
        obj = object.__new__(class_, *args, **kwargs)
        obj.app = app = args[0]
        obj.widgets = app.widgets
        obj.config = app.config
        obj.db = app.db
        obj.locations = app.locations
        return obj

    def __repr__(self):
        return "<GriffithExtension api=%d name=%s version=%s>" % (self.api, self.name, self.version)

    def get_config_value(self, key, default=None):
        return self.config.get("%s_%s" % (self.id, key), default, section='extensions')

    def set_config_value(self, key, value=None):
        self.config.set("%s_%s" % (self.id, key), value, section='extensions')
        self.config.save()

    def _on_toolbar_icon_clicked(self, button_widget):
        session = self.db.Session()
        movie = session.query(db.Movie).filter(db.Movie.movie_id == self.app._movie_id).first()
        if not movie:
            log.error('No movie selected')
        else:
            self.toolbar_icon_clicked(button_widget, movie)

    # methods that can be overwritten:

    def __init__(self, griffith):
        """Initializes extension"""

    def clear(self): # __del__ cannot be used here (signal reference issue)
        """Invoked when extension is about to be disabled"""
        if self.toolbar_icon_widget:
            self.toolbar_icon_widget.destroy()

    def maintree_clicked(self, selection, movie):
        """Invoked every time new movie is selected"""

    def toolbar_icon_clicked(self, widget, movie):
        """Invoked when toolbar icon is clicked"""

    def filter_movies(self, conditions):
        """Modifies movie selection (via search conditions)"""
        return conditions


by_name = {} # extension modules by name


def scan_for_extensions(path):
    """Adds new extensions from given path"""

    names = dict((os.path.basename(x)[:-3], x) for x in glob.glob("%s/ge_[a-zA-Z]*.py" % path))
    names.update(dict((os.path.basename(x)[:-4], x) for x in glob.glob("%s/ge_[a-zA-Z]*.pyo" % path)))
    names.update(dict((os.path.basename(x)[:-4], x) for x in glob.glob("%s/ge_[a-zA-Z]*.pyc" % path)))

    if names:
        remove_from_syspath = False
        if path not in sys.path:
            remove_from_syspath = True
            sys.path.append(path)

        for ext_name in names:
            #module = __import__("plugins.extensions.%s" % ext_name, fromlist=[ext_name])
            module = __import__(ext_name)
            id_ = ext_name[3:] # skip the "ge_"
            extension = module.GriffithExtension
            extension.id = id_
            extension.__file__ = names[ext_name]
            by_name[id_] = extension

        if remove_from_syspath:
            del sys.path[-1]

scan_for_extensions(os.path.dirname(__file__)) # user's directory will be added later (in app)
