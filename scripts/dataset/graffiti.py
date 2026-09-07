from collections import Counter
from pathlib import Path

import csv
import random

from PIL import Image, ImageDraw

from dataset.similarity import (
    compute_image_hashes,
    find_similar_images,
    save_similar_pairs,
    create_similar_pairs_contact_sheet,
)

from dataset.config import (
    RANDOM_SEED,
    OUTPUT_DIR,
    STORM_IMAGES_DIR,
    STORM_ANNOTATIONS_DIR,
    STORM_SPLITS,
    STORM_PHASH_MAX_DISTANCE,
    STORM_MANIFEST_PATH,
)


# ============================================================
# GRAFFITI — STORM
# ============================================================

def audit_storm_split(
    split_name: str,
) -> dict:
    """
    Audit one STORM split
    and its bounding-box annotations.
    """
    images_dir = (
        STORM_IMAGES_DIR
        / split_name
    )

    csv_path = (
        STORM_ANNOTATIONS_DIR
        / f"{split_name}_labels.csv"
    )

    image_files = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file()
    )

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:

        reader = csv.DictReader(
            csv_file
        )

        rows = list(
            reader
        )

    annotated_filenames = {
        row["filename"]
        for row in rows
    }

    classes = Counter(
        row["class"]
        for row in rows
    )

    existing_filenames = {
        path.name
        for path in image_files
    }

    missing_images = (
        annotated_filenames
        - existing_filenames
    )

    images_without_annotations = (
        existing_filenames
        - annotated_filenames
    )

    print(
        f"\nSTORM "
        f"{split_name.upper()}"
    )
    print(
        "-" * 35
    )

    print(
        "Images:                    "
        f"{len(image_files)}"
    )

    print(
        "Annotated images:          "
        f"{len(annotated_filenames)}"
    )

    print(
        "Bounding boxes:            "
        f"{len(rows)}"
    )

    print(
        "Missing images:            "
        f"{len(missing_images)}"
    )

    print(
        "Images without annotations:"
        f" {len(images_without_annotations)}"
    )

    print(
        "\nClasses:"
    )

    for (
        class_name,
        count,
    ) in sorted(
        classes.items()
    ):
        print(
            f"  {class_name}: "
            f"{count}"
        )

    return {
        "images": (
            len(image_files)
        ),
        "annotated_images": (
            len(
                annotated_filenames
            )
        ),
        "boxes": (
            len(rows)
        ),
        "missing_images": (
            len(
                missing_images
            )
        ),
        "images_without_annotations": (
            len(
                images_without_annotations
            )
        ),
        "classes": (
            classes
        ),
    }


def audit_storm_dataset() -> None:
    """
    Audit the complete STORM graffiti dataset.
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "GRAFFITI / STORM DATASET AUDIT"
    )
    print(
        "=" * 45
    )

    total_images = 0
    total_annotated_images = 0
    total_boxes = 0
    total_missing_images = 0
    total_without_annotations = 0

    total_classes = Counter()

    for split_name in STORM_SPLITS:
        stats = (
            audit_storm_split(
                split_name
            )
        )

        total_images += (
            stats[
                "images"
            ]
        )

        total_annotated_images += (
            stats[
                "annotated_images"
            ]
        )

        total_boxes += (
            stats[
                "boxes"
            ]
        )

        total_missing_images += (
            stats[
                "missing_images"
            ]
        )

        total_without_annotations += (
            stats[
                "images_without_annotations"
            ]
        )

        total_classes.update(
            stats[
                "classes"
            ]
        )

    print(
        "\nSTORM TOTAL"
    )
    print(
        "-" * 35
    )

    print(
        "Images:                    "
        f"{total_images}"
    )

    print(
        "Annotated images:          "
        f"{total_annotated_images}"
    )

    print(
        "Bounding boxes:            "
        f"{total_boxes}"
    )

    print(
        "Missing images:            "
        f"{total_missing_images}"
    )

    print(
        "Images without annotations:"
        f" {total_without_annotations}"
    )

    print(
        "\nClasses:"
    )

    for (
        class_name,
        count,
    ) in sorted(
        total_classes.items()
    ):
        print(
            f"  {class_name}: "
            f"{count}"
        )


def get_storm_samples() -> list[dict]:
    """
    Collect all STORM images together with
    their bounding-box annotations.

    STORM contains one source class: Graffiti.
    It is mapped to the e-Patrol class: graffiti.
    """
    samples = []

    for split_name in STORM_SPLITS:
        images_dir = (
            STORM_IMAGES_DIR
            / split_name
        )

        csv_path = (
            STORM_ANNOTATIONS_DIR
            / f"{split_name}_labels.csv"
        )

        annotations_by_image = {}

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:

            reader = csv.DictReader(
                csv_file
            )

            for row in reader:
                filename = (
                    row["filename"]
                )

                annotations_by_image.setdefault(
                    filename,
                    [],
                ).append(
                    {
                        "class": (
                            row["class"]
                        ),
                        "xmin": int(
                            row["xmin"]
                        ),
                        "ymin": int(
                            row["ymin"]
                        ),
                        "xmax": int(
                            row["xmax"]
                        ),
                        "ymax": int(
                            row["ymax"]
                        ),
                    }
                )

        for (
            filename,
            annotations,
        ) in sorted(
            annotations_by_image.items()
        ):
            image_path = (
                images_dir
                / filename
            )

            if not image_path.exists():
                print(
                    "WARNING: missing STORM "
                    "image "
                    f"{split_name}/"
                    f"{filename}"
                )
                continue

            samples.append(
                {
                    "source_dataset": (
                        "storm"
                    ),
                    "original_split": (
                        split_name
                    ),
                    "filename": (
                        filename
                    ),
                    "image_path": (
                        image_path
                    ),
                    "annotations": (
                        annotations
                    ),
                    "classes": [
                        annotation[
                            "class"
                        ]
                        for annotation
                        in annotations
                    ],
                }
            )

    return samples


def print_storm_candidate_stats(
    samples: list[dict],
) -> None:
    """
    Print statistics for the STORM graffiti pool.
    """
    split_counts = Counter()

    total_boxes = 0

    for sample in samples:
        split_counts[
            sample[
                "original_split"
            ]
        ] += 1

        total_boxes += len(
            sample[
                "annotations"
            ]
        )

    print(
        "\nGRAFFITI SELECTED"
    )
    print(
        "-" * 35
    )

    print(
        f"Images: {len(samples)}"
    )

    print(
        f"Objects: {total_boxes}"
    )

    print(
        "\nImages by original split:"
    )

    for split_name in STORM_SPLITS:
        print(
            f"  {split_name}: "
            f"{split_counts[split_name]}"
        )


def save_storm_manifest(
    samples: list[dict],
) -> None:
    """
    Save STORM candidate metadata
    to a reproducibility manifest.
    """
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with STORM_MANIFEST_PATH.open(
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
                "bounding_boxes",
                "epatrol_class",
            ]
        )

        sorted_samples = sorted(
            samples,
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
                    len(
                        sample[
                            "annotations"
                        ]
                    ),
                    "graffiti",
                ]
            )


def create_storm_contact_sheet(
    samples: list[dict],
    sample_count: int = 20,
    seed: int = RANDOM_SEED,
) -> Path:
    """
    Create a random contact sheet
    for visual inspection of STORM images.
    """
    rng = random.Random(
        seed
    )

    selected = rng.sample(
        samples,
        min(
            sample_count,
            len(samples),
        ),
    )

    thumb_width = 240
    thumb_height = 180

    columns = 4

    rows = (
        len(selected)
        + columns
        - 1
    ) // columns

    label_height = 40

    sheet_width = (
        columns
        * thumb_width
    )

    sheet_height = (
        rows
        * (
            thumb_height
            + label_height
        )
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

    for index, sample in enumerate(
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
            row
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

            image = image.convert(
                "RGB"
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

    output_path = (
        OUTPUT_DIR
        / "graffiti_class_samples.jpg"
    )

    sheet.save(
        output_path,
        quality=90,
    )

    return output_path


def prepare_storm_candidates(
) -> list[dict]:
    """
    Prepare the complete STORM dataset
    as the e-Patrol graffiti candidate pool.

    All 1022 images are retained.
    """
    audit_storm_dataset()

    print(
        "\nPREPARING GRAFFITI "
        "CANDIDATES"
    )
    print(
        "-" * 35
    )

    storm_samples = (
        get_storm_samples()
    )

    print(
        "Available images: "
        f"{len(storm_samples)}"
    )

    # We intentionally keep the entire STORM dataset.
    # There are only 1022 images, so removing 22 merely
    # to obtain exactly 1000 would not improve the dataset.
    selected = storm_samples

    print_storm_candidate_stats(
        selected
    )

    save_storm_manifest(
        selected
    )

    print(
        "\nManifest saved to: "
        f"{STORM_MANIFEST_PATH}"
    )

    # --------------------------------------------------------
    # STORM visual audit
    # --------------------------------------------------------

    print(
        "\nCREATING GRAFFITI "
        "CLASS SAMPLE"
    )
    print(
        "-" * 35
    )

    contact_sheet = (
        create_storm_contact_sheet(
            selected,
            sample_count=20,
        )
    )

    print(
        "Contact sheet saved to: "
        f"{contact_sheet}"
    )

    # --------------------------------------------------------
    # STORM similarity audit
    # --------------------------------------------------------

    print(
        "\nCHECKING GRAFFITI "
        "SIMILARITY"
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
                STORM_PHASH_MAX_DISTANCE
            ),
        )
    )

    pairs_path = (
        OUTPUT_DIR
        / "graffiti_similar_pairs.csv"
    )

    contact_sheet_path = (
        OUTPUT_DIR
        / "graffiti_similar_pairs.jpg"
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
        "\nFINAL GRAFFITI "
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
        "e-Patrol class: graffiti"
    )

    return selected
