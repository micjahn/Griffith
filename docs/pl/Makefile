# $Id$
.PHONY: all man
MANPAGES_1= griffith.1
MANPAGES_5= griffith-export-template.5
MANPAGES= $(MANPAGES_1) $(MANPAGES_5)

PREFIX= $(DESTDIR)/usr
MANDIR= $(PREFIX)/share/man
INSTALL ?= install
DOC2MAN ?= docbook2x-man

all: man

man: $(MANPAGES)

clean:
	$(RM) $(MANPAGES)

%.1: %.xml
	$(DOC2MAN) --encoding utf8 $<

%.5: %.xml
	$(DOC2MAN) --encoding utf8 $<

install: $(MANPAGES)
	$(INSTALL) -m 755 -d "$(MANDIR)/pl/man1"
	$(INSTALL) -m 755 -d "$(MANDIR)/pl/man5"
	if test -n "$(MANPAGES_1)"; then $(INSTALL) -m 644 $(MANPAGES_1) $(MANDIR)/pl.UTF-8/man1; fi
	if test -n "$(MANPAGES_5)"; then $(INSTALL) -m 644 $(MANPAGES_5) $(MANDIR)/pl.UTF-8/man5; fi

uninstall: $(MANPAGES)
	for manpage in $(MANPAGES_1); do \
		${RM} $(MANDIR)/man1/pl/$$manpage; \
	done
	for manpage in $(MANPAGES_5); do \
		${RM} $(MANDIR)/man5/pl/$$manpage; \
	done
