# DPCN Assignment 1 — Opinion Network Formation

**This push: the Idea (core network analysis)**

This project constructs and analyzes a network from `Survey_Results_UC.csv`, a
survey collecting opinions on Technology, Education, Society/Ethics, and
Environment (Values) from the class. This repository holds the core network
analysis; Extensions 1–3 build on it.

## Dataset

- 96 respondents, 60 Likert-scale statements labeled by block: **T**echnology
  (T01–T15), **E**ducation (E01–E15), **S**ociety/Ethics (S01–S15),
  **V**alues/Environment (V01–V15).
- Encoding: Strongly Disagree=1, Disagree=2, Neutral=3, Agree=4, Strongly
  Agree=5. "No Comments" and blanks are treated as missing.
- 5 respondents left every question blank and were dropped. 6 more abandoned
  partway through in a clean trailing-block pattern (answered questions 1..N
  in order, then stopped — survey fatigue, not random non-response).
- All network construction here uses the **68 fully-complete respondents**
  (`data_utils.load_complete()`), to avoid missing-data bias in the
  correlation matrix.

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
  (|r| ≥ 0.30) to find the "backbone" — the maximal subgraph where every
  statement is strongly connected to many others.
- **Significance test**: a permutation null. Each of the 60 item columns is
  independently shuffled across the 68 respondents (200 times), which
  destroys all real correlation structure while preserving each item's
  response distribution exactly. The test statistic — mean eigenvector
  centrality of non-Technology items minus mean eigenvector centrality of
  Technology items — is recomputed on every permuted dataset to build a null
  distribution, against which the real (unpermuted) value is compared.

### Results

**Top 8 hub statements (highest eigenvector centrality):**

| Centrality | Code | Statement |
|---|---|---|
| 0.220 | S09 | Universities should promote an inclusive environment where different viewpoints can be discussed respectfully |
| 0.214 | V07 | Protecting biodiversity is essential for long-term human well-being |
| 0.208 | V08 | Universities should adopt environmentally sustainable campus practices even if implementation costs increase |
| 0.191 | E07 | Publishing research before graduation should be encouraged, but not mandatory |
| 0.187 | S14 | Leaders should prioritize ethical decision-making even when it reduces short-term gains |
| 0.185 | V15 | Current generations have a responsibility to protect natural resources for future generations |
| 0.176 | S07 | Equal opportunities should be prioritized regardless of a person's background |
| 0.176 | V13 | Companies should be held accountable for the environmental impacts of their activities |

**5 most peripheral statements (lowest eigenvector centrality):**

| Centrality | Code | Statement |
|---|---|---|
| 0.022 | T08 | AI-assisted diagnosis should become routine in healthcare |
| 0.023 | T01 | Artificial Intelligence will improve society more than it will create problems |
| 0.027 | E06 | Every undergraduate student should participate in at least one research project |
| 0.037 | T02 | Generative AI tools should be allowed as learning aids in higher education |
| 0.039 | T15 | Society will increasingly depend on AI-assisted decision making |

**k-core backbone** (|r| ≥ 0.30 graph): a "9-core" is the subgraph left after
repeatedly stripping away any statement connected to fewer than 9 others
within it — it's a connectivity requirement, not a node count. That
requirement leaves a **22-statement backbone** standing: 6 Society, 4
Education, 12 Environment — **zero Technology statements**. The class's most
tightly interconnected "backbone" of beliefs contains no AI-specific items at
all.

### Significance test

| | Value |
|---|---|
| Statistic | mean eigenvector centrality (non-Tech) − mean eigenvector centrality (Tech) |
| Observed | 0.0668 |
| Permutation null (B=200) | mean = 0.0005, std = 0.0093 |
| **p-value** | **0.0050** (the floor achievable with 200 permutations — 0 of 200 random reshuffles matched or exceeded the observed gap) |

The observed gap sits roughly **7 standard deviations** above the null mean.

### Conclusion

There is a tightly interconnected general civic/pedagogical-values belief
system in this class (centered on ethics, inclusivity, environmental
responsibility, and educational innovation) — but **AI-specific attitudes are
statistically decoupled from it**. Knowing someone is pro-environment,
pro-ethics, or pro-inclusive-education tells you almost nothing about whether
they trust AI in healthcare or believe AI helps society more than it harms.
This is the strongest, most rigorously validated finding across the whole
project (see `idea.md` at the repo root for the full exploratory log and how
this was chosen over other candidate directions).

## Files in this folder

- `data_utils.py` — loads and cleans the survey CSV, returns the 68×60 numeric
  matrix, plus a generic permutation-null helper. (Self-contained; each
  contributor's folder has its own identical copy so folders can be run
  independently.)
- `idea_hub_centrality.py` — builds the network, computes all centrality
  metrics and the k-core backbone, runs the significance test, saves figures
  and a results summary.
- `outputs/network_graph.png` — the full network, laid out force-directed
  (statements with stronger correlation are pulled closer together). Visual
  encoding:
  - **Node size** = eigenvector centrality (bigger = more central/hub-like,
    same value as the tables above — this is why Technology nodes are
    visibly small).
  - **Node color** = T/E/S/V block (see legend).
  - **Black ring** = backbone membership (the 22-statement 9-core described
    above).
  - **Larger, black label text** = the top-8 hub / bottom-5 peripheral
    statements from the tables above (a separate ranking from the backbone
    ring — a node can be one, both, or neither).
  - **Edge darkness/thickness** = strength of the correlation (|r|) between
    two statements.
- `outputs/centrality_by_statement.png` — eigenvector centrality per
  statement, colored by T/E/S/V block.
- `outputs/significance_test.png` — observed value vs. the permutation null
  distribution.
- `outputs/results.md` — full numeric results (regenerated by the script).

**To run:** `python3.12 idea_hub_centrality.py` from inside this folder
(needs `Survey_Results_UC.csv` in the same folder).
