# Idea — Hub-statement centrality: AI attitudes are structurally decoupled

Network: 60 statement nodes, edges = pairwise |r| >= 0.15 (907 edges).

## Top 8 hub statements (eigenvector centrality)
- 0.220  S09  Universities should promote an inclusive environment where different viewpoints can b
- 0.214  V07  Protecting biodiversity is essential for long-term human well-being.
- 0.208  V08  Universities should adopt environmentally sustainable campus practices even if implem
- 0.191  E07  Publishing research before graduation should be encouraged, but not mandatory.
- 0.187  S14  Leaders should prioritize ethical decision-making even when it reduces short-term gai
- 0.185  V15  Current generations have a responsibility to protect natural resources for future gen
- 0.176  S07  Equal opportunities should be prioritized regardless of a person's background.
- 0.176  V13  Companies should be held accountable for the environmental impacts of their activitie

## 5 most peripheral statements (lowest eigenvector centrality)
- 0.022  T08  AI-assisted diagnosis should become routine in healthcare.
- 0.023  T01  Artificial Intelligence will improve society more than it will create problems.
- 0.027  E06  Every undergraduate student should participate in at least one research project.
- 0.037  T02  Generative AI tools should be allowed as learning aids in higher education.
- 0.039  T15  Society will increasingly depend on AI-assisted decision making.

## k-core backbone (|r|>=0.30 graph)
Max core = 9-core, 22 members. Category counts: {np.str_('S'): 6, np.str_('V'): 12, np.str_('E'): 4}
The largest k for which a k-core exists at |r|>=0.30 is 9; that 22-node subgraph is the backbone (k is a connectivity requirement, not a node count).

## PageRank and betweenness: do they add anything beyond eigenvector centrality?
Spearman correlation between eigenvector centrality and PageRank across all 60 statements: 0.985. The two rankings are almost identical, so PageRank does not surface any ordering that eigenvector centrality does not already capture on this graph.
Betweenness centrality (bridging power) mean: Technology = 0.0046, non-Technology = 0.0129. Top-5 by betweenness: S09, V07, E10, V11, E12.

## Significance test
Statistic: mean eigenvector centrality (non-Tech) - mean eigenvector centrality (Tech)
Observed = 0.0668
Permutation null (B=1000): mean = 0.0000, std = 0.0100
p-value = 0.0010 (floor — 0/1000 permutations matched or exceeded observed)

## Robustness check: row-centered (ipsatized) correlation matrix
Recomputing the same graph after subtracting each respondent's own mean response across all 60 items (removing each person's general tendency to agree or disagree) before computing item-item correlations: the centrality gap falls from 0.0668 to 0.0007.
This does not prove the raw-data finding is spurious; a shared general disposition toward pro-social, pro-environment statements could itself be a genuine attitude rather than a survey artifact. But the data cannot distinguish "Technology attitudes are substantively decoupled" from "this gap is mostly a general agreement/response-style factor that happens to load unevenly across blocks," and both readings should be reported together rather than only the first.

Conclusion: in the raw correlation matrix, Technology-block statements are significantly less central to the class's belief network than everything else, and this pattern survives a stricter permutation test (B=1000). Most of that gap, however, is attributable to a general agreement factor rather than to Technology specifically; see the robustness check above.