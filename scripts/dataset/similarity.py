import csv

import imagehash

from PIL import Image, ImageDraw

from dataset.config import OUTPUT_DIR


def compute_image_hashes(
    samples: list[dict],
) -> list[dict]:
    """
    Compute perceptual hashes for images.

    pHash lets us find visually similar images,
    not only byte-identical duplicates.
    """
    hashed_samples = []

    for sample in samples:
        try:
            with Image.open(
                sample["image_path"]
            ) as image:
                image_hash = (
                    imagehash.phash(
                        image
                    )
                )

            hashed_samples.append(
                {
                    **sample,
                    "phash": image_hash,
                }
            )

        except Exception as exc:
            print(
                "WARNING: could not hash "
                f"{sample['image_path']}: "
                f"{exc}"
            )

    return hashed_samples


def find_similar_images(
    hashed_samples: list[dict],
    max_distance: int = 4,
) -> list[dict]:
    """
    Find visually similar image pairs.

    Smaller pHash distance means more visual similarity.
    Distance 0 means identical perceptual hashes.
    """
    similar_pairs = []

    for i in range(
        len(hashed_samples)
    ):
        for j in range(
            i + 1,
            len(hashed_samples),
        ):
            first = (
                hashed_samples[i]
            )

            second = (
                hashed_samples[j]
            )

            distance = (
                first["phash"]
                - second["phash"]
            )

            if distance <= max_distance:
                similar_pairs.append(
                    {
                        "source_1": (
                            first[
                                "source_dataset"
                            ]
                        ),
                        "filename_1": (
                            first[
                                "filename"
                            ]
                        ),
                        "source_2": (
                            second[
                                "source_dataset"
                            ]
                        ),
                        "filename_2": (
                            second[
                                "filename"
                            ]
                        ),
                        "hash_distance": (
                            distance
                        ),
                    }
                )

    return similar_pairs


def save_similar_pairs(
    similar_pairs: list[dict],
    output_path,
) -> None:
    """
    Save visually similar image pairs to CSV.
    """
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "source_1",
                "filename_1",
                "source_2",
                "filename_2",
                "hash_distance",
            ],
        )

        writer.writeheader()
        writer.writerows(
            similar_pairs
        )


def create_similar_pairs_contact_sheet(
    similar_pairs: list[dict],
    selected_samples: list[dict],
    output_path,
) -> None:
    """
    Create a side-by-side preview
    of suspicious image pairs.
    """
    if not similar_pairs:
        return

    sample_lookup = {
        (
            sample["source_dataset"],
            sample["filename"],
        ): sample
        for sample in selected_samples
    }

    thumb_width = 300
    thumb_height = 220
    row_height = 280

    sheet_width = (
        thumb_width * 2
    )

    sheet_height = (
        row_height
        * len(similar_pairs)
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

    for row, pair in enumerate(
        similar_pairs
    ):
        key_1 = (
            pair["source_1"],
            pair["filename_1"],
        )

        key_2 = (
            pair["source_2"],
            pair["filename_2"],
        )

        sample_1 = (
            sample_lookup[key_1]
        )

        sample_2 = (
            sample_lookup[key_2]
        )

        pair_images = [
            (
                sample_1,
                pair["filename_1"],
            ),
            (
                sample_2,
                pair["filename_2"],
            ),
        ]

        for column, (
            sample,
            filename,
        ) in enumerate(
            pair_images
        ):
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

                x = (
                    column
                    * thumb_width
                )

                y = (
                    row
                    * row_height
                )

                sheet.paste(
                    image,
                    (x, y),
                )

            draw.text(
                (
                    x + 5,
                    y
                    + thumb_height
                    + 5,
                ),
                filename,
                fill="black",
            )

        draw.text(
            (
                5,
                row
                * row_height
                + thumb_height
                + 25,
            ),
            (
                "pHash distance: "
                f"{pair['hash_distance']}"
            ),
            fill="black",
        )

    sheet.save(
        output_path,
        quality=90,
    )