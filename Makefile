.PHONY: install uninstall purge validate

install:
	./install.sh

uninstall:
	./uninstall.sh

purge:
	./uninstall.sh --purge

validate:
	./loom validate
