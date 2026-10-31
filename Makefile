PYTHON = python
MAIN = codes/main.py
MAP ?= maps/medium/03_priority_puzzle.txt


run:
	@uv run $(PYTHON) $(MAIN) $(MAP)

install:
	@uv sync

debug:
	@uv run python3 -m pdb $(MAIN)

clean:
	@rm -rf $(shell find . -type d -name "__pycache__")
	@rm -rf $(shell find . -type d -name ".mypy_cache")
	@rm -f $(shell find . -name "*.pyc")

lint:
	@uv run flake8 . --exclude=.venv
	@uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	 --disallow-untyped-defs --check-untyped-defs
