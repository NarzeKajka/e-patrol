from collections import Counter
from pathlib import Path

import csv
import random

from PIL import Image, ImageDraw

from dataset.common import (
    select_samples,
)

from dataset.similarity import (
    compute_image_hashes,
    find_similar_images,
    save_similar_pairs,
    create_similar_pairs_contact_sheet,
)

from dataset.config import (
    RANDOM_SEED,
    OUTPUT_DIR,
    WASTE_DATASET,
    WASTE_TARGET_COUNT,
    WASTE_PHASH_MAX_DISTANCE,
    WASTE_SPLITS,
    WASTE_CLASSES,
    WASTE_MANIFEST_PATH,
)


# ============================================================
# WASTE — ILLEGAL DUMPING
# ============================================================

def read_yolo_class_ids(
    label_path: Path,
) -> list[int]:
    """
    Read all class IDs from one YOLO label file.
    """
    class_ids = []

    lines = (
        label_path.read_text(
            encoding="utf-8"
        ).splitlines()
    )

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        class_id = int(
            parts[0]
        )

        class_ids.append(
            class_id
        )

    return class_ids


def audit_waste_split(
    split_name: str,
) -> dict:
    """
    Audit one original Roboflow split.
    """
    images_dir = (
        WASTE_DATASET
        / split_name
        / "images"
    )

    labels_dir = (
        WASTE_DATASET
        / split_name
        / "labels"
    )

    image_files = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file()
    )

    label_files = sorted(
        labels_dir.glob(
            "*.txt"
        )
    )

    class_counts = Counter()

    empty_labels = 0
    total_boxes = 0
    missing_labels = []

    for image_path in image_files:
        label_path = (
            labels_dir
            / f"{image_path.stem}.txt"
        )

        if not label_path.exists():
            missing_labels.append(
                image_path.name
            )
            continue

        class_ids = (
            read_yolo_class_ids(
                label_path
            )
        )

        if not class_ids:
            empty_labels += 1
            continue

        class_counts.update(
            class_ids
        )

        total_boxes += len(
            class_ids
        )

    print(
        f"\nWASTE "
        f"{split_name.upper()}"
    )
    print(
        "-" * 35
    )

    print(
        "Images:         "
        f"{len(image_files)}"
    )

    print(
        "Labels:         "
        f"{len(label_files)}"
    )

    print(
        "Boxes:          "
        f"{total_boxes}"
    )

    print(
        "Empty labels:   "
        f"{empty_labels}"
    )

    print(
        "Missing labels: "
        f"{len(missing_labels)}"
    )

    print(
        "\nBoxes by source class:"
    )

    for (
        class_id,
        class_name,
    ) in WASTE_CLASSES.items():

        print(
            f"  {class_id} "
            f"{class_name}: "
            f"{class_counts[class_id]}"
        )

    return {
        "images": (
            len(image_files)
        ),
        "labels": (
            len(label_files)
        ),
        "boxes": (
            total_boxes
        ),
        "empty_labels": (
            empty_labels
        ),
        "missing_labels": (
            len(missing_labels)
        ),
        "class_counts": (
            class_counts
        ),
    }


def audit_waste_dataset() -> None:
    """
    Audit the complete Illegal Dumping dataset.
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "WASTE DATASET AUDIT"
    )
    print(
        "=" * 45
    )

    total_images = 0
    total_labels = 0
    total_boxes = 0
    total_empty = 0
    total_missing = 0

    total_class_counts = Counter()

    for split_name in WASTE_SPLITS:
        stats = (
            audit_waste_split(
                split_name
            )
        )

        total_images += (
            stats["images"]
        )

        total_labels += (
            stats["labels"]
        )

        total_boxes += (
            stats["boxes"]
        )

        total_empty += (
            stats["empty_labels"]
        )

        total_missing += (
            stats["missing_labels"]
        )

        total_class_counts.update(
            stats[
                "class_counts"
            ]
        )

    print(
        "\nWASTE TOTAL"
    )
    print(
        "-" * 35
    )

    print(
        "Images:         "
        f"{total_images}"
    )

    print(
        "Labels:         "
        f"{total_labels}"
    )

    print(
        "Boxes:          "
        f"{total_boxes}"
    )

    print(
        "Empty labels:   "
        f"{total_empty}"
    )

    print(
        "Missing labels: "
        f"{total_missing}"
    )

    print(
        "\nBoxes by source class:"
    )

    for (
        class_id,
        class_name,
    ) in WASTE_CLASSES.items():

        print(
            f"  {class_id} "
            f"{class_name}: "
            f"{total_class_counts[class_id]}"
        )


def get_waste_samples() -> list[dict]:
    """
    Collect all Illegal Dumping images.

    The original Roboflow split is preserved
    as metadata in every sample.
    """
    samples = []

    for split_name in WASTE_SPLITS:
        images_dir = (
            WASTE_DATASET
            / split_name
            / "images"
        )

        labels_dir = (
            WASTE_DATASET
            / split_name
            / "labels"
        )

        image_lookup = {
            path.stem: path
            for path in images_dir.iterdir()
            if path.is_file()
        }

        label_files = sorted(
            labels_dir.glob(
                "*.txt"
            )
        )

        for label_path in label_files:
            image_path = (
                image_lookup.get(
                    label_path.stem
                )
            )

            if image_path is None:
                print(
                    "WARNING: missing image "
                    f"for {split_name}/"
                    f"{label_path.name}"
                )
                continue

            class_ids = (
                read_yolo_class_ids(
                    label_path
                )
            )

            samples.append(
                {
                    "source_dataset": (
                        "illegal_dumping"
                    ),
                    "original_split": (
                        split_name
                    ),
                    "filename": (
                        image_path.name
                    ),
                    "image_path": (
                        image_path
                    ),
                    "label_path": (
                        label_path
                    ),
                    "classes": (
                        class_ids
                    ),
                }
            )

    return samples


def print_waste_selection_stats(
    selected: list[dict],
) -> None:
    """
    Print statistics for selected waste candidates.
    """
    object_counts = Counter()
    image_class_counts = Counter()
    split_counts = Counter()

    for sample in selected:
        object_counts.update(
            sample["classes"]
        )

        image_class_counts.update(
            set(
                sample["classes"]
            )
        )

        split_counts[
            sample["original_split"]
        ] += 1

    print(
        "\nWASTE SELECTED"
    )
    print(
        "-" * 35
    )

    print(
        f"Images: {len(selected)}"
    )

    print(
        "Objects: "
        f"{sum(object_counts.values())}"
    )

    print(
        "\nImages by original split:"
    )

    for split_name in WASTE_SPLITS:
        print(
            f"  {split_name}: "
            f"{split_counts[split_name]}"
        )

    print(
        "\nObjects by source class:"
    )

    for (
        class_id,
        class_name,
    ) in WASTE_CLASSES.items():

        print(
            f"  {class_name}: "
            f"{object_counts[class_id]}"
        )

    print(
        "\nImages containing each class:"
    )

    for (
        class_id,
        class_name,
    ) in WASTE_CLASSES.items():

        print(
            f"  {class_name}: "
            f"{image_class_counts[class_id]}"
        )


def save_waste_manifest(
    selected: list[dict],
) -> None:
    """
    Save selected waste candidates
    to a reproducibility manifest.
    """
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with WASTE_MANIFEST_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.writer(
            csv_file
        )

        writer.writerow(
            [
                "source_dataset",
                "original_split",
                "original_filename",
                "original_classes",
                "epatrol_class",
            ]
        )

        sorted_samples = sorted(
            selected,
            key=lambda sample: (
                sample[
                    "original_split"
                ],
                sample[
                    "filename"
                ],
            ),
        )

        for sample in sorted_samples:
            class_names = [
                WASTE_CLASSES[
                    class_id
                ]
                for class_id
                in sample["classes"]
            ]

            writer.writerow(
                [
                    sample[
                        "source_dataset"
                    ],
                    sample[
                        "original_split"
                    ],
                    sample[
                        "filename"
                    ],
                    ";".join(
                        class_names
                    ),
                    "waste",
                ]
            )


# ------------------------------------------------------------
# WASTE VISUAL AUDIT
# ------------------------------------------------------------

def collect_waste_samples_by_class(
) -> dict[int, list[dict]]:
    """
    Group waste images by source class
    for visual inspection.
    """
    samples_by_class = {
        class_id: []
        for class_id in WASTE_CLASSES
    }

    samples = (
        get_waste_samples()
    )

    for sample in samples:
        unique_classes = set(
            sample["classes"]
        )

        for class_id in unique_classes:
            samples_by_class[
                class_id
            ].append(
                sample
            )

    return samples_by_class


def create_waste_class_contact_sheet(
    samples_per_class: int = 12,
    seed: int = RANDOM_SEED,
) -> Path:
    """
    Create a random contact sheet
    for every source waste class.
    """
    samples_by_class = (
        collect_waste_samples_by_class()
    )

    rng = random.Random(
        seed
    )

    thumb_width = 220
    thumb_height = 165

    columns = 4

    rows_per_class = (
        samples_per_class
        + columns
        - 1
    ) // columns

    label_height = 40
    class_header_height = 35

    section_height = (
        class_header_height
        + rows_per_class
        * (
            thumb_height
            + label_height
        )
    )

    sheet_width = (
        columns
        * thumb_width
    )

    sheet_height = (
        len(WASTE_CLASSES)
        * section_height
    )

    sheet = Image.new(
        "RGB",
        (
            sheet_width,
            sheet_height,
        ),
        "white",
    )

    draw = ImageDraw.Draw(
        sheet
    )

    y_section = 0

    for (
        class_id,
        class_name,
    ) in WASTE_CLASSES.items():

        available = (
            samples_by_class[
                class_id
            ]
        )

        selected = rng.sample(
            available,
            min(
                samples_per_class,
                len(available),
            ),
        )

        draw.text(
            (
                10,
                y_section + 8,
            ),
            (
                f"{class_id}: "
                f"{class_name}"
            ),
            fill="black",
        )

        for (
            index,
            sample,
        ) in enumerate(
            selected
        ):
            row = (
                index
                // columns
            )

            column = (
                index
                % columns
            )

            x = (
                column
                * thumb_width
            )

            y = (
                y_section
                + class_header_height
                + row
                * (
                    thumb_height
                    + label_height
                )
            )

            with Image.open(
                sample[
                    "image_path"
                ]
            ) as image:

                image = (
                    image.convert(
                        "RGB"
                    )
                )

                image.thumbnail(
                    (
                        thumb_width,
                        thumb_height,
                    )
                )

                sheet.paste(
                    image,
                    (x, y),
                )

            draw.text(
                (
                    x + 4,
                    y
                    + thumb_height
                    + 4,
                ),
                sample[
                    "filename"
                ][:28],
                fill="black",
            )

        y_section += (
            section_height
        )

    output_path = (
        OUTPUT_DIR
        / "waste_class_samples.jpg"
    )

    sheet.save(
        output_path,
        quality=90,
    )

    return output_path


def prepare_waste_candidates(
) -> list[dict]:
    """
    Audit Illegal Dumping, select 1000 deterministic
    waste candidates and check near-duplicates.
    """
    audit_waste_dataset()

    print(
        "\nCREATING WASTE "
        "CLASS SAMPLE"
    )
    print(
        "-" * 35
    )

    contact_sheet = (
        create_waste_class_contact_sheet(
            samples_per_class=12,
        )
    )

    print(
        "Contact sheet saved to: "
        f"{contact_sheet}"
    )

    print(
        "\nSELECTING WASTE "
        "CANDIDATES"
    )
    print(
        "-" * 35
    )

    waste_samples = (
        get_waste_samples()
    )

    print(
        "Available images: "
        f"{len(waste_samples)}"
    )

    selected = select_samples(
        samples=waste_samples,
        target_count=(
            WASTE_TARGET_COUNT
        ),
        seed=(
            RANDOM_SEED
        ),
    )

    print_waste_selection_stats(
        selected
    )

    save_waste_manifest(
        selected
    )

    print(
        "\nManifest saved to: "
        f"{WASTE_MANIFEST_PATH}"
    )

    print(
        "\nCHECKING WASTE SIMILARITY"
    )
    print(
        "-" * 35
    )

    hashed_samples = (
        compute_image_hashes(
            selected
        )
    )

    similar_pairs = (
        find_similar_images(
            hashed_samples,
            max_distance=(
                WASTE_PHASH_MAX_DISTANCE
            ),
        )
    )

    pairs_path = (
        OUTPUT_DIR
        / "waste_similar_pairs.csv"
    )

    contact_sheet_path = (
        OUTPUT_DIR
        / "waste_similar_pairs.jpg"
    )

    save_similar_pairs(
        similar_pairs,
        pairs_path,
    )

    create_similar_pairs_contact_sheet(
        similar_pairs,
        selected,
        contact_sheet_path,
    )

    print(
        "Hashed images: "
        f"{len(hashed_samples)}"
    )

    print(
        "Similar pairs found: "
        f"{len(similar_pairs)}"
    )

    print(
        "Results saved to: "
        f"{pairs_path}"
    )

    if similar_pairs:
        print(
            "Contact sheet saved to: "
            f"{contact_sheet_path}"
        )

    print(
        "\nFINAL WASTE "
        "CANDIDATE POOL"
    )
    print(
        "-" * 35
    )

    print(
        "Total images: "
        f"{len(selected)}"
    )

    print(
        "e-Patrol class: waste"
    )

    return selected
