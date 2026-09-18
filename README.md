# DPCN Assignment 1 — Opinion Network Formation

**Parts: Idea, Extension 1, Extension 2 & Extension 3 (this push)**

This project constructs and analyzes a network from `Survey_Results_UC.csv`, a
survey collecting opinions on Technology, Education, Society/Ethics, and
Environment (Values) from the class. This is the complete project README,
covering all four parts. The exploratory log behind every design decision
below is in `idea.md` at the repo root.

**Repo layout is flat** — all contributors' files live at the repo root
alongside the shared `Survey_Results_UC.csv`, not in per-person subfolders.
Every script only needs its own filename plus that shared CSV, and output
filenames are unique per contributor (`results.md`, `results_extension1.md`,
`results_extension2.md`, `results_extension3.md`) so no push overwrites
another's output.

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
- Every significance test in this project uses the same permutation-null
  design: each of the 60 item columns is independently shuffled across the
  68 respondents (200 or 300 times, noted per test), which destroys all real
  correlation structure while preserving each item's response distribution
  exactly. That's the "does this look different from uncorrelated noise with
  the same answer patterns" baseline every p-value below is measured against.

---

## Idea: Hub-statement centrality — AI attitudes are structurally decoupled

### Network construction

- **Nodes:** all 60 survey statements.
- **Edges:** Pearson correlation |r| between two statements' answers across
  the 68 complete respondents; kept if |r| ≥ 0.15, weighted by |r| — 907
  edges on 60 nodes, deliberately dense rather than thresholded to a sparse
  top-N%, so centrality reflects the full correlation structure.

### Method

Eigenvector centrality, PageRank, and betweenness centrality (which
statements are hubs vs. peripheral vs. bridges), plus k-core decomposition on
a stricter |r| ≥ 0.30 graph to find the "backbone." Significance test:
permutation null on the gap between mean eigenvector centrality of
non-Technology items vs. Technology items.

### Results

**Top hub statements** (highest eigenvector centrality): S09 (inclusive-
viewpoint discussion), V07 (biodiversity), V08 (sustainable campuses), E07
(publishing research), S14 (ethics-over-short-term-gains) — all
Society/Environment/pedagogy-values items.

**Most peripheral statements** (lowest centrality): T08 (AI diagnosis), T01
(AI net-positive for society), T02 (generative AI as learning aid), T15
(society depending on AI) — core AI-attitude items.

**k-core backbone** (|r| ≥ 0.30): a "9-core" means every statement in it is
connected to at least 9 others within that subgraph — a connectivity
requirement, not a node count. That requirement leaves a 22-statement
backbone standing (6 Society, 4 Education, 12 Environment) — **zero
Technology statements**.

### Significance test

Observed gap = 0.0668 vs. permutation null (B=200) mean = 0.0005, std =
0.0093. **p = 0.0050** (the floor achievable with 200 permutations — 0/200
reshuffles matched it), roughly 7 standard deviations above the null mean.

### Conclusion

There's a tightly interconnected general civic/pedagogical-values belief
system in this class — but AI-specific attitudes are statistically decoupled
from it. Knowing someone is pro-environment or pro-ethics tells you almost
nothing about whether they trust AI. This is the strongest, most rigorously
validated finding in the project, and everything below either corroborates it
or validates the network methodology used to find it.

*(Code: `data_utils.py`, `idea_hub_centrality.py`. Outputs:
`outputs/network_graph.png` — the full network, force-directed, node size =
eigenvector centrality, color = T/E/S/V block, black ring = backbone
membership, larger black labels = top-8/bottom-5 centrality extremes, edge
darkness = correlation strength — plus `outputs/centrality_by_statement.png`,
`outputs/significance_test.png`, `outputs/results.md`.)*

---

## Extension 1: Structural balance on the signed statement network

Asks whether the belief network is internally *consistent* (Heider balance
theory: a triad is "balanced" if the product of its three relationship signs
is positive).

### Network construction

Same 60 statement nodes; edges signed +1 if r ≥ +0.20, −1 if r ≤ −0.20 → 620
positive, 27 negative edges (the network is overwhelmingly positively
correlated).

### Method

Enumerate every complete triad, classify balanced/unbalanced by sign product.
Significance test: reshuffle the sign *labels* (not the edges) onto the same
edge positions 300 times — controls for the fact that a heavily
positive-skewed network is *automatically* mostly balanced, and asks whether
the observed level exceeds what that skew alone would produce. Cross-checked
against the analytic Heider baseline P(balanced) = p³ + 3p(1−p)².

### Results

3,042 of 3,049 complete triads balanced (**99.77%**) vs. an analytic/simulated
random-sign baseline of ~88.5% (null mean 88.50%, max 91.51% across 300
shuffles). **p = 0.0033** — significant.

**All 7 unbalanced triads involve a Technology/AI statement** (T02, T03, T04,
or T15) — e.g. "students should disclose AI use" correlates negatively with
"online learning complements classroom teaching," despite both correlating
positively with a shared third statement.

### Conclusion

The belief system is significantly more logically consistent than chance
predicts, even controlling for its skewed edge signs — and the rare
inconsistencies that do exist are all concentrated on AI/Technology
statements. Independent second confirmation of the Idea's central claim.

*(Code: `extension1_structural_balance.py`. Outputs:
`outputs/balance_significance.png`, `outputs/results_extension1.md`.)*

---

## Extension 2: Network-based missing-data imputation

Asks a methodological question: does the similarity network actually *mean*
anything, or is it just a nice-looking picture? Tests whether it can predict
a respondent's answer to a question that's hidden from it.

### Network construction

**Nodes:** the 68 respondents. **Edges:** k-nearest-neighbors (k=5) on
mean-centered profile correlation between respondents' 60-item answer
vectors (mean-centering removes acquiescence bias — raw answer similarity is
dominated by the fact that most people answer "Agree" most of the time).

### Method

For 500 random (respondent, item) pairs: mask the true answer, predict it
three ways — (a) mean of the 5 nearest network neighbors' answers to that
item, (b) that item's global mean across everyone else (baseline), (c) 5
*random* neighbors' answers (control, to check the *specific* similarity
structure matters, not just "any 5 people"). Compare mean absolute error
(MAE) with paired significance tests since (a) and (b) are computed on the
same 500 held-out cells.

### Results

| Predictor | MAE |
|---|---|
| Network k-NN | **0.533** |
| Global-mean baseline | 0.662 |
| Random-neighbor control | 0.707 |

Paired t-test (baseline vs. k-NN error): t=7.152, **p = 3.1×10⁻¹²**.
Wilcoxon signed-rank (non-parametric check): **p = 1.7×10⁻¹¹**.
Real-network k-NN vs. random-neighbor k-NN: t=5.152, **p = 3.1×10⁻⁷**.

### Conclusion

The strongest p-value anywhere in this project. The similarity network
encodes real, statistically undeniable predictive signal about individual
opinions — it beats both a naive baseline and a same-size random-neighbor
control by a wide, highly significant margin. This is also a concrete,
demonstrated method for reconstructing plausible answers for the 6 survey
respondents who abandoned partway through.

*(Code: `extension2_imputation.py`. Outputs: `outputs/imputation_mae.png`,
`outputs/results_extension2.md`.)*

---

## Extension 3: Multiplex per-category belief-network density

Asks how the T/E/S/V blocks compare to each other as four separate
"sub-networks" (a simple multiplex view), quantifying the descriptive
observation (in `idea.md`) that Environment answers show near-unanimous
agreement while Education answers are the most disputed.

### Network construction

Same 60 statements, split into 4 layers by block. **Edges:** within-layer
Pearson |r| only (no cross-layer edges in this analysis).

### Method

Mean |r| within each layer, each tested against its own permutation null
(B=200 per category, same shuffle design as the Idea's test).

### Results

| Category | mean \|r\| | null mean | p-value |
|---|---|---|---|
| Technology | 0.136 | 0.098 | 0.0050 |
| Education | 0.195 | 0.098 | 0.0050 |
| Society | 0.250 | 0.098 | 0.0050 |
| **Environment** | **0.318** | 0.098 | 0.0050 |

All four blocks are individually significant (all hit the p=0.005 floor), but
the *effect size* differs sharply: Environment's density above its noise
floor (0.220) is roughly **5.7×** Technology's (0.038).

### Conclusion

Every topic block shows real internal correlation beyond chance, but
Environment opinions function almost as a single unified attitude while
Technology opinions are comparatively fragmented — consistent with, and a
third independent confirmation of, the Idea's central finding that Technology
attitudes are the odd one out in this class's belief system.

*(Code: `extension3_multiplex_density.py`. Outputs:
`outputs/category_density.png`, `outputs/results_extension3.md`.)*

---

## Overall synthesis

Four independent analyses, built with three different network
constructions (statement-correlation graph, signed statement graph,
respondent-similarity graph, per-category statement subgraphs) and three
different methods (eigenvector centrality, triad balance, k-NN prediction,
within-layer density), all converge on the same conclusion: **this class's
opinions on ethics, education, and environment form one coherent,
internally-consistent belief system, and attitudes toward AI/Technology sit
statistically apart from it.** Every one of the four core statistics reported
above is significance-tested against a permutation null, not just eyeballed
from a plot — the full negative-result log (ideas tried and discarded because
they didn't survive significance testing) is in `idea.md` at the repo root,
for anyone checking that this wasn't cherry-picked.

## Repository layout

```
Survey_Results_UC.csv                raw data (shared)
idea.md                              full exploratory log: every idea tried, significance
                                      tests, and why this direction was chosen
docs/DPCN_Assignment_1.pdf           assignment brief

data_utils.py                        shared load + permutation-null helper (identical
                                      copy carried by each contributor's script)

idea_hub_centrality.py               Idea
outputs/network_graph.png
outputs/centrality_by_statement.png
outputs/significance_test.png
outputs/results.md

extension1_structural_balance.py     Extension 1
outputs/balance_significance.png
outputs/results_extension1.md

extension2_imputation.py             Extension 2
extension3_multiplex_density.py      Extension 3
outputs/imputation_mae.png
outputs/category_density.png
outputs/results_extension2.md
outputs/results_extension3.md

README.md                            this file — the complete project README
```

**To run any part:** from the repo root, `python3.12 <script_name>.py` — every
script only needs its own `data_utils.py` copy and `Survey_Results_UC.csv`,
both already present at the repo root.

## Next step

Report writing (not yet started) — will assemble Dataset Documentation,
Pipeline, Analysis and Visualizations, Results and Discussion, and Individual
Contribution sections from the four analyses documented above.
