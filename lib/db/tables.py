# -*- coding: UTF-8 -*-
# vim: fdm=marker
__revision__ = '$Id$'

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

from sqlalchemy import Table, Column, ForeignKey, func
from sqlalchemy.types import Boolean, Unicode, Text, Integer, SmallInteger, Date, Binary, PickleType

from db import metadata

posters = Table('posters', metadata,
    Column('md5sum', Unicode(32), primary_key=True),
    Column('data', Binary(1048576), nullable=False))

volumes = Table('volumes', metadata,
    Column('volume_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True),
    Column('loaned', Boolean, nullable=False, default=False))

collections = Table('collections', metadata,
    Column('collection_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True),
    Column('loaned', Boolean, nullable=False, default=False))

media = Table('media', metadata,
    Column('medium_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

ratios = Table('ratios', metadata,
    Column('ratio_id', Integer, primary_key=True),
    Column('name', Unicode(5), nullable=False, unique=True))

vcodecs = Table('vcodecs', metadata,
    Column('vcodec_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

movies = Table('movies', metadata,
    Column('movie_id', Integer, primary_key=True),
    Column('number', Integer, nullable=False, unique=True, index=True),
    Column('collection_id', ForeignKey(collections.c.collection_id)),
    Column('volume_id', ForeignKey(volumes.c.volume_id)),
    Column('medium_id', ForeignKey(media.c.medium_id)),
    Column('ratio_id', ForeignKey(ratios.c.ratio_id)),
    Column('vcodec_id', ForeignKey(vcodecs.c.vcodec_id)),
    Column('poster_md5', ForeignKey(posters.c.md5sum)),
    Column('loaned', Boolean, nullable=False, default=False),
    Column('seen', Boolean, nullable=False, default=False),
    Column('rating', SmallInteger(2)),
    Column('color', SmallInteger),
    Column('cond', SmallInteger), # MySQL will not accept name "condition"
    Column('layers', SmallInteger),
    Column('region', SmallInteger),
    Column('media_num', SmallInteger),
    Column('runtime', SmallInteger),
    Column('year', SmallInteger),
    Column('width', SmallInteger),
    Column('height', SmallInteger),
    Column('barcode', Unicode(32)),
    Column('o_title', Unicode(256), index=True),
    Column('title', Unicode(256), index=True),
    Column('director', Unicode(256)),
    Column('screenplay', Unicode(256)),
    Column('cameraman', Unicode(256)),
    Column('o_site', Unicode(256)),
    Column('site', Unicode(256)),
    Column('trailer', Unicode(256)),
    Column('country', Unicode(128)),
    Column('genre', Unicode(128)),
    Column('studio', Unicode(128)),
    Column('classification', Unicode(128)),
    Column('cast', Text),
    Column('plot', Text),
    Column('notes', Text),
    Column('image', Unicode(128)), # XXX: deprecated
    )

people = Table('people', metadata,
    Column('person_id', Integer, primary_key=True),
    Column('name', Unicode(256), nullable=False, unique=True),
    Column('email', Unicode(128)),
    Column('phone', Unicode(64)))

loans = Table('loans', metadata,
    Column('loan_id', Integer, primary_key=True),
    Column('person_id',  ForeignKey(people.c.person_id), nullable=False),
    Column('movie_id', ForeignKey(movies.c.movie_id), nullable=False),
    Column('volume_id', ForeignKey(volumes.c.volume_id)),
    Column('collection_id', ForeignKey(collections.c.collection_id)),
    Column('date', Date, nullable=False, default=func.current_date()),
    Column('return_date', Date, nullable=True))

languages = Table('languages', metadata,
    Column('lang_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

acodecs = Table('acodecs', metadata,
    Column('acodec_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

achannels = Table('achannels', metadata,
    Column('achannel_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

subformats = Table('subformats', metadata,
    Column('subformat_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

tags = Table('tags', metadata,
    Column('tag_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

movie_lang = Table('movie_lang', metadata,
    Column('ml_id', Integer, primary_key=True),
    Column('type', SmallInteger), # 0: Original, 1:lector, 2:dubbing, 3:subtitle
    Column('movie_id', ForeignKey(movies.c.movie_id), nullable=False),
    Column('lang_id', ForeignKey(languages.c.lang_id), nullable=False),
    Column('acodec_id', ForeignKey(acodecs.c.acodec_id)),
    Column('achannel_id', ForeignKey(achannels.c.achannel_id)),
    Column('subformat_id', ForeignKey(subformats.c.subformat_id)))

movie_tag = Table('movie_tag', metadata,
    Column('mt_id', Integer, primary_key=True),
    Column('movie_id', ForeignKey(movies.c.movie_id)),
    Column('tag_id', ForeignKey(tags.c.tag_id)))

configuration = Table('configuration', metadata,
    Column('param', Unicode(16), primary_key=True),
    Column('value', Unicode(128), nullable=False))

filters = Table('filters', metadata,
    Column('name', Unicode(64), primary_key=True),
    Column('data', PickleType, nullable=False))
