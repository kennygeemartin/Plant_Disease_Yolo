# Submission guidance

> **Scope:** The experiment results in this package are from a separate public-data proxy, not measurements from the submitted study.

The related thesis PDF reports inconsistent epoch counts and contains a YOLOv8 appendix example, so it does not resolve the submitted model's exact configuration.

The lowest-risk revision is to recover the original Roboflow export, 2,141 field images, PlantVillage annotation export, training checkpoint/logs, and IoT logs before revising the results. If those cannot be recovered, discuss a change of study scope with the editor before replacing the paper with a smaller, different public-data proxy study.

## Data availability text for the proxy only

> **Data availability.** The public benchmark images used for the proxy analysis are available from the versioned PlantVillage release at https://huggingface.co/datasets/geraldmc/plantvillage-full (revision `f808f2706d3ce50ce14652d2b6863d3cc30cf9c4`) and the PlantDoc object-detection release at https://huggingface.co/datasets/Project-AgML/plant_doc_detection (revision `0bed0b75b3f0e563d21b6a4e69d15da21b245986`). The class crosswalk, sampled-image hashes, partitions, counts, preprocessing code, and experiment scripts are provided with this revision package. The PlantVillage labels are image-level labels converted to full-frame boxes; this does not establish lesion-level ground truth. Although the PlantDoc dataset card omits a license, AgML's source registry identifies the release as CC BY-SA 4.0; see the attached attribution note and verify terms before redistribution. The original Nigerian field-image archive, Roboflow annotations, original model checkpoint, and run logs were unavailable and therefore are not deposited here.

The URLs/revisions and license evidence must be rechecked at submission. AgML's registry specifies CC BY-SA 4.0 for its PlantDoc release; comply with its attribution/share-alike requirements and resolve any uncertainty with the maintainer.

## Claims to remove or hold pending evidence

- Original combined count, local class distribution, taxonomic diagnoses, and pathologist/laboratory confirmation.
- Original YOLOv10 version/variant, checkpoint, optimizer, loss decomposition, GPU/Colab environment, and run schedule until matching machine-readable records are recovered.
- The manuscript's original validation metrics and undefined 94% “accuracy” unless supported from the historical test predictions and a defined calculation.
- Any assertion that dehazing/equalization improved the original model until matched controlled ablations on the original data are available.
- The claim of early disease detection unless early-stage ground truth and stage-stratified test results exist.
- Real-time/field reliability and notification claims unless device, transmission, inference, and SMTP logs or documented trials exist.
- The challenged Alsakar et al. YOLOv10n comparison; the cited work is identified by the reviewer as YOLOv11n–DeiT.
