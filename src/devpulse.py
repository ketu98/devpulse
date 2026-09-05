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
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


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


def refresh_week(state, cfg):
    current_week = iso_week()
    if state.get("week") == current_week:
        return state

    ordered = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    target = random.randint(cfg["min_runs_per_week"], cfg["max_runs_per_week"])
    days = random.sample(ordered, target)
    slots = ["morning", "afternoon", "evening"]

    state.update({
        "week": current_week,
        "target_runs": target,
        "schedule": [
            {"day": d, "slot": random.choice(slots)}
            for d in sorted(days, key=ordered.index)
        ],
        "published_this_week": []
    })
    return state


def should_publish(state, force=False):
    if force:
        return True
    key = f"{weekday()}:{slot()}"
    scheduled = {f"{x['day']}:{x['slot']}" for x in state.get("schedule", [])}
    return key in scheduled and key not in state.get("published_this_week", [])


def weighted_category(cfg):
    pairs = list(cfg["category_weights"].items())
    return random.choices(
        [p[0] for p in pairs],
        weights=[p[1] for p in pairs],
        k=1
    )[0]


def choose_topic(topics, state, cfg):
    used = set(state.get("used_topics", []))
    unused = [
        (category, topic)
        for category, values in topics.items()
        for topic in values
        if topic not in used
    ]
    if not unused:
        raise RuntimeError("Topic bank exhausted.")

    preferred = weighted_category(cfg)
    candidates = [x for x in unused if x[0] == preferred] or unused
    return random.choice(candidates)


def ollama_chat(model, system, prompt, temperature=0.3, timeout_seconds=360):
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "options": {
            "temperature": temperature,
            "num_predict": 1200
        }
    }
    r = requests.post(url, json=payload, timeout=timeout_seconds)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def strip_fences(text):
    text = text.strip()
    text = re.sub(r"^```(?:json|python|csharp|cs|sql|markdown|text)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_json(text):
    text = strip_fences(text)
    start = text.find("{")
    if start < 0:
        raise ValueError("No JSON object found.")

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
    raise ValueError("Incomplete JSON object.")


def retry(label, fn, attempts=3):
    last = None
    for i in range(1, attempts + 1):
        try:
            print(f"{label} attempt {i}/{attempts}")
            return fn()
        except Exception as ex:
            last = ex
            print(f"{label} failed: {ex}")
    raise RuntimeError(f"{label} failed after {attempts} attempts: {last}")


def generate_metadata(model, category, topic):
    raw = ollama_chat(
        model,
        "Return concise, valid JSON metadata only.",
        f"""
Topic: {topic}
Category: {category}

Return ONLY:
{{
  "slug": "lowercase-kebab-case",
  "title": "engaging but professional technical title",
  "commit_message": "natural conventional-style git commit message"
}}
""",
        temperature=0.1,
        timeout_seconds=150
    )
    obj = json.loads(extract_json(raw))
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", obj.get("slug","")):
        raise ValueError("Invalid slug")
    return obj


def generate_article(model, category, topic, title):
    text = ollama_chat(
        model,
        """You are a senior software engineer writing practical learning notes.
Never invent employer/project experience, metrics, links or citations.""",
        f"""
Write a practical Markdown article titled "{title}" about "{topic}" ({category}).

Requirements:
- 380-600 words
- explain the concept clearly
- include a practical mini-POC angle
- include a short 'What I learned' section
- include 'Key Takeaways'
- sound like a developer documenting an experiment, not marketing copy
- no external URLs; references are inserted separately
- no confidential companies/projects
Return article only.
""",
        temperature=0.35,
        timeout_seconds=360
    )
    if len(text.split()) < 300:
        raise ValueError(f"Article too short: {len(text.split())} words")
    return text


def generate_poc(model, category, topic, title):
    language = "csharp" if category in {"dotnet","efcore","azure"} else "sql" if category == "sql" else "python"
    code = strip_fences(ollama_chat(
        model,
        "Create a small, credible developer proof-of-concept. Return code only.",
        f"""
Create a focused mini-POC for:
Title: {title}
Topic: {topic}
Category: {category}
Preferred language: {language}

Requirements:
- 18-55 lines
- one core idea
- runnable or very close to runnable
- comments only where useful
- no fake APIs/secrets
- avoid unnecessary packages
Return code only, no markdown fences.
""",
        temperature=0.2,
        timeout_seconds=300
    ))
    if len(code.splitlines()) < 8:
        raise ValueError("POC too short")
    return language, code


def generate_readme(model, topic, title, language):
    return ollama_chat(
        model,
        "Write concise README content for a technical mini-POC.",
        f"""
Write 140-230 words of Markdown for the POC "{title}" about "{topic}" in {language}.
Use sections:
## What this demonstrates
## How it works
## How to run
## Things to try
No external links. Return Markdown only.
""",
        temperature=0.25,
        timeout_seconds=220
    )


def generate_diagram_steps(model, topic, title):
    raw = ollama_chat(
        model,
        "Return short architecture/process steps only.",
        f"""
For the topic "{topic}" and title "{title}", provide 4-6 concise flow steps for a technical diagram.
Each step must be 2-6 words.
Return one step per line.
No numbering, bullets, explanations or markdown.
""",
        temperature=0.15,
        timeout_seconds=160
    )
    steps = []
    for line in raw.splitlines():
        line = re.sub(r"^[\-\*\d\.\)\s]+", "", line).strip()
        if line:
            steps.append(line)
    return steps[:6] or ["Input", "Process", "Validate", "Output"]


def _snippet_from_code(code, max_lines=14):
    lines = [x.rstrip() for x in code.strip().splitlines()]
    # Prefer meaningful non-empty lines, while preserving order.
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines])


def generate_linkedin_post(model, category, topic, title, snippet, github_url, refs, video):
    ref_titles = "\n".join(
        f"- {r['source']}: {r['title']} | {r['url']}"
        for r in refs
    ) or "- No article reference available"

    video_text = (
        f"{video.get('title','Reference video')} | {video.get('url','')}"
        if video else "No video available"
    )

    post = ollama_chat(
        model,
        """You write LinkedIn posts in the voice of a hands-on software engineer.
The post must feel personally written after doing a small POC, but never fabricate production experience.
Use genuine line breaks, not literal \\n characters.""",
        f"""
Create a polished LinkedIn post.

Topic: {topic}
Category: {category}
Title: {title}

The automation genuinely created a small POC, so you may naturally say:
"I explored...", "I built a small POC...", "I tried...", "One thing that stood out..."
Do NOT claim it was used at work or in production.

Use this exact practical snippet:
---SNIPPET---
{snippet}
---END SNIPPET---

Specific GitHub POC:
{github_url}

Verified references:
{ref_titles}

Reference video:
{video_text}

STYLE:
- engaging 1-2 line hook
- first-person, natural engineering tone
- short paragraphs
- 2-4 bullets using • where useful
- introduce the code as "Small POC" or similar
- include the code snippet as plain text (do NOT use Markdown ``` fences)
- after the snippet, include a short practical takeaway
- then 📚 References with the supplied URLs
- then 🎥 Reference video with the supplied URL
- then 💻 Full runnable POC with the supplied GitHub URL
- finish with 3-5 relevant hashtags
- 160-260 words excluding URLs/code
- no fake metrics
- no invented references
- no generic "In today's fast-paced world" language
- no heading saying "LinkedIn Post"
- REAL new lines only, never the characters backslash+n
Return only the post.
""",
        temperature=0.45,
        timeout_seconds=300
    )

    post = post.replace("\\r\\n", "\n").replace("\\n", "\n")
    post = strip_fences(post)
    return post


def validate_package(article, linkedin_post, code, cfg):
    banned = ["bosch", "gcmmt", "customer master data workflow"]
    combined = f"{article}\n{linkedin_post}\n{code}".lower()
    for term in banned:
        if term in combined:
            raise ValueError(f"Blocked confidential term: {term}")

    if "\\n" in linkedin_post:
        raise ValueError("LinkedIn post contains literal escaped newlines")

    if len(linkedin_post) > cfg.get("linkedin_max_chars", 2850):
        raise ValueError(f"LinkedIn post too long: {len(linkedin_post)} characters")

    if len(article.split()) < cfg.get("article_min_words", 300):
        raise ValueError("Article below minimum word count")


def ext_for(language):
    return {"csharp":"cs", "python":"py", "sql":"sql"}.get(language, "txt")


def update_index():
    rows = []
    for folder in sorted(PUBLISHED.iterdir(), reverse=True) if PUBLISHED.exists() else []:
        article = folder / "ARTICLE.md"
        if folder.is_dir() and article.exists():
            title = article.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
            rel = article.relative_to(ROOT).as_posix()
            rows.append(f"- [{title}]({rel})")
    (ROOT/"CONTENT_INDEX.md").write_text(
        "# DevPulse Content Index\n\n" + ("\n".join(rows) if rows else "_No content published yet._") + "\n",
        encoding="utf-8"
    )


def main():
    if MANIFEST.exists():
        MANIFEST.unlink()

    force = "--force" in sys.argv
    cfg = load_json(DATA/"config.json")
    topics = load_json(DATA/"topics.json")
    state = refresh_week(load_json(DATA/"state.json"), cfg)
    save_json(DATA/"state.json", state)

    print(f"Week={state['week']} target={state['target_runs']} schedule={state.get('schedule', [])}")

    if not should_publish(state, force):
        print("No publication scheduled for this run.")
        return 0

    category, topic = choose_topic(topics, state, cfg)
    model = cfg["model"]
    print(f"Selected [{category}] {topic}")

    metadata = retry("Metadata", lambda: generate_metadata(model, category, topic), 3)
    title = metadata["title"]
    slug = metadata["slug"]

    article = retry("Article", lambda: generate_article(model, category, topic, title), 2)
    language, code = retry("POC", lambda: generate_poc(model, category, topic, title), 3)
    readme = retry("POC README", lambda: generate_readme(model, topic, title, language), 2)
    diagram_steps = retry("Diagram steps", lambda: generate_diagram_steps(model, topic, title), 2)

    today = utc_now().date().isoformat()
    folder_name = f"{today}-{slug}"
    base = PUBLISHED / folder_name
    sample_dir = base / "sample"
    sample_dir.mkdir(parents=True, exist_ok=True)

    github_repo = cfg["github_repo_url"].rstrip("/")
    github_poc_url = f"{github_repo}/tree/main/published/{folder_name}/sample"

    references = find_references(category, topic)
    refs = references.get("references", [])
    video = references.get("video")

    snippet = _snippet_from_code(code, max_lines=14)
    linkedin_post = retry(
        "LinkedIn post",
        lambda: generate_linkedin_post(
            model, category, topic, title, snippet, github_poc_url, refs, video
        ),
        3
    )

    validate_package(article, linkedin_post, code, cfg)

    article_header = (
        f"# {title}\n\n"
        f"**Topic:** {topic}  \n"
        f"**Category:** {category}\n\n"
    )
    (base/"ARTICLE.md").write_text(article_header + article.strip() + "\n", encoding="utf-8")

    code_file = sample_dir / (
        "Program.cs" if language == "csharp"
        else "main.py" if language == "python"
        else "demo.sql" if language == "sql"
        else "example.txt"
    )
    code_file.write_text(code.strip()+"\n", encoding="utf-8")
    (sample_dir/"README.md").write_text(readme.strip()+"\n", encoding="utf-8")

    # Save references as transparent provenance.
    (base/"REFERENCES.json").write_text(json.dumps(references, indent=2), encoding="utf-8")

    image_path = base / "diagram.png"
    generate_diagram(title, diagram_steps, image_path)

    LINKEDIN.mkdir(exist_ok=True)
    linkedin_file = LINKEDIN / f"{folder_name}.md"
    linkedin_file.write_text(linkedin_post.strip()+"\n", encoding="utf-8")

    update_index()

    run_key = f"{weekday()}:{slot()}"
    if not force and run_key not in state.get("published_this_week", []):
        state.setdefault("published_this_week", []).append(run_key)
    if topic not in state.get("used_topics", []):
        state.setdefault("used_topics", []).append(topic)
    save_json(DATA/"state.json", state)

    (ROOT/".devpulse_commit_message").write_text(metadata["commit_message"].strip(), encoding="utf-8")

    manifest = {
        "generated": True,
        "category": category,
        "topic": topic,
        "title": title,
        "slug": slug,
        "linkedin_file": linkedin_file.relative_to(ROOT).as_posix(),
        "image_file": image_path.relative_to(ROOT).as_posix(),
        "github_poc_url": github_poc_url
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Generated package: {base}")
    print(f"LinkedIn file: {linkedin_file}")
    print(f"Diagram: {image_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
