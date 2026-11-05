# Public-data proxy experiment results

> **Scope:** Results below are from a separate public-data proxy experiment, not measurements from the submitted study.

## Protocol

- Model: `yolov10n.yaml`; Ultralytics 8.3.40.
- Loss: Ultralytics' default YOLOv10 detection loss; no custom loss or loss components were supplied. Default box/classification/DFL weights are 7.5/0.5/1.5.
- Image size: 320; batch: 4; epochs: 5; seeds: 11, 22, 33; device: CPU.
- Same source images and image-level 80/10/10 split across all conditions; preprocessing is applied after splitting.
- Test conditions are clear and simulated haze (I = 0.68J + 0.32×235). Simulated haze is not a measured field condition.
- Results are reported for the mixed test set and separately for the PlantVillage and PlantDoc public-proxy subsets.
- Both image-classification sources are converted to one full-frame box per image. These metrics do not evaluate leaf/lesion localization.
- The five PlantDoc generic 'leaf' labels are mapped to matching PlantVillage healthy labels by name only; this cross-source assumption is not verified and may introduce label error.
- PlantDoc's generic pepper 'leaf spot' label is crosswalked to PlantVillage bacterial spot by name; the causal agent is not verified.
- Reported precision/recall/F1 use the detector's validation operating point; AP is the area under the precision-recall curve. Detection accuracy is not reported.
- Confidence intervals are two-sided 95% Student-t intervals across seeds. With only three runs, intervals are very imprecise and the untransformed limits may extend outside the metrics' [0, 1] range; those limits should not be interpreted as possible metric values. Paired exact Wilcoxon p-values are unadjusted and underpowered.

## Metrics across independent seeds

| Method | Test | Source | Metric | n | Mean | SD | 95% CI |
|---|---|---|---:|---:|---:|---:|---:|
| baseline | clear | all | precision | 3 | 0.0055 | 0.0010 | [0.0029, 0.0081] |
| baseline | clear | all | recall | 3 | 0.3783 | 0.0286 | [0.3074, 0.4493] |
| baseline | clear | all | f1 | 3 | 0.0107 | 0.0020 | [0.0058, 0.0156] |
| baseline | clear | all | map50 | 3 | 0.0204 | 0.0100 | [-0.0044, 0.0451] |
| baseline | clear | all | map50_95 | 3 | 0.0124 | 0.0041 | [0.0023, 0.0226] |
| dehaze | clear | all | precision | 3 | 0.0046 | 0.0010 | [0.0022, 0.0069] |
| dehaze | clear | all | recall | 3 | 0.3848 | 0.0663 | [0.2202, 0.5495] |
| dehaze | clear | all | f1 | 3 | 0.0089 | 0.0019 | [0.0042, 0.0136] |
| dehaze | clear | all | map50 | 3 | 0.0100 | 0.0057 | [-0.0042, 0.0243] |
| dehaze | clear | all | map50_95 | 3 | 0.0069 | 0.0038 | [-0.0025, 0.0162] |
| equalize | clear | all | precision | 3 | 0.3148 | 0.5382 | [-1.0222, 1.6517] |
| equalize | clear | all | recall | 3 | 0.3121 | 0.2688 | [-0.3556, 0.9799] |
| equalize | clear | all | f1 | 3 | 0.0081 | 0.0010 | [0.0057, 0.0105] |
| equalize | clear | all | map50 | 3 | 0.0269 | 0.0242 | [-0.0334, 0.0871] |
| equalize | clear | all | map50_95 | 3 | 0.0218 | 0.0207 | [-0.0296, 0.0732] |
| combined | clear | all | precision | 3 | 0.1649 | 0.2762 | [-0.5211, 0.8510] |
| combined | clear | all | recall | 3 | 0.3294 | 0.1767 | [-0.1095, 0.7683] |
| combined | clear | all | f1 | 3 | 0.0183 | 0.0131 | [-0.0143, 0.0509] |
| combined | clear | all | map50 | 3 | 0.0416 | 0.0418 | [-0.0623, 0.1454] |
| combined | clear | all | map50_95 | 3 | 0.0334 | 0.0389 | [-0.0632, 0.1300] |
| baseline | clear | plantvillage | precision | 3 | 0.0124 | 0.0063 | [-0.0033, 0.0280] |
| baseline | clear | plantvillage | recall | 3 | 0.7619 | 0.1352 | [0.4260, 1.0978] |
| baseline | clear | plantvillage | f1 | 3 | 0.0237 | 0.0115 | [-0.0049, 0.0524] |
| baseline | clear | plantvillage | map50 | 3 | 0.0832 | 0.0270 | [0.0161, 0.1504] |
| baseline | clear | plantvillage | map50_95 | 3 | 0.0614 | 0.0368 | [-0.0300, 0.1527] |
| dehaze | clear | plantvillage | precision | 3 | 0.0090 | 0.0020 | [0.0039, 0.0140] |
| dehaze | clear | plantvillage | recall | 3 | 0.6667 | 0.1091 | [0.3956, 0.9377] |
| dehaze | clear | plantvillage | f1 | 3 | 0.0175 | 0.0039 | [0.0078, 0.0272] |
| dehaze | clear | plantvillage | map50 | 3 | 0.0651 | 0.0017 | [0.0609, 0.0694] |
| dehaze | clear | plantvillage | map50_95 | 3 | 0.0489 | 0.0030 | [0.0416, 0.0563] |
| equalize | clear | plantvillage | precision | 3 | 0.3199 | 0.5425 | [-1.0278, 1.6676] |
| equalize | clear | plantvillage | recall | 3 | 0.6548 | 0.5373 | [-0.6800, 1.9895] |
| equalize | clear | plantvillage | f1 | 3 | 0.0167 | 0.0063 | [0.0010, 0.0323] |
| equalize | clear | plantvillage | map50 | 3 | 0.0830 | 0.0546 | [-0.0525, 0.2185] |
| equalize | clear | plantvillage | map50_95 | 3 | 0.0682 | 0.0494 | [-0.0546, 0.1911] |
| combined | clear | plantvillage | precision | 3 | 0.1907 | 0.3167 | [-0.5961, 0.9775] |
| combined | clear | plantvillage | recall | 3 | 0.6667 | 0.3819 | [-0.2820, 1.6153] |
| combined | clear | plantvillage | f1 | 3 | 0.0306 | 0.0264 | [-0.0349, 0.0961] |
| combined | clear | plantvillage | map50 | 3 | 0.1343 | 0.0920 | [-0.0941, 0.3628] |
| combined | clear | plantvillage | map50_95 | 3 | 0.0997 | 0.0842 | [-0.1094, 0.3088] |
| baseline | clear | plantdoc | precision | 3 | 0.0025 | 0.0007 | [0.0008, 0.0043] |
| baseline | clear | plantdoc | recall | 3 | 0.1798 | 0.0475 | [0.0617, 0.2979] |
| baseline | clear | plantdoc | f1 | 3 | 0.0049 | 0.0013 | [0.0016, 0.0082] |
| baseline | clear | plantdoc | map50 | 3 | 0.0066 | 0.0038 | [-0.0029, 0.0160] |
| baseline | clear | plantdoc | map50_95 | 3 | 0.0030 | 0.0016 | [-0.0010, 0.0070] |
| dehaze | clear | plantdoc | precision | 3 | 0.0027 | 0.0018 | [-0.0017, 0.0072] |
| dehaze | clear | plantdoc | recall | 3 | 0.2234 | 0.0569 | [0.0820, 0.3647] |
| dehaze | clear | plantdoc | f1 | 3 | 0.0052 | 0.0034 | [-0.0033, 0.0138] |
| dehaze | clear | plantdoc | map50 | 3 | 0.0049 | 0.0047 | [-0.0068, 0.0166] |
| dehaze | clear | plantdoc | map50_95 | 3 | 0.0017 | 0.0014 | [-0.0017, 0.0050] |
| equalize | clear | plantdoc | precision | 3 | 0.3103 | 0.5345 | [-1.0175, 1.6380] |
| equalize | clear | plantdoc | recall | 3 | 0.0898 | 0.0744 | [-0.0951, 0.2747] |
| equalize | clear | plantdoc | f1 | 3 | 0.0038 | 0.0013 | [0.0006, 0.0071] |
| equalize | clear | plantdoc | map50 | 3 | 0.0069 | 0.0058 | [-0.0075, 0.0213] |
| equalize | clear | plantdoc | map50_95 | 3 | 0.0032 | 0.0022 | [-0.0024, 0.0087] |
| combined | clear | plantdoc | precision | 3 | 0.1066 | 0.1795 | [-0.3394, 0.5526] |
| combined | clear | plantdoc | recall | 3 | 0.1542 | 0.1003 | [-0.0948, 0.4033] |
| combined | clear | plantdoc | f1 | 3 | 0.0074 | 0.0036 | [-0.0017, 0.0164] |
| combined | clear | plantdoc | map50 | 3 | 0.0125 | 0.0109 | [-0.0146, 0.0395] |
| combined | clear | plantdoc | map50_95 | 3 | 0.0056 | 0.0039 | [-0.0041, 0.0154] |
| baseline | hazy | all | precision | 3 | 0.0095 | 0.0032 | [0.0017, 0.0174] |
| baseline | hazy | all | recall | 3 | 0.2745 | 0.0595 | [0.1268, 0.4222] |
| baseline | hazy | all | f1 | 3 | 0.0164 | 0.0034 | [0.0079, 0.0248] |
| baseline | hazy | all | map50 | 3 | 0.0187 | 0.0101 | [-0.0063, 0.0438] |
| baseline | hazy | all | map50_95 | 3 | 0.0158 | 0.0096 | [-0.0081, 0.0397] |
| dehaze | hazy | all | precision | 3 | 0.0050 | 0.0016 | [0.0010, 0.0089] |
| dehaze | hazy | all | recall | 3 | 0.3811 | 0.0769 | [0.1899, 0.5722] |
| dehaze | hazy | all | f1 | 3 | 0.0097 | 0.0029 | [0.0024, 0.0169] |
| dehaze | hazy | all | map50 | 3 | 0.0118 | 0.0037 | [0.0025, 0.0211] |
| dehaze | hazy | all | map50_95 | 3 | 0.0078 | 0.0024 | [0.0019, 0.0138] |
| equalize | hazy | all | precision | 3 | 0.0047 | 0.0005 | [0.0035, 0.0058] |
| equalize | hazy | all | recall | 3 | 0.4572 | 0.0452 | [0.3450, 0.5693] |
| equalize | hazy | all | f1 | 3 | 0.0092 | 0.0008 | [0.0071, 0.0113] |
| equalize | hazy | all | map50 | 3 | 0.0384 | 0.0233 | [-0.0196, 0.0964] |
| equalize | hazy | all | map50_95 | 3 | 0.0306 | 0.0208 | [-0.0212, 0.0824] |
| combined | hazy | all | precision | 3 | 0.0043 | 0.0005 | [0.0030, 0.0055] |
| combined | hazy | all | recall | 3 | 0.4225 | 0.0734 | [0.2403, 0.6048] |
| combined | hazy | all | f1 | 3 | 0.0084 | 0.0010 | [0.0060, 0.0108] |
| combined | hazy | all | map50 | 3 | 0.0249 | 0.0167 | [-0.0166, 0.0664] |
| combined | hazy | all | map50_95 | 3 | 0.0181 | 0.0162 | [-0.0222, 0.0583] |
| baseline | hazy | plantvillage | precision | 3 | 0.0345 | 0.0139 | [-0.0002, 0.0691] |
| baseline | hazy | plantvillage | recall | 3 | 0.4881 | 0.1031 | [0.2320, 0.7442] |
| baseline | hazy | plantvillage | f1 | 3 | 0.0523 | 0.0100 | [0.0275, 0.0771] |
| baseline | hazy | plantvillage | map50 | 3 | 0.0727 | 0.0334 | [-0.0103, 0.1557] |
| baseline | hazy | plantvillage | map50_95 | 3 | 0.0635 | 0.0356 | [-0.0249, 0.1518] |
| dehaze | hazy | plantvillage | precision | 3 | 0.0091 | 0.0004 | [0.0081, 0.0100] |
| dehaze | hazy | plantvillage | recall | 3 | 0.6548 | 0.1833 | [0.1995, 1.1100] |
| dehaze | hazy | plantvillage | f1 | 3 | 0.0176 | 0.0008 | [0.0156, 0.0197] |
| dehaze | hazy | plantvillage | map50 | 3 | 0.0535 | 0.0216 | [-0.0001, 0.1070] |
| dehaze | hazy | plantvillage | map50_95 | 3 | 0.0400 | 0.0189 | [-0.0069, 0.0870] |
| equalize | hazy | plantvillage | precision | 3 | 0.3175 | 0.5372 | [-1.0169, 1.6519] |
| equalize | hazy | plantvillage | recall | 3 | 0.6667 | 0.5467 | [-0.6914, 2.0248] |
| equalize | hazy | plantvillage | f1 | 3 | 0.0146 | 0.0004 | [0.0137, 0.0156] |
| equalize | hazy | plantvillage | map50 | 3 | 0.1305 | 0.0756 | [-0.0574, 0.3184] |
| equalize | hazy | plantvillage | map50_95 | 3 | 0.0972 | 0.0650 | [-0.0642, 0.2585] |
| combined | hazy | plantvillage | precision | 3 | 0.0063 | 0.0007 | [0.0046, 0.0080] |
| combined | hazy | plantvillage | recall | 3 | 0.8571 | 0.2172 | [0.3175, 1.3968] |
| combined | hazy | plantvillage | f1 | 3 | 0.0124 | 0.0013 | [0.0091, 0.0158] |
| combined | hazy | plantvillage | map50 | 3 | 0.1084 | 0.0548 | [-0.0278, 0.2447] |
| combined | hazy | plantvillage | map50_95 | 3 | 0.0770 | 0.0551 | [-0.0600, 0.2139] |
| baseline | hazy | plantdoc | precision | 3 | 0.0028 | 0.0013 | [-0.0005, 0.0061] |
| baseline | hazy | plantdoc | recall | 3 | 0.1220 | 0.0234 | [0.0638, 0.1802] |
| baseline | hazy | plantdoc | f1 | 3 | 0.0055 | 0.0025 | [-0.0008, 0.0117] |
| baseline | hazy | plantdoc | map50 | 3 | 0.0174 | 0.0221 | [-0.0374, 0.0723] |
| baseline | hazy | plantdoc | map50_95 | 3 | 0.0130 | 0.0179 | [-0.0314, 0.0573] |
| dehaze | hazy | plantdoc | precision | 3 | 0.0031 | 0.0015 | [-0.0005, 0.0067] |
| dehaze | hazy | plantdoc | recall | 3 | 0.2351 | 0.0414 | [0.1322, 0.3380] |
| dehaze | hazy | plantdoc | f1 | 3 | 0.0060 | 0.0028 | [-0.0009, 0.0128] |
| dehaze | hazy | plantdoc | map50 | 3 | 0.0066 | 0.0039 | [-0.0032, 0.0163] |
| dehaze | hazy | plantdoc | map50_95 | 3 | 0.0029 | 0.0019 | [-0.0019, 0.0076] |
| equalize | hazy | plantdoc | precision | 3 | 0.0022 | 0.0009 | [-0.0000, 0.0044] |
| equalize | hazy | plantdoc | recall | 3 | 0.1727 | 0.0887 | [-0.0477, 0.3930] |
| equalize | hazy | plantdoc | f1 | 3 | 0.0043 | 0.0018 | [-0.0001, 0.0086] |
| equalize | hazy | plantdoc | map50 | 3 | 0.0076 | 0.0050 | [-0.0048, 0.0200] |
| equalize | hazy | plantdoc | map50_95 | 3 | 0.0041 | 0.0022 | [-0.0013, 0.0094] |
| combined | hazy | plantdoc | precision | 3 | 0.1310 | 0.2234 | [-0.4240, 0.6860] |
| combined | hazy | plantdoc | recall | 3 | 0.1414 | 0.0912 | [-0.0852, 0.3680] |
| combined | hazy | plantdoc | f1 | 3 | 0.0053 | 0.0024 | [-0.0006, 0.0112] |
| combined | hazy | plantdoc | map50 | 3 | 0.0123 | 0.0128 | [-0.0194, 0.0440] |
| combined | hazy | plantdoc | map50_95 | 3 | 0.0043 | 0.0039 | [-0.0053, 0.0139] |

## Per-class results

See `per_class_metrics.csv` for each seed, input method, clear/hazy condition, source subset, and class. Confusion matrices are saved individually as `confusion_*.csv`.
A source-specific class with no held-out labels has missing (NA) metrics, not a zero score; its coverage is visible in the manifest and per-class CSV.

## Paired tests

See `paired_wilcoxon.csv`. The small number of seeds means these tests have limited power; non-significance is not evidence of equivalence.

## Reproducibility and limitations

Configuration, dataset revisions, sampled image hashes, source labels, splits, and annotation semantics are recorded in `experiment_config.json` and `../data/`.
