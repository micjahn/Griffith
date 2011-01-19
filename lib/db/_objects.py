# -*- coding: UTF-8 -*-
# vim: fdm=marker
__revision__ = '$Id$'

# Copyright © 2009-2011 Piotr Ożarowski
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
import re
import string

from sqlalchemy import and_, func
from sqlalchemy.orm import validates, object_session
from sqlalchemy.sql import select, update

import tables

log = logging.getLogger('Griffith')

EMAIL_PATTERN = re.compile('^[a-z0-9]+[.a-z0-9_+-]*@[a-z0-9_-]+(\.[a-z0-9_-]+)+$', re.IGNORECASE)


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


class AChannel(DBTable):
    pass


class ACodec(DBTable):
    pass


class Lang(DBTable):
    pass


class Medium(DBTable):
    pass


class Ratio(DBTable):
    pass


class SubFormat(DBTable):
    pass


class Tag(DBTable):
    pass


class VCodec(DBTable):
    pass


class Filter(DBTable):
    pass


class Collection(DBTable):

    def _set_loaned_flag(self, flag):
        """Sets loaned flag in current collection and all associated movies.

        :param flag: if True and there are loaned movies in the collection
            already, exception will be raised (whole collection cannot be
            loaned if one of the movies is not available).
            Please also remember to create new entry in loans table later (no
            need to do that if flag is False).
        """

        session = object_session(self)

        if flag: # loaning whole collection
            loaned_movies = session.execute(select([tables.movies.columns.movie_id])\
                    .where(and_(tables.movies.columns.collection_id == self.collection_id,\
                        tables.movies.columns.loaned == True))).fetchall()
            if loaned_movies:
                log.error('cannot loan it, collection contains loaned movie(s): %s', loaned_movies)
                raise Exception('loaned movies in the collection already')

        self._loaned = flag
        update_query = update(tables.movies, tables.movies.columns.collection_id == self.collection_id)
        session.execute(update_query, params={'loaned': flag})

    def _is_loaned(self):
        return self._loaned

    loaned = property(_is_loaned, _set_loaned_flag)


class Volume(DBTable):

    def _set_loaned_flag(self, flag):
        """Sets loaned flag in current volume and all associated movies.

        :param flag: if True, remember to create new entry in loans table
            later!
        """

        session = object_session(self)

        self._loaned = flag
        update_query = update(tables.movies, tables.movies.columns.volume_id == self.volume_id)
        session.execute(update_query, params={'loaned': flag})

    def _is_loaned(self):
        return self._loaned

    loaned = property(_is_loaned, _set_loaned_flag)


class Loan(object):

    def __repr__(self):
        return "<Loan:%s (person:%s, movie_id:%s, volume_id:%s, collection_id:%s )>" % \
                (self.loan_id, self.person_id, self.movie_id, self.volume_id, self.collection_id)

    def returned_on(self, date=None):
        """
        Marks the loan as returned and clears loaned flag in related movies.
        """

        if date is None:
            date = func.current_date()
        # note that SQLAlchemy will convert YYYYMMDD strings to datetime, no need to touch it

        if self.return_date: # already returned, just update the date
            self.return_date = date
            return True

        session = object_session(self)

        if self.collection_id:
            self.collection.loaned = False # will update the loaned flag in all associated movies as well
        if self.volume_id:
            self.volume.loaned = False # will update the loaned flag in all associated movies as well
        if self.movie_id:
            self.movie.loaned = False
        self.return_date = date


class Person(DBTable):

    @validates('email')
    def _validate_email(self, key, address):
        address = address.strip()
        if address and not EMAIL_PATTERN.match(address):
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
