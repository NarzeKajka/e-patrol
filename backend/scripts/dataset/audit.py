import csv
import random

from pathlib import Path

from PIL import Image, ImageDraw

from dataset.config import (
    RANDOM_SEED,
    CROSS_CLASS_AUDIT_SAMPLE_COUNT,
    CROSS_CLASS_AUDIT_DIR,
)


# ============================================================
# CROSS-CLASS VISUAL AUDIT
# ============================================================

def create_cross_class_contact_sheet(
    samples: list[dict],
    epatrol_class: str,
    sample_count: int = CROSS_CLASS_AUDIT_SAMPLE_COUNT,
    seed: int = RANDOM_SEED,
) -> Path:
    """
    Create a deterministic random contact sheet
    for cross-class visual inspection.

    The goal is to check whether images assigned to one
    e-Patrol class visibly contain objects belonging to
    another final e-Patrol class that are not annotated.
    """
    rng = random.Random(seed)

    selected = rng.sample(
        samples,
        min(
            sample_count,
            len(samples),
        ),
    )

    thumb_width = 300
    thumb_height = 220

    columns = 4

    rows = (
        len(selected)
        + columns
        - 1
    ) // columns

    label_height = 55

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
            sample["image_path"]
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

        source_dataset = (
            sample["source_dataset"]
        )

        filename = (
            sample["filename"]
        )

        draw.text(
            (
                x + 4,
                y
                + thumb_height
                + 4,
            ),
            (
                f"{source_dataset} | "
                f"{filename[:30]}"
            ),
            fill="black",
        )

    output_path = (
        CROSS_CLASS_AUDIT_DIR
        / f"{epatrol_class}_samples.jpg"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sheet.save(
        output_path,
        quality=90,
    )

    return output_path


def save_cross_class_audit_manifest(
    class_samples: dict[str, list[dict]],
) -> Path:
    """
    Save the exact random images used in the
    cross-class visual audit.

    The empty audit columns can later be filled
    after visual inspection.
    """
    output_path = (
        CROSS_CLASS_AUDIT_DIR
        / "cross_class_audit.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.writer(
            csv_file
        )

        writer.writerow(
            [
                "epatrol_class",
                "source_dataset",
                "original_split",
                "original_filename",
                "contains_other_epatrol_class",
                "other_class",
                "notes",
            ]
        )

        for (
            epatrol_class,
            samples,
        ) in class_samples.items():

            for sample in samples:
                writer.writerow(
                    [
                        epatrol_class,
                        sample[
                            "source_dataset"
                        ],
                        sample.get(
                            "original_split",
                            "",
                        ),
                        sample[
                            "filename"
                        ],
                        "",
                        "",
                        "",
                    ]
                )

    return output_path


def prepare_cross_class_audit(
    road_samples: list[dict],
    waste_samples: list[dict],
    graffiti_samples: list[dict],
) -> None:
    """
    Prepare deterministic visual samples from all
    three e-Patrol classes for cross-class inspection.
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "CROSS-CLASS VISUAL AUDIT"
    )
    print(
        "=" * 45
    )

    datasets = {
        "road_damage": road_samples,
        "waste": waste_samples,
        "graffiti": graffiti_samples,
    }

    selected_by_class = {}

    for index, (
        epatrol_class,
        samples,
    ) in enumerate(
        datasets.items()
    ):
        rng = random.Random(
            RANDOM_SEED + index
        )

        selected = rng.sample(
            samples,
            min(
                CROSS_CLASS_AUDIT_SAMPLE_COUNT,
                len(samples),
            ),
        )

        selected_by_class[
            epatrol_class
        ] = selected

        # We pass the already selected samples,
        # therefore sample_count == len(selected).
        contact_sheet_path = (
            create_cross_class_contact_sheet(
                samples=selected,
                epatrol_class=epatrol_class,
                sample_count=len(selected),
                seed=RANDOM_SEED,
            )
        )

        print(
            f"{epatrol_class}: "
            f"{len(selected)} images"
        )

        print(
            "  Contact sheet: "
            f"{contact_sheet_path}"
        )

    manifest_path = (
        save_cross_class_audit_manifest(
            selected_by_class
        )
    )

    print(
        "\nAudit manifest: "
        f"{manifest_path}"
    )
