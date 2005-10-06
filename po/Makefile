GetTextFrom = ../griffith ../lib/*.py ../glade/exporthtml.glade.h ../glade/griffith.glade.h ../lib/plugins/movie/*.py ../lib/plugins/export/*.py
GladeFiles = ../glade/griffith.glade ../glade/exporthtml.glade
.PHONY: dist update


all: update dist

dist:
	@echo
	@echo Making all .mo files...
	@for FILE in *.po; do \
		msgconv -t UTF-8 $$FILE -o $$FILE.utf8; \
		msgfmt $$FILE.utf8 -o ../i18n/$${FILE%.po}/LC_MESSAGES/griffith.mo &&\
		echo Created file ../i18n/$${FILE%.po}/LC_MESSAGES/griffith.mo;\
		rm $$FILE.utf8; \
	done

update:
	@echo
	@echo Extracting messages from source files...
	@echo
	@for FILE in $(GladeFiles); do \
		intltool-extract --type="gettext/glade" $$FILE; \
	done
	@echo
	@echo Updating messages.pot file...
	xgettext -k_ -kN_ --language=Python -o messages.pot $(GetTextFrom) --from-code=utf-8
	@echo
	@echo Updating all .po files...
	@for FILE in *.po; do \
		echo -n "Updating '$$FILE' translation";\
		mv $$FILE $$FILE.old;\
		msgmerge $$FILE.old messages.pot > $$FILE;\
		rm $$FILE.old;\
	done
