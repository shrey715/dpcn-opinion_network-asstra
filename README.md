# DPCN Assignment 1 — Opinion Network Formation

**Parts so far: Idea, Extension 1 (this push)**

This project constructs and analyzes a network from `Survey_Results_UC.csv`, a
survey collecting opinions on Technology, Education, Society/Ethics, and
Environment (Values) from the class. This README repeats the core Idea in
full (for context) and adds Extension 1 on top of it.

**Repo layout is flat** — all contributors' files live at the repo root
alongside the shared `Survey_Results_UC.csv`, not in per-person subfolders.
Every script uses only its own filename plus that shared CSV, and output
filenames are kept unique per contributor (`results.md` for the Idea,
`results_extension1.md` / `results_extension2.md` / `results_extension3.md`
for the extensions) so nobody's push overwrites anybody else's output.

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
  respondents** (`data_utils.load_complete()`), to avoid missing-data bias in
  the correlation matrix.

---

## Idea: Hub-statement centrality — AI attitudes are structurally decoupled

### Network construction

- **Nodes:** all 60 survey statements.
- **Edges:** Pearson correlation |r| between two statements' answers across
  the 68 complete respondents; an edge is kept if |r| ≥ 0.15, weighted by
  |r|. This produced **907 edges** on the 60 nodes — a dense weighted graph
  deliberately *not* thresholded down to a sparse top-N%, so centrality
  reflects the full correlation structure rather than an arbitrarily chosen
  cutoff.

### Method

- **Eigenvector centrality** and **PageRank**: which statements are most
  "connected to the connected" — i.e. knowing someone's answer to a hub
  statement is highly predictive of many of their other answers.
- **Betweenness centrality**: which statements bridge otherwise-separate parts
  of the belief network.
- **k-core decomposition** on a separate, more strictly thresholded graph
  (|r| ≥ 0.30) to find the "backbone."
- **Significance test**: a permutation null. Each of the 60 item columns is
  independently shuffled across the 68 respondents (200 times), which
  destroys all real correlation structure while preserving each item's
  response distribution exactly. The test statistic — mean eigenvector
  centrality of non-Technology items minus mean eigenvector centrality of
  Technology items — is recomputed on every permuted dataset to build a null
  distribution, against which the real (unpermuted) value is compared.

### Results

**Top 8 hub statements (highest eigenvector centrality):** S09, V07, V08, E07,
S14, V15, S07, V13 — all Society/Environment/pedagogy-values items.

**5 most peripheral statements (lowest eigenvector centrality):** T08, T01,
E06, T02, T15 — core AI-attitude items dominate this list.

**k-core backbone** (|r| ≥ 0.30 graph): a "9-core" is the subgraph left after
repeatedly stripping away any statement connected to fewer than 9 others
within it — a connectivity requirement, not a node count. That requirement
leaves a **22-statement backbone** standing: 6 Society, 4 Education, 12
Environment — **zero Technology statements**.

### Significance test

| | Value |
|---|---|
| Statistic | mean eigenvector centrality (non-Tech) − mean eigenvector centrality (Tech) |
| Observed | 0.0668 |
| Permutation null (B=200) | mean = 0.0005, std = 0.0093 |
| **p-value** | **0.0050** (floor with 200 permutations) |

### Conclusion

AI-specific attitudes are statistically decoupled from the class's general
civic/pedagogical-values belief system. This is the strongest, most
rigorously validated finding across the whole project.

*(Full code: `data_utils.py`, `idea_hub_centrality.py`; outputs:
`outputs/network_graph.png`, `outputs/centrality_by_statement.png`,
`outputs/significance_test.png`, `outputs/results.md`. See `idea.md` at the
repo root for the full exploratory log behind this choice.)*

---

## Extension 1: Structural balance on the signed statement network

This extension asks a different question of the same underlying data: is the
class's belief system internally *consistent*? Classical social-balance
(Heider) theory says a triad of three mutually-connected opinions is
"balanced" if the product of the three relationship signs is positive (e.g.
all three positively correlated, or one positive and two negative) — roughly,
"the friend of my friend is my friend."

### Network construction

- **Nodes:** the 60 statements, restricted to the ones with at least one
  edge at |r| ≥ 0.20 (all 60 qualify here).
- **Edges:** signed — +1 if r ≥ +0.20, −1 if r ≤ −0.20. This produced 620
  positive edges and 27 negative edges (p_pos = 0.958 — the belief system is
  overwhelmingly made of positive correlations).

### Method

- Enumerate every complete triad (three statements where all three pairwise
  edges exist) and classify it balanced/unbalanced by the sign product.
- **Significance test**: because the edge set is so skewed toward positive
  edges, *some* balance is guaranteed by chance alone. To control for that,
  the null model reshuffles the sign labels (not the edges themselves) onto
  the same 647 edge positions 300 times, and balance is recomputed each time
  — this asks "is the observed balance level higher than what the same
  +/− ratio would produce under random sign assignment," not just "is it
  higher than 50%." An analytic version of the same baseline is computed too
  (P(balanced) = p³ + 3p(1−p)² for p = fraction of positive edges).

### Results

| | Value |
|---|---|
| Complete triads | 3,049 |
| Balanced | 3,042 (**99.77%**) |
| Analytic random-sign baseline (same +/− ratio) | 88.5% |
| Sign-shuffle null (B=300) | mean = 88.50%, max = 91.51% |
| **p-value** | **0.0033** — significant |

### The 7 unbalanced triads

Every single one of the 7 unbalanced triads involves at least one Technology
statement (T02, T03, T04, or T15) — e.g. "students should disclose AI use in
assignments" (T03) correlates *negatively* with "online learning complements
classroom teaching" (E04), even though both individually correlate positively
with a third statement. Full list with the specific statement text is in
`outputs/results_extension1.md`.

### Conclusion

The belief network is significantly more internally consistent than chance
predicts, even after controlling for its skewed positive/negative edge ratio
— this class's opinions rarely contradict each other logically. The rare
exceptions are not random noise: **all 7 involve a Technology/AI statement**,
independently reinforcing the Idea's headline finding that AI attitudes behave
differently from the rest of the belief system.

## Files (this push adds)

- `data_utils.py` — identical to the copy from the Idea's push (shared
  loading/permutation-test helper); included again here so this part runs
  independently even if pulled in isolation. Already present in the repo — no
  changes.
- `extension1_structural_balance.py` — builds the signed network, computes
  balance, runs the sign-shuffle significance test, saves the figure and
  results.
- `outputs/balance_significance.png` — observed balance % vs. the sign-shuffle
  null distribution vs. the analytic Heider baseline.
- `outputs/results_extension1.md` — full numeric results and the 7 unbalanced
  triads (regenerated by the script).

**To run:** `python3.12 extension1_structural_balance.py` from the repo root
(needs `Survey_Results_UC.csv` in the same folder — it's already there).
