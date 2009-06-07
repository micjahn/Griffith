# -*- coding: UTF-8 -*-
# vim: fdm=marker
__revision__ = '$Id$'

# Copyright (c) 2008 Vasco Nunes, Piotr Ożarowski
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


# XXX: keep stdlib and SQLAlchemy imports only in this file

from sqlalchemy     import *
from sqlalchemy.orm import mapper, relation, deferred, validates, column_property
import re
import string
import logging
import marshal
log = logging.getLogger("Griffith")

EMAIL_PATTERN = re.compile('^[a-z0-9]+[.a-z0-9_+-]*@[a-z0-9_-]+(\.[a-z0-9_-]+)+$', re.IGNORECASE)
metadata = MetaData()

class DBTable(object):#{{{
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
     #}}}

### clases #################################################### {{{

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
    def __init__(self, md5sum=None, data=None):
        if md5sum and data:
            if len(md5sum) == 32:
                self.md5sum = md5sum
                self.data = data
            else:
                log.error('md5sum has wrong size')

    def __repr__(self):
        return "<Poster(%s)>" % self.md5sum

class Configuration(object):
    def __repr__(self):
        return "<Config:%s=%s>" % (self.param, self.value)

class Loan(object):
    def __repr__(self):
        return "<Loan:%s (movie:%s person:%s)>" % (self.loan_id, self.movie_id, self.person_id)

class Movie(object):
    _res_aliases = {(2560, 1600): ('QSXGA',),
                    (2048, 1536): ('QXGA',),
                    (1920, 1200): ('WUXGA',),
                    (1920, 1080): ('HD 1080', '1080p', '1080'),
                    (1920, 540): ('1080i',),
                    (1680, 1050): ('WSXGA+',),
                    (1600, 1200): ('UXGA',),
                    (1400, 1050): ('SXGA+',),
                    #(1440, 960): ('',),
                    #(1280, 960): ('',),
                    #(1280, 854): ('',),
                    (1280, 720): ('HD 720', '720p', '720'),
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
                    (320, 200): ('CGA',)}
    _res_alias_res = {}
    for res, aliases in _res_aliases.iteritems():
        for alias in aliases:
            _res_alias_res[alias.upper()] = res
    print aliases, alias, res
    del aliases, alias, res

    def _set_resolution(self, res_string):
        if not res_string: # clear resulution field
            self.width = None
            self.height = None
        elif res_string.upper() in Movie._res_alias_res:
            self.width, self.height = Movie._res_alias_res[res_string.upper()]
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
        if resolution in Movie._res_aliases:
            return Movie._res_aliases[resolution][0]
        else:
            res_string = "%dx%d" % resolution
            return res_string

    resolution = property(_get_resolution, _set_resolution)

    def __repr__(self):
        return "<Movie:%s (number=%s)>" % (self.movie_id, self.number)

    def __contains__(self, name):
        if name in ('volume','collection','medium','vcodec','loans','tags',\
                    'languages','lectors','dubbings','subtitles','resolution'):
            return True
        else: return name in movies_table.columns

    def __getitem__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError, name

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

class Filter(object):
    def __init__(self, name=None, cond=None):
        if name and cond:
            self.name = name
            #self.data = marshal.dumps(cond)
            self.conditions = cond

    def __repr__(self):
        return "<Filter(%s)>" % self.name

    def _set_cond(self, cond):
        self.data = marshal.dumps(cond)
    def _get_cond(self):
        return marshal.loads(self.data)
    conditions = property(_get_cond, _set_cond)
#}}}

### table definitions ######################################### {{{
movies_table = Table('movies', metadata,
    Column('movie_id', Integer, primary_key = True),
    Column('number', Integer, nullable=False, unique=True, index=True),
    Column('collection_id', ForeignKey('collections.collection_id')),
    Column('volume_id', ForeignKey('volumes.volume_id')),
    Column('medium_id', ForeignKey('media.medium_id')),
    Column('ratio_id', ForeignKey('ratios.ratio_id')),
    Column('vcodec_id', ForeignKey('vcodecs.vcodec_id')),
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
    Column('image', Unicode(128)), # XXX: deprecated
    Column('poster_md5', ForeignKey('posters.md5sum')),
    Column('studio', Unicode(128)),
    Column('classification', Unicode(128)),
    Column('cast', Text),
    Column('plot', Text),
    Column('notes', Text))

loans_table = Table('loans', metadata,
    Column('loan_id', Integer, primary_key=True),
    Column('person_id',  ForeignKey('people.person_id'), nullable=False),
    Column('movie_id', ForeignKey('movies.movie_id'), nullable=False),
    Column('volume_id', ForeignKey('volumes.volume_id')),
    Column('collection_id', ForeignKey('collections.collection_id')),
    Column('date', Date, nullable=False, default=func.current_date()),
    Column('return_date', Date, nullable=True))

people_table = Table('people', metadata,
    Column('person_id', Integer, primary_key=True),
    Column('name', Unicode(256), nullable=False, unique=True),
    Column('email', Unicode(128)),
    Column('phone', Unicode(64)))

volumes_table = Table('volumes', metadata,
    Column('volume_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True),
    Column('loaned', Boolean, nullable=False, default=False))

collections_table = Table('collections', metadata,
    Column('collection_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True),
    Column('loaned', Boolean, nullable=False, default=False))

media_table = Table('media', metadata,
    Column('medium_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

ratios_table = Table('ratios', metadata,
    Column('ratio_id', Integer, primary_key=True),
    Column('name', Unicode(5), nullable=False, unique=True))

languages_table = Table('languages', metadata,
    Column('lang_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

vcodecs_table = Table('vcodecs', metadata,
    Column('vcodec_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

acodecs_table = Table('acodecs', metadata,
    Column('acodec_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

achannels_table = Table('achannels', metadata,
    Column('achannel_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

subformats_table = Table('subformats', metadata,
    Column('subformat_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

tags_table = Table('tags', metadata,
    Column('tag_id', Integer, primary_key=True),
    Column('name', Unicode(64), nullable=False, unique=True))

movie_lang_table = Table('movie_lang', metadata,
    Column('ml_id', Integer, primary_key=True),
    Column('type', SmallInteger), # 0: Original, 1:lector, 2:dubbing, 3:subtitle
    Column('movie_id', ForeignKey('movies.movie_id'), nullable=False),
    Column('lang_id', ForeignKey('languages.lang_id'), nullable=False),
    Column('acodec_id', ForeignKey('acodecs.acodec_id')),
    Column('achannel_id', ForeignKey('achannels.achannel_id')),
    Column('subformat_id', ForeignKey('subformats.subformat_id')))

movie_tag_table = Table('movie_tag', metadata,
    Column('mt_id', Integer, primary_key=True),
    Column('movie_id', ForeignKey('movies.movie_id')),
    Column('tag_id', ForeignKey('tags.tag_id')))

configuration_table = Table('configuration', metadata,
    Column('param', Unicode(16), primary_key=True),
    Column('value', Unicode(128), nullable=False))

posters_table = Table('posters', metadata,
    Column('md5sum', Unicode(32), primary_key=True),
    Column('data', Binary(1048576), nullable=False))

filters_table = Table('filters', metadata,
    Column('name', Unicode(64), primary_key=True),
    #Column('data', PickleType, nullable=False))
    Column('data', Binary, nullable=False))
#}}}

### mappers ################################################### {{{
mapper(Configuration, configuration_table)
mapper(Volume, volumes_table, order_by=volumes_table.c.name, properties={
    'movies': relation(Movie, backref='volume')})
mapper(Collection, collections_table, order_by=collections_table.c.name, properties={
    'movies': relation(Movie, backref='collection')})
mapper(Medium, media_table, properties={
    'movies': relation(Movie, backref='medium')})
mapper(Ratio, ratios_table, properties={
    'movies': relation(Movie, backref='ratio')})
mapper(VCodec, vcodecs_table, properties={
    'movies': relation(Movie, backref='vcodec')})
mapper(Person, people_table, properties = {
    'loans': relation(Loan, backref='person', cascade='all, delete-orphan'),
    'loaned_movies_count': column_property(select(
        [func.count(loans_table.c.loan_id)],
        and_(people_table.c.person_id == loans_table.c.person_id,
             loans_table.c.return_date == None
        )).label('loaned_movies_count'), deferred=True),
    'returned_movies_count': column_property(select( # AKA loan history
        [func.count(loans_table.c.loan_id)],
        and_(people_table.c.person_id == loans_table.c.person_id,
             loans_table.c.return_date != None
        )).label('returned_movies_count'), deferred=True)
    })
mapper(MovieLang, movie_lang_table, primary_key=[movie_lang_table.c.ml_id], properties = {
    'movie'    : relation(Movie),
    'language' : relation(Lang),
    'achannel' : relation(AChannel),
    'acodec'   : relation(ACodec),
    'subformat': relation(SubFormat)})
mapper(ACodec, acodecs_table, properties={
    'movielangs': relation(MovieLang)})
mapper(AChannel, achannels_table, properties={
    'movielangs': relation(MovieLang)})
mapper(SubFormat, subformats_table, properties={
    'movielangs': relation(MovieLang)})
mapper(Lang, languages_table, properties={
    'movielangs': relation(MovieLang)})
mapper(MovieTag, movie_tag_table)
mapper(Tag, tags_table, properties={'movietags': relation(MovieTag, backref='tag')})
mapper(Loan, loans_table, properties = {
    'volume'    : relation(Volume),
    'collection': relation(Collection)})
mapper(Movie, movies_table, order_by=movies_table.c.number , properties = {
    'loans'     : relation(Loan, backref='movie', cascade='all, delete-orphan'),
    #'tags'       : relation(Tag, cascade='all, delete-orphan', secondary=movie_tag,
    'tags'      : relation(Tag, secondary=movie_tag_table,
                           primaryjoin=movies_table.c.movie_id==movie_tag_table.c.movie_id,
                           secondaryjoin=movie_tag_table.c.tag_id==tags_table.c.tag_id),
    'languages' : relation(MovieLang, cascade='all, delete-orphan')})
mapper(Poster, posters_table, properties={
    'movies': relation(Movie),
    'data'  :  deferred(posters_table.c.data)
    })
mapper(Filter, filters_table)
#}}}

