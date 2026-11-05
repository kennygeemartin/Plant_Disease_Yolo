"""Run a CPU-limited, repeated-seed YOLOv10n preprocessing ablation."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy.stats import t as student_t
from scipy.stats import wilcoxon
import torch
import ultralytics
from ultralytics.models.yolo.detect.val import DetectionValidator
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
METHODS = ("baseline", "dehaze", "equalize", "combined")
MODEL = "yolov10n.yaml"
TRAINING_PARAMETERS = {
    "optimizer": "AdamW",
    "lr0": 0.001,
    "lrf": 0.01,
    "weight_decay": 0.0005,
    "warmup_epochs": 0,
    "patience": 0,
    "close_mosaic": 0,
    "mosaic": 0,
    "mixup": 0,
    "copy_paste": 0,
    "degrees": 0,
    "translate": 0,
    "scale": 0,
    "shear": 0,
    "perspective": 0,
    "fliplr": 0,
    "flipud": 0,
    "hsv_h": 0,
    "hsv_s": 0,
    "hsv_v": 0,
    "amp": False,
    "pretrained": False,
    "deterministic": True,
    "workers": 0,
    "device": "cpu",
}


def _metric_value(metrics: Any, key: str, class_index: int | None = None) -> float:
    value = getattr(metrics.box, key)
    array = np.asarray(value, dtype=float)
    if class_index is not None:
        class_indices = np.asarray(metrics.box.ap_class_index, dtype=int)
        matches = np.flatnonzero(class_indices == class_index)
        if matches.size == 0:
            return float("nan")
        selected = array[matches[0]]
        if np.asarray(selected).size == 0:
            return float("nan")
        return float(np.nanmean(selected))
    if array.size == 0:
        return float("nan")
    return float(np.nanmean(array))


def _write_confusion(confusion: Any, path: Path, class_names: list[str]) -> None:
    matrix = getattr(confusion, "matrix", None)
    if matrix is None:
        raise RuntimeError("The detector validator did not provide a confusion matrix.")
    matrix = np.asarray(matrix)
    names = class_names + ["background"]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["true\\predicted", *names])
        for index, row in enumerate(matrix):
            label = names[index] if index < len(names) else str(index)
            writer.writerow([label, *row.tolist()])


def _evaluate(
    model: YOLO,
    method: str,
    seed: int,
    condition: str,
    source: str,
    class_names: list[str],
    save_dir: Path,
    imgsz: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    yaml_name = f"data_{condition}_{source}.yaml"
    yaml_path = DATA / "processed" / method / yaml_name
    start = time.perf_counter()
    validation_args = {
        **model.overrides,
        "rect": True,
        "data": str(yaml_path),
        "split": "test",
        "imgsz": imgsz,
        "batch": 4,
        "device": "cpu",
        "workers": 0,
        "plots": False,
        "project": str(save_dir / "validation"),
        "name": f"{method}_seed{seed}_{condition}_{source}",
        "exist_ok": True,
        "verbose": False,
        "conf": 0.001,
        "iou": 0.7,
        "mode": "val",
    }
    validator_instances = []

    class CapturingDetectionValidator(DetectionValidator):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            validator_instances.append(self)

    metrics = model.val(validator=CapturingDetectionValidator, **validation_args)
    if not validator_instances:
        raise RuntimeError("The detector validation did not initialize its validator.")
    validator = validator_instances[-1]
    elapsed = time.perf_counter() - start
    summary = {
        "method": method,
        "seed": seed,
        "test_condition": condition,
        "test_source": source,
        "precision": _metric_value(metrics, "p"),
        "recall": _metric_value(metrics, "r"),
        "f1": _metric_value(metrics, "f1"),
        "map50": _metric_value(metrics, "ap50"),
        "map50_95": _metric_value(metrics, "ap"),
        "inference_seconds_reported": float(metrics.speed.get("inference", math.nan)) / 1000,
        "evaluation_wall_seconds": elapsed,
    }
    per_class = []
    for class_id, class_name in enumerate(class_names):
        per_class.append(
            {
                **{
                    key: summary[key]
                    for key in ("method", "seed", "test_condition", "test_source")
                },
                "class_id": class_id,
                "class": class_name,
                "precision": _metric_value(metrics, "p", class_id),
                "recall": _metric_value(metrics, "r", class_id),
                "f1": _metric_value(metrics, "f1", class_id),
                "ap50": _metric_value(metrics, "ap50", class_id),
                "ap50_95": _metric_value(metrics, "ap", class_id),
            }
        )
    _write_confusion(
        validator.confusion_matrix,
        save_dir / f"confusion_{method}_seed{seed}_{condition}_{source}.csv",
        class_names,
    )
    return summary, per_class


def _mean_ci(values: list[float]) -> dict[str, float]:
    clean = [float(value) for value in values if np.isfinite(value)]
    if not clean:
        return {"n": 0, "mean": math.nan, "sd": math.nan, "ci95_low": math.nan, "ci95_high": math.nan}
    mean = statistics.mean(clean)
    if len(clean) < 2:
        return {"n": len(clean), "mean": mean, "sd": math.nan, "ci95_low": math.nan, "ci95_high": math.nan}
    sd = statistics.stdev(clean)
    half_width = float(student_t.ppf(0.975, df=len(clean) - 1)) * sd / math.sqrt(len(clean))
    return {
        "n": len(clean),
        "mean": mean,
        "sd": sd,
        "ci95_low": mean - half_width,
        "ci95_high": mean + half_width,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _paired_tests(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tests = []
    for condition in ("clear", "hazy"):
        for source in ("all", "plantvillage", "plantdoc"):
            for metric in ("map50", "map50_95", "precision", "recall"):
                by_method = {
                    method: {
                        row["seed"]: row[metric]
                        for row in rows
                        if row["method"] == method
                        and row["test_condition"] == condition
                        and row["test_source"] == source
                        and np.isfinite(row[metric])
                    }
                    for method in METHODS
                }
                baseline = by_method["baseline"]
                for method in METHODS[1:]:
                    common = sorted(set(baseline) & set(by_method[method]))
                    left = [baseline[seed] for seed in common]
                    right = [by_method[method][seed] for seed in common]
                    if len(common) < 2:
                        statistic, p_value = math.nan, math.nan
                    elif all(np.isclose(a, b) for a, b in zip(left, right)):
                        statistic, p_value = 0.0, 1.0
                    else:
                        result = wilcoxon(
                            left,
                            right,
                            zero_method="wilcox",
                            correction=False,
                            alternative="two-sided",
                            method="exact",
                        )
                        statistic, p_value = float(result.statistic), float(result.pvalue)
                    tests.append(
                        {
                            "condition": condition,
                            "test_source": source,
                            "metric": metric,
                            "comparison": f"{method} vs baseline",
                            "paired_seeds": len(common),
                            "wilcoxon_statistic": statistic,
                            "p_value_unadjusted": p_value,
                        }
                    )
    return tests


def _write_report(
    summaries: list[dict[str, Any]],
    per_class: list[dict[str, Any]],
    tests: list[dict[str, Any]],
    config: dict[str, Any],
) -> None:
    summary_rows = []
    for condition in ("clear", "hazy"):
        for source in ("all", "plantvillage", "plantdoc"):
            for method in METHODS:
                selected = [
                    row
                    for row in summaries
                    if row["method"] == method
                    and row["test_condition"] == condition
                    and row["test_source"] == source
                ]
                for metric in ("precision", "recall", "f1", "map50", "map50_95"):
                    stats = _mean_ci([row[metric] for row in selected])
                    summary_rows.append(
                        {
                            "method": method,
                            "test_condition": condition,
                            "test_source": source,
                            "metric": metric,
                            **stats,
                        }
                    )
    _write_csv(RESULTS / "summary_mean_sd_ci.csv", summary_rows)
    _write_csv(RESULTS / "run_metrics.csv", summaries)
    _write_csv(RESULTS / "per_class_metrics.csv", per_class)
    _write_csv(RESULTS / "paired_wilcoxon.csv", tests)
    (RESULTS / "experiment_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    lines = [
        "# Public-data proxy experiment results",
        "",
        "> **Scope:** Results below are from a separate public-data proxy experiment, "
        "not measurements from the submitted study.",
        "",
        "## Protocol",
        "",
        f"- Model: `{config['model']}`; Ultralytics {config['ultralytics_version']}.",
        "- Loss: Ultralytics' default YOLOv10 detection loss; no custom loss or loss "
        "components were supplied. Default box/classification/DFL weights are "
        "7.5/0.5/1.5.",
        f"- Image size: {config['imgsz']}; batch: {config['batch']}; epochs: {config['epochs']}; "
        f"seeds: {', '.join(map(str, config['seeds']))}; device: CPU.",
        "- Same source images and image-level 80/10/10 split across all conditions; "
        "preprocessing is applied after splitting.",
        "- Test conditions are clear and simulated haze (I = 0.68J + 0.32×235). "
        "Simulated haze is not a measured field condition.",
        "- Results are reported for the mixed test set and separately for the PlantVillage "
        "and PlantDoc public-proxy subsets.",
        "- Both image-classification sources are converted to one full-frame box per "
        "image. These metrics do not evaluate leaf/lesion localization.",
        "- The five PlantDoc generic 'leaf' labels are mapped to matching PlantVillage "
        "healthy labels by name only; this cross-source assumption is not verified and "
        "may introduce label error.",
        "- PlantDoc's generic pepper 'leaf spot' label is crosswalked to PlantVillage "
        "bacterial spot by name; the causal agent is not verified.",
        "- Reported precision/recall/F1 use the detector's validation operating point; "
        "AP is the area under the precision-recall curve. Detection accuracy is not reported.",
        "- Confidence intervals are two-sided 95% Student-t intervals across seeds. "
        "With only three runs, intervals are very imprecise and the untransformed "
        "interval limits may extend outside the metrics' [0, 1] range; those limits "
        "should not be interpreted as possible metric values. Paired exact Wilcoxon "
        "p-values are unadjusted and underpowered.",
        "",
        "## Metrics across independent seeds",
        "",
        "| Method | Test | Source | Metric | n | Mean | SD | 95% CI |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        def fmt(value: Any) -> str:
            return "NA" if not np.isfinite(value) else f"{value:.4f}"
        lines.append(
            f"| {row['method']} | {row['test_condition']} | {row['test_source']} | "
            f"{row['metric']} | "
            f"{row['n']} | {fmt(row['mean'])} | {fmt(row['sd'])} | "
            f"[{fmt(row['ci95_low'])}, {fmt(row['ci95_high'])}] |"
        )
    lines += [
        "",
        "## Per-class results",
        "",
        "See `per_class_metrics.csv` for each seed, input method, clear/hazy condition, "
        "source subset, and class. Confusion matrices are saved individually as "
        "`confusion_*.csv`.",
        "A source-specific class with no held-out labels has missing (NA) metrics, "
        "not a zero score; its coverage is visible in the manifest and per-class CSV.",
        "",
        "## Paired tests",
        "",
        "See `paired_wilcoxon.csv`. The small number of seeds means these tests have "
        "limited power; non-significance is not evidence of equivalence.",
        "",
        "## Reproducibility and limitations",
        "",
        "Configuration, dataset revisions, sampled image hashes, source labels, splits, "
        "and annotation semantics are recorded in `experiment_config.json` and `../data/`.",
    ]
    (RESULTS / "EXPERIMENT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(epochs: int, imgsz: int, batch: int, seeds: list[int], resume: bool) -> None:
    if not (DATA / "manifest.json").exists():
        raise FileNotFoundError("Run prepare_proxy_data.py before the ablation.")
    RESULTS.mkdir(parents=True, exist_ok=True)
    class_names = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))["classes"]
    config = {
        "study_type": "public-data proxy; not original-study reproduction",
        "model": MODEL,
        "ultralytics_version": ultralytics.__version__,
        "torch_version": torch.__version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "device": "cpu",
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "seeds": seeds,
        "training_parameters": TRAINING_PARAMETERS,
        "loss": "Ultralytics YOLOv10 default detection loss; no custom loss supplied",
        "loss_weights": {"box": 7.5, "cls": 0.5, "dfl": 1.5},
        "augmentation": "disabled except for the separately generated test haze",
        "confidence_threshold": 0.001,
        "nms_iou_threshold": 0.7,
        "dataset_manifest": "data/manifest.json",
        "paired_statistical_test": "two-sided exact Wilcoxon signed-rank, unadjusted",
        "confidence_interval": "two-sided 95% Student-t interval across seeds",
        "scipy_version": scipy.__version__,
    }
    (RESULTS / "experiment_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    summaries = []
    per_class = []
    for method in METHODS:
        for seed in seeds:
            run_name = f"{method}_seed{seed}"
            weight_path = RESULTS / run_name / "weights" / "best.pt"
            if resume and weight_path.exists():
                model = YOLO(str(weight_path))
            else:
                random.seed(seed)
                np.random.seed(seed)
                torch.manual_seed(seed)
                model = YOLO(MODEL)
                model.train(
                    data=str(DATA / "processed" / method / "data_clear_all.yaml"),
                    project=str(RESULTS),
                    name=run_name,
                    exist_ok=True,
                    device="cpu",
                    workers=0,
                    epochs=epochs,
                    imgsz=imgsz,
                    batch=batch,
                    seed=seed,
                    deterministic=True,
                    pretrained=False,
                    optimizer="AdamW",
                    lr0=0.001,
                    lrf=0.01,
                    weight_decay=0.0005,
                    warmup_epochs=0,
                    patience=0,
                    close_mosaic=0,
                    mosaic=0,
                    mixup=0,
                    copy_paste=0,
                    degrees=0,
                    translate=0,
                    scale=0,
                    shear=0,
                    perspective=0,
                    fliplr=0,
                    flipud=0,
                    hsv_h=0,
                    hsv_s=0,
                    hsv_v=0,
                    amp=False,
                    plots=False,
                    save=True,
                    val=True,
                    verbose=False,
                )
                if not weight_path.exists():
                    raise FileNotFoundError(
                        f"Training did not produce the expected checkpoint: {weight_path}"
                    )
                model = YOLO(str(weight_path))
            for condition in ("clear", "hazy"):
                for source in ("all", "plantvillage", "plantdoc"):
                    summary, classes = _evaluate(
                        model,
                        method,
                        seed,
                        condition,
                        source,
                        class_names,
                        RESULTS,
                        imgsz,
                    )
                    summaries.append(summary)
                    per_class.extend(classes)
                    _write_csv(RESULTS / "run_metrics.csv", summaries)
                    _write_csv(RESULTS / "per_class_metrics.csv", per_class)
    tests = _paired_tests(summaries)
    _write_report(summaries, per_class, tests, config)
    print(f"Completed {len(seeds) * len(METHODS)} training runs.")
    print(f"Results: {RESULTS / 'EXPERIMENT_REPORT.md'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--seeds", type=int, nargs="+", default=[11, 22, 33])
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.epochs < 1 or args.imgsz < 64 or args.batch < 1 or len(args.seeds) < 3:
        parser.error("Use positive training settings and at least three independent seeds.")
    run(args.epochs, args.imgsz, args.batch, args.seeds, args.resume)


if __name__ == "__main__":
    main()
