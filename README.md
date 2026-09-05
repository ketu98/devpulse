# DevPulse

DevPulse is an autonomous developer-presence engine that generates practical technical learning content and small code artifacts using a local Ollama model running inside GitHub Actions.

## What it does

- Randomly schedules exactly 3 or 4 publish days each ISO week.
- Uses Ollama + `qwen3:4b-instruct` inside a GitHub-hosted runner.
- Picks an unused topic from a curated .NET/backend-oriented topic bank.
- Generates:
  - a technical Markdown article,
  - one or more practical code/artifact files,
  - a recruiter-friendly LinkedIn draft.
- Blocks known confidential/project terms.
- Builds generated .NET projects when a `.csproj` is present.
- Updates the content index and topic state.
- Commits and pushes the generated work automatically.

## Architecture

GitHub Schedule → DevPulse Scheduler → Ollama/Qwen → Validator → Artifact Writer → optional `dotnet build` → Git commit/push

## One-time setup

1. Create a **public GitHub repository** for DevPulse.
2. Push this repository.
3. In **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**.
4. Open the **Actions** tab and enable workflows if GitHub asks.
5. Run `DevPulse Autonomous Publisher` manually once with `force_publish=true` to test it.

After that, no machine needs to stay online.

## Schedule behavior

The workflow wakes up in three daily time windows. At the start of each new ISO week, DevPulse randomly chooses 3 or 4 distinct weekdays and randomly assigns one of those time windows to each selected day. Only those exact day/time slots publish.

The generated schedule is stored in `data/state.json`, which is committed back to the repository so every new ephemeral GitHub runner remembers the same weekly plan.

## Topic mix

The default weighting is:

- .NET: 35%
- EF Core: 20%
- SQL: 15%
- Azure: 15%
- System Design: 10%
- AI: 5%

Edit `data/config.json` to change this.

## Important note about LinkedIn

`linkedin-queue/` contains ready-to-post drafts. DevPulse V1 deliberately does not use browser automation to log into LinkedIn. Automatic LinkedIn publishing should only be added through an official supported API/integration.

## Local test

```bash
pip install -r requirements.txt
ollama serve
ollama pull qwen3:4b-instruct
python src/devpulse.py --force
```

## Safety

DevPulse performs basic validation and rejects content containing selected project/company identifiers. Treat the topic bank and validation rules as configuration, not as a complete security boundary.
