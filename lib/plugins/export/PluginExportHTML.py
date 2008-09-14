# -*- coding: UTF-8 -*-
# vim: fdm=marker

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Piotr Ożarowski
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
import sys
import gtk, gtk.glade
import gutils
import glob, shutil
import version
import math
from xml.dom import minidom
import gettext
gettext.install('griffith', unicode=1)
import logging
log = logging.getLogger("Griffith")
import db

plugin_name         = 'HTML'
plugin_description  = _('Plugin exports data using templates')
plugin_author       = 'Piotr Ożarowski'
plugin_author_email = 'ozarow+griffith@gmail.com'
plugin_version      = '3.8'

class ExportPlugin(gtk.Window):
    #==[ configuration - default values ]==========={{{
    config = {
        'sorting'           : 'movies_title',
        'sorting2'          : 'ASC',
        'exported_dir'      : 'griffith_movies',
        'template'          : 0,
        'title'             : _("Griffith's movies list"),
        'style'             : 0,
        'custom_style'      : False,
        'custom_style_file' : None,
        'split_num'         : 50,        # split into x files/pages
        'split_by'          : 1,        # 0==files, 1==movies
        'seen_only'         : 0,        # 0==all movies; 1==seen only;   2==unseen only
        'loaned_only'       : 0,        # 0==all movies; 1==loaned only; 2==not loaned only
        'poster_convert'    : False,        # dont convert
        'poster_height'     : 200,
        'poster_width'      : 150,
        'poster_mode'       : 'RGB',        # RGB == color, L == black and white
        'poster_format'     : 'jpg'
    }
    fields = {
        'movies_cast'           : False,
        'movies_classification' : False,
        'movies_country'        : True,
        'movies_genre'          : True,
        'movies_director'       : True,
        'movies_image'          : True,
        'movies_o_site'         : True,
        'movies_site'           : True,
        'movies_trailer'        : True,
        'movies_loaned'         : False,
        'movies_media_num'      : True,
        'movies_number'         : True,
        'movies_o_title'        : True,
        'movies_plot'           : False,
        'movies_rating'         : True,
        'movies_runtime'        : True,
        'movies_studio'         : False,
        'movies_seen'           : True,
        'movies_title'          : True,
        'movies_year'           : True,
        'movies_notes'          : False,
#        'movies_region'         : False,
#        'movies_layers'         : False,
#        'movies_condition'      : False,
#        'movies_color'          : False,
#        'movies_volume_id'      : False,
#        'movies_collection_id'  : False,
        'media_name'            : True,
        'collections_name'      : True,
        'volumes_name'          : True,
#        'acodecs_name'          : True,
        'vcodecs_name'          : True,
    }
    
    fields_as_columns = {
        'movies_cast'           : 'cast',
        'movies_classification' : 'classification',
        'movies_country'        : 'country',
        'movies_genre'          : 'genre',
        'movies_director'       : 'director',
        'movies_image'          : 'image',
        'movies_o_site'         : 'o_site',
        'movies_site'           : 'site',
        'movies_trailer'        : 'trailer',
        'movies_loaned'         : 'loaned',
        'movies_media_num'      : 'media_num',
        'movies_number'         : 'number',
        'movies_o_title'        : 'o_title',
        'movies_plot'           : 'plot',
        'movies_rating'         : 'rating',
        'movies_runtime'        : 'runtime',
        'movies_studio'         : 'studio',
        'movies_seen'           : 'seen',
        'movies_title'          : 'title',
        'movies_year'           : 'year',
        'movies_notes'          : 'notes',
#        'movies_region'         : 'region',
#        'movies_layers'         : 'layers',
#        'movies_condition'      : 'condition',
#        'movies_color'          : 'color',
#        'movies_volume_id'      : 'volume_id',
#        'movies_collection_id'  : 'collection_id',
        'media_name'            : 'name',
        'collections_name'      : 'name',
        'volumes_name'          : 'name',
#        'acodecs_name'          : 'name',
        'vcodecs_name'          : 'name',
    }
    
    names = {
        _('Cast')           : 'movies_cast',
        _('Classification') : 'movies_classification',
        _('Country')        : 'movies_country',
        _('Director')       : 'movies_director',
        _('Genre')          : 'movies_genre',
        _('Image')          : 'movies_image',
        _('Official site')  : 'movies_o_site',
        _('Site')           : 'movies_site',
        _('Trailer')        : 'movies_trailer',
        _('Loaned')         : 'movies_loaned',
        _('Discs')          : 'movies_media_num',
        _('Number')         : 'movies_number',
        _('Original Title') : 'movies_o_title',
        _('Plot')           : 'movies_plot',
        _('Rating')         : 'movies_rating',
        _('Runtime')        : 'movies_runtime',
        _('Studio')         : 'movies_studio',
        _('Seen it')        : 'movies_seen',
        _('Title')          : 'movies_title',
        _('Year')           : 'movies_year',
        _('Notes')          : 'movies_notes',
#        _('Region')         : 'movies_region',
#        _('Layers')         : 'movies_layers',
#        _('Condition')      : 'movies_condition',
#        _('Color')          : 'movies_color',
#        _('Volume')         : 'movies_volume_id',
#        _('Collection')     : 'movies_collection_id',
        _('Media')          : 'media_name',
        _('Collection')     : 'collections_name',
        _('Volume')         : 'volumes_name',
#        _('Audio codecs')   : 'acodecs_name',
        _('Video codec')    : 'vcodecs_name',
    }
    #}}}

    def __init__(self, database, locations, parent_window, **kwargs):#{{{
        self.db = database
        self.locations = locations
        if kwargs.has_key('config'):
            self.persistent_config = kwargs['config']
        else:
            self.persistent_config = None
        self.widgets = {}
        self.style_list = {}
        self.templates = self.make_template_list()
        # glade
        gf = os.path.join(locations['glade'], 'exporthtml.glade')
        self.define_widgets(gtk.glade.XML(gf))
        self.fill_widgets()
    #}}}

    def get_node_value_by_language(self, parent, name, language='en'):#{{{
        nodes = parent.getElementsByTagName(name)
        for node in nodes:
            if node.parentNode != parent:
                continue
            elif node.attributes.get('xml:lang') is not None:
                if node.attributes.get('xml:lang').value == language:
                    return node.firstChild.nodeValue
            else:    # set default value in case node has no xml:lang attribute
                value = node.firstChild.nodeValue
        return value
    #}}}        
        
    def make_template_list(self):#{{{
        language = 'en'
        if os.environ.has_key('LANG'):
            language = os.environ['LANG'][:2]
        templates = {}
        j=0 # number of templates
        dirName = os.path.join(self.locations['share'], 'export_templates')
        items = os.listdir(dirName)
        items.sort()
        for i in items:
            fileName = os.path.join(dirName, i)
            if not os.path.islink(fileName) and os.path.isdir(fileName):
                # clear previous data
                doc = None; styles = {};
                tpl_name=None; tpl_author=None; tpl_email=None; tpl_version=None; tpl_ext=None; tpl_desc=None
                try:
                    doc = minidom.parse(os.path.join(fileName, 'config.xml'))
                except:
                    log.info("Can't parse configuration file for template: %s"%fileName)
                    continue
                for template in doc.getElementsByTagName('template'):
                    tpl_name    = self.get_node_value_by_language(template, 'name', language)
                    tpl_author  = template.getElementsByTagName('author')[0].firstChild.nodeValue
                    tpl_email   = template.getElementsByTagName('email')[0].firstChild.nodeValue
                    tpl_version = template.getElementsByTagName('version')[0].firstChild.nodeValue
                    tpl_ext     = template.getElementsByTagName('extension')[0].firstChild.nodeValue
                    tpl_desc    = self.get_node_value_by_language(template, 'description', language)
                    k=0    # number of styles
                    try:
                        styles_list = template.getElementsByTagName('styles')[0].getElementsByTagName('style')
                        for style in styles_list:
                            tpl_style_name = self.get_node_value_by_language( style, 'name', language )
                            tpl_style_file = style.getElementsByTagName('file')[0].firstChild.nodeValue
                            # get preview if available
                            try:
                                tpl_style_preview = style.getElementsByTagName('preview')[0].firstChild.nodeValue
                            except:
                                tpl_style_preview = None
                            styles[k] = {
                                'name': tpl_style_name,
                                'file': tpl_style_file,
                                'preview': tpl_style_preview
                            }
                            k=k+1
                    except:
                        styles = None
                if tpl_name=='':
                    continue
                templates[j]= {
                    'dir'     : i,
                    'name'    : tpl_name,
                    'author'  : tpl_author,
                    'email'   : tpl_email,
                    'version' : tpl_version,
                    'ext'     : tpl_ext,
                    'desc'    : tpl_desc,
                    'styles'  : styles
                }
                j=j+1
        return templates
    #}}}

    #==[ widgets ]=================================={{{
    def define_widgets(self, glade_file):
        get = lambda x: glade_file.get_widget(x)
        self.widgets = {
            'window'                : get('w_eh'),
            'fcw'                   : get('fcw'),
            'box_include_1'         : get('box_include_1'),
            'box_include_2'         : get('box_include_2'),
            'box_include_3'         : get('box_include_3'),
            'sb_split_num'          : get('sb_split_num'),
            'rb_split_files'        : get('rb_split_files'),
            'rb_split_movies'       : get('rb_split_movies'),
            'rb_seen'               : get('rb_seen'),
            'rb_seen_only'          : get('rb_seen_only'),
            'rb_seen_only_n'        : get('rb_seen_only_n'),
            'rb_loaned'             : get('rb_loaned'),
            'rb_loaned_only'        : get('rb_loaned_only'),
            'rb_loaned_only_n'      : get('rb_loaned_only_n'),
            'entry_header'          : get('entry_header'),
            'cb_custom_style'       : get('cb_custom_style'),
            'cb_reverse'            : get('cb_reverse'),
            'combo_style'           : get('combo_style'),
            'combo_sortby'          : get('combo_sortby'),
            'combo_theme'           : get('combo_theme'),
            'fcb_custom_style_file' : get('fcb_custom_style_file'),
            'l_tpl_author'          : get('l_tpl_author'),
            'l_tpl_email'           : get('l_tpl_email'),
            'l_tpl_version'         : get('l_tpl_version'),
            'l_tpl_desc'            : get('l_tpl_desc'),
            'image_preview'         : get('image_preview'),
            'vb_posters'            : get('vb_posters'),
            'sb_height'             : get('sb_height'),
            'sb_width'              : get('sb_width'),
            'cb_black'              : get('cb_black'),
            'combo_format'          : get('combo_format'),
            'cb_convert'            : get('cb_convert'),
        }

        # define handlers for general events
        glade_file.signal_autoconnect({
            'on_export_button_clicked'           : self.export_data,
            'on_rb_split_files_toggled'          : self.on_rb_split_files_toggled,
            'on_rb_split_movies_toggled'         : self.on_rb_split_movies_toggled,
            'on_rb_seen_toggled'                 : self.on_rb_seen_toggled,
            'on_rb_seen_only_toggled'            : self.on_rb_seen_only_toggled,
            'on_rb_seen_only_n_toggled'          : self.on_rb_seen_only_n_toggled,
            'on_rb_loaned_toggled'               : self.on_rb_loaned_toggled,
            'on_rb_loaned_only_toggled'          : self.on_rb_loaned_only_toggled,
            'on_rb_loaned_only_n_toggled'        : self.on_rb_loaned_only_n_toggled,
            'on_cancel_button_clicked'           : self.on_quit,
            'on_cb_data_toggled'                 : self.on_cb_data_toggled,
            'on_cb_custom_style_toggled'         : self.on_cb_custom_style_toggled,
            'on_fcb_custom_style_file_activated' : self.on_fcb_custom_style_file_activated,
            'on_combo_style_changed'             : self.on_combo_style_changed,
            'on_combo_theme_changed'             : self.on_combo_theme_changed,
            'on_cb_convert_toggled'              : self.on_cb_convert_toggled,
        })

    def fill_widgets(self):
        # themes
        for i in self.templates:
            self.widgets['combo_theme'].insert_text(i, self.templates[i]['name'])

        # sortby combo
        keys = self.names.keys()
        keys.sort()
        j = 0
        pos_o_title = 0
        for i in keys:
            self.widgets['combo_sortby'].append_text(i)
            if i == _('Original Title'):
                pos_o_title = j
            j = j + 1
        self.widgets['combo_sortby'].set_wrap_width(3)

        # include data
        j = 0
        k = math.ceil( len(self.names) / float(3) )
        for i in keys:
            j = j + 1
            field = self.names[i]
            self.widgets['cb_'+field] = gtk.CheckButton(i)
            self.widgets['cb_'+field].set_name("cb_%s" % field)
            self.widgets['cb_'+field].connect('toggled', self.on_cb_data_toggled)
            self.widgets['cb_'+field].set_active(self.fields[field])
            if j <= k:
                self.widgets['box_include_1'].add(self.widgets["cb_%s" % field])
            elif j<= 2*k:
                self.widgets['box_include_2'].add(self.widgets["cb_%s" % field])
            else:
                self.widgets['box_include_3'].add(self.widgets["cb_%s" % field])
        self.widgets['box_include_1'].show_all()
        self.widgets['box_include_2'].show_all()
        self.widgets['box_include_3'].show_all()

        # set defaults --------------------------------
        self.widgets['entry_header'].set_text(self.config['title'])
        self.widgets['combo_theme'].set_active(2)    # html_tables
        self.widgets['combo_sortby'].set_active(pos_o_title)    # orginal title
        # spliting
        self.widgets['sb_split_num'].set_value(self.config['split_num'])
        if self.config['split_by'] == 0:
            self.widgets['rb_split_files'].set_active(True)
        else:
            self.widgets['rb_split_movies'].set_active(True)
        # limiting
        if self.config['seen_only'] == 2:
            self.widgets['rb_seen_only_n'].set_active(True)
        elif self.config['seen_only'] == 1:
            self.widgets['rb_seen_only'].set_active(True)
        else:
            self.widgets['rb_seen'].set_active(True)
        if self.config['loaned_only'] == 2:
            self.widgets['rb_loaned_only_n'].set_active(True)
        elif self.config['loaned_only'] == 1:
            self.widgets['rb_loaned_only'].set_active(True)
        else:
            self.widgets['rb_loaned'].set_active(True)
        # posters
        self.widgets['combo_format'].set_active(0)
        if self.config['poster_convert'] and self.config['poster_convert'] == True:
            self.widgets['cb_convert'].set_active(True)
            self.widgets['vb_posters'].set_sensitive(True)
        else:
            self.widgets['cb_convert'].set_active(False)
            self.widgets['vb_posters'].set_sensitive(False)
        # persistent config
        if not self.persistent_config is None:
            tmp = self.persistent_config.get('export_dir', None, section='export-html')
            if not tmp is None:
                self.widgets['fcw'].set_current_folder(tmp)
    #}}}

    #==[ callbacks ]================================{{{
    # buttons:
    def on_quit(self, widget=None):
        self.widgets['window'].destroy()

    # data tab -------------------------------------#{{{
    def on_rb_split_files_toggled(self, widget):
        self.config['split_by'] = 0    # files

    def on_rb_split_movies_toggled(self, widget):
        self.config['split_by'] = 1    # movies
    
    # export frame
    def on_cb_data_toggled(self, widget):
        self.fields[gutils.after(widget.get_name(), 'cb_')] = widget.get_active()

    # limit frame
    def on_rb_seen_toggled(self, widget):
        if widget.get_active():
            self.config['seen_only'] = 0    # export all movies

    def on_rb_seen_only_toggled(self, widget):
        if widget.get_active():
            self.config['seen_only'] = 1    # export only seen movies
    
    def on_rb_seen_only_n_toggled(self, widget):
        if widget.get_active():
            self.config['seen_only'] = 2    # export only unseen movies
    
    def on_rb_loaned_toggled(self, widget):
        if widget.get_active():
            self.config['loaned_only'] = 0  # export all movies

    def on_rb_loaned_only_toggled(self, widget):
        if widget.get_active():
            self.config['loaned_only'] = 1  # export only loaned movies
    
    def on_rb_loaned_only_n_toggled(self, widget):
        if widget.get_active():
            self.config['loaned_only'] = 2  # export only not loaned movies
    
    # posters frame
    def on_cb_convert_toggled(self, widget):
        active = widget.get_active()
        self.config['poster_convert'] = active
        if not active:
            self.widgets['vb_posters'].set_sensitive(False)
        else:
            self.widgets['vb_posters'].set_sensitive(True)
    #}}}

    # template tab ---------------------------------#{{{
    def on_combo_theme_changed(self, widget):
        old_id = self.config['template']
        tpl_id = widget.get_active()
        self.config['template'] = tpl_id
        # fill authors data
        self.widgets['l_tpl_author'].set_markup("<i>%s</i>" % self.templates[tpl_id]['author'])
        self.widgets['l_tpl_email'].set_markup("<i>%s</i>" % self.templates[tpl_id]['email'])
        self.widgets['l_tpl_email'].set_selectable(True)
        self.widgets['l_tpl_version'].set_markup("<i>%s</i>" % self.templates[tpl_id]['version'])
        self.widgets['l_tpl_desc'].set_markup("<i>%s</i>" % self.templates[tpl_id]['desc'])
        # remove old style list
        self.widgets['combo_style'].get_model().clear()
        # ... and add new
        if self.templates[tpl_id]['styles'] is not None:
            for i in self.templates[tpl_id]['styles']:
                self.widgets['combo_style'].insert_text(i, self.templates[tpl_id]['styles'][i]['name'])    # template name
            self.widgets['combo_style'].set_active(0)
        else:
            self.config['style'] = None
            self.widgets['image_preview'].set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_LARGE_TOOLBAR)

    def on_combo_style_changed(self, widget):
        self.config['style'] = widget.get_active()
        self.widgets['cb_custom_style'].set_active(False)

        tpl_id = self.config['template']
        template_dir = os.path.join(self.locations['share'], 'export_templates', self.templates[tpl_id]['dir'])
        preview_file = self.templates[self.config['template']]['styles'][self.config['style']]['preview']
        if preview_file is not None:
            preview_file = os.path.join(template_dir, preview_file)
        if preview_file is not None and not os.path.isfile(preview_file):
            preview_file = os.path.join(template_dir, 'preview.jpg')    # try default preview image
            if not os.path.isfile(preview_file):
                preview_file = None
        if preview_file is not None:
            self.widgets['image_preview'].set_from_file(preview_file)
        else:
            self.widgets['image_preview'].set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.widgets['image_preview'].show()

    def on_cb_custom_style_toggled(self, widget):
        if widget.get_active():
            self.config['custom_style'] = True
            self.widgets['image_preview'].hide()
        else:
            self.config['custom_style'] = False
            self.widgets['image_preview'].show()

    def on_fcb_custom_style_file_activated(self, widget):
        self.config['custom_style_file'] = widget.get_filename()
        self.widgets['cb_custom_style'].set_active(True)
    #}}} }}}

    def make_navigation(self, pages, current):#{{{
        if pages > 1:    # navigation needed
            tpl_id = self.config['template']
            t = '<div class="navi">\n\t<p id="prev">'
            if current > 1:
                t += '<a href="./page_%s.%s">%s</a>' % \
                    (str(current-1), self.templates[tpl_id]['ext'], _('previous'))
            else:    # first page
                t += _('previous')
            t += "</p>\n"
            for i in range(1, pages+1):
                if i == current:
                    t +='\t<p id="current">%s</p>\n' % str(i)
                else:
                    t +='\t<p><a href="./page_%s.%s">%s</a></p>\n' % \
                        (str(i), self.templates[tpl_id]['ext'], str(i))
            t += '\t<p id="next">'
            if pages > current:
                t +='<a href="./page_%s.%s">%s</a>' % \
                        (str(current+1), self.templates[tpl_id]['ext'], _('next'))
            else:    # last page
                t += _('next')
            t += "</p>\n</div>"
            return t
        else:
            return ''
    #}}}

    def fill_template(self, template, field, data='', title='', remove=False):    #{{{
        start = template.find('<@'+ field +'>')
        end = template.find('</@'+ field +'>', start+1)
        if start > -1 and end > -1:
            if remove == True:
                return template[:start] + template[end+4+len(field):]
            else:
                tmp = gutils.trim(template,'<@'+field+'>', '</@'+field+'>')
                tmp = tmp.replace("@DATA@", data)
                tmp = tmp.replace("@TITLE@", title)
                tmp = template[:start] + tmp + template[end+4+len(field):]
                if tmp.find('<@'+ field +'>') != -1:
                    tmp = self.fill_template(tmp, field, data, title, remove)
                return tmp
        else:
            return template
    #}}}

    def select(self):    #{{{
        from sqlalchemy import select, outerjoin
        config = self.config
        
        # columns to select
        columns = []
        for i in self.fields_as_columns:
            try:
                columns.append(db.movies_table.c[self.fields_as_columns[i]])
            except:
                pass
        # use outer join to media table to get the name of the media
        columns.append(db.media_table.c['name'])
        media_join = outerjoin(db.movies_table, db.media_table, \
                db.movies_table.c.medium_id==db.media_table.c.medium_id)
        # use outer join to collections table to get the name of the collection
        columns.append(db.collections_table.c['name'])
        collection_join = media_join.outerjoin(db.collections_table, \
            db.movies_table.c.collection_id==db.collections_table.c.collection_id)
        # use outer join to volumes table to get the name of the volume
        columns.append(db.volumes_table.c['name'])
        volume_join = collection_join.outerjoin(db.volumes_table, \
            db.movies_table.c.volume_id==db.volumes_table.c.volume_id)
        # use outer join to volumes table to get the name of the volume
        columns.append(db.vcodecs_table.c['name'])
        vcodec_join = volume_join.outerjoin(db.vcodecs_table, \
            db.movies_table.c.vcodec_id==db.vcodecs_table.c.vcodec_id)
        #
        # selecting the audio codec doesn't work with joins because if more than one codec per movie is
        # added it would duplicate the movie in the result set as many as audio codecs are added to the movie
        #
        # use outer join to language and acodec table to get the name of the audio codec
        #movie_lang_join = vcodec_join.outerjoin( \
        #    db.movie_lang_table, \
        #    db.movies_table.c.movie_id==db.movie_lang_table.c.movie_id)
        #columns.append(db.acodec_table.c['name'])
        #acodec_join = movie_lang_join.outerjoin( \
        #    db.acodec_table, \
        #    db.movie_lang_table.c.acodec_id==db.acodec_table.c.acodec_id)
        
        # sort order    TODO: more than one sort column
        sort_columns = []
        sorting_parts = config['sorting'].split('_')
        if config['sorting2'] == 'ASC':
            from sqlalchemy import asc
            sort_columns.append(asc(db.metadata.tables[sorting_parts[0]].c['_'.join(sorting_parts[1:])]))
        elif config['sorting2'] == 'DESC':
            from sqlalchemy import desc
            sort_columns.append(desc(db.metadata.tables[sorting_parts[0]].c['_'.join(sorting_parts[1:])]))

        statement = select(columns=columns, order_by=sort_columns, bind=self.db.session.bind,
                    from_obj=[media_join, collection_join, volume_join, vcodec_join], use_labels=True)

        # where clause
        if config['seen_only'] == 1:
            statement.append_whereclause(db.movies_table.c.seen==True)
        elif config['seen_only'] == 2:
            statement.append_whereclause(db.movies_table.c.seen!=True)
        if config['loaned_only'] == 1:
            statement.append_whereclause(db.movies_table.c.loaned==True)
        elif config['loaned_only'] == 2:
            statement.append_whereclause(db.movies_table.c.loaned!=True)
        
        return statement.execute()
    #}}}

    #==[ main function ]============================{{{
    def export_data(self, widget):
        """Main exporting function"""

        config = self.config
        fields = self.fields
        tid = config['template']
        
        # get data from widgets
        self.config['exported_dir'] = self.widgets['fcw'].get_filename()
        self.config['title']        = self.widgets['entry_header'].get_text()
        self.config['sorting']      = self.names[self.widgets['combo_sortby'].get_active_text().decode('utf-8')]
        if self.widgets['cb_reverse'].get_active():
            self.config['sorting2'] = 'DESC'
        else:
            self.config['sorting2'] = 'ASC'
        self.config['split_num']     = self.widgets['sb_split_num'].get_value_as_int()
        self.config['poster_height'] = self.widgets['sb_height'].get_value_as_int()
        self.config['poster_width']  = self.widgets['sb_width'].get_value_as_int()
        if self.widgets['cb_black'].get_active():
            self.config['poster_mode'] = 'L'
        else:
            self.config['poster_mode'] = 'RGB'
        self.config['poster_format'] = self.widgets['combo_format'].get_active_text()

        # create directories
        if not config['exported_dir']:
            log.info("Error: Folder name not set!")
            return 1
        
        if not os.path.isdir(config['exported_dir']):
            try:
                os.mkdir(config['exported_dir'])
            except:
                gutils.error(self,_("Can't create %s!") % config['exported_dir'])
                return 2
            
        data_path = os.path.join(self.locations['share'], 'export_templates', self.templates[tid]['dir'], 'data')
        if os.path.isdir(data_path):
            try:
                gutils.copytree(data_path, config['exported_dir'])
            except Exception, err:
                gutils.warning(self, str(err))
        
        # persist config
        if not self.persistent_config is None:
            self.persistent_config.set('export_dir', config['exported_dir'], section='export-html')
            self.persistent_config.save()

        if fields['movies_image']:
            # import modules needed later
            # modules are needed at least to convert griffith.png to nopic.(gif|jpeg|png)
            from PIL import Image
            # py2exe problem workaround:
            if os.name == 'nt' or os.name.startswith('win'): # win32, win64
                from PIL import PngImagePlugin
                from PIL import GifImagePlugin
                from PIL import JpegImagePlugin
                Image._initialized=2
            if not config['poster_convert']:
                config['poster_format'] = 'jpeg' # replace 'jpeg'
            
            posters_dir = os.path.join(config['exported_dir'], 'posters')
            if os.path.isdir(posters_dir):
                if gutils.question(_("Directory %s already exists.\nDo you want to overwrite it?") % posters_dir, True, self) == gtk.RESPONSE_YES:
                    try:
                        shutil.rmtree(posters_dir)
                    except:
                        gutils.error(self,_("Can't remove %s!") % config['exported_dir'])
                        return 3
                else:
                    return 4
            try:
                os.mkdir(posters_dir)
            except:
                gutils.error(self,_("Can't create %s!") % posters_dir)
                return 5

        if config['custom_style']:
            if config['custom_style_file'] is not None and os.path.isfile(config['custom_style_file']):
                try:
                    shutil.copy(config['custom_style_file'],config['exported_dir'])
                except:
                    gutils.warning(self,_("Can't copy %s!")%style_file)
                    config['custom_style'] = False
                style = os.path.split(self.config['custom_style_file'])[1]
            else:
                config['custom_style'] = False


        if config['style'] is not None and config['custom_style']==False:
            style = self.templates[tid]['styles'][config['style']]['file']
            style_path = os.path.join(self.locations['share'], 'export_templates', self.templates[tid]['dir'], style)
            try:
                shutil.copy(style_path,config['exported_dir'])
            except:
                gutils.warning(self,_("Can't copy %s!")%style_path)

        # select exported movies
        exported_movies = self.select().fetchall()
        number_of_exported_movies = len(exported_movies)

        if config['split_by'] == 1:    # split by number of movies per page
            self.entries_per_page = config['split_num']
        else:                # split by number of pagess
            if number_of_exported_movies < config['split_num']:
                self.entries_per_page = 1
            else:
                self.entries_per_page = int(number_of_exported_movies / config['split_num'])

        # calculate number of files to be created (pages)
        self.pages = int(math.ceil(float(number_of_exported_movies) / self.entries_per_page))

        template_dir = os.path.join(self.locations['share'], 'export_templates', self.templates[tid]['dir'])
        try:
            filename = 'page.tpl'
            tpl_header = file(os.path.join(template_dir,filename), "r").read()
        except:
            gutils.error(self,_("Can't open %s!")%filename)
            return False

        tpl_header = self.fill_template(tpl_header, 'header', config['title'])
        try:
            tpl_header = self.fill_template(tpl_header, 'style', style)
        except:
            pass
        tmp = _('Document generated by Griffith v') + version.pversion + \
                ' - Copyright (C) ' + version.pyear + ' ' + version.pauthor + ' - ' + \
                _('Released Under the GNU/GPL License')
        tmp = gutils.html_encode(tmp)
        tmp = tmp.replace('@', ' at ')    # prevent spam
        tpl_header = self.fill_template(tpl_header, 'copyright', tmp)
        tmp = None
        
        tpl_header = self.fill_template(tpl_header, 'pages', self.pages)
        
        # count exported fields
        rowspan = 0
        for i in fields:
            if fields[i] == True:
                rowspan = rowspan + 1
        rowspan = str(rowspan)
        tpl_header = self.fill_template(tpl_header, 'rowspan', rowspan)

        # split template
        tpl_tail = gutils.after(tpl_header, '<!-- /ITEMS -->')
        tpl_item = gutils.trim(tpl_header, '<!-- ITEMS -->','<!-- /ITEMS -->')
        tpl_header = gutils.before(tpl_header, '<!-- ITEMS -->')

        # fill header
        for j in self.names:
            if self.fields[self.names[j]] == True:
                tpl_header = self.fill_template(tpl_header, self.names[j], '', j)
            else:
                tpl_header = self.fill_template(tpl_header, self.names[j], remove=True)

        # check if line break needs conversion
        if tpl_header.upper().find('XHTML 1.0') > -1:
            linebreak_replacement = '<br />'
        else:
            linebreak_replacement = None

        item=1    # item's position on page (1 - first, ...)
        i = 1
        page=1    # page number
        for row in exported_movies:    # fill items {{{
            # check if new file has to be created
            if item==1:
                filename = os.path.join(config['exported_dir'],'page_%s.' % page + self.templates[tid]['ext'])
                try:
                    exported_file = file(filename, 'w')
                except:
                    gutils.error(self,_("Can't create %s!")%filename)
                    return False
                tmp2 = tpl_header + ''
                exported_file.write(self.fill_template(tmp2, 'page', str(page)))
                tmp2 = None

            # ---------------------------------------------
            tmp = tpl_item + '' # a copy (not a reference!)
            tmp = self.fill_template(tmp, 'id', str(item))
            tmp = self.fill_template(tmp, 'item', str(i))
            for j in self.names:
                if self.fields[self.names[j]] == True:
                    if self.names[j] == 'movies_image':
                        if row['movies_image']:
                            #image = row['movies_image'] + '.' + config['poster_format'].lower()
                            image = '%d' % row['movies_number'] + '.' + config['poster_format'].lower()
                            tmp = self.fill_template(tmp, self.names[j], image, j)
                        else:
                            tmp = self.fill_template(tmp, self.names[j], 'nopic.' + config['poster_format'].lower(), j)
                    elif row[self.names[j]] is None:
                        tmp = self.fill_template(tmp, self.names[j], '', j)
                    elif row[self.names[j]] is True:
                        tmp = self.fill_template(tmp, self.names[j], _('Yes'), j)
                    elif row[self.names[j]] is False:
                        tmp = self.fill_template(tmp, self.names[j], _('No'), j)
                    else:
                        try:
                            data = str(row[self.names[j]]).encode('utf-8')
                            if linebreak_replacement is not None:
                                data = data.replace('\r\n', linebreak_replacement)
                                data = data.replace('\n', linebreak_replacement)
                            tmp = self.fill_template(tmp, self.names[j], data, j)
                        except UnicodeDecodeError:
                            log.info("Unicode Decode Error occurred while decoding %s (movie number: %s)" % (self.names[j], row['movies_number']))
                            data = str(row[self.names[j]])
                            if linebreak_replacement is not None:
                                data = data.replace('\r\n', linebreak_replacement)
                                data = data.replace('\n', linebreak_replacement)
                            tmp = self.fill_template(tmp, self.names[j], data, j)
                        except Exception, ex:
                            log.info("Error occurred while decoding %s (movie number: %s)" % (self.names[j], row['movies_number']))
                else:
                    tmp = self.fill_template(tmp, self.names[j], remove=True)
                tmp = gutils.convert_entities(tmp)
            exported_file.write(tmp)
            tmp = None
            # ---------------------------------------------
            
            # copy poster
            if fields['movies_image']:
                if row['movies_image'] is not None:
                    image_file_src = os.path.join(self.locations['posters'], str(row['movies_image']) + '.jpg')
                    image_file_dst = os.path.join(posters_dir, '%d' % row['movies_number']) + '.' + config['poster_format'].lower()
                    if not config['poster_convert']:    # copy file
                        try:
                            shutil.copy(image_file_src,    image_file_dst)
                        except:
                            log.info("Can't copy %s" % image_file_src)
                    else:    # convert posters
                        try:
                            im = Image.open(image_file_src, 'r').convert(config['poster_mode'])
                            im.thumbnail((config['poster_width'], config['poster_height']), Image.ANTIALIAS)
                            im.save(image_file_dst, config['poster_format'])
                        except:
                            log.info("Can't convert %s" % image_file_src)

            # close file if last item
            if ((page-1)*self.entries_per_page)+item == number_of_exported_movies:
                tmp2 = tpl_tail + ''
                exported_file.write(self.fill_template(tmp2, 'navigation', self.make_navigation(self.pages, page)))
                exported_file.close()
                tmp2 = None
            
            # close file if last item in page
            elif item == self.entries_per_page:
                tmp2 = tpl_tail + ''
                exported_file.write(self.fill_template(tmp2, 'navigation', self.make_navigation(self.pages, page)))
                exported_file.close()
                page = page+1
                item=1
                tmp2 = None
            else:
                item=item+1
            i=i+1
        #}}}
        # convert/copy the griffith picture for movies without a poster
        image_file_src = os.path.join(self.locations['images'], 'griffith.png')
        image_file_dst = os.path.join(posters_dir, 'nopic.' + config['poster_format'].lower())
        try:
            if config['poster_convert']:
                im = Image.open(image_file_src, 'r').convert(config['poster_mode'])
                im.thumbnail((config['poster_width'], config['poster_height']), Image.ANTIALIAS)
            else:
                im = Image.open(image_file_src, 'r')
            im.save(image_file_dst, config['poster_format'])
        except:
            log.info("Can't convert %s" % image_file_src)
        gutils.info(self, _("Document has been generated."), self)
        self.on_quit()
    #}}}

