# $Id$
.PHONY: all man
MANPAGES= griffith.1

PREFIX= $(DESTDIR)/usr
MANDIR= $(PREFIX)/share/man
INSTALL ?= install
DOC2MAN ?= docbook2x-man

all: man

man: $(MANPAGES)

clean:
	$(RM) $(MANPAGES)

%.1: %.xml
	$(DOC2MAN) --encoding iso-8859-2 $<

install: $(MANPAGES)
	$(INSTALL) -m 755 -d "$(MANDIR)/pl/man1"
	if test -n "$(MANPAGES)"; then $(INSTALL) -m 644 $(MANPAGES) $(MANDIR)/pl/man1; fi

uninstall: $(MANPAGES)
	for manpage in $(MANPAGES); do \
		${RM} $(MANDIR)/man1/pl/$$manpage; \
	done
