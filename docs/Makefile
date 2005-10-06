LANGUAGES = en pl pt
.PHONY: man clean $(LANGUAGES) 


all: man
#man: $(LANGUAGES)
man: $(LANGUAGES)
	for dir in $(LANGUAGES); do \
	          $(MAKE) -C $$dir man; \
	done
clean: $(LANGUAGES)
	for dir in $(LANGUAGES); do \
	          $(MAKE) -C $$dir clean; \
	done
install:
	for dir in $(LANGUAGES); do \
	          $(MAKE) -C $$dir install; \
	done
