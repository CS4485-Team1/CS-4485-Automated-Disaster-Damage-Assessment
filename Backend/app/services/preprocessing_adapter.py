""" integrating preprocessing output into the VLM pipeline.

This wraps app.services.preprocessing without modifying it.
"""

from __future__ import annotations

import os
from typing import Any

from app.services.preprocessing import get_pairs


DEFAULT_IMAGE_ROOT = os.path.join("Backend", "data", "santa_rosa", "images")


def _as_abs(path: str) -> str:
    return os.path.abspath(path)


def normalize_pair(raw_pair: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw preprocessing pair into stable integration keys."""
    return {
        "id": raw_pair.get("id"),
        "city": raw_pair.get("city"),
        "pre_image_path": raw_pair.get("pre"),
        "post_image_path": raw_pair.get("post"),
        "labels_xy": raw_pair.get("labels", []),
    }


def validate_pair(pair: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate normalized pair and return (is_valid, issues)."""
    issues: list[str] = []

    if not pair.get("id"):
        issues.append("missing id")
    if not pair.get("pre_image_path"):
        issues.append("missing pre_image_path")
    if not pair.get("post_image_path"):
        issues.append("missing post_image_path")

    pre_path = pair.get("pre_image_path")
    post_path = pair.get("post_image_path")
    if isinstance(pre_path, str) and not os.path.exists(pre_path):
        issues.append(f"pre image not found: {pre_path}")
    if isinstance(post_path, str) and not os.path.exists(post_path):
        issues.append(f"post image not found: {post_path}")

    labels = pair.get("labels_xy", [])
    if not isinstance(labels, list):
        issues.append("labels_xy must be a list")

    return len(issues) == 0, issues


def load_and_normalize_pairs(image_root: str = DEFAULT_IMAGE_ROOT) -> list[dict[str, Any]]:
    """Load raw pairs from preprocessing and normalize for pipeline usage."""
    raw_pairs = get_pairs(_as_abs(image_root))
    return [normalize_pair(pair) for pair in raw_pairs]


def load_normalized_pairs_with_issues(image_root: str = DEFAULT_IMAGE_ROOT) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return validated normalized pairs and any rejected pairs with reasons."""
    normalized = load_and_normalize_pairs(image_root=image_root)

    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []

    for pair in normalized:
        is_valid, issues = validate_pair(pair)
        if is_valid:
            valid.append(pair)
        else:
            invalid.append({"pair": pair, "issues": issues})

    return valid, invalid
