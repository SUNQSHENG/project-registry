# ADR 0002: Three privacy lines for publishing

- Status: Accepted
- Date: 2026-08-08

## Context

The author manages 20+ real business projects (hospital collaborations, government training programs, etc.) in `~/projects/PROJECTS.json`. Publishing the skill repository must never leak them.

## Decision

Three mandatory lines of defense:

1. **Full-text scan before push**: grep the entire repository for usernames, absolute paths, and real project names — zero hits required before any push.
2. **Git history hygiene**: `.gitignore` (committed as the *first* file, before anything else) excludes `PROJECTS.json`, `*.bak`, `backups/`. Real data is **never** `git add`ed — a file deleted later is still permanently recoverable from git history.
3. **Fictional demo data**: `examples/PROJECTS.example.json` and all docs use clearly fictional projects, verified to have zero overlap with real project names.

## Consequences

- The repository is safe to publish as-is; the author keeps the real registry locally, untouched.
- The cost: examples are less "realistic" than a live demo screenshot would be.
