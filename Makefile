# Griffith makefile

# (c) 2005 Vasco Nunes
#

# $Id$

PACKAGE=griffith
LANGUAGES= bg cs de es fr pl pt
VERSION=$(shell grep "^pversion" lib/version.py | cut -d \"  -f 2)

.PHONY: help clean freshmeat gnomefiles install

INSTALL ?= install
MAKE ?= make
RM ?= rm
MSGFMT ?= msgfmt
MSGMERGE ?= msgmerge
XGETTEXT ?= xgettext
FIND ?= find

PREFIX = $(DESTDIR)/usr
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share/griffith
LIBDIR = $(DATADIR)/lib
IMAGESDIR = $(DATADIR)/images
GLADEDIR = $(DATADIR)/glade
PLUGINSDIR = $(DATADIR)/plugins
MOVIEPLUGINSDIR = $(PLUGINSDIR)/movie
EXPORTPLUGINSDIR = $(PLUGINSDIR)/export
TPLDIR = $(DATADIR)/export_templates
APPLICATIONSDIR = $(PREFIX)/share/applications
ICONDIR = $(PREFIX)/share/pixmaps
LOCALEDIR = $(PREFIX)/share/locale

TEMPLATES= $(shell cd data/export_templates >/dev/null; $(FIND) . -maxdepth 1 -mindepth 1 -type d -name "[^\.svn]*" -print)

make: help

install: uninstall
	@echo
	@echo "installing griffith"
	@echo "^^^^^^^^^^^^^^^^^^^"
	$(INSTALL) -m 755 -d $(BINDIR) $(DATADIR) $(LIBDIR) $(PLUGINSDIR) $(MOVIEPLUGINSDIR) \
		$(EXPORTPLUGINSDIR) $(FONTSDIR) $(APPLICATIONSDIR) $(ICONDIR) $(TPLDIR) \
		$(IMAGESDIR) $(GLADEDIR)
	$(INSTALL) -m 755 griffith $(LIBDIR)
	$(INSTALL) -m 644 lib/*.py $(LIBDIR)
	$(INSTALL) -m 644 lib/plugins/movie/*.py $(MOVIEPLUGINSDIR)
	$(INSTALL) -m 644 lib/plugins/export/*.py $(EXPORTPLUGINSDIR)
	$(INSTALL) -m 644 glade/*.glade $(GLADEDIR)
	$(INSTALL) -m 644 glade/*.png $(GLADEDIR)
	$(INSTALL) -m 644 images/*.png $(IMAGESDIR)
	$(INSTALL) -m 644 images/griffith.png $(ICONDIR)
	$(INSTALL) -m 644 images/griffith.xpm $(ICONDIR)
	$(INSTALL) -m 644 data/griffith.desktop $(APPLICATIONSDIR)
	
	# installing language files
	for lang in $(LANGUAGES); do \
		${INSTALL} -m 755 -d $(LOCALEDIR)/$$lang/LC_MESSAGES; \
		$(INSTALL) -m 644 i18n/$$lang/LC_MESSAGES/*.mo $(LOCALEDIR)/$$lang/LC_MESSAGES; \
	done
	
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
	@echo
	@echo "uninstalling griffith"
	@echo "^^^^^^^^^^^^^^^^^^^^^"
	${RM} -r $(TPLDIR)
	${RM} -r $(MOVIEPLUGINSDIR)
	${RM} -r $(EXPORTPLUGINSDIR)
	${RM} -r $(PLUGINSDIR)
	${RM} -r $(LIBDIR)
	${RM} -r $(IMAGESDIR)
	${RM} -r $(GLADEDIR)
	${RM} -r $(DATADIR)
	${RM} -r $(ICONDIR)/griffith.png
	${RM} -r $(ICONDIR)/griffith.xpm
	${RM} -r $(APPLICATIONSDIR)/griffith.desktop
	for lang in $(LANGUAGES); do \
		${RM} -r $(LOCALEDIR)/$$lang/LC_MESSAGES/griffith.mo; \
	done
	${RM} -r $(BINDIR)/griffith
	$(MAKE) -C docs uninstall
	
clean:
	${RM} *.pyc *.bak po/*.~ glade/*~ glade/*.bak lib/*.pyc *~ lib/*~ lib/plugins/movie/*~ lib/plugins/export/*~
	
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
	@tar --exclude=*.svn* --exclude=*.tar* --exclude=debian -cf griffith.tar ./
	@mkdir $(PACKAGE)-$(VERSION)
	@tar -xf griffith.tar -C $(PACKAGE)-$(VERSION)
	@${RM} griffith.tar
	@tar -czf $(PACKAGE)-$(VERSION).tar.gz $(PACKAGE)-$(VERSION) && echo File ./$(PACKAGE)-$(VERSION).tar.gz generated successfully
	@${RM} -r $(PACKAGE)-$(VERSION)

package:
	@echo "Remember to update the debian/changelog file!"
	dpkg-buildpackage -rfakeroot

lint:
	pylint --enable-basic=n --indent-string='\t' griffith lib/*.py
