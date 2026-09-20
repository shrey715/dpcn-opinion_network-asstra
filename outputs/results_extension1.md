# Extension 1 — Triangle density and the negative-edge subgraph

Nodes: 60 statements. Edges: |r| >= 0.2 (647 total: 620 positive, 27 negative).
Edge density p_hat = 647/C(60,2) = 0.3655.

## Part A: is the graph more triangle-dense than a random graph of the same density?
Observed triangles = 3049. Observed transitivity (global clustering) = 0.5661.
Closed-form expectation under G(60, p_hat): C(60,3) * p_hat^3 = 1671.4 triangles.
Simulated G(60, p_hat) null (B=200): mean triangles = 1662.7 (std=163.4), mean transitivity = 0.3641.
p-value (observed triangle count vs. simulated null) = 0.0050.
Correlation graphs are transitive by construction (if A and B both correlate strongly with C, A and B are likely to correlate with each other through shared variance), so an Erdos-Renyi comparison is a benchmark showing the graph is denser in triangles than a same-density random graph, not independent proof of a psychological "balance" mechanism.

## Part B: structure of the 27 negative edges
Degree sequence (top 8, nonzero only): [('E03', 9), ('E02', 8), ('E04', 3), ('T02', 2), ('T12', 2), ('E05', 2), ('E06', 2), ('E07', 2)]
Connected components with >= 2 nodes: 5, sizes = [17, 4, 3, 2, 2]
Triangles within the negative-edge subgraph: 0

The largest component (17 nodes) is organized around two Education hub items, E02 (traditional exams accurately measure knowledge) and E03 (attendance should be compulsory), which together account for most of the edges in that component. There is no direct negative edge between E02 and E03 themselves. This is a hub-and-spoke disagreement structure centered on two contested Education statements, not a Technology-centered one.

## Part C: threshold sweep
| tau | edges (obs) | edges (null) | giant (obs) | giant (null) | isolated (obs) | isolated (ER) | Tech gap |
|---|---|---|---|---|---|---|---|
| 0.100 | 1172 | 734.1 | 60 | 60.0 | 0 | 0.00 | 9.956 |
| 0.125 | 1029 | 554.9 | 60 | 60.0 | 0 | 0.00 | 11.600 |
| 0.150 | 907 | 399.1 | 60 | 60.0 | 0 | 0.00 | 11.689 |
| 0.175 | 783 | 272.6 | 60 | 60.0 | 0 | 0.00 | 11.511 |
| 0.200 | 647 | 177.5 | 60 | 59.9 | 0 | 0.00 | 11.956 |
| 0.225 | 565 | 115.2 | 60 | 58.8 | 0 | 0.00 | 11.244 |
| 0.250 | 457 | 68.5 | 60 | 51.0 | 0 | 0.00 | 9.822 |
| 0.275 | 368 | 37.5 | 60 | 21.6 | 0 | 0.00 | 8.089 |
| 0.300 | 304 | 23.6 | 60 | 9.6 | 0 | 0.00 | 6.844 |
| 0.325 | 233 | 11.8 | 56 | 3.8 | 2 | 0.01 | 6.178 |
| 0.350 | 171 | 6.4 | 47 | 3.1 | 8 | 0.15 | 5.289 |
| 0.375 | 125 | 3.7 | 44 | 2.5 | 12 | 0.80 | 3.956 |
| 0.400 | 95 | 1.6 | 42 | 2.0 | 16 | 2.32 | 3.067 |
| 0.425 | 59 | 0.6 | 35 | 1.4 | 19 | 8.12 | 2.000 |
| 0.450 | 41 | 0.2 | 33 | 1.2 | 21 | 15.05 | 1.200 |

The null graph loses its giant component well before the real one does (null giant size collapses starting around tau=0.275-0.30, while the observed giant component holds at 60 nodes through tau=0.30 and only starts shedding nodes past that). The Technology-vs-rest degree gap stays positive at every threshold tested, which is a threshold-robustness check on the |r| >= 0.15 choice used throughout the rest of the project.

## Part D: structural comparison against Erdos-Renyi, and degree distribution
| tau | edges | density | <k> | var(k) obs/ER | components | diameter | <L> obs/ER | C obs/ER | <k_nn> obs/ER |
|---|---|---|---|---|---|---|---|---|---|
| 0.15 | 907 | 0.512 | 30.23 | 94.3 / 15.0 | 1 | 2 | 1.49 / 1.20 | 0.639 / 0.512 | 33.4 / 30.7 |
| 0.20 | 647 | 0.366 | 21.57 | 95.0 / 13.9 | 1 | 3 | 1.67 / 1.33 | 0.566 / 0.366 | 26.0 / 22.2 |
| 0.30 | 304 | 0.172 | 10.13 | 45.2 / 8.5 | 1 | 5 | 2.21 / 1.77 | 0.447 / 0.172 | 14.6 / 11.0 |

At every threshold, observed clustering, degree variance, and average-neighbor-degree all exceed the Erdos-Renyi prediction for a random graph of the same size and density, most sharply at |r| >= 0.30 (clustering 0.45 vs. 0.17, degree variance 45 vs. 8.5). The degree distribution at |r| >= 0.30 is visibly wider than a Binomial(n-1, p) null with the same mean would produce (Figure: degree_distribution.png).

## Why |r| >= 0.15 was used for the main graph
At |r| >= 0.15, permutation resampling shows roughly 43% of the 907 edges (about 393) are expected by chance alone; at |r| >= 0.20 this falls to roughly 28% (179 of 647); at |r| >= 0.30 it falls to roughly 7% (23 of 304). The 0.15 threshold is deliberately permissive so that centrality reflects the full correlation structure rather than a sparse, arbitrarily cut graph, and Part C shows the Technology-vs-rest degree gap survives across every threshold from 0.10 to 0.45, so this choice does not drive the qualitative conclusion, only how much noise is included alongside the real signal.