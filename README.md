# DevPulse V3

DevPulse is an autonomous personal developer-branding pipeline built around GitHub Actions + Ollama.

Each successful publishing run creates:

- a practical technical article,
- a small runnable POC,
- a short code snippet embedded in a human-style LinkedIn post,
- verified technical references retrieved from public APIs,
- a relevant YouTube reference (exact video when a YouTube API key is configured),
- an automatically rendered technical diagram,
- a specific GitHub link to the full POC,
- contextual hashtags,
- an organic image post on the authenticated personal LinkedIn profile.

## Topic weighting

- AI / GenAI — 30%
- .NET / C# — 25%
- Azure — 15%
- System Design — 10%
- EF Core — 10%
- SQL — 10%

## Required GitHub Actions secrets

Repository → Settings → Secrets and variables → Actions:

- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_ID`

Optional but recommended:

- `YOUTUBE_API_KEY`

Without `YOUTUBE_API_KEY`, DevPulse includes a relevant YouTube search link rather than inventing a specific video.

## How references work

Ollama is **not allowed to invent URLs**.

DevPulse currently retrieves:
- Microsoft Learn results from Microsoft's public Learn search API.
- arXiv results for AI/GenAI topics.
- YouTube results through the official YouTube Data API when configured.

The fetched references are also stored in each published package as `REFERENCES.json`.

## LinkedIn media

DevPulse generates `diagram.png`, initializes an image upload through LinkedIn's Images API, uploads the PNG, then attaches the resulting image URN to the organic Posts API request.

## Random schedule

GitHub Actions wakes in three daily windows. At the beginning of an ISO week, DevPulse selects 3 or 4 different weekdays and one random time window for each.

Manual `force_publish=true` tests do not consume one of the weekly scheduled slots.

## Important

The LinkedIn access token is not committed to the repository. Keep it only in GitHub Actions Secrets.

LinkedIn access tokens can expire, so a future reauthorization may be required depending on the token issued to the app.

## Local test

```bash
pip install -r requirements.txt
ollama serve
ollama pull qwen3:4b-instruct
python src/devpulse.py --force
```

For LinkedIn publishing locally, set the two LinkedIn environment variables before running:

```bash
python src/linkedin_publish.py
```
