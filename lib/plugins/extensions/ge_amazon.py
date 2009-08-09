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

import logging
import os
import tempfile
from urllib import urlcleanup, FancyURLopener, urlretrieve

import gtk
from PIL import Image

import gutils
from plugins.extensions import GriffithExtensionBase as Base
from widgets import populate_results_window
from edit import update_image

import amazon

log = logging.getLogger('Griffith')
amazon.setLicense('04GDDMMXX8X9CJ1B22G2')

class GriffithExtension(Base):
    name = 'Amazon'
    description = _('Fetch from Amazon')
    author = 'Piotr Ożarowski'
    email = 'piotr@griffith.cc'
    version = 1
    api = 1

    preferences = {'locale': {'name': _('Select source'),
                              'type': ('US', 'UK', 'DE', 'CA', 'FR', 'JP')}}
    toolbar_icon = 'gtk-network'

    def toolbar_icon_clicked(self, widget, movie):
        log.info('fetching poster from Amazon...')
        self.movie = movie

        if movie is None:
            gutils.error(self.app, _('You have no movies in your database'), self.widgets['window'])
            return False

        locale = self.get_config_value('locale', 'US').lower()

        keyword = movie.o_title
        if locale == 'de':
            keyword = movie.title

        try:
            result = amazon.searchByTitle(keyword, type='Large', product_line='DVD', locale=locale)
            if hasattr(result, 'TotalPages'):
                # get next result pages
                pages = int(result.TotalPages)
                page = 2
                while page <= pages and page < 11:
                    tmp = amazon.searchByTitle(keyword, type='Large', product_line='DVD', locale=locale, page=page)
                    result.Item.extend(tmp.Item)
                    page = page + 1
            if not hasattr(result, 'Item') or not len(result.Item):
                # fallback if nothing is found by title
                result = amazon.searchByKeyword(keyword, type='Large', product_line='DVD', locale=locale)
                if hasattr(result, 'TotalPages'):
                    # get next result pages
                    pages = int(result.TotalPages)
                    page = 2
                    while page <= pages and page < 11:
                        tmp = amazon.searchByKeyword(keyword, type='Large', product_line='DVD', locale=locale, page=page)
                        result.Item.extend(tmp.Item)
                        page = page + 1
            self._result = result
            log.info("... %s posters found" % result.TotalResults)
        except:
            gutils.warning(_('No posters found for this movie.'))
            return

        if not hasattr(result, 'Item') or not len(result.Item):
            gutils.warning(_('No posters found for this movie.'))
            return

        if len(result.Item) == 1:
            o_title = self.widgets['movie']['o_title'].get_text().decode('utf-8')
            if o_title == result.Item[0].ItemAttributes.Title or keyword == result.Item[0].ItemAttributes.Title:
                self.get_poster(self.app, result.Item[0])
                return

        # populate results window
        items = {}
        for i, item in enumerate(result.Item):
            if hasattr(item, 'LargeImage') and len(item.LargeImage.URL):
                title = item.ItemAttributes.Title
                if hasattr(item.ItemAttributes, 'ProductGroup'):
                    title = title + u' - ' + item.ItemAttributes.ProductGroup
                elif hasattr(item.ItemAttributes, 'Binding'):
                    title = title + u' - ' + item.ItemAttributes.Binding
                if hasattr(item.ItemAttributes, 'ReleaseDate'):
                    title = title + u' - ' + item.ItemAttributes.ReleaseDate[:4]
                elif hasattr(item.ItemAttributes, 'TheatricalReleaseDate'):
                    item.ItemAttributes.TheatricalReleaseDate[:4]
                if hasattr(item.ItemAttributes, 'Studio'):
                    title = title + u' - ' + item.ItemAttributes.Studio
                items[i] = title

        populate_results_window(self.app.treemodel_results, items)
        self.widgets['add']['b_get_from_web'].set_sensitive(False) # disable movie plugins (result window is shared)
        self.app._resultswin_process = self.on_result_selected # use this signal (will be reverted when window is closed)
        self.widgets['results']['window'].show()
        self.widgets['results']['window'].set_keep_above(True)

    def on_result_selected(self, key):
        key = int(key)
        if self._result.Item[key].LargeImage.URL:
            poster_file = self.get_poster(self._result.Item[key])
            if poster_file:
                update_image(self.app, self.movie.number, poster_file)
                try:
                    os.remove(poster_file)
                except:
                    log.error('cannot remove %s', poster_file)
        self.widgets['results']['window'].hide()
        self.widgets['add']['b_get_from_web'].set_sensitive(True)

    def get_poster(self, item):
        """Returns file path to the new poster"""

        from movie import Progress, Retriever

        file_to_copy = tempfile.mktemp(suffix=self.widgets['movie']['number'].get_text(), \
            dir=self.locations['temp'])
        file_to_copy += ".jpg"
        canceled = False
        try:
            progress = Progress(self.widgets['window'], _("Fetching poster"), _("Wait a moment"))
            retriever = Retriever(item.LargeImage.URL, self.widgets['window'], progress, file_to_copy)
            retriever.start()
            while retriever.isAlive():
                progress.pulse()
                if progress.status:
                    canceled = True
                while gtk.events_pending():
                    gtk.main_iteration()
            progress.close()
            urlcleanup()
        except:
            canceled = True
            gutils.warning(_("Sorry. A connection error has occurred."))
            try:
                os.remove(file_to_copy)
            except:
                log.error("no permission for %s"%file_to_copy)

        if not canceled:
            if os.path.isfile(file_to_copy):
                im = None
                try:
                    im = Image.open(file_to_copy)
                except IOError:
                    log.warn("failed to identify %s"%file_to_copy)

                if im and im.size == (1,1):
                    url = FancyURLopener().open("http://www.amazon.com/gp/product/images/%s" % item.ASIN).read()
                    if url.find('no-img-sm._V47056216_.gif') > 0:
                        log.warn('No image available')
                        gutils.warning(_("Sorry. This movie is listed but has no poster available at Amazon.com."))
                        return False
                    url = gutils.after(url, 'id="imageViewerDiv"><img src="')
                    url = gutils.before(url, '" id="prodImage"')
                    urlretrieve(url, file_to_copy)
                    try:
                        im = Image.open(file_to_copy)
                    except IOError:
                        log.warn("failed to identify %s", file_to_copy)

                if not im:
                    # something wrong with the image, give some feedback to the user
                    log.warn('No image available')
                    gutils.warning(_("Sorry. This movie is listed but has no poster available at Amazon.com."))
                    return False

                if im.mode != 'RGB': # convert GIFs
                    im = im.convert('RGB')
                    im.save(file_to_copy, 'JPEG')
                # set to None because the file is locked otherwise (os.remove throws an exception)
                im = None

                handler = self.widgets['big_poster'].set_from_file(file_to_copy)

                self.widgets['poster_window'].show()
                self.widgets['poster_window'].move(0,0)
                response = gutils.question(_("Do you want to use this poster instead?"), True, self.widgets['window'])
                if response == -8:
                    return file_to_copy
                else:
                    log.info("Reverting to previous poster and deleting new one from disk.")
                    try:
                        os.remove(file_to_copy)
                    except:
                        log.error('cannot remove %s', file_to_copy)

                self.widgets['poster_window'].hide()
            else:
                gutils.warning(_("Sorry. This movie is listed but has no poster available at Amazon.com."))
        else:
            # cleanup temporary files after canceling the download
            if os.path.isfile(file_to_copy):
                try:
                    os.remove(file_to_copy)
                except:
                    log.error('cannot remove %s', file_to_copy)
