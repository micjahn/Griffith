# Griffith makefile

# (c) 2005 Vasco Nunes
#

# $Id$


PACKAGE=griffith
VERSION=$(shell grep "^pversion" lib/version.py | cut -d \"  -f 2)

.PHONY: help clean freshmeat gnomefiles install

PYTHON ?= python2.3
INSTALL ?= install
MAKE ?= make
RM ?= rm
MSGFMT ?= msgfmt
MSGMERGE ?= msgmerge
XGETTEXT ?= xgettext
FIND ?= find

PREFIX = $(DESTDIR)/usr
LIBDIR = $(PREFIX)/lib/griffith
PLUGINSDIR = $(PREFIX)/lib/griffith/plugins
MOVIEPLUGINSDIR = $(PREFIX)/lib/griffith/plugins/movie
EXPORTPLUGINSDIR = $(PREFIX)/lib/griffith/plugins/export
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share/griffith
TPLDIR = $(PREFIX)/share/griffith/export_templates
#FONTSDIR = $(PREFIX)/share/griffith/fonts
APPLICATIONSDIR = $(PREFIX)/share/applications
ICONDIR = $(PREFIX)/share/pixmaps
LOCALEDIR = $(PREFIX)/share/locale

PYFILES := $(shell $(FIND) . -name "*.py" -print)
TEMPLATES= $(shell cd data/export_templates; $(FIND) . -maxdepth 1 -mindepth 1 -type d -name "[^CVS]*" -print)

make: help

install: uninstall
	$(INSTALL) -m 755 -d $(BINDIR) $(LIBDIR) $(PLUGINSDIR) $(MOVIEPLUGINSDIR) \
		$(EXPORTPLUGINSDIR) $(DATADIR) $(FONTSDIR) $(APPLICATIONSDIR) $(ICONDIR) $(TPLDIR)
	$(INSTALL) -m 755 griffith $(LIBDIR)
	$(INSTALL) -m 644 lib/*.py $(LIBDIR)
	$(INSTALL) -m 644 lib/plugins/movie/*.py $(MOVIEPLUGINSDIR)
	$(INSTALL) -m 644 lib/plugins/export/*.py $(EXPORTPLUGINSDIR)
	$(INSTALL) -m 644 glade/*.glade $(DATADIR)
	$(INSTALL) -m 644 images/*.png $(DATADIR)
	$(INSTALL) -m 644 images/griffith.png $(ICONDIR)
	$(INSTALL) -m 644 images/griffith.xpm $(ICONDIR)
	$(INSTALL) -m 644 data/griffith.desktop $(APPLICATIONSDIR)
	#$(INSTALL) -m 644 fonts/*.* $(FONTSDIR)
	$(INSTALL) -m 755 -d $(LOCALEDIR)/pt/LC_MESSAGES
	$(INSTALL) -m 755 -d $(LOCALEDIR)/pl/LC_MESSAGES
	$(INSTALL) -m 755 -d $(LOCALEDIR)/de/LC_MESSAGES
	$(INSTALL) -m 755 -d $(LOCALEDIR)/bg/LC_MESSAGES
	$(INSTALL) -m 755 -d $(LOCALEDIR)/cs/LC_MESSAGES
	$(INSTALL) -m 755 -d $(LOCALEDIR)/es/LC_MESSAGES
	$(INSTALL) -m 644 i18n/pt/LC_MESSAGES/*.mo $(LOCALEDIR)/pt/LC_MESSAGES
	$(INSTALL) -m 644 i18n/pl/LC_MESSAGES/*.mo $(LOCALEDIR)/pl/LC_MESSAGES
	$(INSTALL) -m 644 i18n/de/LC_MESSAGES/*.mo $(LOCALEDIR)/de/LC_MESSAGES
	$(INSTALL) -m 644 i18n/bg/LC_MESSAGES/*.mo $(LOCALEDIR)/bg/LC_MESSAGES
	$(INSTALL) -m 644 i18n/cs/LC_MESSAGES/*.mo $(LOCALEDIR)/cs/LC_MESSAGES
	$(INSTALL) -m 644 i18n/es/LC_MESSAGES/*.mo $(LOCALEDIR)/es/LC_MESSAGES

	# installing export templates:
	for dir in $(TEMPLATES); do \
		${INSTALL} -m 755 -d  ${TPLDIR}/$$dir; \
		${FIND} data/export_templates/$$dir -maxdepth 1 -type f \
			-exec ${INSTALL} -m 644 '{}' ${TPLDIR}/$$dir \;; \
	done
	
	if test -f $(PREFIX)/bin/griffith; then ${RM} $(PREFIX)/bin/griffith; fi	

	ln -s $(LIBDIR)/griffith $(BINDIR)/griffith
	chmod +x $(BINDIR)/griffith
	$(MAKE) -C docs install
	
uninstall:
	${RM} -rf $(MOVIEPLUGINSDIR)
	${RM} -rf $(EXPORTPLUGINSDIR)
	${RM} -rf $(PLUGINSDIR)
	${RM} -rf $(LIBDIR)
	${RM} -rf $(CSSDIR)
	#${RM} -rf $(FONTSDIR)
	${RM} -rf $(DATADIR)
	${RM} -rf $(ICONDIR)/griffith.ong
	${RM} -rf $(APPLICATIONSDIR)/griffith.desktop
	${RM} -rf $(LOCALEDIR)/pt/LC_MESSAGES/griffith.mo
	${RM} -rf $(LOCALEDIR)/pl/LC_MESSAGES/griffith.mo
	${RM} -rf $(LOCALEDIR)/de/LC_MESSAGES/griffith.mo 	
	${RM} -rf $(LOCALEDIR)/bg/LC_MESSAGES/griffith.mo
	${RM} -rf $(LOCALEDIR)/cs/LC_MESSAGES/griffith.mo
	${RM} -rf $(LOCALEDIR)/es/LC_MESSAGES/griffith.mo
	${RM} -rf $(BINDIR)/griffith
	
clean:
	${RM} -f *.pyc *.bak po/*.~ glade/*~ glade/*.bak lib/*.pyc *~ lib/*~ lib/plugins/movie/*~ lib/plugins/export/*~
	
help:
	@echo Usage:
	@echo "make		- not used"
	@echo "make clean	- delete built modules and object files"
	@echo "make install	- install binaries into the official directories"
	@echo "make uninstall	- uninstall binaries from the official directories"
	@echo "make help	- prints this help"
	@echo "make dist	- makes a distribution tarball"
	@echo "make package	- makes a Debian package"
	@echo
	
freshmeat:
	firefox http://freshmeat.net/add-release/54772/ &

gnomefiles:
	firefox http://www.gnomefiles.org/devs/newversion.php?soft_id=965 &
	
dist:
	@tar --exclude=*.svn* --exclude=*.tar* -cf griffith.tar ./
	@mkdir $(PACKAGE)-$(VERSION)
	@tar -xf griffith.tar -C $(PACKAGE)-$(VERSION)
	@${RM} griffith.tar
	@tar -czf $(PACKAGE)-$(VERSION).tar.gz $(PACKAGE)-$(VERSION) && echo File ./$(PACKAGE)-$(VERSION).tar.gz generated successfully
	@${RM} -rf $(PACKAGE)-$(VERSION)

package:
	@echo "Remember to update the debian/changelog file!"
	dpkg-buildpackage -rfakeroot

lint:
	pylint --enable-basic=n --indent-string='\t' griffith lib/*.py
