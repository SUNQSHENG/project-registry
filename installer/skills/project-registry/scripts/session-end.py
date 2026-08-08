#!/usr/bin/env python3
"""
project-registry · SessionEnd hook：会话结束收尾
1) 备份 CLAUDE.md 到 skill 目录 backups/（10 份轮转，按末尾时间戳排序）
2) 项目 git 提交（有变更才提交）
静默执行，只做快操作（SessionEnd 窗口内被限制，禁止长任务）。
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
PROJECTS_ROOT = HOME / "projects"
SKILL_DIR = HOME / ".claude" / "skills" / "project-registry"
BACKUP_LIMIT = 10


def is_project_dir(cwd: str) -> Path | None:
    try:
        p = Path(cwd).resolve()
    except Exception:
        return None
    root = PROJECTS_ROOT.resolve()
    if p == root or not str(p).startswith(str(root)):
        return None
    rel = p.relative_to(root)
    if len(rel.parts) < 1:
        return None
    return root / rel.parts[0]


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
        subprocess.run(
            ["git", "-C", str(project_dir), "add", "CLAUDE.md", ".gitignore"],
            capture_output=True, timeout=10,
        )
        subprocess.run(
            ["git", "-C", str(project_dir), "commit", "-m", "自动备份：会话结束收尾（CLAUDE.md 变更）"],
            capture_output=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass


def main() -> int:
    project_dir = is_project_dir(os.getcwd())
    if project_dir is None:
        return 0
    backup_rotate(project_dir)
    git_commit(project_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
