# Comparison with models cited in the manuscript

## Published figures reproduced in the manuscript's comparison table

| Study as cited | Model as listed or corrected | Dataset/domain as listed | Reported mAP@0.5 |
|---|---|---|---:|
| Kaur et al. (2025) | YOLOv8 | 8,850 public leaf images; 4 crops, 11 classes | 98.4% |
| Miao et al. (2025) | YOLOv8 | PlantDoc; 2,598 in-field images, 27 classes | 61.6% |
| Wang et al. (2025) | YOLOv10n | Tomato leaf; 4 diseases | 87.4% |
| Alsakar et al. (2026) | YOLOv11n–DeiT (corrected per reviewer; manuscript table says YOLOv10n) | Taiwan tomato dataset; 9 classes | 94.6% |
| This study (manuscript claim) | Improved YOLOv10 | 56,444 images; maize, cassava, and PlantVillage | 90.8% |

These are the manuscript's cited-study figures, not models retrained in this experiment. The reviewer has flagged the Alsakar model designation for correction; verify the primary citation and its metrics before submission.

## Same-proxy comparison

The local proxy uses a capped 14-class mixture from PlantVillage and PlantDoc, full-frame boxes for PlantVillage, and released boxes for PlantDoc. On its clear, all-source test set:

| 10-epoch proxy condition | Completed seeds | mAP@0.5 mean | mAP@0.5:0.95 mean |
|---|---:|---:|---:|
| Baseline YOLOv10n | 3 | 6.05% | 5.02% |
| Dehazing + YOLOv10n | 3 | 5.37% | 4.34% |
| Histogram equalization + YOLOv10n | 3 | 7.07% (SD 5.45) | 5.58% (SD 4.43) |

The equalization mean is numerically above the matched baseline mean (mAP@0.5 7.07% vs 6.05%; mAP@0.5:0.95 5.58% vs 5.02%), but paired tests across the three seeds are not significant (unadjusted p = 1.00 for each mAP metric). Equalization has high seed-to-seed variation; do not infer a reliable improvement from the higher mean.

## Interpretation

The literature values above cannot be ranked head-to-head against these proxy scores: they use different datasets, class counts, annotation/box semantics, train/test partitions, and potentially different metric implementations and operating points. In particular, Miao et al.'s reported PlantDoc score is not directly comparable to this experiment's sampled PlantDoc subset. A valid architecture comparison requires training the candidate models on the same prepared data with matched partitions, compute budgets, and evaluation code. This report does not claim that the proxy outperforms or underperforms the cited models.
