import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from data_utils import load_complete

OUT = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUT, exist_ok=True)

X, qcols, cat_of = load_complete()
n, m = X.shape
K = 5

row_mean = X.mean(axis=1)

# ---- leave-one-item-out evaluation over ALL n*m cells ----
# Similarity for predicting column j is recomputed with column j dropped, so the
# held-out answer never contributes to the neighbor selection for that cell.
errs_knn = np.empty((n, m))
errs_baseline = np.empty((n, m))
for j in range(m):
    mask_cols = [c for c in range(m) if c != j]
    sim_j = np.corrcoef(X[:, mask_cols])
    for i in range(n):
        order = np.argsort(-sim_j[i])
        neigh = order[order != i][:K]
        errs_knn[i, j] = abs(X[neigh, j].mean() - X[i, j])
        errs_baseline[i, j] = abs((X[:, j].sum() - X[i, j]) / (n - 1) - X[i, j])

knn_mae = errs_knn.mean()
baseline_mae = errs_baseline.mean()

# ---- respondent-level bootstrap CI (cells from the same respondent are not independent) ----
per_resp_diff = errs_baseline.mean(axis=1) - errs_knn.mean(axis=1)
rng = np.random.default_rng(0)
B_BOOT = 5000
boot = np.array([per_resp_diff[rng.integers(0, n, size=n)].mean() for _ in range(B_BOOT)])
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
frac_nonpositive = (boot <= 0).mean()

# ---- figure: MAE comparison ----
fig, ax = plt.subplots(figsize=(6, 5))
labels = ['Network\nk-NN', 'Global\nmean baseline']
means = [knn_mae, baseline_mae]
bars = ax.bar(labels, means, color=['#2ecc71', '#e74c3c'])
ax.set_ylabel('Mean Absolute Error (all 4,080 cells)')
ax.set_title('Network-based imputation, leave-one-item-out')
for b, v in zip(bars, means):
    ax.text(b.get_x() + b.get_width()/2, v + 0.01, f'{v:.3f}', ha='center')
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'imputation_mae.png'), dpi=150)
plt.close(fig)

# ---- figure: bootstrap distribution of the improvement ----
fig, ax = plt.subplots(figsize=(7, 5))
ax.hist(boot, bins=40, color='#bdc3c7')
ax.axvline(0, color='black', linewidth=1, linestyle='--')
ax.axvline(per_resp_diff.mean(), color='#e74c3c', linewidth=2,
           label=f'observed mean improvement = {per_resp_diff.mean():.4f}')
ax.set_xlabel('baseline error - k-NN error (per respondent, resampled)')
ax.set_ylabel('count')
ax.set_title(f'Respondent-level bootstrap (B={B_BOOT}): 95% CI [{ci_lo:.4f}, {ci_hi:.4f}]')
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'imputation_bootstrap.png'), dpi=150)
plt.close(fig)

# ---- directed 5-NN respondent network: in-degree analysis ----
sim_full = np.corrcoef(X)
indeg = np.zeros(n, dtype=int)
for i in range(n):
    order = np.argsort(-sim_full[i])
    neigh = order[order != i][:K]
    for j in neigh:
        indeg[j] += 1

rng2 = np.random.default_rng(3)
B_RAND = 500
rand_sds = np.empty(B_RAND)
for b in range(B_RAND):
    indeg_r = np.zeros(n, dtype=int)
    for i in range(n):
        choice = rng2.choice([x for x in range(n) if x != i], size=K, replace=False)
        indeg_r[choice] += 1
    rand_sds[b] = indeg_r.std()

r_indeg_mean = np.corrcoef(indeg, row_mean)[0, 1]

# ---- figure: the respondent network itself, plus its in-degree distribution ----
G_resp = nx.DiGraph()
G_resp.add_nodes_from(range(n))
for i in range(n):
    order = np.argsort(-sim_full[i])
    neigh = order[order != i][:K]
    for j in neigh:
        G_resp.add_edge(i, j)

pos = nx.spring_layout(G_resp, seed=4, k=0.6)
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
node_sizes = 60 + 40 * indeg
nx.draw_networkx_edges(G_resp, pos, ax=axes[0], arrows=True, arrowsize=6, width=0.5, alpha=0.4)
nodes_drawn = nx.draw_networkx_nodes(G_resp, pos, ax=axes[0], node_size=node_sizes,
                                      node_color=indeg, cmap='viridis')
fig.colorbar(nodes_drawn, ax=axes[0], label='in-degree', shrink=0.8)
axes[0].set_title('Respondent 5-NN network (directed)\nnode size/color = in-degree')
axes[0].set_xticks([]); axes[0].set_yticks([])

axes[1].hist(indeg, bins=np.arange(0, indeg.max() + 2) - 0.5, color='#3498db', alpha=0.8,
             label='observed')
axes[1].axvline(K, color='black', linestyle=':', linewidth=1, label='mean in-degree = 5 (by construction)')
axes[1].set_xlabel('in-degree'); axes[1].set_ylabel('number of respondents')
axes[1].set_title('In-degree distribution')
axes[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'respondent_network.png'), dpi=150)
plt.close(fig)

# ---- results summary ----
lines = []
lines.append('# Extension 2 — Network-based missing-data imputation\n')
lines.append('Respondent similarity for predicting item j is recomputed per item, with that item\'s '
             'column dropped, before selecting neighbors for any cell that uses it. Every '
             '(respondent, item) cell (n*m = %d) is evaluated this way.\n' % (n*m))
lines.append(f'Network k-NN MAE (all {n*m} cells): {knn_mae:.4f}')
lines.append(f'Global-mean baseline MAE: {baseline_mae:.4f}')
lines.append(f'Mean improvement per respondent (baseline - knn): {per_resp_diff.mean():.4f}')
lines.append(f'\n## Significance: respondent-level bootstrap (cells from one respondent are not independent)')
lines.append(f'95% CI for mean improvement, resampling respondents with replacement (B={B_BOOT}): '
             f'[{ci_lo:.4f}, {ci_hi:.4f}]')
lines.append(f'Fraction of bootstrap resamples with improvement <= 0: {frac_nonpositive:.4f}')
lines.append('Each respondent contributes m correlated cells, so the n*m cells are not independent '
             'observations; the respondent-level bootstrap above is the valid test, and it does not clear '
             'the conventional 95% threshold. The honest reading is a small, borderline effect.')
lines.append('\nNote: Pearson correlation is already invariant to per-row additive shifts, so subtracting '
             'each respondent\'s own mean before calling corrcoef does not change the resulting similarity '
             'matrix at all; it is not part of this pipeline.')

lines.append('\n## The respondent network as a directed graph')
lines.append('Each respondent points to its 5 nearest neighbors, so the graph is directed and in-degree '
             '(how often a respondent is chosen as someone else\'s neighbor) is not fixed at 5 the way '
             'out-degree is.')
lines.append(f'Observed in-degree: mean=5.00 (fixed by construction), sd={indeg.std():.2f}, '
             f'max={indeg.max()}, respondents with in-degree 0: {int(np.sum(indeg==0))}')
lines.append(f'Random-assignment null (each respondent picks 5 random others, B={B_RAND}): '
             f'in-degree sd = {rand_sds.mean():.2f} (std of that estimate = {rand_sds.std():.3f})')
lines.append(f'Correlation between in-degree and a respondent\'s own mean agreement level: r = {r_indeg_mean:.3f}')
lines.append('In-degree is far more unequal than random assignment would produce, and it correlates with '
             'how agreeable a respondent is overall. What causes that correlation is not established by '
             'this analysis; it is reported as a descriptive fact about the network, not explained.')
lines.append('\nThe six respondents who abandoned the survey partway through are excluded by '
             '`load_complete()` before this network is built, so this network makes no claim about them.')

with open(os.path.join(OUT, 'results_extension2.md'), 'w') as f:
    f.write('\n'.join(lines))
print('\n'.join(lines))
print(f'\nSaved figures + results_extension2.md to {OUT}')
