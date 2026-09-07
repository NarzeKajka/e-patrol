from collections import Counter
from pathlib import Path

import csv
import xml.etree.ElementTree as ET

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
    RDD_CLASSES,
    ROAD_SAMPLES_PER_COUNTRY,
    ROAD_PHASH_MAX_DISTANCE,
    ROAD_DATASETS,
    ROAD_MANIFEST_PATH,
)


# ============================================================
# ROAD DAMAGE — RDD2022
# ============================================================

def read_rdd_annotation(
    xml_path: Path,
) -> list[str]:
    """
    Return road-damage classes occurring
    in one RDD2022 image.
    """
    root = ET.parse(
        xml_path
    ).getroot()

    classes = []

    for obj in root.findall(
        "object"
    ):
        name = obj.findtext(
            "name"
        )

        if name in RDD_CLASSES:
            classes.append(
                name
            )

    return classes


def get_road_samples(
    dataset_name: str,
    paths: dict,
) -> list[dict]:
    """
    Collect positive road-damage images
    from one RDD2022 country.
    """
    samples = []

    xml_files = sorted(
        paths["annotations"].glob(
            "*.xml"
        )
    )

    for xml_path in xml_files:
        classes = (
            read_rdd_annotation(
                xml_path
            )
        )

        # Only positive road-damage images.
        if not classes:
            continue

        image_path = (
            paths["images"]
            / f"{xml_path.stem}.jpg"
        )

        if not image_path.exists():
            print(
                "WARNING: missing image for "
                f"{xml_path.name}"
            )
            continue

        samples.append(
            {
                "source_dataset": (
                    dataset_name
                ),
                "filename": (
                    image_path.name
                ),
                "image_path": (
                    image_path
                ),
                "annotation_path": (
                    xml_path
                ),
                "classes": (
                    classes
                ),
            }
        )

    return samples


def print_road_selection_stats(
    name: str,
    selected: list[dict],
) -> None:
    """
    Print statistics for selected road-damage images.
    """
    object_counts = Counter()
    image_class_counts = Counter()

    for sample in selected:
        object_counts.update(
            sample["classes"]
        )

        image_class_counts.update(
            set(
                sample["classes"]
            )
        )

    print(
        f"\n{name.upper()} SELECTED"
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
        "\nObjects by original RDD class:"
    )

    for class_name in sorted(
        RDD_CLASSES
    ):
        print(
            f"  {class_name}: "
            f"{object_counts[class_name]}"
        )

    print(
        "\nImages containing each class:"
    )

    for class_name in sorted(
        RDD_CLASSES
    ):
        print(
            f"  {class_name}: "
            f"{image_class_counts[class_name]}"
        )


def save_road_manifest(
    selected_samples: list[dict],
) -> None:
    """
    Save selected road-damage candidates
    to a reproducibility manifest.
    """
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ROAD_MANIFEST_PATH.open(
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
                "original_filename",
                "original_classes",
                "epatrol_class",
            ]
        )

        sorted_samples = sorted(
            selected_samples,
            key=lambda sample: (
                sample[
                    "source_dataset"
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
                        "filename"
                    ],
                    ";".join(
                        sample[
                            "classes"
                        ]
                    ),
                    "road_damage",
                ]
            )


def prepare_road_damage_candidates(
) -> list[dict]:
    """
    Prepare the 1000-image road_damage candidate pool:
    500 Czech + 500 Norway.
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "ROAD DAMAGE PREPARATION"
    )
    print(
        "=" * 45
    )

    all_selected = []

    for index, (
        name,
        paths,
    ) in enumerate(
        ROAD_DATASETS.items()
    ):
        samples = (
            get_road_samples(
                name,
                paths,
            )
        )

        print(
            f"\n{name.upper()}"
        )
        print(
            "-" * 35
        )

        print(
            "Available positive images: "
            f"{len(samples)}"
        )

        selected = select_samples(
            samples=samples,
            target_count=(
                ROAD_SAMPLES_PER_COUNTRY
            ),
            seed=(
                RANDOM_SEED
                + index
            ),
        )

        print_road_selection_stats(
            name,
            selected,
        )

        all_selected.extend(
            selected
        )

    save_road_manifest(
        all_selected
    )

    print(
        "\nManifest saved to: "
        f"{ROAD_MANIFEST_PATH}"
    )

    print(
        "\nCHECKING ROAD-DAMAGE "
        "SIMILARITY"
    )
    print(
        "-" * 35
    )

    hashed_samples = (
        compute_image_hashes(
            all_selected
        )
    )

    similar_pairs = (
        find_similar_images(
            hashed_samples,
            max_distance=(
                ROAD_PHASH_MAX_DISTANCE
            ),
        )
    )

    pairs_path = (
        OUTPUT_DIR
        / "road_damage_similar_pairs.csv"
    )

    contact_sheet_path = (
        OUTPUT_DIR
        / "road_damage_similar_pairs.jpg"
    )

    save_similar_pairs(
        similar_pairs,
        pairs_path,
    )

    create_similar_pairs_contact_sheet(
        similar_pairs,
        all_selected,
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
        "\nFINAL ROAD_DAMAGE "
        "CANDIDATE POOL"
    )
    print(
        "-" * 35
    )

    print(
        "Total images: "
        f"{len(all_selected)}"
    )

    print(
        "e-Patrol class: road_damage"
    )

    return all_selected
