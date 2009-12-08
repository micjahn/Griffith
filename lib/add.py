# -*- coding: UTF-8 -*-
# vim: fdm=marker

__revision__ = '$Id$'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ożarowski
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

import gtk
from sqlalchemy.exceptions import IntegrityError

import quick_filter
import db
import gutils

log = logging.getLogger("Griffith")

### widgets ###################################################

def clear(self):
    """clears all fields in dialog"""
    set_details(self, {})
    self.widgets['add']['cb_only_empty'].set_active(False)


def add_movie(self, details={}):
    set_details(self, details)
    
    self.active_plugin = ''
    self.widgets['add']['add_button'].show()
    self.widgets['add']['add_close_button'].show()
    self.widgets['add']['clear_button'].show()
    self.widgets['add']['save_button'].hide()
    self.widgets['add']['window'].set_title(_('Add a new movie'))
    self.widgets['add']['window'].show()


def edit_movie(self, details={}):
    if not 'number' in details:
        details['number'] = gutils.find_next_available(self.db)
    set_details(self, details)
    self.widgets['add']['add_button'].hide()
    self.widgets['add']['add_close_button'].hide()
    self.widgets['add']['clear_button'].hide()
    self.widgets['add']['save_button'].show()
    self.widgets['add']['window'].set_title(_('Edit movie'))
    self.widgets['add']['window'].show()


def update_movie(self):
    session = self.db.Session()

    if self._am_movie_id is not None:
        movie = session.query(db.Movie).filter_by(movie_id=self._am_movie_id).one()
    else:
        movie = session.query(db.Movie).filter_by(movie_id=self._movie_id).one()
    if movie is None: # movie was deleted in the meantime
        return add_movie_db(self, True)
    
    details = get_details(self)

    old_poster_md5 = movie.poster_md5
    new_poster_md5 = None
    if details['image'] and old_poster_md5 != details['image']: # details["image"] can contain MD5 or file path
        new_image_path = os.path.join(self.locations['temp'], "poster_%s.jpg" % details['image'])
        if not os.path.isfile(new_image_path):
            log.warn("cannot read temporary file: %s", new_image_path)
        else:
            new_poster_md5 = gutils.md5sum(file(new_image_path, 'rb'))
            details["poster_md5"] = new_poster_md5
            if session.query(db.Poster).filter_by(md5sum=new_poster_md5).count() == 0:
                try:
                    data = file(new_image_path, 'rb').read()
                except Exception, e:
                    log.warning("cannot read poster data")
                else:
                    poster = db.Poster(md5sum=new_poster_md5, data=data)
                    del details["image"]
                    details['poster_md5'] = new_poster_md5
                    session.add(poster)

                    # delete old image
                    import delete
                    old_poster = session.query(db.Poster).filter_by(md5sum=old_poster_md5).first()
                    if old_poster and len(old_poster.movies) == 1: # other movies are not using the same poster
                        session.delete(old_poster)
                        delete.delete_poster_from_cache(self, old_poster_md5)

    update_movie_instance(movie, details, session)
    
    session.add(movie)
    if commit(session):
        treeselection = self.widgets['treeview'].get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        
        if new_poster_md5 and new_poster_md5 != old_poster_md5:
            # update thumbnail in main list
            new_image_path = gutils.get_image_fname(new_poster_md5, self.db, 's')
            if not new_image_path:
                new_image_path = gutils.get_defaultthumbnail_fname(self)
            handler = self.Image.set_from_file(new_image_path)
            pixbuf = self.Image.get_pixbuf()
            tmp_model.set_value(tmp_iter,1, pixbuf)
        # update main treelist
        tmp_model.set_value(tmp_iter,0,'%004d' % int(movie.number))
        tmp_model.set_value(tmp_iter,2, movie.o_title)
        tmp_model.set_value(tmp_iter,3, movie.title)
        tmp_model.set_value(tmp_iter,4, movie.director)
        tmp_model.set_value(tmp_iter,5, movie.genre)
        tmp_model.set_value(tmp_iter,6, movie.seen)
        if movie.year is None:
            tmp_model.set_value(tmp_iter,7, '')
        else:
            tmp_model.set_value(tmp_iter,7, movie.year)
        if movie.runtime is None:
            tmp_model.set_value(tmp_iter,8, '')
        else:
            tmp_model.set_value(tmp_iter,8, '%003d' % int(movie.runtime) + _(' min'))
        if movie.rating is None:
            tmp_model.set_value(tmp_iter,9, '')
        else:
            tmp_model.set_value(tmp_iter,9, movie.rating)
        # close add window
        self.widgets['add']['window'].hide()
        # refresh
        self.treeview_clicked()
        self.update_statusbar(_('Movie information has been updated'))


def change_rating_from_slider(self):
    rating = int(self.widgets['add']['rating_slider'].get_value())
    self.widgets['add']['image_rating'].show()
    try:
        rimage = int(str(self.config.get('rating_image')))
    except:
        rimage = 0
    if rimage:
        prefix = ''
    else:
        prefix = "meter"
    rating_file = "%s/%s0%d.png" % (self.locations['images'], prefix, rating)
    handler = self.widgets['add']['image_rating'].set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(rating_file))


def populate_with_results(self):
    w = self.widgets['add']
    m_id = None
    if self.founded_results_id:
        log.info("self.founded:results_id: %s", self.founded_results_id)
        m_id = self.founded_results_id
    else:
        self.founded_results_id = 0
        treeselection = self.widgets['results']['treeview'].get_selection()
        (tmp_model, tmp_iter) = treeselection.get_selected()
        if tmp_iter is None:
            return False
        m_id = tmp_model.get_value(tmp_iter, 0)
    
    self.treemodel_results.clear()
    self.widgets['results']['window'].hide()

    plugin_name = 'PluginMovie' + self.active_plugin
    plugin = __import__(plugin_name)
    self.movie = plugin.Plugin(m_id)
    self.movie.locations = self.locations
    self.movie.config = self.config
    
    fields_to_fetch = ['o_title', 'title', 'director', 'plot', 'cast', 'country', 'genre',
                'classification', 'studio', 'o_site', 'site', 'trailer', 'year',
                'notes', 'runtime', 'image', 'rating', 'screenplay', 'cameraman',
                'resolution', 'barcode']
    # remove fields that user doesn't want to fetch: (see preferences window)
    fields_to_fetch = [ i for i in fields_to_fetch if self.config.get("s_%s" % i, True, section='add') ]

    if w['cb_only_empty'].get_active(): # only empty fields
        details = get_details(self)
        fields_to_fetch = [ i for i in fields_to_fetch if details[i] is None ]
    self.movie.fields_to_fetch = fields_to_fetch
    
    if not self.movie.get_movie(w['window']):
        return None
    self.movie.parse_movie()

    if 'year' in fields_to_fetch:
        w['year'].set_value(int(self.movie.year))
        fields_to_fetch.pop(fields_to_fetch.index('year'))
    if 'runtime' in fields_to_fetch:
        w['runtime'].set_value(int(self.movie.runtime))
        fields_to_fetch.pop(fields_to_fetch.index('runtime'))
    if 'cast' in fields_to_fetch:
        cast_buffer = w['cast'].get_buffer()
        cast_buffer.set_text(gutils.convert_entities(self.movie.cast))
        fields_to_fetch.pop(fields_to_fetch.index('cast'))
    if 'plot' in fields_to_fetch:
        plot_buffer = w['plot'].get_buffer()
        plot_buffer.set_text(gutils.convert_entities(self.movie.plot))
        fields_to_fetch.pop(fields_to_fetch.index('plot'))
    if 'notes' in fields_to_fetch:
        notes_buffer = w['notes'].get_buffer()
        notes_buffer.set_text(gutils.convert_entities(self.movie.notes))
        fields_to_fetch.pop(fields_to_fetch.index('notes'))
    if 'rating' in fields_to_fetch:
        if self.movie.rating:
            w['rating_slider'].set_value(float(self.movie.rating))
        fields_to_fetch.pop(fields_to_fetch.index('rating'))
    # poster
    if 'image' in fields_to_fetch:
        if self.movie.image:
            image = os.path.join(self.locations['temp'], "poster_%s.jpg" % self.movie.image)
            try:
                handler = self.Image.set_from_file(image)
                pixbuf = self.Image.get_pixbuf()
                w['picture'].set_from_pixbuf(pixbuf.scale_simple(100, 140, 3))
                w['image'].set_text(self.movie.image)
            except:
                image = gutils.get_defaultimage_fname(self)
                handler = self.Image.set_from_file(image)
                w['picture'].set_from_pixbuf(self.Image.get_pixbuf())
        else:
            image = gutils.get_defaultimage_fname(self)
            handler = self.Image.set_from_file(image)
            Pixbuf = self.Image.get_pixbuf()
            w['picture'].set_from_pixbuf(Pixbuf)
        fields_to_fetch.pop(fields_to_fetch.index('image'))
    # other fields
    for i in fields_to_fetch:
        w[i].set_text(gutils.convert_entities(self.movie[i]))


def show_websearch_results(self):
    total = self.founded_results_id = 0
    for g in self.search_movie.ids:
        if ( str(g) != '' ):
            total += 1
    if total > 1:
        self.widgets['results']['window'].show()
        self.widgets['results']['window'].set_keep_above(True)
        row = None    
        key = 0
        self.treemodel_results.clear()
        for row in self.search_movie.ids:
            if (str(row)!=''):
                if isinstance(self.search_movie.titles[key], unicode):
                    title = self.search_movie.titles[key]
                else:
                    title = str(self.search_movie.titles[key]).decode(self.search_movie.encode)
                myiter = self.treemodel_results.insert_before(None, None)
                self.treemodel_results.set_value(myiter, 0, str(row))
                self.treemodel_results.set_value(myiter, 1, title)
            key +=1
        self.widgets['results']['treeview'].show()
    elif total==1:
        self.widgets['results']['treeview'].set_cursor(total-1)
        for row in self.search_movie.ids:
            if ( str(row) != '' ):
                self.founded_results_id = str(row)
                populate_with_results(self)
    else:
        gutils.error(self.widgets['results']['window'], _("No results"), self.widgets['add']['window'])


def get_from_web(self):
    """search the movie in web using the active plugin"""
    title = self.widgets['add']['title'].get_text()
    o_title = self.widgets['add']['o_title'].get_text()

    if o_title or title:
        option = gutils.on_combo_box_entry_changed_name(self.widgets['add']['source'])
        self.active_plugin = option
        plugin_name = 'PluginMovie%s' % option
        plugin = __import__(plugin_name)
        if self.debug_mode:
            log.debug('reloading %s', plugin_name)
            import sys
            reload(sys.modules[plugin_name])
        self.search_movie = plugin.SearchPlugin()
        self.search_movie.config = self.config
        if o_title:
            self.search_movie.url = self.search_movie.original_url_search
            if self.search_movie.remove_accents:
                self.search_movie.title = gutils.remove_accents(o_title, 'utf-8')
            else:
                self.search_movie.title = unicode(o_title, 'utf-8')
        elif title:
            self.search_movie.url = self.search_movie.translated_url_search
            if self.search_movie.remove_accents:
                self.search_movie.title = gutils.remove_accents(title, 'utf-8')
            else:
                self.search_movie.title = unicode(title, 'utf-8')
        if self.search_movie.search_movies(self.widgets['add']['window']):
            self.search_movie.get_searches()
        if len(self.search_movie.ids) == 1 and o_title and title:
            self.search_movie.url = self.search_movie.translated_url_search
            if self.search_movie.remove_accents:
                self.search_movie.title = gutils.remove_accents(title, 'utf-8')
            else:
                self.search_movie.title = unicode(title, 'utf-8')
            if self.search_movie.search_movies(self.widgets['add']['window']):
                self.search_movie.get_searches()
        self.show_search_results(self.search_movie)
    else:
        gutils.error(self.widgets['results']['window'], \
            _("You should fill the original title\nor the movie title."))


def source_changed(self):
    option = gutils.on_combo_box_entry_changed_name(self.widgets['add']['source'])
    self.active_plugin = option
    plugin_name = 'PluginMovie' + option
    plugin = __import__(plugin_name)
    self.widgets['add']['plugin_desc'].set_text(plugin.plugin_name+"\n" \
        +plugin.plugin_description+"\n"+_("Url: ") \
        +plugin.plugin_url+"\n"+_("Language: ")+plugin.plugin_language)
    image = os.path.join(self.locations['images'], plugin_name + ".png")
    # if movie plugin logo exists lets use it
    if os.path.exists(image):
        handler = self.widgets['add']['plugin_image'].set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(image))


def get_details(self): #{{{
    w = self.widgets['add']
    
    cast_buffer  = w['cast'].get_buffer()
    notes_buffer = w['notes'].get_buffer()
    plot_buffer  = w['plot'].get_buffer()
    
    t_movies = {
        'cameraman'      : w['cameraman'].get_text().decode('utf-8'),
        'classification' : w['classification'].get_text().decode('utf-8'),
        'barcode'        : unicode(gutils.digits_only(w['barcode'].get_text().decode('utf-8'))),
        'color'          : w['color'].get_active(),
        'cond'           : w['condition'].get_active(),
        'country'        : w['country'].get_text().decode('utf-8'),
        'director'       : w['director'].get_text().decode('utf-8'),
        'genre'          : w['genre'].get_text().decode('utf-8'),
        'image'          : w['image'].get_text().decode('utf-8'),
        'layers'         : w['layers'].get_active(),
        'media_num'      : w['discs'].get_value(),
        'number'         : w['number'].get_value(),
        'o_site'         : w['o_site'].get_text().decode('utf-8'),
        'o_title'        : w['o_title'].get_text().decode('utf-8'),
        'rating'         : w['rating_slider'].get_value(),
        'region'         : w['region'].get_active(),
        'resolution'     : w['resolution'].get_text().strip().decode('utf-8'),
        'runtime'        : w['runtime'].get_text().decode('utf-8'),
        'screenplay'     : w['screenplay'].get_text().decode('utf-8'),
        'site'           : w['site'].get_text().decode('utf-8'),
        'studio'         : w['studio'].get_text().decode('utf-8'),
        'title'          : w['title'].get_text().decode('utf-8'),
        'trailer'        : w['trailer'].get_text().decode('utf-8'),
        'year'           : w['year'].get_value(),
        'collection_id'  : w['collection'].get_active(),
        'medium_id'      : w['media'].get_active(),
        'volume_id'      : w['volume'].get_active(),
        'vcodec_id'      : w['vcodec'].get_active(),
        'cast'           : cast_buffer.get_text(cast_buffer.get_start_iter(),cast_buffer.get_end_iter()).decode('utf-8'),
        'notes'          : notes_buffer.get_text(notes_buffer.get_start_iter(),notes_buffer.get_end_iter()).decode('utf-8'),
        'plot'           : plot_buffer.get_text(plot_buffer.get_start_iter(),plot_buffer.get_end_iter()).decode('utf-8'),
    }
    if self._am_movie_id is not None:
        t_movies['movie_id'] = self._am_movie_id

    if t_movies['collection_id'] > 0:
        t_movies['collection_id'] = self.collection_combo_ids[t_movies['collection_id']]
    else:
        t_movies['collection_id'] = None
    if t_movies['volume_id'] > 0:
        t_movies['volume_id'] = self.volume_combo_ids[t_movies['volume_id']]
    else:
        t_movies['volume_id'] = None
    if t_movies['medium_id'] > 0:
        t_movies['medium_id'] = self.media_ids[t_movies['medium_id']]
    else:
        t_movies['medium_id'] = None
    if t_movies['vcodec_id'] > 0:
        t_movies['vcodec_id'] = self.vcodecs_ids[t_movies['vcodec_id']]
    else:
        t_movies['vcodec_id'] = None
    if t_movies['barcode'] == '0':
        t_movies['barcode'] = None
    
    if w['seen'].get_active():
        t_movies['seen'] = True
    else:
        t_movies['seen'] = False
    if t_movies['year'] < 1900:
        t_movies['year'] = None

    def get_id(model, text):
        for i in model:
            if i[1] == text:
                return i[0]
        return None
    # languages
    t_movies['languages'] = set()
    for row in self.lang['model']:
        lang_id   = get_id(self.lang['lang'], row[0])
        lang_type = get_id(self.lang['type'], row[1])
        acodec    = get_id(self.lang['acodec'], row[2])
        achannel  = get_id(self.lang['achannel'], row[3])
        subformat = get_id(self.lang['subformat'], row[4])
        t_movies['languages'].add((lang_id, lang_type, acodec, achannel, subformat))

    # tags
    t_movies['tags'] = {}
    for i in self.tags_ids:
        if self.am_tags[i].get_active() == True:
            t_movies['tags'][self.tags_ids[i]] = 1
    
    validate_details(t_movies)

    return t_movies    #}}}


def set_details(self, item=None):#{{{
    if item is None:
        item = {}
    if 'movie_id' in item and item['movie_id']:
        self._am_movie_id = item['movie_id']
    else:
        self._am_movie_id = None
    w = self.widgets['add']

    cast_buffer  = w['cast'].get_buffer()
    notes_buffer = w['notes'].get_buffer()
    plot_buffer  = w['plot'].get_buffer()

    if 'o_title' in item and item['o_title']:
        w['o_title'].set_text(item['o_title'])
    else:
        w['o_title'].set_text('')
    if 'title' in item and item['title']:
        w['title'].set_text(item['title'])
    else:
        w['title'].set_text('')
    if 'number' in item and item['number']:
        w['number'].set_value(int(item['number']))
    else:
        w['number'].set_value(int(gutils.find_next_available(self.db)))
    if 'title' in item and item['title']:
        w['title'].set_text(item['title'])
    if 'year' in item and item['year']:
        w['year'].set_value( gutils.digits_only(item['year'], 2100))
    else:
        w['year'].set_value(0)
    if 'resolution' in item and item['resolution']:
        if self.config.get('use_resolution_alias', True):
            w['resolution'].set_text(item['resolution'])
        elif 'height' in item and item['height'] and 'width' in item and item['width']:
            w['resolution'].set_text("%dx%d" % (item['width'], item['height']))
        else: # failback to 'resolution'
            w['resolution'].set_text(item['resolution'])
    else:
        w['resolution'].set_text('')
    if 'runtime' in item and item['runtime']:
        w['runtime'].set_value( gutils.digits_only(item['runtime']))
    else:
        w['runtime'].set_value(0)
    if 'barcode' in item and item['barcode']:
        w['barcode'].set_text(item['barcode'])
    else:
        w['barcode'].set_text('')
    if 'cameraman' in item and item['cameraman']:
        w['cameraman'].set_text(item['cameraman'])
    else:
        w['cameraman'].set_text('')
    if 'screenplay' in item and item['screenplay']:
        w['screenplay'].set_text(item['screenplay'])
    else:
        w['screenplay'].set_text('')
    if 'country' in item and item['country']:
        w['country'].set_text(item['country'])
    else:
        w['country'].set_text('')
    if 'classification' in item and item['classification']:
        w['classification'].set_text(item['classification'])
    else:
        w['classification'].set_text('')
    if 'studio' in item and item['studio']:
        w['studio'].set_text(item['studio'])
    else:
        w['studio'].set_text('')
    if 'o_site' in item and item['o_site']:
        w['o_site'].set_text(item['o_site'])
    else:
        w['o_site'].set_text('')
    if 'director' in item and item['director']:
        w['director'].set_text(item['director'])
    else:
        w['director'].set_text('')
    if 'site' in item and item['site']:
        w['site'].set_text(item['site'])
    else:
        w['site'].set_text('')
    if 'trailer' in item and item['trailer']:
        w['trailer'].set_text(item['trailer'])
    else:
        w['trailer'].set_text('')
    if 'genre' in item and item['genre']:
        w['genre'].set_text(item['genre'])
    else:
        w['genre'].set_text('')
    if 'color' in item and item['color']:
        w['color'].set_active( gutils.digits_only(item['color'], 3))
    else:
        w['color'].set_active( gutils.digits_only(self.config.get('color', 0, section='defaults'), 3))
    if 'layers' in item and item['layers']:
        w['layers'].set_active( gutils.digits_only(item['layers'], 4))
    else:
        w['layers'].set_active( gutils.digits_only(self.config.get('layers', 0, section='defaults'), 4))
    if 'region' in item and item['region']>=0:
            w['region'].set_active( gutils.digits_only(item['region'], 8))
    else:
        w['region'].set_active( gutils.digits_only(self.config.get('region', 0, section='defaults'), 8))
    if 'cond' in item and item['cond']>=0:
        w['condition'].set_active( gutils.digits_only( item['cond'], 5) )
    else:
        w['condition'].set_active( gutils.digits_only( self.config.get('condition', 0, section='defaults'), 5))
    if 'media_num' in item and item['media_num']:
        w['discs'].set_value( gutils.digits_only(item['media_num']))
    else:
        w['discs'].set_value(1)
    if 'rating' in item and item['rating']:
        w['rating_slider'].set_value( gutils.digits_only(item['rating'], 10) )
    else:
        w['rating_slider'].set_value(0)
    if 'seen' in item and item['seen'] is True:
        w['seen'].set_active(True)
    else:
        w['seen'].set_active(False)
    if 'cast' in item and item['cast']:
        cast_buffer.set_text(item['cast'])
    else:
        cast_buffer.set_text('')
    if 'notes' in item and item['notes']:
        notes_buffer.set_text(item['notes'])
    else:
        notes_buffer.set_text('')
    if 'plot' in item and item['plot']:
        plot_buffer.set_text(item['plot'])
    else:
        plot_buffer.set_text('')
    pos = 0
    if 'medium_id' in item and item['medium_id']:
        pos = gutils.findKey(item['medium_id'], self.media_ids)
    else:
        pos = gutils.findKey(int(self.config.get('media', 0, section='defaults')), self.media_ids)
    if pos is not None:
        w['media'].set_active(int(pos))
    else:
        w['media'].set_active(0)
    pos = 0
    if 'vcodec_id' in item and item['vcodec_id']:
        pos = gutils.findKey(item['vcodec_id'], self.vcodecs_ids)
    else:
        pos = gutils.findKey(int(self.config.get('vcodec', 0, section='defaults')), self.vcodecs_ids)
    if pos is not None:
        w['vcodec'].set_active(int(pos))
    else:
        w['vcodec'].set_active(0)
    pos = 0
    if 'volume_id' in item and item['volume_id']:
        pos = gutils.findKey(item['volume_id'], self.volume_combo_ids)
    if pos is not None:
        w['volume'].set_active(int(pos))
    else:
        w['volume'].set_active(0)
    pos = 0
    if 'collection_id' in item and item['collection_id']:
        pos = gutils.findKey(item['collection_id'], self.collection_combo_ids)
    if pos is not None:
        w['collection'].set_active(int(pos))
    else:
        w['volume'].set_active(0)
    # tags
    for tag in self.am_tags:
        self.am_tags[tag].set_active(False)
    if 'tags' in item:
        for tag in item['tags']:
            i = gutils.findKey(tag.tag_id, self.tags_ids)
            self.am_tags[i].set_active(True)
    # languages
    w['lang_treeview'].get_model().clear()
    if 'languages' in item and len(item['languages'])>0:
        for i in item['languages']:
            self.create_language_row(i)
    # poster
    if 'poster_md5' in item and item['poster_md5']:
        image_path = gutils.get_image_fname(item["poster_md5"], self.db, 'm')
        if not image_path: image_path = '' # isfile doesn't like bool
        w['image'].set_text(item['poster_md5'])
    elif 'image' in item and item['image']:
        if len(item["image"])==32: # md5
            image_path = gutils.get_image_fname(item["image"], self.db, 'm')
            if not image_path: image_path = '' # isfile doesn't like bool
            else: w['image'].set_text(item['image'])
        else:
            image_path = os.path.join(self.locations['posters'], "m_%s.jpg" % item['image'])
            log.warn("TODO: image=%s", item['image'])
    else:
        w['image'].set_text('')
        image_path = gutils.get_defaultimage_fname(self)
    if not os.path.isfile(image_path):
        image_path = gutils.get_defaultimage_fname(self)
    w['picture'].set_from_file(image_path)
    
    w['notebook'].set_current_page(0)
    w['o_title'].grab_focus()
    #}}}


def validate_details(t_movies, allow_only=None):
    for i in t_movies.keys():
        if t_movies[i] == '':
            t_movies[i] = None
    for i in ('color', 'cond', 'layers', 'media', 'vcodec'):
        if t_movies.has_key(i) and t_movies[i] < 1:
            t_movies[i] = None
    for i in ('volume_id','collection_id', 'runtime'):
        if t_movies.has_key(i) and (t_movies[i] is None or int(t_movies[i]) == 0):
            t_movies[i] = None
    if allow_only is not None:
        # iterate over a copy of keys of the dict because removing elements of a dict
        # within a for enumeration of the same dict instance isn't supported
        for i in t_movies.keys():
            if not i in allow_only:
                t_movies.pop(i)


### database part #############################################


def add_movie_db(self, close):
    session = self.db.Session()

    details = get_details(self)
    if not details['o_title'] and not details['title']:
        gutils.error(self.widgets['results']['window'],
            _("You should fill the original title\nor the movie title."),
            parent=self.widgets['add']['window'])
        return False

    if details['o_title']:
        if session.query(db.Movie).filter_by(o_title=details['o_title']).count() > 0:
            if not gutils.question(_('Movie with that title already exists, are you sure you want to add?'), self.widgets['add']['window']):
                return False
    if details['title']:
        if session.query(db.Movie).filter_by(title=details['title']).count() > 0:
            if not gutils.question(_('Movie with that title already exists, are you sure you want to add?'), self.widgets['add']['window']):
                return False
    
    if details['image']:
        tmp_image_path = os.path.join(self.locations['temp'], "poster_%s.jpg" % details['image'])
        if os.path.isfile(tmp_image_path):
            new_poster_md5 = gutils.md5sum(file(tmp_image_path, 'rb'))

            if session.query(db.Poster).filter_by(md5sum=new_poster_md5).count() == 0:
                try:
                    data = file(tmp_image_path, 'rb').read()
                except Exception, e:
                    log.warning("cannot read poster data")
                else:
                    poster = db.Poster(md5sum=new_poster_md5, data=data)
                    del details["image"]
                    details["poster_md5"] = new_poster_md5
                    session.add(poster)
            try:
                os.remove(tmp_image_path)
            except Exception, e:
                log.warn("cannot remove temporary file %s", tmp_image_path)
        else:
            log.warn("cannot read temporary file: %s", tmp_image_path)


    movie = update_movie_instance(None, details, session)
    session.add(movie)
    if not commit(session):
        return False

    rows = len(self.treemodel)
    if rows > 0:
        insert_after = self.treemodel.get_iter(rows-1)    # last
    else:
        insert_after = None
    myiter = self.treemodel.insert_after(None, insert_after)

    image_path = ''
    if movie.poster_md5:
        image_path = gutils.get_image_fname(movie.poster_md5, self.db, 's')
    if not image_path or not os.path.isfile(image_path):
        image_path = gutils.get_defaultthumbnail_fname(self)
    handler = self.Image.set_from_file(image_path)
    pixbuf = self.Image.get_pixbuf()
    self.treemodel.set_value(myiter, 0, '%004d' % details['number'])
    self.treemodel.set_value(myiter, 1, pixbuf)
    self.treemodel.set_value(myiter, 2, details['o_title'])
    self.treemodel.set_value(myiter, 3, details['title'])
    self.treemodel.set_value(myiter, 4, details['director'])
    self.treemodel.set_value(myiter, 5, details['genre'])
    self.treemodel.set_value(myiter, 6, details['seen'])
    if details['year'] is None:
        self.treemodel.set_value(myiter, 7, '')
    else:
        self.treemodel.set_value(myiter, 7, int(details['year']))
    if details['runtime'] is None:
        self.treemodel.set_value(myiter, 8, '')
    else:
        self.treemodel.set_value(myiter, 8, '%003d' % int(details['runtime']) + _(' min'))
    if details['rating'] is None:
        self.treemodel.set_value(myiter, 9, '')
    else:
        self.treemodel.set_value(myiter, 9, int(details['rating']))
    #update statusbar
    self.total += 1
    self.count_statusbar()
    #select new entry from main treelist
    self.widgets['treeview'].get_selection().select_iter(myiter)
    self.treeview_clicked()
    clear(self)

    if close:
        self.hide_add_window()


def clone_movie(self):
    session = self.db.Session()

    treeselection = self.widgets['treeview'].get_selection()
    (tmp_model, tmp_iter) = treeselection.get_selected()
    if tmp_iter is None:
        log.warn("cannot clone movie: no item selected")
        return False
    number = tmp_model.get_value(tmp_iter, 0)
    movie = session.query(db.Movie).filter_by(number=number).first()

    if movie is None:
        log.warn("cannot clone movie: Movie(%s) not found", number)
        return False

    next_number = gutils.find_next_available(self.db)
    
    # integer problem workaround
    if int(movie.seen)==1:
        seen = True
    else:
        seen = False
    new_movie = db.Movie()
    
    # TODO: WARNING: loan problems (don't copy volume/collection data until resolved)
    new_movie.cast           = movie.cast
    new_movie.classification = movie.classification
    new_movie.vcodec_id      = movie.vcodec_id
    new_movie.barcode        = movie.barcode
    new_movie.cameraman      = movie.cameraman
    new_movie.collection_id  = movie.collection_id
    new_movie.volume_id      = movie.volume_id
    new_movie.color          = movie.color
    new_movie.cond           = movie.cond
    new_movie.country        = movie.country
    new_movie.director       = movie.director
    new_movie.genre          = movie.genre
    new_movie.site           = movie.site
    new_movie.loaned         = movie.loaned
    new_movie.layers         = movie.layers
    new_movie.medium_id      = movie.medium_id
    new_movie.number         = next_number
    new_movie.media_num      = movie.media_num
    new_movie.notes          = movie.notes
    new_movie.o_title        = movie.o_title
    new_movie.plot           = movie.plot
    new_movie.poster_md5     = movie.poster_md5
    new_movie.ratio_id       = movie.ratio_id
    new_movie.rating         = movie.rating
    new_movie.region         = movie.region
    new_movie.runtime        = movie.runtime
    new_movie.resolution     = movie.resolution
    new_movie.screenplay     = movie.screenplay
    new_movie.seen           = seen
    new_movie.o_site         = movie.o_site
    new_movie.studio         = movie.studio
    new_movie.title          = movie.title
    new_movie.trailer        = movie.trailer
    new_movie.year           = movie.year
    
    new_movie.tags           = movie.tags
    new_movie.languages      = movie.languages
    new_movie.loans          = movie.loans
    
    # save
    session.add(new_movie)
    if not commit(session):
        return False

    if movie.poster_md5:
        image_path = gutils.get_image_fname(movie.poster_md5, self.db)
        if not image_path or not os.path.isfile(image_path):
            image_path = gutils.get_defaultimage_fname(self)
        handler = self.Image.set_from_file(image_path)

    # change_filter calls populate_treeview which updates the status bar
    quick_filter.change_filter(self)


def update_movie_instance(movie, details, session):
    if not movie:
        movie = db.Movie()
    if details is not None:
        t_tags = t_languages = None
        if 'tags' in details:
            t_tags = details.pop('tags')
        if 'languages' in details:
            t_languages = details.pop('languages')
        #for i in db.tables.movies.columns.keys():
        for i in details:
            if hasattr(movie, i):
                setattr(movie, i, details[i])

        # clear previous data (in case of updates)
        if movie.languages:
            movie.languages = []
        if movie.tags:
            movie.tags = []
        # languages
        if t_languages is not None:
            for lang in t_languages:
                if lang[0] > 0:
                    ml = db.MovieLang(lang_id=lang[0], type=lang[1],
                        acodec_id=lang[2], achannel_id=lang[3], subformat_id=lang[4])
                    movie.languages.append(ml)
        # tags
        if t_tags is not None:
            for tag in t_tags.keys():
                dbTag = session.query(db.Tag).filter_by(tag_id=tag).one()
                #movie.tags.append(db.MovieTag(tag_id=tag))
                movie.tags.append(dbTag)
        if hasattr(movie, 'image') and movie.image: # TODO: remove it once image will be removed from movies_table
            movie.image = None # remove MD5 or link
    return movie


def commit(session):
    try:
        session.commit()
    except IntegrityError, e:
        session.rollback()
        log.warn("Cannot commit movie: %s", e.message)
        gutils.warning(unicode(e.orig))
        return False
    except Exception, e:
        log.error("Unexpected problem: %s", e)
        return False
    return True
