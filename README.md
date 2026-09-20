# DPCN Assignment 1 — Opinion Network Formation

**Parts: Idea, Extension 1, Extension 2 & Extension 3 (revised)**

This project constructs and analyzes a network from `Survey_Results_UC.csv`, a
survey collecting opinions on Technology, Education, Society/Ethics, and
Environment (Values) from the class. This is the complete project README,
covering all four parts.

**Repo layout is flat** — all contributors' files live at the repo root
alongside the shared `Survey_Results_UC.csv`, not in per-person subfolders.
Every script only needs its own filename plus that shared CSV, and output
filenames are unique per contributor (`results.md`, `results_extension1.md`,
`results_extension2.md`, `results_extension3.md`) so no push overwrites
another's output.

**This revision** fixes four issues an independent review found in the first
draft: data leakage in Extension 2's similarity computation, a sample-size
mismatch in the Section 1 descriptive statistics, a mean-centering step that
is mathematically a no-op for Pearson correlation, and a general-agreement
confound that explains most of the raw-data gap in the Idea and Extension 3
results. All four are addressed in the write-ups below and in the full
`report/report.tex`.

## Dataset

- 96 respondents, 60 Likert-scale statements labeled by block: **T**echnology
  (T01–T15), **E**ducation (E01–E15), **S**ociety/Ethics (S01–S15),
  **V**alues/Environment (V01–V15).
- Encoding: Strongly Disagree=1, Disagree=2, Neutral=3, Agree=4, Strongly
  Agree=5. "No Comments" and blanks are treated as missing.
- 5 respondents left every question blank and were dropped. 6 more abandoned
  partway through in a clean trailing-block pattern (answered questions 1..N
  in order, then stopped — survey fatigue, not random non-response).
- All network construction across this project uses the **68 fully-complete
  respondents** (`data_utils.load_complete()`, identical copy carried by
  every contributor), to avoid missing-data bias in the correlation matrix.
  The descriptive statistics in the report's Dataset Documentation section
  use the 91 non-blank respondents instead (96 minus the 5 blank surveys),
  and the report states this explicitly since the two samples give slightly
  different numbers.
- Every significance test in this project uses the same permutation-null
  design unless noted otherwise: each of the 60 item columns is independently
  shuffled across the 68 respondents, which destroys all real correlation
  structure while preserving each item's response distribution exactly.

---

## Idea: Hub-statement centrality — AI attitudes are less central, with a caveat

### Network construction

- **Nodes:** all 60 survey statements.
- **Edges:** Pearson correlation |r| between two statements' answers across
  the 68 complete respondents; kept if |r| ≥ 0.15, weighted by |r| — 907
  edges on 60 nodes, deliberately dense rather than thresholded to a sparse
  top-N%, so centrality reflects the full correlation structure.

### Method

Eigenvector centrality, PageRank, and betweenness centrality, plus k-core
decomposition on a stricter |r| ≥ 0.30 graph to find the "backbone".
Significance test: permutation null (B=1000) on the gap between mean
eigenvector centrality of non-Technology items vs. Technology items. As a
robustness check, the same graph is rebuilt after subtracting each
respondent's own mean response across all 60 items first (removing general
agreement level) before computing item-item correlations.

### Results

**Top hub statements**: S09 (inclusive-viewpoint discussion), V07
(biodiversity), V08 (sustainable campuses), E07 (publishing research), S14
(ethics-over-short-term-gains).

**Most peripheral statements**: T08 (AI diagnosis), T01 (AI net-positive for
society), E06, T02 (generative AI as learning aid), T15 (society depending on
AI).

**k-core backbone** (|r| ≥ 0.30): the largest k for which a k-core exists is
9; that 22-statement subgraph (6 Society, 4 Education, 12 Environment, 0
Technology) is the backbone.

**PageRank and betweenness**: Spearman correlation between eigenvector
centrality and PageRank is 0.985 — PageRank adds no new ordering here.
Betweenness centrality mean is lower for Technology (0.0046) than the rest of
the network (0.0129).

### Significance test

Observed gap = 0.0668 vs. permutation null (B=1000) mean ≈ 0.0000, std =
0.0100. **p = 0.0010**, roughly 7 standard deviations above the null mean.

### Robustness check: row-centered correlation

Recomputing the graph after removing each respondent's own mean response
first, the centrality gap falls from 0.0668 to **0.0007**, essentially to
zero. This does not prove the raw-data finding is spurious — a shared
disposition toward pro-social, pro-environment statements could itself be a
genuine attitude — but the data cannot separate that reading from "this gap
is mostly a general agreement factor," and both should be reported.

### Conclusion

In the raw data, Technology-specific attitudes are statistically decoupled
from a tightly interconnected civic/pedagogical-values belief system. Most of
that gap, however, tracks a general agreement factor shared across
respondents rather than Technology content specifically; see the robustness
check above and Section 4.1 of the report.

*(Code: `data_utils.py`, `idea_hub_centrality.py`. Outputs:
`outputs/network_graph.png`, `outputs/centrality_by_statement.png`,
`outputs/significance_test.png`, `outputs/results.md`.)*

---

## Extension 1: Triangle density and the negative-edge subgraph

Asks two questions about the unsigned 647-edge statement graph (|r| ≥ 0.20):
is it more triangle-dense than a random graph of the same density, and what
structure do the 27 negative edges have on their own? An earlier version of
this analysis tested Heider structural balance on a signed version of the
graph; that framing conflated ordinary correlation-graph transitivity
(partly guaranteed by construction) with genuine attitudinal consistency, so
it has been replaced with the two comparisons below.

### Network construction

Same 60 statement nodes; edges are unsigned, |r| ≥ 0.20 → 647 edges total
(620 positive, 27 negative).

### Method

**Part A:** compare the observed triangle count against an Erdos-Renyi graph
G(60, p̂) of the same edge density, both via the closed form C(60,3)·p̂³ and
via 200 simulated draws.
**Part B:** treat the 27 negative edges as their own unsigned subgraph and
examine degree, connected components, and triangles within it.

### Results

**Part A:** observed triangles = 3049, transitivity = 0.566, vs. a simulated
Erdos-Renyi null mean of 1663 triangles and transitivity 0.364 (closed-form
expectation: 1671 triangles). **p = 0.0050**. The graph is more
triangle-dense than same-density randomness would predict, which is expected
of correlation graphs generally and is a weaker claim than structural
balance — a sanity check on graph structure, not proof of a psychological
consistency mechanism.

**Part B:** the 27 negative edges form 5 components (sizes 17, 4, 3, 2, 2)
with **0 triangles**. The largest component is a hub-and-spoke structure
anchored by two Education items: E02 ("traditional exams accurately measure
knowledge," degree 9) and E03 ("attendance should be compulsory," degree 8),
which are not directly connected to each other. The disagreement in this
network is concentrated on two contested Education statements, not on
Technology.

### Conclusion

The statement graph is more transitive than chance, as expected for a
correlation graph. The real structure worth reporting is in the negative
edges: disagreement here is a hub-and-spoke pattern around two Education
items, not a Technology-centered phenomenon.

*(Code: `extension1_structural_balance.py`. Outputs:
`outputs/triangle_significance.png`, `outputs/negative_edge_subgraph.png`,
`outputs/results_extension1.md`.)*

---

## Extension 2: Network-based missing-data imputation

Tests whether the respondent similarity network predicts a respondent's
answers better than a naive baseline.

### Network construction

**Nodes:** the 68 respondents. **Edges:** k-nearest-neighbors (k=5) on
profile correlation between respondents' 60-item answer vectors. An earlier
version subtracted each respondent's own mean first ("removes
agreeableness"); that step is mathematically a no-op for Pearson correlation
(which is already invariant to a constant shift in either vector), so it has
been dropped.

### Method

For **all 4,080** (respondent, item) cells (not a random sample): mask the
true answer, predict it from the mean of the 5 nearest neighbors, and compare
against a global item-mean baseline. Similarity for predicting item j is
recomputed with column j dropped first, so the true answer never leaks into
neighbor selection — an earlier version computed similarity once globally
and leaked the held-out answer into it, which inflated the reported effect.
Because the 4,080 cells come from only 68 respondents and are not
independent, significance is assessed with a respondent-level bootstrap
rather than a cell-level test.

### Results

| Predictor | MAE |
|---|---|
| Network k-NN (leak-free) | **0.645** |
| Global-mean baseline | 0.662 |

Respondent-level bootstrap (B=5000) 95% CI for the mean improvement:
**[-0.010, 0.042]** — includes zero. This is a small, borderline effect, not
the extreme significance an earlier leaky version reported (MAE 0.533 vs.
0.662, p=3×10⁻¹², from a cell-level test that also treated 4,080 correlated
cells as independent).

**Network as a directed graph:** in-degree (how often a respondent is chosen
as a neighbor) has standard deviation 5.07, against 2.14 under random
assignment; maximum in-degree 21; 12 respondents with in-degree 0. In-degree
correlates with a respondent's own mean agreement level (r=0.43): more
agreeable respondents get chosen more often, since similarity uses raw
(not de-meaned) profiles.

### Conclusion

The similarity network carries a small amount of real predictive signal, but
not the dramatic effect first reported — that was substantially inflated by
data leakage. The claim that this method reconstructs answers for the six
survey dropouts has been removed: those six are excluded before this network
is built, and no such reconstruction was ever run.

*(Code: `extension2_imputation.py`. Outputs: `outputs/imputation_mae.png`,
`outputs/imputation_bootstrap.png`, `outputs/results_extension2.md`.)*

---

## Extension 3: Per-block link density

Asks how the T/E/S/V blocks compare as four induced subgraphs of the
statement-correlation graph.

### Network construction

Same 60 statements, split into 4 blocks. **Edges:** within-block Pearson |r|
only (no cross-block edges).

### Method

Weighted link density (mean |r|) within each block, tested against its own
permutation null (B=200), and cross-checked against the closed-form expected
value of |r| between two independent 68-observation vectors,
√(2/(π·67)) ≈ 0.098. Also rerun on a row-centered correlation matrix as a
robustness check.

### Results

| Category | mean \|r\| | null mean | p-value |
|---|---|---|---|
| Technology | 0.136 | 0.098 | 0.0050 |
| Education | 0.195 | 0.098 | 0.0050 |
| Society | 0.250 | 0.098 | 0.0050 |
| **Environment** | **0.318** | 0.098 | 0.0050 |

All four blocks are individually significant, and the empirical null mean
matches the closed-form derivation. Environment's density above its noise
floor is roughly **5.7×** Technology's. Once each respondent's general
agreement level is removed first (row-centering), the four blocks converge
to roughly 0.12–0.14 instead of spreading from 0.136 to 0.318 — the raw-data
gap tracks a general agreement factor more than topic-specific structure.
Technology's within-block correlations are weakly related to one another;
nothing here tests for or supports separate sub-views within any block.

### Conclusion

Every block shows real internal correlation beyond chance, but the size of
that effect is mostly explained by a general agreement factor shared across
respondents, echoing the Idea's robustness check.

*(Code: `extension3_multiplex_density.py`. Outputs:
`outputs/category_density.png`, `outputs/results_extension3.md`.)*

---

## Overall synthesis

Four analyses, but not four independent lines of evidence: the Idea,
Extension 1, and Extension 3 all derive from the same 60×60 item correlation
matrix; only Extension 2 uses a genuinely different (respondent×respondent)
matrix. In the raw data, Technology and AI attitudes are less central,
concentrate the graph's only real disagreement structure once Education's
hub items are set aside, and form the least internally correlated topic
block. But robustness checks show most of the Idea's and Extension 3's
raw-data gap tracks a general agreement factor shared across respondents,
not Technology specifically, and Extension 2's corrected effect is small and
statistically borderline. This report does not test, and does not claim,
that a respondent's environmental or ethical positions predict their stance
on AI. See `report/report.tex` (Section 4) for the full discussion,
including limitations.

## Repository layout

```
Survey_Results_UC.csv                raw data (shared)
docs/DPCN_Assignment_1.pdf           assignment brief

data_utils.py                        shared load + permutation-null helper (identical
                                      copy carried by each contributor's script)

idea_hub_centrality.py               Idea
outputs/network_graph.png
outputs/centrality_by_statement.png
outputs/significance_test.png
outputs/results.md

extension1_structural_balance.py     Extension 1 (triangle density + negative-edge subgraph)
outputs/triangle_significance.png
outputs/negative_edge_subgraph.png
outputs/results_extension1.md

extension2_imputation.py             Extension 2
extension3_multiplex_density.py      Extension 3
outputs/imputation_mae.png
outputs/imputation_bootstrap.png
outputs/category_density.png
outputs/results_extension2.md
outputs/results_extension3.md

report/report.tex                    final report (LaTeX source)
report/report.pdf                    final report (compiled)

README.md                            this file — the complete project README
```

**To run any part:** from the repo root, `python3 <script_name>.py` — every
script only needs its own `data_utils.py` copy and `Survey_Results_UC.csv`,
both already present at the repo root.
