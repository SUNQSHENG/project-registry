#!/usr/bin/env python3
"""
project-registry · SessionEnd hook：会话结束归档
1) 备份 CLAUDE.md 到 skill 目录 backups/（10 份轮转，按末尾时间戳排序）
2) 项目 git 提交（有变更才提交）
静默执行，只做快操作（SessionEnd 窗口内被限制，禁止长任务）。
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()

CONFIG_FILE = HOME / ".claude" / "skills" / "project-registry" / "config.json"


def get_projects_root() -> Path:
    """项目根目录：优先 config.json 的 projectsRoot，默认 ~/projects"""
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        r = cfg.get("projectsRoot")
        if r:
            return Path(r).expanduser()
    except Exception:
        pass
    return HOME / "projects"


PROJECTS_ROOT = get_projects_root()
SKILL_DIR = HOME / ".claude" / "skills" / "project-registry"
BACKUP_LIMIT = 10


def is_project_dir(cwd: str) -> Path | None:
    try:
        p = Path(cwd).resolve()
    except Exception:
        return None
    root = PROJECTS_ROOT.resolve()
    # is_relative_to 语义化比较：防 ~/projects2 之类前缀假命中
    if p == root or not p.is_relative_to(root):
        return None
    rel = p.relative_to(root)
    if len(rel.parts) < 1:
        return None
    return root / rel.parts[0]


def encode_path(p: Path) -> str:
    """项目目录 → transcript 目录编码名（: \\ / 全转 -，与 Claude Code 官方编码一致）"""
    return str(p.resolve()).replace(":", "-").replace("\\", "-").replace("/", "-")


def read_stdin_json() -> dict | None:
    """读 hook stdin JSON；手动运行（TTY）或空输入返回 None，不阻塞"""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return None
        data = sys.stdin.read()
        if not data.strip():
            return None
        return json.loads(data)
    except Exception:
        return None


def resolve_project_dir(stdin: dict | None) -> Path | None:
    """定位当前项目：
    - hook 调用（stdin 有 JSON）：① stdin transcript_path 反推（与进程 cwd 无关，
      CLI/IDE 扩展通吃，修复 hook 进程 cwd 漂移/不持久问题）② stdin cwd 字段。
      两者都失配 → 明确返回 None（stdin cwd 与进程 cwd 同源，回退无增益只会假命中）
    - 手动运行（无 stdin）：进程 os.getcwd()"""
    if stdin:
        tp = stdin.get("transcript_path")
        if tp:
            # ~/.claude/projects/<编码路径>/<会话>.jsonl → 用项目清单编码名匹配反推
            parent = Path(tp).resolve().parent
            if parent.name:
                try:
                    for d in PROJECTS_ROOT.iterdir():
                        if d.is_dir() and encode_path(d) == parent.name:
                            return d
                except OSError:
                    pass
        cwd = stdin.get("cwd")
        if cwd:
            p = is_project_dir(cwd)
            if p:
                return p
        return None
    return is_project_dir(os.getcwd())


def backup_rotate(project_dir: Path):
    """备份 CLAUDE.md 并按末尾时间戳轮转（保留最近 10 份）"""
    md = project_dir / "CLAUDE.md"
    if not md.exists():
        return
    backups = SKILL_DIR / "backups"
    backups.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    try:
        (backups / f"CLAUDE.md.{ts}.bak").write_text(md.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        return
    # 轮转：按文件名末尾 YYYYMMDD_HHMMSS 排序，保留最近 10 份
    files = [f for f in backups.glob("CLAUDE.md.*.bak")]
    if len(files) > BACKUP_LIMIT:
        files.sort(key=lambda f: re.search(r"(\d{8}_\d{6})\.bak$", f.name).group(1) if re.search(r"(\d{8}_\d{6})\.bak$", f.name) else "0")
        for f in files[: len(files) - BACKUP_LIMIT]:
            try:
                f.unlink()
            except OSError:
                pass


def git_commit(project_dir: Path):
    """项目目录 git 提交（有变更才提交，CLAUDE.md 与 .git 同级才操作）"""
    if not (project_dir / ".git").is_dir():
        return
    try:
        r = subprocess.run(
            ["git", "-C", str(project_dir), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return
        # 提交前扫描（第三道防线）：变更文件含敏感模式 → 中止提交（防 .memory/ 等泄入 git）
        SENSITIVE = (".memory", "PROJECTS.json", ".bak", "backups/")
        for line in r.stdout.splitlines():
            path = line[3:].strip()
            if any(s in path for s in SENSITIVE):
                print(f"[project-registry] 中止提交：变更含敏感文件 {path}", file=sys.stderr)
                return
        # CLAUDE.md 被跟踪（普通项目）→ add CLAUDE.md + .gitignore
        # CLAUDE.md 未跟踪（发布仓库项目，如 project-registry 开发仓库）→ add -u（仅已跟踪文件，
        #   .memory/PROJECTS.json/backups 仍被 .gitignore 排除；防 CLAUDE.md 泄入公开仓库）
        ls = subprocess.run(
            ["git", "-C", str(project_dir), "ls-files", "--error-unmatch", "CLAUDE.md"],
            capture_output=True, timeout=10,
        )
        if ls.returncode == 0:
            subprocess.run(
                ["git", "-C", str(project_dir), "add", "CLAUDE.md", ".gitignore"],
                capture_output=True, timeout=10,
            )
        else:
            subprocess.run(
                ["git", "-C", str(project_dir), "add", "-u"],
                capture_output=True, timeout=10,
            )
        # commit message 动态化（2026-08-09 已知问题修复）：按实际暂存文件生成
        stat = subprocess.run(
            ["git", "-C", str(project_dir), "diff", "--cached", "--stat"],
            capture_output=True, text=True, timeout=10,
        )
        msg = "自动备份：会话结束归档"
        if stat.stdout.strip():
            files = [
                l.strip().split("|")[0].strip()
                for l in stat.stdout.strip().splitlines()
                if "|" in l and "files changed" not in l
            ]
            if files:
                msg += f"（{', '.join(files[:3])}）"
        subprocess.run(
            ["git", "-C", str(project_dir), "commit", "-m", msg],
            capture_output=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass


def main() -> int:
    stdin = read_stdin_json()
    project_dir = resolve_project_dir(stdin)
    if project_dir is None:
        return 0
    backup_rotate(project_dir)
    git_commit(project_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
