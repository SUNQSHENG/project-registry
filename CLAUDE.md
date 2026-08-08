# project-registry

## 项目目标

将自用 skill `project`（项目管理：PROJECTS.json 注册表）升级为更成熟通用版并开源发布到 GitHub。参考 Keiji-Miyake/agent-skills 的 session-support 设计理念（短会话优化、上下文保持、文档驱动开发、ADR）。

## 技术栈

- Claude Code Skill（SKILL.md + 标准目录结构）
- 分发：npx skills CLI 生态 + Claude Code plugin marketplace（双兼容）

## 当前状态

state: active
- 阶段：发布仓库构建完成 + 多轮测试修复 + 3 次全流程自审查通过，**发布暂缓（用户决定）**
- 最新进展：2026-08-08 用户 2 次实测发现 4 类问题全部修复（grill-with-docs 引入未落地→三动作落实；手动调用提醒；AskUserQuestion 卡片强制化；会话续接卡片化）；3 次全流程自审查全过（隐私零命中 / 25 项目全健康 / 备份 10 份 / 双仓库同步）；测试残留项目已注销

## 架构决策记录

- 2026-08-08 — 单版本通用化：同一份 skill 既自用又开源，不做双版本分叉（原因：零维护成本，数据本就在 skill 外，脱敏容易；分叉后永久同步负担）
- 2026-08-08 — 升级范围：吸收 session-support 三项——①会话开始回顾（进项目时摘要上次进展+确认续接）②保存/退出强制写"下一步行动(按优先级)" ③代码类项目可选文档骨架 SPEC/DESIGN；跳过会话时长管理（原因：业务场景非番茄钟模式）
- 2026-08-08 — 发布双兼容：`skills/<name>/SKILL.md` 布局同时支持 `npx skills add` 与 `/plugin marketplace add`，额外加 `.claude-plugin/marketplace.json`（原因：两者结构不冲突，britt/slamb2k 成熟仓库标准做法）
- 2026-08-08 — 命名 project-registry（原因：名字即功能，可发现性好；claude- 前缀烂大街）
- 2026-08-08 — 语言：SKILL.md 中文 + README 英文主位/中文副位（原因：SKILL.md 是执行指令不影响功能，用户自用零摩擦；README 是星星门面，英文生态为主）
- 2026-08-08 — 隐私三道防线：①发布前全文 grep 扫描（个人路径/用户名/真实项目名零命中）②.gitignore 第一版即含 PROJECTS.json/*.bak/backups/，仓库内永不 add 真实数据（git 历史永久残留不可逆）③演示素材全部虚构，与真实项目名零重叠
- 2026-08-08 — 备份回滚三重保险：SKILL.md 备份到 backups/（跟随 10 份轮转规则）+ skill 目录 git init（.gitignore 排除备份和真实数据）+ 回滚=备份覆盖+删除新增文件
- 2026-08-08 — 同步模式：本地 skill 目录 = 真源，发布仓库 = 快照，低频手动同步（原因：发布是低频动作，无需自动化）
- 2026-08-08 — GitHub 发布前置：本地 git 身份需与 GitHub 账号一致（git config 配置，不在仓库内存储）
- 2026-08-08 — 菜单操作编号字母化（N 新建/D 删除/C 检查），数字序号唯一语义=打开项目（原因：消除数字双语义歧义 bug）
- 2026-08-08 — 会话回顾仅限工作类操作（打开/检测/修改/更新/保存/退出），查看/搜索/统计不触发（原因：轻操作强制回顾是体验负担）
- 2026-08-08 — 新增「打开项目」操作定义（cd + 触发会话回顾）（原因：菜单有入口但操作详情缺失）
- 2026-08-08 — 本地 skill 目录改名 project-registry，备份合并清理至轮转上限（原因：消除备份路径三分裂 + 历史残留超量）
- [✅已执行] 2026-08-08 — 决策归因机制三件套：记录纪律（决策格式升级：状态标记+原因强制+预期可选；重大决策对话中即时确认、日常决策保存补录；重决策落 ADR）+ 归因调查（"为什么X"→决策时间线/原因链/状态/后续影响）+ 内容检查 5 项（状态一致性/停滞/待办堆积/决策未落地/下一步缺失，自然语言触发不占菜单）（原因：用户核心诉求——"突然想起来能查当时为什么这么做，不能缺关键记录无据可查"；预期：任何决策可回溯归因，记录零缺口）
- [✅已执行] 2026-08-08 — 记忆管理章节写入 SKILL.md（三层机制：项目级记忆/生命周期/边界/与全局记忆分工）（原因：用户询问 skill 记忆能力，机制已运转但无集中文档；预期：记忆机制可查、边界清晰）
- [✅已执行] 2026-08-08 — 交互规则强制化：所有是/否与多选一询问必须用 AskUserQuestion 选项卡片，禁止纯文本提问（覆盖引入/骨架/类型/key确认/删除/续接）（原因：用户实测发现询问形式不稳定，有时卡片有时文本；预期：交互形式 100% 卡片化）
- [✅已执行] 2026-08-08 — grill-with-docs 引入落地为三动作：依赖表记录（标注手动调用）+ 待办顶部手动提醒（disable-model-invocation 无法代激活）+ 告知调用方式（原因：实测发现"声称已引入"但未落地，且待办可执行条目是死路；预期：引入即有据、用户知道手动触发）
- [✅已执行] 2026-08-08 — 备份轮转排序规则修正：按文件名末尾时间戳提取排序（原因：特殊命名备份 CLAUDE.md.<项目名>.<时间戳>.bak 按整名字符串排序会误删最新备份；预期：轮转永不误删）
- [✅已执行] 2026-08-08 — 会话续接询问卡片化（原因：与强制交互规则一致，消除文本示例话术残留）

## 项目范围与功能

| 包含 | 不包含 |
|:---|:---|
| SKILL.md 升级与通用化（去个人路径硬编码→~/projects/ 约定；示例名换中性虚构名；修正备份路径不一致） | PROJECTS.json 真实数据 |
| README.md（英）+ README.zh-CN.md + LICENSE(MIT) + marketplace.json + examples/ 虚构示例 + .gitignore | backups/ 目录 |
| 1-2 个 ADR（单版本决策、隐私防线） | 多 skill 集合 |
| GitHub Public 仓库发布 + 安装自测 | 会话时长管理 |

## 依赖关系

| 依赖项目 | 关系 | 说明 |
|:---|:---|:---|
| project-registry（本地安装） | 被依赖 | 本次升级改造的对象，目录 `~/.claude/skills/project-registry/` |
| Keiji-Miyake/agent-skills | 参考 | session-support 设计理念（已归档，0 星，只抄理念不当样板） |

## 待办

- [x] 备份现有 SKILL.md → backups/（20260808_102846.bak）
- [x] 本地 skill 目录 git init + 第一版 .gitignore（backups/、*.bak、PROJECTS.json）
- [x] 改造 SKILL.md：name 改 project-registry；去硬编码；吸收会话开始回顾 + 保存强制优先级下一步行动 + 可选文档骨架；示例名中性化；备份路径修正
- [x] 全文扫描验证（个人路径/用户名/真实项目名零命中）
- [x] 用户试用验收升级版 + 自动验收全面排查（6 项问题全部修复）
- [x] 创建发布仓库结构：skills/project-registry/SKILL.md + README.md(英) + README.zh-CN.md + LICENSE(MIT) + .claude-plugin/marketplace.json + examples/PROJECTS.example.json(虚构) + .gitignore + docs/adr/ + SKILL.md 补 frontmatter license/metadata（P3）
- [x] 提交 CLAUDE.md 变更并保存项目（2026-08-08 首次保存）
- [x] 改本地 git 身份为 GitHub 账号身份（P10：账号 + noreply 匿名邮箱，2026-08-08）
- [x] 用户 2 次实测反馈修复（grill-with-docs 落地/手动提醒/卡片化/续接卡片化）+ 3 次全流程自审查（2026-08-08）
- [ ] GitHub 发布（⏸️ 暂缓，用户决定先不发布；随时可恢复——建 Public 仓库 + push 前最终确认）
- [ ] 安装自测：npx skills add 试装 + /plugin marketplace add 试装（发布时一并做）

## 下一步行动

1. （⏸️ 暂缓）GitHub 发布——建 Public 仓库 + push + 安装自测；恢复条件：用户说"发布"
2. 日常使用中持续验证（新建/保存/会话回顾/归因/检查/卡片交互），发现问题记录到本文件
3. （可选）把保存流程的「备份+轮转」抽成脚本，避免手动备份漏跑轮转（测试会话曾因此积到 20 份）

## 已知问题

- （已修复）原 SKILL.md 文档与实况不一致：写死路径、备份路径指向旧目录名——升级时统一修正
- 本地 git 身份与 GitHub 账号身份配置在发布前完成（git config，不落仓库）

## 参考

- Keiji-Miyake/agent-skills: https://github.com/Keiji-Miyake/agent-skills
- britt/claude-code-skills（plugin marketplace 参考）: https://github.com/britt/claude-code-skills
- npx skills 生态: https://skills.so
