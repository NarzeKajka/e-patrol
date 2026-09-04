from pathlib import Path
import random
import shutil
import xml.etree.ElementTree as ET


CLASS_MAP = {
    "D00": 0,
    "D10": 1,
    "D20": 2,
    "D40": 3,
}

SOURCE_IMAGE_DIR = Path(
    "/Users/narzekajka/Downloads/RDD2022/"
    "Czech/Czech/train/images"
)

SOURCE_XML_DIR = Path(
    "/Users/narzekajka/Downloads/RDD2022/"
    "Czech/Czech/train/annotations/xmls"
)

OUTPUT_ROOT = Path("data/rdd2022_czech")

TRAIN_RATIO = 0.8
RANDOM_SEED = 42


def convert_bbox(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    image_width: float,
    image_height: float,
):
    x_center = ((xmin + xmax) / 2) / image_width
    y_center = ((ymin + ymax) / 2) / image_height
    width = (xmax - xmin) / image_width
    height = (ymax - ymin) / image_height

    return x_center, y_center, width, height


def convert_xml(xml_path: Path) -> list[str]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    size = root.find("size")

    image_width = float(size.findtext("width"))
    image_height = float(size.findtext("height"))

    yolo_lines = []

    for obj in root.findall("object"):
        class_name = obj.findtext("name")

        if class_name not in CLASS_MAP:
            continue

        class_id = CLASS_MAP[class_name]

        bbox = obj.find("bndbox")

        xmin = float(bbox.findtext("xmin"))
        ymin = float(bbox.findtext("ymin"))
        xmax = float(bbox.findtext("xmax"))
        ymax = float(bbox.findtext("ymax"))

        x_center, y_center, width, height = convert_bbox(
            xmin,
            ymin,
            xmax,
            ymax,
            image_width,
            image_height,
        )

        yolo_lines.append(
            f"{class_id} "
            f"{x_center:.6f} "
            f"{y_center:.6f} "
            f"{width:.6f} "
            f"{height:.6f}"
        )

    return yolo_lines


def prepare_directories():
    for split in ["train", "val"]:
        (OUTPUT_ROOT / "images" / split).mkdir(
            parents=True,
            exist_ok=True,
        )

        (OUTPUT_ROOT / "labels" / split).mkdir(
            parents=True,
            exist_ok=True,
        )


def save_sample(xml_path: Path, split: str):
    labels = convert_xml(xml_path)

    image_path = SOURCE_IMAGE_DIR / f"{xml_path.stem}.jpg"

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found for {xml_path.name}: {image_path}"
        )

    destination_image = (
        OUTPUT_ROOT / "images" / split / image_path.name
    )

    destination_label = (
        OUTPUT_ROOT / "labels" / split / f"{xml_path.stem}.txt"
    )

    shutil.copy2(
        image_path,
        destination_image,
    )

    destination_label.write_text(
        "\n".join(labels),
        encoding="utf-8",
    )

    return len(labels)


def main():
    prepare_directories()

    xml_files = sorted(SOURCE_XML_DIR.glob("*.xml"))

    print(f"Found {len(xml_files)} samples")

    random.seed(RANDOM_SEED)
    random.shuffle(xml_files)

    split_index = int(len(xml_files) * TRAIN_RATIO)

    train_files = xml_files[:split_index]
    val_files = xml_files[split_index:]

    train_objects = 0
    val_objects = 0

    for xml_path in train_files:
        train_objects += save_sample(
            xml_path,
            "train",
        )

    for xml_path in val_files:
        val_objects += save_sample(
            xml_path,
            "val",
        )

    print()
    print("Dataset prepared")
    print(f"Train images: {len(train_files)}")
    print(f"Validation images: {len(val_files)}")
    print(f"Train objects: {train_objects}")
    print(f"Validation objects: {val_objects}")
    print(f"Total objects: {train_objects + val_objects}")


if __name__ == "__main__":
    main()