import os
import sys
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "linkedin-queue"

TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]

AUTHOR = f"urn:li:person:{PERSON_ID}"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
    "Linkedin-Version": "202608",
}


def get_latest_post():
    posts = sorted(QUEUE.glob("*.md"), reverse=True)

    if not posts:
        print("No LinkedIn post found.")
        return None

    return posts[0]


def publish_post(text):
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

    response = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    print("LinkedIn response:", response.status_code)

    if response.status_code != 201:
        print(response.text)
        response.raise_for_status()

    post_id = response.headers.get("x-restli-id")

    print("LinkedIn post created successfully.")
    print("Post ID:", post_id)

    return post_id


def main():
    file = get_latest_post()

    if not file:
        return 0

    text = file.read_text(encoding="utf-8").strip()

    if not text:
        print("LinkedIn post is empty.")
        return 1

    publish_post(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
