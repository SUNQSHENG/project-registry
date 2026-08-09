#!/usr/bin/env python3
"""
project-registry · 层1 机械快照：transcript 同步（Stop hook 调用）
零依赖、纯本地、静默执行。

作用：每次 Claude 响应完成后，把会话记录同步到项目目录 .memory/，
保证任何时刻项目目录里有一份完整对话快照（强杀/缓存清理不丢）。
"""
import json
import os
import re
import shutil
import sys
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


def is_project_dir(cwd: str) -> Path | None:
    """当前目录是否在 ~/projects/<key>/ 下；返回项目根目录或 None"""
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


def find_transcript(project_dir: Path) -> Path | None:
    """定位当前会话 transcript：~/.claude/projects/<项目路径转义>/<最新>.jsonl"""
    projects = HOME / ".claude" / "projects"
    if not projects.is_dir():
        return None
    # 项目目录对应的转义名：路径中的 / 和 \ 转成 -
    cand = str(project_dir).replace("\\", "-").replace("/", "-")
    candidates = []
    for entry in projects.iterdir():
        if not entry.is_dir():
            continue
        # 直接匹配转义名目录
        if cand in entry.name:
            for f in entry.glob("*.jsonl"):
                candidates.append(f)
    if not candidates:
        # 兜底：找最近修改的 jsonl（当前项目名下无匹配时）
        for entry in projects.iterdir():
            if entry.is_dir():
                candidates.extend(entry.glob("*.jsonl"))
        if not candidates:
            return None
        candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return candidates[0]
    candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return candidates[0]


def main() -> int:
    cwd = os.getcwd()
    project_dir = is_project_dir(cwd)
    if project_dir is None:
        return 0  # 非项目目录，静默跳过

    transcript = find_transcript(project_dir)
    if transcript is None:
        return 0

    mem = project_dir / ".memory"
    mem.mkdir(exist_ok=True)
    dest = mem / "transcript-latest.jsonl"
    try:
        shutil.copy2(transcript, dest)
    except OSError:
        return 0  # 静默失败，下次再试
    # 按会话历史存档（幂等：同一会话文件名覆盖；跨会话保留原文，
    # 供「未入账兜底」——会话回顾时 mtime > saved_at 判定读取）
    try:
        arch = mem / "transcripts"
        arch.mkdir(exist_ok=True)
        shutil.copy2(transcript, arch / transcript.name)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
