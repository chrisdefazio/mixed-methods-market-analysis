# CURSOR SPEC.MD — Mixed‑Methods Market Analysis (Research Specialist Portfolio Project)

> **Use this SPEC as the single source of truth.** Cursor should execute the steps below to scaffold, implement, and polish the repo. Follow imperative instructions and acceptance criteria exactly.

---

## Repo

* **Name:** `mixed-methods-market-analysis`
* **License:** MIT
* **Default Branch:** `main`
* **Min Python:** 3.10

---

## Project Goals

1. **Quantitative methods:** descriptives, **ANOVA**, **OLS regression**, **PCA** (multivariate).
2. **Qualitative methods:** term frequencies, lightweight topic modeling (**NMF**) and a simple hand‑coding rubric.
3. **Mixed‑methods synthesis:** integrate quant + qual into a short, plain‑language **executive summary** with figures.
4. **Reproducibility & rigor:** numbered notebooks, clear codebook, pinned requirements, deterministic seeds, tidy file tree.
5. **Alpaca integration:** use `alpaca-py` (paid tier) for both **market data** (prices, volumes, sectors) and **market news** (qualitative text).

---

## File Tree

```
.
├─ README.md
├─ LICENSE
├─ CITATION.cff
├─ .gitignore
├─ .env.example
├─ pyproject.toml
├─ requirements.txt
├─ Makefile
├─ .pre-commit-config.yaml
├─ src/
│  ├─ __init__.py
│  ├─ utils.py
│  ├─ features.py
│  └─ plot.py
├─ data/
│  ├─ raw/
│  │  ├─ prices.csv
│  │  ├─ returns.csv
│  │  └─ headlines.csv
│  └─ processed/
│     └─ merged.csv
├─ notebooks/
│  ├─ 01_data_preparation.ipynb
│  ├─ 02_quantitative_analysis.ipynb
│  ├─ 03_qualitative_analysis.ipynb
│  └─ 04_report_figures.ipynb
├─ reports/
│  ├─ report_template.md
│  └─ figures/
│     └─ (generated images)
├─ scripts/
│  ├─ fetch_prices_alpaca.py
│  └─ fetch_news_alpaca.py
├─ tests/
│  ├─ __init__.py
│  └─ test_utils.py
```

---

## Implementation Instructions

1. **Initialize project**

   * Create the file tree above.
   * Add MIT license and minimal CITATION.cff (author: *Chris DeFazio*, year 2025, title = repo name).
   * Write README.md with purpose, quickstart, data schema, notebook order, and Alpaca setup.

2. **Environment & Tooling**

   * Pin dependencies: `alpaca-py`, `pandas`, `numpy`, `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`, `plotly`, `jupyter`, `python-dotenv`, `requests`, `pre-commit`, `ruff`, `black`, `isort`.
   * Pre-commit hooks: ruff, black, isort, end-of-file-fixer, trailing-whitespace.
   * .gitignore: exclude processed data, .env,SPEC.md, .venv, ipynb checkpoints.
   * .env.example: `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`, `APCA_API_BASE_URL=https://data.alpaca.markets`.
   * Makefile targets: install, lint, fmt, precommit, fetch-sample (Alpaca if keys, synthetic fallback), run-all (execute notebooks).

3. **Data Schema**

   * prices.csv: date, ticker, sector, close, volume, volatility.
   * returns.csv: date, ticker, return.
   * headlines.csv: date, symbol, headline, source?, created\_at?.
   * merged.csv: merged dataset with sentiment\_score.

4. **Alpaca Scripts**

   * fetch\_prices\_alpaca.py: fetch OHLCV, compute returns.
   * fetch\_news\_alpaca.py: fetch Alpaca news, dedupe, normalize.
   * Use .env keys. Add retry logic for rate limits.

5. **src Package**

   * utils.py: loaders, validators, seed.
   * features.py: compute returns, merge, sentiment scoring, scaling.
   * plot.py: matplotlib/plotly helpers.

6. **Notebooks**

   * 01: data prep, merge, fallback to synthetic if needed.
   * 02: descriptives, ANOVA, regression, PCA.
   * 03: qualitative text analysis from Alpaca news.
   * 04: report figures.

7. **Reports**

   * report\_template.md: context, methods, results, implications, limitations, next steps.

8. **Tests**

   * Mock Alpaca JSON ingestion.
   * Schema validation.

---

## Acceptance Criteria

* `make install && make fetch-sample && make run-all` runs clean.
* If keys present, data populated from Alpaca; else synthetic fallback.
* ≥3 figures in reports/figures.
* report\_template.md includes placeholders + figure refs.
* linting and formatting pass.
* pytest passes.
* README explains Alpaca config.

---

## Stretch Goals

* Two-way ANOVA.
* Panel regression with fixed effects.
* Sentiment classifier on Alpaca news.
* Streamlit dashboard.

---

## Guardrails

* Do not commit keys.
* Respect rate limits.
* No seaborn.
* Only specified dependencies.

---

## Milestones

* Day 1–2: Scaffold + scripts + fallback.
* Day 3–4: Quant analysis.
* Day 5: Qual analysis + report.

---

**Owner:** Chris DeFazio | Last updated: Aug 2025
