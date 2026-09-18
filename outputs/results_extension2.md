# Extension 2 — Network-based missing-data imputation

Method: for 500 random (respondent, item) pairs, mask the true answer and predict it from the mean of the 5 nearest neighbors in the mean-centered profile-similarity network, vs. a global item-mean baseline, vs. 5 random neighbors (control).

Network k-NN MAE:      0.533
Random-neighbor MAE:   0.707
Global-mean baseline:  0.662

## Significance tests
Paired t-test (baseline error vs k-NN error): t=7.152, p=3.055e-12
Wilcoxon signed-rank (same pairs): W=40492.0, p=1.659e-11
Real-network k-NN vs random-neighbor k-NN (independent t-test): t=5.152, p=3.101e-07

Conclusion: the similarity network encodes real, statistically robust predictive signal about individual opinions -- it is not just a descriptive picture. This also gives a concrete method for reconstructing plausible answers for the survey dropouts.