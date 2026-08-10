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
    if stdin is not None:
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


def find_transcript(project_dir: Path) -> Path | None:
    """定位当前会话 transcript：~/.claude/projects/<项目路径转义>/<最新>.jsonl"""
    projects = HOME / ".claude" / "projects"
    if not projects.is_dir():
        return None
    # 项目目录对应的转义名：路径中的 : \ / 转成 -（与官方 encode 一致）
    cand = encode_path(project_dir)
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
    stdin = read_stdin_json()
    project_dir = resolve_project_dir(stdin)
    if project_dir is None:
        return 0  # 非项目目录，静默跳过

    # hook 调用：stdin transcript_path 即当前会话精确路径，直接消费
    # （绕开 find_transcript 的编码匹配与兜底——同一项目可能有多编码转录目录，
    #   多项目并发时兜底会选错会话）
    transcript = None
    tp = stdin.get("transcript_path") if stdin is not None else None
    if tp:
        tp_path = Path(tp)
        if tp_path.is_file():
            transcript = tp_path
    if transcript is None:
        transcript = find_transcript(project_dir)
    if transcript is None:
        return 0

    # 按会话历史存档（幂等：同一会话文件名覆盖；跨会话保留原文，
    # 供「未入账兜底」——会话回顾时 mtime > saved_at 判定读取）
    # （2026-08-09 简化：移除 transcript-latest.jsonl 覆盖快照——无消费者且职责被本存档完全覆盖）
    mem = project_dir / ".memory"
    mem.mkdir(exist_ok=True)
    try:
        arch = mem / "transcripts"
        arch.mkdir(exist_ok=True)
        shutil.copy2(transcript, arch / transcript.name)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
