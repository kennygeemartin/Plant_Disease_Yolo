"""Download pinned public data and make a reproducible YOLO-format proxy sample."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from collections import Counter, defaultdict
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import cv2
import numpy as np
from PIL import Image
import requests


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PV_ID = "geraldmc/plantvillage-full"
PV_REVISION = "f808f2706d3ce50ce14652d2b6863d3cc30cf9c4"
PLANTDOC_ID = "Project-AgML/plant_doc_detection"
PLANTDOC_REVISION = "0bed0b75b3f0e563d21b6a4e69d15da21b245986"

# Name-based crosswalk; ambiguous healthy/disease assignments are disclosed in the package.
CLASS_MAP = {
    "Apple scab": {
        "plantvillage": "Apple___Apple_scab",
        "plantdoc": "Apple Scab Leaf",
    },
    "Apple healthy": {
        "plantvillage": "Apple___healthy",
        "plantdoc": "Apple leaf",
    },
    "Bell pepper bacterial spot": {
        "plantvillage": "Pepper,_bell___Bacterial_spot",
        "plantdoc": "Bell_pepper leaf spot",
    },
    "Bell pepper healthy": {
        "plantvillage": "Pepper,_bell___healthy",
        "plantdoc": "Bell_pepper leaf",
    },
    "Corn gray leaf spot": {
        "plantvillage": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "plantdoc": "Corn Gray leaf spot",
    },
    "Corn common rust": {
        "plantvillage": "Corn_(maize)___Common_rust_",
        "plantdoc": "Corn rust leaf",
    },
    "Grape black rot": {
        "plantvillage": "Grape___Black_rot",
        "plantdoc": "grape leaf black rot",
    },
    "Grape healthy": {
        "plantvillage": "Grape___healthy",
        "plantdoc": "grape leaf",
    },
    "Potato healthy": {
        "plantvillage": "Potato___healthy",
        "plantdoc": "Potato leaf",
    },
    "Potato early blight": {
        "plantvillage": "Potato___Early_blight",
        "plantdoc": "Potato leaf early blight",
    },
    "Potato late blight": {
        "plantvillage": "Potato___Late_blight",
        "plantdoc": "Potato leaf late blight",
    },
    "Tomato late blight": {
        "plantvillage": "Tomato___Late_blight",
        "plantdoc": "Tomato leaf late blight",
    },
    "Tomato Septoria leaf spot": {
        "plantvillage": "Tomato___Septoria_leaf_spot",
        "plantdoc": "Tomato Septoria leaf spot",
    },
    "Tomato healthy": {
        "plantvillage": "Tomato___healthy",
        "plantdoc": "Tomato leaf",
    },
}
CLASS_NAMES = list(CLASS_MAP)
CLASS_ID = {name: index for index, name in enumerate(CLASS_NAMES)}
PV_LABEL_TO_CLASS = {
    values["plantvillage"]: name for name, values in CLASS_MAP.items()
}
PLANTDOC_LABEL_TO_CLASS = {
    values["plantdoc"]: name for name, values in CLASS_MAP.items()
}
DATASETS_SERVER = "https://datasets-server.huggingface.co/"
HUGGING_FACE_API = "https://huggingface.co/api/datasets/"
METHODS = ("baseline", "dehaze", "equalize", "combined")


def _resize_longest(image: np.ndarray, max_side: int = 640) -> np.ndarray:
    height, width = image.shape[:2]
    scale = min(1.0, max_side / max(height, width))
    if scale < 1:
        image = cv2.resize(
            image,
            (max(1, round(width * scale)), max(1, round(height * scale))),
            interpolation=cv2.INTER_AREA,
        )
    return image


def _dehaze(bgr: np.ndarray) -> np.ndarray:
    image = bgr.astype(np.float32)
    dark = cv2.erode(
        image.min(axis=2), np.ones((15, 15), dtype=np.uint8)
    )
    flat = image.reshape(-1, 3)
    dark_flat = dark.reshape(-1)
    count = max(1, int(dark_flat.size * 0.001))
    indices = np.argsort(dark_flat)[-count:]
    atmospheric = flat[indices].max(axis=0)
    atmospheric = np.maximum(atmospheric, 1.0)
    normalized_dark = (image / atmospheric).min(axis=2)
    normalized_dark = cv2.erode(
        normalized_dark, np.ones((15, 15), dtype=np.uint8)
    )
    transmission = np.maximum(1.0 - 0.95 * normalized_dark, 0.1)
    recovered = (image - atmospheric) / transmission[..., None] + atmospheric
    return np.clip(recovered, 0, 255).astype(np.uint8)


def _equalize_luminance(bgr: np.ndarray) -> np.ndarray:
    yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
    yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)


def transform(bgr: np.ndarray, method: str, hazy: bool = False) -> np.ndarray:
    result = bgr.copy()
    if hazy:
        result = np.clip(
            result.astype(np.float32) * 0.68 + 235.0 * 0.32, 0, 255
        ).astype(np.uint8)
    if method in ("dehaze", "combined"):
        result = _dehaze(result)
    if method in ("equalize", "combined"):
        result = _equalize_luminance(result)
    return result


def _yolo_box_file(boxes: list[tuple[int, float, float, float, float]]) -> str:
    return "".join(
        f"{class_id} {cx:.6f} {cy:.6f} {width:.6f} {height:.6f}\n"
        for class_id, cx, cy, width, height in boxes
    )


def _request_json(
    endpoint: str,
    params: dict[str, Any],
    context: str,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(7):
        try:
            response = requests.get(endpoint, params=params, timeout=(15, 90))
            response.raise_for_status()
            payload = response.json()
            if payload.get("partial"):
                raise RuntimeError(f"{context} returned a partial response.")
            return payload
        except (requests.RequestException, ValueError, RuntimeError) as error:
            last_error = error
            if attempt < 6:
                wait_seconds = min(60, 2 ** (attempt + 1))
                if (
                    isinstance(error, requests.HTTPError)
                    and error.response is not None
                    and error.response.status_code == 429
                ):
                    retry_after = error.response.headers.get("Retry-After")
                    try:
                        wait_seconds = float(retry_after) if retry_after else 60
                    except ValueError:
                        wait_seconds = 60
                time.sleep(wait_seconds)
    raise RuntimeError(f"Could not retrieve {context}.") from last_error


def _write_item(
    item: dict[str, Any],
    split: str,
    image_index: int,
    raw_dir: Path,
    manifest_rows: list[dict[str, Any]],
) -> None:
    image = _resize_longest(np.asarray(item["image"].convert("RGB")))
    height, width = image.shape[:2]
    path = raw_dir / "images" / split / f"{image_index:06d}.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR)):
        raise OSError(f"Could not write image: {path}")
    boxes = []
    for class_name, (x, y, box_width, box_height) in item["boxes"]:
        x1 = float(np.clip(x / item["original_width"], 0, 1))
        y1 = float(np.clip(y / item["original_height"], 0, 1))
        x2 = float(np.clip((x + box_width) / item["original_width"], 0, 1))
        y2 = float(np.clip((y + box_height) / item["original_height"], 0, 1))
        if x2 <= x1 or y2 <= y1:
            continue
        boxes.append(
            (
                CLASS_ID[class_name],
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                x2 - x1,
                y2 - y1,
            )
        )
    if not boxes:
        path.unlink(missing_ok=True)
        return
    label_path = raw_dir / "labels" / split / f"{image_index:06d}.txt"
    label_path.parent.mkdir(parents=True, exist_ok=True)
    label_path.write_text(_yolo_box_file(boxes), encoding="utf-8")
    manifest_rows.append(
        {
            "image_id": f"{image_index:06d}",
            "source": item["source"],
            "source_revision": item["source_revision"],
            "source_label": item["source_label"],
            "primary_class": item["primary_class"],
            "split": split,
            "upstream_split": item.get("upstream_split"),
            "leaf_grouped": item.get("leaf_grouped", False),
            "leaf_id": item.get("leaf_id"),
            "sha256_rgb": item["sha256"],
            "box_count": len(boxes),
            "box_semantics": (
                "full-frame proxy box from image-level label; not lesion localization"
                if item["source"] == "PlantVillage"
                else "source PlantDoc object/leaf box; no independent pathology review"
            ),
            "width": width,
            "height": height,
        }
    )


def _iter_dataset_rows(dataset_id: str, revision: str):
    endpoint = urljoin(DATASETS_SERVER, "rows")
    base_params = {
        "dataset": dataset_id,
        "config": "default",
        "split": "train",
        "offset": 0,
        "length": 100,
    }

    def get_page(offset: int) -> dict[str, Any]:
        params = {**base_params, "offset": offset}
        return _request_json(
            endpoint,
            params,
            f"{dataset_id}@{revision} rows at offset {offset}",
        )

    first_page = get_page(0)
    total = first_page.get("num_rows_total")
    page_size = first_page.get("num_rows_per_page", 100)
    if not isinstance(total, int) or total < 1:
        raise ValueError(f"Dataset API did not report row count for {dataset_id}.")
    for entry in first_page["rows"]:
        yield entry["row"]
    for offset in range(page_size, total, page_size):
        if offset % 10000 == 0:
            print(f"{dataset_id}: scanned {offset:,}/{total:,} rows", flush=True)
        page = get_page(offset)
        for entry in page["rows"]:
            yield entry["row"]
        time.sleep(1.1)


def _validate_dataset_revision(dataset_id: str, revision: str) -> None:
    response = _request_json(
        f"{HUGGING_FACE_API}{dataset_id}/revision/main",
        {},
        f"{dataset_id} current revision",
    )
    current_revision = response.get("sha")
    if current_revision != revision:
        raise RuntimeError(
            f"{dataset_id} main is at {current_revision!r}, not pinned revision "
            f"{revision!r}; the rows API only serves the current dataset snapshot."
        )


def _reservoir_rows(
    rows,
    class_for_row,
    limit: int,
    seed: int,
    source: str,
) -> dict[str, list[dict[str, Any]]]:
    reservoirs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: Counter[str] = Counter()
    rng = random.Random(seed)
    for row in rows:
        class_name = class_for_row(row)
        if class_name is None:
            continue
        seen[class_name] += 1
        reservoir = reservoirs[class_name]
        if len(reservoir) < limit:
            reservoir.append(row)
        else:
            replacement = rng.randrange(seen[class_name])
            if replacement < limit:
                reservoir[replacement] = row
    _validate_reservoirs(reservoirs, seen, limit, source)
    return reservoirs


def _download_image(row: dict[str, Any]) -> Image.Image:
    image_info = row["image"]
    response = requests.get(image_info["src"], timeout=(15, 90))
    response.raise_for_status()
    image = Image.open(BytesIO(response.content)).convert("RGB")
    expected_size = (image_info["width"], image_info["height"])
    if image.size != expected_size:
        raise ValueError(
            f"Downloaded image size {image.size} does not match metadata "
            f"{expected_size}."
        )
    return image


def _plantvillage_items(limit: int, seed: int) -> list[dict[str, Any]]:
    reservoirs = _reservoir_rows(
        _iter_dataset_rows(PV_ID, PV_REVISION),
        lambda row: PV_LABEL_TO_CLASS.get(row["class_label"]),
        limit,
        seed,
        "PlantVillage",
    )
    selected = [
        row
        for class_name in CLASS_NAMES
        for row in reservoirs[class_name]
    ]
    with ThreadPoolExecutor(max_workers=6) as pool:
        images = list(pool.map(_download_image, selected))
    items = []
    for row, image in zip(selected, images, strict=True):
        image_np = np.asarray(image)
        class_name = PV_LABEL_TO_CLASS[row["class_label"]]
        items.append(
            {
                "image": image,
                "source": "PlantVillage",
                "source_revision": PV_REVISION,
                "source_label": row["class_label"],
                "primary_class": class_name,
                "original_width": image.width,
                "original_height": image.height,
                "sha256": hashlib.sha256(image_np.tobytes()).hexdigest(),
                "boxes": [(class_name, (0, 0, image.width, image.height))],
                "leaf_id": row.get("leaf_id"),
                "leaf_grouped": row.get("leaf_grouped", False),
                "upstream_split": row.get("split"),
            }
        )
    return items


def _plantdoc_label_names() -> list[str]:
    schema_rows = _request_json(
        urljoin(DATASETS_SERVER, "rows"),
        {
            "dataset": PLANTDOC_ID,
            "config": "default",
            "split": "train",
            "offset": 0,
            "length": 1,
        },
        "PlantDoc feature schema",
    )
    objects_feature = next(
        feature for feature in schema_rows["features"] if feature["name"] == "objects"
    )
    return objects_feature["type"]["categories"]["feature"]["names"]


def _plantdoc_items(
    limit: int,
    seed: int,
    label_names: list[str] | None = None,
) -> list[dict[str, Any]]:
    if label_names is None:
        label_names = _plantdoc_label_names()

    def class_for_row(row: dict[str, Any]) -> str | None:
        for category_id in row["objects"]["categories"]:
            class_name = PLANTDOC_LABEL_TO_CLASS.get(label_names[int(category_id)])
            if class_name:
                return class_name
        return None

    rows = _reservoir_rows(
        _iter_dataset_rows(PLANTDOC_ID, PLANTDOC_REVISION),
        class_for_row,
        limit,
        seed,
        "PlantDoc detection",
    )
    selected = [
        row
        for class_name in CLASS_NAMES
        for row in rows[class_name]
    ]
    with ThreadPoolExecutor(max_workers=6) as pool:
        images = list(pool.map(_download_image, selected))
    items = []
    for row, image in zip(selected, images, strict=True):
        original_width, original_height = image.size
        boxes = []
        source_label = None
        for box, category_id in zip(
            row["objects"]["bbox"], row["objects"]["categories"], strict=True
        ):
            label = label_names[int(category_id)]
            class_name = PLANTDOC_LABEL_TO_CLASS.get(label)
            if not class_name:
                continue
            source_label = source_label or label
            x, y, width, height = map(float, box)
            boxes.append((class_name, (x, y, width, height)))
        if not boxes:
            raise ValueError("Selected PlantDoc row has no supported box labels.")
        image_np = np.asarray(image)
        resized_image = Image.fromarray(_resize_longest(image_np, max_side=640))
        items.append(
            {
                "image": resized_image,
                "source": "PlantDoc detection",
                "source_revision": PLANTDOC_REVISION,
                "source_label": source_label,
                "primary_class": boxes[0][0],
                "original_width": original_width,
                "original_height": original_height,
                "sha256": hashlib.sha256(image_np.tobytes()).hexdigest(),
                "boxes": boxes,
                "leaf_id": None,
                "leaf_grouped": False,
                "upstream_split": "train",
            }
        )
    return items


def _validate_reservoirs(
    reservoirs: dict[str, list[dict[str, Any]]],
    seen: Counter[str],
    limit: int,
    source: str,
) -> list[dict[str, Any]]:
    insufficient = {
        class_name: {"seen": seen[class_name], "sampled": len(reservoirs[class_name])}
        for class_name in CLASS_NAMES
        if 0 < len(reservoirs[class_name]) < 10
    }
    if insufficient:
        raise ValueError(
            f"{source} has fewer than 10 sampleable images for required classes: "
            f"{insufficient}"
        )
    return [
        item
        for class_name in CLASS_NAMES
        for item in reservoirs[class_name][:limit]
    ]


def _split_items(items: list[dict[str, Any]], seed: int) -> dict[str, list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        groups[(item["source"], item["primary_class"])].append(item)
    splits = {"train": [], "val": [], "test": []}
    for key in sorted(groups):
        leaf_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in groups[key]:
            # PlantVillage provides leaf IDs; PlantDoc has no plant/session IDs,
            # so only exact image duplicates can be grouped for that source.
            group_id = (
                item["leaf_id"]
                if item.get("leaf_grouped") and item.get("leaf_id")
                else item["sha256"]
            )
            leaf_groups[str(group_id)].append(item)
        group_list = list(leaf_groups.values())
        if len(group_list) < 3:
            raise ValueError(
                f"Need at least three independent image/leaf groups in {key}; "
                f"found {len(group_list)}."
            )
        random.Random(f"{seed}:{key}").shuffle(group_list)
        total = sum(len(group) for group in group_list)
        train_target, val_target = total * 0.8, total * 0.9
        train_count = val_count = 0
        for index, group in enumerate(group_list):
            remaining_groups = len(group_list) - index
            if train_count < train_target and remaining_groups > 2:
                splits["train"].extend(group)
                train_count += len(group)
            elif val_count < val_target - train_target and remaining_groups > 1:
                splits["val"].extend(group)
                val_count += len(group)
            else:
                splits["test"].extend(group)
        if not all(
            any(item["source"] == key[0] and item["primary_class"] == key[1]
                for item in splits[split])
            for split in ("train", "val", "test")
        ):
            raise ValueError(f"Group split did not populate all partitions for {key}")
    return splits


def _write_yamls(processed_root: Path) -> None:
    names = json.dumps(CLASS_NAMES, ensure_ascii=False)
    for method in METHODS:
        base = processed_root / method
        for condition in ("clear", "hazy"):
            for source in ("all", "plantvillage", "plantdoc"):
                if source == "all":
                    test_path = (
                        "images/test"
                        if condition == "clear"
                        else f"../{method}_hazy_test/images/test"
                    )
                else:
                    suffix = (
                        f"{method}_test_{source}"
                        if condition == "clear"
                        else f"{method}_hazy_test_{source}"
                    )
                    test_path = f"../{suffix}/images/test"
                yaml_path = base / f"data_{condition}_{source}.yaml"
                yaml_path.write_text(
                    f"path: {base.resolve().as_posix()}\n"
                    "train: images/train\n"
                    "val: images/val\n"
                    f"test: {test_path}\n"
                    f"names: {names}\n",
                    encoding="utf-8",
                )


def prepare(limit: int, seed: int) -> None:
    raw_dir = DATA / "raw"
    processed_root = DATA / "processed"
    if raw_dir.exists():
        raise FileExistsError(
            f"{raw_dir} already exists; move it aside before regenerating data."
        )
    _validate_dataset_revision(PV_ID, PV_REVISION)
    _validate_dataset_revision(PLANTDOC_ID, PLANTDOC_REVISION)
    plantdoc_label_names = _plantdoc_label_names()
    items = _plantvillage_items(limit, seed) + _plantdoc_items(
        limit, seed, plantdoc_label_names
    )
    seen: set[str] = set()
    unique = []
    for item in items:
        if item["sha256"] in seen:
            continue
        seen.add(item["sha256"])
        unique.append(item)
    split_items = _split_items(unique, seed)
    manifest_rows: list[dict[str, Any]] = []
    image_index = 0
    for split in ("train", "val", "test"):
        for item in split_items[split]:
            _write_item(item, split, image_index, raw_dir, manifest_rows)
            image_index += 1

    raw_manifest = DATA / "manifest.csv"
    DATA.mkdir(parents=True, exist_ok=True)
    with raw_manifest.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    with (DATA / "class_mapping.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["class_id", "canonical_proxy_class", "PlantVillage label", "PlantDoc label"])
        for name, values in CLASS_MAP.items():
            writer.writerow(
                [CLASS_ID[name], name, values["plantvillage"], values["plantdoc"]]
            )

    counts = Counter((row["source"], row["split"]) for row in manifest_rows)
    source_class_split = Counter(
        (row["source"], row["primary_class"], row["split"])
        for row in manifest_rows
    )
    summary = {
        "study_type": "public-data proxy; not replication of the submitted study",
        "seed_for_sampling_and_splitting": seed,
        "cap_per_source_class_before_exact_pixel_deduplication": limit,
        "classes": CLASS_NAMES,
        "source_revisions": {
            PV_ID: PV_REVISION,
            PLANTDOC_ID: PLANTDOC_REVISION,
        },
        "source_licenses": {
            PV_ID: "CC0-1.0, as stated on its Hugging Face dataset card",
            PLANTDOC_ID: (
                "Hugging Face dataset card omits a license; AgML source registry "
                "at f0e0135c7fbd425e7e329b9ac45186cdaf03a47b lists CC BY-SA 4.0"
            ),
        },
        "split_counts_by_source": {
            f"{source}/{split}": count
            for (source, split), count in sorted(counts.items())
        },
        "primary_class_counts_by_source_and_split": {
            f"{source}/{class_name}/{split}": count
            for (source, class_name, split), count in sorted(source_class_split.items())
        },
        "unobserved_primary_classes_by_source": {
            source: [
                class_name
                for class_name in CLASS_NAMES
                if not any(
                    observed_source == source and observed_class == class_name
                    for observed_source, observed_class, _ in source_class_split
                )
            ]
            for source in sorted({source for source, _ in counts})
        },
        "class_mapping_notes": [
            "PlantDoc generic leaf labels are mapped to PlantVillage healthy labels by name only; this assumption is not independently verified.",
            "PlantDoc Bell_pepper leaf spot is crosswalked to PlantVillage bacterial spot by name; the causal agent is not independently verified.",
            "PlantDoc had no observed Potato leaf rows in the selected data.",
        ],
        "plantvillage_annotation": (
            "one normalized full-frame box generated from the image-level class "
            "label; not lesion localization"
        ),
        "plantdoc_annotation": (
            "upstream boxes converted from [x,y,width,height] pixel coordinates; "
            "not independently pathology verified"
        ),
        "split": (
            "deterministic 80/10/10 stratification by source and primary class; "
            "PlantVillage images with upstream physical-leaf IDs are kept in one "
            "partition, other PlantVillage images and PlantDoc are split by exact "
            "image; augmentations follow splitting"
        ),
        "limitations": [
            "no original Nigerian field images or source annotations",
            "PlantDoc has no plant/farm/session identifiers; related images may "
            "cross splits; PlantVillage grouping is incomplete for some classes",
            "PlantDoc's Hugging Face card omits a license; AgML's source registry "
            "lists CC BY-SA 4.0; retain attribution/share-alike and verify terms "
            "before redistribution",
            "PlantVillage full-frame boxes and PlantDoc source leaf/object boxes "
            "are not equivalent targets",
            "PlantDoc generic healthy-label and pepper bacterial-spot mappings are "
            "name-based assumptions without independent biological confirmation",
        ],
    }
    (DATA / "manifest.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    for method in METHODS:
        for split in ("train", "val", "test"):
            source_images = sorted((raw_dir / "images" / split).glob("*.jpg"))
            for source_image in source_images:
                bgr = cv2.imread(str(source_image))
                if bgr is None:
                    raise OSError(f"Could not read image: {source_image}")
                transformed = transform(bgr, method)
                out = processed_root / method / "images" / split / source_image.name
                out.parent.mkdir(parents=True, exist_ok=True)
                if not cv2.imwrite(str(out), transformed):
                    raise OSError(f"Could not write image: {out}")
                label_src = raw_dir / "labels" / split / source_image.with_suffix(".txt").name
                label_dst = processed_root / method / "labels" / split / label_src.name
                label_dst.parent.mkdir(parents=True, exist_ok=True)
                label_dst.write_bytes(label_src.read_bytes())
        for source_image in sorted((raw_dir / "images" / "test").glob("*.jpg")):
            bgr = cv2.imread(str(source_image))
            if bgr is None:
                raise OSError(f"Could not read image: {source_image}")
            transformed = transform(bgr, method, hazy=True)
            out = (
                processed_root
                / f"{method}_hazy_test"
                / "images"
                / "test"
                / source_image.name
            )
            out.parent.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(out), transformed):
                raise OSError(f"Could not write image: {out}")
            label_src = raw_dir / "labels" / "test" / source_image.with_suffix(".txt").name
            label_dst = (
                processed_root
                / f"{method}_hazy_test"
                / "labels"
                / "test"
                / label_src.name
            )
            label_dst.parent.mkdir(parents=True, exist_ok=True)
            label_dst.write_bytes(label_src.read_bytes())

    source_by_id = {
        row["image_id"]: (
            "plantvillage" if row["source"] == "PlantVillage" else "plantdoc"
        )
        for row in manifest_rows
        if row["split"] == "test"
    }
    for method in METHODS:
        for condition, source_root in (
            ("clear", processed_root / method),
            ("hazy", processed_root / f"{method}_hazy_test"),
        ):
            for image_path in sorted(
                (source_root / "images" / "test").glob("*.jpg")
            ):
                source = source_by_id[image_path.stem]
                target_root = processed_root / (
                    f"{method}_test_{source}"
                    if condition == "clear"
                    else f"{method}_hazy_test_{source}"
                )
                target_image = target_root / "images" / "test" / image_path.name
                target_label = (
                    target_root / "labels" / "test" / image_path.with_suffix(".txt").name
                )
                target_image.parent.mkdir(parents=True, exist_ok=True)
                target_label.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image_path, target_image)
                label_path = (
                    source_root
                    / "labels"
                    / "test"
                    / image_path.with_suffix(".txt").name
                )
                shutil.copyfile(label_path, target_label)
    _write_yamls(processed_root)
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-per-class", type=int, default=20)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    if args.limit_per_class < 10:
        parser.error("--limit-per-class must be at least 10 for 80/10/10 splits")
    prepare(args.limit_per_class, args.seed)


if __name__ == "__main__":
    main()
