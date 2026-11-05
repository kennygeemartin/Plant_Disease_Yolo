# Public-data proxy experiment package

> **Scope:** Results in this package are from a separate public-data proxy experiment, not measurements from the submitted study.

The proxy uses the public PlantVillage classification release and PlantDoc object-detection release, pinned to the revisions below. It samples 14 canonical proxy categories (nine nominal disease labels and five nominally healthy labels). PlantVillage has image-level labels, so each image receives a full-frame box (not a lesion box); PlantDoc contributes its upstream leaf/object boxes. PlantDoc's five generic “leaf” labels are mapped to PlantVillage healthy labels by name only; that assumption is not independently verified. The PlantDoc pepper “leaf spot” label is also crosswalked to PlantVillage bacterial spot by name, without verifying the causal agent. The mismatch in box semantics, possible label noise, and absence of pathology verification limit interpretation. PlantDoc's Hugging Face card omits a license, but AgML's source registry lists CC BY-SA 4.0; see [THIRD_PARTY_DATA_LICENSES.md](./THIRD_PARTY_DATA_LICENSES.md).

## Reproducible protocol

- PlantVillage: [`geraldmc/plantvillage-full`](https://huggingface.co/datasets/geraldmc/plantvillage-full), revision `f808f2706d3ce50ce14652d2b6863d3cc30cf9c4` (CC0-1.0; 54,304 rows).
- PlantDoc detection: [`Project-AgML/plant_doc_detection`](https://huggingface.co/datasets/Project-AgML/plant_doc_detection), revision `0bed0b75b3f0e563d21b6a4e69d15da21b245986` (2,346 images and 8,435 boxes as described by its dataset card). AgML's [source registry](https://github.com/Project-AgML/AgML/blob/f0e0135c7fbd425e7e329b9ac45186cdaf03a47b/agml/_assets/source_citations.json) identifies the dataset license as CC BY-SA 4.0.
- The preparation script checks that each dataset's current `main` commit matches the recorded revision before it samples. The rows API serves the current snapshot rather than an arbitrary historical revision; the script stops if either dataset has changed.
- Cite the source datasets' original publications: Mohanty, Hughes & Salathé (2016), https://doi.org/10.3389/fpls.2016.01419; Singh et al. (2020), https://doi.org/10.1145/3371158.3371196.
- Canonical categories, sample caps, class mapping, split counts, duplicate hashes, annotation conventions, and source metadata are written to `data/manifest.csv`, `data/class_mapping.csv`, and `data/manifest.json`.
- A canonical class may be absent from one source's labels (for example, no PlantDoc "Potato leaf" rows were found). Such absence is not an acquisition failure: source coverage is recorded from observed rows, and unavailable source/class metrics are reported as missing rather than zero.
- Fixed train/validation/test assignment is made before any preprocessing. PlantVillage images with physical-leaf IDs are grouped; other PlantVillage rows and PlantDoc are split by image because PlantDoc has no plant/farm/session IDs. Three seeds (`11, 22, 33`) use identical source images and partitions.
- Four input conditions are compared: unchanged, dark-channel-prior dehazing, luminance histogram equalization, and dehazing followed by histogram equalization. Each is evaluated on clear and deterministically synthesized hazy test images.
- The dehazing implementation follows the related thesis appendix code: 15×15 minimum filter, top 0.1% dark-channel candidates for atmospheric light, maximum channel value for A, omega 0.95, and minimum transmission 0.1. The thesis narrative mentions a guided filter, but its appendix code does not implement one; this proxy follows the code and does not silently add it. Histogram equalization is applied to the Y channel in YUV.
- Held-out metrics are reported for the mixed proxy set and separately by public source.
- YOLOv10n is initialized from the pinned Ultralytics model YAML (trained from scratch, no pretrained checkpoint) with matching seeds, optimizer, image size, batch size, epoch count, and non-preprocessing augmentations disabled for every condition. The recorded experiment uses five epochs and CPU execution.
- Metrics include per-class precision, recall, AP@0.5, AP@0.5:0.95, confusion matrices, mean/SD and 95% t intervals across seeds, plus paired exact Wilcoxon tests. With only three seeds these tests have very low power.
- The reported t intervals are untransformed; with only three seeds, their limits may extend beyond the metrics' [0, 1] range and should not be read as possible metric values.

## Run

Use Python 3.12. Install the packages in `requirements.txt` (including Ultralytics, which installs PyTorch). The data preparation uses the Hugging Face datasets-server rows API and fetches only the capped image sample, rather than downloading complete Parquet shards. From this folder:

```powershell
python prepare_proxy_data.py --limit-per-class 20
python run_ablation.py --epochs 5 --imgsz 320 --batch 4 --seeds 11 22 33
```

Outputs are written under `data/` and `results/`. The sample limit and short training schedule are deliberately explicit; the 20-image cap is per source and class. Change them only for a separately identified run and preserve the generated configuration and logs.

The generated [experiment report](./results/EXPERIMENT_REPORT.md) includes run-level and per-class metrics, source-specific test results, confusion matrices, confidence intervals, and paired tests. The response drafts can be regenerated with `python build_reviewer_response.py`.
