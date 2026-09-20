# Extension 3 — Per-block link density

Nodes: 60 statements, partitioned into four blocks (T/E/S/V) with no edges drawn across blocks. Each block is treated as an induced subgraph of the full statement-correlation graph. Density here is weighted link density: the mean of |r| over every within-block pair, read directly off the correlation matrix (a generalization of unweighted link density to weighted edges).

| Block | mean\|r\| | permutation null mean | p-value |
|---|---|---|---|
| T | 0.136 | 0.098 | 0.0050 |
| E | 0.195 | 0.098 | 0.0050 |
| S | 0.250 | 0.098 | 0.0050 |
| V | 0.318 | 0.098 | 0.0050 |

## Why the null mean is ~0.098 in every block
For two independent (uncorrelated) vectors of 68 observations, the expected absolute Pearson correlation is approximately sqrt(2 / (pi * (n-1))) = sqrt(2 / (pi * 67)) = 0.0975. This closed form matches the permutation null mean obtained by simulation (~0.098) and does not depend on which block is being tested, since it only uses the sample size.

## Effect sizes
All four blocks clear their permutation null (all p=0.0050, the floor for B=200), but the amount by which they clear it differs: Environment's density above its noise floor (0.220) is roughly 5.7x Technology's (0.038). Technology's within-block correlations are weakly related to each other rather than forming distinct sub-clusters; nothing in this analysis tests for or supports separate sub-views within the block.

## Row-centered robustness check
| Block | raw mean\|r\| | row-centered mean\|r\| |
|---|---|---|
| T | 0.136 | 0.120 |
| E | 0.195 | 0.133 |
| S | 0.250 | 0.129 |
| V | 0.318 | 0.137 |
Once each respondent's own mean response is subtracted before computing correlations (removing each person's general tendency to agree or disagree), the four blocks converge to a similar density (~0.12-0.14) instead of spreading from 0.136 to 0.318. The raw-data gap reported above is therefore driven mostly by a general agreement factor shared across respondents, not purely by topic-specific belief structure.

The Idea network's centrality gap shows the same pattern: 0.0668 raw, 0.0007 row-centered. Both comparisons are drawn together in raw_vs_rowcentered.png.