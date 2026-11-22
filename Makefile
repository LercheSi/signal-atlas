PYTHON ?= .venv/bin/python

.PHONY: check
check:
	$(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) -m ruff check tools tests
	$(PYTHON) -m ruff format --check tools tests
	$(PYTHON) -m mypy tools tests
	git diff --check
