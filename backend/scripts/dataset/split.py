import csv
import random

from collections import Counter
from pathlib import Path

from dataset.config import (
    FINAL_SPLIT_SEED,
    FINAL_TRAIN_RATIO,
    FINAL_VAL_RATIO,
    FINAL_TEST_RATIO,
    FINAL_MANIFEST_PATH,
)


# ============================================================
# FINAL E-PATROL DATASET
# ============================================================

def create_final_samples(
    road_samples: list[dict],
    waste_samples: list[dict],
    graffiti_samples: list[dict],
) -> list[dict]:
    """
    Combine all candidate pools into one common
    representation for the final e-Patrol dataset.
    """
    final_samples = []

    datasets = [
        (
            "road_damage",
            road_samples,
        ),
        (
            "waste",
            waste_samples,
        ),
        (
            "graffiti",
            graffiti_samples,
        ),
    ]

    for epatrol_class, samples in datasets:
        for sample in samples:

            source_dataset = (
                sample["source_dataset"]
            )

            filename = (
                sample["filename"]
            )

            sample_id = (
                f"{epatrol_class}__"
                f"{source_dataset}__"
                f"{filename}"
            )

            final_samples.append(
                {
                    "sample_id": sample_id,
                    "source_dataset": source_dataset,
                    "original_split": sample.get(
                        "original_split",
                        "",
                    ),
                    "original_filename": filename,
                    "image_path": sample["image_path"],
                    "epatrol_class": epatrol_class,

                    "annotation_path": sample.get(
                        "annotation_path"
                    ),

                    "label_path": sample.get(
                        "label_path"
                    ),

                    "annotations": sample.get(
                        "annotations"
                    ),

                    "group_id": sample_id,
                    "final_split": "",
                }
            )

    return final_samples


def load_similarity_groups(
    samples: list[dict],
    pairs_path: Path,
) -> None:
    """
    Merge samples connected by perceptual-similarity
    pairs into common groups.

    This prevents related images from being placed
    in different final train/val/test splits.
    """
    if not pairs_path.exists():
        return

    sample_lookup = {
        (
            sample["source_dataset"],
            sample["original_filename"],
        ): sample
        for sample in samples
    }

    with pairs_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        reader = csv.DictReader(
            csv_file
        )

        for row in reader:
            key_1 = (
                row["source_1"],
                row["filename_1"],
            )

            key_2 = (
                row["source_2"],
                row["filename_2"],
            )

            first = sample_lookup.get(
                key_1
            )

            second = sample_lookup.get(
                key_2
            )

            if (
                first is None
                or second is None
            ):
                continue

            group_1 = first["group_id"]
            group_2 = second["group_id"]

            if group_1 == group_2:
                continue

            # Merge the complete groups, not only
            # the current pair. This also handles
            # chains such as A-B and B-C.
            merged_group = min(
                group_1,
                group_2,
            )

            old_groups = {
                group_1,
                group_2,
            }

            for sample in samples:
                if (
                    sample["group_id"]
                    in old_groups
                ):
                    sample["group_id"] = (
                        merged_group
                    )


def print_final_group_stats(
    samples: list[dict],
) -> None:
    """
    Print basic statistics before creating
    the final train/val/test split.
    """
    class_counts = Counter(
        sample["epatrol_class"]
        for sample in samples
    )

    group_counts = Counter(
        sample["group_id"]
        for sample in samples
    )

    multi_image_groups = {
        group_id: count
        for group_id, count
        in group_counts.items()
        if count > 1
    }

    print(
        "\n"
        + "=" * 45
    )
    print(
        "FINAL DATASET — GROUP PREPARATION"
    )
    print(
        "=" * 45
    )

    print(
        f"Total images: {len(samples)}"
    )

    print(
        f"Total groups: {len(group_counts)}"
    )

    print(
        "Multi-image groups: "
        f"{len(multi_image_groups)}"
    )

    print(
        "\nImages by e-Patrol class:"
    )

    for class_name in [
        "road_damage",
        "waste",
        "graffiti",
    ]:
        print(
            f"  {class_name}: "
            f"{class_counts[class_name]}"
        )

    if multi_image_groups:
        print(
            "\nMulti-image group sizes:"
        )

        for group_id, count in sorted(
            multi_image_groups.items()
        ):
            print(
                f"  {count} images | "
                f"{group_id}"
            )


def assign_final_splits(
    samples: list[dict],
    train_ratio: float = FINAL_TRAIN_RATIO,
    val_ratio: float = FINAL_VAL_RATIO,
    test_ratio: float = FINAL_TEST_RATIO,
    seed: int = FINAL_SPLIT_SEED,
) -> None:
    """
    Assign final train/val/test splits.

    Splitting is performed at group level, so all images
    belonging to one similarity group always stay together.

    Each e-Patrol class is split separately to preserve
    approximately equal class proportions.
    """
    ratio_sum = (
        train_ratio
        + val_ratio
        + test_ratio
    )

    if abs(ratio_sum - 1.0) > 1e-9:
        raise ValueError(
            "Train/val/test ratios must sum to 1.0."
        )

    samples_by_class = {}

    for sample in samples:
        samples_by_class.setdefault(
            sample["epatrol_class"],
            [],
        ).append(
            sample
        )

    for class_index, (
        epatrol_class,
        class_samples,
    ) in enumerate(
        sorted(
            samples_by_class.items()
        )
    ):
        groups = {}

        for sample in class_samples:
            groups.setdefault(
                sample["group_id"],
                [],
            ).append(
                sample
            )

        group_list = list(
            groups.items()
        )

        rng = random.Random(
            seed + class_index
        )

        rng.shuffle(
            group_list
        )

        total_images = len(
            class_samples
        )

        target_train = round(
            total_images
            * train_ratio
        )

        target_val = round(
            total_images
            * val_ratio
        )

        split_counts = {
            "train": 0,
            "val": 0,
            "test": 0,
        }

        for (
            group_id,
            group_samples,
        ) in group_list:

            group_size = len(
                group_samples
            )

            remaining_train = (
                target_train
                - split_counts["train"]
            )

            remaining_val = (
                target_val
                - split_counts["val"]
            )

            if remaining_train > 0:
                split_name = "train"

            elif remaining_val > 0:
                split_name = "val"

            else:
                split_name = "test"

            for sample in group_samples:
                sample["final_split"] = (
                    split_name
                )

            split_counts[
                split_name
            ] += group_size


def validate_final_split(
    samples: list[dict],
) -> None:
    """
    Verify that the final split is valid.

    Checks:
    - every sample has a split,
    - one group never appears in multiple splits.
    """
    missing_split = [
        sample
        for sample in samples
        if not sample[
            "final_split"
        ]
    ]

    if missing_split:
        raise ValueError(
            f"{len(missing_split)} samples "
            "do not have a final split."
        )

    group_splits = {}

    for sample in samples:
        group_id = (
            sample["group_id"]
        )

        split_name = (
            sample["final_split"]
        )

        group_splits.setdefault(
            group_id,
            set(),
        ).add(
            split_name
        )

    leaking_groups = {
        group_id: splits
        for group_id, splits
        in group_splits.items()
        if len(splits) > 1
    }

    if leaking_groups:
        raise ValueError(
            "Group leakage detected: "
            f"{leaking_groups}"
        )


def print_final_split_stats(
    samples: list[dict],
) -> None:
    """
    Print train/val/test statistics by e-Patrol class.
    """
    class_split_counts = Counter()
    split_totals = Counter()

    for sample in samples:
        key = (
            sample["epatrol_class"],
            sample["final_split"],
        )

        class_split_counts[key] += 1
        split_totals[sample["final_split"]] += 1

    print(
        "\n"
        + "=" * 45
    )
    print(
        "FINAL DATASET — TRAIN / VAL / TEST"
    )
    print(
        "=" * 45
    )

    for class_name in [
        "road_damage",
        "waste",
        "graffiti",
    ]:
        print(
            f"\n{class_name}"
        )
        print(
            "-" * 35
        )

        for split_name in [
            "train",
            "val",
            "test",
        ]:
            count = class_split_counts[
                (
                    class_name,
                    split_name,
                )
            ]

            print(
                f"  {split_name}: {count}"
            )

    print(
        "\nTOTAL"
    )
    print(
        "-" * 35
    )

    for split_name in [
        "train",
        "val",
        "test",
    ]:
        count = split_totals[
            split_name
        ]

        print(
            f"  {split_name}: {count}"
        )

    print(
        f"\nGrand total: {len(samples)}"
    )


def save_final_manifest(
    samples: list[dict],
) -> None:
    """
    Save the complete final experimental dataset manifest.
    """
    with FINAL_MANIFEST_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.writer(
            csv_file
        )

        writer.writerow(
            [
                "sample_id",
                "source_dataset",
                "original_split",
                "original_filename",
                "epatrol_class",
                "group_id",
                "final_split",
            ]
        )

        sorted_samples = sorted(
            samples,
            key=lambda sample: (
                sample["final_split"],
                sample["epatrol_class"],
                sample["sample_id"],
            ),
        )

        for sample in sorted_samples:
            writer.writerow(
                [
                    sample["sample_id"],
                    sample["source_dataset"],
                    sample["original_split"],
                    sample["original_filename"],
                    sample["epatrol_class"],
                    sample["group_id"],
                    sample["final_split"],
                ]
            )

    print(
        "\nFinal manifest saved to: "
        f"{FINAL_MANIFEST_PATH}"
    )
