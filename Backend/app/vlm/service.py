"""VLM service layer."""

import os

from app.vlm.label_utils import compare_with_ground_truth, load_label


def assess_damage(pre_image_path: str, post_image_path: str, label_path: str) -> dict:
    """Return structured assessment."""
    model_result = {
        "damage_level": "no-damage",
        "confidence": None,
        "reasoning": "Assessment pipeline is connected; detailed scoring is in progress.",
    }

    label_json = load_label(label_path)
    evaluation = compare_with_ground_truth(model_result, label_json)

    return {
        "model": model_result,
        "evaluation": evaluation,
        "inputs": {
            "pre_image": os.path.basename(pre_image_path),
            "post_image": os.path.basename(post_image_path),
            "label_file": os.path.basename(label_path),
        },
    }
