# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

###########################################################################
#    Copyright (C) 2006-2007 by Jessica Katharina Parth                         
#    <Jessica.K.P@women-at-work.org>                                       
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

from plugins.imp import ImportPlugin as IP
import gtk
import gtk.glade
import os
import pygtk
import sys
import gutils
import string


def digits_only(s):
    import string, re
    _match = re.compile(r"\d+")
    try:
        s = reduce( string.join, _match.findall(s) )
    except:
        s = '0'
    return s
    
def letters_only(s):
    import string, re
    _match = re.compile(r"\D+")
    try:
        s = reduce( unicode.join, _match.findall(s) )
    except:
        s = unicode(s)
    return s
    
class ImportPlugin(IP):
    description    = _("Full CSV list import plugin")
    author        = "Jessica Katharina Parth"
    email        = "Jessica.K.P@women-at-work.org"
    version        = "0.3"
    file_filters    = '*.[cC][sS][vV]'
    mime_types    = ('text/comma-separated-values', 'text/csv', 'application/csv')

    def initialize(self):
        if not IP.initialize(self):
            return False
        # glade
        gf = os.path.join(self.locations['glade'], 'importcsv.glade')
        # try to open the glade file
        try:
            self.gtk = gtk.glade.XML(gf)
        except:
            log.info("Glade-file %s can not be loaded.", gf)
            return False
        # open gtk window
        self.gtk.get_widget('d_import').set_transient_for( self.widgets['window'] )
        
        # simple string lists
        self.tv_csv = self.gtk.get_widget('tv_csv')
        self.tv_assigned = self.gtk.get_widget('tv_assigned')
        self.tv_griffith = self.gtk.get_widget('tv_griffith')
        
        # 1st list
        self.ls_csv = gtk.ListStore(str)
        self.tv_csv.set_model(self.ls_csv)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("none", renderer, text=0)
        self.tv_csv.append_column(column)
        
        # 2nd list 
        self.ls_griffith = gtk.ListStore(str,str)
        self.tv_griffith.set_model(self.ls_griffith)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("none", renderer, text=0)
        column.set_visible(False)
        self.tv_griffith.append_column(column)
        column = gtk.TreeViewColumn("none", renderer, text=1)
        self.tv_griffith.append_column(column)
        self.set_griffith_fields()
        
        # 3rd list
        self.ls_assigned = gtk.ListStore(str,str,str)
        self.tv_assigned.set_model(self.ls_assigned)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("none", renderer, text=0)
        self.tv_assigned.append_column(column)
        # add the columns for internal information handling and hide them
        column = gtk.TreeViewColumn("none", renderer, text=1)
        column.set_visible(False)
        self.tv_assigned.append_column(column)
        column = gtk.TreeViewColumn("none", renderer, text=2)
        column.set_visible(False)
        self.tv_assigned.append_column(column)
    
        # hide tabs
        self.nb_pages = self.gtk.get_widget('nb_pages')
        self.nb_pages.get_nth_page(1).hide()
        self.nb_pages.connect("switch-page", self._on_page_changed)
        
        # Events
        # Buttons
        self.b_cancel = self.gtk.get_widget("b_cancel")
        self.b_cancel.connect("clicked", self._clicked)
        
        self.b_next = self.gtk.get_widget("b_next")
        self.b_next.connect("clicked", self._clicked)
        
        self.b_back = self.gtk.get_widget("b_back")
        self.b_back.connect("clicked", self._clicked)
        
        self.b_add = self.gtk.get_widget("b_add")
        self.b_add.connect("clicked", self._clicked)
        
        self.b_del = self.gtk.get_widget("b_del")
        self.b_del.connect("clicked", self._clicked)
        
        # Treeviews
        self.tv_griffith.connect("row_activated", self._on_row_activated)
        self.tv_griffith.connect("cursor_changed", self._on_cursor_changed)
        self.tv_csv.connect("row_activated", self._on_row_activated)
        self.tv_csv.connect("cursor_changed", self._on_cursor_changed)
        self.tv_assigned.connect("cursor_changed", self._on_cursor_changed)
        
        self.gtk.get_widget('e_lineterminator').set_active(0)
        
        self.selected_griffith = None
        self.selected_csv = None
        self.current_csv_row = 0
        self.csv_header = None
        return True
    
    def set_griffith_fields(self):
        # 2nd list
        sorted_list = ( "number", "title", "o_title", "director", "year", "country",
                "cast", "studio", "plot", "runtime", "genre", "classification",
                "site", "o_site", "trailer", "image", "seen", "loaned", "notes",
                "rating", "movie_id", "collection_id", "volume_id", "medium_id",
                "vcodec_id", "color", "cond", "layers", "region", "media_num" )
        # sort the list and add field and translated field-name
        for sorted in sorted_list:
            for name in self.fields_to_import:
                if sorted == name:
                    iterator = self.ls_griffith.append()
                    self.ls_griffith.set_value(iterator, 0, name)
                    self.ls_griffith.set_value(iterator, 1, self.fields[name])

    def create_import_table(self):
        self.import_table = {}
        item = self.ls_assigned.get_iter_first()
        while item is not None:
            self.import_table[self.ls_assigned.get_value(item,1)] = self.ls_assigned.get_value(item,2)
            item = self.ls_assigned.iter_next(item)
            
    def _on_page_changed(self, notebook, page, page_num):
        if page_num == 0:
            self.b_back.set_sensitive(False)
        if page_num == 1:
            self.b_back.set_sensitive(True)
            self.open_source()
            
        
    def _clicked(self, widget, event=None, data=None):
        if widget == self.b_cancel:
            self.gtk.get_widget('d_import').hide()
            self.gtk.get_widget('d_import').response(gtk.RESPONSE_CANCEL)
            
        if widget == self.b_back:
            if self.nb_pages.get_current_page() == 1:
                self.nb_pages.prev_page()

        if widget == self.b_next:
            if self.nb_pages.get_current_page() == 0:
                self.nb_pages.get_nth_page(1).show()
                self.nb_pages.next_page()
            else:
                if self.nb_pages.get_current_page() == 1:
                    # test if at least one field is assigned
                    if self.ls_assigned.get_iter_first() is not None:
                        # prepare tabelle for import
                        self.create_import_table()
                            
                        # hide everything
                        self.gtk.get_widget('d_import').hide()
                        self.gtk.get_widget('d_import').response(gtk.RESPONSE_OK)
                    else:
                        gutils.info(_("Please assign at least one field first!"), self.gtk.get_widget('d_import') )
                        
        if widget == self.b_add:
            iterator = self.ls_assigned.append()
            self.ls_assigned.set_value(iterator, 0, "%s > %s" % (self.selected_csv, self.fields[self.selected_griffith]) )
            # add information for the import tabelle
            self.ls_assigned.set_value(iterator, 1, self.selected_griffith )
            self.ls_assigned.set_value(iterator, 2, str(self.csv_header.index(self.selected_csv)) )
            self.ls_griffith.remove(self.iter_griffith)
            self.selected_griffith = None
            
            self.b_add.set_sensitive(False)
        
        if widget == self.b_del:
            # re-add field to griffith
            field_name = self.ls_assigned.get_value(self.iter_assigned,1)

            iterator = self.ls_griffith.append()
            self.ls_griffith.set_value(iterator, 0, field_name)
            self.ls_griffith.set_value(iterator, 1, self.fields[field_name])
            
            # remove assigned row
            self.ls_assigned.remove(self.iter_assigned)
            
            self.b_del.set_sensitive(False)
            
                    
    def _on_row_activated(self, treeview, path, view_column, data = None):
        # get selected rows from both treeviews/lists
        if treeview == self.tv_griffith:
            self.iter_griffith = self.ls_griffith.get_iter(path)
        
            if self.iter_griffith:
                self.selected_griffith = self.ls_griffith.get_value(self.iter_griffith,0)
        
        if treeview == self.tv_csv:
            iter = self.ls_csv.get_iter(path)
        
            if iter:
                self.selected_csv = self.ls_csv.get_value(iter,0)
                
        # enable add button if both lists have a selected item
        if self.selected_griffith is not None and self.selected_csv is not None:
            self.b_add.set_sensitive(True)
        else:
            self.b_add.set_sensitive(False)
        
    def _on_cursor_changed(self, widget, data1 = None, data2 = None):
        # get selected rows from both treeviews/lists
        selection = widget.get_selection()
        (model,iter) = selection.get_selected()
            
        if widget == self.tv_griffith:
            self.iter_griffith = iter
            if self.iter_griffith:
                self.selected_griffith = str(model.get_value(self.iter_griffith, 0))
            else:
                self.selected_griffith = None
        
        if widget == self.tv_csv:
            if iter:
                self.selected_csv = str(model.get_value(iter, 0))
            else:
                self.selected_csv = None
                
        if widget == self.tv_assigned:
            self.iter_assigned = iter
            if self.iter_assigned:
                self.b_del.set_sensitive(True)
            else:
                self.b_del.set_sensitive(False)
                
        # enable add button if both lists have a selected item
        if self.selected_griffith is not None and self.selected_csv is not None:
            self.b_add.set_sensitive(True)
        else:
            self.b_add.set_sensitive(False)
            
    def open_source(self):
        import csv, codecs, os
        # get user values for converting/opening the csv-file
        self.start_row = int(digits_only( self.gtk.get_widget('e_startrow').get_text() ))
        encoding = self.gtk.get_widget('e_encoding').get_active_text()
        encoding = encoding[:string.find( encoding, ' ' )]
        delimiter = self.gtk.get_widget('e_delimiter').get_text()
        if delimiter == '':
            delimiter = ","
        # quotechar
        quotechar =  self.gtk.get_widget('e_quotechar').get_text()
        if quotechar == '':
            quotechar == '"'
        # lineterminator
        active = self.gtk.get_widget('e_lineterminator').get_active()
        # default for none selected and the same for linux and macintosh
        lineterminator = '\r'
        # windows lineterminator
        if active == 1:
            lineterminator = '\r\n'
        
        # open file
        try:
            self.data = csv.reader(codecs.open(self.__source_name, 'r', encoding), dialect='excel', quotechar=quotechar, delimiter=delimiter, lineterminator = lineterminator)

            # get the first line in csv file for the field names
            self.csv_header = self.data.next()
            
            # if the user wants to import line 0 then we have to open it again 
            if self.start_row == 0:
                self.data = csv.reader(codecs.open(self.__source_name, 'r', encoding), dialect='excel', quotechar=quotechar, delimiter=delimiter, lineterminator = lineterminator)
            
        
            # fill the found csv-headers in the simple string list
            self.ls_csv.clear()
            for name in self.csv_header:
                iterator = self.ls_csv.append()
                self.ls_csv.set_value(iterator, 0, name)
            return True
        except:
            gutils.info(_("Can't open the file %s") % self.__source_name, self.gtk.get_widget('d_import') )
            return False
            

    def set_source(self, name):
        import os
        # source _dependent_ initialization goes here
        if name is None or not os.path.isfile(name):
            return False
        self.__source_name = name
        # auto-detect file-encoding (optional)
        try:
            from chardet.universaldetector import UniversalDetector
            detector = UniversalDetector()
            detector.reset()
            lines = 0
            for line in file(self.__source_name, 'rb'):
                detector.feed(line)
                lines += 1
                if detector.done or lines == 50:
                    break
            detector.close()
            encoding = detector.result['encoding'].replace('-', '')
        except:
            encoding = 'utf_8'
        # remove - and _ for better detection
        encoding = encoding.replace('_', '')
        
        model    = self.gtk.get_widget('e_encoding').get_model()
        itempos    = 0
        for item in model:
            pos1 = string.find( string.replace( string.lower(str(item[0])), '_', '' ) , encoding )
            if pos1 == 0:
                break
            itempos += 1
        self.gtk.get_widget('e_encoding').set_active(itempos)
        
        # run dialog
        response = self.gtk.get_widget('d_import').run()
        if response == gtk.RESPONSE_OK:
            return True
        else:
            return False

    def count_movies(self):
        i = 0
        try:
            import csv
            data = csv.reader(open(self.__source_name))
            while data.next():
                i += 1
        except:
            return i
    
    def get_movie_details(self):
        try:
            item = self.data.next()
        except:
            return None
        if item is None:
            return None
        import copy
        # start with the right line
        self.current_csv_row += 1
        if self.current_csv_row < self.start_row:
            return None
        
        # assign the keys
        t_movies = copy.deepcopy(self.import_table)

        # values are overwritten here with the imports
        for field in self.import_table:
            try:
                # some minor fixes to the import so it fits the griffith variable types
                if field == 'year' or field == 'runtime' or field == 'media_num' or field == 'number'  or field == 'volume_id':
                    t_movies[field] = int( digits_only( item[ int(self.import_table[field]) ] ) )
                elif field == 'seen' or field == 'loaned':
                    t_movies[field] = bool( item[ int(self.import_table[field]) ] )
                elif field == 'country':
                    t_movies[field] = letters_only( item[ int(self.import_table[field]) ] )
                elif field == 'cast':
                    try:
                        if item[int(self.import_table[field])].index(", ") != -1:
                            t_movies[field] = item[ int(self.import_table[field]) ].replace(', ', "\n")
                    except:
                        t_movies[field] = item[ int(self.import_table[field]) ].replace(',', "\n")
                    t_movies[field] = unicode(t_movies[field])
                else:
                    # 1:1 import
                    t_movies[field] = unicode(item[ int(self.import_table[field])])
            except:
                # error field can't be imported
                log.debug("field %s cannot be imported (%s)", field, e)
                t_movies.pop(field)
        
        return t_movies

    def clear(self):
        IP.clear(self)
        self.nb_pages.get_nth_page(1).hide()
        self.csv_header = None
        self.ls_assigned.clear()
        self.ls_griffith.clear()
        # add default griffith fields again
        self.set_griffith_fields()

    def destroy(self):
        self.gtk.get_widget('d_import').destroy()
