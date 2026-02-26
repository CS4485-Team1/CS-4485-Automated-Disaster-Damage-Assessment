"""Batch dataset runner using normalized preprocessing pairs."""

from app.services.preprocessing_adapter import load_normalized_pairs_with_issues
from app.vlm.service import extract_critical_regions_from_labels


def run_dataset(image_root: str = "data/santa_rosa/images") -> None:
    valid_pairs, invalid_pairs = load_normalized_pairs_with_issues(image_root=image_root)

    print(f"Loaded pairs: valid={len(valid_pairs)} invalid={len(invalid_pairs)}")

    if invalid_pairs:
        first = invalid_pairs[0]
        print(f"Example invalid pair issues: {first['issues']}")

    if not valid_pairs:
        return

    first_pair = valid_pairs[0]
    regions = extract_critical_regions_from_labels(first_pair.get("labels_xy", []))

    print(
        "Sample pair "
        f"id={first_pair.get('id')} city={first_pair.get('city')} "
        f"regions_extracted={len(regions)}"
    )


if __name__ == "__main__":
    run_dataset()
