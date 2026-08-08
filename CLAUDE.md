# project-registry

## 项目目标

将自用 skill `project`（项目管理：PROJECTS.json 注册表）升级为更成熟通用版并开源发布到 GitHub。参考 Keiji-Miyake/agent-skills 的 session-support 设计理念（短会话优化、上下文保持、文档驱动开发、ADR）。

## 技术栈

- Claude Code Skill（SKILL.md + 标准目录结构）
- 分发：npx skills CLI 生态 + Claude Code plugin marketplace（双兼容）

## 当前状态

state: active
- 阶段：设计定稿（grilling 完成），待执行升级
- 最新进展：2026-08-08 grilling 全会话完成，决策全部确认；项目已注册（seq 25）

## 架构决策记录

- 2026-08-08 — 单版本通用化：同一份 skill 既自用又开源，不做双版本分叉（原因：零维护成本，数据本就在 skill 外，脱敏容易；分叉后永久同步负担）
- 2026-08-08 — 升级范围：吸收 session-support 三项——①会话开始回顾（进项目时摘要上次进展+确认续接）②保存/退出强制写"下一步行动(按优先级)" ③代码类项目可选文档骨架 SPEC/DESIGN；跳过会话时长管理（原因：业务场景非番茄钟模式）
- 2026-08-08 — 发布双兼容：`skills/<name>/SKILL.md` 布局同时支持 `npx skills add` 与 `/plugin marketplace add`，额外加 `.claude-plugin/marketplace.json`（原因：两者结构不冲突，britt/slamb2k 成熟仓库标准做法）
- 2026-08-08 — 命名 project-registry（原因：名字即功能，可发现性好；claude- 前缀烂大街）
- 2026-08-08 — 语言：SKILL.md 中文 + README 英文主位/中文副位（原因：SKILL.md 是执行指令不影响功能，用户自用零摩擦；README 是星星门面，英文生态为主）
- 2026-08-08 — 隐私三道防线：①发布前全文 grep 扫描（su2q/SunQs/真实项目名零命中）②.gitignore 第一版即含 PROJECTS.json/*.bak/backups/，仓库内永不 add 真实数据（git 历史永久残留不可逆）③演示素材全部虚构，与 24 个真实项目名零重叠
- 2026-08-08 — 备份回滚三重保险：SKILL.md 备份到 backups/（跟随 10 份轮转规则）+ skill 目录 git init（.gitignore 排除备份和真实数据）+ 回滚=备份覆盖+删除新增文件
- 2026-08-08 — 同步模式：本地 skill 目录 = 真源，发布仓库 = 快照，低频手动同步（原因：发布是低频动作，无需自动化）
- 2026-08-08 — GitHub 前置：用户已有账号（Edge 浏览器登录态），发布走 Edge CDP；git 身份 admin@local 需改为账号身份

## 项目范围与功能

| 包含 | 不包含 |
|:---|:---|
| SKILL.md 升级与通用化（去 su2q/SunQs 硬编码→~/projects/ 约定；示例名换中性虚构名；修正备份路径不一致） | PROJECTS.json 真实数据 |
| README.md（英）+ README.zh-CN.md + LICENSE(MIT) + marketplace.json + examples/ 虚构示例 + .gitignore | backups/ 目录 |
| 1-2 个 ADR（单版本决策、隐私防线） | 多 skill 集合 |
| GitHub Public 仓库发布 + 安装自测 | 会话时长管理 |

## 依赖关系

| 依赖项目 | 关系 | 说明 |
|:---|:---|:---|
| project（自用 skill） | 被依赖 | 本次升级改造的对象，目录 `~/.claude/skills/project/` |
| Keiji-Miyake/agent-skills | 参考 | session-support 设计理念（已归档，0 星，只抄理念不当样板） |

## 待办

- [ ] 备份现有 SKILL.md → `~/.claude/skills/project/backups/SKILL.md.<时间戳>.bak`
- [ ] 本地 skill 目录 git init + 第一版 .gitignore（backups/、*.bak、PROJECTS.json）
- [ ] 改造 SKILL.md：name 改 project-registry；去硬编码；吸收会话开始回顾 + 保存强制优先级下一步行动 + 可选文档骨架；示例名中性化；备份路径修正
- [ ] 全文扫描验证（su2q/SunQs/真实项目名零命中）
- [ ] 用户试用验收升级版（不满意 → 备份覆盖回滚）
- [ ] 创建发布仓库结构：skills/project-registry/SKILL.md + README.md(英) + README.zh-CN.md + LICENSE(MIT) + .claude-plugin/marketplace.json + examples/PROJECTS.example.json(虚构) + .gitignore + docs/adr/
- [ ] GitHub 发布：Edge CDP 建 Public 仓库 project-registry → push（推送前最终确认）
- [ ] 安装自测：npx skills add 试装 + /plugin marketplace add 试装
- [ ] 提交 CLAUDE.md 变更并保存项目

## 已知问题

- 原 SKILL.md 文档与实况不一致：写死路径 `C:\Users\su2q`（实际 SunQs）；备份路径写 project-manager（实际 project）——升级时统一修正
- 本地 git 身份 admin@local，发布前必须改
- gh CLI 未安装，发布操作走 Edge 浏览器 CDP 或安装 gh

## 参考

- Keiji-Miyake/agent-skills: https://github.com/Keiji-Miyake/agent-skills
- britt/claude-code-skills（plugin marketplace 参考）: https://github.com/britt/claude-code-skills
- npx skills 生态: https://skills.so
