# Extension 1 — Structural balance on the signed statement network

Nodes: 60 statements with >=1 edge at |r|>=0.2. Edges: signed (+1 if r>=+0.2, -1 if r<=-0.2).
Signed edges: 620 positive, 27 negative (p_pos=0.958).

## Balance result
3042/3049 complete triads balanced = 99.77%
Analytic random-sign-assignment expectation (same +/- ratio): 88.5%

## Significance test (sign-shuffle null, B=300)
Null mean = 88.50%, max = 91.51%
p-value = 0.0033  -> SIGNIFICANT

## The 7 unbalanced triads
- T02 <-> E14 (+1), E14 <-> S11 (+1), T02 <-> S11 (-1)
    T02: Generative AI tools should be allowed as learning aids in higher educa
    E14: Strong collaborations between universities and industry improve studen
    S11: People should be free to express differing opinions as long as they do
- T02 <-> S11 (-1), S11 <-> V11 (+1), T02 <-> V11 (+1)
    T02: Generative AI tools should be allowed as learning aids in higher educa
    S11: People should be free to express differing opinions as long as they do
    V11: Technological innovation is essential for addressing environmental cha
- T03 <-> E04 (-1), E04 <-> E10 (+1), T03 <-> E10 (+1)
    T03: Students should disclose the use of AI in assignments and reports.
    E04: High-quality online learning can effectively complement classroom teac
    E10: Universities should prioritize innovation and problem-solving over rot
- T04 <-> S13 (+1), S13 <-> V04 (+1), T04 <-> V04 (-1)
    T04: Every engineering student should receive formal education in AI.
    S13: Critical evaluation of online information should be taught as a core e
    V04: Public transportation and non-motorized transport should be promoted e
- T04 <-> V03 (+1), V03 <-> V04 (+1), T04 <-> V04 (-1)
    T04: Every engineering student should receive formal education in AI.
    V03: Individuals should actively reduce their personal energy consumption.
    V04: Public transportation and non-motorized transport should be promoted e
- T04 <-> V04 (-1), V04 <-> V15 (+1), T04 <-> V15 (+1)
    T04: Every engineering student should receive formal education in AI.
    V04: Public transportation and non-motorized transport should be promoted e
    V15: Current generations have a responsibility to protect natural resources
- T15 <-> E09 (-1), E09 <-> V15 (+1), T15 <-> V15 (+1)
    T15: Society will increasingly depend on AI-assisted decision making.
    E09: Collaborative learning is generally more effective than individual lea
    V15: Current generations have a responsibility to protect natural resources

Conclusion: the belief network is significantly more internally consistent (balanced) than chance predicts even after controlling for its skewed positive/negative edge ratio. The rare exceptions cluster around AI-accountability/disclosure tensions, echoing the main Idea's finding that AI attitudes behave differently from the rest of the belief system.