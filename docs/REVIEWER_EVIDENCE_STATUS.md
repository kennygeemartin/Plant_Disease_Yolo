# Verified evidence and limits (18 November 2026)

## Verified from machine-readable repository records

- Results for **four methods × three matched seeds × clear/hazy × all/PlantVillage/PlantDoc** give 72 run-level evaluation rows.
- Independent recalculation from `results/run_metrics.csv` matched all 120 mean/SD/95%-Student-t summary rows in `results/summary_mean_sd_ci.csv`, within floating-point precision.
- Independent exact signed-rank enumeration matched all 72 paired p-values in `results/paired_wilcoxon.csv`.
- The 1,008 class-wise metric records reproduce all 14 class rows of the combined clear condition reported in manuscript Table 7.
- Five original PlantDoc *primary-label* mappings are ambiguous: Apple leaf, Bell_pepper leaf, grape leaf, Tomato leaf and Bell_pepper leaf spot. These represent 20 images each (100 of the sampled 260 PlantDoc images). **This does not establish that all associated boxes are erroneous**. They require manual annotation review.
- Table 5 exploratory 5-epoch mean mAP@0.5: baseline 2.04% and combined 4.16% clear (paired p=0.75); baseline 1.87% and combined 2.49% synthetic haze (p=1.00). Equalisation alone achieved 3.84% under synthetic haze. None constitutes a proven improvement.
- The separate **partial** 10-epoch experiment contains 54 evaluation records (9 of 12 planned runs). Clear pooled baseline 6.05%, dehaze 5.37%, equalise 7.07% mAP@0.5. **Combined preprocessing was not run at 10 epochs.** This is descriptive follow-up, not a complete four-way experiment.

## Unsupported results and explicit protections

1. Original historical 150-epoch trajectory: original detector model identity, training dataset membership/labels, checkpoint, split and independent-test status cannot be recovered from the cited proxy repository. It must not be treated as verified YOLOv10n performance or compared with five-epoch proxy metrics.
2. PlantVillage full-frame boxes are pseudo-boxes, not annotated lesions. PlantDoc box semantics differ. Pooled mAP does not validate lesion localisation.
3. Checkpoint weights, versioned training folders, the original 2,141 local Nigerian field-image archive and raw per-image test predictions are not deposited in this public repository. Aggregate CSVs are not a substitute.
4. The smartphone/API/SMTP service now has code and mocked integration tests. No validated disease checkpoint or actual smartphone-network/SMTP inbox evidence is provided. No claims of live deployment, reliable alert receipt or end-to-end real-time performance should be made.
5. Existing detector CPU inference times exclude upload, OpenCV preprocessing, formatting, notification and inbox delivery. Time fields emitted by the research prototype measure its own server stages only.

## Reference verification

- Miao et al., *Frontiers in Plant Science*, volume 15 (2024 collection), published 20 January 2025, doi:10.3389/fpls.2024.1514832: unmodified YOLOv8 61.6% and enhanced SerpensGate-YOLOv8 64.9% mAP@0.5.
- Wang et al., *Sensors* 25(9) (2025), 2882, doi:10.3390/s25092882: the YOLOv10n baseline is 87.4% mAP@0.5; the article summary rounds recall to 86.3%, while a table uses 86.2%.
- Wang et al., *NeurIPS 37* (2024), doi:10.52202/079017-3429: YOLOv10 origin.
- Alsakar et al., *Scientific Reports* 16 (2026), 24553, doi:10.1038/s41598-026-64897-8: enhanced YOLOv11n–DeiT on its own Taiwan tomato dataset, mAP@0.5 97.8%. These papers are not head-to-head comparisons with the present 53-image proxy test.

## Reproduction and future validation

Run `python tools/audit_results.py --input results --manifest data/manifest.csv` to regenerate statistics, archive hashes, per-class checks and an exact image-level annotation review queue. A confirmatory detector comparison requires a relabelled object-detection corpus, properly trained/pretrained matched models (including the combined condition), independent out-of-domain validation and raw prediction/checkpoint deposits. Run `python -m pytest -q tests/test_gateway.py` to exercise *mocked* app integration. A cloud deployment additionally requires authentication, secure hosting, a validated checkpoint, real SMTP credentials and independently collected delivery/latency logs.

**Scope:** This note reports a reproducibility audit and an engineered research prototype; it is not evidence of a validated operational farm disease system.
