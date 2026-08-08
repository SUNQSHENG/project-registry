# project-registry

## 项目背景

将自用 Claude Code skill `project`（项目管理：项目注册表 PROJECTS.json + 增删改查 + 开发记录 CLAUDE.md）升级为更成熟、可公开的通用版本，并发布到 GitHub 获取星星。

设计参考：[Keiji-Miyake/agent-skills](https://github.com/Keiji-Miyake/agent-skills) 的 session-support（原 dev-support）——短会话优化、上下文保持、文档驱动开发、ADR 支持。

## 项目目标

1. **升级**：吸收 session-support 三项能力（会话开始回顾 / 保存时强制写优先级下一步行动 / 代码类项目可选文档骨架），保留现有全部能力
2. **通用化**：单版本策略——同一份 skill 既自用又开源，清除全部个人硬编码
3. **开源**：发布到 GitHub（Public），支持 `npx skills add` + `/plugin marketplace add` 双分发路径，获取星星
4. **安全**：三道隐私防线，绝不泄露真实业务项目数据

## 项目范围

| 包含 | 不包含 |
|:---|:---|
| SKILL.md 升级与通用化 | PROJECTS.json（真实数据） |
| README 中英双语、LICENSE、marketplace.json、examples 虚构示例 | backups/ 备份目录 |
| 1-2 个 ADR（记录关键决策） | 任何 `C:\Users\su2q` / `SunQs` 硬编码 |
| GitHub 发布与安装自测 | 多 skill 集合（只发一个 skill） |

## 关键决策摘要（详见 CLAUDE.md）

- 单版本通用化，不做双版本分叉
- 跳过会话时长管理（业务场景不需要）
- 命名 `project-registry`（仓库名 + skill name）
- SKILL.md 中文，README 英文主位 + 中文副位
- 本地目录为真源，发布仓库为快照
