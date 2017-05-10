# -*- coding: UTF-8 -*-

__revision__ = '$Id: ge_movieposterdb.py 1624 2012-06-07 19:07:22Z mikej06 $'

# Copyright © 2010 Michael Jahn
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

import os
import logging
from urllib import quote, urlcleanup
import gtk
import gutils
from edit import update_image_from_memory
from movie import Progress, Retriever
from plugins.extensions import GriffithExtensionBase as Base

log = logging.getLogger('Griffith')


class GriffithExtension(Base):
    name = 'MoviePosterDB'
    description = _('Fetch posters from MoviePosterDB.com')
    author = 'Michael Jahn'
    email = 'mike@griffith.cc'
    version = 1
    api = 1
    enabled = True

    toolbar_icon = 'ge_movieposterdb.png'

    baseurltitle = 'http://www.movieposterdb.com/embed.inc.php?movie_title=%s'
    baseurltitleyear = 'http://www.movieposterdb.com/embed.inc.php?movie_title=%s[%s]'

    progress = None

    def toolbar_icon_clicked(self, widget, movie):
        log.info('fetching poster from MoviePosterDB.com...')
        self.movie = movie

        # correction of the movie name for the search
        o_title = None
        title = None
        if movie.o_title:
            if movie.o_title.endswith(', The'):
                o_title = u"The %s" % movie.o_title[:-5]
            else:
                o_title = movie.o_title
        if movie.title:
            if movie.title.endswith(', The'):
                title = u"The %s" % movie.title[:-5]
            else:
                title = movie.title

        # try to get an url to the large version of a poster for the movie
        # (requests are in the order:
        #  original title + year, original title only, title + year, title only)
        try:
            largeurl = None
            data = False
            if o_title:
                if movie.year:
                    url = self.baseurltitleyear % (o_title, movie.year)
                    data = self._get(url, self.widgets['window'])
                    if data and data.find('movie/0000000') < 0:
                        largeurl = gutils.trim(data, 'src=\\"', '\\"').replace('/t_', '/l_')
                if not data or not largeurl:
                    url = self.baseurltitle % o_title
                    data = self._get(url, self.widgets['window'])
                    if data and data.find('movie/0000000') < 0:
                        largeurl = gutils.trim(data, 'src=\\"', '\\"').replace('/t_', '/l_')
            if not data or not largeurl and title and title != o_title:
                if movie.year:
                    url = self.baseurltitleyear % (title, movie.year)
                    data = self._get(url, self.widgets['window'])
                    if data and data.find('movie/0000000') < 0:
                        largeurl = gutils.trim(data, 'src=\\"', '\\"').replace('/t_', '/l_')
                if not data or not largeurl:
                    url = self.baseurltitle % title
                    data = self._get(url, self.widgets['window'])
                    if data and data.find('movie/0000000') < 0:
                        largeurl = gutils.trim(data, 'src=\\"', '\\"').replace('/t_', '/l_')
        except:
            log.exception('')
            gutils.warning(_('No posters found for this movie.'))
            return

        if not data or not largeurl:
            gutils.warning(_('No posters found for this movie.'))
            return

        # got the url for a large poster, fetch the data, show preview and update the
        # movie entry if the user want it
        data = self._get(largeurl, self.widgets['window'], decode=False)
        if not data:
            gutils.warning(_('No posters found for this movie.'))
            return

        if self._show_preview(data):
            update_image_from_memory(self.app, movie.number, data)

    def _show_preview(self, data):
        loader = gtk.gdk.PixbufLoader()
        loader.write(data, len(data))
        loader.close()
        # show before set_from_pixbuf because it doesn't resize otherwise
        self.widgets['poster_window'].show()
        handler = self.widgets['big_poster'].set_from_pixbuf(loader.get_pixbuf())
        result = gutils.question(_("Do you want to use this poster instead?"), self.widgets['window'])
        self.widgets['poster_window'].hide()
        return result

    def _get(self, url, parent_window, decode=True):
        # initialize the progress dialog once for the following search process
        if not self.progress:
            self.progress = Progress(parent_window)

        data = None
        url = url.encode('utf-8', 'replace')
        log.debug('Using url <%s>', url)
        self.progress.set_data(parent_window, _('Searching'), _('Wait a moment'), True)
        try:
            retriever = Retriever(url, parent_window, self.progress)
            retriever.start()
            while retriever.isAlive():
                self.progress.pulse()
                if self.progress.status:
                    retriever.join()
                while gtk.events_pending():
                    gtk.main_iteration()
            try:
                if retriever.html:
                    ifile = file(retriever.html[0], 'rb')
                    try:
                        data = ifile.read()
                    finally:
                        ifile.close()
                    # check for gzip compressed pages before decoding to unicode
                    if len(data) > 2 and data[0:2] == '\037\213':
                        data = gutils.decompress(data)
                    if decode:
                        data = data.decode('utf-8', 'replace')
                    os.remove(retriever.html[0])
            except IOError:
                log.exception('')
        finally:
            self.progress.hide()
        urlcleanup()
        return data
