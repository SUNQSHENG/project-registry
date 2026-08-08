# project-registry

A Claude Code skill that manages a **personal project registry** with per-project **AI-readable development logs** — list, create, delete, save, resume, audit and roll back all your projects from one menu.

> Chinese docs: [README.zh-CN.md](README.zh-CN.md)

## Why this skill

Claude Code loses context between sessions. You start a project, work for a while, come back next week — and Claude has no idea what happened, what to do next, or even which projects exist. `project-registry` fixes this with:

- **One registry**: every project registered in a single `~/projects/PROJECTS.json`, with auto sequence management
- **AI-readable logs**: each project has a `CLAUDE.md` (auto-loaded by Claude every session) recording status, decisions (with mandatory reasons), todos and **prioritized next actions**
- **Session resume**: entering a project recalls last progress and asks what to continue from — no more cold starts
- **Decision attribution**: ask "why X" and get the decision timeline with reasons and impact
- **Auto-save**: hooks keep data safe (layer 1) and optionally keep CLAUDE.md fresh (layer 2)
- **Safety by default**: automatic backups with rotation (10 per type), `git init` per project, confirmation before any deletion, rollback with diff confirmation

## Features

| Feature | What it does |
|:---|:---|
| 📋 Project registry | CRUD + search + stats over `~/projects/PROJECTS.json` |
| 🧭 Session resume | Entering a project → recall last progress → confirm what to continue |
| 📜 Decision discipline | Every decision records WHY (mandatory) — traceable months later |
| 🔎 Decision attribution | "Why X" → decision timeline + reason chain + status + impact |
| 💾 Auto-save on exit | Save/exit **forces** CLAUDE.md update with prioritized next actions |
| 🔁 Auto-save (hooks) | Layer 1: transcript snapshot + backup/commit (silent, zero deps) |
| 🔁 Auto-summary (API) | Layer 2: conversation auto-extracted into CLAUDE.md (optional) |
| 🔍 MD health check | Batch-verify `CLAUDE.md` + `.git` exist for every registered project |
| ↩️ Version rollback | CLAUDE.md / project files / registry — diff confirm + new commit |
| 🛡️ Backup rotation | PROJECTS.json / CLAUDE.md / SKILL.md backups, keep latest 10 each |
| 📁 Optional doc skeleton | Code projects: optional `docs/SPEC.md` + `DESIGN.md` per feature |
| 🌍 Universal | No hardcoded paths, works for business and code projects alike |

## Install

### Option 1: npx skills (recommended)

```bash
npx skills add SUNQSHENG/project-registry
# or install globally
npx skills add SUNQSHENG/project-registry -g
```

### Option 2: Claude Code plugin marketplace

```
/plugin marketplace add SUNQSHENG/project-registry
/plugin install project-registry@project-registry
```

### Option 3: Manual

```bash
git clone https://github.com/SUNQSHENG/project-registry
cp -r project-registry/skills/project-registry ~/.claude/skills/
```

Restart Claude Code. Then type "list projects" — or simply use `/project-registry`.

## Quick start

```text
1. Trigger the skill: "list projects" / /project-registry
2. Menu shows all projects with numbers:
   - type a number (1-99) → open that project (session resume kicks in)
   - N → new project     D → delete project     C → health check
3. Work in the project. Auto-save runs silently in the background — you never need to "remember to save"
4. When done: "save project" or "exit" (forces a full CLAUDE.md review)
5. Later: "why X" → decision attribution · "rollback" → restore a version · "check projects" → health check
```

New project structure:

```
~/projects/
  PROJECTS.json            # registry (single source of truth)
  <project-key>/
    README.md              # for humans: background & scope
    CLAUDE.md              # for AI: status, decisions, todos, next actions
    .memory/               # auto-save transcripts (gitignored, never committed)
    .git/                  # git init automatically (CLAUDE.md must be at .git level)
```

`CLAUDE.md` is the heart of it — Claude Code auto-loads it every session, so long-running projects never lose context.

## Auto-save (hooks, silent)

Two layers, fully silent, run only inside `~/projects/` project directories:

**Layer 1 - Mechanical snapshot (zero dependencies, on by default)**

| Hook | Action |
|:---|:---|
| `Stop` (after every response) | Sync transcript to `<project>/.memory/` (second-level) |
| `SessionEnd` | Backup CLAUDE.md (rotation of 10) + git commit |

`.memory/` contains raw conversation - it is **gitignored** and never committed. Layer 1 keeps data safe even if you kill the terminal: nothing is ever lost.

**Enable Layer 1** (one-time, add hooks to `~/.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "always",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/skills/project-registry/scripts/transcript-sync.py" },
          { "type": "command", "command": "python ~/.claude/skills/project-registry/scripts/auto-summary.py" }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "always",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/skills/project-registry/scripts/session-end.py" }
        ]
      }
    ]
  }
}
```

On first use the skill will ask whether you want to enable auto-save (skippable, asked once).

**Layer 2 - Auto-summary (optional, enabled by configuring an API key)**

Extracts progress / decisions / todos / next actions from the conversation and merges them into CLAUDE.md automatically (throttled: >=10 new messages or >=10 minutes). Works with **any OpenAI-compatible API** - bring your own key:

```bash
# any OpenAI-compatible API works (DeepSeek / OpenAI / Qwen / local Ollama - same shape)
export PR_API_BASE_URL=https://your-provider.example.com/v1   # <-- replace with your provider base URL
export PR_API_KEY=sk-your-key                                 # <-- your own key
export PR_API_MODEL=your-model                                # <-- e.g. deepseek-v4-flash / gpt-4o-mini / qwen-plus
```

Without a key, the skill still gives you Layer 1 (data safety) plus all core features; with a key you additionally get auto-fresh CLAUDE.md. On first use the skill asks whether you want to configure a key (skippable, asked once). Conversation is only sent to the endpoint you configure.

## Example registry

See [examples/PROJECTS.example.json](examples/PROJECTS.example.json) for a sample registry with fictional projects.

## Development

- `skills/project-registry/SKILL.md` — the skill itself (self-contained, no dependencies)
- `skills/project-registry/scripts/` — auto-save hooks (transcript-sync / auto-summary / session-end)
- Design decisions: [docs/adr/](docs/adr/)

## License

[MIT](LICENSE)
