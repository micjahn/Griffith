# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2006-2007 Piotr Ożarowski
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

import glob
import os
import os.path
import time
import gc
import struct
from tempfile import mkstemp
import add
import logging
log = logging.getLogger("Griffith")

import db
import edit

# detect all plugins:
__all__ = [os.path.basename(x)[:-3] for x in glob.glob("%s/*.py" % os.path.dirname(__file__))]
__all__.remove('__init__')


class ImportPlugin(object):
    description = None
    author = None
    email = None
    version = None
    # file chooser:
    file_filters = None
    mime_types = None

    edit = False        # open add window for every movie?

    imported = 0
    data = None

    previous_dir = None

    # maps foreign key column names to mappings dicts name to id
    foreignkeymaps = None
    # mappings tag names to id
    tagmap = None

    def __init__(self, parent, fields_to_import):
        self.parent = parent
        self.db = parent.db
        self.locations = parent.locations
        self.fields = parent.field_names
        self.conditions = parent._conditions
        self.colors = parent._colors
        self.lang_types = parent._lang_types
        self.layers = parent._layers
        self.regions = parent._regions
        self.widgets = parent.widgets['import']
        self.fields_to_import = fields_to_import
        self._continue = True

    def initialize(self):
        """Initializes plugin (get all parameters from user, etc.)"""
        self.imported = 0
        return True

    def abort(self, *args):
        """called after abort button clicked"""
        self._continue = False

    def set_source(self, name):
        """Prepare source (open file, etc.)"""
        # change current dir because there are posters with relative paths (perhaps)
        self.previous_dir = os.getcwd()
        os.chdir(os.path.dirname(name))

    def count_movies(self):
        """Returns number of movies in file which is about to be imported"""
        pass

    def get_movie_details(self):
        """Returns dictionary with movie details"""
        pass

    def run(self, name):
        """Import movies, function called in a loop over source files"""
        from add import validate_details, edit_movie
        from sqlalchemy import select
        import gtk

        if not self.set_source(name):
            log.info("Can't read data from file %s", name)
            return False

        self.widgets['pwindow'].show()
        while gtk.events_pending():    # give GTK some time for updates
            gtk.main_iteration()

        # progressbar
        update_on = []
        count = self.count_movies()
        if count > 0:
            for i in range(0, 100):
                update_on.append(int(float(i) / 100 * count))

        session = self.db.Session()
        session.bind = self.db.session.bind

        # move some stuff outside the loop to speed it up
        set_fraction = self.widgets['progressbar'].set_fraction
        set_text = self.widgets['progressbar'].set_text
        main_iteration = gtk.main_iteration

        # get some values from DB to avoid queries in the loop
        statement = select([db.Movie.number, db.Movie.title, db.Movie.o_title])
        data = session.execute(statement).fetchall()
        numbers = set(i[0] for i in data)
        titles = set(i[1].lower() for i in data if i[1])
        o_titles = set(i[2].lower() for i in data if i[2])

        gc_was_enabled = gc.isenabled()
        if gc_was_enabled:
            gc.collect()
            gc.disable()

        begin = time.time()
        processed = 0
        try:
            while self._continue:
                details = self.get_movie_details()
                if details is None:
                    break

                processed += 1
                if processed in update_on:
                    set_fraction(float(processed) / count)
                    main_iteration()
                    set_text("%s (%s/%s)" % (self.imported, processed, count))
                    main_iteration()
                    main_iteration() # extra iteration for abort button

                o_title_lower = details.get('o_title', '').lower()
                title_lower = details.get('title', '').lower()

                if o_title_lower or title_lower:
                    if o_title_lower and o_title_lower in o_titles:
                        if title_lower and title_lower in titles:
                            log.info("movie already exists (o_title=%s, title=%s)", details['o_title'], details['title'])
                            continue
                    elif title_lower and title_lower in titles: # o_title is not available so lets check title only
                        log.info("movie already exists (title=%s)", details['title'])
                        continue
                    if self.edit: # XXX: not used for now
                        validate_details(details, self.fields_to_import)
                        response = edit_movie(self.parent, details)    # FIXME: wait until save or cancel button pressed
                        if response == 1:
                            self.imported += 1
                    else:
                        number = details.get('number', 1)
                        while number in numbers:
                            number += 1
                        details['number'] = number
                        if 'tags' in details:
                            tags = details.pop('tags')
                        else:
                            tags = None
                        if 'poster' in details:
                            poster = details.pop('poster')
                        else:
                            poster = None
                        try:
                            # optional: do mapping of lookup data
                            if not self.foreignkeymaps:
                                self._loadmappings()
                            for fkcolumnname in self.foreignkeymaps:
                                try:
                                    if fkcolumnname in details and details[fkcolumnname]:
                                        fkcolumn_id = int(details[fkcolumnname])
                                except:
                                    try:
                                        fkcolumn_id = self.normalizename(details[fkcolumnname])
                                        currentmap = self.foreignkeymaps[fkcolumnname]
                                        if fkcolumn_id in currentmap:
                                            details[fkcolumnname] = currentmap[fkcolumn_id]
                                        else:
                                            details[fkcolumnname] = self._addmappingvalue(fkcolumnname, details[fkcolumnname])
                                    except:
                                        log.exception(fkcolumnname)
                                        details[fkcolumnname] = None
                            # validation before insertion
                            validate_details(details, self.fields_to_import)
                            # insert the movie in the database
                            movie = db.tables.movies.insert(bind=self.db.session.bind).execute(details)
                            self.imported += 1
                            # optional: adding tags
                            if tags:
                                if self.tagmap is None:
                                    self.loadmappings()
                                for tag in tags:
                                    try:
                                        if isinstance(tag, (str, unicode)):
                                            # TODO: adding new tag names?
                                            tag_id = self.tagmap[tag.lower()]
                                        else:
                                            tag_id = int(tag)
                                        db.tables.movie_tag.insert(bind=self.db.session.bind).execute({'movie_id': movie.lastrowid, 'tag_id': tag_id})
                                    except:
                                        pass
                            # adding poster
                            if poster:
                                if len(poster) > 4:
                                    # check for JPEG/PNG header otherwise it should be a filename
                                    header = struct.unpack_from('4s', poster)[0]
                                    if header == '\xff\xd8\xff\xe0' or \
                                       header == '\x89\x50\x4e\x47':
                                        # make a temporary file
                                        try:
                                            posterfilefd, posterfilename = mkstemp('.img')
                                            try:
                                                os.write(posterfilefd, poster)
                                            finally:
                                                os.close(posterfilefd)
                                            edit.update_image(self.parent, number, posterfilename)
                                        finally:
                                            if os.path.isfile(posterfilename):
                                                os.remove(posterfilename)
                                    else:
                                        edit.update_image(self.parent, number, poster)
                        except Exception:
                            log.exception("movie details are not unique, skipping")
                        numbers.add(number)
                else:
                    log.info('skipping movie without title and original title')
        finally:
            log.info("Import process took %s s; %s/%s movies imported", (time.time() - begin), processed, count)
            if gc_was_enabled:
                gc.enable()
            self.widgets['pwindow'].hide()
        return True

    def clear(self):
        """clear plugin before next source file"""
        self.data = None
        self.imported = 0
        self.__source_name = None
        self._continue = True
        if self.previous_dir:
            os.chdir(self.previous_dir)

    def destroy(self):
        """close all resources"""
        pass

    def _loadmappings(self):
        # add all lookup mapping lists to a list which maps by foreign key column name
        self.foreignkeymaps = {}
        self.foreignkeymaps['medium_id'] = self._loadmappingmedium()
        self.foreignkeymaps['vcodec_id'] = self._loadmappingvcodecs()
        self.foreignkeymaps['collection_id'] = self._loadmappingcollections()
        self.foreignkeymaps['volume_id'] = self._loadmappingvolumes()
        # tags are no foreign key lookup data; it's an intersection
        self.tagmap = {}
        for tag in self.db.session.query(db.Tag.tag_id, db.Tag.name).all():
            tagname = self.normalizename(tag.name)
            if not tagname in self.tagmap:
                self.tagmap[tagname] = tag.tag_id

    def _loadmappingmedium(self):
        mediummap = {}
        for medium in self.db.session.query(db.Medium.medium_id, db.Medium.name).all():
            mediumname = self.normalizename(medium.name)
            if not mediumname in mediummap:
                mediummap[mediumname] = medium.medium_id
        return mediummap

    def _loadmappingvcodecs(self):
        vcodecsmap = {}
        for vcodec in self.db.session.query(db.VCodec.vcodec_id, db.VCodec.name).all():
            vcodecname = self.normalizename(vcodec.name)
            if not vcodecname in vcodecsmap:
                vcodecsmap[vcodecname] = vcodec.vcodec_id
        return vcodecsmap

    def _loadmappingcollections(self):
        collectionsmap = {}
        for collection in self.db.session.query(db.Collection.collection_id, db.Collection.name).all():
            collectionname = self.normalizename(collection.name)
            if not collectionname in collectionsmap:
                collectionsmap[collectionname] = collection.collection_id
        return collectionsmap

    def _loadmappingvolumes(self):
        volumesmap = {}
        for volume in self.db.session.query(db.Volume.volume_id, db.Volume.name).all():
            volumename = self.normalizename(volume.name)
            if not volumename in volumesmap:
                volumesmap[volumename] = volume.volume_id
        return volumesmap

    def _addmappingvalue(self, fkcolumnname, newname):
        id = None
        log.debug("Adding <%s> for <%s>", newname, fkcolumnname)
        if fkcolumnname == 'medium_id':
            id = add.add_medium(self.parent, newname)
            self.foreignkeymaps['medium_id'] = self._loadmappingmedium()
        elif fkcolumnname == 'vcodec_id':
            id = add.add_vcodec(self.parent, newname)
            self.foreignkeymaps['vcodec_id'] = self._loadmappingvcodecs()
        elif fkcolumnname == 'collection_id':
            id = add.add_collection(self.parent, newname)
            self.foreignkeymaps['collection_id'] = self._loadmappingcollections()
        elif fkcolumnname == 'volume_id':
            id = add.add_volume(self.parent, newname)
            self.foreignkeymaps['volume_id'] = self._loadmappingvolumes()
        return id

    def normalizename(self, name):
        name = name.replace('-', '')
        name = name.replace('_', '')
        name = name.replace(' ', '')
        name = name.replace(u'\xa0', '') # unicode whitespace from XML data (&x160;)
        return name.lower().strip()


def on_import_plugin_changed(combobox, widgets, *args):
    from gtk import FileFilter
    import plugins.imp
    plugin_name = widgets['plugin'].get_active_text()
    __import__("plugins.imp.%s" % plugin_name)
    ip = eval("plugins.imp.%s.ImportPlugin" % plugin_name)
    widgets['author'].set_markup("<i>%s</i>" % ip.author)
    widgets['email'].set_markup("<i>%s</i>" % ip.email)
    widgets['version'].set_markup("<i>%s</i>" % ip.version)
    widgets['description'].set_markup("<i>%s</i>" % ip.description)
    # file filters
    for i in widgets['fcw'].list_filters():
        widgets['fcw'].remove_filter(i)
    f = FileFilter()
    f.set_name(plugin_name)
    if ip.file_filters is not None:
        if isinstance(ip.file_filters, tuple) or isinstance(ip.file_filters, list):
            for i in ip.file_filters:
                f.add_pattern(i)
        else:
            f.add_pattern(ip.file_filters)
    if ip.mime_types is not None:
        if isinstance(ip.mime_types, tuple) or isinstance(ip.mime_types, list):
            for i in ip.mime_types:
                f.add_mime_type(i)
        else:
            f.add_mime_type(ip.mime_types)
    widgets['fcw'].add_filter(f)
    f = FileFilter()
    f.set_name(_("All files"))
    f.add_pattern("*")
    widgets['fcw'].add_filter(f)


def on_import_button_clicked(button, self, *args):
    import plugins.imp
    import gutils
    plugin_name = self.widgets['import']['plugin'].get_active_text()
    filenames = self.widgets['import']['fcw'].get_filenames()

    fields = []
    w = self.widgets['import']['fields']
    for i in w:
        if w[i].get_active():
            fields.append(i)

    __import__("plugins.imp.%s" % plugin_name)
    if self.debug_mode:
        log.debug('reloading %s', plugin_name)
        import sys
        reload(sys.modules["plugins.imp.%s" % plugin_name])
    ip = eval("plugins.imp.%s.ImportPlugin(self, fields)" % plugin_name)
    if ip.initialize():
        self.widgets['window'].set_sensitive(False)
        try:
            self.widgets['import']['window'].hide()
            self.widgets['import']['pabort'].connect('clicked', ip.abort, ip)
            for filename in filenames:
                self.widgets['import']['progressbar'].set_fraction(0)
                self.widgets['import']['progressbar'].set_text('')
                if ip.run(filename):
                    gutils.info(_("%s file has been imported. %s movies added.") \
                        % (plugin_name, ip.imported), self.widgets['window'])
                    self.populate_treeview()
                ip.clear()
        except Exception, e:
            log.exception('')
            gutils.error(self, str(e), self.widgets['window'])
        finally:
            ip.destroy()
            self.widgets['import']['pwindow'].hide()
            self.widgets['window'].set_sensitive(True)


def on_abort_button_clicked(button, self, *args):
    self.widgets['import']['window'].hide()
    self.widgets['import']['pwindow'].hide()
    self.widgets['window'].set_sensitive(True)
