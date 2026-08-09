# project-registry

**面向个人开发者的 Claude Code 多项目管理技能。** 一个注册表管全部项目、会话恢复带全上下文、数据永远丢不了——静默设计，开口才动。

## 为什么需要它

个人开发者同时开多个项目——工作、副业、学习。Claude Code 会跨会话丢失上下文：回来时 Claude 不知道发生了什么、下一步做什么，甚至不知道有哪些项目。`project-registry` 解决这个问题：

| 问题 | 方案 |
|:---|:---|
| "我到底有哪些项目？" | **单一注册表**——所有项目登记在一个 `~/projects/PROJECTS.json`，增删改查 + 搜索 + 统计 |
| "上次做到哪了？" | **AI 可读的开发记录**——每个项目有 `CLAUDE.md`（每次会话自动加载），记录状态、决策、待办和**按优先级的下一步行动** |
| "当初为什么选 X？" | **决策归因**——"为什么 X" 返回决策时间线（原因 + 影响） |
| "我忘了保存" | **自动备份 hooks**——每次响应后 transcript 存档，退出时备份 + 提交（零依赖） |
| "上次说了什么？" | **transcript 历史**——每个会话的对话原文存档在项目内，未收录的工作随时可恢复 |
| "我改坏了东西" | **版本回滚**——CLAUDE.md / 项目文件 / 注册表差异确认后恢复 |

**设计哲学：意图驱动，不打扰。** 项目体系是*你的*工作流，不是会话的默认态。Claude 从不主动推销你的项目——你开口它才动，你在项目目录里它才认得你。

## 工作原理

```
你的项目在 ~/projects/<key>/
  PROJECTS.json      ← 身份索引（项目名、状态、描述、更新时间）
  <key>/CLAUDE.md    ← 深度内容（状态、决策、待办、下一步）
  <key>/.memory/     ← transcript 存档（gitignore，绝不提交）
```

| 层 | 机制 | 职责 |
|:---|:---|:---|
| **原生加载** | Claude Code 在项目目录开会话时自动加载 `CLAUDE.md` | 深度——发生了什么、下一步做什么 |
| **注册表** | `PROJECTS.json`，*你*开口时访问（查看/打开/搜索/统计） | 身份——有哪些项目、各是什么状态 |
| **自动备份（默认）** | `Stop` hook → transcript 按会话存档到 `<项目>/.memory/transcripts/`（幂等）· `SessionEnd` hook → 备份轮转 + git 提交 | 安全——强杀终端也不丢，对话原文跨会话保留 |
| **手动保存** | "保存项目"/"退出"强制全面更新 CLAUDE.md | 质量——深思熟虑、有据可查的记录 |

两种记忆职责刻意不重叠：Claude Code 内置 auto-memory 管 *Claude 的*跨会话记忆，自动备份保证 *对话原文永不丢*（每次响应存档，强杀终端也不丢）；而 CLAUDE.md 的整理记录，需要手动保存。

**手动保存产生最终记录（CLAUDE.md）。** 保存/退出时强制全面更新 CLAUDE.md：补录决策（含 WHY）、按优先级重排下一步行动。

**怎么手动保存？** 在对话中直接对 agent 说「保存」或「退出」即可——**没有按钮、没有命令**，就是这么一句话。随时可以说，不依赖自动备份是否启用。

## 与其他方案对比

| | project-registry | Claude Code 内置 auto-memory |
|:---|:---:|:---:|
| 项目注册表（增删改查/统计） | ✅ | ❌ |
| 会话恢复（每项目回顾上次进展） | ✅ | ❌ |
| 决策归因（"为什么 X" 可回溯） | ✅ | ❌ |
| 项目健康检查（批量体检 CLAUDE.md/.git） | ✅ | ❌ |
| 版本回滚（CLAUDE.md/文件/注册表） | ✅ | ❌ |
| transcript 安全/恢复 | ✅ 秒级 + 轮转 + git | 部分 |
| 未入账对话恢复 | ✅ transcript 历史 + 保存时刻兜底（saved_at） | ❌ |
| 中文支持 | ✅ | ✅ |
| 隐私 | 本地优先，数据不出本机 | 本地 |

## 功能

| 功能 | 说明 |
|:---|:---|
| 📋 项目注册表 | `~/projects/PROJECTS.json` 增删改查 + 统计 |
| ➕ 新建项目 | 一条命令搭好：key + 目录 + README/CLAUDE.md + .gitignore + git init + 注册清单 |
| 🧭 会话恢复 | 进入项目 → 回顾上次进展 + 按优先级下一步行动 |
| 📜 决策纪律 | 每条决策必写原因（强制）——三个月后可追溯 |
| 🔎 决策归因 | "为什么 X" → 决策时间线 + 原因链 + 状态 + 影响 |
| 💾 退出保存 | 保存/退出**强制**更新 CLAUDE.md 并写出按优先级的下一步行动 |
| 🔁 自动备份（hooks） | transcript 按会话存档 + 备份/提交（静默、零依赖） |
| 🗂️ 未入账恢复 | 保存时刻兜底（saved_at）：未保存对话在会话回顾时读回 |
| 🔍 MD 健康检查 | 批量检查所有注册项目的 CLAUDE.md + .git |
| ↩️ 版本回滚 | CLAUDE.md / 项目文件 / 注册表——差异确认 + 新提交 |
| 🛡️ 备份轮转 | PROJECTS.json / CLAUDE.md / SKILL.md 各保留最近 10 份 |
| 📁 可选文档骨架 | 代码类项目可选 docs/SPEC.md + DESIGN.md |
| 🌍 通用 | 无硬编码路径，业务项目与代码项目都适用 |

> **说明：** 自动摘要（层 2，基于 API 的 CLAUDE.md 提炼）已在 v1.2.0 移除——手动保存 + transcript 历史更可靠地覆盖同一需求。

## 安装

### 方式一：npm（一键安装，推荐）

```bash
npx @sunqsheng/project-registry
# 或全局安装，随时可运行
npm i -g @sunqsheng/project-registry && project-registry
```

复制 skill 并带授权提示配置自动备份 hooks。幂等；`project-registry --remove` 可移除。

### 方式二：npx skills

```bash
npx skills add SUNQSHENG/project-registry
# 或全局安装
npx skills add SUNQSHENG/project-registry -g
```

### 方式三：Claude Code 插件市场

```
/plugin marketplace add SUNQSHENG/project-registry
/plugin install project-registry@project-registry
```

### 方式四：手动

```bash
git clone https://github.com/SUNQSHENG/project-registry
cp -r project-registry/skills/project-registry ~/.claude/skills/
```

重启 Claude Code，输入"查看项目"或"list projects"即可使用。

## 快速开始

```text
1. 触发技能："查看项目" / "list projects"
2. 菜单列出全部项目：
   - 输入数字序号（1-99）→ 打开项目（触发会话恢复）
   - N → 新建项目   D → 删除项目   C → 健康检查
3. 在项目内工作。**自动备份静默守护数据安全**——但 CLAUDE.md 全面更新仍需"保存项目"手动执行
4. 结束时："保存项目" 或 "退出"（强制全面更新 CLAUDE.md）
5. 之后："为什么 X" → 归因 · "回滚" → 恢复版本 · "检查项目" → 健康检查
```

新建项目结构：

```
<项目根>/                  # 默认：~/projects/（可自定义）
  PROJECTS.json            # 项目注册清单（唯一权威来源）
  <project-key>/
    README.md              # 面向人：背景和范围
    CLAUDE.md              # 面向 AI：状态、决策、待办、下一步行动
    .memory/               # 自动备份 transcript（gitignore，绝不提交）
    .git/                  # 自动 git init（CLAUDE.md 生效前提）
```

项目根**默认 `~/projects/`**，可在首次使用引导（检查 2）或说「设置项目路径」时自定义（存量项目可自动迁移）。

`CLAUDE.md` 是核心——Claude Code 每次会话自动加载它，长项目不会丢失上下文。

## 自动备份（hooks，静默执行）

机制全部后台静默，只在**项目根**（默认 `~/projects/`，可自定义）项目目录生效：

**自动备份（零依赖，默认开启）**

| Hook | 动作 |
|:---|:---|
| `Stop`（每次响应后） | transcript 按会话存档到 `<项目>/.memory/transcripts/`（秒级，幂等） |
| `SessionEnd` | CLAUDE.md 备份（10 份轮转）+ git 提交 |

`.memory/` 含对话原文——已 gitignore，绝不进仓库。强杀终端也不丢数据。

**启用自动备份**（一次性配置，把 hooks 加入 `~/.claude/settings.json`）：

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

首次使用 skill 会询问是否启用自动备份——**讲清楚授权什么**（向你的 settings.json 添加 hooks，仅本地，不向任何外部服务发送数据）**和带来什么**（数据永不丢）。可跳过，只问一次。

**未入账恢复（保存时刻兜底）**

保存项目会记录保存时刻（saved_at）；打开项目时若最近存档晚于保存时刻，会话回顾会读取对话原文尾部——**未保存的对话永不静默丢失**（量大时询问是否完整读取）。零配置即用：自动备份数据安全 + 全部核心功能。

**可移植性 —— 能在 Claude 之外用吗？**

核心工作流（注册表、新建项目、会话恢复、CLAUDE.md 保存、决策归因、回滚）就是指令 + JSON + git，可以移植到其他 AI agent（Codex / Gemini CLI / Cursor 等 AGENTS.md 类体系），把 SKILL.md 的指令按其格式重述即可。**Claude Code 专属的部分**：自动备份——依赖 Claude 的 transcript 文件与 Stop/SessionEnd hooks，因此自动备份仅限 Claude。核心功能不依赖它，照样完整可用。

## 示例注册表

见 [examples/PROJECTS.example.json](examples/PROJECTS.example.json)（虚构数据示例）。

## 开发

- `skills/project-registry/SKILL.md` — 技能本体（自包含，零依赖）
- `skills/project-registry/scripts/` — 自动备份 hooks（transcript-sync / session-end）
- 设计决策： [docs/adr/](docs/adr/)

## 许可证

[MIT](LICENSE)
