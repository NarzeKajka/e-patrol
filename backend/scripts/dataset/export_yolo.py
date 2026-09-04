import random
import shutil
import xml.etree.ElementTree as ET

from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

from dataset.config import (
    RANDOM_SEED,
    FINAL_DATASET_DIR,
    FINAL_VISUAL_AUDIT_DIR,
    FINAL_VISUAL_AUDIT_PER_CLASS,
    RDD_CLASSES,
)


# ============================================================
# FINAL YOLO EXPORT
# ============================================================

def convert_bbox_to_yolo(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    image_width: int,
    image_height: int,
) -> tuple[float, float, float, float]:
    """
    Convert absolute bounding-box coordinates:

        xmin, ymin, xmax, ymax

    to normalized YOLO coordinates:

        x_center, y_center, width, height
    """
    box_width = (
        xmax - xmin
    )

    box_height = (
        ymax - ymin
    )

    x_center = (
        xmin + box_width / 2
    )

    y_center = (
        ymin + box_height / 2
    )

    return (
        x_center / image_width,
        y_center / image_height,
        box_width / image_width,
        box_height / image_height,
    )

def get_road_yolo_annotations(
    sample: dict,
) -> list[str]:
    """
    Convert RDD2022 Pascal VOC annotations
    to the final e-Patrol YOLO format.

    D00, D10, D20 and D40 are all mapped to:

        0 = road_damage
    """
    annotation_path = (
        sample["annotation_path"]
    )

    if annotation_path is None:
        raise ValueError(
            "Missing RDD annotation path for "
            f"{sample['sample_id']}"
        )

    root = ET.parse(
        annotation_path
    ).getroot()

    size = root.find(
        "size"
    )

    image_width = int(
        size.findtext("width")
    )

    image_height = int(
        size.findtext("height")
    )

    yolo_lines = []

    for obj in root.findall(
        "object"
    ):
        class_name = obj.findtext(
            "name"
        )

        if class_name not in RDD_CLASSES:
            continue

        bbox = obj.find(
            "bndbox"
        )

        xmin = float(
            bbox.findtext("xmin")
        )

        ymin = float(
            bbox.findtext("ymin")
        )

        xmax = float(
            bbox.findtext("xmax")
        )

        ymax = float(
            bbox.findtext("ymax")
        )

        (
            x_center,
            y_center,
            width,
            height,
        ) = convert_bbox_to_yolo(
            xmin=xmin,
            ymin=ymin,
            xmax=xmax,
            ymax=ymax,
            image_width=image_width,
            image_height=image_height,
        )

        yolo_lines.append(
            (
                "0 "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{width:.6f} "
                f"{height:.6f}"
            )
        )

    return yolo_lines


def get_waste_yolo_annotations(
    sample: dict,
) -> list[str]:
    """
    Convert Illegal Dumping YOLO annotations
    to the final e-Patrol taxonomy.

    All seven source classes are mapped to:

        1 = waste
    """
    label_path = (
        sample["label_path"]
    )

    if label_path is None:
        raise ValueError(
            "Missing waste label path for "
            f"{sample['sample_id']}"
        )

    yolo_lines = []

    for line in label_path.read_text(
        encoding="utf-8"
    ).splitlines():

        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) != 5:
            raise ValueError(
                "Invalid YOLO annotation in "
                f"{label_path}: {line}"
            )

        _, x, y, width, height = (
            parts
        )

        yolo_lines.append(
            (
                "1 "
                f"{x} "
                f"{y} "
                f"{width} "
                f"{height}"
            )
        )

    return yolo_lines


def get_graffiti_yolo_annotations(
    sample: dict,
) -> list[str]:
    """
    Convert STORM bounding boxes
    to the final e-Patrol YOLO format.

    Graffiti is mapped to:

        2 = graffiti
    """
    annotations = (
        sample["annotations"]
    )

    if annotations is None:
        raise ValueError(
            "Missing STORM annotations for "
            f"{sample['sample_id']}"
        )

    with Image.open(
        sample["image_path"]
    ) as image:
        image_width, image_height = (
            image.size
        )

    yolo_lines = []

    for annotation in annotations:

        (
            x_center,
            y_center,
            width,
            height,
        ) = convert_bbox_to_yolo(
            xmin=annotation["xmin"],
            ymin=annotation["ymin"],
            xmax=annotation["xmax"],
            ymax=annotation["ymax"],
            image_width=image_width,
            image_height=image_height,
        )

        yolo_lines.append(
            (
                "2 "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{width:.6f} "
                f"{height:.6f}"
            )
        )

    return yolo_lines


def test_final_annotation_conversion(
    samples: list[dict],
) -> None:
    """
    Test annotation conversion on one sample
    from each final e-Patrol class.
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "FINAL YOLO ANNOTATION TEST"
    )
    print(
        "=" * 45
    )

    converters = {
        "road_damage": (
            get_road_yolo_annotations
        ),
        "waste": (
            get_waste_yolo_annotations
        ),
        "graffiti": (
            get_graffiti_yolo_annotations
        ),
    }

    for class_name, converter in (
        converters.items()
    ):
        sample = next(
            sample
            for sample in samples
            if sample["epatrol_class"]
            == class_name
        )

        annotations = converter(
            sample
        )

        print(
            f"\n{class_name}"
        )
        print(
            "-" * 35
        )

        print(
            "Image: "
            f"{sample['original_filename']}"
        )

        print(
            "Bounding boxes: "
            f"{len(annotations)}"
        )

        for line in annotations[:5]:
            print(
                f"  {line}"
            )


def export_final_yolo_dataset(
    samples: list[dict],
) -> None:
    """
    Export the complete e-Patrol dataset
    in YOLO format.

    Final classes:
        0 = road_damage
        1 = waste
        2 = graffiti
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "EXPORTING FINAL YOLO DATASET"
    )
    print(
        "=" * 45
    )

    converters = {
        "road_damage": get_road_yolo_annotations,
        "waste": get_waste_yolo_annotations,
        "graffiti": get_graffiti_yolo_annotations,
    }

    # --------------------------------------------------------
    # Prepare directory structure
    # --------------------------------------------------------

    if FINAL_DATASET_DIR.exists():
        print(
            "Removing previous exported dataset..."
        )

        shutil.rmtree(
            FINAL_DATASET_DIR
        )

    for split_name in [
        "train",
        "val",
        "test",
    ]:
        (
            FINAL_DATASET_DIR
            / "images"
            / split_name
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            FINAL_DATASET_DIR
            / "labels"
            / split_name
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------------
    # Export samples
    # --------------------------------------------------------

    exported_counts = Counter()
    box_counts = Counter()

    for sample in samples:
        split_name = (
            sample["final_split"]
        )

        epatrol_class = (
            sample["epatrol_class"]
        )

        converter = converters[
            epatrol_class
        ]

        yolo_lines = converter(
            sample
        )

        # Prefixing prevents filename collisions
        # between different source datasets.
        export_stem = (
            sample["sample_id"]
            .replace("::", "__")
        )

        # sample_id already contains the original
        # extension, so remove it before adding
        # the final image suffix.
        export_stem = Path(
            export_stem
        ).stem

        source_image = (
            sample["image_path"]
        )

        image_suffix = (
            source_image.suffix.lower()
        )

        target_image = (
            FINAL_DATASET_DIR
            / "images"
            / split_name
            / f"{export_stem}{image_suffix}"
        )

        target_label = (
            FINAL_DATASET_DIR
            / "labels"
            / split_name
            / f"{export_stem}.txt"
        )

        shutil.copy2(
            source_image,
            target_image,
        )

        target_label.write_text(
            "\n".join(
                yolo_lines
            )
            + "\n",
            encoding="utf-8",
        )

        exported_counts[
            split_name
        ] += 1

        box_counts[
            epatrol_class
        ] += len(
            yolo_lines
        )

    # --------------------------------------------------------
    # data.yaml
    # --------------------------------------------------------

    yaml_path = (
        FINAL_DATASET_DIR
        / "data.yaml"
    )

    yaml_content = """path: .
train: images/train
val: images/val
test: images/test

names:
  0: road_damage
  1: waste
  2: graffiti
"""

    yaml_path.write_text(
        yaml_content,
        encoding="utf-8",
    )

    print(
        "\nExported images:"
    )

    for split_name in [
        "train",
        "val",
        "test",
    ]:
        print(
            f"  {split_name}: "
            f"{exported_counts[split_name]}"
        )

    print(
        "\nBounding boxes:"
    )

    for class_name in [
        "road_damage",
        "waste",
        "graffiti",
    ]:
        print(
            f"  {class_name}: "
            f"{box_counts[class_name]}"
        )

    print(
        "\nDataset exported to: "
        f"{FINAL_DATASET_DIR}"
    )

    print(
        "YOLO config: "
        f"{yaml_path}"
    )


def validate_exported_yolo_dataset() -> None:
    """
    Validate the exported YOLO dataset.

    Checks:
    - image/label counts match,
    - every image has a label,
    - every label has an image,
    - every annotation has five values,
    - class IDs are valid,
    - normalized bbox values are within 0..1.
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "VALIDATING EXPORTED YOLO DATASET"
    )
    print(
        "=" * 45
    )

    valid_class_ids = {
        0,
        1,
        2,
    }

    total_images = 0
    total_labels = 0
    total_boxes = 0

    for split_name in [
        "train",
        "val",
        "test",
    ]:
        images_dir = (
            FINAL_DATASET_DIR
            / "images"
            / split_name
        )

        labels_dir = (
            FINAL_DATASET_DIR
            / "labels"
            / split_name
        )

        image_files = [
            path
            for path in images_dir.iterdir()
            if path.is_file()
        ]

        label_files = list(
            labels_dir.glob(
                "*.txt"
            )
        )

        image_stems = {
            path.stem
            for path in image_files
        }

        label_stems = {
            path.stem
            for path in label_files
        }

        missing_labels = (
            image_stems
            - label_stems
        )

        missing_images = (
            label_stems
            - image_stems
        )

        if missing_labels:
            raise ValueError(
                f"{split_name}: "
                f"{len(missing_labels)} "
                "images have no label."
            )

        if missing_images:
            raise ValueError(
                f"{split_name}: "
                f"{len(missing_images)} "
                "labels have no image."
            )

        split_boxes = 0

        for label_path in label_files:
            lines = (
                label_path
                .read_text(
                    encoding="utf-8"
                )
                .splitlines()
            )

            for line_number, line in enumerate(
                lines,
                start=1,
            ):
                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) != 5:
                    raise ValueError(
                        "Invalid YOLO row: "
                        f"{label_path}, "
                        f"line {line_number}"
                    )

                class_id = int(
                    parts[0]
                )

                coordinates = [
                    float(value)
                    for value in parts[1:]
                ]

                if class_id not in valid_class_ids:
                    raise ValueError(
                        "Invalid class ID "
                        f"{class_id} in "
                        f"{label_path}"
                    )

                if not all(
                    0.0 <= value <= 1.0
                    for value in coordinates
                ):
                    raise ValueError(
                        "BBox outside 0..1 in "
                        f"{label_path}, "
                        f"line {line_number}: "
                        f"{coordinates}"
                    )

                if (
                    coordinates[2] <= 0
                    or coordinates[3] <= 0
                ):
                    raise ValueError(
                        "Invalid bbox size in "
                        f"{label_path}, "
                        f"line {line_number}"
                    )

                split_boxes += 1

        total_images += len(
            image_files
        )

        total_labels += len(
            label_files
        )

        total_boxes += (
            split_boxes
        )

        print(
            f"\n{split_name}"
        )
        print(
            f"  images: {len(image_files)}"
        )
        print(
            f"  labels: {len(label_files)}"
        )
        print(
            f"  boxes:  {split_boxes}"
        )

    print(
        "\nTOTAL"
    )
    print(
        f"  images: {total_images}"
    )
    print(
        f"  labels: {total_labels}"
    )
    print(
        f"  boxes:  {total_boxes}"
    )

    if total_images != 3022:
        raise ValueError(
            "Expected 3022 images, "
            f"found {total_images}."
        )

    print(
        "\nYOLO DATASET VALIDATION: OK"
    )


def draw_yolo_annotations(
    image_path: Path,
    label_path: Path,
) -> Image.Image:
    """
    Draw final YOLO bounding boxes on an image.

    This reads the exported annotation, so the preview
    verifies the final dataset rather than source labels.
    """
    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    draw = ImageDraw.Draw(
        image
    )

    image_width, image_height = (
        image.size
    )

    class_names = {
        0: "road_damage",
        1: "waste",
        2: "graffiti",
    }

    lines = label_path.read_text(
        encoding="utf-8"
    ).splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        class_id = int(
            parts[0]
        )

        x_center = float(
            parts[1]
        )

        y_center = float(
            parts[2]
        )

        box_width = float(
            parts[3]
        )

        box_height = float(
            parts[4]
        )

        # YOLO normalized coordinates -> pixels.
        x_center *= image_width
        y_center *= image_height
        box_width *= image_width
        box_height *= image_height

        xmin = (
            x_center
            - box_width / 2
        )

        ymin = (
            y_center
            - box_height / 2
        )

        xmax = (
            x_center
            + box_width / 2
        )

        ymax = (
            y_center
            + box_height / 2
        )

        draw.rectangle(
            [
                xmin,
                ymin,
                xmax,
                ymax,
            ],
            outline="red",
            width=4,
        )

        draw.text(
            (
                xmin + 4,
                ymin + 4,
            ),
            class_names[
                class_id
            ],
            fill="red",
        )

    return image


def create_final_class_audit_sheet(
    samples: list[dict],
    class_name: str,
    sample_count: int,
    seed: int,
) -> Path:
    """
    Create a contact sheet from the FINAL exported
    dataset with final YOLO annotations drawn on it.
    """
    class_samples = [
        sample
        for sample in samples
        if sample["epatrol_class"]
        == class_name
    ]

    rng = random.Random(
        seed
    )

    selected = rng.sample(
        class_samples,
        min(
            sample_count,
            len(class_samples),
        ),
    )

    thumb_width = 300
    thumb_height = 220
    label_height = 45
    columns = 4

    rows = (
        len(selected)
        + columns
        - 1
    ) // columns

    sheet = Image.new(
        "RGB",
        (
            columns * thumb_width,
            rows
            * (
                thumb_height
                + label_height
            ),
        ),
        "white",
    )

    draw = ImageDraw.Draw(
        sheet
    )

    for index, sample in enumerate(
        selected
    ):
        split_name = (
            sample["final_split"]
        )

        export_stem = Path(
            sample["sample_id"]
            .replace("::", "__")
        ).stem

        source_suffix = (
            sample["image_path"]
            .suffix
            .lower()
        )

        image_path = (
            FINAL_DATASET_DIR
            / "images"
            / split_name
            / f"{export_stem}{source_suffix}"
        )

        label_path = (
            FINAL_DATASET_DIR
            / "labels"
            / split_name
            / f"{export_stem}.txt"
        )

        annotated_image = (
            draw_yolo_annotations(
                image_path,
                label_path,
            )
        )

        annotated_image.thumbnail(
            (
                thumb_width,
                thumb_height,
            )
        )

        row = (
            index // columns
        )

        column = (
            index % columns
        )

        x = (
            column * thumb_width
        )

        y = (
            row
            * (
                thumb_height
                + label_height
            )
        )

        sheet.paste(
            annotated_image,
            (x, y),
        )

        draw.text(
            (
                x + 4,
                y + thumb_height + 4,
            ),
            (
                f"{split_name} | "
                f"{sample['original_filename'][:28]}"
            ),
            fill="black",
        )

    FINAL_VISUAL_AUDIT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        FINAL_VISUAL_AUDIT_DIR
        / f"{class_name}_final_annotations.jpg"
    )

    sheet.save(
        output_path,
        quality=90,
    )

    return output_path


def create_final_visual_audit(
    samples: list[dict],
) -> None:
    """
    Create visual sanity-check sheets for all
    final e-Patrol classes.
    """
    print(
        "\n"
        + "=" * 45
    )
    print(
        "FINAL DATASET — VISUAL ANNOTATION AUDIT"
    )
    print(
        "=" * 45
    )

    for index, class_name in enumerate(
        [
            "road_damage",
            "waste",
            "graffiti",
        ]
    ):
        output_path = (
            create_final_class_audit_sheet(
                samples=samples,
                class_name=class_name,
                sample_count=(
                    FINAL_VISUAL_AUDIT_PER_CLASS
                ),
                seed=(
                    RANDOM_SEED
                    + index
                ),
            )
        )

        print(
            f"{class_name}: "
            f"{FINAL_VISUAL_AUDIT_PER_CLASS} images"
        )

        print(
            f"  {output_path}"
        )