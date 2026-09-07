from pathlib import Path

import tensorflow as tf
from PIL import Image


DATASET_DIR = Path("data/epatrol_dataset")
OUTPUT_DIR = Path("data/tfod")

CLASSES = {
    0: (1, "road_damage"),
    1: (2, "waste"),
    2: (3, "graffiti"),
}


def feature_bytes(value):
    return tf.train.Feature(
        bytes_list=tf.train.BytesList(value=[value])
    )


def feature_bytes_list(values):
    return tf.train.Feature(
        bytes_list=tf.train.BytesList(value=values)
    )


def feature_int(value):
    return tf.train.Feature(
        int64_list=tf.train.Int64List(value=[value])
    )


def feature_int_list(values):
    return tf.train.Feature(
        int64_list=tf.train.Int64List(value=values)
    )


def feature_float_list(values):
    return tf.train.Feature(
        float_list=tf.train.FloatList(value=values)
    )


def create_example(image_path, label_path):
    image_bytes = image_path.read_bytes()

    with Image.open(image_path) as image:
        width, height = image.size
        image_format = image.format.lower()

    if image_format == "jpg":
        image_format = "jpeg"

    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    class_names = []
    class_ids = []

    for line in label_path.read_text().splitlines():
        class_id, xc, yc, w, h = map(float, line.split())
        class_id = int(class_id)

        tf_id, class_name = CLASSES[class_id]

        xmins.append(max(0, xc - w / 2))
        xmaxs.append(min(1, xc + w / 2))
        ymins.append(max(0, yc - h / 2))
        ymaxs.append(min(1, yc + h / 2))

        class_names.append(class_name.encode())
        class_ids.append(tf_id)

    features = {
        "image/height": feature_int(height),
        "image/width": feature_int(width),
        "image/filename": feature_bytes(image_path.name.encode()),
        "image/source_id": feature_bytes(image_path.name.encode()),
        "image/encoded": feature_bytes(image_bytes),
        "image/format": feature_bytes(image_format.encode()),
        "image/object/bbox/xmin": feature_float_list(xmins),
        "image/object/bbox/xmax": feature_float_list(xmaxs),
        "image/object/bbox/ymin": feature_float_list(ymins),
        "image/object/bbox/ymax": feature_float_list(ymaxs),
        "image/object/class/text": feature_bytes_list(class_names),
        "image/object/class/label": feature_int_list(class_ids),
    }

    return tf.train.Example(
        features=tf.train.Features(feature=features)
    )


def convert_split(split):
    images_dir = DATASET_DIR / "images" / split
    labels_dir = DATASET_DIR / "labels" / split
    output_path = OUTPUT_DIR / f"{split}.record"

    images = sorted(
        list(images_dir.glob("*.jpg"))
        + list(images_dir.glob("*.jpeg"))
        + list(images_dir.glob("*.png"))
    )

    with tf.io.TFRecordWriter(str(output_path)) as writer:
        for image_path in images:
            label_path = labels_dir / f"{image_path.stem}.txt"

            example = create_example(
                image_path,
                label_path,
            )

            writer.write(
                example.SerializeToString()
            )

    print(f"{split}: {len(images)} images")


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    label_map = """
item {
  id: 1
  name: 'road_damage'
}

item {
  id: 2
  name: 'waste'
}

item {
  id: 3
  name: 'graffiti'
}
""".strip()

    (OUTPUT_DIR / "label_map.pbtxt").write_text(label_map)

    for split in ["train", "val", "test"]:
        convert_split(split)


if __name__ == "__main__":
    main()