#!/usr/bin/env python3
"""
project-registry · 层2 通用 API 自动摘要（Stop hook 调用，可选）
从 transcript 增量提取进展/决策/待办/下一步，合并更新 CLAUDE.md。

配置（环境变量，任意 OpenAI 兼容提供商）：
  PR_API_BASE_URL  如 https://api.deepseek.com/v1 或 https://api.openai.com/v1 或 http://localhost:11434/v1
  PR_API_KEY       用户自己的 key
  PR_API_MODEL     如 deepseek-chat / gpt-4o-mini / qwen-plus
未配置任何一项 → 自动跳过（机械层不受影响）。

静默执行：无输出、失败静默、节流控制（>=10 条新消息 或 >=10 分钟）。
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
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
THROTTLE_MIN = 10          # 分钟
THROTTLE_MSGS = 10         # 条


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


def extract_text(content) -> str:
    """从 transcript 消息 content 提取纯文本"""
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and item.get("text"):
                    parts.append(str(item["text"]))
                elif item.get("type") == "tool_result" and isinstance(item.get("content"), (str, list)):
                    parts.append(extract_text(item["content"]))
            elif isinstance(item, str):
                parts.append(item)
    return "\n".join(parts)


def read_transcript(path: Path) -> list[dict]:
    """读 transcript，返回 [{role, text}]"""
    msgs = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                typ = obj.get("type", "")
                if typ not in ("user", "assistant"):
                    continue
                text = extract_text(obj.get("message", {}).get("content", ""))
                if text.strip():
                    msgs.append({"role": "user" if typ == "user" else "assistant", "text": text.strip()})
    except OSError:
        return []
    return msgs


def load_state(project_dir: Path) -> dict:
    try:
        return json.loads((project_dir / ".memory" / "state.json").read_text(encoding="utf-8"))
    except Exception:
        return {"offset": 0, "last_summary": 0}


def save_state(project_dir: Path, state: dict):
    mem = project_dir / ".memory"
    mem.mkdir(exist_ok=True)
    (mem / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def call_api(messages: list[dict]) -> str | None:
    base = os.environ.get("PR_API_BASE_URL", "").rstrip("/")
    key = os.environ.get("PR_API_KEY", "")
    model = os.environ.get("PR_API_MODEL", "")
    if not base or not key or not model:
        return None
    url = base + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError):
        return None


def parse_summary(raw: str) -> dict:
    """解析 API 返回的 JSON（容忍 markdown 代码块包裹）"""
    raw = raw.strip()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}


def insert_to_section(md: str, section: str, lines: list[str]) -> str:
    """在指定 ## 段落内末尾插入行（段落不存在则追加到文件末尾）"""
    if not lines:
        return md
    pat = re.compile(rf"^## {re.escape(section)}\n", re.M)
    m = pat.search(md)
    if not m:
        return md.rstrip() + "\n" + "\n".join(lines) + "\n"
    # 段落结束 = 任意下一个 ## 标题（不是同一个 section！）
    end = re.search(r"^## ", md, re.M)  # placeholder
    end = re.search(r"^## ", md[m.end():], re.M)
    tail_start = (m.end() + end.start()) if end else len(md)
    segment = md[m.end():tail_start]
    # 段内去重（精确匹配行）
    existing_lines = set(l.strip() for l in segment.splitlines() if l.strip())
    new_lines = [l for l in lines if l.strip() not in existing_lines]
    if not new_lines:
        return md
    insert = "\n" + "\n".join(new_lines) + "\n"
    return md[:tail_start] + insert + md[tail_start:]


def merge_claude_md(project_dir: Path, summary: dict):
    """把摘要合并进 CLAUDE.md（按段落插入决策/待办/下一步，更新进展）"""
    md_path = project_dir / "CLAUDE.md"
    if not md_path.exists():
        return
    md = md_path.read_text(encoding="utf-8")
    today = time.strftime("%Y-%m-%d")

    # ① 最新进展：更新「当前状态」段的"最新进展"行（统一格式：日期 | 自动摘要）
    progress = str(summary.get("progress", "")).strip()
    if progress:
        if "最新进展：" in md:
            md = re.sub(r"- 最新进展：.*", f"- 最新进展：{today} | {progress[:100]}", md, count=1)
        else:
            md += f"\n- 最新进展：{today} | {progress[:100]}\n"

    # ② 新决策：插入「架构决策记录」段内（含原因/状态，段内去重）
    decisions = summary.get("decisions", [])
    d_lines = []
    for d in decisions if isinstance(decisions, list) else []:
        if not isinstance(d, dict):
            continue
        title = str(d.get("decision") or d.get("title") or "").strip()
        if not title:
            continue
        reason = str(d.get("reason") or "").strip()
        line = f"- [🔄进行中] {today} — {title}"
        if reason:
            line += f"（原因：{reason}）"
        d_lines.append(line)
    md = insert_to_section(md, "架构决策记录", d_lines)

    # ③ 待办：插入「待办」段内（去重）
    todos = summary.get("todos", [])
    t_lines = [f"- [ ] {str(t).strip()}" for t in todos if isinstance(t, str) and t.strip()]
    md = insert_to_section(md, "待办", t_lines)

    # ④ 下一步行动：插入「下一步行动」段内（去重，编号顺延）
    next_actions = summary.get("next_actions", [])
    n_lines = [str(a).strip() for a in next_actions if isinstance(a, str) and str(a).strip()]
    if n_lines:
        pat = re.compile(r"^## 下一步行动\n", re.M)
        m = pat.search(md)
        if m:
            end = re.search(r"^## ", md[m.end():], re.M)
            tail = (m.end() + end.start()) if end else len(md)
            segment = md[m.end():tail]
            existing = [l.strip() for l in segment.splitlines() if l.strip()]
            # 已有数字条目数
            num = len([l for l in existing if re.match(r"^\d+\. ", l)])
            new_items = []
            for a in n_lines:
                if any(a in e or e in a for e in existing):
                    continue
                new_items.append(a)
            if new_items:
                insert = "\n" + "\n".join(f"{num+i+1}. {a}" for i, a in enumerate(new_items[:3])) + "\n"
                md = md[:tail] + insert + md[tail:]
        else:
            block = "## 下一步行动\n\n" + "\n".join(f"{i+1}. {a}" for i, a in enumerate(n_lines[:3]))
            md = md.rstrip() + "\n\n" + block + "\n"

    md_path.write_text(md, encoding="utf-8")


def main() -> int:
    project_dir = is_project_dir(os.getcwd())
    if project_dir is None:
        return 0

    # API 未配置 → 静默跳过
    if not (os.environ.get("PR_API_BASE_URL") and os.environ.get("PR_API_KEY") and os.environ.get("PR_API_MODEL")):
        return 0

    transcript = project_dir / ".memory" / "transcript-latest.jsonl"
    if not transcript.exists():
        return 0

    msgs = read_transcript(transcript)
    state = load_state(project_dir)
    # 会话重置检测：transcript 是覆盖式快照（新会话覆盖旧会话），
    # 旧会话 offset 越界（offset > 当前消息数）→ 重置指针，重新消费新会话
    if state.get("offset", 0) > len(msgs):
        state["offset"] = 0
    new_msgs = msgs[state.get("offset", 0):]

    # 节流：新消息不足 或 时间未到
    now = time.time()
    if len(new_msgs) < THROTTLE_MSGS and (now - state.get("last_summary", 0)) < THROTTLE_MIN * 60:
        return 0

    if not new_msgs:
        return 0

    # 构造提炼 prompt（只发增量，控制 token）
    conv = "\n".join(f"{m['role']}: {m['text'][:2000]}" for m in new_msgs[-40:])
    prompt = (
        "你是项目上下文提炼器。从对话中提取结构化信息，只输出 JSON：\n"
        '{"progress": "最新进展一句话", "decisions": [{"decision": "决策内容", "reason": "原因"}], '
        '"todos": ["新待办"], "next_actions": ["下一步行动(按优先级)"]}\n'
        "严格规则：\n"
        "1. decisions 只提取【真正的决策】——影响项目方向、难逆转、有取舍的选择；"
        "执行动作（\"做了X\"\"修改了Y\"）不算决策，不提取\n"
        "2. decision 必须一句话（不超过 30 字），reason 必须存在（对话中找不到原因就跳过该决策）\n"
        "3. progress 是最新进展的一句话（不超过 50 字），用过去时\n"
        "4. todos 是对话中新提出的待办；next_actions 按优先级排列\n"
        "5. 没有对应内容就留空数组\n\n对话：\n" + conv[-12000:]
    )
    raw = call_api([
        {"role": "system", "content": "你是项目上下文提炼器，输出 JSON。"},
        {"role": "user", "content": prompt},
    ])
    if not raw:
        return 0

    summary = parse_summary(raw)
    if not summary:
        return 0

    merge_claude_md(project_dir, summary)
    state["offset"] = len(msgs)
    state["last_summary"] = now
    save_state(project_dir, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
