.PHONY: all man
MANPAGES_1= griffith.1
MANPAGES_5= griffith-export-template.5
MANPAGES= $(MANPAGES_1) $(MANPAGES_5)

PREFIX= $(DESTDIR)/usr
MANDIR= $(PREFIX)/share/man
INSTALL ?= install

all: man

man: $(MANPAGES)

clean:
	$(RM) $(MANPAGES)

%.1: %.xml
	docbook2x-man $<

%.5: %.xml
	docbook2x-man $<

install: $(MANPAGES)
	$(INSTALL) -m 755 -d "$(MANDIR)/pt/man1"
	$(INSTALL) -m 755 -d "$(MANDIR)/pt/man5"
	if test -n "$(MANPAGES_1)"; then $(INSTALL) -m 644 $(MANPAGES_1) $(MANDIR)/pt/man1; fi
	if test -n "$(MANPAGES_5)"; then $(INSTALL) -m 644 $(MANPAGES_5) $(MANDIR)/pt/man5; fi

uninstall: $(MANPAGES)
	for manpage in $(MANPAGES_1); do \
		${RM} $(MANDIR)/man1/pt/$$manpage; \
	done
	for manpage in $(MANPAGES_5); do \
		${RM} $(MANDIR)/man5/pt/$$manpage; \
	done
