from __future__ import annotations
import datetime as dt
import json, os, random, re, subprocess, sys, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PUBLISHED = ROOT / "published"
LINKEDIN = ROOT / "linkedin-queue"

def load_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def save_json(p, obj): Path(p).write_text(json.dumps(obj, indent=2), encoding="utf-8")

def iso_week():
    now = dt.datetime.now(dt.timezone.utc)
    y, w, _ = now.isocalendar()
    return f"{y}-W{w:02d}"

def weekday():
    return dt.datetime.now(dt.timezone.utc).strftime("%A")

def slot():
    # Workflow wakes at 04:17, 10:43 and 15:29 UTC.
    # Match the closest expected trigger window.
    h = dt.datetime.now(dt.timezone.utc).hour
    if h < 8:
        return "morning"
    if h < 13:
        return "afternoon"
    return "evening"

def refresh_week(state, cfg):
    wk = iso_week()
    if state.get("week") == wk:
        return state
    target = random.randint(cfg["min_runs_per_week"], cfg["max_runs_per_week"])
    ordered = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    days = random.sample(ordered, target)
    slots = ["morning", "afternoon", "evening"]
    schedule = [
        {"day": day, "slot": random.choice(slots)}
        for day in sorted(days, key=ordered.index)
    ]
    state.update({
        "week": wk,
        "target_runs": target,
        "schedule": schedule,
        "published_this_week": []
    })
    return state

def should_publish(state, force=False):
    if force:
        return True
    today, current_slot = weekday(), slot()
    key = f"{today}:{current_slot}"
    scheduled = {f"{x['day']}:{x['slot']}" for x in state.get("schedule", [])}
    return key in scheduled and key not in state["published_this_week"]

def weighted_category(cfg):
    items = list(cfg["category_weights"].items())
    cats = [x[0] for x in items]
    weights = [x[1] for x in items]
    return random.choices(cats, weights=weights, k=1)[0]

def choose_topic(topics, state, cfg):
    unused = []
    for cat, vals in topics.items():
        for topic in vals:
            if topic not in state["used_topics"]:
                unused.append((cat, topic))
    if not unused:
        raise RuntimeError("Topic bank exhausted.")
    preferred = weighted_category(cfg)
    candidates = [x for x in unused if x[0] == preferred] or unused
    return random.choice(candidates)

def ollama_chat(model, system, prompt, temperature=0.5):
    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role":"system","content":system},
            {"role":"user","content":prompt}
        ],
        "options":{"temperature":temperature}
    }
    r = requests.post(url, json=payload, timeout=900)
    r.raise_for_status()
    return r.json()["message"]["content"]

def strip_fences(s):
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

def generation_prompt(category, topic):
    return f"""
Create one practical developer-learning contribution on the topic: {topic}
Category: {category}

Audience: recruiters and experienced .NET/backend engineers.
The work must be educational, technically careful, original, and not pretend to come from a real employer/project.

Return ONLY valid JSON with this exact shape:
{{
  "slug": "kebab-case-slug",
  "title": "human title",
  "commit_message": "conventional commit style message",
  "article_markdown": "500-900 word Markdown article",
  "linkedin_post": "120-220 word professional LinkedIn post with 3-5 hashtags",
  "code_files": [
    {{"path":"Program.cs","content":"..."}},
    {{"path":"README.md","content":"..."}}
  ]
}}

Rules:
- Prefer runnable C#/.NET samples for dotnet/efcore/azure topics.
- For SQL, include a .sql sample where useful.
- For system-design or AI, code is optional but include a practical artifact.
- Never mention Bosch, GCMMT, clients, internal systems, confidential data, or fabricated production metrics.
- Do not invent citations or external links.
- Make the LinkedIn post useful even without clicking GitHub.
- Do not include Markdown fences around the overall JSON.
"""

def validate_payload(p):
    required = ["slug","title","commit_message","article_markdown","linkedin_post","code_files"]
    for k in required:
        if k not in p:
            raise ValueError(f"Missing {k}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["slug"]):
        raise ValueError("Invalid slug")
    if len(p["article_markdown"].split()) < 350:
        raise ValueError("Article too short")
    banned = ["bosch", "gcmmt", "customer master data workflow"]
    blob = json.dumps(p).lower()
    if any(x in blob for x in banned):
        raise ValueError("Potential confidential/project reference")
    if not isinstance(p["code_files"], list) or not p["code_files"]:
        raise ValueError("No code/artifact files")
    for f in p["code_files"]:
        path = Path(f["path"])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe output path")

def write_output(category, topic, p):
    date = dt.datetime.now(dt.timezone.utc).date().isoformat()
    base = PUBLISHED / f"{date}-{p['slug']}"
    base.mkdir(parents=True, exist_ok=True)
    header = f"# {p['title']}\n\n**Topic:** {topic}  \n**Category:** {category}\n\n"
    (base / "ARTICLE.md").write_text(header + p["article_markdown"].strip() + "\n", encoding="utf-8")
    sample = base / "sample"
    sample.mkdir(exist_ok=True)
    for f in p["code_files"]:
        dest = sample / f["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f["content"], encoding="utf-8")
    LINKEDIN.mkdir(exist_ok=True)
    (LINKEDIN / f"{date}-{p['slug']}.md").write_text(p["linkedin_post"].strip()+"\n", encoding="utf-8")
    return base

def maybe_dotnet_build(base):
    projs = list(base.rglob("*.csproj"))
    if not projs:
        return
    for proj in projs:
        subprocess.run(["dotnet","build",str(proj),"-c","Release","--nologo"], check=True)

def update_index():
    rows = []
    for p in sorted(PUBLISHED.iterdir(), reverse=True) if PUBLISHED.exists() else []:
        if p.is_dir() and (p/"ARTICLE.md").exists():
            title = (p/"ARTICLE.md").read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
            rows.append(f"- [{title}]({p.as_posix()}/ARTICLE.md)")
    (ROOT/"CONTENT_INDEX.md").write_text("# DevPulse Content Index\n\n" + "\n".join(rows) + "\n", encoding="utf-8")

def main():
    force = "--force" in sys.argv
    cfg = load_json(DATA/"config.json")
    topics = load_json(DATA/"topics.json")
    state = refresh_week(load_json(DATA/"state.json"), cfg)
    save_json(DATA/"state.json", state)

    print(f"Week {state['week']} target={state['target_runs']} schedule={state.get('schedule', [])}")
    if not should_publish(state, force):
        print("No publication scheduled for today.")
        return 0

    category, topic = choose_topic(topics, state, cfg)
    print(f"Selected: [{category}] {topic}")

    system = """You are DevPulse, a careful senior backend engineering educator.
Return strict JSON only. Favor correctness and practical examples over hype."""
    raw = ollama_chat(cfg["model"], system, generation_prompt(category, topic))
    try:
        payload = json.loads(strip_fences(raw))
        validate_payload(payload)
    except Exception as e:
        print("Initial generation invalid:", e)
        repair = f"""Repair the following output so it is valid JSON and satisfies the requested schema.
Do not add commentary. Original topic: {topic}
Error: {e}
OUTPUT:
{raw}"""
        raw = ollama_chat(cfg["model"], system, repair, 0.2)
        payload = json.loads(strip_fences(raw))
        validate_payload(payload)

    base = write_output(category, topic, payload)
    maybe_dotnet_build(base)
    update_index()

    run_key = f"{weekday()}:{slot()}"
    if run_key not in state["published_this_week"]:
        state["published_this_week"].append(run_key)
    if topic not in state["used_topics"]:
        state["used_topics"].append(topic)
    save_json(DATA/"state.json", state)

    Path(ROOT/".devpulse_commit_message").write_text(payload["commit_message"].strip(), encoding="utf-8")
    print(f"Published {base}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
