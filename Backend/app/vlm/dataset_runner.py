import json
import os
import time

from app.services.preprocessing_adapter import load_normalized_pairs_with_issues
from app.vlm.service import assess_damage_with_retry

RESULTS_PATH = os.path.join("data", "santa_rosa", "results.json")


def load_existing_results(results_path):
    if not os.path.exists(results_path):
        return []

    try:
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: invalid JSON in {results_path}")
        return []

    if isinstance(data, list):
        return data

    return []


def save_results(results_path, results):
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    temp_path = f"{results_path}.tmp"

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    for _ in range(3):
        try:
            os.replace(temp_path, results_path)
            return
        except PermissionError:
            time.sleep(0.2)

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    if os.path.exists(temp_path):
        os.remove(temp_path)


def get_label_path_from_post_image(post_image_path):
    images_dir = os.path.dirname(post_image_path)
    data_dir = os.path.dirname(images_dir)
    labels_dir = os.path.join(data_dir, "labels")
    label_name = os.path.basename(post_image_path).replace(".png", ".json")
    return os.path.join(labels_dir, label_name)


def run_dataset(image_root="data/santa_rosa/images", results_path=RESULTS_PATH):
    valid_pairs, invalid_pairs = load_normalized_pairs_with_issues(image_root=image_root)

    results = load_existing_results(results_path)
    processed_ids = set()
    for item in results:
        if isinstance(item, dict) and item.get("id"):
            processed_ids.add(item.get("id"))

    skipped_done = 0
    skipped_missing_label = 0
    failed = 0
    completed_new = 0

    for pair in valid_pairs:
        pair_id = pair.get("id")
        if not pair_id:
            continue

        if pair_id in processed_ids:
            skipped_done += 1
            continue

        pre_image_path = pair.get("pre_image_path")
        post_image_path = pair.get("post_image_path")

        if not isinstance(pre_image_path, str) or not isinstance(post_image_path, str):
            failed += 1
            continue

        label_path = get_label_path_from_post_image(post_image_path)
        if not os.path.exists(label_path):
            skipped_missing_label += 1
            results.append({
                "id": pair_id,
                "city": pair.get("city"),
                "status": "skipped_missing_label",
                "pre_image_path": pre_image_path,
                "post_image_path": post_image_path,
                "label_path": label_path,
            })
            processed_ids.add(pair_id)
            save_results(results_path, results)
            continue

        try:
            prediction = assess_damage_with_retry(pre_image_path, post_image_path, label_path)
            results.append({
                "id": pair_id,
                "city": pair.get("city"),
                "status": "ok",
                "pre_image_path": pre_image_path,
                "post_image_path": post_image_path,
                "label_path": label_path,
                **prediction,
            })
            completed_new += 1
        except Exception as error:
            failed += 1
            results.append({
                "id": pair_id,
                "city": pair.get("city"),
                "status": "failed",
                "error": str(error),
                "pre_image_path": pre_image_path,
                "post_image_path": post_image_path,
                "label_path": label_path,
            })

        processed_ids.add(pair_id)
        save_results(results_path, results)

    for item in invalid_pairs:
        pair = item.get("pair", {})
        pair_id = pair.get("id")

        if pair_id and pair_id in processed_ids:
            continue

        results.append({
            "id": pair_id,
            "status": "invalid_pair",
            "issues": item.get("issues", []),
            "pair": pair,
        })

        if pair_id:
            processed_ids.add(pair_id)

        save_results(results_path, results)

    print(
        "Done "
        f"new_ok={completed_new} "
        f"already_done={skipped_done} "
        f"missing_label={skipped_missing_label} "
        f"failed={failed} "
        f"invalid_pairs={len(invalid_pairs)}"
    )
    print(f"Saved: {results_path}")


if __name__ == "__main__":
    run_dataset()
