from __future__ import annotations

import datetime as dt
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLISHED = ROOT / "published"
LINKEDIN = ROOT / "linkedin-queue"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path, obj):
    Path(path).write_text(
        json.dumps(obj, indent=2),
        encoding="utf-8"
    )


def iso_week():
    now = dt.datetime.now(dt.timezone.utc)
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def weekday():
    return dt.datetime.now(dt.timezone.utc).strftime("%A")


def slot():
    """
    Workflow wakes at approximately:
      04:17 UTC
      10:43 UTC
      15:29 UTC

    Categorize the current execution into a logical slot.
    """

    hour = dt.datetime.now(dt.timezone.utc).hour

    if hour < 8:
        return "morning"

    if hour < 13:
        return "afternoon"

    return "evening"


def refresh_week(state, cfg):
    current_week = iso_week()

    if state.get("week") == current_week:
        return state

    target_runs = random.randint(
        cfg["min_runs_per_week"],
        cfg["max_runs_per_week"]
    )

    ordered_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    selected_days = random.sample(
        ordered_days,
        target_runs
    )

    available_slots = [
        "morning",
        "afternoon",
        "evening"
    ]

    schedule = [
        {
            "day": day,
            "slot": random.choice(available_slots)
        }
        for day in sorted(
            selected_days,
            key=ordered_days.index
        )
    ]

    state.update({
        "week": current_week,
        "target_runs": target_runs,
        "schedule": schedule,
        "published_this_week": []
    })

    return state


def should_publish(state, force=False):
    if force:
        return True

    today = weekday()
    current_slot = slot()

    current_key = f"{today}:{current_slot}"

    scheduled = {
        f"{item['day']}:{item['slot']}"
        for item in state.get("schedule", [])
    }

    return (
        current_key in scheduled
        and current_key not in state["published_this_week"]
    )


def weighted_category(cfg):
    items = list(cfg["category_weights"].items())

    categories = [
        item[0]
        for item in items
    ]

    weights = [
        item[1]
        for item in items
    ]

    return random.choices(
        categories,
        weights=weights,
        k=1
    )[0]


def choose_topic(topics, state, cfg):
    unused_topics = []

    for category, values in topics.items():
        for topic in values:
            if topic not in state["used_topics"]:
                unused_topics.append(
                    (category, topic)
                )

    if not unused_topics:
        raise RuntimeError(
            "Topic bank exhausted."
        )

    preferred_category = weighted_category(cfg)

    candidates = [
        item
        for item in unused_topics
        if item[0] == preferred_category
    ]

    if not candidates:
        candidates = unused_topics

    return random.choice(candidates)


def ollama_chat(
    model,
    system,
    prompt,
    temperature=0.4
):
    url = os.environ.get(
        "OLLAMA_URL",
        "http://127.0.0.1:11434/api/chat"
    )

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "options": {
            "temperature": temperature
        }
    }

    response = requests.post(
        url,
        json=payload,
        timeout=900
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def strip_fences(text):
    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def extract_json(text):
    """
    Extract the first complete JSON object from an LLM response.

    Handles:
    - ```json fences
    - text before JSON
    - text after JSON
    - braces inside JSON strings
    """

    text = strip_fences(text)

    start = text.find("{")

    if start == -1:
        raise ValueError(
            "No JSON object found in model response."
        )

    depth = 0
    in_string = False
    escape = False

    for index in range(
        start,
        len(text)
    ):
        char = text[index]

        if escape:
            escape = False
            continue

        if char == "\\" and in_string:
            escape = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if not in_string:
            if char == "{":
                depth += 1

            elif char == "}":
                depth -= 1

                if depth == 0:
                    return text[
                        start:index + 1
                    ]

    raise ValueError(
        "Incomplete JSON object returned by model."
    )


def parse_generated_json(raw):
    json_text = extract_json(raw)

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as ex:
        raise ValueError(
            f"Invalid generated JSON: {ex}"
        ) from ex


def generation_prompt(
    category,
    topic
):
    return f"""
Create one practical developer-learning contribution.

Topic:
{topic}

Category:
{category}

Audience:
Recruiters, backend developers, senior engineers,
and developers learning practical software engineering.

Return ONLY valid JSON.

Use this exact shape:

{{
  "slug": "kebab-case-slug",
  "title": "human-readable title",
  "commit_message": "conventional commit message",
  "article_markdown": "500-900 word Markdown article",
  "linkedin_post": "120-220 word professional LinkedIn post including 3-5 relevant hashtags",
  "code_files": [
    {{
      "path": "Program.cs",
      "content": "file content"
    }},
    {{
      "path": "README.md",
      "content": "file content"
    }}
  ]
}}

IMPORTANT RULES:

1. Return JSON only.
2. Do not wrap the result in Markdown fences.
3. Escape quotes correctly inside JSON strings.
4. Escape newlines inside JSON strings.
5. Do not use trailing commas.
6. Prefer practical examples over theory.
7. Prefer runnable C#/.NET examples for:
   - dotnet
   - efcore
   - azure
8. For SQL topics, include a .sql artifact where useful.
9. For AI / GenAI topics, include:
   - a small POC,
   - practical code,
   - architecture explanation where appropriate.
10. Do not invent external links.
11. Do not invent statistics or production metrics.
12. Never mention:
   - Bosch
   - GCMMT
   - internal company systems
   - customer names
   - confidential project information
13. Make the LinkedIn post useful even without opening GitHub.
14. Use 3-5 relevant hashtags maximum.
15. Do not produce generic motivational filler.
"""


def validate_payload(payload):
    required_fields = [
        "slug",
        "title",
        "commit_message",
        "article_markdown",
        "linkedin_post",
        "code_files"
    ]

    for field in required_fields:
        if field not in payload:
            raise ValueError(
                f"Missing required field: {field}"
            )

    slug = payload["slug"]

    if not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*",
        slug
    ):
        raise ValueError(
            "Invalid slug format."
        )

    article_words = len(
        payload["article_markdown"].split()
    )

    if article_words < 350:
        raise ValueError(
            f"Article too short: {article_words} words."
        )

    linkedin_words = len(
        payload["linkedin_post"].split()
    )

    if linkedin_words < 50:
        raise ValueError(
            "LinkedIn post is too short."
        )

    banned_terms = [
        "bosch",
        "gcmmt",
        "customer master data workflow"
    ]

    combined_text = json.dumps(
        payload
    ).lower()

    for term in banned_terms:
        if term in combined_text:
            raise ValueError(
                f"Potential confidential reference found: {term}"
            )

    code_files = payload["code_files"]

    if not isinstance(
        code_files,
        list
    ):
        raise ValueError(
            "code_files must be a list."
        )

    if not code_files:
        raise ValueError(
            "No code/artifact files generated."
        )

    for file in code_files:
        if "path" not in file:
            raise ValueError(
                "Generated file missing path."
            )

        if "content" not in file:
            raise ValueError(
                "Generated file missing content."
            )

        path = Path(
            file["path"]
        )

        if path.is_absolute():
            raise ValueError(
                "Absolute output paths are not allowed."
            )

        if ".." in path.parts:
            raise ValueError(
                "Unsafe output path."
            )


def write_output(
    category,
    topic,
    payload
):
    today = (
        dt.datetime
        .now(dt.timezone.utc)
        .date()
        .isoformat()
    )

    base = (
        PUBLISHED
        / f"{today}-{payload['slug']}"
    )

    base.mkdir(
        parents=True,
        exist_ok=True
    )

    article_header = (
        f"# {payload['title']}\n\n"
        f"**Topic:** {topic}  \n"
        f"**Category:** {category}\n\n"
    )

    article_path = (
        base
        / "ARTICLE.md"
    )

    article_path.write_text(
        article_header
        + payload["article_markdown"].strip()
        + "\n",
        encoding="utf-8"
    )

    sample_dir = (
        base
        / "sample"
    )

    sample_dir.mkdir(
        exist_ok=True
    )

    for file in payload["code_files"]:
        destination = (
            sample_dir
            / file["path"]
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        destination.write_text(
            file["content"],
            encoding="utf-8"
        )

    LINKEDIN.mkdir(
        exist_ok=True
    )

    linkedin_path = (
        LINKEDIN
        / f"{today}-{payload['slug']}.md"
    )

    github_link = (
        "\n\n"
        "💻 Full POC & code:\n"
        "https://github.com/ketu98/devpulse"
    )

    linkedin_text = (
        payload["linkedin_post"].strip()
        + github_link
        + "\n"
    )

    linkedin_path.write_text(
        linkedin_text,
        encoding="utf-8"
    )

    return base


def maybe_dotnet_build(base):
    projects = list(
        base.rglob("*.csproj")
    )

    if not projects:
        print(
            "No .csproj generated. "
            "Skipping dotnet build."
        )
        return

    for project in projects:
        print(
            f"Building generated project: "
            f"{project}"
        )

        subprocess.run(
            [
                "dotnet",
                "build",
                str(project),
                "-c",
                "Release",
                "--nologo"
            ],
            check=True
        )


def update_index():
    rows = []

    if PUBLISHED.exists():
        folders = sorted(
            PUBLISHED.iterdir(),
            reverse=True
        )

        for folder in folders:
            if not folder.is_dir():
                continue

            article = (
                folder
                / "ARTICLE.md"
            )

            if not article.exists():
                continue

            lines = article.read_text(
                encoding="utf-8"
            ).splitlines()

            if not lines:
                continue

            title = (
                lines[0]
                .lstrip("# ")
                .strip()
            )

            relative = (
                article
                .relative_to(ROOT)
                .as_posix()
            )

            rows.append(
                f"- [{title}]({relative})"
            )

    content = (
        "# DevPulse Content Index\n\n"
    )

    if rows:
        content += "\n".join(rows)
        content += "\n"

    else:
        content += (
            "_No content published yet._\n"
        )

    (
        ROOT
        / "CONTENT_INDEX.md"
    ).write_text(
        content,
        encoding="utf-8"
    )


def generate_payload(
    cfg,
    category,
    topic
):
    system_prompt = """
You are DevPulse, a careful senior backend and AI engineering educator.

Your job is to create practical,
technically accurate developer content.

Return strict JSON only.

Prefer correctness,
working examples,
and practical explanations
over hype.
"""

    max_repair_attempts = cfg.get(
        "max_repair_attempts",
        4
    )

    payload = None
    raw = None
    last_error = None

    total_attempts = (
        max_repair_attempts + 1
    )

    for attempt in range(
        1,
        total_attempts + 1
    ):
        try:
            if attempt == 1:
                print(
                    "Generating DevPulse content..."
                )

                raw = ollama_chat(
                    cfg["model"],
                    system_prompt,
                    generation_prompt(
                        category,
                        topic
                    ),
                    temperature=0.35
                )

            else:
                repair_number = (
                    attempt - 1
                )

                print(
                    f"Repair attempt "
                    f"{repair_number}/"
                    f"{max_repair_attempts}"
                )

                repair_prompt = f"""
The previous response was invalid.

Topic:
{topic}

Category:
{category}

Validation error:
{last_error}

Repair the response.

CRITICAL RULES:

1. Return ONLY JSON.
2. Do NOT use ```json fences.
3. Do NOT add explanations before or after the JSON.
4. Escape all newline characters inside JSON string values using \\n.
5. Escape double quotes inside code strings.
6. Do not include trailing commas.
7. Ensure every key/value pair is separated by a comma.
8. Ensure Python json.loads() can parse the response.
9. Do not remove required fields.
10. Preserve the intended technical content.

Required structure:

{{
  "slug": "kebab-case-slug",
  "title": "title",
  "commit_message": "commit message",
  "article_markdown": "markdown article",
  "linkedin_post": "linkedin post with hashtags",
  "code_files": [
    {{
      "path": "Program.cs",
      "content": "file content"
    }}
  ]
}}

Previous response:

{raw}
"""

                raw = ollama_chat(
                    cfg["model"],
                    system_prompt,
                    repair_prompt,
                    temperature=0.1
                )

            payload = parse_generated_json(
                raw
            )

            validate_payload(
                payload
            )

            print(
                "Generated content validated successfully."
            )

            return payload

        except Exception as ex:
            last_error = str(ex)

            print(
                f"Generation attempt "
                f"{attempt} failed:"
            )

            print(
                last_error
            )

            payload = None

    raise RuntimeError(
        "Unable to generate valid content "
        f"after {total_attempts} attempts. "
        f"Last error: {last_error}"
    )


def main():
    force = (
        "--force"
        in sys.argv
    )

    cfg = load_json(
        DATA / "config.json"
    )

    topics = load_json(
        DATA / "topics.json"
    )

    state = load_json(
        DATA / "state.json"
    )

    state = refresh_week(
        state,
        cfg
    )

    save_json(
        DATA / "state.json",
        state
    )

    print(
        f"Week {state['week']} "
        f"target={state['target_runs']} "
        f"schedule={state.get('schedule', [])}"
    )

    if not should_publish(
        state,
        force
    ):
        print(
            "No publication scheduled "
            "for this run."
        )

        return 0

    category, topic = choose_topic(
        topics,
        state,
        cfg
    )

    print(
        f"Selected: "
        f"[{category}] "
        f"{topic}"
    )

    payload = generate_payload(
        cfg,
        category,
        topic
    )

    base = write_output(
        category,
        topic,
        payload
    )

    maybe_dotnet_build(
        base
    )

    update_index()

    run_key = (
        f"{weekday()}:"
        f"{slot()}"
    )

    if run_key not in state[
        "published_this_week"
    ]:
        state[
            "published_this_week"
        ].append(
            run_key
        )

    if topic not in state[
        "used_topics"
    ]:
        state[
            "used_topics"
        ].append(
            topic
        )

    save_json(
        DATA / "state.json",
        state
    )

    (
        ROOT
        / ".devpulse_commit_message"
    ).write_text(
        payload[
            "commit_message"
        ].strip(),
        encoding="utf-8"
    )

    print(
        f"Published locally: {base}"
    )

    print(
        "LinkedIn content generated."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
