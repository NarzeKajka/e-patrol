import random


def select_samples(
    samples: list[dict],
    target_count: int,
    seed: int,
) -> list[dict]:
    """
    Select a deterministic random sample.

    Using a fixed seed makes the selection reproducible.
    """
    if target_count > len(samples):
        raise ValueError(
            f"Requested {target_count} samples, "
            f"but only {len(samples)} are available."
        )

    rng = random.Random(seed)

    return rng.sample(
        samples,
        target_count,
    )