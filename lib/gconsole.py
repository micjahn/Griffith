# -*- coding: ISO-8859-1 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes
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

from gettext import gettext as _
import getopt
import sys
import gutils

def check_args(self):
	if len(sys.argv)>1:
		try:
			opts, args = getopt.getopt(sys.argv[1:], 'hDCo:t:d:c:y:s:',
				('help', 'debug', 'sqlecho', 'clean', 'check-dep', 'fix-db',
					'original_title=', 'title=', 'director=', 'cast=', 'year=',
					'sort=', 'seen=', 'loaned=', 'number=', 'runtime=',
					'rating='))
		except getopt.GetoptError:
			# print help information and exit:
			con_usage()
			sys.exit(2)

		sort = None
		where = {}
		for o, a in opts:
			if o in ('-h', '--help'):
				con_usage()
				sys.exit()
			elif o in ('-D', '--debug'):
				self.debug.set_debug()
			elif o in ('-C', '--clean'):
				gutils.clean_posters_dir(self)
				sys.exit()
			elif o == '--check-dep':
				check_dependencies()
				sys.exit()
			elif o == '--fix-db':
				self.db.fix_old_data()
			elif o == '--sqlecho':
				self.db.metadata.engine.echo = True
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
		if i in ('seen', 'loaned'):	# force boolean
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

	(missing, extra) = gutils.missing_dependencies()

	def __print_missing(modules):
		for i in missing:
			tmp = None
			if ostype is not None:
				if ostype == 'debian' and i.has_key('debian'):
					tmp = "%s package is missing" % i['debian']
					if i.has_key('debian_version') and i['debian_version'] is not None:
						tmp += "\n\tminimum required version: %s" % i['debian_version']
			if tmp is None:
				tmp = "%s module is missing" % i['module']
				if i.has_key('module_version') and i['module_version'] is not None:
					tmp += "\n\tminimum required version: %s" % i['module_version']
				if i.has_key('module_url'):
					tmp += "\n\tURL: %s" % i['module_url']
			print tmp

	if missing:
		print 'Dependencies missing:'
		print '^^^^^^^^^^^^^^^^^^^^^'
		__print_missing(missing)
	if extra:
		print '\nOptional dependencies missing:'
		print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
		__print_missing(extra)

def con_usage():
	print "USAGE:", sys.argv[0], "[OPTIONS] [HOMEDIR]"
	print "\nHOMEDIR is optional home directory (if different than ~/.griffith)"
	print "\nOPTION:"
	print "-h, --help\tprints this screen"
	print "-D, --debug\trun with more debug info"
	print "-C, --clean\tfind and delete orphan files in posters directory"
	print "--check-dep\tcheck dependencies"
	print "--fix-db\tfix old database"
	print "--sqlecho\tprint SQL queries"
	print "\n printing movie list:"
	print "-c <expr>, --cast=<expr>"
	print "-d <expr>, --director=<expr>"
	print "-o <expr>, --original_title=<expr>"
	print "-t <expr>, --title=<expr>"
	print "-y <number>, --year=<number>"
	print "-s <columns>, --sort=<columns>"

