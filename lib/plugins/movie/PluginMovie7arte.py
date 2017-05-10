# -*- coding: UTF-8 -*-

__revision__ = '$Id: PluginMovie7arte.py 1138 2009-01-31 21:48:43Z mikej06 $'

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

plugin_name         = "7arte"
plugin_description  = "O cinema em Portugal"
plugin_url          = "7arte.net"
plugin_language     = _("Portuguese")
plugin_author       = "Vasco Nunes"
plugin_author_email = "<vasco.m.nunes@gmail.com>"
plugin_version      = "0.6"

class Plugin(movie.Movie):
    """A movie plugin object"""
    def __init__(self, id):
        self.encode='iso-8859-1'
        self.movie_id = id
        self.url = "http://7arte.net/cgi-bin/filme.pl?codigo=" + str(self.movie_id)

    def get_image(self):
        """Finds the film's poster image"""
        self.image_url = "http://7arte.net/imagens/filmes/" + str(self.movie_id) + ".jpg"

    def get_o_title(self):
        """Finds the film's original title"""
        self.o_title = string.capwords(gutils.trim(self.page, "</B></FONT><BR>", "<BR>"))

    def get_title(self):
        """Finds the film's local title.
        Probably the original title translation"""
        self.title = string.capwords(gutils.trim(self.page, "<FONT SIZE=+1><B>", "</B>"))

    def get_director(self):
        """Finds the film's director"""
        self.director = gutils.trim(self.page, "</B> <FONT SIze=-1>", "</FONT><TABLE><TR>")
        self.director = gutils.strip_tags(self.director)

    def get_plot(self):
        """Finds the film's plot"""
        self.plot = gutils.trim(self.page, "<B>Sinopse:</B><BR>", "<Font Size=-2>[ www.7arte.net ]</font></FONT></P>")

    def get_year(self):
        """Finds the film's year"""
        self.year = gutils.trim(self.page, "<B>Ano:</B> <FONT SIze=-1>", "</FONT>")

    def get_runtime(self):
        """Finds the film's running time"""
        self.runtime = gutils.trim(self.page, "<B>Dura", " minutos")
        self.runtime = gutils.after(self.runtime, "-1>")

    def get_genre(self):
        """Finds the film's genre"""
        self.genre = gutils.trim(self.page, "nero:</B> <FONT SIze=-1>", "</FONT><BR>")

    def get_cast(self):
        self.cast = gutils.trim(self.page, "<B>Actores:</B>", "</FONT></TD>")
        self.cast = string.replace(self.cast, u"<B>»</B> ", "")

    def get_classification(self):
        """Find the film's classification"""
        self.classification = gutils.trim(self.page, "<B>Idade:</B> <FONT SIze=-1>", "</FONT>")

    def get_studio(self):
        """Find the studio"""
        self.studio = gutils.trim(self.page, "<B>Distribuidora:</B> <FONT SIze=-1>", "</FONT>")

    def get_o_site(self):
        """Find the film's oficial site"""
        self.o_site = gutils.trim(self.page, \
            "<A HREF='", \
            "' TARGET=_blank><IMG SRC='/imagens/bf_siteoficial.gif'")

    def get_site(self):
        """Find the film's imdb details page"""
        self.site = gutils.trim(self.page, \
            "/imagens/bf_siteoficial.gif' WIDTH=89 HEIGHT=18 BORDER=0 ALT=''>", \
            "' TARGET=_blank><IMG SRC='/imagens/bf_imdb.gif'")
        self.site = gutils.after(self.site, "<A HREF='")
        self.site = string.replace(self.site, "'", "")

    def get_trailer(self):
        """Find the film's trailer page or location"""
        self.trailer = gutils.trim(self.page, \
            "/imagens/bf_imdb.gif' WIDTH=89 HEIGHT=18 BORDER=0 ALT=''>", \
            "' TARGET=_blank><IMG SRC='/imagens/bf_trailer.gif'")
        self.trailer = gutils.after(self.trailer, "<A HREF='")

    def get_country(self):
        """Find the film's country"""
        self.country = gutils.trim(self.page, "s de Origem:</B> <FONT SIze=-1>", "</FONT><BR>")

    def get_rating(self):
        """Find the film's rating. From 0 to 10.
        Convert if needed when assigning."""
        tmp_rating = gutils.trim(self.page, "ticas por:</B></Center>", "c_critica.pl?id=")
        if tmp_rating:
            self.rating = str(float(string.count(tmp_rating, 'estrela.gif'))*2)

class SearchPlugin(movie.SearchMovie):
    """A movie search object"""
    def __init__(self):
        self.original_url_search   = "http://7arte.net/cgi-bin/arq_search_orig.pl?proc="
        self.translated_url_search = "http://7arte.net/cgi-bin/arq_search.pl?proc="
        self.encode                = 'iso-8859-1'

    def search(self, parent_window):
        """Perform the web search"""
        if not self.open_search(parent_window):
            return None
        self.sub_search()
        return self.page

    def sub_search(self):
        """Isolating just a portion (with the data we want) of the results"""
        self.page = gutils.trim(self.page, \
            "Resultados Encontrados</I></B></FONT>", "</DIR></FONT>")

    def get_searches(self):
        """Try to find both id and film title for each search result"""
        elements = string.split(self.page, "</A><BR>")
        self.number_results = elements[-1]

        if (len(elements[0])):
            for element in elements:
                self.ids.append(gutils.trim(element, "codigo=", "')"))
                self.titles.append(gutils.convert_entities \
                    (gutils.trim(element, "')\">", " )")) + " )")
        else:
            self.number_results = 0

