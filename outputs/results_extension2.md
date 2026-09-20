# Extension 2 — Network-based missing-data imputation

Respondent similarity for predicting item j is recomputed per item, with that item's column dropped, before selecting neighbors for any cell that uses it. Every (respondent, item) cell (n*m = 4080) is evaluated this way.

Network k-NN MAE (all 4080 cells): 0.6454
Global-mean baseline MAE: 0.6615
Mean improvement per respondent (baseline - knn): 0.0162

## Significance: respondent-level bootstrap (cells from one respondent are not independent)
95% CI for mean improvement, resampling respondents with replacement (B=5000): [-0.0099, 0.0420]
Fraction of bootstrap resamples with improvement <= 0: 0.1052
Each respondent contributes m correlated cells, so the n*m cells are not independent observations; the respondent-level bootstrap above is the valid test, and it does not clear the conventional 95% threshold. The honest reading is a small, borderline effect.

Note: Pearson correlation is already invariant to per-row additive shifts, so subtracting each respondent's own mean before calling corrcoef does not change the resulting similarity matrix at all; it is not part of this pipeline.

## The respondent network as a directed graph
Each respondent points to its 5 nearest neighbors, so the graph is directed and in-degree (how often a respondent is chosen as someone else's neighbor) is not fixed at 5 the way out-degree is.
Observed in-degree: mean=5.00 (fixed by construction), sd=5.07, max=21, respondents with in-degree 0: 12
Random-assignment null (each respondent picks 5 random others, B=500): in-degree sd = 2.14 (std of that estimate = 0.191)
Correlation between in-degree and a respondent's own mean agreement level: r = 0.432
In-degree is far more unequal than random assignment would produce, and it correlates with how agreeable a respondent is overall. What causes that correlation is not established by this analysis; it is reported as a descriptive fact about the network, not explained.

The six respondents who abandoned the survey partway through are excluded by `load_complete()` before this network is built, so this network makes no claim about them.