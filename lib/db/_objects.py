# -*- coding: UTF-8 -*-
# vim: fdm=marker
__revision__ = '$Id: _objects.py 1251 2009-07-06 18:29:12Z piotrek $'

# Copyright © 2009 Piotr Ożarowski
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

from sqlalchemy.orm import validates

log = logging.getLogger("Griffith")

class DBTable(object):
    def __init__(self, **kwargs):
        for i in kwargs:
            if hasattr(self, i):
                setattr(self, i, kwargs[i])
            else:
                log.warn("%s.%s not set", self.__class__.__name__, i)
    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.name.encode('utf-8'))

    @validates('name')
    def _validate_name(self, key, name):
        if not name or not name.strip():
            log.warning("%s: empty name (%s)", self.__class__.__name__, name)
            raise ValueError(_("Name cannot be empty"))
        return name.strip()

class AChannel(DBTable): pass
class ACodec(DBTable): pass
class Collection(DBTable): pass
class Lang(DBTable): pass
class Medium(DBTable): pass
class Ratio(DBTable): pass
class SubFormat(DBTable): pass
class Tag(DBTable): pass
class VCodec(DBTable): pass
class Volume(DBTable): pass
class Filter(DBTable): pass

class Person(DBTable):
    @validates('email')
    def _validate_email(self, key, address):
        address = address.strip()
        if not EMAIL_PATTERN.match(address):
            log.warning("%s: email address is not valid (%s)", self.__class__.__name__, address)
            raise ValueError(_("E-mail address is not valid"))
        return address

    @validates('phone')
    def _digits_only(self, key, value):
        """removes non-digits"""
        allchars = string.maketrans('', '')
        delchars = allchars.translate(allchars, string.digits)
        return unicode(str(value).translate(allchars, delchars))

class Poster(object):
    @validates('md5sum')
    def _check_md5sum_length(self, key, value):
        if len(value) != 32:
            raise ValueError('md5sum has wrong size')
        return value

    def __init__(self, md5sum=None, data=None):
        if md5sum and data:
            self.md5sum = md5sum
            self.data = data

    def __repr__(self):
        return "<Poster:%s>" % self.md5sum

class Configuration(object):
    def __repr__(self):
        return "<Config:%s=%s>" % (self.param, self.value)

class Loan(object):
    def __repr__(self):
        return "<Loan:%s (person:%s, movie_id:%s, volume_id:%s, collection_id:%s )>" % \
                (self.loan_id, self.person_id, self.movie_id, self.volume_id, self.collection_id)

class MovieLang(object):
    def __init__(self, lang_id=None, type=None, acodec_id=None, achannel_id=None, subformat_id=None):
        self.lang_id = lang_id
        self.type = type
        self.acodec_id = acodec_id
        self.achannel_id = achannel_id
        self.subformat_id = subformat_id

    def __repr__(self):
        return "<MovieLang:%s-%s (Type:%s ACodec:%s AChannel:%s SubFormat:%s)>" % \
            (self.movie_id, self.lang_id, self.type, self.acodec_id, self.achannel_id, self.subformat_id)

class MovieTag(object):
    def __init__(self, tag_id=None):
        self.tag_id = tag_id

    def __repr__(self):
        return "<MovieTag:%s-%s>" % (self.movie_id, self.tag_id)


# has to be at the end of file (objects from this module are imported there)
from _movie import Movie # from _objects import * should import Movie as well
