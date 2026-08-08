# project-registry

**Multi-project management for personal developers using Claude Code.** One registry for all your projects, session resume with full context, and data you can never lose — silent by design, active on demand.

> 中文文档：[README.zh-CN.md](README.zh-CN.md)

## Why this skill

Personal developers juggle several projects at once — work, side projects, learning. Claude Code loses context between sessions: you come back next week and Claude has no idea what happened, what to do next, or even which projects exist. `project-registry` fixes this:

| Problem | Solution |
|:---|:---|
| "Which projects do I even have?" | **One registry** — every project in a single `~/projects/PROJECTS.json`, with CRUD, search and stats |
| "What did I do last time?" | **AI-readable logs** — each project has a `CLAUDE.md` (auto-loaded every session) with status, decisions, todos and **prioritized next actions** |
| "Why did I choose X?" | **Decision attribution** — "why X" returns the decision timeline with reasons and impact |
| "I forgot to save" | **Auto-save hooks** — transcript snapshots every response, backup + commit on exit (Layer 1, zero dependencies) |
| "CLAUDE.md went stale" | **Fresh-keeping (optional)** — an LLM of your choice extracts progress into CLAUDE.md (Layer 2) |
| "I broke something" | **Rollback** — diff-confirmed version restore for CLAUDE.md, files and the registry |

**Design philosophy: intent-driven, never pushy.** The project system is *your* workflow, not the default state of a session. Claude never advertises your projects unprompted — it answers when you ask, and recognizes you when you *are* in a project directory.

## How it works

```
Your project lives in ~/projects/<key>/
  PROJECTS.json      ← identity index (name, status, description, updated-at)
  <key>/CLAUDE.md    ← deep content (status, decisions, todos, next actions)
  <key>/.memory/     ← transcript snapshots (gitignored, never committed)
```

| Layer | Mechanism | Responsibility |
|:---|:---|:---|
| **Native loading** | Claude Code auto-loads `CLAUDE.md` when a session starts in the project dir | Depth — what happened, what's next |
| **Registry** | `PROJECTS.json`, accessed when *you* ask (list / open / search / stats) | Identity — which projects exist, their state |
| **Layer 1 (default)** | `Stop` hook → transcript snapshot · `SessionEnd` hook → backup rotation + git commit | Safety — data survives even a killed terminal |
| **Layer 2 (optional)** | Your own OpenAI-compatible API extracts the conversation into CLAUDE.md (throttled) | Freshness — CLAUDE.md never goes stale |
| **Manual save** | "save project" / "exit" forces a full CLAUDE.md review | Quality — a considered, attributed record |

The three memory functions are deliberately non-overlapping: Claude Code's built-in auto-memory keeps *Claude's* cross-session memory, Layer 2 keeps *your project's document* fresh, and Layer 1 guarantees *nothing is ever lost*.

## Compared to alternatives

| | project-registry | Claude Code auto-memory | memory-mcp |
|:---|:---:|:---:|:---:|
| Project registry (CRUD/stats/rollback) | ✅ | ❌ | ❌ (path lookup only) |
| Project `CLAUDE.md` auto-fresh | ✅ (optional, any API) | ❌ (writes global memory dir) | ❌ (writes global memory) |
| Transcript safety / recovery | ✅ seconds-level + rotation + git | partial | ✅ git snapshots |
| Works in Chinese | ✅ | ✅ | ❌ |
| Privacy | Local-first; Layer 2 sends only to the endpoint you configure | local | local |

## Features

| Feature | What it does |
|:---|:---|
| 📋 Project registry | CRUD + search + stats over `~/projects/PROJECTS.json` |
| 🧭 Session resume | Entering a project → recall last progress → confirm what to continue |
| 📜 Decision discipline | Every decision records WHY (mandatory) — traceable months later |
| 🔎 Decision attribution | "Why X" → decision timeline + reason chain + status + impact |
| 💾 Save on exit | Save/exit **forces** CLAUDE.md update with prioritized next actions |
| 🔁 Auto-save (hooks) | Layer 1: transcript snapshot + backup/commit (silent, zero deps) |
| 🔁 Fresh-keeping (API) | Layer 2: conversation auto-extracted into CLAUDE.md (optional) |
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

On first use the skill will ask whether you want to enable auto-save — it explains exactly what gets authorized (hooks in your `settings.json`, local-only, nothing leaves your machine) and what you get (nothing is ever lost). Skippable, asked once.

**Layer 2 - Fresh-keeping (optional, bring your own key)**

Keeps CLAUDE.md fresh by extracting progress / decisions / todos / next actions from the conversation and merging them (throttled: >=10 new messages or >=10 minutes). Works with **any OpenAI-compatible API**:

```bash
# any OpenAI-compatible API works (DeepSeek / OpenAI / Qwen / local Ollama - same shape)
export PR_API_BASE_URL=https://your-provider.example.com/v1   # <-- replace with your provider base URL
export PR_API_KEY=sk-your-key                                 # <-- your own key
export PR_API_MODEL=your-model                                # <-- e.g. deepseek-v4-flash / gpt-4o-mini / qwen-plus
```

Without a key you still get Layer 1 plus all core features; with a key you additionally get an always-fresh CLAUDE.md. Conversation is only sent to the endpoint you configure. On first use the skill asks whether you want to configure a key (skippable, asked once).

## Example registry

See [examples/PROJECTS.example.json](examples/PROJECTS.example.json) for a sample registry with fictional projects.

## Development

- `skills/project-registry/SKILL.md` — the skill itself (self-contained, no dependencies)
- `skills/project-registry/scripts/` — auto-save hooks (transcript-sync / auto-summary / session-end)
- Design decisions: [docs/adr/](docs/adr/)

## License

[MIT](LICENSE)
