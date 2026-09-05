from __future__ import annotations

import datetime as dt
import json
import os
import random
import re
import sys
from pathlib import Path

import requests

from reference_finder import find_references
from diagram_generator import generate_diagram


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLISHED = ROOT / "published"
LINKEDIN = ROOT / "linkedin-queue"
MANIFEST = ROOT / ".devpulse_manifest.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj):
    path.write_text(
        json.dumps(obj, indent=2),
        encoding="utf-8"
    )


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def iso_week():
    year, week, _ = utc_now().isocalendar()
    return f"{year}-W{week:02d}"


def weekday():
    return utc_now().strftime("%A")


def slot():
    hour = utc_now().hour

    if hour < 8:
        return "morning"

    if hour < 13:
        return "afternoon"

    return "evening"


# ============================================================
# WEEKLY RANDOM SCHEDULING
# ============================================================

def refresh_week(state, cfg):
    current_week = iso_week()

    if state.get("week") == current_week:
        return state

    ordered_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    target_runs = random.randint(
        cfg["min_runs_per_week"],
        cfg["max_runs_per_week"]
    )

    selected_days = random.sample(
        ordered_days,
        target_runs
    )

    slots = [
        "morning",
        "afternoon",
        "evening"
    ]

    schedule = [
        {
            "day": day,
            "slot": random.choice(slots)
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

    current_key = (
        f"{weekday()}:{slot()}"
    )

    scheduled = {
        f"{item['day']}:{item['slot']}"
        for item in state.get(
            "schedule",
            []
        )
    }

    return (
        current_key in scheduled
        and current_key not in state.get(
            "published_this_week",
            []
        )
    )


# ============================================================
# TOPIC SELECTION
# ============================================================

def weighted_category(cfg):
    pairs = list(
        cfg["category_weights"].items()
    )

    categories = [
        pair[0]
        for pair in pairs
    ]

    weights = [
        pair[1]
        for pair in pairs
    ]

    return random.choices(
        categories,
        weights=weights,
        k=1
    )[0]


def choose_topic(
    topics,
    state,
    cfg
):
    used_topics = set(
        state.get(
            "used_topics",
            []
        )
    )

    unused = [
        (
            category,
            topic
        )
        for category, values
        in topics.items()
        for topic in values
        if topic not in used_topics
    ]

    if not unused:
        raise RuntimeError(
            "Topic bank exhausted."
        )

    preferred = weighted_category(
        cfg
    )

    candidates = [
        item
        for item in unused
        if item[0] == preferred
    ]

    if not candidates:
        candidates = unused

    return random.choice(
        candidates
    )


# ============================================================
# OLLAMA
# ============================================================

def ollama_chat(
    model,
    system,
    prompt,
    temperature=0.3,
    timeout_seconds=360
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
            "temperature": temperature,
            "num_predict": 1200
        }
    }

    response = requests.post(
        url,
        json=payload,
        timeout=timeout_seconds
    )

    response.raise_for_status()

    return response.json()[
        "message"
    ][
        "content"
    ].strip()


def strip_fences(
    text
):
    text = text.strip()

    text = re.sub(
        r"^```(?:json|python|csharp|cs|sql|markdown|text)?\s*",
        "",
        text,
        flags=re.I
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def extract_json(
    text
):
    text = strip_fences(
        text
    )

    start = text.find("{")

    if start < 0:
        raise ValueError(
            "No JSON object found."
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
                        start:
                        index + 1
                    ]

    raise ValueError(
        "Incomplete JSON object."
    )


def retry(
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
        f"{attempts} attempts: "
        f"{last_error}"
    )


# ============================================================
# METADATA
# ============================================================

def generate_metadata(
    model,
    category,
    topic
):
    raw = ollama_chat(
        model,
        "Return concise, valid JSON metadata only.",
        f"""
Topic:
{topic}

Category:
{category}

Return ONLY:

{{
  "slug": "lowercase-kebab-case",
  "title": "engaging but professional technical title",
  "commit_message": "natural conventional-style git commit message"
}}

No explanations.
No Markdown fences.
""",
        temperature=0.1,
        timeout_seconds=150
    )

    obj = json.loads(
        extract_json(raw)
    )

    slug = obj.get(
        "slug",
        ""
    )

    if not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*",
        slug
    ):
        raise ValueError(
            "Invalid slug."
        )

    return obj


# ============================================================
# ARTICLE
# ============================================================

def generate_article(
    model,
    category,
    topic,
    title
):
    article = ollama_chat(
        model,
        """
You are a senior software engineer writing practical learning notes.

Never invent employer/project experience,
production metrics,
links,
or citations.
""",
        f"""
Write a practical Markdown article.

Title:
{title}

Topic:
{topic}

Category:
{category}

Requirements:

- 380 to 600 words
- explain the concept clearly
- include a practical mini-POC angle
- include a section called "What I learned"
- include a section called "Key Takeaways"
- sound like a developer documenting an experiment
- no marketing language
- no external URLs
- no company/client references
- no fabricated production experience

Return article only.
""",
        temperature=0.35,
        timeout_seconds=360
    )

    word_count = len(
        article.split()
    )

    if word_count < 300:
        raise ValueError(
            f"Article too short: "
            f"{word_count} words."
        )

    return article


# ============================================================
# MINI POC
# ============================================================

def generate_poc(
    model,
    category,
    topic,
    title
):
    if category in {
        "dotnet",
        "efcore",
        "azure"
    }:
        language = "csharp"

    elif category == "sql":
        language = "sql"

    else:
        language = "python"

    code = ollama_chat(
        model,
        """
Create a small credible developer proof-of-concept.

Return code only.
No Markdown fences.
""",
        f"""
Create a focused mini-POC.

Title:
{title}

Topic:
{topic}

Category:
{category}

Language:
{language}

Requirements:

- approximately 18-55 lines
- demonstrate one core idea
- runnable or very close to runnable
- meaningful code, not pseudo-code
- comments only where useful
- no fake credentials
- no fake APIs
- no unnecessary dependencies

Return only code.
""",
        temperature=0.2,
        timeout_seconds=300
    )

    code = strip_fences(
        code
    )

    if len(
        code.splitlines()
    ) < 8:
        raise ValueError(
            "POC too short."
        )

    return (
        language,
        code
    )


# ============================================================
# POC README
# ============================================================

def generate_readme(
    model,
    topic,
    title,
    language
):
    return ollama_chat(
        model,
        """
Write concise README content
for a technical mini-POC.
""",
        f"""
Write 140-230 words of Markdown.

POC:
{title}

Topic:
{topic}

Language:
{language}

Use:

## What this demonstrates

## How it works

## How to run

## Things to try

No external links.
Return Markdown only.
""",
        temperature=0.25,
        timeout_seconds=220
    )


# ============================================================
# DIAGRAM
# ============================================================

def generate_diagram_steps(
    model,
    topic,
    title
):
    raw = ollama_chat(
        model,
        """
Return short architecture/process
steps only.
""",
        f"""
For this topic:

{topic}

Title:

{title}

Provide 4-6 concise flow steps
for a technical diagram.

Each step:
- 2 to 6 words
- one step per line

Do not number them.
Do not use bullets.
No explanation.
""",
        temperature=0.15,
        timeout_seconds=160
    )

    steps = []

    for line in raw.splitlines():

        line = re.sub(
            r"^[\-\*\d\.\)\s]+",
            "",
            line
        ).strip()

        if line:
            steps.append(
                line
            )

    return (
        steps[:6]
        or [
            "Input",
            "Process",
            "Validate",
            "Output"
        ]
    )


# ============================================================
# LINKEDIN CODE SNIPPET
# ============================================================

def snippet_from_code(
    code,
    max_lines=12
):
    """
    Avoid posting only imports/usings.

    Skip leading boilerplate and show
    the first useful implementation section.
    """

    lines = [
        line.rstrip()
        for line
        in code.strip().splitlines()
    ]

    if not lines:
        return ""

    skip_prefixes = (
        "import ",
        "from ",
        "using ",
        "#",
        "//",
        "namespace ",
        "package "
    )

    start = 0

    while start < len(lines):

        stripped = (
            lines[start]
            .strip()
        )

        if (
            not stripped
            or stripped.startswith(
                skip_prefixes
            )
        ):
            start += 1
            continue

        break

    if start >= len(lines):
        start = 0

    snippet = lines[
        start:
        start + max_lines
    ]

    meaningful = [
        line
        for line in snippet
        if line.strip()
    ]

    if len(
        meaningful
    ) < 5:

        snippet = lines[
            :max_lines
        ]

    return "\n".join(
        snippet
    ).strip()


# ============================================================
# GUARANTEED HASHTAGS
# ============================================================

def hashtags_for(
    category,
    topic
):
    base = {
        "ai": [
            "#GenerativeAI",
            "#AIEngineering",
            "#LLM",
            "#SoftwareEngineering"
        ],

        "dotnet": [
            "#DotNet",
            "#CSharp",
            "#BackendEngineering",
            "#SoftwareEngineering"
        ],

        "azure": [
            "#Azure",
            "#CloudComputing",
            "#DotNet",
            "#SoftwareEngineering"
        ],

        "system-design": [
            "#SystemDesign",
            "#SoftwareArchitecture",
            "#BackendEngineering",
            "#Scalability"
        ],

        "efcore": [
            "#EntityFrameworkCore",
            "#DotNet",
            "#CSharp",
            "#BackendEngineering"
        ],

        "sql": [
            "#SQL",
            "#SQLServer",
            "#Database",
            "#BackendEngineering"
        ]
    }

    tags = list(
        base.get(
            category,
            [
                "#SoftwareEngineering",
                "#BackendEngineering"
            ]
        )
    )

    topic_lower = (
        topic.lower()
    )

    keyword_tags = [
        (
            "rag",
            "#RAG"
        ),
        (
            "agent",
            "#AgenticAI"
        ),
        (
            "embedding",
            "#Embeddings"
        ),
        (
            "vector",
            "#VectorDatabase"
        ),
        (
            "fastapi",
            "#FastAPI"
        ),
        (
            "ollama",
            "#Ollama"
        ),
        (
            "prompt",
            "#PromptEngineering"
        ),
        (
            "azure",
            "#Azure"
        ),
        (
            "ef core",
            "#EntityFrameworkCore"
        ),
        (
            "sql",
            "#SQL"
        ),
        (
            "api",
            "#APIDesign"
        )
    ]

    for keyword, tag in keyword_tags:

        if (
            keyword in topic_lower
            and tag not in tags
        ):
            tags.insert(
                1,
                tag
            )

    return tags[:5]


# ============================================================
# LINKEDIN HUMAN BODY
# ============================================================

def generate_linkedin_body(
    model,
    category,
    topic,
    title
):
    body = ollama_chat(
        model,
        """
You write LinkedIn posts in the voice
of a hands-on software engineer.

The automation genuinely created a
small POC.

It is valid to say things such as:
- I explored...
- I tried...
- I built a small POC...
- One thing that stood out...

Never claim this was used at an employer
or in production unless explicitly told.

Use REAL line breaks.

Do NOT generate:
- hashtags
- URLs
- code
- headings
- Markdown code fences
""",
        f"""
Write ONLY the human narrative body
for a professional LinkedIn post.

Topic:
{topic}

Category:
{category}

Title:
{title}

Requirements:

- approximately 90-145 words
- engaging first 1-2 lines
- natural first-person engineering tone
- short paragraphs
- explain what was explored
- then exactly 3 concise takeaways
- every takeaway begins with •
- conclude with one practical takeaway sentence
- no hashtags
- no URLs
- no code
- no fake metrics
- no fake production claims
- no section title saying "LinkedIn Post"
- no literal \\n text

Return body only.
""",
        temperature=0.42,
        timeout_seconds=260
    )

    body = body.replace(
        "\\r\\n",
        "\n"
    ).replace(
        "\\n",
        "\n"
    )

    return strip_fences(
        body
    )


# ============================================================
# FINAL LINKEDIN COMPOSITION
# ============================================================

def compose_linkedin_post(
    category,
    topic,
    body,
    snippet,
    github_url,
    references,
    video
):
    """
    Final LinkedIn formatting is generated
    by Python rather than the LLM.

    This guarantees:
    - spacing
    - section labels
    - hashtags
    - references
    - POC link
    """

    sections = [
        body.strip()
    ]

    if snippet.strip():

        sections.append(
            "💻 Small POC\n\n"
            + snippet.strip()
        )

    sections.append(
        "✅ Key takeaway\n\n"
        "For me, the useful part of building a small POC is seeing where the concept actually holds up once it reaches code."
    )

    if references:

        reference_lines = []

        for reference in references[:2]:

            reference_title = (
                reference
                .get(
                    "title",
                    "Reference"
                )
                .strip()
            )

            url = (
                reference
                .get(
                    "url",
                    ""
                )
                .strip()
            )

            if url:

                reference_lines.append(
                    f"• {reference_title}\n"
                    f"  {url}"
                )

        if reference_lines:

            sections.append(
                "📚 References\n\n"
                + "\n\n".join(
                    reference_lines
                )
            )

    if (
        video
        and video.get("url")
    ):

        video_title = (
            video
            .get(
                "title",
                "Reference video"
            )
            .strip()
        )

        sections.append(
            "🎥 Reference video\n\n"
            f"{video_title}\n"
            f"{video['url']}"
        )

    sections.append(
        "🔗 Full runnable POC\n\n"
        + github_url
    )

    hashtag_block = " ".join(
        hashtags_for(
            category,
            topic
        )
    )

    sections.append(
        hashtag_block
    )

    return "\n\n".join(
        sections
    ).strip()


def generate_linkedin_post(
    model,
    category,
    topic,
    title,
    snippet,
    github_url,
    references,
    video
):
    body = generate_linkedin_body(
        model,
        category,
        topic,
        title
    )

    return compose_linkedin_post(
        category=category,
        topic=topic,
        body=body,
        snippet=snippet,
        github_url=github_url,
        references=references,
        video=video
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_package(
    article,
    linkedin_post,
    code,
    cfg
):
    banned_terms = [
        "bosch",
        "gcmmt",
        "customer master data workflow"
    ]

    combined = (
        article
        + "\n"
        + linkedin_post
        + "\n"
        + code
    ).lower()

    for term in banned_terms:

        if term in combined:

            raise ValueError(
                f"Blocked confidential term: "
                f"{term}"
            )

    if "\\n" in linkedin_post:

        raise ValueError(
            "LinkedIn post contains literal escaped newlines."
        )

    if "---SNIPPET---" in linkedin_post:

        raise ValueError(
            "Prompt marker leaked into LinkedIn post."
        )

    if "#" not in linkedin_post:

        raise ValueError(
            "LinkedIn post has no hashtags."
        )

    max_chars = cfg.get(
        "linkedin_max_chars",
        2850
    )

    if len(
        linkedin_post
    ) > max_chars:

        raise ValueError(
            f"LinkedIn post too long: "
            f"{len(linkedin_post)} characters."
        )

    article_min_words = cfg.get(
        "article_min_words",
        300
    )

    if len(
        article.split()
    ) < article_min_words:

        raise ValueError(
            "Article below minimum word count."
        )


# ============================================================
# CONTENT INDEX
# ============================================================

def update_index():
    rows = []

    if PUBLISHED.exists():

        folders = sorted(
            PUBLISHED.iterdir(),
            reverse=True
        )

        for folder in folders:

            article = (
                folder
                / "ARTICLE.md"
            )

            if (
                folder.is_dir()
                and article.exists()
            ):

                first_line = (
                    article
                    .read_text(
                        encoding="utf-8"
                    )
                    .splitlines()[0]
                )

                title = (
                    first_line
                    .lstrip("# ")
                    .strip()
                )

                relative_path = (
                    article
                    .relative_to(ROOT)
                    .as_posix()
                )

                rows.append(
                    f"- [{title}]"
                    f"({relative_path})"
                )

    output = (
        "# DevPulse Content Index\n\n"
    )

    if rows:

        output += (
            "\n".join(rows)
            + "\n"
        )

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

    if MANIFEST.exists():

        MANIFEST.unlink()

    force = (
        "--force"
        in sys.argv
    )

    cfg = load_json(
        DATA
        / "config.json"
    )

    topics = load_json(
        DATA
        / "topics.json"
    )

    state = load_json(
        DATA
        / "state.json"
    )

    state = refresh_week(
        state,
        cfg
    )

    save_json(
        DATA
        / "state.json",
        state
    )

    print(
        f"Week={state['week']} "
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

    model = cfg["model"]

    print(
        f"Selected "
        f"[{category}] "
        f"{topic}"
    )

    metadata = retry(
        "Metadata",
        lambda: generate_metadata(
            model,
            category,
            topic
        ),
        3
    )

    title = metadata[
        "title"
    ]

    slug = metadata[
        "slug"
    ]

    article = retry(
        "Article",
        lambda: generate_article(
            model,
            category,
            topic,
            title
        ),
        2
    )

    language, code = retry(
        "POC",
        lambda: generate_poc(
            model,
            category,
            topic,
            title
        ),
        3
    )

    readme = retry(
        "POC README",
        lambda: generate_readme(
            model,
            topic,
            title,
            language
        ),
        2
    )

    diagram_steps = retry(
        "Diagram steps",
        lambda: generate_diagram_steps(
            model,
            topic,
            title
        ),
        2
    )

    today = (
        utc_now()
        .date()
        .isoformat()
    )

    folder_name = (
        f"{today}-{slug}"
    )

    base = (
        PUBLISHED
        / folder_name
    )

    sample_dir = (
        base
        / "sample"
    )

    sample_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    github_repo = (
        cfg[
            "github_repo_url"
        ]
        .rstrip("/")
    )

    github_poc_url = (
        f"{github_repo}"
        f"/tree/main/"
        f"published/"
        f"{folder_name}"
        f"/sample"
    )

    resource_package = (
        find_references(
            category,
            topic
        )
    )

    references = (
        resource_package
        .get(
            "references",
            []
        )
    )

    video = (
        resource_package
        .get(
            "video"
        )
    )

    snippet = snippet_from_code(
        code,
        max_lines=12
    )

    linkedin_post = retry(
        "LinkedIn post",
        lambda: generate_linkedin_post(
            model=model,
            category=category,
            topic=topic,
            title=title,
            snippet=snippet,
            github_url=github_poc_url,
            references=references,
            video=video
        ),
        3
    )

    validate_package(
        article,
        linkedin_post,
        code,
        cfg
    )

    article_header = (
        f"# {title}\n\n"
        f"**Topic:** {topic}  \n"
        f"**Category:** {category}\n\n"
    )

    base.mkdir(
        parents=True,
        exist_ok=True
    )

    (
        base
        / "ARTICLE.md"
    ).write_text(
        article_header
        + article.strip()
        + "\n",
        encoding="utf-8"
    )

    if language == "csharp":

        code_filename = (
            "Program.cs"
        )

    elif language == "python":

        code_filename = (
            "main.py"
        )

    elif language == "sql":

        code_filename = (
            "demo.sql"
        )

    else:

        code_filename = (
            "example.txt"
        )

    (
        sample_dir
        / code_filename
    ).write_text(
        code.strip()
        + "\n",
        encoding="utf-8"
    )

    (
        sample_dir
        / "README.md"
    ).write_text(
        readme.strip()
        + "\n",
        encoding="utf-8"
    )

    (
        base
        / "REFERENCES.json"
    ).write_text(
        json.dumps(
            resource_package,
            indent=2
        ),
        encoding="utf-8"
    )

    image_path = (
        base
        / "diagram.png"
    )

    generate_diagram(
        title,
        diagram_steps,
        image_path
    )

    LINKEDIN.mkdir(
        exist_ok=True
    )

    linkedin_file = (
        LINKEDIN
        / f"{folder_name}.md"
    )

    linkedin_file.write_text(
        linkedin_post.strip()
        + "\n",
        encoding="utf-8"
    )

    update_index()

    current_run_key = (
        f"{weekday()}:{slot()}"
    )

    if not force:

        if current_run_key not in state.get(
            "published_this_week",
            []
        ):

            state.setdefault(
                "published_this_week",
                []
            ).append(
                current_run_key
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
        DATA
        / "state.json",
        state
    )

    (
        ROOT
        / ".devpulse_commit_message"
    ).write_text(
        metadata[
            "commit_message"
        ].strip(),
        encoding="utf-8"
    )

    manifest = {
        "generated": True,
        "category": category,
        "topic": topic,
        "title": title,
        "slug": slug,
        "linkedin_file":
            linkedin_file
            .relative_to(ROOT)
            .as_posix(),
        "image_file":
            image_path
            .relative_to(ROOT)
            .as_posix(),
        "github_poc_url":
            github_poc_url
    }

    MANIFEST.write_text(
        json.dumps(
            manifest,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"Generated package: "
        f"{base}"
    )

    print(
        f"LinkedIn file: "
        f"{linkedin_file}"
    )

    print(
        f"Diagram: "
        f"{image_path}"
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
