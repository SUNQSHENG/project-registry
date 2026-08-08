# ADR 0001: Single version for both personal use and open source

- Status: Accepted
- Date: 2026-08-08

## Context

This skill started as a personal, highly customized tool (Chinese UI, bound to the author's own `PROJECTS.json`, real business projects). Open-sourcing it naively would either leak personal data or fork the codebase into two versions (personal + public) that drift apart.

## Decision

Ship **one version** that is:

- Fully generic: no hardcoded absolute paths (`~/projects/` convention only)
- Data-agnostic: the registry file lives *outside* the skill directory, so the skill contains zero user data
- Same file the author uses daily, also published as-is

## Consequences

- **Pro**: zero maintenance cost of a second branch; every personal improvement automatically becomes a public release
- **Pro**: personal data stays safe because it never enters the repository (see ADR 0002)
- **Con**: the SKILL.md stays Chinese-first, which may slightly reduce adoption among non-Chinese-speaking users (mitigated by an English README)

## Alternatives considered

- **Two versions** (personal + sanitized public): rejected — permanent fork, sync burden, and the public version would lag behind and die.
- **Demo-only release**: rejected — a neutered demo doesn't represent the real capability and gets no stars.
