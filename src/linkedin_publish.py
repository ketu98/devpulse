from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import requests


ROOT = Path(
    __file__
).resolve().parents[1]

MANIFEST = (
    ROOT
    / ".devpulse_manifest.json"
)

TOKEN = os.environ[
    "LINKEDIN_ACCESS_TOKEN"
]

PERSON_ID = os.environ[
    "LINKEDIN_PERSON_ID"
]

AUTHOR = (
    f"urn:li:person:"
    f"{PERSON_ID}"
)

VERSION = os.environ.get(
    "LINKEDIN_VERSION",
    "202608"
)


HEADERS = {
    "Authorization":
        f"Bearer {TOKEN}",

    "Content-Type":
        "application/json",

    "X-Restli-Protocol-Version":
        "2.0.0",

    "Linkedin-Version":
        VERSION,
}


# ============================================================
# TEXT CLEANING
# ============================================================

def normalize_text(
    text
):
    """
    LinkedIn commentary is plain text.

    Clean accidental LLM formatting
    and preserve real line breaks.
    """

    text = text.replace(
        "\\r\\n",
        "\n"
    )

    text = text.replace(
        "\\n",
        "\n"
    )

    text = text.replace(
        "\\t",
        " "
    )

    text = text.replace(
        "---SNIPPET---",
        ""
    )

    text = text.replace(
        "---END SNIPPET---",
        ""
    )

    text = re.sub(
        r"```(?:\w+)?",
        "",
        text
    )

    text = text.replace(
        "```",
        ""
    )

    cleaned_lines = [
        line.rstrip()
        for line
        in text.splitlines()
    ]

    text = "\n".join(
        cleaned_lines
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# IMAGE UPLOAD
# ============================================================

def initialize_image_upload():

    payload = {
        "initializeUploadRequest": {
            "owner": AUTHOR
        }
    }

    response = requests.post(
        (
            "https://api.linkedin.com/"
            "rest/images"
            "?action=initializeUpload"
        ),
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    print(
        "Initialize image:",
        response.status_code
    )

    if response.status_code not in (
        200,
        201
    ):

        print(
            response.text
        )

        response.raise_for_status()

    value = response.json()[
        "value"
    ]

    upload_url = value[
        "uploadUrl"
    ]

    image_urn = value[
        "image"
    ]

    return (
        upload_url,
        image_urn
    )


def upload_image(
    upload_url,
    image_path
):
    data = (
        image_path
        .read_bytes()
    )

    headers = {
        "Authorization":
            f"Bearer {TOKEN}",

        "Content-Type":
            "application/octet-stream"
    }

    response = requests.put(
        upload_url,
        headers=headers,
        data=data,
        timeout=120
    )

    print(
        "Upload image bytes:",
        response.status_code
    )

    if not (
        200
        <= response.status_code
        < 300
    ):

        print(
            response.text
        )

        response.raise_for_status()


# ============================================================
# LINKEDIN POST
# ============================================================

def publish_post(
    text,
    image_urn,
    alt_text
):
    payload = {
        "author":
            AUTHOR,

        "commentary":
            text,

        "visibility":
            "PUBLIC",

        "distribution": {
            "feedDistribution":
                "MAIN_FEED",

            "targetEntities":
                [],

            "thirdPartyDistributionChannels":
                []
        },

        "lifecycleState":
            "PUBLISHED",

        "isReshareDisabledByAuthor":
            False
    }

    if image_urn:

        payload[
            "content"
        ] = {
            "media": {
                "altText":
                    alt_text[:120],

                "id":
                    image_urn
            }
        }

    response = requests.post(
        (
            "https://api.linkedin.com/"
            "rest/posts"
        ),
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    print(
        "LinkedIn post response:",
        response.status_code
    )

    if response.status_code != 201:

        print(
            response.text
        )

        response.raise_for_status()

    post_id = (
        response
        .headers
        .get(
            "x-restli-id"
        )
    )

    print(
        "LinkedIn post created successfully."
    )

    print(
        "Post ID:",
        post_id
    )

    return post_id


# ============================================================
# VALIDATION
# ============================================================

def validate_linkedin_text(
    text
):
    if not text:

        raise ValueError(
            "LinkedIn post is empty."
        )

    if "\\n" in text:

        raise ValueError(
            "Literal escaped newline remains."
        )

    if "---SNIPPET---" in text:

        raise ValueError(
            "Prompt marker remains."
        )

    hashtag_count = len(
        re.findall(
            r"(?<!\w)#\w+",
            text
        )
    )

    if hashtag_count < 3:

        raise ValueError(
            f"Only {hashtag_count} hashtags found."
        )

    required_sections = [
        "💻 Small POC",
        "✅ Key takeaway",
        "🔗 Full runnable POC"
    ]

    for section in required_sections:

        if section not in text:

            raise ValueError(
                f"Missing LinkedIn section: "
                f"{section}"
            )

    if not (
        100
        <= len(text)
        <= 3000
    ):

        raise ValueError(
            "Unexpected LinkedIn commentary "
            f"length: {len(text)}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    if not MANIFEST.exists():

        print(
            "No current DevPulse manifest. "
            "Nothing to publish."
        )

        return 0

    manifest = json.loads(
        MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    if not manifest.get(
        "generated"
    ):

        print(
            "Manifest says no content "
            "was generated."
        )

        return 0

    linkedin_file = (
        ROOT
        / manifest[
            "linkedin_file"
        ]
    )

    image_file = (
        ROOT
        / manifest[
            "image_file"
        ]
    )

    if not linkedin_file.exists():

        raise FileNotFoundError(
            linkedin_file
        )

    text = (
        linkedin_file
        .read_text(
            encoding="utf-8"
        )
    )

    text = normalize_text(
        text
    )

    validate_linkedin_text(
        text
    )

    print(
        "\n"
        "===== LINKEDIN PREVIEW ====="
        "\n"
    )

    print(
        text
    )

    print(
        "\n"
        "============================"
        "\n"
    )

    image_urn = None

    if image_file.exists():

        (
            upload_url,
            image_urn
        ) = initialize_image_upload()

        upload_image(
            upload_url,
            image_file
        )

        time.sleep(
            3
        )

    post_id = publish_post(
        text=text,
        image_urn=image_urn,
        alt_text=(
            "DevPulse technical diagram: "
            + manifest.get(
                "title",
                "technical POC"
            )
        )
    )

    published_metadata = {
        "post_id":
            post_id,

        "title":
            manifest.get(
                "title"
            ),

        "topic":
            manifest.get(
                "topic"
            ),

        "published_via":
            "LinkedIn Posts API"
    }

    metadata_path = (
        linkedin_file
        .with_suffix(
            ".published.json"
        )
    )

    metadata_path.write_text(
        json.dumps(
            published_metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
