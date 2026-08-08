# project-registry

管理**个人项目注册表** + 每个项目**面向 AI 的开发记录**的 Claude Code 技能——从一个菜单完成项目的查看、新建、删除、保存、续接、归因、回滚和健康检查。

## 为什么需要它

Claude Code 会跨会话丢失上下文。项目做了几天，下次回来 Claude 不知道发生了什么、下一步做什么，甚至不知道有哪些项目。`project-registry` 解决这个问题：

- **单一注册表**：所有项目登记在一个 `~/projects/PROJECTS.json`，自动序号管理
- **AI 可读的开发记录**：每个项目有 `CLAUDE.md`（每次会话自动加载），记录状态、决策、待办和**按优先级的下一步行动**
- **会话恢复**：进入项目自动回顾上次进展，询问从哪继续——不再冷启动
- **安全默认**：自动备份 + 轮转（每类保留 10 份）、每个项目自动 `git init`、删除前必须确认

## 功能

| 功能 | 说明 |
|:---|:---|
| 📋 项目注册表 | `~/projects/PROJECTS.json` 增删改查 + 统计 |
| 🧭 会话恢复 | 进入项目 → 回顾上次进展 → 确认续接 |
| 📜 决策纪律 | 每条决策必写原因（强制）——三个月后可追溯 |
| 🔎 决策归因 | "为什么 X" → 决策时间线 + 原因链 + 状态 + 影响 |
| 💾 退出自动保存 | 保存/退出**强制**更新 CLAUDE.md 并写出按优先级的下一步行动 |
| 🔁 自动保存（hooks） | 层1：transcript 快照 + 备份/提交（静默、零依赖） |
| 🔁 自动摘要（API） | 层2：对话自动提炼进 CLAUDE.md（可选） |
| 🔍 MD 健康检查 | 批量检查所有注册项目的 CLAUDE.md + .git |
| ↩️ 版本回滚 | CLAUDE.md / 项目文件 / 注册表——差异确认 + 新提交 |
| 🛡️ 备份轮转 | PROJECTS.json / CLAUDE.md / SKILL.md 各保留最近 10 份 |
| 📁 可选文档骨架 | 代码类项目可选 docs/SPEC.md + DESIGN.md |
| 🌍 通用 | 无硬编码路径，业务项目与代码项目都适用 |

## 安装

### 方式一：npx skills（推荐）

```bash
npx skills add SUNQSHENG/project-registry
# 或全局安装
npx skills add SUNQSHENG/project-registry -g
```

### 方式二：Claude Code 插件市场

```
/plugin marketplace add SUNQSHENG/project-registry
/plugin install project-registry@project-registry
```

### 方式三：手动

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
3. 在项目内工作。**自动保存后台静默运行**——不需要"记得保存"
4. 结束时："保存项目" 或 "退出"（强制全面回顾 CLAUDE.md）
5. 之后："为什么 X" → 归因 · "回滚" → 恢复版本 · "检查项目" → 健康检查
```

新建项目结构：

```
~/projects/
  PROJECTS.json            # 项目注册清单（唯一权威来源）
  <project-key>/
    README.md              # 面向人：背景和范围
    CLAUDE.md              # 面向 AI：状态、决策、待办、下一步行动
    .memory/               # 自动保存 transcript（gitignore，绝不提交）
    .git/                  # 自动 git init（CLAUDE.md 生效前提）
```

`CLAUDE.md` 是核心——Claude Code 每次会话自动加载它，长项目不会丢失上下文。

## 自动保存（hooks，静默执行）

两层机制，全部后台静默，只在 `~/projects/` 项目目录生效：

**层 1 机械快照（零依赖，默认开启）**

| Hook | 动作 |
|:---|:---|
| `Stop`（每次响应后） | transcript 同步到 `<项目>/.memory/`（秒级） |
| `SessionEnd` | CLAUDE.md 备份（10 份轮转）+ git 提交 |

`.memory/` 含对话原文——已 gitignore，绝不进仓库。强杀终端也不丢数据。

**层 2 自动摘要（可选，配置 API 后启用）**

自动提取进展/决策/待办/下一步并合并更新 CLAUDE.md（节流：≥10 条新消息或 ≥10 分钟）。**任意 OpenAI 兼容 API**，用自己的 key：

```bash
# 任意 OpenAI 兼容 API 均可（DeepSeek / OpenAI / 通义 / 本地 Ollama 同格式）
export PR_API_BASE_URL=https://你的提供商地址/v1   # <-- 替换为你的提供商 base URL
export PR_API_KEY=sk-你的key                        # <-- 你自己的 key
export PR_API_MODEL=你的模型名                      # <-- 如 deepseek-v4-flash / gpt-4o-mini / qwen-plus
```

不配 key：层 1 数据安全 + 全部核心功能；配 key：额外获得 CLAUDE.md 实时保鲜。首次使用会询问是否配置（可跳过，只问一次）。对话只发送到你配置的端点。

## 示例注册表

见 [examples/PROJECTS.example.json](examples/PROJECTS.example.json)（虚构数据示例）。

## 开发

- `skills/project-registry/SKILL.md` — 技能本体（自包含，零依赖）
- `skills/project-registry/scripts/` — 自动保存 hooks（transcript-sync / auto-summary / session-end）
- 设计决策： [docs/adr/](docs/adr/)

## 许可证

[MIT](LICENSE)
