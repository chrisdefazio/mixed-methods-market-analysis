# Executive Summary Template

## Context

Brief description of the market period, tickers, and news sources analyzed.

## Methods

### Quantitative

Descriptives, one-way ANOVA across sectors, OLS with HC3 SEs
(`return ~ sentiment_score + volume + volatility + C(sector)`), and PCA.

### Qualitative

Term frequencies (CountVectorizer), NMF topics (k=3–5), hand-coding rubric.

### Mixed-Methods Synthesis

Integrate statistical results with topic/sentiment evidence into a narrative.

## Results

Key findings:
- ANOVA F=__F_STAT__ (p=__P_ANOVA__).
- OLS: coef(sentiment)=__B_SENT__, HC3 SE=__SE_SENT__, p=__P_SENT__.
- PCA: PC1 var=__PC1_VAR__%, PC2 var=__PC2_VAR__%.

## Figures

- [reports/figures/figure_returns_by_sector.png](../reports/figures/figure_returns_by_sector.png)
- [reports/figures/figure_returns_vs_sentiment_bins.png](../reports/figures/figure_returns_vs_sentiment_bins.png)
- [reports/figures/figure_pca_scatter.png](../reports/figures/figure_pca_scatter.png)

## Implications

Practical implications for market participants and hypothesis alignment.

## Limitations

Sample size, time window, dictionary-based sentiment, and data coverage.

## Next Steps

Validation on longer horizons, robustness checks, expand topic modeling.
