# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski

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

import os
import gtk
import tempfile
import shutil
from PIL     import Image
from urllib  import urlcleanup, FancyURLopener, urlretrieve
import logging
log = logging.getLogger("Griffith")
import amazon
import db
import delete
import gutils
import movie

def change_poster(self):
    """
    changes movie poster image to a custom one
    showing a file chooser dialog to select it
    """
    picture = self.widgets['movie']['picture']
    number = self.get_maintree_selection()[0]
    if number is None:
        gutils.error(self,_("You have no movies in your database"), self.widgets['window'])
        return False
    filename = gutils.file_chooser(_("Select image"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK), name="", folder=self.locations['desktop'], picture=True)
    if filename and filename[0]:
        filename = filename[0].decode('UTF-8')
        update_image(self, number, filename)

def update_image(self, number, filename):
    session = self.db.Session()
    try:
        self.widgets['movie']['picture'].set_from_pixbuf(\
                gtk.gdk.pixbuf_new_from_file(filename).scale_simple(100, 140, gtk.gdk.INTERP_BILINEAR))
    except Exception, e:
        log.error(str(e))
        gutils.error(self, _("Image is not valid."), self.widgets['window'])
        return False

    poster_md5 = gutils.md5sum(file(filename, 'rb'))

    movie = session.query(db.Movie).filter_by(number=number).one()
    old_poster_md5 = movie.poster_md5

    if not session.query(db.Poster).filter_by(md5sum=poster_md5).first():
        poster = db.Poster(md5sum=poster_md5, data=file(filename, 'rb').read())
        session.add(poster)

    # update the md5 *after* all other queries (so that UPDATE will not be invoked)
    movie.poster_md5 = poster_md5
    
    if old_poster_md5:
        delete.delete_poster(self, old_poster_md5)

    session.add(movie)
    try:
        session.commit()
    except Exceptionm, e:
        session.rollback()
        log.error("cannot add poster to database: %s" % e)
        return False

    filename = gutils.get_image_fname(poster_md5, self.db, 's')
    if filename:
        update_tree_thumbnail(self, filename)

    self.widgets['movie']['picture_button'].set_sensitive(True)
    self.widgets['add']['delete_poster'].set_sensitive(True)
    self.widgets['menu']['delete_poster'].set_sensitive(True)

    self.update_statusbar(_("Image has been updated"))

def delete_poster(self):
    session = self.db.Session()
    movie = session.query(db.Movie).filter_by(movie_id=self._movie_id).first()
    if not movie:
        log.error("Cannot delete unknown movie's poster!")
        return False
    response = gutils.question(_("Are you sure you want to delete this poster?"), True, self.widgets['window'])
    if response==-8:
        image_path = os.path.join(self.locations['images'], 'default.png')
        handler = self.widgets['movie']['picture'].set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image_path))
        gutils.garbage(handler)
        update_tree_thumbnail(self, os.path.join(self.locations['images'], 'default_thumbnail.png'))
        
        # update in database
        delete.delete_poster(self, movie.poster_md5)
        movie.poster_md5 = None
        session.add(movie)
        try:
            session.commit()
        except Exception, e:
            session.rollback()
            log.error("cannot delete poster: %s" % e)
            return False

        self.update_statusbar(_("Image has been updated"))

        self.widgets['add']['delete_poster'].set_sensitive(False)
        self.widgets['menu']['delete_poster'].set_sensitive(False)
        self.widgets['movie']['picture_button'].set_sensitive(False)
    else:
        pass

def update_tree_thumbnail(self, t_image_path):
    treeselection = self.widgets['treeview'].get_selection()
    (tmp_model, tmp_iter) = treeselection.get_selected()
    self.Image.set_from_file(t_image_path)
    pixbuf = self.Image.get_pixbuf()
    self.treemodel.set_value(tmp_iter, 1, pixbuf)

def fetch_bigger_poster(self):
    match = 0
    log.info("fetching poster from amazon...")
    movie = self.db.session.query(db.Movie).filter_by(movie_id=self._movie_id).first()
    if movie is None:
        gutils.error(self,_("You have no movies in your database"), self.widgets['window'])
        return False
    current_poster_md5 = movie.poster_md5
    if current_poster_md5:
        current_poster = gutils.get_image_fname(current_poster_md5, self.db)
    else:
        current_poster = None
    amazon.setLicense("04GDDMMXX8X9CJ1B22G2")

    locale = self.config.get('amazon_locale', 0, section='add')
    keyword = self.widgets['movie']['o_title'].get_text()
    if locale == '1':
        locale = 'uk'
    elif locale == '2':
        locale = 'de'
        keyword = self.widgets['movie']['title'].get_text()
    elif locale == '3':
        locale = 'ca'
    elif locale == '4':
        locale = 'fr'
    elif locale == '5':
        locale = 'jp'
    else:
        locale = None

    try:
        result = amazon.searchByTitle(keyword, type="Large", product_line="DVD", locale=locale)
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
            result = amazon.searchByKeyword(keyword, type="Large", product_line="DVD", locale=locale)
            if hasattr(result, 'TotalPages'):
                # get next result pages
                pages = int(result.TotalPages)
                page = 2
                while page <= pages and page < 11:
                    tmp = amazon.searchByKeyword(keyword, type='Large', product_line='DVD', locale=locale, page=page)
                    result.Item.extend(tmp.Item)
                    page = page + 1
        log.info("... %s posters found" % result.TotalResults)
    except:
        gutils.warning(self, _("No posters found for this movie."))
        return

    from widgets import connect_poster_signals, reconnect_add_signals
    connect_poster_signals(self, get_poster_select_dc, result, current_poster)

    if not hasattr(result, 'Item') or not len(result.Item):
        gutils.warning(self, _("No posters found for this movie."))
        reconnect_add_signals(self)
        return

    if len(result.Item) == 1:
        o_title = self.widgets['movie']['o_title'].get_text().decode('utf-8')
        if o_title == result.Item[0].ItemAttributes.Title or keyword == result.Item[0].ItemAttributes.Title:
            get_poster(self, 0, result, current_poster)
            return

    self.treemodel_results.clear()
    self.widgets['add']['b_get_from_web'].set_sensitive(False) # disable movie plugins (result window is shared)

    for f in range(len(result.Item)):
        if hasattr(result.Item[f], "LargeImage") and len(result.Item[f].LargeImage.URL):
            title = result.Item[f].ItemAttributes.Title
            if hasattr(result.Item[f].ItemAttributes, 'ProductGroup'):
                title = title + u' - ' + result.Item[f].ItemAttributes.ProductGroup
            elif hasattr(result.Item[f].ItemAttributes, 'Binding'):
                title = title + u' - ' + result.Item[f].ItemAttributes.Binding
            if hasattr(result.Item[f].ItemAttributes, 'ReleaseDate'):
                title = title + u' - ' + result.Item[f].ItemAttributes.ReleaseDate[:4]
            elif hasattr(result.Item[f].ItemAttributes, 'TheatricalReleaseDate'):
                result.Item[f].ItemAttributes.TheatricalReleaseDate[:4]
            if hasattr(result.Item[f].ItemAttributes, 'Studio'):
                title = title + u' - ' + result.Item[f].ItemAttributes.Studio
            myiter = self.treemodel_results.insert_before(None, None)
            self.treemodel_results.set_value(myiter, 0, str(f))
            self.treemodel_results.set_value(myiter, 1, title)

    self.widgets['results']['window'].show()
    self.widgets['results']['window'].set_keep_above(True)

def get_poster_select_dc(self, event, mself, result, current_poster):
    if event.type == gtk.gdk._2BUTTON_PRESS:
        get_poster(mself, None, result)

def get_poster_select(self, mself, result, current_poster):
    get_poster(mself, None, result)

def get_poster(self, f, result):
    from widgets import reconnect_add_signals
    if f is None:
        treeselection = self.widgets['results']['treeview'].get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        if tmp_iter is None:
            return False
        f = int(tmp_model.get_value(tmp_iter, 0))
        self.widgets['results']['window'].hide()

    file_to_copy = tempfile.mktemp(suffix=self.widgets['movie']['number'].get_text(), \
        dir=self.locations['temp'])
    file_to_copy += ".jpg"
    canceled = False
    if len(result.Item[f].LargeImage.URL):
        try:
            progress = movie.Progress(self.widgets['window'],_("Fetching poster"),_("Wait a moment"))
            retriever = movie.Retriever(result.Item[f].LargeImage.URL, self.widgets['window'], progress, file_to_copy)
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
            gutils.warning(self, _("Sorry. A connection error has occurred."))
            try:
                os.remove(file_to_copy)
            except:
                log.error("no permission for %s"%file_to_copy)

    if not canceled:
        if os.path.isfile(file_to_copy):
            try:
                im = Image.open(file_to_copy)
            except IOError:
                log.warn("failed to identify %s"%file_to_copy)

            if im.size == (1,1):
                url = FancyURLopener().open("http://www.amazon.com/gp/product/images/%s" % result.Item[f].ASIN).read()
                if url.find('no-img-sm._V47056216_.gif') > 0:
                    log.warn('No image available')
                    gutils.warning(self, _("Sorry. This movie is listed but has no poster available at Amazon.com."))
                    return False
                url = gutils.after(url, 'id="imageViewerDiv"><img src="')
                url = gutils.before(url, '" id="prodImage"')
                urlretrieve(url, file_to_copy)
                try:
                    im = Image.open(file_to_copy)
                except IOError:
                    log.warn("failed to identify %s"%file_to_copy)

            if im.mode != 'RGB': # convert GIFs
                im = im.convert('RGB')
                im.save(file_to_copy, 'JPEG')
        
            handler = self.widgets['big_poster'].set_from_file(file_to_copy)

            self.widgets['poster_window'].show()
            self.widgets['poster_window'].move(0,0)
            response = gutils.question(_("Do you want to use this poster instead?"), True, self.widgets['window'])
            if response == -8:
                log.info("Using fetched poster, updating and removing old one from disk.")
                update_image(self, self.widgets['movie']['number'].get_text(), file_to_copy)
            else:
                log.info("Reverting to previous poster and deleting new one from disk.")
                try:
                    os.remove(file_to_copy)
                except:
                    log.error("no permission for %s"%file_to_copy)

            self.widgets['poster_window'].hide()
        else:
            gutils.warning(self, _("Sorry. This movie is listed but has no poster available at Amazon.com."))
    reconnect_add_signals(self)

