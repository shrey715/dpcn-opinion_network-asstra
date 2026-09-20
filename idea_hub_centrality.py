import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy import stats
from data_utils import load_complete, permutation_null, pval

OUT = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUT, exist_ok=True)

X, qcols, cat_of = load_complete()
m = len(qcols)
t_idx = np.where(cat_of == 'T')[0]

def build_graph(C, thresh=0.15):
    G = nx.Graph()
    G.add_nodes_from(range(m))
    for i in range(m):
        for j in range(i + 1, m):
            r = C[i, j]
            if np.isfinite(r) and abs(r) >= thresh:
                G.add_edge(i, j, weight=abs(r))
    return G

def eig_gap_stat(Xp):
    Cp = np.corrcoef(Xp, rowvar=False)
    Gp = build_graph(Cp)
    if Gp.number_of_edges() == 0:
        return 0.0
    eig = nx.eigenvector_centrality(Gp, weight='weight', max_iter=1000)
    eigT = np.mean([eig.get(i, 0) for i in t_idx])
    eignT = np.mean([eig.get(i, 0) for i in range(m) if i not in t_idx])
    return eignT - eigT

# ---- observed network ----
C = np.corrcoef(X, rowvar=False)
G = build_graph(C)
eig = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
pr = nx.pagerank(G, weight='weight')
btw = nx.betweenness_centrality(G, weight=lambda u, v, d: 1 / d['weight'])

eigT = np.mean([eig[i] for i in t_idx])
eignT = np.mean([eig[i] for i in range(m) if i not in t_idx])
obs_gap = eignT - eigT

top_hubs = sorted(eig.items(), key=lambda x: -x[1])[:8]
bottom = sorted(eig.items(), key=lambda x: x[1])[:5]

# ---- PageRank vs eigenvector centrality: do we need both? ----
eig_arr = np.array([eig[i] for i in range(m)])
pr_arr = np.array([pr[i] for i in range(m)])
btw_arr = np.array([btw[i] for i in range(m)])
rho_eig_pr, _ = stats.spearmanr(eig_arr, pr_arr)

btw_T = btw_arr[t_idx].mean()
btw_nonT = btw_arr[[i for i in range(m) if i not in t_idx]].mean()
top5_btw = sorted(range(m), key=lambda i: -btw_arr[i])[:5]

# ---- robustness check: row-centered (ipsatized) item-item correlation ----
row_mean_resp = X.mean(axis=1)
Xr = X - row_mean_resp[:, None]
Cr = np.corrcoef(Xr, rowvar=False)
Gr_check = build_graph(Cr)
eig_r = nx.eigenvector_centrality(Gr_check, weight='weight', max_iter=1000)
eigT_r = np.mean([eig_r.get(i, 0) for i in t_idx])
eignT_r = np.mean([eig_r.get(i, 0) for i in range(m) if i not in t_idx])
obs_gap_row_centered = eignT_r - eigT_r

# k-core backbone
G_thresh = nx.Graph()
G_thresh.add_nodes_from(range(m))
for i in range(m):
    for j in range(i + 1, m):
        if abs(C[i, j]) >= 0.30:
            G_thresh.add_edge(i, j)
core_num = nx.core_number(G_thresh)
max_core = max(core_num.values())
backbone = [n for n, k in core_num.items() if k == max_core]
backbone_cats = [cat_of[n] for n in backbone]

# ---- significance test ----
null_gap = permutation_null(X, eig_gap_stat, B=1000, seed=0)
p = pval(obs_gap, null_gap)

# ---- figure: eigenvector centrality by statement, colored by category ----
order = np.argsort(-np.array([eig[i] for i in range(m)]))
colors = {'T': '#e74c3c', 'E': '#3498db', 'S': '#2ecc71', 'V': '#9b59b6'}
fig, ax = plt.subplots(figsize=(14, 6))
vals = [eig[i] for i in order]
bar_colors = [colors[cat_of[i]] for i in order]
labels = [qcols[i][:3] for i in order]
ax.bar(range(m), vals, color=bar_colors)
ax.set_xticks(range(m))
ax.set_xticklabels(labels, rotation=90, fontsize=6)
ax.set_ylabel('Eigenvector centrality')
ax.set_title('Statement hub-centrality (red=Technology) — Tech items cluster at the low end')
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors.values()]
ax.legend(handles, colors.keys(), title='Block')
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'centrality_by_statement.png'), dpi=150)
plt.close(fig)

# ---- figure: permutation null histogram vs observed ----
fig, ax = plt.subplots(figsize=(7, 5))
ax.hist(null_gap, bins=30, color='#bdc3c7', label='permutation null (n=1000)')
ax.axvline(obs_gap, color='#e74c3c', linewidth=2, label=f'observed gap = {obs_gap:.3f}')
ax.set_xlabel('non-Technology minus Technology eigenvector centrality')
ax.set_ylabel('count')
ax.set_title(f'Significance test: p = {p:.4f}')
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'significance_test.png'), dpi=150)
plt.close(fig)

# ---- figure: the network itself (flagship visualization) ----
pos = nx.spring_layout(G, weight='weight', k=2.0 / np.sqrt(m), iterations=400, seed=7)

edge_list = list(G.edges(data=True))
w = np.array([d['weight'] for _, _, d in edge_list])
w_norm = (w - w.min()) / (w.max() - w.min() + 1e-9)
segments = [[pos[u], pos[v]] for u, v, _ in edge_list]
edge_colors = np.tile([0.25, 0.25, 0.25, 1.0], (len(w_norm), 1))
edge_colors[:, 3] = 0.03 + 0.45 * w_norm
lc = LineCollection(segments, colors=edge_colors, linewidths=0.3 + 1.8 * w_norm, zorder=1)

fig, ax = plt.subplots(figsize=(16, 14))
ax.add_collection(lc)

backbone_set = set(backbone)
xs = np.array([pos[i][0] for i in range(m)])
ys = np.array([pos[i][1] for i in range(m)])
sizes = 250 + 7000 * np.array([eig[i] for i in range(m)])
node_colors = [colors[cat_of[i]] for i in range(m)]
edge_widths = [2.4 if i in backbone_set else 0.6 for i in range(m)]
edge_edgecolors = ['black' if i in backbone_set else 'white' for i in range(m)]

ax.scatter(xs, ys, s=sizes, c=node_colors, edgecolors=edge_edgecolors,
           linewidths=edge_widths, zorder=2)

hub_ids = set(i for i, _ in top_hubs) | set(i for i, _ in bottom)
for i in range(m):
    fontsize = 9 if i in hub_ids else 5.5
    ax.annotate(qcols[i][:3], (xs[i], ys[i]), fontsize=fontsize, color='black',
                ha='center', va='center', zorder=3)

cat_names = {'T': 'Technology', 'E': 'Education', 'S': 'Society/Ethics', 'V': 'Environment/Values'}
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c, markersize=12, label=cat_names[k])
           for k, c in colors.items()]
handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                           markeredgecolor='black', markeredgewidth=2, markersize=12,
                           label=f'Backbone: {len(backbone)} statements,\n'
                                 f'≥{max_core} strong links each (black ring)'))
ax.legend(handles=handles, loc='upper left', fontsize=10, framealpha=0.9)
ax.set_title('Statement co-endorsement network — node size = eigenvector centrality\n'
             'Technology nodes (red) are small and pushed to the periphery', fontsize=14)
ax.set_xticks([]); ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'network_graph.png'), dpi=220)
plt.close(fig)

# ---- results summary ----
lines = []
lines.append('# Idea — Hub-statement centrality: AI attitudes are structurally decoupled\n')
lines.append(f'Network: {m} statement nodes, edges = pairwise |r| >= 0.15 ({G.number_of_edges()} edges).\n')
lines.append('## Top 8 hub statements (eigenvector centrality)')
for i, v in top_hubs:
    lines.append(f'- {v:.3f}  {qcols[i][:3]}  {qcols[i][5:90]}')
lines.append('\n## 5 most peripheral statements (lowest eigenvector centrality)')
for i, v in bottom:
    lines.append(f'- {v:.3f}  {qcols[i][:3]}  {qcols[i][5:90]}')
lines.append(f'\n## k-core backbone (|r|>=0.30 graph)')
lines.append(f'Max core = {max_core}-core, {len(backbone)} members. Category counts: '
             + str({c: backbone_cats.count(c) for c in set(backbone_cats)}))
lines.append(f'The largest k for which a k-core exists at |r|>=0.30 is {max_core}; that {len(backbone)}-node '
             f'subgraph is the backbone (k is a connectivity requirement, not a node count).')

lines.append('\n## PageRank and betweenness: do they add anything beyond eigenvector centrality?')
lines.append(f'Spearman correlation between eigenvector centrality and PageRank across all {m} statements: '
             f'{rho_eig_pr:.3f}. The two rankings are almost identical, so PageRank does not surface any '
             f'ordering that eigenvector centrality does not already capture on this graph.')
lines.append(f'Betweenness centrality (bridging power) mean: Technology = {btw_T:.4f}, '
             f'non-Technology = {btw_nonT:.4f}. Top-5 by betweenness: '
             + ', '.join(qcols[i][:3] for i in top5_btw) + '.')

lines.append('\n## Significance test')
lines.append(f'Statistic: mean eigenvector centrality (non-Tech) - mean eigenvector centrality (Tech)')
lines.append(f'Observed = {obs_gap:.4f}')
lines.append(f'Permutation null (B=1000): mean = {np.mean(null_gap):.4f}, std = {np.std(null_gap):.4f}')
lines.append(f'p-value = {p:.4f}' + (' (floor — 0/1000 permutations matched or exceeded observed)' if p <= 1/1001 else ''))

lines.append('\n## Robustness check: row-centered (ipsatized) correlation matrix')
lines.append(f'Recomputing the same graph after subtracting each respondent\'s own mean response across all '
             f'{m} items (removing each person\'s general tendency to agree or disagree) before computing '
             f'item-item correlations: the centrality gap falls from {obs_gap:.4f} to {obs_gap_row_centered:.4f}.')
lines.append('This does not prove the raw-data finding is spurious; a shared general disposition toward '
             'pro-social, pro-environment statements could itself be a genuine attitude rather than a survey '
             'artifact. But the data cannot distinguish "Technology attitudes are substantively decoupled" '
             'from "this gap is mostly a general agreement/response-style factor that happens to load '
             'unevenly across blocks," and both readings should be reported together rather than only the '
             'first.')

lines.append(f'\nConclusion: in the raw correlation matrix, Technology-block statements are significantly '
             f'less central to the class\'s belief network than everything else, and this pattern survives '
             f'a stricter permutation test (B=1000). Most of that gap, however, is attributable to a general '
             f'agreement factor rather than to Technology specifically; see the robustness check above.')

with open(os.path.join(OUT, 'results.md'), 'w') as f:
    f.write('\n'.join(lines))

print('\n'.join(lines))
print(f'\nSaved figures + results.md to {OUT}')
