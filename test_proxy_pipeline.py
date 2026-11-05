import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image

from prepare_proxy_data import (
    CLASS_NAMES,
    METHODS,
    _split_items,
    _write_item,
    _validate_reservoirs,
    transform,
)
from run_ablation import _metric_value, _write_confusion


class PreprocessingTests(unittest.TestCase):
    def test_all_methods_preserve_image_shape_and_type(self):
        image = np.zeros((64, 80, 3), dtype=np.uint8)
        image[:, :, 0] = np.arange(80, dtype=np.uint8)[None, :]
        image[:, :, 1] = np.arange(64, dtype=np.uint8)[:, None]
        for method in METHODS:
            with self.subTest(method=method):
                result = transform(image, method)
                self.assertEqual(result.shape, image.shape)
                self.assertEqual(result.dtype, np.uint8)
                self.assertTrue(np.isfinite(result).all())

    def test_baseline_is_unchanged(self):
        image = np.full((32, 32, 3), 127, dtype=np.uint8)
        np.testing.assert_array_equal(transform(image, "baseline"), image)


class SplitTests(unittest.TestCase):
    def test_leaf_groups_do_not_cross_partitions(self):
        items = []
        for index in range(40):
            items.append(
                {
                    "source": "PlantVillage",
                    "primary_class": "Apple scab",
                    "leaf_id": f"leaf-{index // 2}",
                    "leaf_grouped": True,
                    "sha256": f"image-{index}",
                }
            )
        partitions = _split_items(items, seed=7)
        seen = {}
        for split, images in partitions.items():
            for item in images:
                group = item["leaf_id"]
                if group in seen:
                    self.assertEqual(seen[group], split)
                else:
                    seen[group] = split
        self.assertEqual(len(seen), 20)
        self.assertEqual(set(partitions), {"train", "val", "test"})

    def test_source_can_omit_categories_absent_from_its_labels(self):
        reservoirs = {name: [] for name in CLASS_NAMES}
        seen = Counter()
        reservoirs[CLASS_NAMES[0]] = [{} for _ in range(10)]
        seen[CLASS_NAMES[0]] = 10
        self.assertEqual(
            _validate_reservoirs(reservoirs, seen, limit=20, source="fixture"),
            reservoirs[CLASS_NAMES[0]],
        )

    def test_source_with_too_few_examples_for_a_category_fails(self):
        reservoirs = {name: [] for name in CLASS_NAMES}
        seen = Counter()
        reservoirs[CLASS_NAMES[0]] = [{} for _ in range(9)]
        seen[CLASS_NAMES[0]] = 9
        with self.assertRaisesRegex(ValueError, "fewer than 10 sampleable"):
            _validate_reservoirs(reservoirs, seen, limit=20, source="fixture")

    def test_write_item_creates_image_and_label_directories(self):
        image = Image.new("RGB", (16, 12), color=(30, 60, 90))
        item = {
            "image": image,
            "source": "PlantVillage",
            "source_revision": "fixture",
            "source_label": "Apple___Apple_scab",
            "primary_class": "Apple scab",
            "original_width": 16,
            "original_height": 12,
            "sha256": "fixture-hash",
            "boxes": [("Apple scab", (0, 0, 16, 12))],
            "leaf_id": None,
            "leaf_grouped": False,
            "upstream_split": "train",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "raw"
            manifest_rows = []
            _write_item(item, "train", 0, root, manifest_rows)
            self.assertTrue(
                (root / "images" / "train" / "000000.jpg").is_file()
            )
            self.assertTrue(
                (root / "labels" / "train" / "000000.txt").is_file()
            )
            self.assertEqual(len(manifest_rows), 1)


class MetricIndexTests(unittest.TestCase):
    def test_per_class_metrics_follow_class_ids_not_present_order(self):
        box = SimpleNamespace(
            p=np.array([0.75, 0.25]),
            r=np.array([0.5, 0.125]),
            ap_class_index=np.array([3, 10]),
        )
        metrics = SimpleNamespace(box=box)
        self.assertEqual(_metric_value(metrics, "p", 3), 0.75)
        self.assertEqual(_metric_value(metrics, "p", 10), 0.25)
        self.assertTrue(np.isnan(_metric_value(metrics, "p", 0)))

    def test_per_class_ap_averages_iou_thresholds(self):
        box = SimpleNamespace(
            ap=np.array([[0.8, 0.6], [0.4, 0.2]]),
            ap_class_index=np.array([5, 12]),
        )
        metrics = SimpleNamespace(box=box)
        self.assertAlmostEqual(_metric_value(metrics, "ap", 12), 0.3)


class ConfusionMatrixTests(unittest.TestCase):
    def test_confusion_matrix_is_written_with_background_label(self):
        matrix = SimpleNamespace(matrix=np.array([[3, 1], [2, 4]]))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "confusion.csv"
            _write_confusion(matrix, path, ["Apple scab"])
            with path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.reader(file))
        self.assertEqual(rows[0], ["true\\predicted", "Apple scab", "background"])
        self.assertEqual(rows[1], ["Apple scab", "3", "1"])


if __name__ == "__main__":
    unittest.main()
