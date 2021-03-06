# Griffith

Griffith is a film collection manager, released under the GNU/GPL License.

Please see the file COPYING for licensing and warranty information.
The latest version of this software is available at the following URL:
https://github.com/micjahn/Griffith

## System Requirements

| Name                                                     | Minimum version | URL                                            | NOTE                                                  |
|----------------------------------------------------------|-----------------|------------------------------------------------|-------------------------------------------------------|
| Python                                                   | 2.5 or higher   | https://www.python.org                         |                                                       |
| GTK+                                                     | tested on 2.8.6 | https://www.gtk.org                            |                                                       |
| PyGTK (with glade3)                                      | 2.6.8           | https://pygobject.readthedocs.io               |                                                       |
| SQLAlchemy                                               | 0.5             | https://www.sqlalchemy.org/                    |                                                       |
| pysqlite2                                                | 2               | https://github.com/ghaering/pysqlite           | Python 2.5's sqlite3 module will be used if available |
| PIL                                                      |                 | http://www.pythonware.com/products/pil/        |                                                       |
| ReportLab                                                | 1.19            | https://www.reportlab.com/                     |                                                       |
| PostgreSQL support (optional): Psycopg2                  | 2               | http://initd.org/psycopg/docs/                 |                                                       |
| MySQL support: MySQLDb                                   |                 | https://sourceforge.net/projects/mysql-python/ |                                                       |
| Encoding detection of imported CSV file support: chardet |                 | https://github.com/chardet/chardet             |                                                       |
| Gtkspell: python-gnome-extras                            |                 |                                                |                                                       |
| Covers and reports support: PDF reader                   |                 |                                                |                                                       |
|                                                          |                 |                                                |                                                       |
## To check dependencies

    $ ./griffith --check-dep

## To show detected Python modules versions:

    $ ./griffith --show-dep

Windows installer includes all the needed requirements.
A GTK+ runtime is not necessary when using this installer.


## External databases

You need to prepare a new database and a new user by yourself

### PostgreSQL


	CREATE USER griffith UNENCRYPTED PASSWORD 'gRiFiTh' NOCREATEDB NOCREATEUSER;
	CREATE DATABASE griffith WITH OWNER = griffith ENCODING = 'UNICODE';
	GRANT ALL ON DATABASE griffith TO griffith;

### MySQL

	CREATE DATABASE `griffith` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
	CREATE USER 'griffith'@'localhost' IDENTIFIED BY 'gRiFiTh';
	CREATE USER 'griffith'@'%' IDENTIFIED BY 'gRiFiTh';
	GRANT ALL ON `griffith` . * TO 'griffith'@'localhost';
	GRANT ALL ON `griffith` . * TO 'griffith'@'%';

### Microsoft SQL Server

	CREATE DATABASE griffith
	EXEC sp_addlogin @loginame='griffith', @passwd='gRiFiTh', @defdb='griffith'
	GO
	USE griffith
	EXEC sp_changedbowner @loginame='griffith'


## Installation

See INSTALL file

## Reporting Bugs

If you want to help or report any bugs founded please visit:
  - https://github.com/micjahn/Griffith/issues/new

## TODO

See TODO file

## About the Authors

See AUTHORS file
