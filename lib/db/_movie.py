# -*- coding: UTF-8 -*-
__revision__ = '$Id: _movie.py 1556 2011-06-13 20:46:47Z mikej06 $'

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

from sqlalchemy import and_, or_
from sqlalchemy.orm import object_session
from sqlalchemy.sql import select, update

import tables
from _objects import Loan, DBTable

log = logging.getLogger('Griffith')

res_aliases = {(2560, 1600): ('QSXGA',),
                (2048, 1536): ('QXGA',),
                (1920, 1200): ('WUXGA',),
                (1920, 1080): ('1080p', 'HD 1080', '1080'),
                (1920, 540): ('1080i',),
                (1680, 1050): ('WSXGA+',),
                (1600, 1200): ('UXGA',),
                (1400, 1050): ('SXGA+',),
                #(1440, 960): ('',),
                #(1280, 960): ('',),
                #(1280, 854): ('',),
                (1280, 720): ('720p', 'HD 720', '720'),
                (1280, 360): ('720i',),
                (1280, 1024): ('SXGA',),
                #(1152, 768): ('',),
                (1024, 768): ('XGA',),
                (854, 480): ('WVGA',),
                (800, 600): ('SVGA',),
                (768, 576): ('PAL',),
                (720, 480): ('NTSC',),
                (640, 480): ('VGA',),
                (320, 240): ('QVGA',),
                (320, 200): ('CGA',),
                # some kine of "virtual" resolutions
                (1, 1): ('4:3 Fullscreen',),
                (1, 2): ('Widescreen',),
                (1, 3): ('Anamorphic Widescreen',)}
res_alias_res = {}
for res, aliases in res_aliases.iteritems():
    for alias in aliases:
        res_alias_res[alias.upper()] = res
del aliases, alias, res


class Movie(DBTable):

    def _set_resolution(self, res_string):
        if not res_string: # clear resulution field
            self.width = None
            self.height = None
        elif res_string.upper() in res_alias_res:
            self.width, self.height = res_alias_res[res_string.upper()]
        else:
            try:
                if 'x' in res_string:
                    self.width, self.height = map(int, res_string.lower().split('x'))
                else:
                    self.width, self.height = map(int, res_string.lower().split())
            except Exception, e:
                log.warning('wrong resolution name: %s', e)
                raise ValueError('Use standard resolution name or \d+x\d+')

    def _get_resolution(self):
        if not self.width or not self.height:
            return None
        resolution = (self.width, self.height)
        if resolution in res_aliases:
            return res_aliases[resolution][0]
        else:
            res_string = "%dx%d" % resolution
            return res_string
    resolution = property(_get_resolution, _set_resolution)

    def __repr__(self):
        return "<Movie:%s (number=%s)>" % (self.movie_id, self.number)

    def __contains__(self, name):
        if name in ('volume', 'collection', 'medium', 'vcodec', 'loans', 'tags',\
                    'languages', 'lectors', 'dubbings', 'subtitles', 'resolution'):
            return True
        else:
            return name in tables.movies.columns

    def __getitem__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError(name)

    def _get_loan_history(self):
        where = [tables.loans.c.movie_id == self.movie_id]
        if self.collection_id is not None:
            where.append(tables.loans.c.collection_id == self.collection_id)
        if self.volume_id is not None:
            where.append(tables.loans.c.volume_id == self.volume_id)
        return object_session(self).query(Loan).filter(\
                and_(tables.loans.c.return_date != None, or_(*where))).all()
    loan_history = property(_get_loan_history, doc='list of already returned loans')

    def _get_loan_details(self):
        where = [tables.loans.c.movie_id == self.movie_id]
        if self.collection_id is not None:
            where.append(tables.loans.c.collection_id == self.collection_id)
        if self.volume_id is not None:
            where.append(tables.loans.c.volume_id == self.volume_id)
        return object_session(self).query(Loan).filter(and_(tables.loans.c.return_date == None, or_(*where))).first()
    loan_details = property(_get_loan_details, doc='current loan details or None')

    def loan_to(self, person, whole_collection=False):
        """
        Loans movie, all other movies from the same volume and optionally
        movie's collection.

        :param person: Person instance or person_id.
        :param whole_collection=False: if True, will loan all movies from the same
            collection.
        """

        if self.loaned:
            log.warn('movie already loaned: %s', self.loan_details)
            return False

        session = object_session(self)

        if hasattr(person, 'person_id'):
            person = person.person_id
        elif not isinstance(person, int):
            raise ValueError("expecting int or Person instance, got %s instead" % type(person))

        loan = Loan()
        loan.person_id = person
        loan.movie = self

        if whole_collection:
            if self.collection:
                # next line will update the status of all other movies in collection
                # or raise and OtherMovieAlreadyLoanedError
                self.collection.loaned = True
                loan.collection_id = self.collection_id
            else:
                log.debug('this movie doesn\'t have collection assigned, whole_collection param ignored')

        if self.volume:
            # next line will update the status of all other movies in volume
            self.volume.loaned = True
            loan.volume_id = self.volume_id

        self.loaned = True
        session.add(loan)

        return True
