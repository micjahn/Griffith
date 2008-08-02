# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski
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
gettext.install('griffith', unicode=1)
import gutils
import os
import db

def update_volume_combo_ids(self):
    self.volume_combo_ids = {}
    self.volume_combo_ids[0] = 0
    i = 1
    for volume in self.db.session.query(db.Volume).all():
        self.volume_combo_ids[i] = volume.volume_id
        i += 1

def update_collection_combo_ids(self):
    self.collection_combo_ids = {}
    self.collection_combo_ids[0] = 0
    i = 1
    for collection in self.db.session.query(db.Collection).all():
        self.collection_combo_ids[i] = collection.collection_id
        i += 1

def update_loanedto_combo_ids(self):
    self.loanedto_combo_ids = {}
    self.loanedto_combo_ids[0] = 0
    i = 1
    for person in self.db.session.query(db.Person).order_by('name').all():
        self.loanedto_combo_ids[i] = person.person_id
        i += 1

def update_bytag_combo_ids(self):
    self.bytag_combo_ids = {}
    self.bytag_combo_ids[0] = 0
    i = 1
    for tag in self.db.session.query(db.Tag).order_by('name').all():
        self.bytag_combo_ids[i] = tag.tag_id
        i += 1
