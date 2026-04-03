import json
import sys
from collections import Counter
from pathlib import Path

from adapter import normalize_building_pairs
from preprocessing import get_pairs
from service import call_vlm_with_retry


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_evaluation_summary(results):
    total = len(results)
    matched = 0
    ground_truth_counts = Counter()
    prediction_counts = Counter()
    confusion_counts = Counter()
    mismatches = []

    for item in results:
        ground_truth = item.get("ground_truth")
        prediction = item.get("model", {}).get("damage_level")
        match = item.get("match")

        if match is True:
            matched += 1

        if ground_truth:
            ground_truth_counts[ground_truth] += 1
        if prediction:
            prediction_counts[prediction] += 1
        if ground_truth and prediction:
            confusion_counts[f"{ground_truth} -> {prediction}"] += 1

        if match is False:
            mismatches.append({
                "id": item.get("id"),
                "ground_truth": ground_truth,
                "prediction": prediction,
                "confidence": item.get("model", {}).get("confidence"),
                "reasoning": item.get("model", {}).get("reasoning"),
            })

    accuracy = 0.0
    if total:
        accuracy = matched / total

    return {
        "total": total,
        "matched": matched,
        "accuracy": round(accuracy, 4),
        "ground_truth_counts": dict(ground_truth_counts),
        "prediction_counts": dict(prediction_counts),
        "confusion_counts": dict(confusion_counts),
        "mismatches": mismatches,
    }


def build_evaluation_records(results):
    evaluation = []

    for item in results:
        model = item.get("model", {})
        evaluation.append({
            "id": item.get("id"),
            "city": item.get("city"),
            "ground_truth": item.get("ground_truth"),
            "prediction": model.get("damage_level"),
            "match": item.get("match"),
            "confidence": model.get("confidence"),
            "reasoning": model.get("reasoning"),
        })

    return evaluation


def run_preprocessing(image_dir, output_dir, scene_id=None):
    crop_dir = Path(output_dir) / "building_crops"
    results_name = "building_pairs.json"
    if scene_id:
        results_name = f"{scene_id}_building_pairs.json"
    results_path = Path(output_dir) / results_name
    crop_dir.mkdir(parents=True, exist_ok=True)

    raw_pairs = get_pairs(image_dir, str(crop_dir), scene_id=scene_id)
    normalized = normalize_building_pairs(raw_pairs)

    save_json(results_path, normalized)

    print(f"building_pairs={len(normalized)}")
    print(f"results={results_path}")
    return normalized


def run_vlm_demo(output_dir, limit=10, scene_id=None):
    pairs_name = "building_pairs.json"
    results_name = "vlm_results.json"
    evaluation_name = "vlm_evaluation.json"
    summary_name = "vlm_summary.json"
    if scene_id:
        pairs_name = f"{scene_id}_building_pairs.json"
        results_name = f"{scene_id}_vlm_results.json"
        evaluation_name = f"{scene_id}_vlm_evaluation.json"
        summary_name = f"{scene_id}_vlm_summary.json"

    pairs_path = Path(output_dir) / pairs_name
    results_path = Path(output_dir) / results_name
    evaluation_path = Path(output_dir) / evaluation_name
    summary_path = Path(output_dir) / summary_name

    with open(pairs_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    selected = pairs[:limit]
    results = []

    for item in selected:
        result = call_vlm_with_retry(item["pre_image_path"], item["post_image_path"])
        ground_truth = item.get("ground_truth")
        prediction = result.get("damage_level")
        results.append({
            "id": item["id"],
            "city": item["city"],
            "pre_image_path": item["pre_image_path"],
            "post_image_path": item["post_image_path"],
            "ground_truth": ground_truth,
            "match": prediction == ground_truth if ground_truth is not None else None,
            "model": result,
        })

    save_json(results_path, results)
    evaluation = build_evaluation_records(results)
    save_json(evaluation_path, evaluation)
    summary = build_evaluation_summary(results)
    save_json(summary_path, summary)

    print(f"vlm_pairs_run={len(results)}")
    print(f"vlm_results={results_path}")
    print(f"vlm_evaluation={evaluation_path}")
    print(f"accuracy={summary['matched']}/{summary['total']}")
    print(f"vlm_summary={summary_path}")


def summarize_results(output_dir, scene_id=None):
    results_name = "vlm_results.json"
    evaluation_name = "vlm_evaluation.json"
    summary_name = "vlm_summary.json"
    if scene_id:
        results_name = f"{scene_id}_vlm_results.json"
        evaluation_name = f"{scene_id}_vlm_evaluation.json"
        summary_name = f"{scene_id}_vlm_summary.json"

    results_path = Path(output_dir) / results_name
    evaluation_path = Path(output_dir) / evaluation_name
    summary_path = Path(output_dir) / summary_name

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    evaluation = build_evaluation_records(results)
    save_json(evaluation_path, evaluation)
    summary = build_evaluation_summary(results)
    save_json(summary_path, summary)

    print(f"vlm_evaluation={evaluation_path}")
    print(f"accuracy={summary['matched']}/{summary['total']}")
    print(f"vlm_summary={summary_path}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    image_dir = root / "Backend" / "data" / "santa_rosa" / "images"
    output_dir = root / "Demo" / "output"

    if len(sys.argv) > 1 and sys.argv[1] == "vlm":
        limit = 10
        if len(sys.argv) > 2:
            limit = int(sys.argv[2])
        run_vlm_demo(str(output_dir), limit=limit)
    elif len(sys.argv) > 2 and sys.argv[1] == "summary":
        summarize_results(str(output_dir), scene_id=sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "scene-vlm":
        limit = 10
        if len(sys.argv) > 3:
            limit = int(sys.argv[3])
        run_vlm_demo(str(output_dir), limit=limit, scene_id=sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "scene":
        run_preprocessing(str(image_dir), str(output_dir), scene_id=sys.argv[2])
    else:
        run_preprocessing(str(image_dir), str(output_dir))
