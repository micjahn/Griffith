# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes
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

import csv
import gtk
import gutils
import os
import commands
import string
import platform
import shutil
from tempfile import mkdtemp
import db
from plugins.export import Base

# TODO: bypass the 4Kb file limit on the iPod notes folder, splitting the file in multiple ones and linking them.

class Path2iPod(object):

  def __init__(self):
    self.thing_to_find="iPod_Control"
    self.basepath="/Volumes/"
    self.path_to_pod=self.basepath
  
  def returnPath(self):
    rawfiles = commands.getoutput('ls '+self.basepath)
    myfiles=string.split(rawfiles,'\n')
  
    for myfilename in myfiles:
      tempout = commands.getoutput('ls "'+self.basepath+myfilename+'"')
      newfiles=string.split(tempout,'\n')
      for piece in newfiles:
        if piece==self.thing_to_find:
          self.path_to_pod=self.basepath+myfilename

    if self.path_to_pod == self.basepath:
      return ''
    else:
      return self.path_to_pod

class ExportPlugin(Base):
    name = "iPod"
    description = _("iPod Notes export plugin")
    author = "Vasco Nunes"
    email = "<vasco.m.nunes@gmail.com>"
    version = "0.2"

    fields_to_export = ('number', 'o_title', 'title', 'director' )

    def run(self):
        tmp_dir = mkdtemp()
        griffith_list = open(os.path.join(tmp_dir,"movies"),"w")
        t = []
       
        movies = self.get_query().execute().fetchall()
        for movie in movies:
            t.append("%s | %s | %s | %s" % (movie['number'], movie['o_title'].encode('utf-8'), movie['title'].encode('utf-8'), movie['director'].encode('utf-8')))
    
        griffith_list.write("<title>%s</title><br><br>" % _("My Movies List"))
        
        for movie in t:
            griffith_list.write(movie)
            griffith_list.write("<br>")
            
        griffith_list.close()
        
        # this is a mac, lets export to iPod's notes folder
        # TODO: windows and linux iPod autodetection
        if platform.system() == 'Darwin':
            thisPod=Path2iPod()
            thisPath=thisPod.returnPath()
        
            if thisPath:
                commands.getoutput('mv '+os.path.join(tmp_dir,"movies")+' "'+thisPath+'/Notes/"') # FIXME: WTF?
                gutils.info(_("List was successful exported to iPod."), self.parent_window)
            else:
                gutils.info(_("iPod is not connected."), self.parent_window)
        # this is not a mac, lets save the file
        else:
            filename = gutils.file_chooser(_("Export a %s document")%"CSV", action=gtk.FILE_CHOOSER_ACTION_SAVE, \
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK),name='ipod_griffith_list')
            if filename and filename[0]:
                overwrite = None
                if os.path.isfile(filename[0]):
                    if gutils.question(_("File exists. Do you want to overwrite it?"), self.parent_window):
                        overwrite = True
                    else:
                        overwrite = False
                if overwrite == True or overwrite is None:
                    shutil.copyfile(os.path.join(tmp_dir,"movies"), filename[0])
                    gutils.info(_("List was successful exported. Now you should move it to the 'Notes' folder on your iPod."), self.parent_window)
