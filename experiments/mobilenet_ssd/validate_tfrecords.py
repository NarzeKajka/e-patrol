from pathlib import Path

import tensorflow as tf


TFOD_DIR = Path("data/tfod")

CLASS_NAMES = {
    1: "road_damage",
    2: "waste",
    3: "graffiti",
}

EXPECTED = {
    "train": {
        "images": 2115,
        "boxes": 4552,
        "classes": {
            1: 1890,
            2: 991,
            3: 1671,
        },
    },
    "val": {
        "images": 453,
        "boxes": 852,
        "classes": {
            1: 357,
            2: 201,
            3: 294,
        },
    },
    "test": {
        "images": 454,
        "boxes": 992,
        "classes": {
            1: 390,
            2: 228,
            3: 374,
        },
    },
}


def validate_split(split):
    record_path = TFOD_DIR / f"{split}.record"

    image_count = 0
    box_count = 0
    class_counts = {
        1: 0,
        2: 0,
        3: 0,
    }

    dataset = tf.data.TFRecordDataset(
        str(record_path)
    )

    for raw_record in dataset:
        example = tf.train.Example()
        example.ParseFromString(
            raw_record.numpy()
        )

        labels = example.features.feature[
            "image/object/class/label"
        ].int64_list.value

        image_count += 1
        box_count += len(labels)

        for class_id in labels:
            class_counts[class_id] += 1

    print(f"\n{split.upper()}")
    print(f"images: {image_count}")
    print(f"boxes: {box_count}")

    for class_id, class_name in CLASS_NAMES.items():
        print(
            f"{class_id} {class_name}: "
            f"{class_counts[class_id]}"
        )

    expected = EXPECTED[split]

    assert image_count == expected["images"]
    assert box_count == expected["boxes"]

    for class_id in CLASS_NAMES:
        assert (
            class_counts[class_id]
            == expected["classes"][class_id]
        )

    return (
        image_count,
        box_count,
        class_counts,
    )


def main():
    total_images = 0
    total_boxes = 0

    total_classes = {
        1: 0,
        2: 0,
        3: 0,
    }

    for split in ["train", "val", "test"]:
        (
            image_count,
            box_count,
            class_counts,
        ) = validate_split(split)

        total_images += image_count
        total_boxes += box_count

        for class_id in CLASS_NAMES:
            total_classes[class_id] += (
                class_counts[class_id]
            )

    print("\nTOTAL")
    print(f"images: {total_images}")
    print(f"boxes: {total_boxes}")

    for class_id, class_name in CLASS_NAMES.items():
        print(
            f"{class_id} {class_name}: "
            f"{total_classes[class_id]}"
        )

    assert total_images == 3022
    assert total_boxes == 6396

    assert total_classes[1] == 2637
    assert total_classes[2] == 1420
    assert total_classes[3] == 2339

    print("\nTFRecord validation: OK")


if __name__ == "__main__":
    main()