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
from sqlalchemy import select, desc
from sqlalchemy.sql.expression import Select

import db
import gutils
import sql

log = logging.getLogger("Griffith")

def treeview_clicked(self):
    if self.initialized is False:
        return False
    if self.total:
        treeselection = self.widgets['treeview'].get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        if tmp_iter is None:
            log.info('Treeview: no selection')
            return False
        number = tmp_model.get_value(tmp_iter,0)
        movie = self.db.session.query(db.Movie).filter_by(number=number).first()
        if movie is None:
            log.info("Treeview: movie doesn't exists (number=%s)", number)
        elif movie.poster_md5 and self.widgets['poster_window'].flags() & gtk.VISIBLE == gtk.VISIBLE:
            # poster window is visible
            filename = gutils.get_image_fname(movie.poster_md5, self.db)
            self.widgets['big_poster'].set_from_file(filename)
        for ext in self.extensions:
            ext.maintree_clicked(treeselection, movie)
        set_details(self, movie)
    else:
        set_details(self, {})

def set_details(self, item=None):#{{{
    if item is None:
        item = {}
    if 'movie_id' in item and item['movie_id']:
        self._movie_id = item['movie_id']
    else:
        self._movie_id = None
    w = self.widgets['movie']

    if 'number' in item and item['number']:
        w['number'].set_text(str(int(item['number'])))
    else:
        w['number'].set_text('')
    if 'title' in item and item['title']:
        w['title'].set_markup("<b><span size='large'>%s</span></b>" % gutils.html_encode(item['title']))
    else:
        w['title'].set_text('')
    if 'o_title' in item and item['o_title']:
        w['o_title'].set_markup("<span size='medium'><i>%s</i></span>" % gutils.html_encode(item['o_title']))
    else:
        w['o_title'].set_text('')
    if 'director' in item and item['director']:
        w['director'].set_markup("<i>%s</i>" % gutils.html_encode(item['director']))
    else:
        w['director'].set_text('')
    if 'plot' in item and item['plot']:
        w['plot'].set_text(str(item['plot']))
    else:
        w['plot'].set_text('')
    if 'year' in item and item['year']:
        w['year'].set_text(str(item['year']))
    else:
        w['year'].set_text('')
    if False: # FIXME: add a field in main window
    #if 'resolution' in item and item['resolution']:
        if self.config.get('use_resolution_alias', True):
            w['resolution'].set_text(item['resolution'])
        elif 'height' in item and item['height'] and 'width' in item and item['width']:
            w['resolution'].set_text("%dx%d" % (item['width'], item['height']))
        else: # failback to 'resolution'
            w['resolution'].set_text(item['resolution'])
    else:
        #w['resolution'].set_text('') # FIXME: add a field in main window
        pass
    if 'runtime' in item and item['runtime']:
        w['runtime'].set_text(str(int(item['runtime'])))
    else:
        w['runtime'].set_text('x')
    if 'cameraman' in item and item['cameraman']:
        w['cameraman'].set_markup("<i>%s</i>" % gutils.html_encode(item['cameraman']))
    else:
        w['cameraman'].set_text('')
    if 'screenplay' in item and item['screenplay']:
        w['screenplay'].set_markup("<i>%s</i>" % gutils.html_encode(item['screenplay']))
    else:
        w['screenplay'].set_text('')
    if 'cast' in item and item['cast']:
        w['cast'].set_text(str(item['cast']))
    else:
        w['cast'].set_text('')
    if 'country' in item and item['country']:
        w['country'].set_markup("<i>%s</i>" % gutils.html_encode(item['country']))
    else:
        w['country'].set_text('')
    if 'genre' in item and item['genre']:
        w['genre'].set_markup("<i>%s</i>" % gutils.html_encode(item['genre']))
    else:
        w['genre'].set_text('')
    if 'cond' in item and item['cond']:
        if str(item['cond']) in [ str(i) for i in range(len(self._conditions)) ]:
            w['condition'].set_markup("<i>%s</i>" % self._conditions[item['cond']])
        else:
            w['condition'].set_text('')
            log.info("Wrong value in 'condition' field (movie_id=%s, cond=%s)" % (item['movie_id'], item['cond']))
    else:
        w['condition'].set_text('')
    if 'region' in item and item['region']:
        if str(item['region']) in [ str(i) for i in range(len(self._regions)) ]:
            w['region'].set_markup("<i>%s</i>" % gutils.html_encode(item['region']))
            if int(item['region']) < 9:
                self.widgets['tooltips'].set_tip(w['region'], self._regions[int(item['region'])])
        else:
            log.info("Wrong value in 'region' field (movie_id=%s, region=%s)" % (item['movie_id'], item['region']))
            w['region'].set_text('')
            self.widgets['tooltips'].set_tip(w['region'], self._regions[0]) # N/A
    else:
        w['region'].set_text('')
        self.widgets['tooltips'].set_tip(w['region'], self._regions[0]) # N/A
    if 'layers' in item and item['layers']:
        if str(item['layers']) in [ str(i) for i in range(len(self._layers)) ]:
            w['layers'].set_markup("<i>%s</i>" % self._layers[item['layers']])
        else:
            log.info("Wrong value in 'layers' field (movie_id=%s, layers=%s)" % (item['movie_id'], item['layers']))
            w['layers'].set_text('')
    else:
        w['layers'].set_text('')
    if 'color' in item and item['color']:
        if str(item['color']) in [ str(i) for i in range(len(self._colors)) ]:
            w['color'].set_markup("<i>%s</i>" % self._colors[item['color']])
        else:
            log.info("Wrong value in 'color' field (movie_id=%s, color=%s)" % (item['movie_id'], item['color']))
            w['color'].set_markup('')
    else:
        w['color'].set_markup('')
    if 'classification' in item and item['classification']:
        w['classification'].set_markup("<i>%s</i>" % gutils.html_encode(item['classification']))
    else:
        w['classification'].set_text('')
    if 'studio' in item and item['studio']:
        w['studio'].set_markup("<i>%s</i>" % gutils.html_encode(item['studio']))
    else:
        w['studio'].set_text('')
    if 'o_site' in item and item['o_site']:
        self._o_site_url = str(item['o_site'])
        w['go_o_site_button'].set_sensitive(True)
    else:
        self._o_site_url = None
        w['go_o_site_button'].set_sensitive(False)
    if 'site' in item and item['site']:
        self._site_url = str(item['site'])
        w['go_site_button'].set_sensitive(True)
    else:
        self._site_url = None
        w['go_site_button'].set_sensitive(False)
    if 'trailer' in item and item['trailer']:
        self._trailer_url = str(item.trailer)
        w['go_trailer_button'].set_sensitive(True)
    else:
        self._trailer_url = None
        w['go_trailer_button'].set_sensitive(False)
    if 'seen' in item and item['seen'] == True:
        w['seen_icon'].set_from_file(os.path.join(self.locations['images'], 'seen.png'))
    else:
        w['seen_icon'].set_from_file(os.path.join(self.locations['images'], 'unseen.png'))
    if 'notes' in item and item['notes']:
        w['notes'].set_text(str(item.notes))
    else:
        w['notes'].set_text('')
    tmp = ''
    if 'media_num' in item and item['media_num']:
        tmp = str(item.media_num)
    else:
        tmp = '0'
    if 'medium_id' in item and item['medium_id']:
        if item.medium is not None:
            tmp += ' x ' + item.medium.name
        else:
            pass
    w['medium'].set_markup("<i>%s</i>" % gutils.html_encode(tmp))
    if 'vcodec_id' in item:
        if item.vcodec is not None:
            w['vcodec'].set_markup("<i>%s</i>" % gutils.html_encode(item.vcodec.name))
        else:
            w['vcodec'].set_text('')
    else:
        w['vcodec'].set_text('')
    if 'ratio_id' in item:
        if item.ratio is not None:
            w['ratio'].set_markup("<i>%s</i>" % gutils.html_encode(item.ratio.name))
        else:
            w['ratio'].set_text('')
    else:
        w['ratio'].set_text('')

    # poster
    if 'poster_md5' in item and item['poster_md5']:
        filename = gutils.get_image_fname(item['poster_md5'], self.db, 'm')
        if filename and os.path.isfile(filename):
            image_path = filename
            self.widgets['add']['delete_poster'].set_sensitive(True)
            w['picture_button'].set_sensitive(True)
        else:
            image_path = os.path.join(self.locations['images'], 'default.png')
            self.widgets['add']['delete_poster'].set_sensitive(False)
            w['picture_button'].set_sensitive(False)
    else:
        image_path = os.path.join(self.locations['images'], 'default.png')
        w['picture_button'].set_sensitive(False)
    w['picture'].set_from_file(image_path)
    # ratig
    rimage = int(self.config.get('rating_image', 0))
    if rimage:
        prefix = ''
    else:
        prefix = 'meter'
    if 'rating' in item and item['rating']:
        rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, item['rating'])
    else:
        rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, 0)
    handler = w['image_rating'].set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(rating_file))
    gutils.garbage(handler)

    # check loan status and adjust buttons and history box
    if 'loaned' in item and item['loaned'] is True:
        self.widgets['popups']['loan'].set_sensitive(False)
        self.widgets['popups']['email'].set_sensitive(True)
        self.widgets['popups']['return'].set_sensitive(True)
        self.widgets['menu']['loan'].set_sensitive(False)
        self.widgets['menu']['email'].set_sensitive(True)
        self.widgets['menu']['return'].set_sensitive(True)
        w['loan_button'].set_sensitive(False)
        w['email_reminder_button'].set_sensitive(True)
        w['return_button'].set_sensitive(True)
        
        if getattr(item, 'loan_details', None) is None:
            log.warning("movie has no loan data, changing 'loaned' flag to False (movie_id: %s)", item['movie_id'])
            item.loaned = False
        else:
            self.person_name = item.loan_details.person.name
            self.person_email = item.loan_details.person.email
            self.loan_date = str(item.loan_details.date)
            w['loan_info'].set_use_markup(False)
            w['loan_info'].set_label(_("This movie has been loaned to %s on %s") % (self.person_name, self.loan_date[:10]))
    if 'loaned' in item and not item['loaned']: # "loaned" status can be changed above, so don't use "else:" in this line
        self.widgets['popups']['loan'].set_sensitive(True)
        self.widgets['popups']['email'].set_sensitive(False)
        self.widgets['popups']['return'].set_sensitive(False)
        self.widgets['menu']['loan'].set_sensitive(True)
        self.widgets['menu']['email'].set_sensitive(False)
        self.widgets['menu']['return'].set_sensitive(False)
        w['return_button'].set_sensitive(False)
        w['email_reminder_button'].set_sensitive(False)
        w['loan_button'].set_sensitive(True)
        w['loan_info'].set_markup("<b>%s</b>" % _("Movie not loaned"))

    # loan history    
    self.loans_treemodel.clear()
    if getattr(item, 'loan_history', None) is not None:
        for loan in item.loan_history:
            myiter = self.loans_treemodel.append(None)
            self.loans_treemodel.set_value(myiter, 0,'%s' % str(loan.date)[:10])
            if loan.return_date and  loan.return_date != '':
                self.loans_treemodel.set_value(myiter, 1, str(loan.return_date)[:10])
            else:
                self.loans_treemodel.set_value(myiter, 1, "---")
            person = self.db.session.query(db.Person.name).filter_by(person_id=loan.person.person_id).first()
            self.loans_treemodel.set_value(myiter, 2, person.name)

    # volumes/collections
    if 'volume_id' in item and item['volume_id']>0:
        if 'volume' in item and item['volume']:
            w['volume'].set_markup("<b>%s</b>" % gutils.html_encode(item['volume'].name))
            w['show_volume_button'].set_sensitive(True)
        else:
            w['volume'].set_text('')
            w['show_volume_button'].set_sensitive(False)
    else:
            w['volume'].set_text('')
            w['show_volume_button'].set_sensitive(False)
    if 'collection_id' in item and item['collection_id']>0:
        if 'collection' in item and item['collection']:
            w['collection'].set_markup("<b>%s</b>" % gutils.html_encode(item['collection'].name))
            w['show_collection_button'].set_sensitive(True)
        else:
            w['collection'].set_text('')
            w['show_collection_button'].set_sensitive(False)
    else:
        w['collection'].set_text('')
        w['show_collection_button'].set_sensitive(False)

    # languages
    for i in w['audio_vbox'].get_children():
        i.destroy()
    for i in w['subtitle_vbox'].get_children():
        i.destroy()
    if 'languages' in item and len(item['languages'])>0:
        for i in item['languages']:
            if i.type == 3: # subtitles
                if i.subformat:
                    tmp = "%s - %s" % (i.language.name, i.subformat.name)
                else:
                    tmp = "%s" % i.language.name
                w['subtitle_vbox'].pack_start(gtk.Label(tmp))
            else:
                language = i.language.name
                if i.type is not None and len(self._lang_types[i.type])>0:
                    language += " <i>%s</i>" % self._lang_types[i.type]
                tmp = ''
                if i.achannel:
                    tmp = i.achannel.name
                if i.acodec:
                    if len(tmp)>0:
                        tmp += ", %s" % i.acodec.name
                    else:
                        tmp = i.acodec.name
                if len(tmp)>0:
                    tmp = "%s (%s)" % (language, tmp)
                else:
                    tmp = language
                widget = gtk.Label(tmp)
                widget.set_use_markup(True)
                w['audio_vbox'].pack_start(widget)
    w['audio_vbox'].show_all()
    w['subtitle_vbox'].show_all()
    #tags
    if 'tags' in item:
        tmp = ''
        for tag in item['tags']:
            tmp += "%s, " % tag.name
        tmp = tmp[:-2] # cut last comma
        w['tags'].set_text(tmp)
    #}}}
    
def populate(self, movies=None, where=None, qf=True):#{{{
    if self.initialized is False: # dont try to fill movie list if Griffith is not initialized yet
        return False
    
    if qf and not movies or isinstance(movies, Select): # if ".execute().fetchall()" not invoked on movies yet
        if not where: # due to possible 'seen', 'loaned', 'collection_id' in where
            import advfilter
            
            # saved in advfilter
            name = self.widgets['filter']['advfilter'].get_active_text()[:-3].decode('utf-8') # :-3 due to additional '   ' in the name
            if name:
                cond = self.db.session.query(db.Filter).filter_by(name=name).first()
                if not cond:
                    cond = advfilter.get_def_conditions()
                else:
                    cond = cond.data
            else:
                cond = advfilter.get_def_conditions()
            # add sorting from config
            sort_column_name = self.config.get('sortby', 'number', section='mainlist')
            sort_reverse = self.config.get('sortby_reverse', False, section='mainlist')
            if sort_reverse:
                cond['sort_by'] = set((sort_column_name + ' DESC', ))
            else:
                cond['sort_by'] = set((sort_column_name, ))

            # seen / loaned
            if self.widgets['menu']['loaned_movies'].get_active():
                cond['loaned'] = True
            if self.widgets['menu']['not_seen_movies'].get_active():
                cond["seen"] = False
            # collection
            pos = self.widgets['filter']['collection'].get_active()
            if pos >= 0:
                col_id = self.collection_combo_ids[pos]
                if col_id > 0:
                    cond["collections"].add(col_id)

            movies = advfilter.create_select_query(self, None, cond, movies)
        else:
            # select sort column
            sort_column_name = self.config.get('sortby', 'number', section='mainlist')
            sort_reverse = self.config.get('sortby_reverse', False, section='mainlist')
            # explicit conditions, only empty dictionary needed to add the order by values
            cond = {}
            if sort_reverse:
                cond['sort_by'] = set((sort_column_name + ' DESC', ))
            else:
                cond['sort_by'] = set((sort_column_name, ))
            movies = sql.update_whereclause(movies, cond)
        
        # additional whereclause (volume_id, collection_id, ...)
        if where:
            for i in where:
                if i in db.Movie:
                    movies.append_whereclause(db.Movie[i]==where[i])
        movies = movies.execute().fetchall()

    self.total = len(movies)
    # disable refreshing while inserting
    self.widgets['treeview'].freeze_child_notify()
    self.widgets['treeview'].set_model(None)

    # save user sort column
    sort_column_id, order = self.treemodel.get_sort_column_id()

    # new treemodel (faster and prevents some problems)
    self.treemodel = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, str, str, str, bool, str, str, int)

    # check preferences to hide or show columns
    if self.config.get('number', True, 'mainlist') == True:
        self.number_column.set_visible(True)
    else:
        self.number_column.set_visible(False)
    if self.config.get('otitle', True, 'mainlist') == True:
        self.otitle_column.set_visible(True)
    else:
        self.otitle_column.set_visible(False)
    if self.config.get('title', True, 'mainlist') == True:
        self.title_column.set_visible(True)
    else:
        self.title_column.set_visible(False)
    if self.config.get('director', True, 'mainlist') == True:
        self.director_column.set_visible(True)
    else:
        self.director_column.set_visible(False)
    if self.config.get('image', True, 'mainlist') == True:
        self.image_column.set_visible(True)
    else:
        self.image_column.set_visible(False)
    if self.config.get('genre', True, 'mainlist') == True:
        self.genre_column.set_visible(True)
    else:
        self.genre_column.set_visible(False)
    if self.config.get('seen', True, 'mainlist') == True:
        self.seen_column.set_visible(True)
    else:
        self.seen_column.set_visible(False)
    if self.config.get('year', True, 'mainlist') == True:
        self.year_column.set_visible(True)
    else:
        self.year_column.set_visible(False)
    if self.config.get('runtime', True, 'mainlist') == True:
        self.runtime_column.set_visible(True)
    else:
        self.runtime_column.set_visible(False)
    if self.config.get('rating', True, 'mainlist') == True:
        self.rating_column.set_visible(True)
    else:
        self.rating_column.set_visible(False)
        
    for movie in movies:
        myiter = self.treemodel.append(None)
        
        self.treemodel.set_value(myiter,0,'%004d' % int(movie.number))

        if self.config.get('image', True, section='mainlist') == True:
            filename = None
            if movie.poster_md5:
                filename = gutils.get_image_fname(movie.poster_md5, self.db, "s")
            if not filename:
                filename = os.path.join(self.locations['images'], 'default_thumbnail.png')

            self.Image.set_from_file(filename)
            pixbuf = self.Image.get_pixbuf()
            self.treemodel.set_value(myiter, 1, pixbuf)
        self.treemodel.set_value(myiter,2,movie.o_title)
        self.treemodel.set_value(myiter,3,movie.title)
        self.treemodel.set_value(myiter,4,movie.director)
        self.treemodel.set_value(myiter,5,movie.genre)
        self.treemodel.set_value(myiter,6,movie.seen)
        if movie.year is not None and (isinstance(movie.year, int) or isinstance(movie.year, long)):
            self.treemodel.set_value(myiter,7,movie.year)
        if movie.runtime is not None and (isinstance(movie.runtime, int) or isinstance(movie.runtime, long)):
            self.treemodel.set_value(myiter,8, '%003d' % movie.runtime + _(' min'))
        if movie.rating is not None and (isinstance(movie.rating, int) or isinstance(movie.rating, long)):
            self.treemodel.set_value(myiter,9,movie.rating)

    # restore user sort column
    if sort_column_id is not None:
        self.treemodel.set_sort_column_id(sort_column_id, gtk.SORT_ASCENDING)
    
    # add new treemodel and allow refreshs again
    self.widgets['treeview'].set_model(self.treemodel)
    self.widgets['treeview'].thaw_child_notify()
    self.widgets['treeview'].set_cursor_on_cell(0)
    self.count_statusbar()
#}}}

# vim: fdm=marker
