"""Compare other classifiers with Notebook 03's Random Forest and the burn rule, for the report.

Uses Notebook 03's committed point features (data/processed/ml_point_features_sangrur_2025.csv) and its exact
cross-validation: stratified 5-fold splits of the 147 labelled, harvested points, repeated 10 times (seed 0);
points never harvested are called not burnt by every method; precision, recall and F1 are scored on all 187
labelled points (`unsure` left out), once per repeat. Each model uses its library's default settings, apart from
class weights to balance burnt and not burnt where the model supports them; nothing is tuned. An exact McNemar test
asks, per repeat, whether the points only the model gets right and the points only the rule (map as reported) gets
right split unevenly.

Writes data/processed/ml_model_comparison_sangrur_2025.csv. Downloads nothing; takes about two minutes.

Run from the project folder:  python report/compare_classifiers.py
"""
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

PROJECT = Path(__file__).resolve().parent.parent
FEATURES_CSV = PROJECT / 'data' / 'processed' / 'ml_point_features_sangrur_2025.csv'
OUT = PROJECT / 'data' / 'processed' / 'ml_model_comparison_sangrur_2025.csv'
FOLDS, REPEATS, SEED = 5, 10, 0          # as in Notebook 03

MODELS = {
    # Notebook 03's forest, exactly as configured there.
    'Random Forest (Notebook 03)': lambda s: RandomForestClassifier(
        n_estimators=500, min_samples_leaf=2, max_features='sqrt', class_weight='balanced', random_state=s, n_jobs=-1),
    'Extra Trees': lambda s: ExtraTreesClassifier(
        n_estimators=500, min_samples_leaf=2, class_weight='balanced', random_state=s, n_jobs=-1),
    'Gradient boosting (HistGradientBoosting)': lambda s: HistGradientBoostingClassifier(
        class_weight='balanced', random_state=s),
    'Support vector machine (RBF kernel)': lambda s: make_pipeline(StandardScaler(), SVC(class_weight='balanced')),
    'k-nearest neighbours (k = 5)': lambda s: make_pipeline(StandardScaler(), KNeighborsClassifier(5)),
    'Logistic regression': lambda s: make_pipeline(StandardScaler(),
                                                   LogisticRegression(class_weight='balanced', max_iter=5000)),
    'Single decision tree': lambda s: DecisionTreeClassifier(min_samples_leaf=2, class_weight='balanced',
                                                             random_state=s),
}


def main():
    warnings.filterwarnings('ignore', category=UserWarning)
    pts = pd.read_csv(FEATURES_CSV)
    features = list(pts.columns[pts.columns.get_loc('peak_ndvi'):])
    assert len(features) == 23, features
    sure = pts['label'].isin(['yes', 'no']).to_numpy()
    truth = (pts['label'] == 'yes').to_numpy()
    pool = np.where(sure & pts['harvested'].astype(bool).to_numpy())[0]
    X = np.nan_to_num(pts[features].to_numpy(float), nan=0.0)      # as Notebook 03: rare gaps become 0
    rule = pts['rule_map_as_reported'].astype(bool).to_numpy()
    print(f'{sure.sum()} labelled points; {len(pool)} labelled and harvested ({truth[pool].sum()} burnt); '
          f'{len(features)} features.')

    def prf(pred):
        tp = (pred & truth & sure).sum()
        fp, fn = (pred & ~truth & sure).sum(), (~pred & truth & sure).sum()
        return tp / (tp + fp), tp / (tp + fn), 2 * tp / (2 * tp + fp + fn)

    def against_rule(pred):
        only_model = int(((pred == truth) & (rule != truth) & sure).sum())
        only_rule = int(((rule == truth) & (pred != truth) & sure).sum())
        p = binomtest(only_model, only_model + only_rule, 0.5).pvalue if only_model + only_rule else 1.0
        return only_model, only_rule, p

    rows = []
    p, r, f = prf(rule)
    rows.append({'method': 'Burn rule: map as reported (Notebook 02)', 'f1_mean': f, 'f1_min': f, 'f1_max': f,
                 'precision_mean': p, 'recall_mean': r})
    for name, make in MODELS.items():
        started = time.time()
        runs = [np.zeros(len(pts), bool) for _ in range(REPEATS)]
        splitter = RepeatedStratifiedKFold(n_splits=FOLDS, n_repeats=REPEATS, random_state=SEED)
        for k, (fit_i, test_i) in enumerate(splitter.split(pool, truth[pool])):
            model = make(SEED + k).fit(X[pool[fit_i]], truth[pool[fit_i]])
            runs[k // FOLDS][pool[test_i]] = model.predict(X[pool[test_i]]).astype(bool)
        scores = np.array([prf(run) for run in runs])
        tests = np.array([against_rule(run) for run in runs])
        rows.append({'method': name, 'f1_mean': scores[:, 2].mean(), 'f1_min': scores[:, 2].min(),
                     'f1_max': scores[:, 2].max(), 'precision_mean': scores[:, 0].mean(),
                     'recall_mean': scores[:, 1].mean(), 'only_model_right_mean': tests[:, 0].mean(),
                     'only_rule_right_mean': tests[:, 1].mean(), 'mcnemar_p_min': tests[:, 2].min(),
                     'mcnemar_p_max': tests[:, 2].max()})
        print(f'  {name}: F1 {scores[:, 2].mean():.3f} ({time.time() - started:.0f} s)')
    table = pd.DataFrame(rows)
    table.to_csv(OUT, index=False)
    print(table.round(3).to_string(index=False))
    print('Written to', OUT)


if __name__ == '__main__':
    main()
