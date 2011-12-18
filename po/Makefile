# $Id$
INSTALL ?= install

PYFILES = ../griffith $(wildcard ../lib/*.py ../lib/db/*.py ../lib/plugins/movie/*.py ../lib/plugins/export/*.py ../lib/plugins/imp/*.py) 
GLADEFILES = $(wildcard ../glade/*.glade)
POFILES = $(wildcard *.po)

GLADEHFILES := $(GLADEFILES:.glade=.glade.h)

help:
	@echo "USAGE:"
	@echo "make update - updates messages.pot and .po files"
	@echo "make dist   - creates .mo files in ../i18n dir"
	@echo "make pl.po  - updates pl.po file OR creates new one"
	@echo "              (replace 'pl' with your language code)"

%.h: %
	intltool-extract --type="gettext/glade" $*

messages.pot: $(GLADEHFILES)
	xgettext -k_ -kN_ --language=Python -o messages.pot $(PYFILES) $(GLADEHFILES) --from-code=utf-8

%.po: messages.pot
	@if test -f $@; then \
		echo -n "Updating '$*' language ";\
		msgmerge -U $@ messages.pot;\
	else \
		msginit -l $*.UTF8 -o $@; \
	fi

%.mo: %.po
	for pofile in $(patsubst ../i18n/%/LC_MESSAGES/griffith.mo,%.po,$@); do \
		${INSTALL} -m 755 -d $(subst griffith.mo,,$@);\
		msgconv -t UTF-8 $${pofile} -o $${pofile}_utf8;\
		msgfmt $${pofile}_utf8 -o $@;\
		rm $${pofile}_utf8;\
	done

update: $(POFILES)
dist: $(POFILES:%.po=../i18n/%/LC_MESSAGES/griffith.mo)

clean:
	$(RM) $(GLADEHFILES)
	$(RM) $(POFILES:%.po=../i18n/%/LC_MESSAGES/griffith.mo)
	$(RM) messages.pot
	$(RM) *~

.PHONY: update dist
