# -*- coding: UTF-8 -*-
# vim: fdm=marker

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

# imports
from sqlalchemy            import create_engine
from sqlalchemy.orm        import sessionmaker
from sqlalchemy.exceptions import SQLError, OperationalError
import os.path
import gettext
gettext.install('griffith', unicode=1)
import logging
log = logging.getLogger("Griffith")
import gutils
import db # ORM data (SQLAlchemy stuff)

class GriffithSQL:
    version = 3    # database format version, increase after changing data structures

    def __init__(self, config, griffith_dir, reconnect=True):
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
            url = "mysql://%s:%s@%s:%d/%s" % (
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
            log.info("MetaData: %s" % e)
            if not reconnect:
                return False
            config.set('type', 'sqlite', section='database')
            gutils.warning(self, "%s\n\n%s" % (_('Cannot connect to database.\nFalling back to SQLite.'), _('Please check debug output for more informations.')))
            url = "sqlite:///%s" % os.path.join(griffith_dir, config.get('name', 'griffith', section='database') + '.db')
            engine = create_engine(url)
            conn = engine.connect()

        # try to establish a db connection
        try:
            Session = sessionmaker(bind=engine)
            self.session = Session()
            #self.metadata.bind.connect()
        except Exception, e:
            log.info("engine connection: %s" % e)
            if not reconnect:
                return False
            gutils.error(self, _('Database connection failed.'))
            config.set('type', 'sqlite', section='database')
            url = "sqlite:///%s" % os.path.join(griffith_dir, 'griffith.db')
            engine = create_engine(url)
            Session = sessionmaker(bind=engine)
            self.session = Session()
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
            upgrade_database(self, v)
