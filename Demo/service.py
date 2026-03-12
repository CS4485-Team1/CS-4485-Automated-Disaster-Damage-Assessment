import base64
import json
import os
import random
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / "Backend" / ".env")

MODEL_NAME = os.getenv("OPENAI_VLM_MODEL", "gpt-4o-mini")


def image_to_data_url(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/png"
    if ext in [".jpg", ".jpeg"]:
        mime = "image/jpeg"

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{b64}"


def extract_json_text(response):
    text = (response.output_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return text


def call_vlm(pre_image_path, post_image_path):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Compare these cropped pre-disaster and post-disaster building images. "
                            "Return JSON only with keys: damage_level, confidence, reasoning. "
                            "damage_level must be one of: no-damage, minor-damage, major-damage, destroyed."
                        ),
                    },
                    {"type": "input_image", "image_url": image_to_data_url(pre_image_path)},
                    {"type": "input_image", "image_url": image_to_data_url(post_image_path)},
                ],
            }
        ],
        temperature=0,
    )

    raw_text = extract_json_text(response)
    result = json.loads(raw_text)

    if "damage_level" not in result:
        result["damage_level"] = "no-damage"
    if "confidence" not in result:
        result["confidence"] = None
    if "reasoning" not in result:
        result["reasoning"] = ""

    return result


def call_vlm_with_retry(pre_image_path, post_image_path, max_attempts=4, base_delay_seconds=0.5):
    last_error = None

    for attempt in range(max_attempts):
        try:
            return call_vlm(pre_image_path, post_image_path)
        except Exception as error:
            last_error = error
            if attempt == max_attempts - 1:
                break

            delay = base_delay_seconds * (2 ** attempt)
            delay += random.uniform(0.0, 0.2)
            print(f"Retry {attempt + 1}/{max_attempts - 1} after error: {error}")
            time.sleep(delay)

    raise RuntimeError(f"VLM call failed after {max_attempts} attempts: {last_error}")
