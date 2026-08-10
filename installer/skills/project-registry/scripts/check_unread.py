#!/usr/bin/env python3
"""
project-registry · 未入账判定（会话开始流程步骤 5 单一入口）
判断保存时刻（.memory/state.json saved_at）之后是否有未入账实质 user 消息，
有则输出尾部快览供会话回顾使用。一次调用，毫秒级，替代现写 python 判定。
用法: python check_unread.py <项目目录>
输出: UNREAD=0/1 + 有未入账时尾部 30 条快览（超量提示弹卡决策）
双格式兼容：message 字段直接是 dict 对象 或 字符串化 dict；timestamp 数字或 ISO。
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Windows GBK 控制台打印 emoji/特殊字符崩溃 → 强制 UTF-8 输出
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def parse_ts(ts):
    """timestamp：数字直接返回；ISO 字符串（2026-08-10T11:14:22.931Z）转 epoch 秒"""
    if isinstance(ts, (int, float)):
        return float(ts)
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def get_content(msg):
    """取 (content, isMeta)：message 字段 dict 对象 或 字符串化 dict 两种形态都兼容"""
    m = msg.get("message")
    if isinstance(m, str):
        try:
            m = json.loads(m)
        except (json.JSONDecodeError, ValueError):
            m = None
    if isinstance(m, dict):
        c = m.get("content")
        meta = m.get("isMeta", False)
    else:
        c = msg.get("content")
        meta = False
    if isinstance(c, list):
        texts = []
        for item in c:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
        return "\n".join(texts), meta
    return c, meta


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python check_unread.py <项目目录>")
        return 1
    proj = Path(sys.argv[1]).resolve()

    state = proj / ".memory" / "state.json"
    if not state.exists():
        print("UNREAD=1  无保存时刻记录（旧项目，保守触发）")
        return 0
    try:
        saved_at = json.loads(state.read_text(encoding="utf-8")).get("saved_at")
    except Exception:
        saved_at = None
    if not saved_at:
        print("UNREAD=1  无 saved_at（旧项目，保守触发）")
        return 0

    arch = proj / ".memory" / "transcripts"
    if not arch.is_dir():
        print("UNREAD=0  无存档")
        return 0
    files = sorted(arch.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not files:
        print("UNREAD=0  无存档")
        return 0

    latest = files[-1]
    try:
        lines = latest.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = latest.read_text(encoding="utf-8", errors="replace").splitlines()

    unread = []
    for line in lines:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") != "user":
            continue
        ts = parse_ts(msg.get("timestamp"))
        if ts is None or ts <= saved_at:
            continue
        content, meta = get_content(msg)
        if meta:
            continue
        if isinstance(content, str) and content.strip():
            unread.append((ts, content.strip()))

    if not unread:
        print("UNREAD=0  无未入账实质对话（saved_at 后无实质 user 消息）")
        return 0

    total = len(unread)
    print(f"UNREAD=1  {total} 条未入账对话")
    for ts, c in unread[-30:]:
        local = datetime.fromtimestamp(ts)
        print(f"  [{local:%m-%d %H:%M:%S}] {c.replace(chr(10), ' ')[:100]}")
    if total > 30:
        print(f"  …共 {total} 条（>30，Agent 按流程弹卡：完整读/读尾部/跳过）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
