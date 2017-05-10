# -*- coding: UTF-8 -*-

# $Id: PluginMovieMediadis.py 1090 2008-12-16 20:59:02Z piotrek $

# Copyright (c) 2005-2007 Vasco Nunes
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import gutils
import movie,string

plugin_name = "Mediadis"
plugin_description = "Entertaining People"
plugin_url = "www.mediadis.com"
plugin_language = _("English")
plugin_author = "Vasco Nunes"
plugin_version = "0.2"

class Plugin(movie.Movie):
    def __init__(self, id):
        self.movie_id = id
        self.url = "http://www.mediadis.com/dvd/detail.asp?id=" + str(self.movie_id)

    def get_image(self):
        self.image_url = gutils.trim(self.page,"<img src=\"http://www.mediadis.com/pictures/big/", ".jpg\" border=\"0\"")
        self.image_url = "http://www.mediadis.com/pictures/big/" + self.image_url + ".jpg"

    def get_o_title(self):
        self.o_title = string.capwords(gutils.trim(self.page,"<b>Original title</b>&nbsp;:&nbsp;","<br>") )

    def get_title(self):
        self.title = self.o_title

    def get_director(self):

        self.director = gutils.trim(self.page,"<b>Director(s)</b>&nbsp;:&nbsp;","<br>")
        self.director = string.replace(self.director, "&nbsp;-&nbsp;", ", ")
        self.director = gutils.strip_tags(self.director)

    def get_plot(self):
        self.plot = gutils.trim(self.page,"<td valign=\"top\" align=\"left\">","</td>")
        self.plot = string.strip(self.plot.decode('latin-1'))
        self.plot = string.replace(self.plot,"<br>", " ")
        self.plot = string.replace(self.plot,"<p>", " ")
        self.plot = string.replace(self.plot,"'","_")
        self.plot = string.strip(gutils.strip_tags(self.plot))

    def get_year(self):
        self.year = gutils.trim(self.page,"<b>Year</b>&nbsp;:&nbsp;","<br>")

    def get_runtime(self):
        self.runtime = gutils.trim(self.page,"<b>Duration</b>&nbsp;:&nbsp;","&nbsp;min")

    def get_genre(self):
        self.genre = gutils.trim(self.page,"<b>Genres</b>&nbsp;:&nbsp;","<br>")
        self.genre = string.replace(self.genre,"&nbsp;-&nbsp;",", ")

    def get_cast(self):
        self.cast = ""
        self.cast = gutils.trim(self.page,"<b>Actors</b>&nbsp;:&nbsp;","<br>")
        self.cast = string.replace(self.cast,"&nbsp;-&nbsp;", "\n")
        self.cast = string.strip(gutils.strip_tags(self.cast))

    def get_classification(self):
        self.classification = ""

    def get_studio(self):
        self.studio = gutils.trim(self.page,"<b>Studio</b>&nbsp;:&nbsp;","<br>")

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = ""

    def get_trailer(self):
        self.trailer = ""

    def get_country(self):
        self.country = gutils.trim(self.page,"<b>Country</b>&nbsp;:&nbsp;","<br>")

    def get_rating(self):
        self.rating = gutils.trim(self.page, "Global rating :&nbsp;<b>","/10</b>&nbsp;")
        if self.rating:
            self.rating = string.replace(self.rating, ",", ".")
        self.rating = str(float(gutils.clean(self.rating)))

class SearchPlugin(movie.SearchMovie):

    def __init__(self):
        self.original_url_search    = "http://www.mediadis.com/dvd/search.asp?t=1&kw=";
        self.translated_url_search    = "http://www.mediadis.com/dvd/search.asp?t=1&kw=";

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        self.sub_search()
        return self.page

    def sub_search(self):
        self.page = gutils.trim(self.page,"Click to sort out", "Result of your research on the criteria")

    def get_searches(self):
        elements = string.split(self.page,"<td rowspan=\"4\" align=\"center\" valign=\"top\" style=\"padding:4px;\">")
        self.number_results = elements[-1]

        if (elements[0]<>''):
            for element in elements:
                self.ids.append(gutils.trim(element,"/dvd/detail.asp?id=","\">"))
                self.titles.append(gutils.convert_entities(gutils.trim(element,"\" class=\"dvd-search-title\">","</a>")))    
        else:
            self.number_results = 0
