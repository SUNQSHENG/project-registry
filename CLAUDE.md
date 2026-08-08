# project-registry

## 项目目标

将自用 skill `project`（项目管理：PROJECTS.json 注册表）升级为更成熟通用版并开源发布到 GitHub。参考 Keiji-Miyake/agent-skills 的 session-support 设计理念（短会话优化、上下文保持、文档驱动开发、ADR）。

## 技术栈

- Claude Code Skill（SKILL.md + 标准目录结构）
- 分发：npx skills CLI 生态 + Claude Code plugin marketplace（双兼容）

## 当前状态

state: active
- 阶段：**自动保存完成并验证（v1.0.2）**——层1+层3 全链路跑通，提取质量优化两轮
- 最新进展：2026-08-08 | v1.0.2全面自检通过：层3链路验证OK、提取质量优化发布、双仓库git干净

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
- [✅已执行] 2026-08-08 — frontmatter description 改 YAML 双引号格式（74 处转义）（原因：npx skills add 安装自测发现 strict YAML 解析拒绝"Triggers: "冒号+空格——主安装路径完全不可用；预期：双路径安装全通）
- [✅已执行] 2026-08-08 — marketplace.json 改官方 schema（owner 对象 + plugins 数组 + source 字段）（原因：/plugin marketplace add 报 Invalid schema（owner/plugins 缺失）；预期：插件市场安装全通）
- [✅已执行] 2026-08-08 — 发布决策：解除暂缓，Public 仓库 + push（经本地代理 10808）+ 三条安装路径验证通过（原因：目标 B（破 50-100 星）确立 + 第 4 次审查通过；预期：星星开始累积）
- [✅已执行] 2026-08-08 — README 安装命令实测修正：/plugin install 正确写法是 project-registry@project-registry（marketplace 名 = 顶层 name 字段，非 GitHub 用户名）（原因：用户实测报 Marketplace not found；预期：安装命令 100% 可复制）
- [✅已执行] 2026-08-08 — 推广策略定稿：中文社区为主（掘金/知乎文章，业务型场景差异化蓝海）+ 英文目录提交辅助（skills.so/claudedirectory 自动触达英文用户）+ 暂不做英文亲自发帖（无账号/英文写作，投入产出为负）；SKILL.md 不英文化正文（英文 README 已覆盖门面，中文守住蓝海），改为顶部加英文简介块（原因：星星主要看 README+可发现性，SKILL.md 语言是次级因素；预期：中文转化 + 英文目录自动铺）
- [✅已执行] 2026-08-08 — 推广执行计划定稿（grill-with-docs）：目标破 100 星（用户从 500 星修正，对齐 B 档）；窗口 2 个月、每周 2-3 小时；渠道 P0-P3（topics/英文简介块/README 截图/中文文章-混合叙事/英文目录/每周小更新）；复盘机制（第 4 周 checkpoint + 第 8 周终检，数据源 GitHub Insights + 文章平台）（原因：B 档目标需执行到位而非堆量；预期：2 个月破 100）——2026-08-08 拆分后推广执行与复盘归 project_registry_promo_20260808
- [✅已执行] 2026-08-08 — 推广拆分独立项目 project_registry_promo_20260808（原因：推广生命周期（2 个月运营窗口）与开发迭代不同，混装导致 CLAUDE.md 混杂、归档牵连；预期：推广上下文聚焦，到期归档不影响本开发项目）
- [✅已执行] 2026-08-08 — 自动保存两层设计：层1 机械快照（Stop transcript 同步 + SessionEnd 备份提交，零依赖）+ 层3 通用 API 自动摘要（节流触发，任意 OpenAI 兼容，环境变量配置，未配置跳过）；**取消 CronCreate 定时层**（原因：7 天续期限制 + hooks 方案可完全替代；预期：数据永不丢 + CLAUDE.md 实时保鲜，无续期负担）
- [✅已执行] 2026-08-08 — 层3 API 通用化：支持任意 OpenAI 兼容提供商 + 用户自己的 key（原因：不绑定单一厂商，降低安装门槛，优于 memory-mcp 的强制 Anthropic key；预期：任意兼容端点可插拔）
- [✅已执行] 2026-08-08 — 首次使用配置引导（检查 PR_API_KEY → 卡片询问 → 引导设置/跳过记录）（原因：开源用户需要清晰的"配 key 有什么好处"决策；预期：只问一次，跳过不烦人）
- [⚠️ 事故复盘] 2026-08-08 — **隐私事故**：session-end 脚本曾把 .memory/（对话原文 6MB）提交进 git（本地提交 b65460a，未推送）→ 已处置：git reset 回退 + .gitignore 加 .memory/ + 脚本 git add 白名单化（只 add CLAUDE.md/.gitignore）+ make_cards.py 本地路径加固（原因：教训——**自动脚本的 git 操作必须白名单，禁止批量 add**；预期：此类事故不再发生，发布前隐私扫描排除 .memory 已成惯例）
- [✅已执行] 2026-08-08 — 层3 验证与提取质量优化两轮：①决策定义收紧（执行动作不提取，只提取影响方向/难逆转的真决策）②progress 格式统一（`日期 | 摘要`）③next_actions 改为**追加去重**（不整体替换，防吞手写内容）（原因：实测发现执行动作被误判为决策、下一步行动被覆盖丢失；预期：自动摘要与手动保存互补不互毁）
- [✅已执行] 2026-08-08 — DeepSeek API 模型名坑：用户配置名 `deepseek-v4-flash[1m]`（Claude Code 网关名）对 API 无效，官方名为 `deepseek-v4-flash`——已修正写入环境变量（原因：实测 API 报 invalid_request_error；预期：环境变量配置文档需注明官方模型名）


- [🔄进行中] 2026-08-08 — 采用官方模型名deepseek-v4-flash（原因：网关名[1m]后缀API调用无效）
- [🔄进行中] 2026-08-08 — 下一步行动合并策略改为追加去重（原因：原整体替换策略丢失手写内容）
- [🔄进行中] 2026-08-08 — 提取prompt强化决策定义与格式约束（原因：v1提取误将执行动作记为决策）
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
| project_registry_promo_20260808 | 被依赖 | 推广运营（独立项目，2026-08-08 拆分） |
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
- [x] GitHub 发布（2026-08-08：Public 仓库 + push + 三条安装路径验证通过）
- [x] **自动保存功能开发（2026-08-08 完成，v1.0.1）**：
  - [x] settings.json hooks 配置（Stop transcript 同步 / SessionEnd 备份提交 / Stop 摘要-可选）
  - [x] 脚本 1：transcript 同步（零依赖，纯本地）——干跑测试通过
  - [x] 脚本 2：通用 API 自动摘要（环境变量 PR_API_BASE_URL/KEY/MODEL，任意 OpenAI 兼容提供商；未配置自动跳过）——跳过逻辑测试通过
  - [x] 脚本 3：session-end（备份轮转 + git 提交）
  - [x] SKILL.md 新增「⚙️ 首次配置引导」+「🔁 自动保存」章节
  - [x] 发布版同步 + README 配置说明（v1.0.1 已推送）
  - [x] 全流程审查：隐私扫描（排除 .memory 零命中）+ .memory 未入库 + make_cards.py 路径加固
- [ ] 持续迭代：收集 issue/反馈


- [ ] 重启Claude Code使hooks加载DeepSeek环境变量
- [ ] 日常验证自动保存并记录提取质量问题
## 下一步行动

1. ✅ 环境变量已配置（2026-08-08：BASE_URL/KEY/MODEL=deepseek-v4-flash 写入 Windows 用户级）
2. **重启 Claude Code 后实测 hooks**：观察 .memory/ 自动更新 + 自动摘要 + SessionEnd 提交
3. 日常使用中持续验证，发现问题记录到本文件
4. 响应开源 issue/PR 反馈
5. 推广相关：见 project_registry_promo_20260808（已拆分）


6. 重启Claude Code实测hooks自动保存与SessionEnd提交
7. 持续验证层3提取质量并迭代prompt
8. 监控隐私扫描与备份轮转
## 已知问题

- （已修复）原 SKILL.md 文档与实况不一致：写死路径、备份路径指向旧目录名——升级时统一修正
- 本地 git 身份与 GitHub 账号身份配置在发布前完成（git config，不落仓库）

## 参考

- Keiji-Miyake/agent-skills: https://github.com/Keiji-Miyake/agent-skills
- britt/claude-code-skills（plugin marketplace 参考）: https://github.com/britt/claude-code-skills
- npx skills 生态: https://skills.so
