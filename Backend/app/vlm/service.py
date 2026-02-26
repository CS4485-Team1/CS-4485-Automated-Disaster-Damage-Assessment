import os
import random
import time

from app.vlm.label_utils import compare_with_ground_truth, load_label

MAX_REGIONS_FOR_PROMPT = 40


def parse_xy_polygon_points(raw_coords):
    points = []
    if not isinstance(raw_coords, str):
        return points

    for pair in raw_coords.split(","):
        parts = pair.strip().split()
        if len(parts) < 2:
            continue
        try:
            x = float(parts[0])
            y = float(parts[1])
            points.append((x, y))
        except ValueError:
            continue

    return points


def extract_critical_regions_from_labels(labels_xy, max_regions=MAX_REGIONS_FOR_PROMPT):
    regions = []

    for i, raw_coords in enumerate(labels_xy):
        points = parse_xy_polygon_points(raw_coords)
        if not points:
            continue

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)

        width = max_x - min_x
        height = max_y - min_y
        area = max(0.0, width * height)

        regions.append({
            "id": f"region_{i + 1}",
            "bbox": [round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2)],
            "center": [round((min_x + max_x) / 2.0, 2), round((min_y + max_y) / 2.0, 2)],
            "bbox_area": round(area, 2),
        })

    regions.sort(key=lambda item: item["bbox_area"], reverse=True)
    return regions[:max_regions]


def extract_labels_xy_from_label_json(label_json):
    labels_xy = []
    features = label_json.get("features", {}).get("xy", [])

    for feature in features:
        wkt = feature.get("wkt")
        if isinstance(wkt, str):
            labels_xy.append(wkt.replace("POLYGON ((", "").replace("))", ""))

    return labels_xy


def normalize_region_predictions(model_result, valid_region_ids):
    raw_regions = model_result.get("critical_regions", [])
    if not isinstance(raw_regions, list):
        model_result["critical_regions"] = []
        model_result["critical_regions_unknown_ids"] = []
        return

    normalized = []
    unknown_ids = []

    for item in raw_regions:
        if not isinstance(item, dict):
            continue
        region_id = item.get("id")
        if not isinstance(region_id, str):
            continue

        if region_id in valid_region_ids:
            normalized.append(item)
        else:
            unknown_ids.append(region_id)

    model_result["critical_regions"] = normalized
    model_result["critical_regions_unknown_ids"] = unknown_ids


def assess_damage(pre_image_path, post_image_path, label_path):
    model_result = {
        "damage_level": "no-damage",
        "confidence": None,
        "reasoning": "Assessment pipeline is connected; detailed scoring is in progress.",
        "critical_regions": [],
    }

    label_json = load_label(label_path)
    labels_xy = extract_labels_xy_from_label_json(label_json)
    critical_regions = extract_critical_regions_from_labels(labels_xy)
    valid_region_ids = {region["id"] for region in critical_regions}
    normalize_region_predictions(model_result, valid_region_ids)

    evaluation = compare_with_ground_truth(model_result, label_json)

    return {
        "model": model_result,
        "evaluation": evaluation,
        "region_count_used": len(critical_regions),
        "critical_regions": critical_regions,
        "inputs": {
            "pre_image": os.path.basename(pre_image_path),
            "post_image": os.path.basename(post_image_path),
            "label_file": os.path.basename(label_path),
        },
    }


def assess_damage_with_retry(pre_image_path, post_image_path, label_path, max_attempts=4, base_delay_seconds=0.5):
    last_error = None

    for attempt in range(max_attempts):
        try:
            return assess_damage(pre_image_path, post_image_path, label_path)
        except Exception as error:
            last_error = error
            if attempt == max_attempts - 1:
                break

            delay = base_delay_seconds * (2 ** attempt)
            delay += random.uniform(0.0, 0.2)
            print(f"Retry {attempt + 1}/{max_attempts - 1} after error: {error}")
            time.sleep(delay)

    raise RuntimeError(f"Assessment failed after {max_attempts} attempts: {last_error}")
