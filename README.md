# project-registry

A Claude Code skill that manages a **personal project registry** with per-project **AI-readable development logs** — list, create, delete, save, resume and health-check all your projects from one menu.

> Chinese docs: [README.zh-CN.md](README.zh-CN.md)

## Why this skill

Claude Code loses context between sessions. You start a project, work for a while, come back next week — and Claude has no idea what happened, what to do next, or even which projects exist. `project-registry` fixes this with:

- **One registry**: every project registered in a single `~/projects/PROJECTS.json`, with auto sequence management
- **AI-readable logs**: each project has a `CLAUDE.md` (auto-loaded by Claude every session) recording status, decisions, todos and **prioritized next actions**
- **Session resume**: entering a project recalls last progress and asks what to continue from — no more cold starts
- **Safety by default**: automatic backups with rotation (10 per type), `git init` per project, confirmation before any deletion

## Features

| Feature | What it does |
|:---|:---|
| 📋 Project registry | CRUD + search + stats over `~/projects/PROJECTS.json` |
| 🧭 Session resume | Entering a project → recall last progress → confirm what to continue |
| 💾 Auto-save on exit | Save/exit **forces** CLAUDE.md update with prioritized next actions |
| 🔍 MD health check | Batch-verify `CLAUDE.md` + `.git` exist for every registered project |
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
3. Work in the project. When done: "save project" or "exit"
4. Save/exit auto-updates CLAUDE.md with progress + prioritized next actions
```

New project structure:

```
~/projects/
  PROJECTS.json            # registry (single source of truth)
  <project-key>/
    README.md              # for humans: background & scope
    CLAUDE.md              # for AI: status, decisions, todos, next actions
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
- Design decisions: [docs/adr/](docs/adr/)

## License

[MIT](LICENSE)
