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

fetch-sample:
	@if [ -n "$$APCA_API_KEY_ID" ] && [ -n "$$APCA_API_SECRET_KEY" ]; then \
		. .venv/bin/activate && python scripts/fetch_prices_alpaca.py -symbols AAPL,MSFT -start 2024-01-02 -end 2024-04-30 -timeframe 1Day -sector-map sector_map.json ; \
		. .venv/bin/activate && python scripts/fetch_news_alpaca.py -symbols AAPL,MSFT -start 2024-01-02 -end 2024-04-30 -limit 1000 ; \
	else \
		. .venv/bin/activate && python scripts/generate_synthetic.py ; \
	fi

run-all:
	. .venv/bin/activate && jupyter nbconvert --to html --no-input notebooks/*.ipynb


