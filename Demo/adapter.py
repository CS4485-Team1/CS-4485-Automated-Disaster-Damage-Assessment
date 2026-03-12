def normalize_building_pair(item):
    building_id = item.get("building_id")
    return {
        "id": building_id,
        "city": item.get("city"),
        "pre_image_path": item.get("pre_crop"),
        "post_image_path": item.get("post_crop"),
        "ground_truth": item.get("subtype"),
    }


def normalize_building_pairs(items):
    normalized = []
    for item in items:
        normalized.append(normalize_building_pair(item))
    return normalized
