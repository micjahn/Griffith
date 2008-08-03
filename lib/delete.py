# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski
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

import os
import gettext
gettext.install('griffith', unicode=1)
import logging
log = logging.getLogger("Griffith")
import gutils
import db

def delete_movie(self):
    m_id = None
    number, m_iter = self.get_maintree_selection()
    movie = self.db.session.query(db.Movie).filter_by(number=number).first()
    if movie is None:
        gutils.error(self,_("You have no movies in your database"), self.widgets['window'])
        return False
    
    if int(movie.loaned)==1:
        gutils.warning(self, msg=_("You can't delete movie while it is loaned."))
        return False

    response = gutils.question(self, _("Are you sure you want to delete this movie?"), \
        1, self.widgets['window'])
    if response == -8:    # gtk.RESPONSE_YES == -8
        delete_poster(self, movie.poster_md5)

        self.db.session.delete(movie)
        try:
            self.db.session.commit()
        except:
            log.info("Unexpected problem: %s" % e)
            return False

        # update main treelist
        self.total -= 1
        self.clear_details()
        self.initialized = False
        self.go_prev()
        self.treemodel.remove(m_iter)
        self.initialized = True
        self.go_next()
        self.count_statusbar()
    else:
        return False

def delete_poster(self, md5sum, commit=False):
    poster = self.db.session.query(db.Poster).filter_by(md5sum=md5sum).first()
    if poster and len(poster.movies) <= 1: # other movies are not using the same poster
        self.db.session.delete(poster)
        if commit:
            try:
                self.db.session.commit()
            except Exception, e:
                log.warn("cannot delete poster from db: %s" % e)
                self.db.session.rollback()
                return False

    delete_poster_from_cache(self, md5sum)
    return True

def delete_poster_from_cache(self, md5sum):
    if not md5sum:
        log.info('Delete poster: no poster to delete')
        return False

    posters_dir = os.path.join(self.locations['posters'])

    image_full = os.path.join(posters_dir, md5sum+".jpg")
    image_small = os.path.join(posters_dir, md5sum+"_s.jpg")
    image_medium = os.path.join(posters_dir, md5sum+"_m.jpg")

    if os.path.isfile(image_small):
        try:
            os.remove(image_small)
        except:
            log.info("Can't remove %s file" % image_small)
    if os.path.isfile(image_medium):
        try:
            os.remove(image_medium)
        except:
            log.info("Can't remove %s file" % image_medium)
    if os.path.isfile(image_full):
        try:
            os.remove(image_full)
        except:
            log.info("Can't remove %s file" % image_full)

