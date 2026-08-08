#!/usr/bin/env node
/**
 * project-registry installer
 *
 * What it does:
 *   1. Copies the skill into ~/.claude/skills/project-registry/
 *   2. Adds auto-save hooks (Stop + SessionEnd) to ~/.claude/settings.json
 *      — after showing exactly what gets authorized and what you get
 *
 * Idempotent: re-running never duplicates hooks.
 * Local-only: nothing is sent anywhere. Layer 2 (auto-summary) only talks
 * to an endpoint YOU configure with your own API key — until then it's silent.
 *
 * Usage:
 *   npx @sunqsheng/project-registry
 *   npx @sunqsheng/project-registry --yes    # skip the confirmation prompt
 */
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const readline = require('node:readline');

const HOME = process.env.PR_HOME || os.homedir();
const SKILL_DIR = path.join(HOME, '.claude', 'skills');
const SKILL_DEST = path.join(SKILL_DIR, 'project-registry');
const SETTINGS_PATH = path.join(HOME, '.claude', 'settings.json');
const SRC_DIR = path.join(__dirname, '..', 'skills', 'project-registry');

const PYTHON = process.platform === 'win32' ? 'python' : 'python3';
const MARKER = 'project-registry/scripts/'; // any hook command containing this is ours

const HOOKS = {
  Stop: [
    {
      matcher: 'always',
      hooks: [
        { type: 'command', command: `${PYTHON} ${path.join(SKILL_DEST, 'scripts', 'transcript-sync.py').replace(/\\/g, '/')}` },
        { type: 'command', command: `${PYTHON} ${path.join(SKILL_DEST, 'scripts', 'auto-summary.py').replace(/\\/g, '/')}` }
      ]
    }
  ],
  SessionEnd: [
    {
      matcher: 'always',
      hooks: [
        { type: 'command', command: `${PYTHON} ${path.join(SKILL_DEST, 'scripts', 'session-end.py').replace(/\\/g, '/')}` }
      ]
    }
  ]
};

const BANNER = `
┌──────────────────────────────────────────────────────────────┐
│  project-registry — multi-project management for Claude Code │
└──────────────────────────────────────────────────────────────┘`;

const AUTHORIZE_TEXT = `
⚠️  WHAT THIS AUTHORIZES
   Adds 3 hooks (Stop x2 + SessionEnd) to your ~/.claude/settings.json
   They run only inside ~/projects/ project directories.
   100% local and silent — nothing is ever sent anywhere.
   (Layer 2 auto-summary is optional and needs YOUR API key; until you
   set one, it stays completely silent.)

✅  WHAT YOU GET
   · Second-level transcript snapshots — kill the terminal, lose nothing
   · Auto backup (10 rotated) + git commit on session end
   · Session resume with full project context
   · You never need to "remember to save"

   (The hooks are easy to remove: delete the "hooks" block the installer
   adds, or run this installer and choose "remove".)
`;

function ask(question) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

function copySkill() {
  if (fs.existsSync(SKILL_DEST)) {
    console.log(`· skill already exists at ${SKILL_DEST}`);
    console.log('  → keeping it (re-run with --force to overwrite)');
    return false;
  }
  fs.mkdirSync(path.dirname(SKILL_DEST), { recursive: true });
  fs.cpSync(SRC_DIR, SKILL_DEST, {
    recursive: true,
    filter: (src) => !src.includes('__pycache__')
  });
  console.log(`✓ skill installed → ${SKILL_DEST}`);
  return true;
}

function loadSettings() {
  if (!fs.existsSync(SETTINGS_PATH)) return { settings: {}, existed: false };
  return { settings: JSON.parse(fs.readFileSync(SETTINGS_PATH, 'utf-8')), existed: true };
}

function hasOurHooks(settings) {
  const hooks = settings.hooks || {};
  for (const event of Object.keys(hooks)) {
    for (const matcher of hooks[event] || []) {
      for (const h of matcher.hooks || []) {
        if (h.command && h.command.includes(MARKER)) return true;
      }
    }
  }
  return false;
}

function addHooks(settings) {
  const hooks = settings.hooks || {};
  const stop = hooks.Stop || [];
  if (!hasOurHooks(settings)) stop.push(...HOOKS.Stop);
  hooks.Stop = stop;
  const end = hooks.SessionEnd || [];
  if (!end.some((m) => (m.hooks || []).some((h) => h.command && h.command.includes(MARKER)))) {
    end.push(...HOOKS.SessionEnd);
  }
  hooks.SessionEnd = end;
  settings.hooks = hooks;
  return settings;
}

function removeHooks(settings) {
  const hooks = settings.hooks || {};
  for (const event of Object.keys(hooks)) {
    hooks[event] = (hooks[event] || []).map((m) => ({
      ...m,
      hooks: (m.hooks || []).filter((h) => !h.command || !h.command.includes(MARKER))
    })).filter((m) => (m.hooks || []).length > 0);
    if (hooks[event].length === 0) delete hooks[event];
  }
  if (Object.keys(hooks).length === 0) delete settings.hooks;
  return settings;
}

function writeSettings(settings) {
  if (fs.existsSync(SETTINGS_PATH)) {
    fs.copyFileSync(SETTINGS_PATH, SETTINGS_PATH + '.pre-project-registry.bak');
  }
  fs.mkdirSync(path.dirname(SETTINGS_PATH), { recursive: true });
  fs.writeFileSync(SETTINGS_PATH, JSON.stringify(settings, null, 2) + '\n', 'utf-8');
  console.log(`✓ hooks configured → ${SETTINGS_PATH} (backup saved as .pre-project-registry.bak)`);
}

async function main() {
  const args = process.argv.slice(2);
  const yes = args.includes('--yes');
  const force = args.includes('--force');
  const remove = args.includes('--remove');

  console.log(BANNER);

  if (!fs.existsSync(SRC_DIR)) {
    console.error('✗ skill bundle missing in this package — broken install. Please report: https://github.com/SUNQSHENG/project-registry/issues');
    process.exit(1);
  }

  if (remove) {
    const { settings } = loadSettings();
    const was = hasOurHooks(settings);
    const updated = removeHooks(settings);
    if (was) {
      writeSettings(updated);
      console.log('✓ project-registry hooks removed (settings.json restored).');
    } else {
      console.log('· no project-registry hooks found — nothing to remove.');
    }
    return;
  }

  copySkill();
  if (!force && fs.existsSync(SKILL_DEST)) {
    // skill kept; hooks may still be missing — continue to hook setup
  }

  const { settings, existed } = loadSettings();
  if (hasOurHooks(settings)) {
    console.log('· auto-save hooks already configured — nothing to do.');
    console.log('\n✅ Done. Restart Claude Code, then say "list projects" or "/project-registry".');
    return;
  }

  console.log(AUTHORIZE_TEXT);

  if (!yes) {
    const answer = await ask('Enable auto-save hooks? [Y/n] ');
    if (answer !== '' && answer !== 'y' && answer !== 'yes') {
      console.log('· skipped — hooks not added. You can re-run any time, or say "save project" manually.');
      return;
    }
  }

  const updated = addHooks(settings);
  writeSettings(updated);

  console.log(`
✅ Done! Restart Claude Code, then:

   · say "list projects" or "/project-registry" to see the menu
   · create a project: "new project"
   · your data is now auto-saved — nothing can be lost

   Remove hooks anytime:  npx @sunqsheng/project-registry --remove
`);
}

main().catch((err) => {
  console.error('✗ installer failed:', err.message);
  process.exit(1);
});
