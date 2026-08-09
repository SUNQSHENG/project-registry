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
| "I forgot to save" | **Auto-backup hooks** — transcript archived every response, backup + commit on exit (zero dependencies) |
| "What did I say last time?" | **Transcript history** — every session's raw conversation is archived in the project, so unrecorded work is always recoverable |
| "I broke something" | **Rollback** — diff-confirmed version restore for CLAUDE.md, files and the registry |

**Design philosophy: intent-driven, never pushy.** The project system is *your* workflow, not the default state of a session. Claude never advertises your projects unprompted — it answers when you ask, and recognizes you when you *are* in a project directory.

## How it works

```
Your project lives in ~/projects/<key>/
  PROJECTS.json      ← identity index (name, status, description, updated-at)
  <key>/CLAUDE.md    ← deep content (status, decisions, todos, next actions)
  <key>/.memory/     ← transcript archives (gitignored, never committed)
```

| Layer | Mechanism | Responsibility |
|:---|:---|:---|
| **Native loading** | Claude Code auto-loads `CLAUDE.md` when a session starts in the project dir | Depth — what happened, what's next |
| **Registry** | `PROJECTS.json`, accessed when *you* ask (list / open / search / stats) | Identity — which projects exist, their state |
| **Auto-backup (default)** | `Stop` hook → transcript archived per-session into `<project>/.memory/transcripts/` (idempotent) · `SessionEnd` hook → backup rotation + git commit | Safety — survives even a killed terminal; raw conversation kept across sessions |
| **Manual save** | "save project" / "exit" forces a full CLAUDE.md update | Quality — a considered, attributed record |

The two memory functions are deliberately non-overlapping: Claude Code's built-in auto-memory keeps *Claude's* cross-session memory, and auto-backup guarantees *the raw conversation is never lost* (archived every response, safe even if the terminal is killed). The organized CLAUDE.md record, however, requires manual save.

**Manual save produces the final record (CLAUDE.md).** Saving or exiting forces a full CLAUDE.md update: decisions get recorded with their WHY, next actions get re-prioritized.

**How do I manually save?** Just tell the agent **"save"** or **"exit"** in the conversation — there's no button and no command, that's it. You can say it anytime; it works regardless of whether auto-backup is enabled.

## Compared to alternatives

| | project-registry | Claude Code auto-memory |
|:---|:---:|:---:|
| Project registry (CRUD/stats) | ✅ | ❌ |
| Session resume (recall last progress per project) | ✅ | ❌ |
| Decision attribution ("why X" traceable) | ✅ | ❌ |
| Project health check (batch audit CLAUDE.md/.git) | ✅ | ❌ |
| Version rollback (CLAUDE.md / files / registry) | ✅ | ❌ |
| Transcript safety / recovery | ✅ seconds-level + rotation + git | partial |
| Unrecorded-work recovery | ✅ transcript history + save-time fallback (saved_at) | ❌ |
| Works in Chinese | ✅ | ✅ |
| Privacy | Local-first, nothing leaves your machine | local |

## Features

| Feature | What it does |
|:---|:---|
| 📋 Project registry | CRUD + search + stats over `~/projects/PROJECTS.json` |
| ➕ New project | One-command scaffold: key + directory + README/CLAUDE.md + .gitignore + git init + registry entry |
| 🧭 Session resume | Entering a project → recall last progress + prioritized next actions |
| 📜 Decision discipline | Every decision records WHY (mandatory) — traceable months later |
| 🔎 Decision attribution | "Why X" → decision timeline + reason chain + status + impact |
| 💾 Save on exit | Save/exit **forces** CLAUDE.md update with prioritized next actions |
| 🔁 Auto-backup (hooks) | transcript archive + backup/commit (silent, zero deps) |
| 🗂️ Transcript history | Per-session raw conversation archived (silent, zero deps) |
| 🔍 MD health check | Batch-verify `CLAUDE.md` + `.git` exist for every registered project |
| ↩️ Version rollback | CLAUDE.md / project files / registry — diff confirm + new commit |
| 🛡️ Backup rotation | PROJECTS.json / CLAUDE.md / SKILL.md backups, keep latest 10 each |
| 📁 Optional doc skeleton | Code projects: optional `docs/SPEC.md` + `DESIGN.md` per feature |
| 🌍 Universal | No hardcoded paths, works for business and code projects alike |

> **Note:** Auto-summary (Layer 2, API-based CLAUDE.md extraction) was removed in v1.2.0 — manual save + transcript history cover the same need more reliably.

## Install

### Option 1: npm (one-command, recommended)

```bash
npx @sunqsheng/project-registry
# or install globally and run whenever you want
npm i -g @sunqsheng/project-registry && project-registry
```

Copies the skill and configures auto-backup hooks with an authorization prompt. Idempotent; remove with `project-registry --remove`.

### Option 2: npx skills

```bash
npx skills add SUNQSHENG/project-registry
# or install globally
npx skills add SUNQSHENG/project-registry -g
```

### Option 3: Claude Code plugin marketplace

```
/plugin marketplace add SUNQSHENG/project-registry
/plugin install project-registry@project-registry
```

### Option 4: Manual

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
3. Work in the project. Auto-backup keeps data safe silently — but manual save is still required for the full CLAUDE.md update
4. When done: "save project" or "exit" (forces a full CLAUDE.md update)
5. Later: "why X" → decision attribution · "rollback" → restore a version · "check projects" → health check
```

New project structure:

```
<projects-root>/           # default: ~/projects/ (configurable)
  PROJECTS.json            # registry (single source of truth)
  <project-key>/
    README.md              # for humans: background & scope
    CLAUDE.md              # for AI: status, decisions, todos, next actions
    .memory/               # auto-backup transcripts (gitignored, never committed)
    .git/                  # git init automatically (CLAUDE.md must be at .git level)
```

Projects live under a configurable root — the default is `~/projects/`; you can change it during first-use onboarding or by saying "set project path" (existing projects are migrated on request).

`CLAUDE.md` is the heart of it — Claude Code auto-loads it every session, so long-running projects never lose context.

## Auto-backup (hooks, silent)

Two layers, fully silent, run only inside the projects root (default `~/projects/`, configurable):

**Auto-backup (zero dependencies, on by default)**

| Hook | Action |
|:---|:---|
| `Stop` (after every response) | Archive transcript per-session into `<project>/.memory/transcripts/` (second-level, idempotent) |
| `SessionEnd` | Backup CLAUDE.md (rotation of 10) + git commit |

`.memory/` contains raw conversation - it is **gitignored** and never committed. Auto-backup keeps data safe even if you kill the terminal: nothing is ever lost.

**Enable auto-backup** (one-time, add hooks to `~/.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "always",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/skills/project-registry/scripts/transcript-sync.py" }
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

On first use the skill will ask whether you want to enable auto-backup — it explains exactly what gets authorized (hooks in your `settings.json`, local-only, nothing leaves your machine) and what you get (nothing is ever lost). Skippable, asked once.

**Unrecorded-work recovery (save-time fallback)**

Saving a project records the save moment (saved_at); when you open a project and the latest archive is newer than the save moment, the session resume reads the tail of the conversation — **unrecorded work is never silently lost** (it asks before reading large volumes). Zero configuration; auto-backup keeps data safe and all core features work out of the box.

**Portability - can I use this outside Claude Code?**

The core workflow (registry, new project, session resume, CLAUDE.md save, decision attribution, rollback) is plain instructions + JSON + git, so you can port it to other AI agents (Codex / Gemini CLI / Cursor and other AGENTS.md-style setups) by re-stating the SKILL.md commands in their format. What stays **Claude Code-specific**: the auto-backup layers (1 & 2) - they depend on Claude's transcript files and Stop/SessionEnd hooks, so auto-backup is Claude-only. All core features work without it.

## Example registry

See [examples/PROJECTS.example.json](examples/PROJECTS.example.json) for a sample registry with fictional projects.

## Development

- `skills/project-registry/SKILL.md` — the skill itself (self-contained, no dependencies)
- `skills/project-registry/scripts/` — auto-backup hooks (transcript-sync / session-end)
- Design decisions: [docs/adr/](docs/adr/)

## License

[MIT](LICENSE)
