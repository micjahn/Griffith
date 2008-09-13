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

import gettext
gettext.install('griffith', unicode=1)
from sqlalchemy     import *
from sqlalchemy.orm import mapper, relation, sessionmaker, validates
import re
import string
import logging
log = logging.getLogger("Griffith")

EMAIL_PATTERN = re.compile('^[a-z0-9]+[.a-z0-9_+-]*@[a-z0-9_-]+(\.[a-z0-9_-]+)+$', re.IGNORECASE)
metadata = MetaData()

class DBTable(object):#{{{
    def __init__(self, **kwargs):
        for i in kwargs:
            if hasattr(self, i):
                setattr(self, i, kwargs[i])
            else:
                log.warn("%s.%s not set" % (self.__class__.__name__, i))
    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.name.encode('utf-8'))

    @validates('name')
    def _validate_name(self, key, name):
        if not name or not name.strip():
            log.warning("%s: empty name (%s)" % (self.__class__.__name__, name))
            raise ValueError(_("Name cannot be empty"))
        return name.strip()

    def remove_from_db(self):
        dbtable_id = self.__dict__[self.__class__.__name__.lower() + '_id']
        if dbtable_id<1:
            log.info("%s: none selected => none removed" % self.__class__.__name__)
            return False
        tmp = None
        if hasattr(self,'movies'):
            tmp = getattr(self,'movies')
        elif hasattr(self,'movielangs'):
            tmp = getattr(self,'movielangs')
        if tmp and len(tmp)>0:
            gutils.warning(self, msg=_("This item is in use.\nOperation aborted!"))
            return False
        log.info("%s: removing '%s' (id=%s) from database..."%(self.__class__.__name__, self.name, dbtable_id))
        self.delete()
        try:
            self.flush()
        except exceptions.SQLError, e:
            log.info("%s: remove_from_db: %s" % (self.__class__.__name__, e))
            return False
        #self.refresh()
        return True
    def update_in_db(self):
        dbtable_id = self.__dict__[self.__class__.__name__.lower() + '_id']
        if dbtable_id<1:
            log.info("%s: none selected => none updated" % self.__class__.__name__)
            return False
        tmp = self.query.filter_by(name=self.name).first()
        if tmp is not None and tmp is not self:
            gutils.warning(self, msg=_("This name is already in use!"))
            return False
        self.update()
        try:
            self.flush()
        except exceptions.SQLError, e:
            log.info("%s: update_in_db: %s" % (self.__class__.__name__, e))
            return False
        self.refresh()
        return True
     #}}}

### clases #################################################### {{{
class AChannel(DBTable):
    pass

class ACodec(DBTable):
    pass

class Collection(DBTable):
    pass

class Lang(DBTable):
    pass

class Medium(DBTable):
    pass

class Person(DBTable):
    @validates('email')
    def _validate_email(self, key, address):
        address = address.strip()
        if not EMAIL_PATTERN.match(address):
            log.warning("%s: email address is not valid (%s)" % (self.__class__.__name__, address))
            raise ValueError(_("E-mail address is not valid"))
        return address

    @validates('phone')
    def _digits_only(self, key, value):
        """removes non-digits"""
        allchars = string.maketrans('', '')
        delchars = allchars.translate(allchars, string.digits)
        return unicode(str(value).translate(allchars, delchars))

class Ratio(DBTable):
    pass

class SubFormat(DBTable):
    pass

class Tag(DBTable):
    pass

class VCodec(DBTable):
    pass

class Volume(DBTable):
    pass

class Poster(object):
    def __init__(self, md5sum=None, data=None):
        if md5sum and data:
            if len(md5sum) == 32:
                self.md5sum = md5sum
                self.data = data
            else:
                log.error("md5sum has wrong size")

    def __repr__(self):
        return "<Poster(%s)>" % self.md5sum

class Configuration(object):
    def __repr__(self):
        return "<Config:%s=%s>" % (self.param, self.value)

class Loan(object):
    def __repr__(self):
        return "<Loan:%s (movie:%s person:%s)>" % (self.loan_id, self.movie_id, self.person_id)

class Movie(object):
    def __repr__(self):
        return "<Movie:%s (number=%s)>" % (self.movie_id, self.number)
    def __contains__(self, name):
        if name in ('volume','collection','medium','vcodec','loans','tags','languages','lectors','dubbings','subtitles'): return True
        else: return name in movies_table.columns
    def __getitem__(self, name):
        if name in self:
            return getattr(self, name)
        else: raise AttributeError, name

class MovieLang(object):
    def __init__(self, lang_id=None, type=None, acodec_id=None, achannel_id=None, subformat_id=None):
        self.lang_id      = lang_id
        self.type         = type
        self.acodec_id    = acodec_id
        self.achannel_id  = achannel_id
        self.subformat_id = subformat_id
    def __repr__(self):
        return "<MovieLang:%s-%s (Type:%s ACodec:%s AChannel:%s SubFormat:%s)>" % \
            (self.movie_id, self.lang_id, self.type, self.acodec_id, self.achannel_id, self.subformat_id)

class MovieTag(object):
    def __init__(self, tag_id=None):
        self.tag_id = tag_id
    def __repr__(self):
        return "<MovieTag:%s-%s>" % (self.movie_id, self.tag_id)
#}}}

### table definitions ######################################### {{{
movies_table = Table('movies', metadata,
    Column('movie_id', Integer, primary_key = True),
    Column('number', Integer, nullable=False, unique=True),
    Column('collection_id', Integer, ForeignKey('collections.collection_id')),
    Column('volume_id', Integer, ForeignKey('volumes.volume_id')),
    Column('medium_id', Integer, ForeignKey('media.medium_id')),
    Column('ratio_id', Integer, ForeignKey('ratios.ratio_id')),
    Column('vcodec_id', Integer, ForeignKey('vcodecs.vcodec_id')),
    Column('loaned', Boolean, nullable=False, default=False),
    Column('seen', Boolean, nullable=False, default=False),
    Column('rating', SmallInteger(2)),
    Column('color', SmallInteger),
    Column('cond', SmallInteger),    # MySQL will not accept name "condition"
    Column('layers', SmallInteger),
    Column('region', SmallInteger),
    Column('media_num', SmallInteger),
    Column('runtime', Integer),
    Column('year', Integer),
    Column('o_title', Unicode(256)),
    Column('title', Unicode(256)),
    Column('director', Unicode(256)),
    Column('screenplay', Unicode(256)),
    Column('cameraman', Unicode(256)),
    Column('o_site', Unicode(256)),
    Column('site', Unicode(256)),
    Column('trailer', Unicode(256)),
    Column('country', Unicode(128)),
    Column('genre', Unicode(128)),
    Column('image', Unicode(128)), # XXX: deprecated
    Column('poster_md5', Unicode(32), ForeignKey('posters.md5sum')),
    Column('studio', Unicode(128)),
    Column('classification', Unicode(128)),
    Column('cast', TEXT),
    Column('plot', TEXT),
    Column('notes', TEXT))

loans_table = Table('loans', metadata,
    Column('loan_id', Integer, primary_key=True),
    Column('person_id', Integer, ForeignKey('people.person_id'), nullable=False),
    Column('movie_id', Integer, ForeignKey('movies.movie_id'), nullable=False),
    Column('volume_id', Integer, ForeignKey('volumes.volume_id')),
    Column('collection_id', Integer, ForeignKey('collections.collection_id')),
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
    Column('movie_id', Integer, ForeignKey('movies.movie_id'), nullable=False),
    Column('lang_id', Integer, ForeignKey('languages.lang_id'), nullable=False),
    Column('acodec_id', Integer, ForeignKey('acodecs.acodec_id')),
    Column('achannel_id', Integer, ForeignKey('achannels.achannel_id')),
    Column('subformat_id', Integer, ForeignKey('subformats.subformat_id')))

movie_tag_table = Table('movie_tag', metadata,
    Column('mt_id', Integer, primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.movie_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id')))

configuration_table = Table('configuration', metadata,
    Column('param', Unicode(16), primary_key=True),
    Column('value', Unicode(128), nullable=False))

posters_table = Table('posters', metadata,
    Column('md5sum', Unicode(32), primary_key=True),
    Column('data', BLOB, nullable=False))

tables = {
    'movies':         movies_table,
    'loans':          loans_table,
    'people':         people_table,
    'volumes':        volumes_table,
    'collections':    collections_table,
    'media':          media_table,
    'ratios':         ratios_table,
    'languages':      languages_table,
    'vcodecs':        vcodecs_table,
    'acodecs':        acodecs_table,
    'achannels':      achannels_table,
    'subformats':     subformats_table,
    'tags':           tags_table,
    'movie_lang':     movie_lang_table,
    'movie_tag':      movie_tag_table,
    'configuration':  configuration_table,
    'posters':        posters_table}
#}}}

### mappers ################################################### {{{
mapper(Configuration, configuration_table)
mapper(Volume, volumes_table, order_by=volumes_table.c.name, properties={
    'movies': relation(Movie, backref='volume')})
mapper(Collection, collections_table, order_by=collections_table.c.name, properties={
    'movies': relation(Movie, backref='collection')})
mapper(Medium, media_table, properties={
    'movies': relation(Movie, backref='medium')})
mapper(Ratio, media_table, properties={
    'movies': relation(Movie, backref='ratios')})
mapper(VCodec, vcodecs_table, properties={
    'movies': relation(Movie, backref='vcodec')})
mapper(Person, people_table, properties = {
    'loans'    : relation(Loan, backref='person', cascade='all, delete-orphan')})
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
    'movies': relation(Movie)})
#}}}



# for debugging (run: ipython db.py)
if __name__ == '__main__':
    import os.path
    import sqlalchemy
    logging.basicConfig()
    log.setLevel(logging.INFO)
    log.info("SQLAlchemy version: %s" % sqlalchemy.__version__)

    ### ENGINE ###
    engine_mem = create_engine('sqlite:///:memory:', echo=False)

    # create tables
    metadata.create_all(engine_mem)

    ### MEMORY SESSION ###
    # create a configured "Session" class
    Session = sessionmaker(bind=engine_mem)
    # create a Session
    sess_mem = Session()


    griffith_dir = os.path.expanduser("~/.griffith/")
    url = "sqlite:///%s" % os.path.join(griffith_dir, 'griffith.db')
    engine_my = create_engine(url, echo=False)
    Session2 = sessionmaker(bind=engine_my)
    sess_my = Session2()

    print "\nAvailable variables:"
    print "sess_my:  %s" % sess_my
    print "sess_mem: %s" % sess_mem

    movie1_my = sess_my.query(Movie).first()
    if movie1_my:
        movie1_mem = sess_mem.merge(movie1_my)
        movie1_mem.title = u'updated movie title'
        sess_mem.add(movie1_mem)
        sess_mem.commit()
        print "movie1_my:  %s - title: %s" % (movie1_my, movie1_my.title)
        print "movie1_mem: %s - title: %s" % (movie1_mem, movie1_mem.title)
