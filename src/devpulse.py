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


# ============================================================
# BASIC FILE HELPERS
# ============================================================

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj):
    path.write_text(
        json.dumps(obj, indent=2),
        encoding="utf-8"
    )


# ============================================================
# SCHEDULING
# ============================================================

def iso_week():
    now = dt.datetime.now(dt.timezone.utc)
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def weekday():
    return dt.datetime.now(dt.timezone.utc).strftime("%A")


def slot():
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
        for day in sorted(selected_days, key=ordered_days.index)
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

    current_key = f"{weekday()}:{slot()}"

    scheduled = {
        f"{item['day']}:{item['slot']}"
        for item in state.get("schedule", [])
    }

    return (
        current_key in scheduled
        and current_key not in state.get("published_this_week", [])
    )


# ============================================================
# TOPIC SELECTION
# ============================================================

def weighted_category(cfg):
    items = list(cfg["category_weights"].items())

    categories = [item[0] for item in items]
    weights = [item[1] for item in items]

    return random.choices(
        categories,
        weights=weights,
        k=1
    )[0]


def choose_topic(topics, state, cfg):
    unused = []

    used_topics = set(
        state.get("used_topics", [])
    )

    for category, topic_list in topics.items():
        for topic in topic_list:
            if topic not in used_topics:
                unused.append(
                    (category, topic)
                )

    if not unused:
        raise RuntimeError(
            "Topic bank exhausted."
        )

    preferred_category = weighted_category(cfg)

    candidates = [
        item
        for item in unused
        if item[0] == preferred_category
    ]

    if not candidates:
        candidates = unused

    return random.choice(candidates)


# ============================================================
# OLLAMA
# ============================================================

def ollama_chat(
    model: str,
    system: str,
    prompt: str,
    temperature: float = 0.3,
    timeout_seconds: int = 420
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
        timeout=timeout_seconds
    )

    response.raise_for_status()

    return response.json()["message"]["content"].strip()


# ============================================================
# SMALL JSON METADATA GENERATION
# ============================================================

def strip_fences(text: str):
    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def extract_json_object(text: str):
    text = strip_fences(text)

    start = text.find("{")

    if start == -1:
        raise ValueError(
            "No JSON object found."
        )

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
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
                    return text[start:index + 1]

    raise ValueError(
        "Incomplete JSON object."
    )


def generate_metadata(
    model: str,
    category: str,
    topic: str
):
    system = """
You are DevPulse.

You create concise metadata for practical developer content.

Return strict JSON only.
"""

    prompt = f"""
Create metadata for this developer topic.

Topic:
{topic}

Category:
{category}

Return ONLY this JSON shape:

{{
  "slug": "kebab-case-slug",
  "title": "clear technical title",
  "commit_message": "short natural git commit message"
}}

Rules:

- slug must use lowercase letters, numbers and hyphens only
- commit message should look natural
- no markdown fences
- no explanations
"""

    raw = ollama_chat(
        model,
        system,
        prompt,
        temperature=0.15,
        timeout_seconds=180
    )

    obj = json.loads(
        extract_json_object(raw)
    )

    slug = obj.get("slug", "").strip()

    if not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*",
        slug
    ):
        raise ValueError(
            f"Invalid slug: {slug}"
        )

    if not obj.get("title"):
        raise ValueError(
            "Missing title."
        )

    if not obj.get("commit_message"):
        raise ValueError(
            "Missing commit message."
        )

    return obj


# ============================================================
# ARTICLE GENERATION
# ============================================================

def generate_article(
    model: str,
    category: str,
    topic: str,
    title: str
):
    system = """
You are a senior backend and AI engineering educator.

Write practical, technically careful developer content.

Do not invent production metrics.
Do not mention confidential companies or projects.
"""

    prompt = f"""
Write a practical technical article.

Title:
{title}

Topic:
{topic}

Category:
{category}

Requirements:

- 400 to 650 words
- Markdown format
- clear introduction
- explain why the topic matters
- include one practical example
- include one section called "Key Takeaways"
- avoid generic motivational filler
- do not invent external links
- do not mention Bosch, GCMMT, customers, internal systems or confidential work
- for AI topics, emphasize engineering and implementation
- for .NET topics, emphasize practical backend usage
- return article only
"""

    article = ollama_chat(
        model,
        system,
        prompt,
        temperature=0.35,
        timeout_seconds=420
    )

    word_count = len(article.split())

    if word_count < 320:
        raise ValueError(
            f"Article too short: {word_count} words."
        )

    return article


# ============================================================
# LINKEDIN POST GENERATION
# ============================================================

def generate_linkedin_post(
    model: str,
    category: str,
    topic: str,
    title: str
):
    system = """
You write professional LinkedIn posts for software engineers.

Make them practical, conversational and technically useful.

Avoid hype and generic filler.
"""

    prompt = f"""
Write a LinkedIn post for this technical topic.

Title:
{title}

Topic:
{topic}

Category:
{category}

Requirements:

- 110 to 180 words
- strong first 1-2 lines
- practical engineering angle
- include 2-4 short bullet points if useful
- mention that a small POC or code sample is available in GitHub
- end naturally
- include 3 to 5 contextual hashtags
- no fake metrics
- no company/client references
- no invented external article links
- return only the LinkedIn post
"""

    post = ollama_chat(
        model,
        system,
        prompt,
        temperature=0.4,
        timeout_seconds=240
    )

    if len(post.split()) < 60:
        raise ValueError(
            "LinkedIn post too short."
        )

    return post


# ============================================================
# SMALL POC GENERATION
# ============================================================

def generate_poc(
    model: str,
    category: str,
    topic: str,
    title: str
):
    system = """
You create small, practical developer proof-of-concept examples.

Keep examples simple and focused.
"""

    if category in {"dotnet", "efcore", "azure"}:
        language = "csharp"

    elif category == "sql":
        language = "sql"

    else:
        language = "python"

    prompt = f"""
Create a very small practical POC for:

Title:
{title}

Topic:
{topic}

Category:
{category}

Preferred language:
{language}

Return ONLY the code.

Requirements:

- keep it small
- roughly 15 to 60 lines
- runnable or very close to runnable
- demonstrate one core idea only
- avoid unnecessary dependencies
- no markdown fences
- no explanations outside code
"""

    code = ollama_chat(
        model,
        system,
        prompt,
        temperature=0.2,
        timeout_seconds=300
    )

    if len(code.splitlines()) < 5:
        raise ValueError(
            "POC too short."
        )

    return language, code


# ============================================================
# README FOR THE POC
# ============================================================

def generate_poc_readme(
    model: str,
    topic: str,
    title: str,
    language: str
):
    system = """
You write concise README files for small technical demos.
"""

    prompt = f"""
Write a concise README for a small proof-of-concept.

Title:
{title}

Topic:
{topic}

Language:
{language}

Requirements:

- Markdown only
- 150 to 250 words
- sections:
  - What this demonstrates
  - How it works
  - How to run
  - Notes
- no external links
- no invented metrics
"""

    return ollama_chat(
        model,
        system,
        prompt,
        temperature=0.25,
        timeout_seconds=240
    )


# ============================================================
# CONTENT GENERATION WITH COMPONENT-LEVEL RETRIES
# ============================================================

def retry_component(
    label,
    func,
    attempts=3
):
    last_error = None

    for attempt in range(
        1,
        attempts + 1
    ):
        try:
            print(
                f"{label} attempt "
                f"{attempt}/{attempts}"
            )

            return func()

        except Exception as ex:
            last_error = ex

            print(
                f"{label} failed: {ex}"
            )

    raise RuntimeError(
        f"{label} failed after "
        f"{attempts} attempts. "
        f"Last error: {last_error}"
    )


def generate_content_package(
    cfg,
    category,
    topic
):
    model = cfg["model"]

    metadata = retry_component(
        "Metadata generation",
        lambda: generate_metadata(
            model,
            category,
            topic
        ),
        attempts=3
    )

    title = metadata["title"]

    article = retry_component(
        "Article generation",
        lambda: generate_article(
            model,
            category,
            topic,
            title
        ),
        attempts=3
    )

    linkedin_post = retry_component(
        "LinkedIn generation",
        lambda: generate_linkedin_post(
            model,
            category,
            topic,
            title
        ),
        attempts=3
    )

    language, poc_code = retry_component(
        "POC generation",
        lambda: generate_poc(
            model,
            category,
            topic,
            title
        ),
        attempts=3
    )

    poc_readme = retry_component(
        "POC README generation",
        lambda: generate_poc_readme(
            model,
            topic,
            title,
            language
        ),
        attempts=2
    )

    return {
        "slug": metadata["slug"],
        "title": title,
        "commit_message": metadata["commit_message"],
        "article": article,
        "linkedin_post": linkedin_post,
        "language": language,
        "poc_code": poc_code,
        "poc_readme": poc_readme
    }


# ============================================================
# WRITE OUTPUT
# ============================================================

def file_extension(language: str):
    mapping = {
        "csharp": "cs",
        "python": "py",
        "sql": "sql"
    }

    return mapping.get(
        language.lower(),
        "txt"
    )


def write_output(
    category,
    topic,
    package
):
    today = dt.datetime.now(
        dt.timezone.utc
    ).date().isoformat()

    base = (
        PUBLISHED
        / f"{today}-{package['slug']}"
    )

    base.mkdir(
        parents=True,
        exist_ok=True
    )

    article_header = (
        f"# {package['title']}\n\n"
        f"**Topic:** {topic}  \n"
        f"**Category:** {category}\n\n"
    )

    (
        base
        / "ARTICLE.md"
    ).write_text(
        article_header
        + package["article"].strip()
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

    extension = file_extension(
        package["language"]
    )

    if extension == "cs":
        code_filename = "Program.cs"

    elif extension == "py":
        code_filename = "main.py"

    elif extension == "sql":
        code_filename = "demo.sql"

    else:
        code_filename = "example.txt"

    (
        sample_dir
        / code_filename
    ).write_text(
        package["poc_code"].strip()
        + "\n",
        encoding="utf-8"
    )

    (
        sample_dir
        / "README.md"
    ).write_text(
        package["poc_readme"].strip()
        + "\n",
        encoding="utf-8"
    )

    LINKEDIN.mkdir(
        exist_ok=True
    )

    github_link = (
        "\n\n"
        "💻 Full POC & code:\n"
        "https://github.com/ketu98/devpulse"
    )

    linkedin_content = (
        package["linkedin_post"].strip()
        + github_link
        + "\n"
    )

    linkedin_path = (
        LINKEDIN
        / f"{today}-{package['slug']}.md"
    )

    linkedin_path.write_text(
        linkedin_content,
        encoding="utf-8"
    )

    return base


# ============================================================
# VALIDATION
# ============================================================

def validate_generated_content(
    category,
    topic,
    package
):
    combined = (
        package["article"]
        + "\n"
        + package["linkedin_post"]
        + "\n"
        + package["poc_code"]
    ).lower()

    banned_terms = [
        "bosch",
        "gcmmt",
        "customer master data workflow"
    ]

    for term in banned_terms:
        if term in combined:
            raise ValueError(
                f"Potential confidential reference found: {term}"
            )

    if len(
        package["article"].split()
    ) < 320:
        raise ValueError(
            "Article validation failed."
        )

    if len(
        package["linkedin_post"].split()
    ) < 60:
        raise ValueError(
            "LinkedIn validation failed."
        )

    if not package["poc_code"].strip():
        raise ValueError(
            "POC code is empty."
        )

    print(
        "Content package validation passed."
    )


# ============================================================
# OPTIONAL BUILD
# ============================================================

def maybe_dotnet_build(base):
    projects = list(
        base.rglob("*.csproj")
    )

    if not projects:
        print(
            "No generated .csproj found. "
            "Skipping dotnet build."
        )
        return

    for project in projects:
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


# ============================================================
# INDEX
# ============================================================

def update_index():
    rows = []

    if PUBLISHED.exists():
        for folder in sorted(
            PUBLISHED.iterdir(),
            reverse=True
        ):
            if not folder.is_dir():
                continue

            article = folder / "ARTICLE.md"

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

    output = (
        "# DevPulse Content Index\n\n"
    )

    if rows:
        output += "\n".join(rows)
        output += "\n"

    else:
        output += (
            "_No content published yet._\n"
        )

    (
        ROOT
        / "CONTENT_INDEX.md"
    ).write_text(
        output,
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

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

    package = generate_content_package(
        cfg,
        category,
        topic
    )

    validate_generated_content(
        category,
        topic,
        package
    )

    base = write_output(
        category,
        topic,
        package
    )

    maybe_dotnet_build(
        base
    )

    update_index()

    run_key = (
        f"{weekday()}:{slot()}"
    )

    if not force:
        if run_key not in state.get(
            "published_this_week",
            []
        ):
            state.setdefault(
                "published_this_week",
                []
            ).append(
                run_key
            )

    if topic not in state.get(
        "used_topics",
        []
    ):
        state.setdefault(
            "used_topics",
            []
        ).append(
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
        package[
            "commit_message"
        ].strip(),
        encoding="utf-8"
    )

    print(
        f"DevPulse package written to: "
        f"{base}"
    )

    print(
        "LinkedIn post generated successfully."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
