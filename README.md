# Mixed‑Methods Market Analysis

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Purpose: A research portfolio project that integrates quantitative (descriptives, ANOVA, OLS regression, PCA) and qualitative (term frequencies, NMF topic modeling, simple hand-coding rubric) methods on market data and news, with a mixed‑methods synthesis and reproducible numbered notebooks.

## Quickstart

1. Python 3.10+.
2. Create and activate a virtual environment, then install:
   - `make install`
3. Configure Alpaca API keys (optional but recommended): copy `.env.example` to `.env` and fill values.
4. Pre-commit hooks: installed by `make install`. Run them anytime with `make precommit`.
5. Data sample: `make fetch-sample` (placeholder for now; will fetch from Alpaca if keys are present, otherwise generate synthetic data).
6. Run notebooks: `make run-all` (placeholder for now; will execute notebooks in order).

## Alpaca Setup

Set the following environment variables (e.g., in `.env`):

```
APCA_API_KEY_ID=YOUR_KEY
APCA_API_SECRET_KEY=YOUR_SECRET
APCA_API_BASE_URL=https://data.alpaca.markets
APCA_DATA_FEED=sip
APCA_ADJUSTMENT=all
```

The project will use `alpaca-py` to retrieve market OHLCV, sectors, and news.

## Data Schema

- prices.csv: `date`, `ticker`, `sector`, `close`, `volume`, `volatility`
- returns.csv: `date`, `ticker`, `return`
- headlines.csv: `date`, `symbol`, `headline`, `source?`, `created_at?`
- merged.csv: merged dataset with `sentiment_score`

## Notebook Order

1. `01_data_preparation.ipynb`
2. `02_quantitative_analysis.ipynb`
3. `03_qualitative_analysis.ipynb`
4. `04_report_figures.ipynb`

## Synthetic vs Alpaca Data

- If Alpaca keys are configured, data will be fetched from Alpaca endpoints.
- Otherwise, the workflow will fall back to synthetic sample data that matches the schemas above.

## Demo Walkthrough

Commands to reproduce end-to-end (assuming Python 3.10+):

```
make install
make fetch-sample
make run-all
make lint
pytest -q
```

Expected artifacts:
- `data/raw/prices.csv`, `data/raw/returns.csv`, `data/raw/headlines.csv`
- `data/processed/merged.csv`
- `notebooks/*.html` (converted notebooks)
- `reports/figures/*.png` (after running the figures notebook)

Success note: Acceptance steps (`make install`, `make precommit`, `make fetch-sample`, `make run-all`, `make lint`, `pytest -q`) were verified on 2025-08-19 with Python 3.11.
