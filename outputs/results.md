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

## Significance test
Statistic: mean eigenvector centrality (non-Tech) - mean eigenvector centrality (Tech)
Observed = 0.0668
Permutation null (B=200): mean = 0.0005, std = 0.0093
p-value = 0.0050 (floor — 0/200 permutations matched or exceeded observed)

Conclusion: Technology-block statements are significantly less central to the class's belief network than everything else. General civic/education/environment values form a tight backbone; AI-specific attitudes sit apart from it.