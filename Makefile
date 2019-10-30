PYLINT = pylint
PYTHONFILES := $(wildcard **/*.py)
pylint: $(patsubst %.py,%.pylint,$(PYTHONFILES))

%.pylint:
	$(PYLINT) $*.py
