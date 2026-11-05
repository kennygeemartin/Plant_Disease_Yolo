# Response to reviewers — author draft

> **DRAFT — NOT READY TO SUBMIT. Scope: results below are from a separate public-data proxy experiment, not measurements from the submitted study.**

The public-data proxy experiment completed; its measured output is linked below.

The experiment report contains methods, measurements, and source details.

## Reviewer 1

**Reviewer 1 — statistical validation**

The submitted run's training data, source code, checkpoint, and run logs were not supplied, so its historical results could not be statistically reanalysed. The attached proxy report gives mean, sample SD, 95% t intervals, and paired exact Wilcoxon comparisons across three seeds. The intervals are imprecise at this sample size; repeated 150-epoch runs of the submitted experiment remain unaddressed.

## Reviewer 2, comment 1 — biological validity and local labels

The local cassava and maize images and their label/diagnostic records were not supplied, so we cannot authenticate their disease names, causal agents, diagnostic criteria, or pathologist/laboratory review. The proxy uses the published source labels from PlantVillage and PlantDoc without claiming independent pathology confirmation. Five generic PlantDoc 'leaf' labels are mapped to PlantVillage healthy labels by name only, an unverified cross-source assumption that may introduce label error. PlantDoc's generic pepper 'leaf spot' label is also mapped to PlantVillage bacterial spot by name only, without confirming the pathogen. This does not resolve biological validation; disease identities should follow independently reviewed labels.

## Reviewer 2, comment 2 — source-wise counts and bounding boxes

The original Roboflow export is unavailable. The proxy class mapping, source counts, split counts, source revisions, image hashes, and box counts are recorded in data/class_mapping.csv, data/manifest.csv, and data/manifest.json. PlantDoc's released boxes are retained. PlantVillage supplies image-level labels only, so each PlantVillage image receives one full-frame box, not a lesion box. Five generic PlantDoc 'leaf' labels are mapped to healthy classes by name only, not verified pathologically. The PlantDoc Hugging Face card omits a license, but AgML's source registry lists CC BY-SA 4.0; retain attribution/share-alike and verify terms before redistribution.

## Reviewer 2, comment 3 — partitions, leakage, independent test results

The original split files and identifiers were not supplied. In the proxy, sampling and 80/10/10 partitions are fixed before preprocessing; available physical-leaf IDs in PlantVillage are grouped, while PlantDoc can only be split by image because plant/farm/session IDs are absent. Test metrics are reported for the combined proxy and separately for PlantVillage and PlantDoc. Residual near-duplicate/plant-level leakage in PlantDoc cannot be ruled out.

## Reviewer 2, comment 4 — detector implementation and training records

The related PDF does not verify the submitted model: it lists 300 epochs in the training section, ends its results table at epoch 149, and its appendix example uses YOLOv8n/Ultralytics 8.2.58 rather than YOLOv10. The revised manuscript separately says 150 epochs and Google Colab. The proxy identifies YOLOv10n, its Ultralytics/PyTorch versions, CPU hardware, training arguments, seed, and checkpoint paths in results/experiment_config.json and per-run logs/checkpoints. It uses AdamW and a five-epoch schedule.

## Reviewer 2, comment 5 — preprocessing ablation

The proxy compares unchanged input, dark-channel-prior dehazing, luminance histogram equalization, and their combination under matched training settings. It evaluates clear images and a deterministically synthesized haze condition; algorithm parameters and code are supplied in prepare_proxy_data.py. The thesis describes guided-filter refinement but its appendix code omits it; the proxy follows the appendix code and records that discrepancy. Synthetic haze is not field-measured degradation.

## Reviewer 2, comment 6 — definition, per-class results, and errors

The proxy reports per-class precision, recall, F1, AP@0.5 and AP@0.5:0.95, confusion matrices, test-set results, and seed-level variation. Detection accuracy is not reported because the original 94% value is undefined and cannot be reconstructed without its calculation and test predictions.

## Reviewer 2, comment 7 — IoT latency, trials, and early detection

No phone, cloud deployment, transmission/notification logs, or field-trial records were supplied. Capture-to-alert, upload, preprocessing, inference, and notification latency were not measured, and no field trial is claimed. This draft response explicitly distinguishes visible-symptom recognition from early-stage diagnosis. The original real-time, reliability, field-trial, and early-detection claims require evidence or must be withdrawn.

## Reviewer 2, comment 8 — comparison table and references

We do not rely on the challenged cross-paper performance figures in the proxy analysis. The cited Alsakar et al. model designation must be YOLOv11n–DeiT, not YOLOv10n; its reported metrics should be removed unless verified directly against the original paper. The manuscript also has in-text citations without matching entries (including Shueil et al., Dun et al., and Nnaedozie et al.). A complete source-by-source reference audit is still required before resubmission; no unverified DOI or bibliographic entry is invented here.

## Editorial comments

- Citation wording: change forms such as “According to [5]” to “According to Ref. [5]” or “According to Author et al. [5]”.
- Use “Figure” and “Table” consistently when referring to numbered items in the text.
- Verify every DOI and link against the cited primary publication; add DOI links where they exist and do not invent missing DOIs.
- Ensure every in-text citation has exactly one matching reference and every reference is cited. The missing Shueil, Dun, and Nnaedozie entries still need primary-source audit.
- Cite and discuss every retained table and figure in the main text, explaining its purpose and key information.
- Punctuate every equation correctly and verify the journal's equation formatting.
- Proofread the complete revised manuscript for language, spelling, and typographical errors.
- Replace any scanned, blurred, or unreadable figures with original, publication-quality artwork; this package has not validated or replaced the source manuscript's figures.
- Add a Data Availability section with stable links and exact dataset/code versions. The proxy links/revisions are recorded in the experiment package; the original local dataset is unavailable.
- Apply the Journal of the Nigerian Society of Physical Sciences manuscript/reference style and verify the current author guidelines.
- The supplied work is an empirical engineering study rather than a mathematical paper; confirm whether LaTeX is required with the editor before submission.
- Apply the journal's book and book-chapter reference formats to any such sources; verify publisher, location, pages, and DOI rather than assuming journal format.

## Proxy results

The complete methods, run-level outputs, per-class results, confusion matrices, confidence intervals, paired tests, and limitations are in [results/EXPERIMENT_REPORT.md](./results/EXPERIMENT_REPORT.md).

| Method | Condition | Source | Metric | n | Mean | SD | 95% CI |
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

## Data and files

- Dataset revisions: `{"Project-AgML/plant_doc_detection": "0bed0b75b3f0e563d21b6a4e69d15da21b245986", "geraldmc/plantvillage-full": "f808f2706d3ce50ce14652d2b6863d3cc30cf9c4"}`
- Dataset counts and image-level split details: `data/manifest.json` and `data/manifest.csv`.
- Class mapping and annotation conventions: `data/class_mapping.csv` and `data/manifest.json`.
- Third-party dataset terms and attribution: `THIRD_PARTY_DATA_LICENSES.md`.
- Scripts and pinned dependencies: `prepare_proxy_data.py`, `run_ablation.py`, and `requirements.txt`.
- Source-document discrepancies: `SOURCE_DOCUMENT_AUDIT.md`.

## Required before resubmission

Recover the original images/annotations and run records, or remove all unsupported original-study performance claims and agree with the editor on a replacement study. Obtain/record pathologist review, verify all citations/DOIs against primary sources, provide actual independent test and multi-seed results, and measure the full IoT pipeline on documented hardware. Apply PlantDoc attribution/share-alike obligations before redistribution or publication.
