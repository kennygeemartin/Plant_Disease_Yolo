# Public-data proxy experiment results

> **Scope:** Results below are from a separate public-data proxy experiment, not measurements from the submitted study.

## Protocol

- Model: `yolov10n.yaml`; Ultralytics 8.3.40.
- Loss: Ultralytics' default YOLOv10 detection loss; no custom loss or loss components were supplied. Default box/classification/DFL weights are 7.5/0.5/1.5.
- Image size: 320; batch: 4; epochs: 10; seeds: 11, 22, 33; device: CPU.
- Same source images and image-level 80/10/10 split across all conditions; preprocessing is applied after splitting.
- Test conditions are clear and simulated haze (I = 0.68J + 0.32×235). Simulated haze is not a measured field condition.
- Results are reported for the mixed test set and separately for the PlantVillage and PlantDoc public-proxy subsets.
- Both image-classification sources are converted to one full-frame box per image. These metrics do not evaluate leaf/lesion localization.
- The five PlantDoc generic 'leaf' labels are mapped to matching PlantVillage healthy labels by name only; this cross-source assumption is not verified and may introduce label error.
- PlantDoc's generic pepper 'leaf spot' label is crosswalked to PlantVillage bacterial spot by name; the causal agent is not verified.
- Reported precision/recall/F1 use the detector's validation operating point; AP is the area under the precision-recall curve. Detection accuracy is not reported.
- Confidence intervals are two-sided 95% Student-t intervals across seeds. With only three runs, intervals are very imprecise and the untransformed interval limits may extend outside the metrics' [0, 1] range; those limits should not be interpreted as possible metric values. Paired exact Wilcoxon p-values are unadjusted and underpowered.

## Metrics across independent seeds

| Method | Test | Source | Metric | n | Mean | SD | 95% CI |
|---|---|---|---:|---:|---:|---:|---:|
| baseline | clear | all | precision | 3 | 0.2614 | 0.4400 | [-0.8318, 1.3545] |
| baseline | clear | all | recall | 3 | 0.3413 | 0.2553 | [-0.2929, 0.9755] |
| baseline | clear | all | f1 | 3 | 0.0235 | 0.0163 | [-0.0170, 0.0639] |
| baseline | clear | all | map50 | 3 | 0.0605 | 0.0152 | [0.0227, 0.0984] |
| baseline | clear | all | map50_95 | 3 | 0.0502 | 0.0147 | [0.0138, 0.0866] |
| dehaze | clear | all | precision | 3 | 0.1060 | 0.1741 | [-0.3265, 0.5386] |
| dehaze | clear | all | recall | 3 | 0.3167 | 0.2492 | [-0.3024, 0.9357] |
| dehaze | clear | all | f1 | 3 | 0.0146 | 0.0068 | [-0.0024, 0.0316] |
| dehaze | clear | all | map50 | 3 | 0.0537 | 0.0143 | [0.0181, 0.0892] |
| dehaze | clear | all | map50_95 | 3 | 0.0434 | 0.0133 | [0.0103, 0.0766] |
| equalize | clear | all | precision | 3 | 0.1628 | 0.2760 | [-0.5228, 0.8484] |
| equalize | clear | all | recall | 3 | 0.2563 | 0.1962 | [-0.2311, 0.7437] |
| equalize | clear | all | f1 | 3 | 0.0194 | 0.0222 | [-0.0356, 0.0745] |
| equalize | clear | all | map50 | 3 | 0.0707 | 0.0545 | [-0.0647, 0.2061] |
| equalize | clear | all | map50_95 | 3 | 0.0558 | 0.0443 | [-0.0542, 0.1658] |
| combined | clear | all | precision | 0 | NA | NA | [NA, NA] |
| combined | clear | all | recall | 0 | NA | NA | [NA, NA] |
| combined | clear | all | f1 | 0 | NA | NA | [NA, NA] |
| combined | clear | all | map50 | 0 | NA | NA | [NA, NA] |
| combined | clear | all | map50_95 | 0 | NA | NA | [NA, NA] |
| baseline | clear | plantvillage | precision | 3 | 0.2612 | 0.4373 | [-0.8253, 1.3476] |
| baseline | clear | plantvillage | recall | 3 | 0.6495 | 0.4612 | [-0.4963, 1.7952] |
| baseline | clear | plantvillage | f1 | 3 | 0.0352 | 0.0313 | [-0.0426, 0.1130] |
| baseline | clear | plantvillage | map50 | 3 | 0.1443 | 0.0372 | [0.0519, 0.2368] |
| baseline | clear | plantvillage | map50_95 | 3 | 0.1257 | 0.0367 | [0.0344, 0.2169] |
| dehaze | clear | plantvillage | precision | 3 | 0.0347 | 0.0431 | [-0.0723, 0.1417] |
| dehaze | clear | plantvillage | recall | 3 | 0.9167 | 0.0899 | [0.6934, 1.1399] |
| dehaze | clear | plantvillage | f1 | 3 | 0.0211 | 0.0065 | [0.0050, 0.0371] |
| dehaze | clear | plantvillage | map50 | 3 | 0.1541 | 0.0436 | [0.0457, 0.2624] |
| dehaze | clear | plantvillage | map50_95 | 3 | 0.1312 | 0.0357 | [0.0426, 0.2199] |
| equalize | clear | plantvillage | precision | 3 | 0.3793 | 0.3359 | [-0.4552, 1.2139] |
| equalize | clear | plantvillage | recall | 3 | 0.4048 | 0.5204 | [-0.8880, 1.6975] |
| equalize | clear | plantvillage | f1 | 3 | 0.0328 | 0.0367 | [-0.0584, 0.1239] |
| equalize | clear | plantvillage | map50 | 3 | 0.1618 | 0.0666 | [-0.0036, 0.3272] |
| equalize | clear | plantvillage | map50_95 | 3 | 0.1312 | 0.0523 | [0.0014, 0.2610] |
| combined | clear | plantvillage | precision | 0 | NA | NA | [NA, NA] |
| combined | clear | plantvillage | recall | 0 | NA | NA | [NA, NA] |
| combined | clear | plantvillage | f1 | 0 | NA | NA | [NA, NA] |
| combined | clear | plantvillage | map50 | 0 | NA | NA | [NA, NA] |
| combined | clear | plantvillage | map50_95 | 0 | NA | NA | [NA, NA] |
| baseline | clear | plantdoc | precision | 3 | 0.0038 | 0.0021 | [-0.0013, 0.0090] |
| baseline | clear | plantdoc | recall | 3 | 0.2080 | 0.0585 | [0.0628, 0.3533] |
| baseline | clear | plantdoc | f1 | 3 | 0.0074 | 0.0039 | [-0.0023, 0.0172] |
| baseline | clear | plantdoc | map50 | 3 | 0.0325 | 0.0135 | [-0.0010, 0.0660] |
| baseline | clear | plantdoc | map50_95 | 3 | 0.0223 | 0.0139 | [-0.0122, 0.0568] |
| dehaze | clear | plantdoc | precision | 3 | 0.2396 | 0.4110 | [-0.7815, 1.2607] |
| dehaze | clear | plantdoc | recall | 3 | 0.1158 | 0.0697 | [-0.0573, 0.2888] |
| dehaze | clear | plantdoc | f1 | 3 | 0.0122 | 0.0136 | [-0.0216, 0.0460] |
| dehaze | clear | plantdoc | map50 | 3 | 0.0117 | 0.0113 | [-0.0163, 0.0397] |
| dehaze | clear | plantdoc | map50_95 | 3 | 0.0042 | 0.0025 | [-0.0020, 0.0104] |
| equalize | clear | plantdoc | precision | 3 | 0.0280 | 0.0442 | [-0.0818, 0.1378] |
| equalize | clear | plantdoc | recall | 3 | 0.1100 | 0.0807 | [-0.0905, 0.3105] |
| equalize | clear | plantdoc | f1 | 3 | 0.0045 | 0.0012 | [0.0015, 0.0075] |
| equalize | clear | plantdoc | map50 | 3 | 0.0094 | 0.0088 | [-0.0126, 0.0313] |
| equalize | clear | plantdoc | map50_95 | 3 | 0.0051 | 0.0062 | [-0.0104, 0.0206] |
| combined | clear | plantdoc | precision | 0 | NA | NA | [NA, NA] |
| combined | clear | plantdoc | recall | 0 | NA | NA | [NA, NA] |
| combined | clear | plantdoc | f1 | 0 | NA | NA | [NA, NA] |
| combined | clear | plantdoc | map50 | 0 | NA | NA | [NA, NA] |
| combined | clear | plantdoc | map50_95 | 0 | NA | NA | [NA, NA] |
| baseline | hazy | all | precision | 3 | 0.0065 | 0.0003 | [0.0057, 0.0073] |
| baseline | hazy | all | recall | 3 | 0.4550 | 0.0265 | [0.3890, 0.5209] |
| baseline | hazy | all | f1 | 3 | 0.0127 | 0.0006 | [0.0111, 0.0142] |
| baseline | hazy | all | map50 | 3 | 0.0417 | 0.0053 | [0.0286, 0.0549] |
| baseline | hazy | all | map50_95 | 3 | 0.0348 | 0.0041 | [0.0245, 0.0450] |
| dehaze | hazy | all | precision | 3 | 0.0055 | 0.0013 | [0.0023, 0.0087] |
| dehaze | hazy | all | recall | 3 | 0.4667 | 0.0230 | [0.4096, 0.5238] |
| dehaze | hazy | all | f1 | 3 | 0.0107 | 0.0025 | [0.0046, 0.0169] |
| dehaze | hazy | all | map50 | 3 | 0.0457 | 0.0256 | [-0.0180, 0.1093] |
| dehaze | hazy | all | map50_95 | 3 | 0.0373 | 0.0187 | [-0.0091, 0.0837] |
| equalize | hazy | all | precision | 3 | 0.0070 | 0.0065 | [-0.0093, 0.0232] |
| equalize | hazy | all | recall | 3 | 0.3425 | 0.1508 | [-0.0321, 0.7171] |
| equalize | hazy | all | f1 | 3 | 0.0129 | 0.0115 | [-0.0158, 0.0415] |
| equalize | hazy | all | map50 | 3 | 0.0624 | 0.0575 | [-0.0806, 0.2053] |
| equalize | hazy | all | map50_95 | 3 | 0.0505 | 0.0488 | [-0.0707, 0.1718] |
| combined | hazy | all | precision | 0 | NA | NA | [NA, NA] |
| combined | hazy | all | recall | 0 | NA | NA | [NA, NA] |
| combined | hazy | all | f1 | 0 | NA | NA | [NA, NA] |
| combined | hazy | all | map50 | 0 | NA | NA | [NA, NA] |
| combined | hazy | all | map50_95 | 0 | NA | NA | [NA, NA] |
| baseline | hazy | plantvillage | precision | 3 | 0.0086 | 0.0017 | [0.0044, 0.0128] |
| baseline | hazy | plantvillage | recall | 3 | 0.9286 | 0.0945 | [0.6938, 1.1633] |
| baseline | hazy | plantvillage | f1 | 3 | 0.0169 | 0.0033 | [0.0086, 0.0252] |
| baseline | hazy | plantvillage | map50 | 3 | 0.1389 | 0.0167 | [0.0975, 0.1803] |
| baseline | hazy | plantvillage | map50_95 | 3 | 0.1208 | 0.0148 | [0.0840, 0.1575] |
| dehaze | hazy | plantvillage | precision | 3 | 0.0081 | 0.0029 | [0.0010, 0.0152] |
| dehaze | hazy | plantvillage | recall | 3 | 0.9762 | 0.0412 | [0.8737, 1.0786] |
| dehaze | hazy | plantvillage | f1 | 3 | 0.0160 | 0.0054 | [0.0026, 0.0293] |
| dehaze | hazy | plantvillage | map50 | 3 | 0.1373 | 0.0521 | [0.0079, 0.2667] |
| dehaze | hazy | plantvillage | map50_95 | 3 | 0.1157 | 0.0393 | [0.0180, 0.2133] |
| equalize | hazy | plantvillage | precision | 3 | 0.2263 | 0.3758 | [-0.7072, 1.1599] |
| equalize | hazy | plantvillage | recall | 3 | 0.6429 | 0.5285 | [-0.6701, 1.9558] |
| equalize | hazy | plantvillage | f1 | 3 | 0.0198 | 0.0101 | [-0.0053, 0.0448] |
| equalize | hazy | plantvillage | map50 | 3 | 0.1620 | 0.0819 | [-0.0413, 0.3653] |
| equalize | hazy | plantvillage | map50_95 | 3 | 0.1332 | 0.0693 | [-0.0390, 0.3055] |
| combined | hazy | plantvillage | precision | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantvillage | recall | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantvillage | f1 | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantvillage | map50 | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantvillage | map50_95 | 0 | NA | NA | [NA, NA] |
| baseline | hazy | plantdoc | precision | 3 | 0.0035 | 0.0004 | [0.0024, 0.0045] |
| baseline | hazy | plantdoc | recall | 3 | 0.1651 | 0.0518 | [0.0364, 0.2938] |
| baseline | hazy | plantdoc | f1 | 3 | 0.0066 | 0.0007 | [0.0050, 0.0082] |
| baseline | hazy | plantdoc | map50 | 3 | 0.0190 | 0.0054 | [0.0055, 0.0325] |
| baseline | hazy | plantdoc | map50_95 | 3 | 0.0128 | 0.0019 | [0.0082, 0.0175] |
| dehaze | hazy | plantdoc | precision | 3 | 0.0032 | 0.0015 | [-0.0006, 0.0070] |
| dehaze | hazy | plantdoc | recall | 3 | 0.1816 | 0.0521 | [0.0521, 0.3111] |
| dehaze | hazy | plantdoc | f1 | 3 | 0.0062 | 0.0029 | [-0.0011, 0.0135] |
| dehaze | hazy | plantdoc | map50 | 3 | 0.0134 | 0.0147 | [-0.0231, 0.0498] |
| dehaze | hazy | plantdoc | map50_95 | 3 | 0.0072 | 0.0091 | [-0.0154, 0.0299] |
| equalize | hazy | plantdoc | precision | 3 | 0.0020 | 0.0016 | [-0.0021, 0.0061] |
| equalize | hazy | plantdoc | recall | 3 | 0.1077 | 0.0775 | [-0.0847, 0.3002] |
| equalize | hazy | plantdoc | f1 | 3 | 0.0038 | 0.0032 | [-0.0041, 0.0117] |
| equalize | hazy | plantdoc | map50 | 3 | 0.0069 | 0.0080 | [-0.0131, 0.0268] |
| equalize | hazy | plantdoc | map50_95 | 3 | 0.0034 | 0.0037 | [-0.0058, 0.0125] |
| combined | hazy | plantdoc | precision | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantdoc | recall | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantdoc | f1 | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantdoc | map50 | 0 | NA | NA | [NA, NA] |
| combined | hazy | plantdoc | map50_95 | 0 | NA | NA | [NA, NA] |

## Per-class results

See `per_class_metrics.csv` for each seed, input method, clear/hazy condition, source subset, and class. Confusion matrices are saved individually as `confusion_*.csv`.
A source-specific class with no held-out labels has missing (NA) metrics, not a zero score; its coverage is visible in the manifest and per-class CSV.

## Paired tests

See `paired_wilcoxon.csv`. The small number of seeds means these tests have limited power; non-significance is not evidence of equivalence.

## Reproducibility and limitations

Configuration, dataset revisions, sampled image hashes, source labels, splits, and annotation semantics are recorded in `experiment_config.json` and `../data/`.
