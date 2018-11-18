# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2010
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

import logging
import string
import threading
import time
import urllib2
import cookielib
import gtk
import gutils

log = logging.getLogger("Griffith")


class WebAccess(object):

    debug_mode = False
    progress = None
    parent_window = None

    def prepare(self, parent_window=None, title=None, message=None, debug=False):
        self.parent_window = parent_window
        self.debug_mode = debug
        if not self.progress:
            self.progress = Progress(parent_window)
        self.progress.set_data(_("Fetching data"), _("Wait a moment"), False)

    def fetch(self, url=None, encoding=None, title=None, message=None, autodetectencoding=False, postdata=None):
        if title or message:
            self.progress.set_data(title, message, True)
        else:
            self.progress.show()
        retriever = Retriever(url, self.parent_window, self.progress, postdata = postdata)
        retriever.start()
        while retriever.isAlive():
            self.progress.pulse()
            #if self.progress.status:
            # waits infinite if retriever thread hangs in urllib
            #    retriever.join()
            while gtk.events_pending():
                gtk.main_iteration()
        data = ''
        if retriever.data:
            data = retriever.data
            # if autodetecting of the encoding is wanted or we are at debug mode
            if self.debug_mode or autodetectencoding:
                import chardet
                chardetresult = chardet.detect(data)
                if chardetresult['encoding']:
                    detectedencoding = string.lower(chardetresult['encoding'])
                    if self.debug_mode and encoding != detectedencoding:
                        log.warn('Detected encoding differs from selected encoding: %s != %s' % (detectedencoding, encoding))
                        log.warn(chardetresult)
                    if autodetectencoding:
                        encoding = detectedencoding
                elif autodetectencoding:
                    log.warn('Can\'t auto-detect encoding, fallback to utf8')
                    encoding = 'utf8'
            try:
                # try to decode it strictly
                if encoding:
                    data = data.decode(encoding)
            except UnicodeDecodeError, e:
                # something is wrong, perhaps a wrong character set
                # or some pages are not as strict as they should be
                # (like OFDb, mixes utf8 with iso8859-1)
                # I want to log the error here so that I can find it
                # but the program should not terminate
                log.warn('Decoding error: %s' % str(e))
                data = data.decode(encoding, 'ignore')
        return data

    def unprepare(self):
        if self.progress:
            self.progress.hide()


# global cookie jar is important because the cookies are only stored in memory
_cookiejar = None

class Retriever(threading.Thread):

    chunksize = 4096

    def __init__(self, URL, parent_window, progress, postdata = None, referer = None):
        global _cookiejar
        self.URL = URL
        self.data = None
        self.parent_window = parent_window
        self.progress = progress
        self.postdata = postdata
        self.referer = referer
        self._stopevent = threading.Event()
        self._sleepperiod = 1.0
        if not _cookiejar:
            _cookiejar = cookielib.LWPCookieJar(policy = cookielib.DefaultCookiePolicy())
        self.cj = _cookiejar
        threading.Thread.__init__(self, name = "Retriever")

    def run(self):
        try:
            self.progress.status = False
            self.data = self.urlretrieve(self.URL, self.postdata, self.referer)
            if self.progress.status:
                self.data = None
        except IOError:
            self.progress.dialog.hide()
            gutils.urllib_error(_("Connection error"), self.parent_window)
            self.join()

    def reportprogress(self, count, blockSize, totalSize):
        if totalSize > 0:
            try:
                downloaded_percentage = min((count * blockSize * 100) / totalSize, 100)
            except:
                downloaded_percentage = 100
            if count != 0:
                downloaded_kbyte = int(count * blockSize / 1024.0)
                filesize_kbyte = int(totalSize / 1024.0)
        return not self.progress.status

    def urlretrieve(self, url, data = None, referer = None):
        headers = self.get_headers()
        if referer:
            headers['Referer'] = referer
        opener = self.create_opener()
        # make the request
        the_page = ''
        try:
            log.debug('Fetching URL: %s' % url)
            if data:
                log.debug('POST data: %s' % data)
            req = urllib2.Request(url, data, headers)
            response = opener.open(req)
        except:
            log.exception('')
            log.error('URL: %s' % url)
        else:
            log.debug('Fetched URL: %s' % response.geturl())
            #log.debug('URL info: %s' % response.info())
            headers = response.info()
            if "content-length" in headers:
                size = int(headers["Content-Length"])
            else:
                size = -1
            read = 0
            blocknum = 0
            while not self.progress.status:
                block = response.read(self.chunksize)
                if block == '':
                    break
                the_page = the_page + block
                read += len(block)
                blocknum += 1
                if not self.reportprogress(blocknum, self.chunksize, size):
                    # breakable data fetching
                    break
            if not self.progress.status:
                the_page = self.try_decompress(the_page)
        return the_page

    def get_headers(self):
        # use Firefox 3.5 User-Agent string from Windows XP
        # additional HTTP headers to work around the html file compression which
        # is used by UMTS connections. compression breaks the movie import plugins sometimes
        return {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Accept-Encoding': 'gzip'
        }

    def create_opener(self):
        return urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))

    def try_decompress(self, data):
        # check for gzip compressed pages
        if data[0:2] == '\037\213':
            return gutils.decompress(data)
        return data


class Progress:

    def __init__(self, window, title='', message=''):
        self.status = False
        self.dialog = gtk.Dialog(title, window, gtk.DIALOG_MODAL, ())
        self.dialog.set_urgency_hint(False)
        self.dialog.set_position(gtk.WIN_POS_CENTER)
        self.dialog.stick()
        self.label = gtk.Label()
        self.label.set_markup(message)
        self.dialog.vbox.pack_start(self.label)
        self.progress = gtk.ProgressBar()
        self.progress.set_pulse_step(0.01)
        self.dialog.vbox.pack_start(self.progress, False, False)
        self.button = gtk.Button(_("Cancel"), gtk.STOCK_CANCEL)
        self.button.connect("clicked", self.callback)
        self.dialog.vbox.pack_start(self.button, False, False)

    def callback(self, widget):
        #self.hide()
        self.label.set_markup(_('Cancelling...'))
        self.status = True

    def pulse(self):
        self.progress.pulse()
        time.sleep(0.01)

    def close(self):
        self.dialog.destroy()

    def hide(self):
        if self.dialog.get_property('visible'):
            self.dialog.hide()

    def show(self):
        if not self.dialog.get_property('visible'):
            self.dialog.show_all()

    def set_data(self, title, message, showit):
        self.dialog.set_title(title)
        self.label.set_markup(message)
        if showit is True:
            self.show()
# vim: fdm=marker
