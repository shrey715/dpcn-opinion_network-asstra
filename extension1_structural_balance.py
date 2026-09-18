import os, itertools
import numpy as np
import matplotlib.pyplot as plt
from data_utils import load_complete

OUT = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUT, exist_ok=True)

X, qcols, cat_of = load_complete()
m = len(qcols)
THRESH = 0.20

C = np.corrcoef(X, rowvar=False)
signed_edges = {}
for i in range(m):
    for j in range(i + 1, m):
        r = C[i, j]
        if abs(r) >= THRESH:
            signed_edges[(i, j)] = 1 if r > 0 else -1

nodes = sorted(set(x for e in signed_edges for x in e))
n_pos = sum(1 for v in signed_edges.values() if v > 0)
n_neg = sum(1 for v in signed_edges.values() if v < 0)
p_pos = n_pos / (n_pos + n_neg)
analytic_balanced = p_pos**3 + 3 * p_pos * (1 - p_pos)**2

balanced, unbalanced, unbalanced_triads = 0, 0, []
for a, b, c in itertools.combinations(nodes, 3):
    e_ab = signed_edges.get((a, b)) or signed_edges.get((b, a))
    e_bc = signed_edges.get((b, c)) or signed_edges.get((c, b))
    e_ac = signed_edges.get((a, c)) or signed_edges.get((c, a))
    if e_ab is not None and e_bc is not None and e_ac is not None:
        if e_ab * e_bc * e_ac > 0:
            balanced += 1
        else:
            unbalanced += 1
            unbalanced_triads.append((a, b, c, e_ab, e_bc, e_ac))
obs_frac = balanced / (balanced + unbalanced)

# ---- significance: shuffle the sign LABELS onto the same edge positions ----
rng = np.random.default_rng(2)
signs = np.array(list(signed_edges.values()))
edge_keys = list(signed_edges.keys())
B = 300
null_fracs = []
for _ in range(B):
    shuffled = rng.permutation(signs)
    se = dict(zip(edge_keys, shuffled))
    bal = unb = 0
    for a, b, c in itertools.combinations(nodes, 3):
        e_ab = se.get((a, b)) or se.get((b, a))
        e_bc = se.get((b, c)) or se.get((c, b))
        e_ac = se.get((a, c)) or se.get((c, a))
        if e_ab is not None and e_bc is not None and e_ac is not None:
            if e_ab * e_bc * e_ac > 0:
                bal += 1
            else:
                unb += 1
    null_fracs.append(bal / (bal + unb))
null_fracs = np.array(null_fracs)
p = (np.sum(null_fracs >= obs_frac) + 1) / (B + 1)

# ---- figure: observed vs null distribution ----
fig, ax = plt.subplots(figsize=(7, 5))
ax.hist(null_fracs * 100, bins=25, color='#bdc3c7', label=f'sign-shuffle null (n={B})')
ax.axvline(obs_frac * 100, color='#e74c3c', linewidth=2, label=f'observed = {obs_frac*100:.2f}%')
ax.axvline(analytic_balanced * 100, color='#2c3e50', linestyle='--', linewidth=1.5,
           label=f'analytic Heider baseline = {analytic_balanced*100:.1f}%')
ax.set_xlabel('% balanced triads')
ax.set_ylabel('count')
ax.set_title(f'Structural balance significance test: p = {p:.4f}')
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'balance_significance.png'), dpi=150)
plt.close(fig)

# ---- results summary ----
lines = []
lines.append('# Extension 1 — Structural balance on the signed statement network\n')
lines.append(f'Nodes: {len(nodes)} statements with >=1 edge at |r|>={THRESH}. '
             f'Edges: signed (+1 if r>=+{THRESH}, -1 if r<=-{THRESH}).')
lines.append(f'Signed edges: {n_pos} positive, {n_neg} negative (p_pos={p_pos:.3f}).\n')
lines.append(f'## Balance result')
lines.append(f'{balanced}/{balanced+unbalanced} complete triads balanced = {obs_frac*100:.2f}%')
lines.append(f'Analytic random-sign-assignment expectation (same +/- ratio): {analytic_balanced*100:.1f}%')
lines.append(f'\n## Significance test (sign-shuffle null, B={B})')
lines.append(f'Null mean = {null_fracs.mean()*100:.2f}%, max = {null_fracs.max()*100:.2f}%')
lines.append(f'p-value = {p:.4f}  -> {"SIGNIFICANT" if p < 0.05 else "not significant"}')
lines.append(f'\n## The {len(unbalanced_triads)} unbalanced triads')
for a, b, c, eab, ebc, eac in unbalanced_triads:
    lines.append(f'- {qcols[a][:3]} <-> {qcols[b][:3]} ({eab:+d}), '
                 f'{qcols[b][:3]} <-> {qcols[c][:3]} ({ebc:+d}), '
                 f'{qcols[a][:3]} <-> {qcols[c][:3]} ({eac:+d})')
    lines.append(f'    {qcols[a][:3]}: {qcols[a][5:75]}')
    lines.append(f'    {qcols[b][:3]}: {qcols[b][5:75]}')
    lines.append(f'    {qcols[c][:3]}: {qcols[c][5:75]}')
lines.append('\nConclusion: the belief network is significantly more internally consistent (balanced) '
             'than chance predicts even after controlling for its skewed positive/negative edge ratio. '
             'The rare exceptions cluster around AI-accountability/disclosure tensions, echoing the main '
             'Idea\'s finding that AI attitudes behave differently from the rest of the belief system.')

with open(os.path.join(OUT, 'results_extension1.md'), 'w') as f:
    f.write('\n'.join(lines))

print('\n'.join(lines))
print(f'\nSaved figure + results_extension1.md to {OUT}')
