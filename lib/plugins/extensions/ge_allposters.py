# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright © 2010 Michael Jahn
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

import os
import re
import logging
from urllib import quote, urlcleanup
import gtk
import gutils
from edit import update_image_from_memory
from webaccess import WebAccess
from plugins.extensions import GriffithExtensionBase as Base

log = logging.getLogger('Griffith')


class PosterResultsViewer():

    def showresultlist(self, previewposterurls, parent_window):
        """ returns the selected index in previewposterurls or None if cancel is pressed """
        if not previewposterurls or not len(previewposterurls):
            return None

        self._previewposterurls = previewposterurls
        self._currentposition = 0
        self._selectedindex = None
        self._parent_window = parent_window
        self._thumbnailcache = []
        self.webaccess = WebAccess()
        # glade
        try:
            self.gtk = gtk.glade.xml_new_from_buffer(self._gladexml, len(self._gladexml))
        except:
            log.exception("Glade data can not be loaded.")
            return False
        # open gtk window
        self.gtk.get_widget('PosterResultList').set_transient_for(parent_window)
        # Events
        # Buttons
        self.gtk.get_widget("buttoncancel").connect("clicked", self._clicked_cancel)
        if len(previewposterurls) > 0:
            self.gtk.get_widget("buttonimage1").connect("clicked", self._clicked_buttonimage1)
        if len(previewposterurls) > 1:
            self.gtk.get_widget("buttonimage2").connect("clicked", self._clicked_buttonimage2)
        if len(previewposterurls) > 2:
            self.gtk.get_widget("buttonimage3").connect("clicked", self._clicked_buttonimage3)
        if len(previewposterurls) > 3:
            self.gtk.get_widget("buttonleft").connect("clicked", self._clicked_left)
            self.gtk.get_widget("buttonright").connect("clicked", self._clicked_right)
            self.gtk.get_widget("buttonfirst").connect("clicked", self._clicked_first)
            self.gtk.get_widget("buttonlast").connect("clicked", self._clicked_last)
        else:
            self.gtk.get_widget("buttonleft").set_sensitive(False)
            self.gtk.get_widget("buttonright").set_sensitive(False)
            self.gtk.get_widget("buttonfirst").set_sensitive(False)
            self.gtk.get_widget("buttonlast").set_sensitive(False)
        # fill the first 3 images
        self._refreshimagebuttons()
        self._refreshlabelposition()
        # run dialog
        response = self.gtk.get_widget('PosterResultList').run()
        return self._selectedindex

    def _clicked_buttonimage1(self, widget):
        self._selectedindex = self._currentposition
        self.gtk.get_widget('PosterResultList').hide()
        self.gtk.get_widget('PosterResultList').response(gtk.RESPONSE_OK)

    def _clicked_buttonimage2(self, widget):
        self._selectedindex = self._currentposition + 1
        self.gtk.get_widget('PosterResultList').hide()
        self.gtk.get_widget('PosterResultList').response(gtk.RESPONSE_OK)

    def _clicked_buttonimage3(self, widget):
        self._selectedindex = self._currentposition + 2
        self.gtk.get_widget('PosterResultList').hide()
        self.gtk.get_widget('PosterResultList').response(gtk.RESPONSE_OK)

    def _clicked_cancel(self, widget):
        self.gtk.get_widget('PosterResultList').hide()
        self.gtk.get_widget('PosterResultList').response(gtk.RESPONSE_CANCEL)

    def _clicked_left(self, widget):
        if self._currentposition > 0:
            self._currentposition = self._currentposition - 1
            self._refreshimagebuttons()
            self._refreshlabelposition()

    def _clicked_right(self, widget):
        if self._currentposition < len(self._previewposterurls) - 3:
            self._currentposition = self._currentposition + 1
            self._refreshimagebuttons()
            self._refreshlabelposition()

    def _clicked_first(self, widget):
        # get them all from the cache, because if that handler is called there are more then 3 posters
        self._currentposition = 0
        self._refreshimagebuttons()
        self._refreshlabelposition()

    def _clicked_last(self, widget):
        self._currentposition = len(self._previewposterurls) - 3
        self._refreshimagebuttons()
        self._refreshlabelposition()

    def _refreshimagebuttons(self):
        self._ensurethumbnailcache()
        handler = self.gtk.get_widget('image1').set_from_pixbuf(self._thumbnailcache[self._currentposition])
        handler = self.gtk.get_widget('image2').set_from_pixbuf(self._thumbnailcache[self._currentposition + 1])
        handler = self.gtk.get_widget('image3').set_from_pixbuf(self._thumbnailcache[self._currentposition + 2])

    def _refreshlabelposition(self):
        max = len(self._previewposterurls)
        end = self._currentposition + 3
        while end > max:
            end = end - 1
        self.gtk.get_widget('labelposition').set_text("%s - %s / %s" % (self._currentposition + 1, end, max))

    def _ensurethumbnailcache(self):
        while len(self._thumbnailcache) < self._currentposition + 3:
            self._thumbnailcache.append(None)
        self.webaccess.prepare(self.gtk.get_widget('PosterResultList'), _('Searching'), _('Wait a moment'))
        try:
            if len(self._previewposterurls) > self._currentposition and not self._thumbnailcache[self._currentposition]:
                image = self.webaccess.fetch(self._previewposterurls[self._currentposition], encoding=None)
                self._thumbnailcache[self._currentposition] = self._loadimagetopixbuf(image)
            if len(self._previewposterurls) > self._currentposition + 1 and not self._thumbnailcache[self._currentposition + 1]:
                image = self.webaccess.fetch(self._previewposterurls[self._currentposition + 1], encoding=None)
                self._thumbnailcache[self._currentposition + 1] = self._loadimagetopixbuf(image)
            if len(self._previewposterurls) > self._currentposition + 2 and not self._thumbnailcache[self._currentposition + 2]:
                image = self.webaccess.fetch(self._previewposterurls[self._currentposition + 2], encoding=None)
                self._thumbnailcache[self._currentposition + 2] = self._loadimagetopixbuf(image)
        except:
            log.exception('')
        finally:
            self.webaccess.unprepare()

    def _loadimagetopixbuf(self, data):
        loader = gtk.gdk.PixbufLoader()
        loader.write(data, len(data))
        loader.close()
        return loader.get_pixbuf()

    # inline glade file
    _gladexml = """<?xml version="1.0"?>
<glade-interface>
  <!-- interface-requires gtk+ 2.12 -->
  <!-- interface-naming-policy project-wide -->
  <widget class="GtkDialog" id="PosterResultList">
    <property name="border_width">5</property>
    <property name="title" translatable="yes">Found Results</property>
    <property name="default_width">320</property>
    <property name="default_height">240</property>
    <property name="type_hint">normal</property>
    <property name="has_separator">False</property>
    <child internal-child="vbox">
      <widget class="GtkVBox" id="dialog-vbox1">
        <property name="visible">True</property>
        <property name="orientation">vertical</property>
        <child>
          <widget class="GtkHBox" id="hboximages">
            <property name="visible">True</property>
            <child>
              <widget class="GtkButton" id="buttonimage1">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <child>
                  <widget class="GtkImage" id="image1">
                    <property name="visible">True</property>
                    <property name="stock">gtk-missing-image</property>
                  </widget>
                </child>
              </widget>
              <packing>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <widget class="GtkButton" id="buttonimage2">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <child>
                  <widget class="GtkImage" id="image2">
                    <property name="visible">True</property>
                    <property name="stock">gtk-missing-image</property>
                  </widget>
                </child>
              </widget>
              <packing>
                <property name="position">1</property>
              </packing>
            </child>
            <child>
              <widget class="GtkButton" id="buttonimage3">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <child>
                  <widget class="GtkImage" id="image3">
                    <property name="visible">True</property>
                    <property name="stock">gtk-missing-image</property>
                  </widget>
                </child>
              </widget>
              <packing>
                <property name="position">2</property>
              </packing>
            </child>
          </widget>
          <packing>
            <property name="position">1</property>
          </packing>
        </child>
        <child>
          <widget class="GtkHBox" id="hboxbuttons">
            <property name="visible">True</property>
            <child>
              <widget class="GtkLabel" id="labelposition">
                <property name="visible">True</property>
                <property name="label" translatable="yes">1 - 3 / 3</property>
              </widget>
              <packing>
                <property name="expand">False</property>
                <property name="fill">False</property>
                <property name="padding">10</property>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <widget class="GtkHButtonBox" id="dialog-action_area1">
                <property name="visible">True</property>
                <property name="layout_style">end</property>
                <child>
                  <widget class="GtkButton" id="buttonfirst">
                    <property name="label" translatable="yes">|&lt;</property>
                    <property name="visible">True</property>
                    <property name="can_focus">True</property>
                    <property name="receives_default">True</property>
                  </widget>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">False</property>
                    <property name="position">0</property>
                  </packing>
                </child>
                <child>
                  <widget class="GtkButton" id="buttonleft">
                    <property name="label" translatable="yes">&lt;</property>
                    <property name="visible">True</property>
                    <property name="can_focus">True</property>
                    <property name="receives_default">True</property>
                  </widget>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">False</property>
                    <property name="position">1</property>
                  </packing>
                </child>
                <child>
                  <widget class="GtkButton" id="buttonright">
                    <property name="label" translatable="yes">&gt;</property>
                    <property name="visible">True</property>
                    <property name="can_focus">True</property>
                    <property name="receives_default">True</property>
                  </widget>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">False</property>
                    <property name="position">2</property>
                  </packing>
                </child>
                <child>
                  <widget class="GtkButton" id="buttonlast">
                    <property name="label" translatable="yes">&gt;|</property>
                    <property name="visible">True</property>
                    <property name="can_focus">True</property>
                    <property name="receives_default">True</property>
                  </widget>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">False</property>
                    <property name="position">3</property>
                  </packing>
                </child>
                <child>
                  <widget class="GtkButton" id="buttoncancel">
                    <property name="label" translatable="yes">Cancel</property>
                    <property name="visible">True</property>
                    <property name="can_focus">True</property>
                    <property name="receives_default">True</property>
                  </widget>
                  <packing>
                    <property name="expand">False</property>
                    <property name="fill">False</property>
                    <property name="position">4</property>
                  </packing>
                </child>
              </widget>
              <packing>
                <property name="expand">False</property>
                <property name="pack_type">end</property>
                <property name="position">1</property>
              </packing>
            </child>
          </widget>
          <packing>
            <property name="expand">False</property>
            <property name="pack_type">end</property>
            <property name="position">2</property>
          </packing>
        </child>
        <child internal-child="action_area">
          <widget class="GtkHButtonBox" id="dialog-action_area2"/>
          <packing>
            <property name="expand">False</property>
            <property name="pack_type">end</property>
            <property name="position">0</property>
          </packing>
        </child>
      </widget>
    </child>
  </widget>
</glade-interface>"""


class GriffithExtension(Base):
    name = 'AllPosters'
    description = _('Fetch posters from AllPosters.com')
    author = 'Michael Jahn'
    email = 'mike@griffith.cc'
    version = 1
    api = 1
    enabled = True

    toolbar_icon = 'gtk-network'

    baseurl = 'http://www.allposters.com'
    baseurltitle = 'http://www.allposters.com/gallery.asp?startat=/GetThumb.asp&CategoryID=101&imagefield2.x=0&imagefield2.y=0&psize=48&ItemType=1&FilterType1=1&search=%s'
    alternateurltitle = 'http://www.allposters.com/gallery.asp?startat=/GetThumb.asp&imagefield2.x=0&imagefield2.y=0&psize=48&ItemType=1&FilterType1=1&search=%s'
    RESULTFILTER = re.compile('([<]a[ ]+[^>]+[>])[^<]*([<]img[ ]+class="thmbd"[^>]+[>])', re.DOTALL | re.M)

    webaccess = WebAccess()
    firstfetch = True

    def toolbar_icon_clicked(self, widget, movie):
        log.info('fetching poster from AllPosters.com ...')
        self.movie = movie

        # correction of the movie name for the search
        o_title = None
        title = None
        if movie.o_title:
            if movie.o_title.endswith(', The'):
                o_title = u"The %s" % movie.o_title[:-5]
            else:
                o_title = movie.o_title
        if movie.title:
            if movie.title.endswith(', The'):
                title = u"The %s" % movie.title[:-5]
            else:
                title = movie.title

        # fetch the result list
        self.webaccess.prepare(self.widgets['window'], _('Searching'), _('Wait a moment'))
        try:
            titlestolookfor = []
            if o_title:
                titlestolookfor.append(o_title)
            if title and not title == o_title:
                titlestolookfor.append(title)
            (previewposterurls, posterpageurls) = self._fetchfirstresultlists(self.baseurltitle, titlestolookfor)
            if not previewposterurls or not len(previewposterurls):
                (previewposterurls, posterpageurls) = self._fetchfirstresultlists(self.alternateurltitle, titlestolookfor)
        except:
            log.exception('')
            gutils.warning(_('No posters found for this movie.'))
            return
        finally:
            self.webaccess.unprepare()

        if not previewposterurls or not len(previewposterurls):
            gutils.warning(_('No posters found for this movie.'))
            return

        viewer = PosterResultsViewer()
        selectedindex = viewer.showresultlist(previewposterurls, self.widgets['window'])
        if selectedindex:
            poster = self._fetchposter(posterpageurls[selectedindex])
            if poster:
                update_image_from_memory(self.app, movie.number, poster)

    def _fetchfirstresultlists(self, baseurl, titlestolookfor):
        if self.firstfetch:
            # throw away the first attempt because it is needed for http session
            # initialization of allposter.com. There is a redirection to the start
            # page for the first query
            url = self.baseurltitle % quote('Rocky') # dosn't matter
            data = self.webaccess.fetch(url, autodetectencoding=True)
            self.firstfetch = False

        data = False
        previewposterurls = None
        posterpageurls = None
        # go through all search string, find the first one which gives results
        for titletolookfor in titlestolookfor:
            if titletolookfor:
                url = baseurl % quote(titletolookfor)
                data = self.webaccess.fetch(url, autodetectencoding=True)
                if data:
                    (previewposterurls, posterpageurls) = self._filterresultlists(data)
            if not previewposterurls or not len(previewposterurls):
                # nothing found, perhaps it is a direct result page
                directresult = self._filterposter(data)
                if directresult:
                    previewposterurls = [directresult]
                    posterpageurls = [url]
            if previewposterurls and len(previewposterurls):
                break

        return (previewposterurls, posterpageurls)

    def _filterresultlists(self, data):
        previewposterurls = []
        posterpageurls = []
        posters = self.RESULTFILTER.findall(data)
        if posters:
            for poster in posters:
                posterpageurl = gutils.trim(poster[0], 'href="', '"')
                posterurl = gutils.trim(poster[1], 'src="', '"')
                if posterurl and not posterurl.startswith('http://'):
                    posterurl = self.baseurl + posterurl
                previewposterurls.append(posterurl)
                if posterpageurl and not posterpageurl.startswith('http://'):
                    posterpageurl = self.baseurl + posterpageurl
                posterpageurls.append(posterpageurl)
        return (previewposterurls, posterpageurls)

    def _fetchposter(self, posterpageurl):
        data = self.webaccess.fetch(posterpageurl, 'iso8859-1')
        if data:
            tmp = self._filterposter(data)
            data = self.webaccess.fetch(tmp, encoding=None)
        return data

    def _filterposter(self, data):
        tmp = gutils.trim(data, '<div class="imageBorder">', '</div>')
        tmp = gutils.trim(tmp, 'src="', '"')
        return tmp