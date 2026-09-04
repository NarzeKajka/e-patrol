from dataset.config import OUTPUT_DIR

from dataset.road_damage import (
    prepare_road_damage_candidates,
)

from dataset.waste import (
    prepare_waste_candidates,
)

from dataset.graffiti import (
    prepare_storm_candidates,
)

from dataset.audit import (
    prepare_cross_class_audit,
)

from dataset.split import (
    create_final_samples,
    load_similarity_groups,
    print_final_group_stats,
    assign_final_splits,
    validate_final_split,
    print_final_split_stats,
    save_final_manifest,
)

from dataset.export_yolo import (
    test_final_annotation_conversion,
    export_final_yolo_dataset,
    validate_exported_yolo_dataset,
    create_final_visual_audit,
)


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    road_samples = (
        prepare_road_damage_candidates()
    )

    waste_samples = (
        prepare_waste_candidates()
    )

    graffiti_samples = (
        prepare_storm_candidates()
    )

    prepare_cross_class_audit(
        road_samples=road_samples,
        waste_samples=waste_samples,
        graffiti_samples=graffiti_samples,
    )

    final_samples = create_final_samples(
        road_samples=road_samples,
        waste_samples=waste_samples,
        graffiti_samples=graffiti_samples,
    )

    load_similarity_groups(
        final_samples,
        OUTPUT_DIR
        / "waste_similar_pairs.csv",
    )

    print_final_group_stats(
        final_samples
    )

    assign_final_splits(
        final_samples
    )

    validate_final_split(
        final_samples
    )

    print_final_split_stats(
        final_samples
    )

    save_final_manifest(
        final_samples
    )

    test_final_annotation_conversion(
        final_samples
    )

    export_final_yolo_dataset(
        final_samples
    )

    validate_exported_yolo_dataset()

    create_final_visual_audit(
        final_samples
    )


if __name__ == "__main__":
    main()