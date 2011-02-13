# -*- coding: UTF-8 -*-
# vim: fdm=marker

__revision__ = '$Id$'

# Copyright © 2005-2009 Vasco Nunes, Piotr Ożarowski
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

import logging
import os.path

from sqlalchemy import create_engine, or_, and_, not_, exists, asc, desc
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql.expression import Update, Delete

import db # ORM data (SQLAlchemy stuff)
from gutils import warning # TODO: get rid of this import
from gutils import get_filesystem_pagesize

log = logging.getLogger("Griffith")


class GriffithSQL(object):
    version = db.__version__
    DEFAULT_PORTS = dict(postgres=5432, mysql=3306, mssql=1433)

    def __init__(self, config, griffith_dir, fallback=True):
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
            if config.get('port', 0, section='database') == 0:
                config.set('port', GriffithSQL.DEFAULT_PORTS[config.get('type', section='database')], section='database')

        conn_params = config.to_dict(section='database')
        conn_params.update({'port': int(conn_params.get('port', 0)),
                            'engine_kwargs': {'echo': False, 'convert_unicode': False}})

        # connect to database --------------------------------------{{{
        dbinitializingsql = None
        if config.get('type', section='database') == 'sqlite':
            sqlitefile = "%s.db" % os.path.join(griffith_dir, conn_params['name'])
            if not os.path.isfile(sqlitefile):
                # for new created database this is an optimization step syncing the database page size
                # to the filesystem page size
                dbinitializingsql = 'PRAGMA page_size=' + str(get_filesystem_pagesize(sqlitefile))
            url = "sqlite:///%s" % sqlitefile
        elif config.get('type', section='database') == 'postgres':
            # sqlalchemy version check because postgres dialect is renamed in sqlalchemy>=0.6 from postgres to postgresql
            from sqlalchemy import __version__ as sqlalchemyversion
            if map(int, sqlalchemyversion[:3].split('.')) < [0, 6]:
                url = "postgres"
            else:
                url = "postgresql"
            url = url + "://%(user)s:%(passwd)s@%(host)s:%(port)d/%(name)s" % conn_params
        elif config.get('type', section='database') == 'mysql':
            conn_params['engine_kwargs']['convert_unicode'] = True
            conn_params['engine_kwargs']['pool_recycle'] = int(config.get('pool_recycle', 3600, section='database'))
            url = "mysql://%(user)s:%(passwd)s@%(host)s:%(port)d/%(name)s?charset=utf8&use_unicode=0" % conn_params
        elif config.get('type', section='database') == 'mssql':
            # use_scope_identity=0 have to be set as workaround for a sqlalchemy bug
            # but it is not guaranteed that the right identity value will be selected
            # because the select @@identity statement selects the very last id which
            # also can be a id from a trigger-insert or another user
            # sqlalchemy uses a wrong syntax. It has to select the id within the insert
            # statement: insert <table> (<columns>) values (<values>) select scope_identity()
            # (one statement !) After preparing and executing there should be a fetch
            # If it is executed as two separate statements the scope is lost after insert.
            url = "mssql://%(user)s:%(passwd)s@%(host)s:%(port)d/%(name)s?use_scope_identity=0" % conn_params
        else:
            config.set('type', 'sqlite', section='database')
            url = "sqlite:///%s.db" % os.path.join(griffith_dir, conn_params['name'])

        # try to establish a db connection
        try:
            engine = create_engine(url, **conn_params['engine_kwargs'])
            conn = engine.connect()
            if dbinitializingsql is not None:
                engine.execute(dbinitializingsql)
        except Exception, e:    # InvalidRequestError, ImportError
            log.info("MetaData: %s", e)
            if not fallback:
                raise e
            config.set('type', 'sqlite', section='database')
            warning("%s\n\n%s" % (_('Cannot connect to database.\nFalling back to SQLite.'), _('Please check debug output for more informations.')))
            url = "sqlite:///%s.db" % os.path.join(griffith_dir, conn_params['name'])
            engine = create_engine(url)
            conn = engine.connect()

        # scoped_session(...) is a workaround for unclosed sessions in the program
        # https://bugs.launchpad.net/griffith/+bug/574370
        self.Session = scoped_session(sessionmaker(bind=engine)) # create new sessions using this class
        self.engine = engine
        self.session = self.Session() # TODO: get rid of it, force developers to create new session using gsql.Session()
        #}}}

        # check if database needs an upgrade
        db.metadata.create_all(engine)
        try:
            v = self.session.query(db.Configuration).filter_by(param=u'version').first()    # returns None if table exists && param ISNULL
        except OperationalError, e:
            log.info(e)
            v = 0
        except Exception, e:
            log.error(e)
            v = 0

        if v is not None and v > 1:
            v = int(v.value)
        if v < self.version:
            from dbupgrade import upgrade_database
            if not upgrade_database(self, v, config):
                raise Exception('cannot upgrade database')
        elif v > self.version:
            log.error("database version mismatch (detected:%s; current:%s)", v, self.version)
            warning(_('This database requires newer version of Griffith.'))
            raise Exception("database version mismatch")

    def dispose(self):
        # close every session and connection so that a sqlite database file can be removed
        # otherwise it will remain opened by the current process and can't be deleted
        try:
            self.session.close()
            self.Session.close_all()
            self.engine.dispose()
            del self.session
            del self.Session
            del self.engine
        except:
            log.exception('')


def update_whereclause(query, cond): # {{{
    if cond['loaned'] is True:
        query = query.where(db.Movie.loaned == True)
    if cond['loaned'] is False:
        query = query.where(db.Movie.loaned == False)
    if cond['seen'] is True:
        query = query.where(db.Movie.seen == True)
    if cond['seen'] is False:
        query = query.where(db.Movie.seen == False)

    if cond["collections"]:
        query = query.where(db.Movie.collection_id.in_(cond["collections"]))
    if cond["no_collections"]:
        query = query.where(or_(~db.Movie.collection_id.in_(cond["no_collections"]), db.Movie.collection_id == None))

    if cond["volumes"]:
        query = query.where(db.Movie.volume_id.in_(cond["volumes"]))
    if cond["no_volumes"]:
        query = query.where(or_(~db.Movie.volume_id.in_(cond["no_volumes"]), db.Movie.volume_id == None))

    loaned_to = []
    for per_id in cond["loaned_to"]:
        loaned_to.append(exists([db.tables.loans.c.movie_id],\
                and_(db.Movie.movie_id == db.tables.loans.c.movie_id,
                     db.tables.loans.c.person_id == per_id,
                     db.tables.loans.c.return_date == None)))
    if loaned_to:
        query = query.where(or_(*loaned_to))

    loan_history = []
    for per_id in cond["loan_history"]:
        loan_history.append(exists([db.tables.loans.c.movie_id],\
                and_(db.Movie.movie_id == db.tables.loans.c.movie_id,
                     db.tables.loans.c.person_id == per_id)))
    if loan_history:
        query = query.where(or_(*loan_history))

    required_tags = []
    for tag_id in cond["required_tags"]:
        required_tags.append(exists([db.MovieTag.movie_id], \
            and_(db.Movie.movie_id == db.MovieTag.movie_id,
                 db.MovieTag.tag_id == tag_id)))
    if required_tags:
        query = query.where(and_(*required_tags))

    tags = []
    for tag_id in cond["tags"]:
        tags.append(exists([db.MovieTag.movie_id], \
            and_(db.Movie.movie_id == db.MovieTag.movie_id,
                 db.MovieTag.tag_id == tag_id)))
    if tags:
        query = query.where(or_(*tags))

    no_tags = []
    for tag_id in cond["no_tags"]:
        no_tags.append(~exists([db.MovieTag.movie_id], \
            and_(db.Movie.movie_id == db.MovieTag.movie_id,
                 db.MovieTag.tag_id == tag_id)))
    if no_tags:
        query = query.where(and_(*no_tags))

    for field in cond["equals_n"]:
        values = [db.tables.movies.columns[field] != value for value in cond["equals_n"][field]]
        query = query.where(and_(*values))

    for field in cond["startswith_n"]:
        values = [not_(db.tables.movies.columns[field].startswith(value)) for value in cond["startswith_n"][field]]
        query = query.where(and_(*values))

    for field in cond["like_n"]:
        values = [not_(db.tables.movies.columns[field].like(value)) for value in cond["like_n"][field]]
        query = query.where(and_(*values))

    for field in cond["contains_n"]: # XXX: it's not the SQLAlchemy's .contains() i.e. not for one-to-many or many-to-many collections
        values = [not_(db.tables.movies.columns[field].like('%' + value + '%')) for value in cond["contains_n"][field]]
        query = query.where(and_(*values))

    for field in cond["equals"]:
        values = [db.tables.movies.columns[field] == value for value in cond["equals"][field]]
        query = query.where(or_(*values))

    for field in cond["startswith"]:
        values = [db.tables.movies.columns[field].startswith(value) for value in cond["startswith"][field]]
        query = query.where(or_(*values))

    for field in cond["like"]:
        values = [db.tables.movies.columns[field].like(value) for value in cond["like"][field]]
        query = query.where(or_(*values))

    for field in cond["contains"]: # XXX: it's not the SQLAlchemy's .contains() i.e. not for one-to-many or many-to-many collections
        values = [db.tables.movies.columns[field].like('%' + value + '%') for value in cond["contains"][field]]
        query = query.where(or_(*values))

    # sorting
    if not isinstance(query, (Update, Delete)):
        for rule in cond.get('sort_by', []):
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
                query = query.order_by(desc(db.metadata.tables[table].columns[column]))
            else:
                query = query.order_by(asc(db.metadata.tables[table].columns[column]))

    log.debug(query)
    return query #}}}
