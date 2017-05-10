# -*- coding: UTF-8 -*-

# $Id: PluginMovieMoviefone.py 1113 2009-01-06 21:30:41Z mikej06 $

# Copyright (c) 2005-2009 Vasco Nunes
# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import gutils
import movie,string,re

plugin_name        = "Moviefone"
plugin_description = "A Service of America Online"
plugin_url         = "www.moviefone.de"
plugin_language    = _("English")
plugin_author      = "Vasco Nunes"
plugin_version     = "0.4"

class Plugin(movie.Movie):
    BASEURL = "http://www.moviefone.com/movie/%s"

    def __init__(self, id):
        self.movie_id = id
        self.url = self.BASEURL % self.movie_id + '/main'

    def initialize(self):
        self.page_main     = self.page
        self.page_synopsis = self.open_page(self.parent_window, url = self.BASEURL % self.movie_id + '/synopsis')
        self.page_cast     = self.open_page(self.parent_window, url = self.BASEURL % self.movie_id + '/credits')

    def get_image(self):
        self.image_url = gutils.trim(self.page_main, 'http://www.aolcdn.com/mf_movies/', '"')
        self.image_url = 'http://www.aolcdn.com/mf_movies/' + self.image_url

    def get_o_title(self):
        self.o_title = gutils.trim(self.page_main, '<h1>', '</h1>')

    def get_title(self):
        self.title = gutils.trim(self.page_main, '<h1>', '</h1>')

    def get_director(self):
        self.director = gutils.trim(self.page_main, '<dt>Director(s)</dt>', '</dl>')
        self.director = gutils.strip_tags(self.director.replace('</dd>', ','))
        self.director = re.sub(',[ ]*$', '', self.director)

    def get_plot(self):
        self.plot = gutils.trim(self.page_synopsis, '<h3>Synopsis</h3>', '</p>')
        self.plot = string.strip(gutils.strip_tags(self.plot))

    def get_year(self):
        self.year = gutils.trim(self.page_synopsis, 'Theatrical Release Date:', '<div class="row')
        self.year = string.strip(gutils.strip_tags(self.year))
        self.year = re.sub('[0-9][0-9]/[0-9][0-9]/', '', self.year)

    def get_runtime(self):
        self.runtime = string.strip(gutils.strip_tags(gutils.regextrim(self.page_main, '<dt>Runtime</dt>', ' min[. ]*</dd>')))

    def get_genre(self):
        self.genre = gutils.trim(self.page_synopsis, 'Genre(s):', '<div class="row')
        self.genre = gutils.strip_tags(self.genre)

    def get_cast(self):
        self.cast = ''
        tmp = re.split('(?:[<]div[ \t]+class="name"[>])', self.page_cast)
        for index in range(1, len(tmp), 1):
            entry = tmp[index]
            if string.find(entry, '<h3>Director</h3>') >= 0 or string.find(entry, '<h3>Producer</h3>') >= 0 or string.find(entry, '<h3>Writer</h3>') >= 0:
                break
            name = string.strip(gutils.strip_tags(gutils.before(entry, '</div>')))
            role = string.strip(gutils.strip_tags(gutils.trim(entry, '<div class="role">', '</div>')))
            if role:
                self.cast = self.cast + name + _(' as ') + role + '\n'
            else:
                self.cast = self.cast + name + '\n'

    def get_classification(self):
        self.classification = gutils.trim(self.page_synopsis, 'Rating:', '<div class="row')
        self.classification = gutils.strip_tags(self.classification)

    def get_studio(self):
        self.studio = gutils.trim(self.page_synopsis, 'Production Co.:', '<div class="row')
        self.studio = gutils.strip_tags(self.studio)

    def get_o_site(self):
        self.o_site = ""

    def get_site(self):
        self.site = self.url

    def get_trailer(self):
        self.trailer = ''

    def get_country(self):
        self.country = gutils.trim(self.page_synopsis, 'Country of Origin:', '<div class="row')
        self.country = gutils.strip_tags(self.country)

    def get_rating(self):
        self.rating = '0'
        tmp = gutils.trim(self.page_main, '<dt>Critics Say</dt>', '</dd>')
        parts = re.split('(starAvg3)', tmp)
        if parts and len(parts):
            self.rating = len(parts) - 1

class SearchPlugin(movie.SearchMovie):
    PATTERN = re.compile('<a[ \t]+href="/movie/([^/]+/[0-9]+)/main"[ \t]+class="title">([^<]+)(?:[^(]+)[(]([0-9]+)[)]')
    SUBPAGE_PATTERN = re.compile('(?:movies[?]subCategory=&restrictToCategory=&page=)([0-9]+)')
    
    def __init__(self):
        self.original_url_search   = "http://www.moviefone.com/search/%s/movies";
        self.translated_url_search = "http://www.moviefone.com/search/%s/movies";

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        subpages = self.SUBPAGE_PATTERN.split(self.page)
        if len(subpages) > 4:
            maxsubpage = subpages[len(subpages) - 4]
            completepage = self.page
            try:
                for subpage in range(1, int(maxsubpage) + 1, 1):
                    self.url = "http://www.moviefone.com/search/%s/movies?subCategory=&restrictToCategory=&page=" + str(subpage)
                    if not self.open_search(parent_window):
                        return None
                    completepage = completepage + self.page
            finally:
                self.page = completepage
        return self.page

    def get_searches(self):
        elements = self.PATTERN.split(self.page)

        for index in range(1, len(elements), 4):
            id = elements[index]
            title = elements[index + 1]
            year = elements[index + 2]
            self.ids.append(id)
            self.titles.append(title + ' (' + year + ')')
