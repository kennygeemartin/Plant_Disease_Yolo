# 10-epoch comparison results

> **Scope:** This is a partial public-data proxy experiment. Three seeds were completed for baseline, dehazing, and histogram equalization; the combined preprocessing condition was not run. These figures do not establish a statistically significant improvement.

## Stopping point

The planned comparison was four preprocessing methods (`baseline`, `dehaze`, `equalize`, `combined`) across seeds 11, 22, and 33. After the seed-11 equalization result exceeded its matched baseline, the remaining equalization seeds were completed to assess run-to-run variation. Nine of twelve runs are now complete: all three baseline, dehazing, and equalization seeds. The combined condition was not run.

The available 10-epoch result files contain 54 held-out evaluation rows (nine runs × six test/source configurations), with per-class outputs, confusion matrices, summary statistics, and paired tests.

## Clear, all-source held-out results

| Run | Completed seeds | mAP@0.5 mean | Sample SD | mAP@0.5:0.95 mean | Sample SD |
|---|---:|---:|---:|---:|---:|
| 5-epoch baseline (previous run) | 3 | 0.0204 | 0.0100 | 0.0124 | 0.0041 |
| 10-epoch baseline | 3 | 0.0605 | 0.0152 | 0.0502 | 0.0147 |
| 10-epoch dehazing | 3 | 0.0537 | 0.0143 | 0.0434 | 0.0133 |
| 10-epoch histogram equalization | 3 | 0.0707 | 0.0545 | 0.0558 | 0.0443 |

The equalization mean is numerically higher than the 10-epoch baseline mean for both mAP metrics. However, the paired exact Wilcoxon comparisons across three seeds were not significant (unadjusted p = 1.00 for mAP@0.5 and mAP@0.5:0.95), and equalization had high seed-to-seed variation.

## Interpretation

The 10-epoch baseline mean exceeds the previous 5-epoch baseline mean. The equalization three-seed mean is slightly above the 10-epoch baseline, but the paired test and large variability do not support claiming a reliable improvement. Dehazing's mean is below the 10-epoch baseline. The manuscript's proposed *combined* dehazing-plus-equalization condition has no 10-epoch results, so this experiment does not test the full proposed preprocessing pipeline at 10 epochs.

The manuscript also cites YOLOv8 and YOLOv10/YOLOv11-based studies. Their published scores use different datasets and protocols and cannot be ranked head-to-head against this proxy. See `MANUSCRIPT_MODEL_COMPARISON.md` for those reported figures and the comparability caveat.

Full per-run records are in `run_metrics.csv`; per-class results are in `per_class_metrics.csv`; paired comparisons are in `paired_wilcoxon.csv`; epoch-level logs and weights are in each run directory. The experiment configuration is in `experiment_config.json`. Model checkpoints and training folders are intentionally excluded from repository publication.
