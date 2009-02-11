# -*- coding: UTF-8 -*-
# vim: fdm=marker

__revision__ = '$Id$'

# Copyright (c) 2005-2009 Vasco Nunes, Piotr Ożarowski
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


# XXX: keep stdlib, griffith.db and SQLAlchemy imports only in this file

from sqlalchemy            import *
from sqlalchemy.orm        import sessionmaker
from sqlalchemy.exceptions import OperationalError
import os.path
import logging
log = logging.getLogger("Griffith")
import gutils # TODO: get rid of this import
import db # ORM data (SQLAlchemy stuff)

class GriffithSQL(object):
    version = 4 # database format version, increase after changing data structures

    def __init__(self, config, griffith_dir, locations, fallback=True):
        #mapper = Session.mapper
        self.config = config
        self.data_dir = griffith_dir

        if config.get('type', None, section='database') is None:
            config.set('type', 'sqlite', section='database')

        if config.get('type', 'sqlite', section='database') != 'sqlite':
            if config.get('host', None, section='database') is None:
                config.set('host', '127.0.0.1', section='database')
            if config.get('user', None, section='database') is None:
                config.set('user', 'griffith', section='database')
            if config.get('passwd', None, section='database') is None:
                config.set('passwd', 'gRiFiTh', section='database')
            if config.get('name', None, section='database') is None:
                config.set('name', 'griffith', section='database')

        # connect to database --------------------------------------{{{
        if config.get('type', section='database') == 'sqlite':
            url = "sqlite:///%s" % os.path.join(griffith_dir, config.get('name', 'griffith', section='database') + '.db')
        elif config.get('type', section='database') == 'postgres':
            if config.get('port', 0, section='database')==0:
                config.set('port', 5432, section='database')
            url = "postgres://%s:%s@%s:%d/%s" % (
                config.get('user', section='database'),
                config.get('passwd', section='database'),
                config.get('host', section='database'),
                int(config.get('port', section='database')),
                config.get('name', section='database'))
        elif config.get('type', section='database') == 'mysql':
            if config.get('port', 0, section='database')==0:
                config.set('port', 3306, section='database')
            url = "mysql://%s:%s@%s:%d/%s?charset=utf8&use_unicode=0" % (
                config.get('user', section='database'),
                config.get('passwd', section='database'),
                config.get('host', section='database'),
                int(config.get('port', section='database')),
                config.get('name', section='database'))
        elif config.get('type', section='database') == 'mssql':
            if config.get('port', 0, section='database')==0:
                config.set('port', 1433, section='database')
            # use_scope_identity=0 have to be set as workaround for a sqlalchemy bug
            # but it is not guaranteed that the right identity value will be selected
            # because the select @@identity statement selects the very last id which
            # also can be a id from a trigger-insert or another user
            # sqlalchemy uses a wrong syntax. It has to select the id within the insert
            # statement: insert <table> (<columns>) values (<values>) select scope_identity()
            # (one statement !) After preparing and executing there should be a fetch
            # If it is executed as two separate statements the scope is lost after insert.
            url = "mssql://%s:%s@%s:%d/%s?use_scope_identity=0" % (
                config.get('user', section='database'),
                config.get('passwd', section='database'),
                config.get('host', section='database'),
                int(config.get('port', section='database')),
                config.get('name', section='database'))
        else:
            config.set('type', 'sqlite', section='database')
            url = "sqlite:///%s" % os.path.join(griffith_dir, config.get('name', 'griffith', section='database') + '.db')

        try:
            engine = create_engine(url, echo=False)
            conn = engine.connect()
        except Exception, e:    # InvalidRequestError, ImportError
            log.info("MetaData: %s", e)
            if not fallback:
                raise e
            config.set('type', 'sqlite', section='database')
            gutils.warning(self, "%s\n\n%s" % (_('Cannot connect to database.\nFalling back to SQLite.'), _('Please check debug output for more informations.')))
            url = "sqlite:///%s" % os.path.join(griffith_dir, config.get('name', 'griffith', section='database') + '.db')
            engine = create_engine(url)
            conn = engine.connect()

        # try to establish a db connection
        try:
            Session = sessionmaker(bind=engine)
            session = Session()
            #self.metadata.bind.connect()
        except Exception, e:
            log.info("engine connection error: %s", e)
            if not fallback:
                raise e
            gutils.error(self, _('Database connection failed.'))
            config.set('type', 'sqlite', section='database')
            url = "sqlite:///%s" % os.path.join(griffith_dir, 'griffith.db')
            engine = create_engine(url)
            Session = sessionmaker(bind=engine)
            session = Session()

        self.session = session # global session
        self.Session = Session # create new sessions using this class
        #}}}

        # check if database needs an upgrade
        db.metadata.create_all(engine)
        try:
            v = self.session.query(db.Configuration).filter_by(param=u'version').first()    # returns None if table exists && param ISNULL
        except OperationalError, e:
            log.info(str(e))
            v = 0
        except Exception, e:
            log.error(str(e))
            v = 0

        if v is not None and v>1:
            v = int(v.value)
        if v < self.version:
            from dbupgrade import upgrade_database
            if not upgrade_database(self, v, locations, config):
                raise Exception('cannot upgrade database')
        elif v > self.version:
            log.error("database version mismatch (detected:%s; current:%s)", v, self.version)
            gutils.warning(_('This database requires newer version of Griffith.'))
            raise Exception("database version mismatch")


def update_whereclause(query, cond): # {{{
    if cond['loaned'] is True:
        query.append_whereclause(db.Movie.loaned==True)
    if cond['loaned'] is False:
        query.append_whereclause(db.Movie.loaned==False)
    if cond['seen'] is True:
        query.append_whereclause(db.Movie.seen==True)
    if cond['seen'] is False:
        query.append_whereclause(db.Movie.seen==False)

    if cond["collections"]:
        query.append_whereclause(db.Movie.collection_id.in_(cond["collections"]))
    if cond["no_collections"]:
        query.append_whereclause(~db.Movie.collection_id.in_(cond["no_collections"]))

    if cond["volumes"]:
        query.append_whereclause(db.Movie.volume_id.in_(cond["volumes"]))
    if cond["no_volumes"]:
        query.append_whereclause(~db.Movie.volume_id.in_(cond["no_volumes"]))

    loaned_to = []
    for per_id in cond["loaned_to"]:
        loaned_to.append(exists([db.loans_table.c.movie_id],\
                and_(db.Movie.movie_id==db.loans_table.c.movie_id, db.loans_table.c.person_id==per_id, db.loans_table.c.return_date==None)))
    if loaned_to:
        query.append_whereclause(or_(*loaned_to))

    loan_history = []
    for per_id in cond["loan_history"]:
        loan_history.append(exists([db.loans_table.c.movie_id],\
                and_(db.Movie.movie_id==db.loans_table.c.movie_id, db.loans_table.c.person_id==per_id)))
    if loan_history:
        query.append_whereclause(or_(*loan_history))

    required_tags = []
    for tag_id in cond["required_tags"]:
        required_tags.append(exists([db.MovieTag.movie_id], \
            and_(db.Movie.movie_id==db.MovieTag.movie_id, db.MovieTag.tag_id==tag_id)))
    if required_tags:
        query.append_whereclause(and_(*required_tags))

    tags = []
    for tag_id in cond["tags"]:
        tags.append(exists([db.MovieTag.movie_id], \
            and_(db.Movie.movie_id==db.MovieTag.movie_id, db.MovieTag.tag_id==tag_id)))
    if tags:
        query.append_whereclause(or_(*tags))

    no_tags = []
    for tag_id in cond["no_tags"]:
        no_tags.append(~exists([db.MovieTag.movie_id], \
            and_(db.Movie.movie_id==db.MovieTag.movie_id, db.MovieTag.tag_id==tag_id)))
    if no_tags:
        query.append_whereclause(and_(*no_tags))

    for field in cond["equals_n"]:
        values = [ db.movies_table.columns[field]!=value for value in cond["equals_n"][field] ]
        query.append_whereclause(and_(*values))

    for field in cond["startswith_n"]:
        values = [ not_(db.movies_table.columns[field].startswith(value)) for value in cond["startswith_n"][field] ]
        query.append_whereclause(and_(*values))

    for field in cond["like_n"]:
        values = [ not_(db.movies_table.columns[field].like(value)) for value in cond["like_n"][field] ]
        query.append_whereclause(and_(*values))

    for field in cond["ilike_n"]:
        values = [ not_(db.movies_table.columns[field].ilike(value)) for value in cond["ilike_n"][field] ]
        query.append_whereclause(and_(*values))

    for field in cond["contains_n"]: # XXX: it's not the SQLAlchemy's .contains() i.e. not for one-to-many or many-to-many collections
        values = [ not_(db.movies_table.columns[field].like('%'+value+'%')) for value in cond["contains_n"][field] ]
        query.append_whereclause(and_(*values))

    for field in cond["equals"]:
        values = [ db.movies_table.columns[field]==value for value in cond["equals"][field] ]
        query.append_whereclause(or_(*values))

    for field in cond["startswith"]:
        values = [ db.movies_table.columns[field].startswith(value) for value in cond["startswith"][field] ]
        query.append_whereclause(or_(*values))

    for field in cond["like"]:
        values = [ db.movies_table.columns[field].like(value) for value in cond["like"][field] ]
        query.append_whereclause(or_(*values))

    for field in cond["ilike"]:
        values = [ db.movies_table.columns[field].ilike(value) for value in cond["ilike"][field] ]
        query.append_whereclause(or_(*values))

    for field in cond["contains"]: # XXX: it's not the SQLAlchemy's .contains() i.e. not for one-to-many or many-to-many collections
        values = [ db.movies_table.columns[field].like('%'+value+'%') for value in cond["contains"][field] ]
        query.append_whereclause(or_(*values))

    # sorting
    for rule in cond["sort_by"]:
        if rule.endswith(" DESC"):
            reverse = True
            column = rule.replace(" DESC", '')
        else:
            column = rule.replace(" ASC", '') # note that " ASC" is optional
            reverse = False

        table = 'movies'
        tmp = column.split('.')
        if len(tmp) > 1:
            table = tmp[0]
            column = tmp[1]

        if reverse:
            query.append_order_by(desc(db.metadata.tables[table].columns[column]))
        else:
            query.append_order_by(asc(db.metadata.tables[table].columns[column]))

    log.debug(query.compile())
    return query #}}}

# MOVIE LOAN related functions --------------------------------{{{
def loan_movie(gsql, movie_id, person_id, whole_collection=False):
    """loans a movie, movie's volume and optionally movie's collection"""

    session = gsql.Session() # create new session

    person = session.query(db.Person).filter_by(person_id=person_id).first()
    if not person:
        log.warn("loan_movie: person doesn't exist")
        return False
    movie = session.query(db.Movie).filter_by(movie_id=movie_id).first()
    if not movie:
        log.warn("loan_movie: wrong movie_id")
        return False

    loan = db.Loan()
    loan.person = person
    loan.movie = movie

    if whole_collection:
        loan.collection = movie.collection
        movie.collection.loaned = True
        for m in movie.collection.movies:
            if m.loaned:
                log.warn("collection contains loaned movie (%s), cannot proceed", m.number)
                session.rollback()
                return -1
            m.loaned = True
            session.add(m)
        session.add(movie.collection)

    if movie.volume:
        loan.volume = movie.volume
        movie.volume.loaned = True
        for m in movie.volume.movies:
            m.loaned = True
            session.add(m)
        session.add(movie.volume)

    movie.loaned = True
    session.add(movie)
    session.add(loan)

    try:
        session.commit()
    except Exception, e:
        session.rollback()
        log.error(str(e))
        return False
    return True

def loan_return(gsql, movie_id):
    """marks movie, movie's volume and movie's collection as returned"""

    session = gsql.Session() # create new session

    loan = session.query(db.Loan).filter_by(movie_id=movie_id, return_date=None).first()

    if loan is None:
        movie = session.query(db.Movie).filter_by(movie_id=movie_id).first()
        if not movie:
            log.warn("Cannot find movie: %s", movie_id)
            return False
        # lets check if whole colletion was loaned
        elif movie.collection and movie.collection.loaned:
            loan = session.query(db.Loan).filter_by(collection_id=movie.collection_id, return_date=None).first()
            if not loan:
                log.error("Collection is marked as loaned but there's no loan data")
                return False
        elif movie.volume and movie.volume.loaned:
            loan = session.query(db.Loan).filter_by(volume_id=movie.volume_id, return_date=None).first()
        else:
            log.error("Cannot find loan data (movie_id:%s)", movie_id)
            return False

    if loan.collection:
        loan.collection.loaned = False
        for m in loan.collection.movies:
            m.loaned = False
            session.add(m)
        session.add(loan.collection)
    elif loan.volume:
        loan.volume.loaned = False
        for m in loan.volume.movies:
            m.loaned = False
            session.add(m)
        session.add(loan.volume)
    else:
        loan.movie.loaned = False
        session.add(loan.movie)
    loan.return_date = func.current_date()
    session.add(loan)

    try:
        session.commit()
    except Exception, e:
        session.rollback()
        log.error(str(e))
        return False
    return True

def get_loan_info(gsql, movie_id, volume_id=None, collection_id=None):
    """Returns current collection/volume/movie loan data"""

    movie = gsql.session.query(db.Movie).filter_by(movie_id=movie_id).first()
    if movie is None:
        return False

    # fix or add volume/collection data:
    if movie.collection_id is not None:
        collection_id = movie.collection_id
    if movie.volume_id is not None:
        volume_id = movie.volume_id

    if collection_id > 0 and volume_id > 0:
        return gsql.session.query(db.Loan).filter(and_(db.Loan.return_date==None,
                                                              or_(db.Loan.collection_id==collection_id,
                                                                  db.Loan.volume_id==volume_id,
                                                                  db.Loan.movie_id==movie_id))).first()
    elif collection_id > 0:
        return gsql.session.query(db.Loan).filter(and_(db.Loan.return_date==None,
                                                              or_(db.Loan.collection_id==collection_id,
                                                                  db.Loan.movie_id==movie_id))
                                                        ).first()
    elif volume_id > 0:
        return gsql.session.query(db.Loan).filter(and_(db.Loan.return_date==None,
                                                              or_(db.Loan.volume_id==volume_id,
                                                                  db.Loan.movie_id==movie_id),
                                                        )).first()
    else:
        return gsql.session.query(db.Loan).filter(db.Loan.movie_id==movie_id).filter(db.Loan.return_date==None).first()

def get_loan_history(gsql, movie_id, volume_id=None, collection_id=None):
    """Returns collection/volume/movie loan history"""

    if collection_id > 0 and volume_id > 0:
        return gsql.session.query(db.Loan).filter(and_(db.Loan.return_date!=None,
                                                          or_(db.Loan.collection_id==collection_id,
                                                              db.Loan.volume_id==volume_id,
                                                              db.Loan.movie_id==movie_id)
                                                    )).all()
    elif collection_id > 0:
        return gsql.session.query(db.Loan).filter(and_(db.Loan.return_date!=None,
                                                              or_(db.Loan.collection_id==collection_id,
                                                                  db.Loan.movie_id==movie_id))
                                                        ).all()
    elif volume_id > 0:
        return gsql.session.query(db.Loan).filter(and_(db.Loan.return_date!=None,
                                                              or_(db.Loan.volume_id==volume_id,
                                                                  db.Loan.movie_id==movie_id),
                                                        )).all()
    else:
        return gsql.session.query(db.Loan).filter(db.Loan.movie_id==movie_id).filter(db.Loan.return_date!=None).all()

def save_conditions(gsql, name, cond):
    session = gsql.Session(bind=gsql.session.bind)
    #session.bind = gsql.session.bind
    filter_ = session.query(db.Filter).filter_by(name=name).first()
    if filter_:
        filter_.conditions = cond
    else:
        filter_ = db.Filter(name, cond)
    session.add(filter_)
    try:
        session.commit()
    except Exception, e:
        session.rollback()
        log.warn(str(e))
        return False
    return True

def load_conditions(gsql, name):
    filter_ = gsql.session.query(db.Filter).filter_by(name=name).first()
    if filter_:
        return filter_.conditions
    else:
        log.warn("Cannot find search conditions: %s", name)
        return None
#}}}
