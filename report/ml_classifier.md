# ML burn classifier: why a Random Forest, and how other models compare

**Question.** Notebook 03 trained a Random Forest to tell burnt from unburnt harvested fields. Why that model, and would another one have done better?

This draft is for Section 5 (Method) and Section 6 (Findings) of the report.

**Labels**, as in `mission_tradeoff.md`:
- **[Reported]** comes from a cited source.
- **[Ours]** was measured in this project, for Sangrur district in the 2025 season.
- **[Recommendation]** is our judgement.

## 1. What the classifier had to do

- **Task:** call each harvested 20 m pixel burnt or not burnt. Each pixel is described by 23 numbers from its season: the crop before harvest, how dark the field turned after harvest, the timing, and what followed [Ours].
- **Labels to learn from:** 147 labelled points on harvested fields, 69 of them burnt. They were interpreted from imagery at the centres of uniform 3 × 3 blocks, not visited in the field [Ours].
- **What it had to beat:** Notebook 02's three-threshold burn rule (NBR, MIRBI and near-infrared). Against the same labels, the rule's map scores F1 0.92 [Ours].
- **So the question was narrow:** does a model that learns from the labels beat a simple rule, not which model is best in general. The model had to be a fair challenger to the rule [Recommendation].

## 2. Why a Random Forest

- **Few labels.** A Random Forest averages many decision trees, each grown on a random resample of the training points, choosing from a random subset of the features at each split (Breiman 2001) [Reported]. Averaging keeps it stable on small samples, and it works with its usual settings, so nothing had to be tuned on 147 points [Recommendation].
- **Tabular data.** Each point is a row of 23 numbers. On a benchmark of tabular datasets of about 10,000 rows, tree-based models remain state of the art against deep learning (Grinsztajn et al. 2022) [Reported]. Our 147 rows are far fewer. Deep learning on image patches or time series needs thousands of labels, so it was not an option [Recommendation].
- **A threshold-shaped signal.** A burn is "dark in near-infrared, NBR low and MIRBI high". Trees split on thresholds and combine them, so a forest can learn the rule's kind of test, or a better one, from the labels [Recommendation].
- **Practical.**
  - The inputs need no rescaling, and related features do no harm.
  - Class weights balance burnt and not burnt.
  - It trains on a laptop CPU in under a minute.
  - Permutation importance shows what it relied on (section 4) [Ours].
- **Precedent.** Walker et al. (2022) used a Random Forest on PlanetScope and Sentinel-2 imagery to detect crop burning in Punjab, and reached 82% overall accuracy against ground records [Reported].

## 3. How other models compare

**Method** [Ours]:
- **Data and splits:** six other common classifiers, run on Notebook 03's own features with its exact cross-validation. The 147 labelled harvested points are split into 5 folds, and this is repeated 10 times. Every point is predicted by a model that never saw it.
- **Scoring:** points never harvested are called not burnt by every method, and scores are taken on all 187 labelled points.
- **Settings:** each model uses its library's default settings, with class weights where it supports them. Nothing is tuned.
- **Test against the rule:** a McNemar test asks, in each of the 10 runs, whether the points only the model gets right and the points only the rule gets right split unevenly.
- **Reproducible:** `report/compare_classifiers.py` writes the table to `data/processed/ml_model_comparison_sangrur_2025.csv` in about two minutes.

| Method | F1, mean (range over 10 runs) | Precision | Recall | Points only the model gets right / only the rule gets right (mean per run) | McNemar p against the rule |
|---|---|---|---|---|---|
| Burn rule: map as reported | 0.92 | 0.87 | 0.97 | – | – |
| **Random Forest** (Notebook 03) | 0.92 (0.88–0.94) | 0.91 | 0.93 | 5.8 / 4.6 | 0.39–1.00 |
| Extra Trees | 0.94 (0.91–0.96) | 0.94 | 0.94 | 7.1 / 3.9 | 0.15–1.00 |
| Gradient boosting (HistGradientBoosting) | 0.92 (0.89–0.93) | 0.91 | 0.92 | 6.3 / 5.8 | 0.39–1.00 |
| Support vector machine (RBF kernel) | 0.92 (0.91–0.93) | 0.96 | 0.89 | 8.3 / 6.6 | 0.61–1.00 |
| k-nearest neighbours (k = 5) | 0.91 (0.89–0.93) | 0.90 | 0.93 | 5.5 / 5.6 | 0.39–1.00 |
| Logistic regression | 0.90 (0.88–0.93) | 0.90 | 0.91 | 5.5 / 6.8 | 0.27–1.00 |
| Single decision tree | 0.89 (0.87–0.91) | 0.87 | 0.91 | 5.8 / 9.6 | 0.24–1.00 |

**Reading the table** [Ours]:
- **All models score about the same:** F1 from 0.89 to 0.94, around the rule's 0.92.
- **None beats the rule beyond chance:** the McNemar p is never below 0.14, in any run of any model (lowest 0.146, Extra Trees).
- **Extra Trees scores highest (0.94), but only just:** its edge over the rule is about 3 of 187 points per run (7.1 against 3.9). Picking the best of seven models on the same splits also flatters the winner.
- **Different trade-offs:** the rule finds almost every labelled burn (recall 0.97) at the cost of more false alarms (precision 0.87). The models give up some recall for precision. This fits the rule mapping more burnt area than the forest (71,600 ha for every burn against 55,700 ha; Notebook 03).
- **The simplest models do a little worse.** A single tree is unstable from sample to sample, and logistic regression can only draw a straight boundary through the features (F1 0.89 and 0.90).

## 4. What it means

- **The limit is the labels and the signal, not the model** [Ours]:
  - The forest's F1 levels off at about 0.92 from 40 training points, level with the rule (Notebook 03's learning curve).
  - Shuffling the features that describe how dark the field turned after harvest cuts its F1 by 0.45. Shuffling any other group changes it by less than 0.01.
  - Every model is reading the same signal the rule tests.
- **Keep the rule as the map** [Recommendation]:
  - No model adds accuracy at the labelled points.
  - The rule needs no labels to train, is easier to explain, and carries to another season unchanged, as the 2021 run did.
  - This is the decision logged on 31 Oct 2026. The forest's map is kept as a cross-check of where the two methods agree.
- **What could raise accuracy instead** [Recommendation]:
  - labels at field edges and in small burnt patches, where the forest's and the rule's maps disagree most
  - labels from field visits
  - new information that optical images can't give, such as Sentinel-1 radar through cloud and smoke (`mission_tradeoff.md`)

## 5. Limits

- **No tuning** [Ours]: every model ran with default settings. Tuning would need a second, inner round of cross-validation, which 147 points can barely support [Recommendation].
- **Same labels for training and scoring** [Ours]: the models learn from the same image-interpreted labels they are scored on.
- **Block centres only** [Ours]: the labels sit at block centres, so no method was tested at field edges or in small patches.
- **One season, one district** [Ours]: Sangrur, 2025.

## Sources

- Breiman, L. (2001). Random forests. *Machine Learning* 45, 5–32. https://doi.org/10.1023/A:1010933404324 (in `methodology/methodology.md`).
- Grinsztajn, L., Oyallon, E. and Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? NeurIPS 2022, Datasets and Benchmarks track. https://arxiv.org/abs/2207.08815 (accessed 2026-11-03).
- Walker, K. et al. (2022). Detecting crop burning in India using satellite data. arXiv:2209.10148 (preprint). https://arxiv.org/abs/2209.10148 (accessed 2026-10-31).
- **Our numbers:**
  - this comparison: `data/processed/ml_model_comparison_sangrur_2025.csv`, written by `report/compare_classifiers.py`
  - Notebook 03's results: `ml_accuracy_sangrur_2025.csv`, `ml_learning_curve_sangrur_2025.csv`, `ml_feature_importance_sangrur_2025.csv` and `ml_map_comparison_sangrur_2025.csv`, in `data/processed/`
