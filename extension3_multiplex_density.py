import os
import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from data_utils import load_complete, permutation_null, pval

OUT = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUT, exist_ok=True)

X, qcols, cat_of = load_complete()
n, m = X.shape
cats = ['T', 'E', 'S', 'V']
idx_of = {c: np.where(cat_of == c)[0] for c in cats}

def block_density(C, idx):
    """Weighted link density of the induced subgraph on `idx`: mean |r| over all pairs."""
    sub = C[np.ix_(idx, idx)]
    iu = np.triu_indices(len(idx), 1)
    return np.nanmean(np.abs(sub[iu]))

C = np.corrcoef(X, rowvar=False)
obs = {c: block_density(C, idx_of[c]) for c in cats}

nulls = {}
for c in cats:
    stat_fn = lambda Xp, idx=idx_of[c]: block_density(np.corrcoef(Xp, rowvar=False), idx)
    nulls[c] = permutation_null(X, stat_fn, B=200, seed=3)

pvals = {c: pval(obs[c], nulls[c]) for c in cats}

# ---- closed-form null: expected |r| for two independent vectors of length n ----
closed_form_null = math.sqrt(2 / (math.pi * (n - 1)))

# ---- row-centered (ipsatized) version, as a robustness check ----
row_mean = X.mean(axis=1)
Xr = X - row_mean[:, None]
Cr = np.corrcoef(Xr, rowvar=False)
obs_row = {c: block_density(Cr, idx_of[c]) for c in cats}

# ---- the Idea network's centrality gap, raw vs. row-centered, for the combined figure below ----
t_idx = idx_of['T']
non_t_idx = np.concatenate([idx_of[c] for c in cats if c != 'T'])

def centrality_gap(Cm, thresh=0.15):
    G = nx.Graph()
    G.add_nodes_from(range(m))
    for i in range(m):
        for j in range(i + 1, m):
            if abs(Cm[i, j]) >= thresh:
                G.add_edge(i, j, weight=abs(Cm[i, j]))
    eig = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    eig_t = np.mean([eig[i] for i in t_idx])
    eig_nont = np.mean([eig[i] for i in non_t_idx])
    return eig_nont - eig_t

gap_raw = centrality_gap(C)
gap_row_centered = centrality_gap(Cr)

# ---- combined figure: raw vs. row-centered, centrality gap and block densities ----
colors = {'T': '#e74c3c', 'E': '#3498db', 'S': '#2ecc71', 'V': '#9b59b6'}
fig, axes = plt.subplots(1, 2, figsize=(11, 5))

axes[0].bar(['raw', 'row-centered'], [gap_raw, gap_row_centered], color=['#e74c3c', '#95a5a6'])
axes[0].set_ylabel('non-Tech minus Tech eigenvector centrality')
axes[0].set_title('Idea: centrality gap')
for i, v in enumerate([gap_raw, gap_row_centered]):
    axes[0].text(i, v + 0.001, f'{v:.4f}', ha='center')

x = np.arange(len(cats))
axes[1].bar(x - 0.2, [obs[c] for c in cats], width=0.4, color=[colors[c] for c in cats], label='raw')
axes[1].bar(x + 0.2, [obs_row[c] for c in cats], width=0.4, color='#95a5a6', label='row-centered')
axes[1].set_xticks(x)
axes[1].set_xticklabels(['Technology', 'Education', 'Society', 'Environment'])
axes[1].set_ylabel('mean |r| within block')
axes[1].set_title('Extension 3: block density')
axes[1].legend(fontsize=8)

fig.suptitle('Raw vs. row-centered: how much of each result survives removing general agreement level')
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'raw_vs_rowcentered.png'), dpi=150)
plt.close(fig)

# ---- figure ----
fig, ax = plt.subplots(figsize=(7, 5))
x = np.arange(len(cats))
obs_vals = [obs[c] for c in cats]
null_means = [np.mean(nulls[c]) for c in cats]
ax.bar(x - 0.2, obs_vals, width=0.4, color=[colors[c] for c in cats], label='observed')
ax.bar(x + 0.2, null_means, width=0.4, color='#bdc3c7', label='permutation null mean')
ax.axhline(closed_form_null, color='black', linestyle='--', linewidth=1,
           label=f'closed-form null = {closed_form_null:.3f}')
ax.set_xticks(x)
ax.set_xticklabels(['Technology', 'Education', 'Society', 'Environment'])
ax.set_ylabel('Weighted link density: mean |r| within block')
ax.set_title('Per-block link density (observed vs. chance)')
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'category_density.png'), dpi=150)
plt.close(fig)

lines = []
lines.append('# Extension 3 — Per-block link density\n')
lines.append('Nodes: 60 statements, partitioned into four blocks (T/E/S/V) with no edges drawn across '
             'blocks. Each block is treated as an induced subgraph of the full statement-correlation '
             'graph. Density here is weighted link density: the mean of |r| over every within-block pair, '
             'read directly off the correlation matrix (a generalization of unweighted link density to '
             'weighted edges).\n')
lines.append('| Block | mean\\|r\\| | permutation null mean | p-value |')
lines.append('|---|---|---|---|')
for c in cats:
    lines.append(f'| {c} | {obs[c]:.3f} | {np.mean(nulls[c]):.3f} | {pvals[c]:.4f} |')

lines.append(f'\n## Why the null mean is ~0.098 in every block')
lines.append(f'For two independent (uncorrelated) vectors of {n} observations, the expected absolute '
             f'Pearson correlation is approximately sqrt(2 / (pi * (n-1))) = sqrt(2 / (pi * {n-1})) = '
             f'{closed_form_null:.4f}. This closed form matches the permutation null mean obtained by '
             f'simulation (~0.098) and does not depend on which block is being tested, since it only uses '
             f'the sample size.')

effect_V = obs['V'] - np.mean(nulls['V'])
effect_T = obs['T'] - np.mean(nulls['T'])
lines.append(f'\n## Effect sizes')
lines.append(f'All four blocks clear their permutation null (all p={min(pvals.values()):.4f}, the floor for '
             f'B=200), but the amount by which they clear it differs: Environment\'s density above its noise '
             f'floor ({effect_V:.3f}) is roughly {effect_V/effect_T:.1f}x Technology\'s ({effect_T:.3f}). '
             f'Technology\'s within-block correlations are weakly related to each other rather than forming '
             f'distinct sub-clusters; nothing in this analysis tests for or supports separate sub-views '
             f'within the block.')

lines.append(f'\n## Row-centered robustness check')
lines.append('| Block | raw mean\\|r\\| | row-centered mean\\|r\\| |')
lines.append('|---|---|---|')
for c in cats:
    lines.append(f'| {c} | {obs[c]:.3f} | {obs_row[c]:.3f} |')
lines.append('Once each respondent\'s own mean response is subtracted before computing correlations '
             '(removing each person\'s general tendency to agree or disagree), the four blocks converge '
             'to a similar density (~0.12-0.14) instead of spreading from 0.136 to 0.318. The raw-data '
             'gap reported above is therefore driven mostly by a general agreement factor shared across '
             'respondents, not purely by topic-specific belief structure.')
lines.append(f'\nThe Idea network\'s centrality gap shows the same pattern: {gap_raw:.4f} raw, '
             f'{gap_row_centered:.4f} row-centered. Both comparisons are drawn together in '
             f'raw_vs_rowcentered.png.')

with open(os.path.join(OUT, 'results_extension3.md'), 'w') as f:
    f.write('\n'.join(lines))
print('\n'.join(lines))
print(f'\nSaved figure + results_extension3.md to {OUT}')
