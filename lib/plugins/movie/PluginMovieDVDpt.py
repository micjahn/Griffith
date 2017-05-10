# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovieDVDpt.py 1138 2009-01-31 21:48:43Z mikej06 $'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ozarowski
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

import gutils
import movie
import string

plugin_name         = "DVDpt"
plugin_description  = ""
plugin_url          = "dvdpt.com"
plugin_language     = _("Portuguese")
plugin_author       = "Ivo Nunes"
plugin_author_email = "<netherblood@gmail.com>"
plugin_version      = "0.1"

class Plugin(movie.Movie):
    """A movie plugin object"""
    def __init__(self, id):
        self.encode='iso-8859-1'
        self.movie_id = id
        self.url = "http://www.dvdpt.com/" + str(self.movie_id) + ".php"

    def get_image(self):
        """Finds the film's poster image"""
        self.image_url = "http://www.dvdpt.com/" + str(self.movie_id) + ".jpg"

    def get_o_title(self):
        """Finds the film's original title"""
        self.o_title = string.capwords(gutils.trim(self.page, '<font face=arial size=-1><b>"', '"'))

    def get_title(self):
        """Finds the film's local title.
        Probably the original title translation"""
        self.title = string.capwords(gutils.trim(self.page, "<title>", "</title>"))

    def get_director(self):
        """Finds the film's director"""
        self.director = gutils.trim(self.page, "<b>REALIZADOR</b></font>\n<br />\n<font face=arial size=-1>", "\n<br /><br />")
        self.director = gutils.strip_tags(self.director)

    def get_plot(self):
        """Finds the film's plot"""
        self.plot = gutils.trim(self.page, '<center>\n<b>"', '"</b><br />')

    def get_year(self):
        """Finds the film's year"""
        self.year = gutils.trim(self.page, '" (', ' -')

    def get_runtime(self):
        """Finds the film's running time"""
        self.runtime = gutils.trim(self.page, " - ", "m)")
        #self.runtime = gutils.after(self.runtime, "-1>")

    def get_genre(self):
        """Finds the film's genre"""
        self.genre = ""

    def get_cast(self):
        self.cast = gutils.trim(self.page, "<b>INTÉRPRETES</b></font>\n<br />\n<font face=arial size=-1>", "\n</div>")

    def get_classification(self):
        """Find the film's classification"""
        self.classification = ""

    def get_studio(self):
        """Find the studio"""
        self.studio = gutils.trim(self.page, "<font color=red face=arial size=-1><b>ESTÚDIO</b></font> \n<br />\n<font face=arial size=-1>", "<br />")

    def get_o_site(self):
        """Find the film's oficial site"""
        self.o_site = ""

    def get_site(self):
        """Find the film's imdb details page"""
        self.site = ""

    def get_trailer(self):
        """Find the film's trailer page or location"""
        self.trailer = ""

    def get_country(self):
        """Find the film's country"""
        self.country = ""

    def get_rating(self):
        """Find the film's rating. From 0 to 10.
        Convert if needed when assigning."""
        self.rating = ""

class SearchPlugin(movie.SearchMovie):
    """A movie search object"""
    def __init__(self):
        self.original_url_search   = "http://search.freefind.com/find.html?id=58910933&pageid=r&mode=all&n=0&query="
        self.translated_url_search = "http://search.freefind.com/find.html?id=58910933&pageid=r&mode=all&n=0&query="
        self.encode                = 'utf-8'

    def search(self, parent_window):
        """Perform the web search"""
        if not self.open_search(parent_window):
            return None
        self.sub_search()
        return self.page

    def sub_search(self):
        """Isolating just a portion (with the data we want) of the results"""
        self.page = gutils.trim(self.page, \
            "<!-- search results copyright FreeFind.com.  All rights reserved. Results may not be re-used, meta searched, or searched robotically -->", "<table class=search-nav-form-table>")

    def get_searches(self):
        """Try to find both id and film title for each search result"""
        elements = string.split(self.page, "<br>")
        self.number_results = elements[-1]

        if (len(elements[0])):
            for element in elements:
                self.ids.append(gutils.trim(element, '<a  href="http://www.dvdpt.com/', '.php" >'))
                title = gutils.trim(element, '.php" >', '</a>')
                title = title.replace("<b>", "")
                title = title.replace("</b>", "")
                self.titles.append(title)
        else:
            self.number_results = 0

