# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
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

from gettext import gettext as _
import string
import os
import gtk
import htmlentitydefs
import re
import webbrowser
import gobject

url_re = re.compile('^\w+://')
entity = re.compile(r'\&.\w*?\;')
html_tags = re.compile(r'\<.*?\>')

def remove_accents(txt, encoding='iso-8859-1'):
	d = {192: u'A', 193: u'A', 194: u'A', 195: u'A', 196: u'A', 197: u'A',
			199: u'C', 200: u'E', 201: u'E', 202: u'E', 203: u'E', 204: u'I',
			205: u'I', 206: u'I', 207: u'I', 209: u'N', 210: u'O', 211: u'O',
			212: u'O', 213: u'O', 214: u'O', 216: u'O', 217: u'U', 218: u'U',
			219: u'U', 220: u'U', 221: u'Y', 224: u'a', 225: u'a', 226: u'a',
			227: u'a', 228: u'a', 229: u'a', 231: u'c', 232: u'e', 233: u'e',
			234: u'e', 235: u'e', 236: u'i', 237: u'i', 238: u'i', 239: u'i',
			241: u'n', 242: u'o', 243: u'o', 244: u'o', 245: u'o', 246: u'o',
			248: u'o', 249: u'u', 250: u'u', 251: u'u', 252: u'u', 253: u'y',
			255: u'y'}
	return unicode(txt, encoding).translate(d)

def is_number(x):
	try:
		return(x==x-0)
	except:
		return False

def find_next_available(self):
	"""
	finds next available movie number.
	This is the first empty position.
	If none is empty then increments the last position.
	"""
	a = first = 0
	row = None

	movies = self.db.Movie.select(order_by="number ASC")
	for movie in movies:
		second = int(movie.number)
		if second == None:
			second = 0
		if (second>first+1):
			break
		first = second
		a += a

	if first == None:
		return 1
	else:
		number = first+1
		return number

def trim(text,key1,key2):
	p1 = string.find(text,key1)
	if p1 == -1:
		return ""
	else:
		p1 = p1+len(key1)
	p2 = string.find(text[p1:],key2)
	if p2 == -1:
		return ""
	else:
		p2 = p1+p2
	return text[p1:p2]

def after(text,key):
	return text.split(key, 1)[1]

def before(text,key):
	return text.split(key, 1)[0]

def gescape(text):
	text=string.replace(text,"'", "''")
	text=string.replace(text,"--", "-")
	return text

def progress(blocks,size_block,size):
	transfered = blocks * size_block
	if size > 0 and transfered > size:
		transfered = size
	elif size < 0:
		size = "?"
	print transfered, '/', size, 'bytes'

# functions to handle comboboxentry stuff

def set_model_from_list (cb, items):
	"""Setup a ComboBox or ComboBoxEntry based on a list of strings."""
	model = gtk.ListStore(str)
	for i in items:
		model.append([i])
	cb.set_model(model)
	if type(cb) == gtk.ComboBoxEntry:
		cb.set_text_column(0)
	elif type(cb) == gtk.ComboBox:
		cell = gtk.CellRendererText()
		cb.pack_start(cell, True)
		cb.add_attribute(cell, 'text', 0)

def on_combo_box_entry_changed(widget):
	model = widget.get_model()
	m_iter = widget.get_active_iter()
	if m_iter:
		return model.get_value(m_iter, 0)
	else:
		return 0

def on_combo_box_entry_changed_name(widget):
	return widget.get_active_text()

def convert_entities(text):
	def conv(ents):
		entities = htmlentitydefs.entitydefs
		ents = ents.group(0)
		ent_code = entities.get(ents[1:-1], None)
		if ent_code:
			try:
				ents = unicode(ent_code, 'UTF-8')
			except UnicodeDecodeError:
				ents = unicode(ent_code, 'latin-1')
			except Exception, ex:
				print("error occurred while converting entity %s: %s" % (ents, ex))

			# check if it still needs conversion
			if not entity.search(ents):
				return ents

		if ents[1] == '#':
			code = ents[2:-1]
			base = 10
			if code[0] == 'x':
				code = code[1:]
				base = 16
			return unichr(int(code, base))
		else:
			return

	in_entity = entity.search(text)
	if not in_entity:
		return text
	else:
		ctext = in_entity.re.sub(conv, text)
		return ctext

def strip_tags(text):
	finished = 0
	while not finished:
		finished = 1
		# check if there is an open tag left
		start = text.find("<")
		if start >= 0:
			# if there is, check if the tag gets closed
			stop = text[start:].find(">")
			if stop >= 0:
				# if it does, strip it, and continue loop
				text = text[:start] + text[start+stop+1:]
				finished = 0
	return text

def save_pixmap(self, pixmap, filename):
	pixmap.save(filename, "jpeg", {"quality":"70"})

def clean(text):
	t = strip_tags(text)
	t = string.replace(t, "&nbsp;", " ")
	t = string.replace(t,'&#34;',"")
	return string.strip(t)

def gdecode(txt, encode):
	try:
		return txt.decode(encode)
	except:
		return txt

# Messages

def error(self, msg, parent=None):
	dialog = gtk.MessageDialog(parent,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
	dialog.run()
	dialog.destroy()

def urllib_error(msg, parent=None):
	dialog = gtk.MessageDialog(parent,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
	dialog.run()
	dialog.destroy()

def warning(self, msg, parent=None):
	dialog = gtk.MessageDialog(parent,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
	dialog.run()
	dialog.destroy()

def info(self, msg, parent=None):
	dialog = gtk.MessageDialog(parent,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
	dialog.run()
	dialog.destroy()

def question(self, msg, cancel=1, parent=None):
	if not parent: parent = self
	dialog = gtk.MessageDialog(parent,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, msg)
	dialog.add_buttons(gtk.STOCK_YES, gtk.RESPONSE_YES,
			gtk.STOCK_NO, gtk.RESPONSE_NO)
	dialog.set_default_response(gtk.RESPONSE_NO)
	response = dialog.run()
	dialog.destroy()
	return response

def file_chooser(title, action=None, buttons=None, name="", folder=os.path.expanduser("~"), picture = False):
	dialog = gtk.FileChooserDialog(title=title, action=action, buttons=buttons)
	dialog.set_default_response(gtk.RESPONSE_OK)
	if name:
		dialog.set_current_name(name)
	if folder:
		dialog.set_current_folder(folder)
	mfilter = gtk.FileFilter()
	if picture==True:
		preview = gtk.Image()
		dialog.set_preview_widget(preview)
		dialog.connect("update-preview", update_preview_cb, preview)
		mfilter.set_name(_("Images"))
		mfilter.add_mime_type("image/png")
		mfilter.add_mime_type("image/jpeg")
		mfilter.add_mime_type("image/gif")
		mfilter.add_pattern("*.[pP][nN][gG]")
		mfilter.add_pattern("*.[jJ][pP][gG]")
		mfilter.add_pattern("*.[gG][iI][fF]")
		mfilter.add_pattern("*.[tT][iI][fF]")
		mfilter.add_pattern("*.[xX][pP][mM]")
		dialog.add_filter(mfilter)
	mfilter = gtk.FileFilter()
	mfilter.set_name(_("All files"))
	mfilter.add_pattern("*")
	dialog.add_filter(mfilter)


	response = dialog.run()
	if response == gtk.RESPONSE_OK:
		filename = dialog.get_filename()
	elif response == gtk.RESPONSE_CANCEL:
		filename = None
	else:
		return False
	path = dialog.get_current_folder()
	dialog.destroy()
	return filename, path

def update_preview_cb(file_chooser, preview):
	filename = file_chooser.get_preview_filename()
	try:
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 128, 128)
		preview.set_from_pixbuf(pixbuf)
		have_preview = True
	except:
		have_preview = False
	file_chooser.set_preview_widget_active(have_preview)
	return

def run_browser(url):
	webbrowser.register('open', webbrowser.GenericBrowser("open '%s'"))
	webbrowser._tryorder.append('open')
	webbrowser.open(url)

def get_media_list_index(media):
	media_desc = {"DVD":0,"DVD-R":1, "DVD-RW":2, "DVD+R":3, "DVD+RW":4, \
		"DVD-RAM":5, "VHS":6, "BETACAM":7, "WMV":8, "DIVX":9, "XVID":10, \
		"VCD":11, "SVCD":12 }
	for k, v in media_desc.items():
		if media == k:
			return v
	return 0

def read_plugins(prefix,directory):
	"""returns available plugins"""
	import glob
	return glob.glob("%s/%s*.py" % (directory,prefix) )

def findKey(val, dict):
	for key, value in dict.items():
		if value == val: return key
	return None

def garbage(handler):
	pass

def make_thumbnail(self, file_name):
	source = os.path.join(self.griffith_dir, "posters/%s"%file_name)
	if os.path.isfile(source):
		self.Image.set_from_file(source)
		pixbuf = self.Image.get_pixbuf()
		pixbuf = pixbuf.scale_simple(30, 40, 'bilinear')
		save_pixmap(self, pixbuf, os.path.join(self.griffith_dir, "posters/t_%s"%file_name))
	else:
		return 0

def make_medium_image(self, file_name):
	source = os.path.join(self.griffith_dir, "posters/%s"%file_name)
	if os.path.isfile(source):
		self.Image.set_from_file(source)
		pixbuf = self.Image.get_pixbuf()
		pixbuf = pixbuf.scale_simple(100, 140, 'bilinear')
		save_pixmap(self, pixbuf, os.path.join(self.griffith_dir, "posters/m_%s"%file_name))
	else:
		return 0

def clean_posters_dir(self):
	posters_dir = os.path.join(self.locations['home'], 'posters')

	counter = 0

	for files in os.walk(posters_dir):
		for names in files:
			for name in names:
				if name.startswith('poster'):
					# lets check if this poster is orphan
					used = self.db.Movie.count_by(image=string.replace(name,".jpg",""))
					if not used:
						counter += 1
						os.unlink(os.path.join(posters_dir, name))
						m_file = os.path.join(posters_dir, "m_"+name)
						if os.path.isfile(m_file):
							os.unlink(m_file)
						t_file = os.path.join(posters_dir, "t_"+name)
						if os.path.isfile(t_file):
							os.unlink(t_file)

	if counter:
		print "%d orphan files cleaned."%counter
	else:
		print "No orphan files found."

def decompress(data):
	import gzip, StringIO
	try:
		compressedStream = StringIO.StringIO(data)
		gzipper = gzip.GzipFile(fileobj=compressedStream)
		data = gzipper.read()
	except:
		pass
	return data
