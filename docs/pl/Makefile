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
	rm $(MANPAGES)
install: $(MANPAGES)
	$(INSTALL) -m 755 -d "$(MANDIR)/pl/man1"
	$(INSTALL) -m 755 -d "$(MANDIR)/pl/man5"
	if test -n "$(MANPAGES_1)"; then $(INSTALL) -m 644 $(MANPAGES_1) $(MANDIR)/pl/man1; fi
	if test -n "$(MANPAGES_5)"; then $(INSTALL) -m 644 $(MANPAGES_5) $(MANDIR)/pl/man5; fi
%.1: %.xml
	docbook2x-man $<
%.5: %.xml
	docbook2x-man $<
