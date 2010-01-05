# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright © 2005-2009 Vasco Nunes, Piotr Ożarowski
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

import gettext
import logging
import math
import os
import platform
import re
import sys
from glob import glob
from locale import getdefaultlocale

import gobject
import gtk

import db
import gutils

try:
    import gtkspell
    spell_support = 1
except:
    spell_support = 0

log = logging.getLogger("Griffith")


def locations(self, home_dir):
    defaultLang, defaultEnc = getdefaultlocale()
    if defaultEnc is None:
        defaultEnc = 'UTF-8'
    locations = {}
    locations['exec'] = os.path.abspath(os.path.dirname(sys.argv[0])) # deprecated
    locations['lib'] = os.path.dirname(__file__)
    locations['home'] = home_dir

    if os.name == 'nt' or os.name.startswith('win'): # win32, win64
        import winshell
        from win32com.shell import shellcon, shell

        locations['movie_plugins'] = "%s\\lib\\plugins\\movie" % locations['exec']
        locations['export_plugins'] = "%s\\lib\\plugins\\export" % locations['exec']
        locations['images'] = "%s\\images" % locations['exec']
        locations['share'] = locations['images']
        locations['glade'] = "%s\\glade\\" % locations['exec']
        locations['desktop'] = ''
        locations['i18n'] = "%s\\i18n" % locations['exec']
        os.environ['PATH'] += ";lib;"

        # windows hack for locale setting
        lang = os.getenv('LANG')
        if lang is None:
            if defaultLang:
                lang = defaultLang
        if lang:
            os.environ['LANG'] = lang

    elif os.name == 'posix':
        locations['share'] = os.path.abspath(os.path.join(locations['lib'], '..'))
        locations['glade'] = os.path.join(locations['share'], 'glade')
        locations['i18n'] = os.path.abspath(os.path.join(locations['share'], '..', 'locale'))
        if not os.path.isdir(locations['i18n']):
            locations['i18n'] = os.path.join(locations['share'], 'i18n')
        #some locations
        locations['movie_plugins'] = os.path.join(locations['lib'], 'plugins', 'movie')
        locations['export_plugins'] = os.path.join(locations['lib'], 'plugins', 'export')
        locations['images'] = os.path.join(locations['share'], 'images')
        locations['desktop'] = os.path.join(os.path.expanduser('~'), 'Desktop').decode(defaultEnc)
    else:
        print 'Operating system not supported'
        sys.exit()

    from tempfile import gettempdir
    locations['temp'] = gettempdir()

    try:
        if not os.path.exists(locations['home']):
            log.info('Creating %s', locations['home'])
            os.makedirs(locations['home'])
        else:
            log.info("Using Griffith directory: %s", locations['home'])
    except OSError:
        log.info('Unable to create griffith directory.')
        raise
        sys.exit()

    if not os.access(locations['home'], os.W_OK):
        log.info('Cannot write to griffith directory, %s', locations['home'])
        sys.exit()

    locations['posters'] = os.path.join(locations['home'], 'posters')
    if not os.path.isdir(locations['posters']):
        os.makedirs(locations['posters'])

    # includes plugins in system path for easier importing
    sys.path.append(locations['lib'])
    sys.path.append(locations['movie_plugins'])
    sys.path.append(locations['export_plugins'])

    self.locations = locations
    return locations


def gui(self):
    self._ = None

    if platform.system() == 'Darwin':
        self.mac = True
    else:
        self.mac = False

    self.griffith_dir = self.locations['home']    # deprecated

    if self.windows:
        gtk.rc_parse('%s\\gtkrc' % self.locations['exec'])

    gf = os.path.join(self.locations['glade'], 'griffith.glade')
    from widgets import define_widgets
    define_widgets(self, gtk.glade.XML(gf))

    self.pdf_reader = self.config.get('pdf_reader')


def i18n(self, location):
    gettext.bindtextdomain('griffith', location)
    gettext.textdomain('griffith')
    gtk.glade.bindtextdomain('griffith', location)
    gtk.glade.textdomain('griffith')
    gettext.install('griffith', location, unicode=1)


def toolbar(self):
    """if toolbar is hide in config lets hide the widget"""
    if not self.config.get('view_toolbar', True, section='window'):
        self.widgets['toolbar'].hide()
        self.widgets['menu']['toolbar'].set_active(False)
    else:
        self.widgets['toolbar'].show()
        self.widgets['menu']['toolbar'].set_active(True)
    if not self.config.get('view_ext_toolbar', True, section='window'):
        self.widgets['extensions']['toolbar_hb'].hide()
        self.widgets['menu']['ext_toolbar'].set_active(False)
    else:
        self.widgets['extensions']['toolbar_hb'].show()
        self.widgets['menu']['ext_toolbar'].set_active(True)


def treeview(self):
    self.treemodel = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, str, str, str, bool, str, str, int)
    self.widgets['treeview'].set_model(self.treemodel)
    self.widgets['treeview'].set_headers_visible(True)
    # number column
    renderer = gtk.CellRendererText()
    self.number_column = gtk.TreeViewColumn(_('No.'), renderer, text=0)
    self.number_column.set_resizable(True)
    self.number_column.set_sort_column_id(0)
    self.number_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.number_column)
    # pic column
    renderer = gtk.CellRendererPixbuf()
    self.image_column = gtk.TreeViewColumn(_('Image'), renderer, pixbuf=1)
    self.image_column.set_resizable(False)
    self.image_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.image_column)
    # original title column
    renderer = gtk.CellRendererText()
    self.otitle_column = gtk.TreeViewColumn(_('Original Title'), renderer, text=2)
    self.otitle_column.set_resizable(True)
    self.otitle_column.set_sort_column_id(2)
    self.otitle_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.otitle_column)
    # title column
    renderer = gtk.CellRendererText()
    self.title_column = gtk.TreeViewColumn(_('Title'), renderer, text=3)
    self.title_column.set_resizable(True)
    self.title_column.set_sort_column_id(3)
    self.title_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.title_column)
    # director column
    renderer = gtk.CellRendererText()
    self.director_column = gtk.TreeViewColumn(_('Director'), renderer, text=4)
    self.director_column.set_sort_column_id(4)
    self.director_column.set_resizable(True)
    self.director_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.director_column)
    # genre column
    renderer = gtk.CellRendererText()
    self.genre_column = gtk.TreeViewColumn(_('Genre'), renderer, text=5)
    self.genre_column.set_sort_column_id(5)
    self.genre_column.set_resizable(True)
    self.genre_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.genre_column)
    # seen column
    renderer = gtk.CellRendererToggle()
    self.seen_column = gtk.TreeViewColumn(_('Seen it'), renderer, active=6)
    self.seen_column.set_sort_column_id(6)
    self.seen_column.set_resizable(True)
    self.seen_column.set_reorderable(True)
    self.widgets['treeview'].insert_column(self.seen_column, 1)
    # year column
    renderer = gtk.CellRendererText()
    renderer.set_property('xalign', 0.5)
    self.year_column = gtk.TreeViewColumn(_('Year'), renderer, text=7)
    self.year_column.set_sort_column_id(7)
    self.year_column.set_resizable(True)
    self.year_column.set_alignment(0.5)
    self.year_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.year_column)
    # runtime column
    renderer = gtk.CellRendererText()
    renderer.set_property('xalign', 1)
    self.runtime_column = gtk.TreeViewColumn(_('Runtime'), renderer, text=8)
    self.runtime_column.set_sort_column_id(8)
    self.runtime_column.set_resizable(True)
    self.runtime_column.set_alignment(1)
    self.runtime_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.runtime_column)
    # rating column
    renderer = gtk.CellRendererText()
    renderer.set_property('xalign', 0.5)
    self.rating_column = gtk.TreeViewColumn(_('Rating'), renderer, text=9)
    self.rating_column.set_sort_column_id(9)
    self.rating_column.set_resizable(True)
    self.rating_column.set_alignment(0.5)
    self.rating_column.set_reorderable(True)
    self.widgets['treeview'].append_column(self.rating_column)
    # reflect saved column order
    columnorder = self.config.get('columnorder', None, section='mainlist')
    if not columnorder is None:
        currentcol = None
        columnordersplitted = re.split('[ \t]*,[ \t]*', columnorder)
        for col in columnordersplitted:
            if col == 'number':
                self.widgets['treeview'].move_column_after(self.number_column, currentcol)
                currentcol = self.number_column
            elif col == 'image':
                self.widgets['treeview'].move_column_after(self.image_column, currentcol)
                currentcol = self.image_column
            elif col == 'otitle':
                self.widgets['treeview'].move_column_after(self.otitle_column, currentcol)
                currentcol = self.otitle_column
            elif col == 'title':
                self.widgets['treeview'].move_column_after(self.title_column, currentcol)
                currentcol = self.title_column
            elif col == 'director':
                self.widgets['treeview'].move_column_after(self.director_column, currentcol)
                currentcol = self.director_column
            elif col == 'genre':
                self.widgets['treeview'].move_column_after(self.genre_column, currentcol)
                currentcol = self.genre_column
            elif col == 'seen':
                self.widgets['treeview'].move_column_after(self.seen_column, currentcol)
                currentcol = self.seen_column
            elif col == 'year':
                self.widgets['treeview'].move_column_after(self.year_column, currentcol)
                currentcol = self.year_column
            elif col == 'runtime':
                self.widgets['treeview'].move_column_after(self.runtime_column, currentcol)
                currentcol = self.runtime_column
            elif col == 'rating':
                self.widgets['treeview'].move_column_after(self.rating_column, currentcol)
                currentcol = self.rating_column
    # reflect saved column sorting
    columnsortid = self.config.get('columnsortid', None, section='mainlist')
    columnsortorder = self.config.get('columnsortorder', None, section='mainlist')
    try:
        if columnsortid:
            columnsortid = int(columnsortid)
            if columnsortorder:
                columnsortorder = gtk.SortType(int(columnsortorder))
            else:
                columnsortorder = gtk.SORT_ASCENDING
            self.treemodel.set_sort_column_id(columnsortid, columnsortorder)
    except:
        log.exception('')
    # add data to treeview
    self.total = self.db.session.query(db.Movie).count()
    self.widgets['treeview'].show()


def loans_treeview(self):
    self.loans_treemodel = gtk.TreeStore(str, str, str) # move to self.widgets
    self.widgets['movie']['loan_history'].set_model(self.loans_treemodel)
    self.widgets['movie']['loan_history'].set_headers_visible(True)
    # loan date
    renderer = gtk.CellRendererText()
    self.date_column = gtk.TreeViewColumn(_('Loan Date'), renderer, text=0)
    self.date_column.set_resizable(True)
    self.widgets['movie']['loan_history'].append_column(self.date_column)
    self.date_column.set_sort_column_id(0)
    # return date
    renderer = gtk.CellRendererText()
    self.return_column = gtk.TreeViewColumn(_('Return Date'), renderer, text=1)
    self.return_column.set_resizable(True)
    self.widgets['movie']['loan_history'].append_column(self.return_column)
    # loan to
    renderer = gtk.CellRendererText()
    self.loaner_column = gtk.TreeViewColumn(_('Loaned To'), renderer, text=2)
    self.loaner_column.set_resizable(True)
    self.widgets['movie']['loan_history'].append_column(self.loaner_column)


def lang_treeview(self):
    treeview = self.widgets['add']['lang_treeview']
    self.lang['model'] = gtk.TreeStore(str, str, str, str, str)
    treeview.set_model(self.lang['model'])
    treeview.set_headers_visible(True)

    model = self.lang['lang'] = gtk.ListStore(int, str)
    for i in self.db.session.query(db.Lang.lang_id, db.Lang.name).all():
        model.append([i.lang_id, i.name])
    combo = gtk.CellRendererCombo()
    combo.set_property('model', model)
    combo.set_property('text-column', 1)
    combo.set_property('editable', True)
    combo.set_property('has-entry', False)
    combo.connect('edited', self.on_tv_lang_combo_edited, 0)
    column = gtk.TreeViewColumn(_('Language'), combo, text=0)
    column.set_property('min-width', 80)
    column.set_property('resizable', True)
    column.set_sort_column_id(0)
    treeview.append_column(column)

    model = self.lang['type'] = gtk.ListStore(int, str)
    #i = 0
    #for lang_type in self._lang_types:
    #    model.append([i, lang_type])
    #    i += 1
    model.append([0, ''])
    model.append([1, _('lector')])
    model.append([2, _('dubbing')])
    model.append([3, _('subtitles')])
    model.append([4, _("commentary")])
    combo = gtk.CellRendererCombo()
    combo.set_property('model', model)
    combo.set_property('text-column', 1)
    combo.set_property('editable', True)
    combo.set_property('has-entry', False)
    combo.connect('edited', self.on_tv_lang_combo_edited, 1)
    column = gtk.TreeViewColumn(_('Type'), combo, text=1)
    column.set_property('min-width', 80)
    column.set_property('resizable', True)
    column.set_sort_column_id(1)
    treeview.append_column(column)

    model = self.lang['acodec'] = gtk.ListStore(int, str)
    for i in self.db.session.query(db.ACodec.acodec_id, db.ACodec.name).all():
        model.append([i.acodec_id, i.name])
    combo = gtk.CellRendererCombo()
    combo.set_property('model', model)
    combo.set_property('text-column', 1)
    combo.set_property('editable', True)
    combo.set_property('has-entry', False)
    combo.connect('edited', self.on_tv_lang_combo_edited, 2)
    column = gtk.TreeViewColumn(_('Codec'), combo, text=2)
    column.set_property('min-width', 80)
    column.set_property('resizable', True)
    column.set_sort_column_id(2)
    treeview.append_column(column)

    model = self.lang['achannel'] = gtk.ListStore(int, str)
    for i in self.db.session.query(db.AChannel.achannel_id, db.AChannel.name).all():
        model.append([i.achannel_id, i.name])
    combo = gtk.CellRendererCombo()
    combo.set_property('model', model)
    combo.set_property('text-column', 1)
    combo.set_property('editable', True)
    combo.set_property('has-entry', False)
    combo.connect('edited', self.on_tv_lang_combo_edited, 3)
    column = gtk.TreeViewColumn(_('Channels'), combo, text=3)
    column.set_property('min-width', 80)
    column.set_property('resizable', True)
    column.set_sort_column_id(3)
    treeview.append_column(column)

    model = self.lang['subformat'] = gtk.ListStore(int, str)
    for i in self.db.session.query(db.SubFormat.subformat_id, db.SubFormat.name).all():
        model.append([i.subformat_id, i.name])
    combo = gtk.CellRendererCombo()
    combo.set_property('model', model)
    combo.set_property('text-column', 1)
    combo.set_property('editable', True)
    combo.set_property('has-entry', False)
    combo.connect('edited', self.on_tv_lang_combo_edited, 4)
    column = gtk.TreeViewColumn(_('Subtitle format'), combo, text=4)
    column.set_property('min-width', 80)
    column.set_property('resizable', True)
    column.set_sort_column_id(4)
    treeview.append_column(column)

    treeview.show_all()


def movie_plugins(self):
    """
    dinamically finds the movie source information plugins
    and fills the plugins drop down list
    """
    self.plugins = gutils.read_plugins('PluginMovie', \
        self.locations['movie_plugins'])
    self.plugins.sort()
    mcounter = 0
    default_plugin = self.config.get('default_movie_plugin')
    for p in self.plugins:
        plugin_module = os.path.basename(p).replace('.py', '')
        plugin_name = plugin_module.replace('PluginMovie', '')
        self.widgets['add']['source'].append_text(plugin_name)
        self.widgets['preferences']['default_plugin'].append_text(plugin_name)
        if plugin_name == default_plugin:
            self.widgets['preferences']['default_plugin'].set_active(mcounter)
            self.widgets['add']['source'].set_active(mcounter)
        mcounter = mcounter + 1


def export_plugins(self):
    """
    dinamically finds the available export plugins
    and fills the export menu entry
    """
    plugins = gutils.read_plugins('PluginExport', \
        self.locations['export_plugins'])
    plugins.sort()
    for p in plugins:
        plugin_module = os.path.basename(p).replace('.py', '')
        plugin_name = plugin_module.replace('PluginExport', '')
        menu_items = gtk.MenuItem(plugin_name)
        self.widgets['menu']['export'].append(menu_items)
        menu_items.connect('activate', self.on_export_activate, plugin_name)
        menu_items.show()


def import_plugins(self):
    """
    dinamically finds the available import plugins
    and fills the import menu entry
    """

    import plugins.imp

    fields_to_import = ('number', 'title', 'o_title', 'director', 'year', 'runtime', 'country',
        'seen', 'rating', 'genre', 'studio', 'plot', 'cast', 'notes', 'classification',
        'site', 'o_site', 'trailer', 'medium_id', 'media_num', 'vcodec_id', 'color', 'cond',
        'layers', 'region', 'collection_id', 'volume_id', 'image', 'ratio_id', 'screenplay',
        'cameraman', 'barcode', 'tags', 'poster')

    # glade
    glade_file = gtk.glade.XML(os.path.join(self.locations['glade'], 'import.glade'))
    get = lambda x: glade_file.get_widget(x)

    w = self.widgets['import'] = {
        'window': get('dialog_import'),
        'pwindow': get('dialog_progress'),
        'pabort': get('p_abortbutton'),
        'fcw': get('fcw'),
        'plugin': get('combo_plugin'),
        'author': get('l_author'),
        'email': get('l_email'),
        'version': get('l_version'),
        'description': get('l_description'),
        'box_import_1': get('box_import_1'),
        'box_import_2': get('box_import_2'),
        'box_import_3': get('box_import_3'),
        'progress': get('l_progress'),
        'progressbar': get('progressbar'),
        'fields': {},
    }
    get('cancel_button').connect('clicked', plugins.imp.on_abort_button_clicked, self)
    get('import_button').connect('clicked', plugins.imp.on_import_button_clicked, self)
    w['plugin'].connect('changed', plugins.imp.on_import_plugin_changed, w)
    w['window'].set_transient_for(self.widgets['window'])
    w['pwindow'].set_transient_for(self.widgets['window'])

    for name in plugins.imp.__all__:
        w['plugin'].append_text(name)
    w['plugin'].set_active(0)

    # fields to import
    j = 0
    k = math.ceil(len(self.field_names) / float(3))
    for i in fields_to_import:
        j = j + 1
        w['fields'][i] = gtk.CheckButton(self.field_names[i])
        w['fields'][i].set_active(True) # TODO: get from config
        if j <= k:
            w['box_import_1'].add(w['fields'][i])
        elif j <= 2 * k:
            w['box_import_2'].add(w['fields'][i])
        else:
            w['box_import_3'].add(w['fields'][i])
    w['box_import_1'].show_all()
    w['box_import_2'].show_all()
    w['box_import_3'].show_all()


def extension(self, module, enabled):
    if enabled:
        try:
            ext = module(self)
        except (NotImplementedError, DeprecationWarning), e:
            log.warning('extension skipped: %s', e.message)
            log.debug('extension skipped: %s', module.__file__)
            return [None, None]
        if module.toolbar_icon:
            toolbar = self.widgets['extensions']['toolbar']
            if module.toolbar_icon.endswith('.png'):
                icon_path = os.path.join(os.path.dirname(module.__file__), 'data', module.toolbar_icon)
                if not os.path.isfile(icon_path):
                    icon_path = os.path.join(self.locations['images'], module.toolbar_icon)
                if not os.path.isfile(icon_path):
                    log.error('icon not found: %s', module.toolbar_icon)
                else:
                    icon = gtk.Image()
                    icon.set_from_file(icon_path)
                    ext.toolbar_icon_widget = toolbar.insert_item(None, module.description, None, icon, ext._on_toolbar_icon_clicked, None, -1)
            else:
                ext.toolbar_icon_widget = toolbar.insert_stock(module.toolbar_icon, module.description, None, ext._on_toolbar_icon_clicked, None, -1)
    else:
        ext = None

    return ext


def extension_preferences(self, module, enabled):
    # preferences window
    p_vbox = self.widgets['extensions']['preferences_vbox']

    configwidgets = {}

    label = "%s v%s <i>(%s &lt;%s&gt;)</i>" % (module.name, module.version, module.author, module.email)
    expander = gtk.Expander(label=label)
    expander.get_label_widget().set_tooltip_markup(module.description)
    expander.set_use_markup(True)
    vbox = gtk.VBox()

    # extension details
    hbox = gtk.HBox()
    vbox.pack_start(hbox, expand=False)
    enabled_cb = gtk.CheckButton(label=_('enable this extension'))
    enabled_cb.set_active(enabled)
    configwidgets['enabled'] = enabled_cb
    vbox.pack_start(enabled_cb, expand=False)

    for pref_name in module.preferences:
        name = module.preferences[pref_name].get('name', pref_name)
        hint = module.preferences[pref_name].get('hint')
        value = module.preferences[pref_name].get('default')
        value = self.config.get("%s_%s" % (module.name, pref_name), value, section='extensions')
        type_ = module.preferences[pref_name].get('type', unicode)

        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(name), expand=False, padding=4)

        if type_ is unicode:
            w = gtk.Entry()
            w.insert_text(value)
            # TODO: min, max
        # elif type is int: # TODO
        elif isinstance(type_, (list, tuple, dict)):
            model = gtk.TreeStore(str, str)
            if isinstance(type_, dict):
                iterable = type_.iteritems()
            else:
                iterable = enumerate(type_)
            pos = None
            count = 0
            for code, codevalue in iterable:
                myiter = model.append(None, None)
                model.set_value(myiter, 0, unicode(code))
                model.set_value(myiter, 1, unicode(codevalue))
                if value and value == codevalue:
                    pos = count
                count = count + 1
            # combobox with complex binding to a model needs cell renderer
            w = gtk.ComboBox(model=model)
            renderer = gtk.CellRendererText()
            w.pack_start(renderer)
            w.add_attribute(renderer, 'text', 1)
            if pos is not None:
                w.set_active(int(pos))
        else:
            log.error('type not recognized %s', type(type_))
            continue

        if hint:
            w.set_tooltip_markup(hint)
        hbox.pack_start(w)

        vbox.pack_start(hbox, expand=False)

        configwidgets[pref_name] = w

    expander.add(vbox)
    p_vbox.pack_start(expander, expand=False)
    p_vbox.show_all()

    return configwidgets


def extensions(self):
    import plugins.extensions
    user_extensions_path = os.path.join(self.locations['home'], 'lib', 'extensions')
    if os.path.isdir(user_extensions_path):
        plugins.extensions.scan_for_extensions(user_extensions_path)

    if hasattr(self, 'extensions'):
        for ext in self.extensions:
            ext.clear()
    self.extensions = [] # deletes previous instances

    for ext_name in plugins.extensions.by_name:
        ext_module = plugins.extensions.by_name[ext_name]
        enabled = self.config.get("%s_enabled" % ext_name, ext_module.enabled, section='extensions')
        if not hasattr(ext_module, 'preferenceswidgets'):
            ext_module.preferenceswidgets = extension_preferences(self, ext_module, enabled)
        ext = extension(self, ext_module, enabled)
        if ext:
            self.extensions.append(ext)


def people_treeview(self, create=True):
    row = None
    self.p_treemodel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
    self.widgets['preferences']['treeview'].set_model(self.p_treemodel)
    self.widgets['preferences']['treeview'].set_headers_visible(True)

    if create is True:
        # name column
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Name'), renderer, text=0)
        column.set_resizable(True)
        column.set_sort_column_id(0)
        self.widgets['preferences']['treeview'].append_column(column)
        # email column
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('E-mail'), renderer, text=1)
        column.set_resizable(True)
        column.set_sort_column_id(1)
        self.widgets['preferences']['treeview'].append_column(column)
    # add data to treeview
    self.p_treemodel.clear()
    for i in self.db.session.query(db.Person.name, db.Person.email).order_by(db.Person.name.asc()):
        myiter = self.p_treemodel.insert_before(None, None)
        self.p_treemodel.set_value(myiter, 0, i.name)
        self.p_treemodel.set_value(myiter, 1, i.email)
    self.widgets['preferences']['treeview'].show()


def combos(self):
    i = 0
    for cond in self._conditions:
        self.widgets['preferences']['condition'].insert_text(i, cond)
        self.widgets['add']['condition'].insert_text(i, cond)
        i += 1
    i = 0
    for color in self._colors:
        self.widgets['preferences']['color'].insert_text(i, color)
        self.widgets['add']['color'].insert_text(i, color)
        i += 1
    i = 0
    for region in self._regions:
        self.widgets['preferences']['region'].insert_text(i, region)
        self.widgets['add']['region'].insert_text(i, region)
        i += 1
    i = 0
    for layer in self._layers:
        self.widgets['preferences']['layers'].insert_text(i, layer)
        self.widgets['add']['layers'].insert_text(i, layer)
        i += 1
    i = 0
    pos_to_activate = 0
    selected_criteria = self.config.get('criteria', None, section='mainlist')
    for criteria in self.search_criteria:
        new_criteria = self.field_names[criteria]
        self.widgets['filter']['criteria'].insert_text(i, new_criteria)
        if selected_criteria == new_criteria:
            pos_to_activate = i
        i += 1
    self.widgets['filter']['criteria'].set_active(pos_to_activate)
    i = 0
    for field in self.sort_criteria:
        if field != 'movie_id':
            self.widgets['preferences']['sortby'].insert_text(i, self.field_names[field])
        else:
            self.widgets['preferences']['sortby'].insert_text(i, _('Last added'))
        i += 1
    self.widgets['preferences']['sortby'].set_wrap_width(3)
    self.widgets['preferences']['sortby'].set_active(0) # Number


def dictionaries(self):
    """initializes data filled dynamically by users"""
    self.am_tags = {} # dictionary for tag CheckBoxes
    update_volume_combo_ids(self)
    update_collection_combo_ids(self)
    fill_volumes_combo(self)
    fill_collections_combo(self)
    fill_advfilter_combo(self)
    fill_preferences_tags_combo(self)
    language_combos(self)
    acodec_combos(self)
    achannel_combos(self)
    subformat_combos(self)
    vcodec_combos(self)
    media_combos(self)
    create_tag_vbox(self, widget=self.widgets['add']['tag_vbox'], tab=self.am_tags)
    self.sort_criteria = [ # "[]" because of index()
        'number', 'o_title', 'title', 'director', 'year', 'runtime', 'country',
        'genre', 'studio', 'media_num', 'rating', 'classification', 'collection_id',
        'volume_id', 'cond', 'layers', 'region', 'movie_id']
    self.search_criteria = (
        'o_title', 'title', 'number', 'director', 'plot', 'cast', 'notes', 'year',
        'runtime', 'country', 'genre', 'studio', 'media_num', 'rating')
    self.field_names = {
        'barcode': _('Barcode'),
        'cast': _('Cast'),
        'cameraman': _('Cameraman'),
        'classification': _('Classification'),
        'collection_id': _('Collection'),
        'color': _('Color'),
        'cond': _('Condition'),
        'country': _('Country'),
        'director': _('Director'),
        'genre': _('Genre'),
        'image': _('Image'),
        'layers': _('Layers'),
        'loaned': _('Loaned'),
        'media_num': _('Discs'),
        'medium_id': _('Medium'),
        'notes': _('Notes'),
        'number': _('Number'),
        'o_site': _('Official site'),
        'o_title': _('Original Title'),
        'plot': _('Plot'),
        'poster': _('Poster'),
        'ratio_id': _('Aspect ratio'),
        'rating': _('Rating'),
        'region': _('Region'),
        'runtime': _('Runtime'),
        'screenplay': _('Screenplay'),
        'seen': _('Seen it'),
        'site': _('Site'),
        'studio': _('Studio'),
        'tags': _('Tags'),
        'title': _('Title'),
        'trailer': _('Trailer'),
        'vcodec_id': _('Video codec'),
        'volume_id': _('Volume'),
        'year': _('Year')}
    self._conditions = (_('N/A'), _('Damaged'), _('Poor'), _('Fair'), _('Good'), _('Excellent'))
    self._colors = (_('N/A'), _('Color'), _('Black and White'), _('Mixed'))
    self._lang_types = ('', _('lector'), _('dubbing'), _('subtitles'), _('commentary'))
    self._layers = (_('N/A'), _('Single Side, Single Layer'), _('Single Side, Dual Layer'), _('Dual Side, Single Layer'), _('Dual Side, Dual Layer'))
    self._regions = (
        _('Region 0 (No Region Coding)'),
        _('Region 1 (United States of America, Canada)'),
        _('Region 2 (Europe, Egypt, Arabia, Japan and South Africa)'),
        _('Region 3 (Korea, Thailand, Vietnam, Borneo and Indonesia)'),
        _('Region 4 (Australia and New Zealand, Mexico and South America)'),
        _('Region 5 (India, Africa, Russia and former USSR countries)'),
        _('Region 6 (Popular Republic of China)'),
        _('Region 7 (Reserved for Unspecified Special Use)'),
        _('Region 8 (Airlines/Cruise Ships)'),
    )


def web_results(self):
    self.treemodel_results = gtk.TreeStore(str, str)
    self.widgets['results']['treeview'].set_model(self.treemodel_results)
    self.widgets['results']['treeview'].set_headers_visible(False)
    # column ids
    renderer = gtk.CellRendererText()
    column1 = gtk.TreeViewColumn(None, renderer, text=0)
    column1.set_visible(False)
    self.widgets['results']['treeview'].append_column(column1)
    # column titles
    renderer = gtk.CellRendererText()
    column2 = gtk.TreeViewColumn(None, renderer, text=1)
    column2.set_resizable(True)
    column2.set_sort_column_id(1)
    self.widgets['results']['treeview'].append_column(column2)


def spellcheck(self):
    global spell_support
    spell_error = False
    if self.posix and spell_support:
        if self.config.get('gtkspell', False, section='spell') == True:
            if self.config.get('notes', True, section='spell') == True and self.config.get('lang', section='spell') != '':
                try:
                    self.notes_spell = gtkspell.Spell(self.widgets['add']['cast'], self.config.get('lang', section='spell'))
                except:
                    spell_error = True
            if self.config.get('plot', True, section='spell') is True and self.config.get('lang', section='spell') != '':
                try:
                    self.plot_spell = gtkspell.Spell(self.widgets['add']['plot'], self.config.get('lang', section='spell'))
                except:
                    spell_error = True
            if spell_error:
                log.info('Dictionary not available. Spellcheck will be disabled.')
                if not self.config.get('notified', False, section='spell'):
                    gutils.info(_("Dictionary not available. Spellcheck will be disabled. \n" + \
                        "Please install the aspell-%s package or adjust the spellchekcer preferences.") % self.config.get('lang', section='spell'), \
                        self.widgets['preferences']['window'])
                    self.config.set('notified', True, section='spell')
                    self.config.save()
    else:
        log.info('Spellchecker is not available')


def preferences(self):
    self.widgets['preferences']['db_type'].insert_text(0, 'SQLite3 (internal)')
    self.widgets['preferences']['db_type'].insert_text(1, 'PostgreSQL')
    self.widgets['preferences']['db_type'].insert_text(2, 'MySQL')
    self.widgets['preferences']['db_type'].insert_text(3, 'Microsoft SQL')
    self.widgets['preferences']['db_host'].set_text(self.config.get('host', '', section='database'))
    self.widgets['preferences']['db_port'].set_value(int(self.config.get('port', 0, section='database')))
    self.widgets['preferences']['db_user'].set_text(self.config.get('user', '', section='database'))
    self.widgets['preferences']['db_passwd'].set_text(self.config.get('passwd', '', section='database'))
    self.widgets['preferences']['db_name'].set_text(self.config.get('name', '', section='database'))
    db_type = self.config.get('type', 'sqlite', section='database')
    if db_type == 'postgres':
        self.widgets['preferences']['db_type'].set_active(1)
    elif db_type == 'mysql':
        self.widgets['preferences']['db_type'].set_active(2)
    elif db_type == 'mssql':
        self.widgets['preferences']['db_type'].set_active(3)
    else:
        self.widgets['preferences']['db_type'].set_active(0)

    # add completion data
    treemodel = gtk.TreeStore(str)
    for name in (os.path.basename(x)[:-3] for x in glob("%s/*.db" % self.locations['home'])):
        myiter = treemodel.append(None)
        treemodel.set_value(myiter, 0, name)
    completion = gtk.EntryCompletion()
    completion.set_minimum_key_length(0)
    self.widgets['preferences']['db_name'].set_completion(completion)
    completion.set_model(treemodel)
    completion.set_text_column(0)


def update_volume_combo_ids(self):
    self.volume_combo_ids = {}
    self.volume_combo_ids[0] = 0
    for i, item in enumerate(self.db.session.query(db.Volume.volume_id).all()):
        self.volume_combo_ids[i + 1] = item.volume_id


def update_collection_combo_ids(self):
    self.collection_combo_ids = {}
    self.collection_combo_ids[0] = 0
    for i, item in enumerate(self.db.session.query(db.Collection.collection_id).all()):
        self.collection_combo_ids[i + 1] = item.collection_id


def fill_volumes_combo(self, default=0):
    _tmp = self.initialized
    self.initialized = False # don't refresh main treeview
    self.widgets['add']['volume'].get_model().clear()
    for i in self.volume_combo_ids:
        vol_id = self.volume_combo_ids[i]
        if vol_id > 0:
            name = self.db.session.query(db.Volume.name).filter_by(volume_id=vol_id).first().name
        else:
            name = ''
        self.widgets['add']['volume'].insert_text(int(i), name)
    self.widgets['add']['volume'].show_all()
    i = gutils.findKey(default, self.volume_combo_ids)
    if i is not None:
        self.widgets['add']['volume'].set_active(int(i))
    self.widgets['add']['volume'].set_wrap_width(3)
    self.initialized = _tmp


def fill_collections_combo(self, default=0):
    _tmp = self.initialized
    self.initialized = False # don't refresh main treeview
    self.widgets['add']['collection'].get_model().clear()
    self.widgets['filter']['collection'].get_model().clear()
    for i in self.collection_combo_ids:
        col_id = self.collection_combo_ids[i]
        if col_id > 0:
            name = self.db.session.query(db.Collection.name).filter_by(collection_id=col_id).first().name
        else:
            name = ''
        self.widgets['add']['collection'].insert_text(int(i), name)
        # add some white spaces to prevent scrollbar hides parts of the names
        self.widgets['filter']['collection'].insert_text(int(i), name + '   ')
    self.widgets['add']['collection'].show_all()
    self.widgets['filter']['collection'].show_all()
    self.widgets['filter']['collection'].set_active(0)
    i = gutils.findKey(default, self.collection_combo_ids)
    if i is not None:
        self.widgets['add']['collection'].set_active(int(i))
    self.widgets['add']['collection'].set_wrap_width(2)
    self.initialized = _tmp


def fill_advfilter_combo(self):
    _tmp = self.initialized
    self.initialized = False # don't refresh main treeview
    self.widgets['filter']['advfilter'].get_model().clear()
    self.widgets['filter']['advfilter'].insert_text(0, '') # empty one
    for i, item in enumerate(self.db.session.query(db.Filter.name).all()):
        # add some white spaces to prevent scrollbar hides parts of the names
        self.widgets['filter']['advfilter'].insert_text(i + 1, item.name + '   ')
    self.widgets['filter']['advfilter'].show_all()
    self.widgets['filter']['advfilter'].set_active(0)
    self.initialized = _tmp


def fill_preferences_tags_combo(self):
    _tmp = self.initialized
    self.initialized = False # don't refresh main treeview
    self.widgets['preferences']['tag_name'].get_model().clear()
    self.tags_ids = {}
    for i, tag in enumerate(self.db.session.query(db.Tag.name, db.Tag.tag_id).all()):
        self.tags_ids[i] = tag.tag_id
        self.widgets['preferences']['tag_name'].insert_text(i, tag.name)
    self.widgets['preferences']['tag_name'].show_all()
    self.widgets['preferences']['tag_name'].set_active(0)
    self.initialized = _tmp


def language_combos(self):
    self.widgets['preferences']['lang_name'].get_model().clear()
    self.languages_ids = {}
    self.languages_ids[0] = 0    # empty one
    self.lang['lang'].clear()
    self.widgets['preferences']['lang_name'].insert_text(0, '')
    for i, lang in enumerate(self.db.session.query(db.Lang.lang_id, db.Lang.name).all()):
        self.languages_ids[i] = lang.lang_id
        self.widgets['preferences']['lang_name'].insert_text(i + 1, lang.name)
        # add movie languages treeview
        self.lang['lang'].append([lang.lang_id, lang.name])
    self.widgets['preferences']['lang_name'].show_all()
    self.widgets['preferences']['lang_name'].set_active(0)


def acodec_combos(self):
    self.widgets['preferences']['acodec_name'].get_model().clear()
    self.acodecs_ids = {}
    self.acodecs_ids[0] = 0    # empty one
    self.lang['acodec'].clear()
    self.widgets['preferences']['acodec_name'].insert_text(0, '')
    for i, acodec in enumerate(self.db.session.query(db.ACodec.acodec_id, db.ACodec.name).all()):
        self.acodecs_ids[i] = acodec.acodec_id
        self.widgets['preferences']['acodec_name'].insert_text(i + 1, acodec.name)
        # add movie languages treeview
        self.lang['acodec'].append([acodec.acodec_id, acodec.name])
    self.widgets['preferences']['acodec_name'].show_all()
    self.widgets['preferences']['acodec_name'].set_active(0)


def achannel_combos(self):
    self.widgets['preferences']['achannel_name'].get_model().clear()
    self.achannels_ids = {}
    self.achannels_ids[0] = 0    # empty one
    self.lang['achannel'].clear()
    self.widgets['preferences']['achannel_name'].insert_text(0, '')
    for i, achannel in enumerate(self.db.session.query(db.AChannel.achannel_id, db.AChannel.name).all()):
        self.achannels_ids[i] = achannel.achannel_id
        self.widgets['preferences']['achannel_name'].insert_text(i + 1, achannel.name)
        # add movie languages treeview
        self.lang['achannel'].append([achannel.achannel_id, achannel.name])
    self.widgets['preferences']['achannel_name'].show_all()
    self.widgets['preferences']['achannel_name'].set_active(0)


def subformat_combos(self):
    self.widgets['preferences']['subformat_name'].get_model().clear()
    self.subformats_ids = {}
    self.subformats_ids[0] = 0    # empty one
    self.lang['subformat'].clear()
    self.widgets['preferences']['subformat_name'].insert_text(0, '')
    for i, subformat in enumerate(self.db.session.query(db.SubFormat.subformat_id, db.SubFormat.name).all()):
        self.subformats_ids[i] = subformat.subformat_id
        self.widgets['preferences']['subformat_name'].insert_text(i + 1, subformat.name)
        # add movie languages treeview
        self.lang['subformat'].append([subformat.subformat_id, subformat.name])
    self.widgets['preferences']['subformat_name'].show_all()
    self.widgets['preferences']['subformat_name'].set_active(0)


def media_combos(self):
    # clear data
    self.widgets['preferences']['medium_name'].get_model().clear()
    self.widgets['preferences']['media'].get_model().clear()
    self.widgets['add']['media'].get_model().clear()

    self.media_ids = {}

    self.media_ids[0] = None
    self.widgets['preferences']['medium_name'].insert_text(0, '')
    self.widgets['add']['media'].insert_text(0, _('N/A'))
    self.widgets['preferences']['media'].insert_text(0, _('N/A'))
    for i, medium in enumerate(self.db.session.query(db.Medium.medium_id, db.Medium.name).all()):
        self.media_ids[i + 1] = medium.medium_id
        self.widgets['preferences']['medium_name'].insert_text(i + 1, medium.name)
        self.widgets['add']['media'].insert_text(i + 1, medium.name)
        self.widgets['preferences']['media'].insert_text(i + 1, medium.name)

    self.widgets['preferences']['medium_name'].show_all()
    self.widgets['add']['media'].show_all()
    self.widgets['preferences']['media'].show_all()
    if self.config.has_key('media', section='defaults'):
        pos = gutils.findKey(self.config.get('media', section='defaults'), self.media_ids)
        if pos  is not None:
            self.widgets['preferences']['media'].set_active(int(pos))
        else:
            self.widgets['preferences']['media'].set_active(0)
    else:
        self.widgets['preferences']['media'].set_active(0)
    self.widgets['preferences']['medium_name'].set_active(0)


def vcodec_combos(self):
    # clear data
    self.widgets['preferences']['vcodec_name'].get_model().clear()
    self.widgets['preferences']['vcodec'].get_model().clear()
    self.widgets['add']['vcodec'].get_model().clear()

    self.vcodecs_ids = {}

    self.vcodecs_ids[0] = None
    self.widgets['preferences']['vcodec_name'].insert_text(0, '')
    self.widgets['add']['vcodec'].insert_text(0, _('N/A'))
    self.widgets['preferences']['vcodec'].insert_text(0, _('N/A'))
    for i, vcodec in enumerate(self.db.session.query(db.VCodec.vcodec_id, db.VCodec.name).all()):
        self.vcodecs_ids[i + 1] = vcodec.vcodec_id
        self.widgets['preferences']['vcodec_name'].insert_text(i + 1, vcodec.name)
        self.widgets['add']['vcodec'].insert_text(i + 1, vcodec.name)
        self.widgets['preferences']['vcodec'].insert_text(i + 1, vcodec.name)

    self.widgets['preferences']['vcodec_name'].show_all()
    self.widgets['add']['vcodec'].show_all()
    self.widgets['preferences']['vcodec'].show_all()

    pos = gutils.findKey(self.config.get('vcodec', 0, section='defaults'), self.vcodecs_ids)
    if pos is not None:
        self.widgets['preferences']['vcodec'].set_active(int(pos))
    else:
        self.widgets['preferences']['vcodec'].set_active(0)
    self.widgets['preferences']['vcodec_name'].set_active(0)


def create_tag_vbox(self, widget, tab):
    for i in widget.get_children():
        i.destroy()
    for i in self.tags_ids:
        tag_id = self.tags_ids[i]
        tag_name = self.db.session.query(db.Tag.name).filter_by(tag_id=tag_id).first().name
        tab[i] = gtk.CheckButton(tag_name)
        tab[i].set_active(False)
        widget.pack_start(tab[i])
    widget.show_all()


def remove_hbox(self, widget, tab):
    number = len(widget.get_children())-1    # last box number
    try:
        tab.pop()
        widget.remove(widget.get_children().pop())
    except:
        log.info('List is empty')
    widget.show_all()
