PYTHON := python3

.PHONY: install lint fmt precommit fetch-sample run-all

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && pre-commit install

lint:
	. .venv/bin/activate && ruff check .

fmt:
	. .venv/bin/activate && ruff check --fix .
	. .venv/bin/activate && black .
	. .venv/bin/activate && isort .

precommit:
	. .venv/bin/activate && pre-commit run --all-files

# Placeholder: will fetch Alpaca if keys present, else synthetic fallback later
fetch-sample:
	@echo "Fetch-sample placeholder (data fetching to be implemented later)"

run-all:
	. .venv/bin/activate && jupyter nbconvert --to html --no-input notebooks/*.ipynb


