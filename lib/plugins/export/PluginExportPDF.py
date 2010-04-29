# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2010 Vasco Nunes
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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.rl_config import defaultPageSize
from reportlab.rl_config import defaultEncoding
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, ParagraphAndImage, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.fonts import addMapping
from xml.sax import saxutils
import config
import gtk
import os
import string
import sys
from locale import getdefaultlocale
import db
import gutils
import version
from plugins.export import Base

class ExportPlugin(Base):
    name = "PDF"
    description = _("PDF export plugin")
    author = "Vasco Nunes"
    email = "<vasco.m.nunes@gmail.com>"
    version = "0.6"
    
    fields_to_export = ('number', 'o_title', 'title', 'director', 'genre', 'cast', 'poster_md5')

    def initialize(self):
        self.fontName = ''
        return True

    def run(self):
        """exports a simple movie list to a pdf file"""
        
        basedir = None
        if not self.config is None:
            basedir = self.config.get('export_dir', None, section='export-pdf')
        if basedir is None:
            filename = gutils.file_chooser(_("Export a PDF"), action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name="griffith_simple_list.pdf")
        else:
            filename = gutils.file_chooser(_("Export a PDF"), action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name="griffith_simple_list.pdf",folder=basedir)
        if filename is not False and filename[0]:
            if not self.config is None and filename[1]:
                self.config.set('export_dir', filename[1], section='export-pdf')
                self.config.save()
            overwrite = None
            pdffilename = filename[0].decode('utf-8')
            if os.path.isfile(pdffilename):
                if gutils.question(_("File exists. Do you want to overwrite it?"), self.parent_window):
                    overwrite = True
                else:
                    overwrite = False
                    
            if overwrite == True or overwrite is None:
                # filename encoding
                defaultLang, defaultEnc = getdefaultlocale()
                if defaultEnc is None:
                    defaultEnc = 'UTF-8'
                c = SimpleDocTemplate(pdffilename.encode(defaultEnc), \
                    author = 'Griffith', \
                    title = _('List of films').encode('utf-8'), \
                    subject = _('List of films').encode('utf-8'))
                # data encoding
                #if defaultEncoding == 'WinAnsiEncoding':
                #    defaultEnc = 'cp1252'
                #else:
                defaultEnc = 'utf-8'

                self.create_styles()
                style = self.styles["Normal"]
                Story = [Spacer(1,2*inch)]

                # select sort column - FIXME
                sort_column_name = self.config.get('sortby', 'number', section='mainlist')
                sort_reverse = self.config.get('sortby_reverse', False, section='mainlist')
                do_grouping = True
                for i in sort_column_name.split(','):
                    if i != 'title' and i != 'o_title':
                        do_grouping = False

                # build the query
                query = self.get_query()
                movies = query.execute().fetchall()

                # define some custom stylesheetfont
                total = len(movies)
                p = Paragraph(saxutils.escape((_("List of films")).encode('utf-8')), self.styles["Heading1"] )
                Story.append(p)
                Story.append(Paragraph(" ",style))
                p = Paragraph(saxutils.escape((_("Total Movies: %s") % str(total)).encode('utf-8')), self.styles["Heading3"])
                Story.append(p)
                Story.append(Paragraph(" ",style))
                # output movies
                first_letter = ''
                for movie in movies:
                    number = movie.number
                    if movie.o_title:
                        original_title = movie.o_title.encode(defaultEnc)
                    else:
                        original_title = ''
                    if movie.title:
                        title = movie.title.encode(defaultEnc)
                    else:
                        title = ''
                    grouping_title = movie.title
                    if grouping_title is None:
                        grouping_title = u'None'
                    if movie.director:
                        director = ' - ' + movie.director.encode(defaultEnc)
                    else:
                        director = ""
                    # group by first letter
                    # use movie.title/grouping_title for grouping because of encoding problems !!!
                    if do_grouping and grouping_title[0] != first_letter:
                        if grouping_title[0] in '0123456789':
                            # Group Numbers
                            if first_letter != '0-9':
                                first_letter = '0-9'
                                paragraph_text = saxutils.escape(first_letter)
                                p = Paragraph(paragraph_text.decode(defaultEnc), self.styles['Heading2'])
                                Story.append(p)
                        else:
                            first_letter = grouping_title[0]
                            paragraph_text = saxutils.escape(first_letter)
                            p = Paragraph(paragraph_text.decode(defaultEnc), self.styles['Heading2'])
                            Story.append(p)
                    # add movie title
                    image_filename = None
                    if movie.poster_md5:
                        image_filename = gutils.get_image_fname(movie.poster_md5, self.db, 's')
                    paragraph_text = '<b>'+ saxutils.escape(title) + '</b>' + \
                        saxutils.escape(' (' + original_title + ') | ' + str(number))
                    p = Paragraph(paragraph_text.decode(defaultEnc), self.styles['Heading3'])
                    if image_filename:
                        p = ParagraphAndImage(p, Image(image_filename), side = 'left')
                    Story.append(p)
                    if movie.director:
                        paragraph_text = '<b>' + _('Director') + ': </b>' + saxutils.escape(movie.director.encode(defaultEnc))
                        p = Paragraph(paragraph_text.decode(defaultEnc), self.styles['Normal'])
                        Story.append(p)
                    if movie.genre:
                        paragraph_text = '<b>' + _('Genre') + ': </b>' + saxutils.escape(movie.genre.encode(defaultEnc))
                        p = Paragraph(paragraph_text.decode(defaultEnc), self.styles['Normal'])
                        Story.append(p)
                    if movie.cast:
                        paragraph_text = '<i><b>' + _('Cast') + ': </b>' + saxutils.escape('; '.join(movie.cast.encode(defaultEnc).split("\n")[0:2])) + '</i>'
                        p = Paragraph(paragraph_text.decode(defaultEnc), self.styles['Normal'])
                        Story.append(p)
                c.build(Story, onFirstPage=self.page_template, onLaterPages=self.page_template)
                gutils.info(_('PDF has been created.'), self.parent_window)

    def create_styles(self):
        self.styles = getSampleStyleSheet()

        if self.config.get('font', '') != '':
            self.fontName = 'custom_font'
            fontfilename = self.config.get('font', '')
            (fontfilenamebase, fontfilenameextension) = os.path.splitext(fontfilename)

            pdfmetrics.registerFont(TTFont(self.fontName, fontfilename))
            addMapping(self.fontName, 0, 0, self.fontName)
            # build font family if available to support <b> and <i>
            if os.path.isfile(fontfilenamebase + 'bd' + fontfilenameextension):
                pdfmetrics.registerFont(TTFont(self.fontName + '-bold', fontfilenamebase + 'bd' + fontfilenameextension))
                addMapping(self.fontName, 1, 0, self.fontName + '-bold')
            if os.path.isfile(fontfilenamebase + 'bi' + fontfilenameextension):
                pdfmetrics.registerFont(TTFont(self.fontName + '-bolditalic', fontfilenamebase + 'bi' + fontfilenameextension))
                addMapping(self.fontName, 1, 1, self.fontName + '-bolditalic')
            if os.path.isfile(fontfilenamebase + 'i' + fontfilenameextension):
                pdfmetrics.registerFont(TTFont(self.fontName + '-italic', fontfilenamebase + 'i' + fontfilenameextension))
                addMapping(self.fontName, 0, 1, self.fontName + '-italic')
        else:
            self.fontName = "Helvetica"
            
        if self.config.get('font_size', '') != '':
            self.base_font_size = int(self.config.get('font_size'))
        else:
            self.base_font_size = 18
        title_font_size = self.base_font_size
        heading1_font_size = self.base_font_size - 8
        heading2_font_size = self.base_font_size - 3
        heading3_font_size = self.base_font_size - 11
        normal_font_size = self.base_font_size - 13
        if heading1_font_size < 4:
            heading1_font_size = 4
        if heading2_font_size < 4:
            heading2_font_size = 4
        if heading3_font_size < 4:
            heading3_font_size = 4
        if normal_font_size < 4:
            normal_font_size = 4

        # adjust font
        for (name, style) in self.styles.byName.items():
            style.fontName = self.fontName

        #adjust font sizes
        self.styles['Title'].fontSize = title_font_size
        self.styles['Title'].leading = title_font_size + 2
        self.styles['Normal'].fontSize = normal_font_size
        self.styles['Normal'].leading = normal_font_size + 2
        self.styles['Heading1'].fontSize = heading1_font_size
        self.styles['Heading1'].leading = heading1_font_size + 2
        self.styles['Heading2'].fontSize = heading2_font_size
        self.styles['Heading2'].leading = heading2_font_size + 2
        self.styles['Heading3'].fontSize = heading3_font_size
        self.styles['Heading3'].leading = heading3_font_size + 2

    def page_template(self, canvas, doc):
        canvas.saveState()
        canvas.setFont(self.fontName,7)
        canvas.drawCentredString(defaultPageSize[0]/2, 40,_("Page %d") % doc.page)
        canvas.setFont(self.fontName,5)
        canvas.drawCentredString(defaultPageSize[0]/2, 20, (_("Document generated by Griffith v")+
            version.pversion+" - Copyright (C) "+version.pyear+" "+
            version.pauthor+" - " + _("Released Under the GNU/GPL License")).encode('utf-8'))
        canvas.restoreState()
