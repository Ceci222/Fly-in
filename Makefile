PYTHON = python3
MAIN = main.py
MAP = maps/easy/01_linear_path.txt

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m pip install "pydantic>=2" flake8 mypy

run:
	$(PYTHON) $(MAIN) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict