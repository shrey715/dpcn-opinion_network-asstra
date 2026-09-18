import os
import numpy as np
import pandas as pd

LIKERT = {'Strongly Disagree': 1, 'Disagree': 2, 'Neutral': 3, 'Agree': 4, 'Strongly Agree': 5}
CSV_PATH = os.path.join(os.path.dirname(__file__), 'Survey_Results_UC.csv')


def load_complete():
    """Returns (X, qcols, cat_of) — X is the 68-respondent x 60-item numeric matrix
    (fully-complete respondents only; encoding 'No Comments' and blanks as missing)."""
    df = pd.read_csv(CSV_PATH)
    qcols = list(df.columns[1:])
    num = df[qcols].apply(lambda c: c.map(LIKERT))
    complete = num.dropna()
    X = complete.values.astype(float)
    cat_of = np.array([c[0] for c in qcols])
    return X, qcols, cat_of


def permutation_null(X, stat_fn, B=200, seed=0):
    """Generic permutation null: shuffle each column of X independently B times,
    apply stat_fn(Xp) -> value each time. Returns list of B null values."""
    rng = np.random.default_rng(seed)
    return [stat_fn(rng.permuted(X, axis=0)) for _ in range(B)]


def pval(obs, null_vals, greater=True):
    null_vals = np.asarray(null_vals)
    if greater:
        return (np.sum(null_vals >= obs) + 1) / (len(null_vals) + 1)
    return (np.sum(null_vals <= obs) + 1) / (len(null_vals) + 1)
