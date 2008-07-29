# -*- coding: UTF-8 -*-
# vim: fdm=marker

__revision__ = '$Id: $'

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

# imports
from sqlalchemy     import *
from sqlalchemy.orm import mapper, relation, sessionmaker

metadata = MetaData()

### clases #################################################### {{{
class Configuration(object):
    def __repr__(self):
        return "<Config:%s=%s>" % (self.param, self.value)
class AChannel(object):
    pass
class ACodec(object):
    pass
class Collection(object):
    pass
class Lang(object):
    pass
class Medium(object):
    pass
class Person(object):
    pass
class SubFormat(object):
    pass
class Tag(object):
    pass
class VCodec(object):
    pass
class Volume(object):
    pass
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
    Column('o_title', VARCHAR(255)),
    Column('title', VARCHAR(255)),
    Column('director', VARCHAR(255)),
    Column('o_site', VARCHAR(255)),
    Column('site', VARCHAR(255)),
    Column('trailer', VARCHAR(256)),
    Column('country', VARCHAR(128)),
    Column('genre', VARCHAR(128)),
    Column('image', VARCHAR(128)),
    Column('studio', VARCHAR(128)),
    Column('classification', VARCHAR(128)),
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
    Column('name', VARCHAR(255), nullable=False, unique=True),
    Column('email', VARCHAR(128)),
    Column('phone', VARCHAR(64)))

volumes_table = Table('volumes', metadata,
    Column('volume_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True),
    Column('loaned', Boolean, nullable=False, default=False))

collections_table = Table('collections', metadata,
    Column('collection_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True),
    Column('loaned', Boolean, nullable=False, default=False))

media_table = Table('media', metadata,
    Column('medium_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True))

languages_table = Table('languages', metadata,
    Column('lang_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True))

vcodecs_table = Table('vcodecs', metadata,
    Column('vcodec_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True))

acodecs_table = Table('acodecs', metadata,
    Column('acodec_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True))

achannels_table = Table('achannels', metadata,
    Column('achannel_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True))

subformats_table = Table('subformats', metadata,
    Column('subformat_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True))

tags_table = Table('tags', metadata,
    Column('tag_id', Integer, primary_key=True),
    Column('name', VARCHAR(64), nullable=False, unique=True))

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
    Column('param', VARCHAR(16), primary_key=True),
    Column('value', VARCHAR(128), nullable=False))
#}}}

### mappers ################################################### {{{
mapper(Configuration, configuration_table)
mapper(Volume, volumes_table, order_by=volumes_table.c.name, properties={
    'movies': relation(Movie, backref='volume')})
mapper(Collection, collections_table, order_by=collections_table.c.name, properties={
    'movies': relation(Movie, backref='collection')})
mapper(Medium, media_table, properties={
    'movies': relation(Movie, backref='medium')})
mapper(VCodec, vcodecs_table, properties={
    'movies': relation(Movie, backref='vcodec')})
mapper(Person, people_table, properties = {
    'loans'    : relation(Loan, backref='person', cascade='all, delete-orphan')})
mapper(MovieLang, movie_lang_table, primary_key=[movie_lang_table.c.ml_id], properties = {
    'movie'    : relation(Movie, lazy=False),
    'language' : relation(Lang, lazy=False),
    'achannel' : relation(AChannel),
    'acodec'   : relation(ACodec),
    'subformat': relation(SubFormat)})
mapper(ACodec, acodecs_table, properties={
    'movielangs': relation(MovieLang, lazy=False)})
mapper(AChannel, achannels_table, properties={
    'movielangs': relation(MovieLang, lazy=False)})
mapper(SubFormat, subformats_table, properties={
    'movielangs': relation(MovieLang, lazy=False)})
mapper(Lang, languages_table, properties={
    'movielangs': relation(MovieLang, lazy=False)})
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
#}}}



# for debugging (run: ipython db.py)
if __name__ == '__main__':
    import os.path
    import sqlalchemy

    ### ENGINE ###
    engine = create_engine('sqlite:///:memory:', echo=False)

    # create tables
    metadata.create_all(engine)


    ### SESSION ###
    # create a configured "Session" class
    Session = sessionmaker(bind=engine)
    # create a Session
    sess = Session()
    # work with sess
    myobject = Movie()
    #sess.add(myobject)
    #sess.commit()
    # close when finished
    #sess.close()
    print "SQLAlchemy version: %s" % sqlalchemy.__version__


    griffith_dir = "/home/pox/.griffith/"
    url = "sqlite:///%s" % os.path.join(griffith_dir, 'griffith.db')
    engine2 = create_engine(url, echo=False)
    Session2 = sessionmaker(bind=engine2)
    sess2 = Session2()

    movie1 = sess2.query(Movie)[0]
    print movie1, movie1.title
    movie1_clone = sess.merge(movie1)
    movie1_clone.title = 'cos'
    sess.add(movie1_clone)
    sess.commit()
    for i in sess.query(Movie)[:3]:
        print i, i.title
