# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ożarowski

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

import logging
import os

import gtk

import db
import delete
import gutils

log = logging.getLogger("Griffith")

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

    if session.query(db.Poster).filter_by(md5sum=poster_md5).count() == 0:
        poster = db.Poster(md5sum=poster_md5, data=file(filename, 'rb').read())
        session.add(poster)

    # update the md5 *after* all other queries (so that UPDATE will not be invoked)
    movie.poster_md5 = poster_md5
    
    if old_poster_md5:
        delete.delete_poster(self, old_poster_md5)

    session.add(movie)
    try:
        session.commit()
    except Exception, e:
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

