# -*- coding: utf-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2008 Vasco Nunes, Piotr Ożarowski

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

import getopt
import os
import sys
import gutils
import logging
log = logging.getLogger("Griffith")
from locale import getdefaultlocale

options = ('hvDCo:t:d:c:y:s:', ('help', 'debug', 'sqlecho', 'clean', 'check-dep',
    'show-dep', 'original_title=', 'title=', 'director=', 'cast=', 'year=',
    'sort=', 'seen=', 'loaned=', 'number=', 'runtime=', 'rating=', 'home=',
    'config=', 'version' ))

def check_args():
    default_lang, default_enc = getdefaultlocale()
    if not default_enc:
        default_enc = 'UTF-8'
    
    if os.name == 'nt' or os.name.startswith('win'): # win32, win64
        from win32com.shell import shellcon, shell
        home = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0), 'griffith').decode(defaultEnc)
    else:
        home = os.path.join(os.path.expanduser('~'), '.griffith').decode(default_enc)
    config = 'griffith.cfg'

    if len(sys.argv)>1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], options[0], options[1])
        except getopt.GetoptError:
            # print help information and exit:
            con_usage()
            sys.exit(2)
        
        for o, a in opts:
            if o in ('-h', '--help'):
                con_usage()
                sys.exit()
            if o in ('-v', '--version'):
                import version
                print version.pversion
                sys.exit()
            elif o in ('-D', '--debug'):
                log.setLevel(logging.DEBUG)
            elif o == '--sqlecho':
                sa_log = logging.getLogger("sqlalchemy")
                sa_log.setLevel(logging.INFO)
            elif o == '--home':
                home = a
            elif o == '--config':
                config = a
            elif o == '--check-dep':
                check_dependencies()
                sys.exit()
            elif o == '--show-dep':
                show_dependencies()
                sys.exit()
    return home, config

def check_args_with_db(self):
    if len(sys.argv)>1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], options[0], options[1])
        except getopt.GetoptError:
            # print help information and exit:
            con_usage()
            sys.exit(3)

        sort = None
        where = {}
        for o, a in opts:
            if o in ('-C', '--clean'):
                gutils.clean_posters_dir(self)
                sys.exit()
            elif o in ('-s', '--sort'):
                sort = a
            elif o in ('-o', '--original_title'):
                where['o_title'] = a
            elif o in ('-t', '--title'):
                where['title'] = a
            elif o in ('-d', '--director'):
                where['director'] = a
            elif o in ('-c', '--cast'):
                where['cast'] = a
            elif o in ('-y', '--year'):
                where['year'] = str(int(a))
            elif o == '--seen':
                where['seen'] = a
            elif o == '--loaned':
                where['loaned'] = a
            elif o == '--number':
                where['number'] = a
            elif o == '--runtime':
                where['runtime'] = a
            elif o == '--rating':
                where['rating'] = a
        if where:
            con_search_movie(self, where, sort)

def con_search_movie(self, where, sort=None):
    # for search function
    from sqlalchemy import select
    col = lambda x: self.db.Movie.c[x]
    columns = (col('number'), col('title'), col('o_title'), col('director'), col('year'))
    
    sort_columns = []
    if sort:
        for i in sort.split(','):
            if self.db.Movie.c.has_key(i):
                sort_columns.append(col(i))
    else:
        sort_columns = [col('number')]

    statement = select(columns=columns, order_by=sort_columns)

    for i in where:
        if i in ('seen', 'loaned'):    # force boolean
            if where[i].lower() in ('0', 'no', 'n'):
                where[i] = False
            else:
                where[i] = True
        if i in ('year', 'number', 'runtime', 'seen', 'loaned', 'rating'):
            statement.append_whereclause(col(i)==where[i])
        else:
            statement.append_whereclause(col(i).like('%' + where[i] + '%' ))

    movies = statement.execute().fetchall()
    if not movies:
        print _("No movie found")
    else:
        for movie in movies:
            print "\033[31;1m[%s]\033[0m\t\033[38m%s\033[0m (\033[35m%s\033[0m), %s - \033[32m%s\033[0m" % \
                (movie.number, movie.title, movie.o_title, movie.year, movie.director)
    sys.exit()

def check_dependencies():
    ostype = None
    if sys.version.rfind('Debian'):
        ostype = 'debian'

    (missing, extra) = gutils.get_dependencies()

    def __print_missing(modules):
        import string
        missing = ''
        for i in modules:
            if i['version']==False or (not isinstance(i['version'], bool) and i['version'].startswith('-')):
                tmp = None
                if ostype is not None:
                    if ostype == 'debian' and i.has_key('debian'):
                        tmp = "\n%s package" % i['debian']
                        if i.has_key('debian_req') and i['debian_req'] is not None:
                            tmp += "\n\tminimum required package version: %s" % i['debian_req']
                if tmp is None:
                    tmp = "\n%s module" % i['module']
                    if i.has_key('module_req') and i['module_req'] is not None:
                        tmp += "\n\tminimum required module version: %s" % i['module_req']
                    if i.has_key('url'):
                        tmp += "\n\tURL: %s" % i['url']
                if i['version'] is not False and i['version'].startswith('-'):
                    tmp += "\n\tavailable module version: %s" % i['version'][1:]
                if tmp is not None:
                    missing += tmp
        if missing == '':
            return None
        else:
            return missing

    tmp = __print_missing(missing)
    if tmp is not None:
        print 'Dependencies missing:'
        print '===================='
        print tmp
    tmp = __print_missing(extra)
    if tmp is not None:
        print '\n\nOptional dependencies missing:'
        print '============================='
        print tmp, "\n"

def show_dependencies():
    (missing, extra) = gutils.get_dependencies()
    for i in missing:
        print "%(module)s :: %(version)s" % i
    for i in extra:
        print "%(module)s :: %(version)s" % i

def con_usage():
    print "USAGE:", sys.argv[0], '[OPTIONS]'
    print "\nOPTIONS:"
    print "-h, --help\tprints this screen"
    print "-v, --version\tprints Griffith's version"
    print "-D, --debug\trun with more debug info"
    print "-C, --clean\tfind and delete orphan files in posters directory"
    print "--check-dep\tcheck dependencies"
    print "--show-dep\tshow dependencies"
    print "--sqlecho\tprint SQL queries"
    print "--home DIR \tset Griffith's home directory (instead of the default ~/.griffith)"
    print "\n printing movie list:"
    print "-c <expr>, --cast=<expr>"
    print "-d <expr>, --director=<expr>"
    print "-o <expr>, --original_title=<expr>"
    print "-t <expr>, --title=<expr>"
    print "-y <number>, --year=<number>"
    print "-s <columns>, --sort=<columns>"

