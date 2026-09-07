from pathlib import Path
import argparse


NUM_CLASSES = 3
BATCH_SIZE = 16
NUM_STEPS = 13_300

LEARNING_RATE = 0.01
WARMUP_LEARNING_RATE = 0.003333
WARMUP_STEPS = 266


def configure_pipeline(
    source_config: Path,
    output_config: Path,
    checkpoint_path: str,
    tfod_dir: Path,
):
    config = source_config.read_text()

    replacements = {
        "num_classes: 90": f"num_classes: {NUM_CLASSES}",
        "batch_size: 128": f"batch_size: {BATCH_SIZE}",
        "num_steps: 50000": f"num_steps: {NUM_STEPS}",
        'fine_tune_checkpoint: "PATH_TO_BE_CONFIGURED"':
            f'fine_tune_checkpoint: "{checkpoint_path}"',
        'label_map_path: "PATH_TO_BE_CONFIGURED/label_map.txt"':
            f'label_map_path: "{tfod_dir / "label_map.pbtxt"}"',
        'input_path: "PATH_TO_BE_CONFIGURED/train2017-?????-of-00256.tfrecord"':
            f'input_path: "{tfod_dir / "train.record"}"',
        'input_path: "PATH_TO_BE_CONFIGURED/val2017-?????-of-00032.tfrecord"':
            f'input_path: "{tfod_dir / "val.record"}"',
    }

    for old, new in replacements.items():
        if old not in config:
            raise ValueError(
                f"Expected setting not found:\n{old}"
            )

        config = config.replace(old, new)

    config = config.replace(
        "initial_learning_rate: 0.08",
        f"initial_learning_rate: {LEARNING_RATE}",
    )

    config = config.replace(
        "warmup_learning_rate: 0.026666",
        f"warmup_learning_rate: {WARMUP_LEARNING_RATE}",
    )

    config = config.replace(
        "warmup_steps: 1000",
        f"warmup_steps: {WARMUP_STEPS}",
    )

    config = config.replace(
        "total_steps: 50000",
        f"total_steps: {NUM_STEPS}",
    )

    output_config.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_config.write_text(config)

    print(f"Saved: {output_config}")
    print(f"num_classes: {NUM_CLASSES}")
    print(f"batch_size: {BATCH_SIZE}")
    print(f"num_steps: {NUM_STEPS}")
    print(f"learning_rate: {LEARNING_RATE}")
    print(f"warmup_steps: {WARMUP_STEPS}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--checkpoint",
        required=True,
    )

    parser.add_argument(
        "--tfod-dir",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    configure_pipeline(
        source_config=args.source,
        output_config=args.output,
        checkpoint_path=args.checkpoint,
        tfod_dir=args.tfod_dir,
    )


if __name__ == "__main__":
    main()