from pathlib import Path


# ============================================================
# GENERAL
# ============================================================

RANDOM_SEED = 42

OUTPUT_DIR = Path(
    "data/epatrol_preparation"
)


# ============================================================
# CROSS-CLASS VISUAL AUDIT
# ============================================================

CROSS_CLASS_AUDIT_SAMPLE_COUNT = 24

CROSS_CLASS_AUDIT_DIR = (
    OUTPUT_DIR
    / "cross_class_audit"
)


# ============================================================
# FINAL E-PATROL DATASET
# ============================================================

FINAL_SPLIT_SEED = 42

FINAL_TRAIN_RATIO = 0.70
FINAL_VAL_RATIO = 0.15
FINAL_TEST_RATIO = 0.15

FINAL_MANIFEST_PATH = (
    OUTPUT_DIR
    / "final_dataset_manifest.csv"
)

FINAL_DATASET_DIR = Path(
    "data/epatrol_dataset"
)

FINAL_CLASS_IDS = {
    "road_damage": 0,
    "waste": 1,
    "graffiti": 2,
}

FINAL_VISUAL_AUDIT_DIR = (
    OUTPUT_DIR
    / "final_visual_audit"
)

FINAL_VISUAL_AUDIT_PER_CLASS = 12


# ============================================================
# ROAD DAMAGE — RDD2022
# ============================================================

RDD_CLASSES = {
    "D00",
    "D10",
    "D20",
    "D40",
}

ROAD_SAMPLES_PER_COUNTRY = 500
ROAD_PHASH_MAX_DISTANCE = 4

ROAD_DATASETS = {
    "czech": {
        "images": (
            Path.home()
            / "Downloads"
            / "RDD2022"
            / "Czech"
            / "Czech"
            / "train"
            / "images"
        ),
        "annotations": (
            Path.home()
            / "Downloads"
            / "RDD2022"
            / "Czech"
            / "Czech"
            / "train"
            / "annotations"
            / "xmls"
        ),
    },
    "norway": {
        "images": (
            Path.home()
            / "Downloads"
            / "RDD2022"
            / "Norway"
            / "Norway"
            / "train"
            / "images"
        ),
        "annotations": (
            Path.home()
            / "Downloads"
            / "RDD2022"
            / "Norway"
            / "Norway"
            / "train"
            / "annotations"
            / "xmls"
        ),
    },
}

ROAD_MANIFEST_PATH = (
    OUTPUT_DIR
    / "road_damage_candidates.csv"
)


# ============================================================
# WASTE — ILLEGAL DUMPING
# ============================================================

WASTE_DATASET = Path(
    "data/source/illegal_dumping"
)

WASTE_TARGET_COUNT = 1000
WASTE_PHASH_MAX_DISTANCE = 4

WASTE_SPLITS = [
    "train",
    "valid",
    "test",
]

WASTE_CLASSES = {
    0: "dump",
    1: "furniture",
    2: "mattress",
    3: "pallet",
    4: "rubbish",
    5: "trolley",
    6: "tyre",
}

WASTE_MANIFEST_PATH = (
    OUTPUT_DIR
    / "waste_candidates.csv"
)


# ============================================================
# GRAFFITI — STORM
# ============================================================

STORM_DATASET = Path(
    "data/source/storm"
)

STORM_IMAGES_DIR = (
    STORM_DATASET
    / "images"
)

STORM_ANNOTATIONS_DIR = (
    STORM_DATASET
    / "Bounding_boxes"
)

STORM_SPLITS = [
    "train",
    "test",
]

STORM_PHASH_MAX_DISTANCE = 4

STORM_MANIFEST_PATH = (
    OUTPUT_DIR
    / "graffiti_candidates.csv"
)