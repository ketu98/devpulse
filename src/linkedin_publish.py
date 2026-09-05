from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".devpulse_manifest.json"

TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]
AUTHOR = f"urn:li:person:{PERSON_ID}"
VERSION = os.environ.get("LINKEDIN_VERSION", "202608")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
    "Linkedin-Version": VERSION,
}


def normalize_text(text: str):
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", " ")
    text = re.sub(r"```(?:\w+)?", "", text)
    text = text.replace("```", "")
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def initialize_image_upload():
    payload = {
        "initializeUploadRequest": {
            "owner": AUTHOR
        }
    }
    r = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=HEADERS,
        json=payload,
        timeout=60
    )
    print("Initialize image:", r.status_code)
    if r.status_code not in (200, 201):
        print(r.text)
        r.raise_for_status()

    value = r.json()["value"]
    return value["uploadUrl"], value["image"]


def upload_image(upload_url: str, image_path: Path):
    data = image_path.read_bytes()
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    r = requests.put(upload_url, headers=headers, data=data, timeout=120)
    print("Upload image bytes:", r.status_code)
    if not (200 <= r.status_code < 300):
        print(r.text)
        r.raise_for_status()


def publish_post(text: str, image_urn: str | None, alt_text: str):
    payload = {
        "author": AUTHOR,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    if image_urn:
        payload["content"] = {
            "media": {
                "altText": alt_text[:120],
                "id": image_urn
            }
        }

    r = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    print("LinkedIn post response:", r.status_code)
    if r.status_code != 201:
        print(r.text)
        r.raise_for_status()

    post_id = r.headers.get("x-restli-id")
    print("LinkedIn post created successfully.")
    print("Post ID:", post_id)
    return post_id


def main():
    if not MANIFEST.exists():
        print("No current DevPulse manifest. Nothing to publish.")
        return 0

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if not manifest.get("generated"):
        print("Manifest says no content was generated.")
        return 0

    linkedin_file = ROOT / manifest["linkedin_file"]
    image_file = ROOT / manifest["image_file"]

    if not linkedin_file.exists():
        raise FileNotFoundError(linkedin_file)

    text = normalize_text(linkedin_file.read_text(encoding="utf-8"))

    if "\\n" in text:
        raise ValueError("Literal escaped newline remains in LinkedIn text.")
    if not (100 <= len(text) <= 3000):
        raise ValueError(f"Unexpected LinkedIn commentary length: {len(text)}")

    print("\n===== LINKEDIN PREVIEW =====\n")
    print(text)
    print("\n============================\n")

    image_urn = None
    if image_file.exists():
        upload_url, image_urn = initialize_image_upload()
        upload_image(upload_url, image_file)
        # Asset processing is asynchronous. A short wait is normally enough for a small PNG.
        time.sleep(3)

    post_id = publish_post(
        text,
        image_urn=image_urn,
        alt_text=f"DevPulse technical diagram: {manifest.get('title','technical POC')}"
    )

    # Save publication metadata so the repo shows what was posted.
    published_meta = {
        "post_id": post_id,
        "title": manifest.get("title"),
        "topic": manifest.get("topic"),
        "published_via": "LinkedIn Posts API"
    }
    meta_path = (ROOT / manifest["linkedin_file"]).with_suffix(".published.json")
    meta_path.write_text(json.dumps(published_meta, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
