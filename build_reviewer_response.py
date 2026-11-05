"""Build an honest, point-by-point reviewer response from recorded run outputs."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

REPLIES = [
    (
        "Reviewer 1 — statistical validation",
        "The submitted run's training data, source code, checkpoint, and run logs "
        "were not supplied, so its historical results could not be statistically "
        "reanalysed. The attached proxy report gives mean, sample SD, 95% t intervals, "
        "and paired exact Wilcoxon comparisons across three seeds. The intervals are "
        "imprecise at this sample size; repeated 150-epoch runs of the submitted "
        "experiment remain unaddressed.",
    ),
    (
        "Reviewer 2, comment 1 — biological validity and local labels",
        "The local cassava and maize images and their label/diagnostic records were "
        "not supplied, so we cannot authenticate their disease names, causal agents, "
        "diagnostic criteria, or pathologist/laboratory review. The proxy uses the "
        "published source labels from PlantVillage and PlantDoc without claiming "
        "independent pathology confirmation. Five generic PlantDoc 'leaf' labels are "
        "mapped to PlantVillage healthy labels by name only, an unverified "
        "cross-source assumption that may introduce label error. PlantDoc's generic "
        "pepper 'leaf spot' label is also mapped to PlantVillage bacterial spot by "
        "name only, without confirming the pathogen. This does not resolve biological "
        "validation; disease identities should follow independently reviewed labels.",
    ),
    (
        "Reviewer 2, comment 2 — source-wise counts and bounding boxes",
        "The original Roboflow export is unavailable. The proxy class mapping, source "
        "counts, split counts, source revisions, image hashes, and box counts are "
        "recorded in data/class_mapping.csv, data/manifest.csv, and data/manifest.json. "
        "PlantDoc's released boxes are retained. PlantVillage supplies image-level "
        "labels only, so each PlantVillage image receives one full-frame box, not a "
        "lesion box. Five generic PlantDoc 'leaf' labels are mapped to healthy classes "
        "by name only, not verified pathologically. The PlantDoc Hugging Face "
        "card omits a license, but AgML's source registry lists CC BY-SA 4.0; retain "
        "attribution/share-alike and verify terms before redistribution.",
    ),
    (
        "Reviewer 2, comment 3 — partitions, leakage, independent test results",
        "The original split files and identifiers were not supplied. In the proxy, "
        "sampling and 80/10/10 "
        "partitions are fixed before preprocessing; available physical-leaf IDs in "
        "PlantVillage are grouped, while PlantDoc can only be split by image because "
        "plant/farm/session IDs are absent. Test metrics are reported for the "
        "combined proxy and separately for PlantVillage and PlantDoc. Residual "
        "near-duplicate/plant-level leakage in PlantDoc cannot be ruled out.",
    ),
    (
        "Reviewer 2, comment 4 — detector implementation and training records",
        "The related PDF does not verify the submitted model: it lists 300 epochs in "
        "the training section, ends its results table at epoch 149, and its appendix "
        "example uses YOLOv8n/Ultralytics 8.2.58 rather than YOLOv10. The revised "
        "manuscript separately says 150 epochs and Google Colab. The proxy identifies "
        "YOLOv10n, its Ultralytics/PyTorch versions, CPU hardware, training arguments, "
        "seed, and checkpoint paths in results/experiment_config.json and per-run "
        "logs/checkpoints. It uses AdamW and a five-epoch schedule.",
    ),
    (
        "Reviewer 2, comment 5 — preprocessing ablation",
        "The proxy compares unchanged input, dark-channel-prior dehazing, luminance "
        "histogram equalization, and their combination under matched training settings. "
        "It evaluates clear images and a deterministically synthesized haze condition; "
        "algorithm parameters and code are supplied in prepare_proxy_data.py. The thesis "
        "describes guided-filter refinement but its appendix code omits it; the proxy "
        "follows the appendix code and records that discrepancy. Synthetic "
        "haze is not field-measured degradation.",
    ),
    (
        "Reviewer 2, comment 6 — definition, per-class results, and errors",
        "The proxy reports per-class precision, recall, F1, AP@0.5 and AP@0.5:0.95, "
        "confusion matrices, test-set results, and seed-level variation. Detection "
        "accuracy is not reported because the original 94% value is undefined and "
        "cannot be reconstructed without its calculation and test predictions.",
    ),
    (
        "Reviewer 2, comment 7 — IoT latency, trials, and early detection",
        "No phone, cloud deployment, transmission/notification logs, or field-trial "
        "records were supplied. Capture-to-alert, upload, preprocessing, "
        "inference, and notification latency were not measured, and no field trial is "
        "claimed. This draft response explicitly distinguishes visible-symptom "
        "recognition from early-stage diagnosis. The original real-time, reliability, "
        "field-trial, and early-detection claims require evidence or must be withdrawn.",
    ),
    (
        "Reviewer 2, comment 8 — comparison table and references",
        "We do not rely on the challenged cross-paper performance figures in the proxy "
        "analysis. The cited Alsakar et al. model designation must be YOLOv11n–DeiT, "
        "not YOLOv10n; its reported metrics should be removed unless verified directly "
        "against the original paper. The manuscript also has in-text citations without "
        "matching entries (including Shueil et al., Dun et al., and Nnaedozie et al.). "
        "A complete source-by-source reference audit is still required before "
        "resubmission; no unverified DOI or bibliographic entry is invented here.",
    ),
]

EDITORIAL = [
    "Citation wording: change forms such as “According to [5]” to “According to Ref. [5]” "
    "or “According to Author et al. [5]”.",
    "Use “Figure” and “Table” consistently when referring to numbered items in the text.",
    "Verify every DOI and link against the cited primary publication; add DOI links where "
    "they exist and do not invent missing DOIs.",
    "Ensure every in-text citation has exactly one matching reference and every reference "
    "is cited. The missing Shueil, Dun, and Nnaedozie entries still need primary-source audit.",
    "Cite and discuss every retained table and figure in the main text, explaining its "
    "purpose and key information.",
    "Punctuate every equation correctly and verify the journal's equation formatting.",
    "Proofread the complete revised manuscript for language, spelling, and typographical errors.",
    "Replace any scanned, blurred, or unreadable figures with original, publication-quality "
    "artwork; this package has not validated or replaced the source manuscript's figures.",
    "Add a Data Availability section with stable links and exact dataset/code versions. "
    "The proxy links/revisions are recorded in the experiment package; the original local "
    "dataset is unavailable.",
    "Apply the Journal of the Nigerian Society of Physical Sciences manuscript/reference "
    "style and verify the current author guidelines.",
    "The supplied work is an empirical engineering study rather than a mathematical paper; "
    "confirm whether LaTeX is required with the editor before submission.",
    "Apply the journal's book and book-chapter reference formats to any such sources; "
    "verify publisher, location, pages, and DOI rather than assuming journal format.",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _format_metric(value: str) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA" if not value else value
    return f"{number:.4f}" if math.isfinite(number) else "NA"


def build() -> None:
    manifest_path = DATA / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    summary = _read_csv(RESULTS / "summary_mean_sd_ci.csv")
    report_exists = (RESULTS / "EXPERIMENT_REPORT.md").exists()
    status = (
        "The public-data proxy experiment completed; its measured output is linked below."
        if report_exists
        else "The public-data proxy experiment has not completed; no proxy metrics are asserted."
    )
    warning = (
        "DRAFT — NOT READY TO SUBMIT. Scope: results below are from a separate "
        "public-data proxy experiment, not measurements from the submitted study."
    )
    replies = list(REPLIES)
    if not report_exists:
        replies[0] = (
            replies[0][0],
            "The submitted run's training data, source code, checkpoint, and run logs "
            "were not supplied, so its historical results could not be statistically "
            "reanalysed. The public-data proxy is still in progress, so this draft "
            "reports no proxy measurements. Repeated 150-epoch runs remain unaddressed.",
        )
        replies[5] = (
            replies[5][0],
            "The proxy scripts define a comparison of unchanged input, dark-channel-prior "
            "dehazing, luminance histogram equalization, and their combination. No "
            "completed ablation measurements are available in this package yet. The "
            "thesis describes guided-filter refinement but its appendix code omits it; "
            "the planned proxy follows the appendix code. Synthetic haze is not "
            "field-measured degradation.",
        )
        replies[6] = (
            replies[6][0],
            "The planned proxy report will include per-class precision, recall, F1, "
            "AP@0.5 and AP@0.5:0.95, confusion matrices, and seed-level variation. "
            "No completed proxy metrics are available yet. Detection accuracy is not "
            "reported because the original 94% value lacks a defined calculation "
            "and test predictions.",
        )
    if not manifest:
        replies[2] = (
            replies[2][0],
            "The original Roboflow export is unavailable, and the proxy data manifest "
            "has not been generated. Its sampling, source counts, split counts, and "
            "annotation details therefore cannot yet be reported. PlantVillage has "
            "image-level labels only, so the planned proxy uses full-frame boxes, not "
            "lesion boxes.",
        )
        replies[3] = (
            replies[3][0],
            "The original split files and identifiers were not supplied. No proxy "
            "split manifest or held-out results are available yet; plant/session-level "
            "leakage cannot be ruled out for PlantDoc.",
        )
        replies[4] = (
            replies[4][0],
            "The related PDF does not verify the submitted model: it lists 300 epochs "
            "in the training section, ends its results table at epoch 149, and its "
            "appendix example uses YOLOv8n/Ultralytics 8.2.58 rather than YOLOv10. "
            "The revised manuscript separately says 150 epochs and Google Colab. "
            "No proxy training configuration or run logs are available yet.",
        )
    lines = [
        "# Response to reviewers — author draft",
        "",
        f"> **{warning}**",
        "",
        status,
        "",
        "The experiment report contains methods, measurements, and source details.",
        "",
        "## Reviewer 1",
        "",
        f"**{replies[0][0]}**",
        "",
        replies[0][1],
        "",
    ]
    for heading, reply in replies[1:]:
        lines += [f"## {heading}", "", reply, ""]
    lines += ["## Editorial comments", ""]
    lines.extend(f"- {entry}" for entry in EDITORIAL)
    lines += [
        "",
        "## Proxy results",
        "",
        "The complete methods, run-level outputs, per-class results, confusion matrices, "
        "confidence intervals, paired tests, and limitations are in "
        "[results/EXPERIMENT_REPORT.md](./results/EXPERIMENT_REPORT.md).",
        "",
    ]
    if summary:
        lines += [
            "| Method | Condition | Source | Metric | n | Mean | SD | 95% CI |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for row in summary:
            lines.append(
                f"| {row['method']} | {row['test_condition']} | {row['test_source']} | "
                f"{row['metric']} | {row['n']} | {_format_metric(row['mean'])} | "
                f"{_format_metric(row['sd'])} | "
                f"[{_format_metric(row['ci95_low'])}, {_format_metric(row['ci95_high'])}] |"
            )
        lines.append("")
    lines += [
        "## Data and files",
        "",
        f"- Dataset revisions: `{json.dumps(manifest.get('source_revisions', {}), sort_keys=True)}`",
        "- Dataset counts and image-level split details: `data/manifest.json` and `data/manifest.csv`.",
        "- Class mapping and annotation conventions: `data/class_mapping.csv` and `data/manifest.json`.",
        "- Third-party dataset terms and attribution: `THIRD_PARTY_DATA_LICENSES.md`.",
        "- Scripts and pinned dependencies: `prepare_proxy_data.py`, `run_ablation.py`, and `requirements.txt`.",
        "- Source-document discrepancies: `SOURCE_DOCUMENT_AUDIT.md`.",
        "",
        "## Required before resubmission",
        "",
        "Recover the original images/annotations and run records, or remove all unsupported "
        "original-study performance claims and agree with the editor on a replacement study. "
        "Obtain/record pathologist review, verify all citations/DOIs against primary sources, "
        "provide actual independent test and multi-seed results, and measure the full IoT "
        "pipeline on documented hardware. Apply PlantDoc attribution/share-alike "
        "obligations before redistribution or publication.",
    ]
    markdown_path = ROOT / "RESPONSE_TO_REVIEWERS_DRAFT.md"
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    document.styles["Normal"].font.name = "Arial"
    document.styles["Normal"].font.size = Pt(10)
    document.add_heading("Response to reviewers — author draft", 0)
    paragraph = document.add_paragraph()
    run = paragraph.add_run(warning)
    run.bold = True
    document.add_paragraph(status)
    document.add_paragraph("See the experiment report for methods and measured outputs.")
    document.add_heading("Reviewer 1", level=1)
    document.add_heading(replies[0][0], level=2)
    document.add_paragraph(replies[0][1])
    for heading, reply in replies[1:]:
        document.add_heading(heading, level=1)
        document.add_paragraph(reply)
    document.add_heading("Editorial comments", level=1)
    for entry in EDITORIAL:
        document.add_paragraph(entry, style="List Bullet")
    document.add_heading("Proxy results", level=1)
    document.add_paragraph(
        "See results/EXPERIMENT_REPORT.md for the full methods, run-level outputs, "
        "per-class results, confusion matrices, confidence intervals, paired tests, "
        "and limitations."
    )
    if summary:
        table = document.add_table(rows=1, cols=8)
        table.style = "Light Shading Accent 1"
        headers = ["Method", "Condition", "Source", "Metric", "n", "Mean", "SD", "95% CI"]
        for cell, value in zip(table.rows[0].cells, headers, strict=True):
            cell.text = value
        for row in summary:
            cells = table.add_row().cells
            values = [
                row["method"],
                row["test_condition"],
                row["test_source"],
                row["metric"],
                row["n"],
                _format_metric(row["mean"]),
                _format_metric(row["sd"]),
                f"[{_format_metric(row['ci95_low'])}, {_format_metric(row['ci95_high'])}]",
            ]
            for cell, value in zip(cells, values, strict=True):
                cell.text = value
    document.add_heading("Data and files", level=1)
    document.add_paragraph(
        f"Dataset revisions: {json.dumps(manifest.get('source_revisions', {}), sort_keys=True)}"
    )
    document.add_paragraph(
        "Counts/splits: data/manifest.json and data/manifest.csv. Class mapping and "
        "annotation conventions: data/class_mapping.csv. Third-party dataset terms: "
        "THIRD_PARTY_DATA_LICENSES.md. Scripts and dependencies: prepare_proxy_data.py, "
        "run_ablation.py, requirements.txt. Source-document discrepancies: "
        "SOURCE_DOCUMENT_AUDIT.md."
    )
    document.add_heading("Required before resubmission", level=1)
    document.add_paragraph(
        "Recover the original images/annotations and run records, or remove all "
        "unsupported original-study performance claims and agree with the editor on "
        "a replacement study. Obtain/record pathologist review, verify all citations/"
        "DOIs against primary sources, provide actual independent test and multi-seed "
        "results, and measure the full IoT pipeline on documented hardware. Apply "
        "PlantDoc attribution/share-alike obligations before redistribution or publication."
    )
    document.save(ROOT / "RESPONSE_TO_REVIEWERS_DRAFT.docx")

    editorial_lines = [
        "# Editorial response — author draft",
        "",
        "> **DRAFT — NOT READY TO SUBMIT.** The source manuscript has not been edited. "
        "Each item below remains an author action; the package does not claim that the "
        "journal's formatting or reference corrections were applied.",
        "",
    ]
    editorial_lines.extend(f"- **Pending:** {entry}" for entry in EDITORIAL)
    (ROOT / "EDITORIAL_RESPONSE_DRAFT.md").write_text(
        "\n".join(editorial_lines) + "\n", encoding="utf-8"
    )
    editorial_document = Document()
    editorial_document.sections[0].top_margin = Inches(0.7)
    editorial_document.sections[0].bottom_margin = Inches(0.7)
    editorial_document.styles["Normal"].font.name = "Arial"
    editorial_document.styles["Normal"].font.size = Pt(10)
    editorial_document.add_heading("Editorial response — author draft", 0)
    paragraph = editorial_document.add_paragraph()
    run = paragraph.add_run(
        "DRAFT — NOT READY TO SUBMIT. The source manuscript has not been edited. "
        "Each item remains an author action; no formatting or reference correction "
        "is represented as applied."
    )
    run.bold = True
    for entry in EDITORIAL:
        editorial_document.add_paragraph(f"Pending: {entry}", style="List Bullet")
    editorial_document.save(ROOT / "EDITORIAL_RESPONSE_DRAFT.docx")


if __name__ == "__main__":
    build()
