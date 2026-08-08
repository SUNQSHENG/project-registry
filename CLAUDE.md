# project-registry

## 项目目标

将自用 skill `project`（项目管理：PROJECTS.json 注册表）升级为更成熟通用版并开源发布到 GitHub。参考 Keiji-Miyake/agent-skills 的 session-support 设计理念（短会话优化、上下文保持、文档驱动开发、ADR）。

## 技术栈

- Claude Code Skill（SKILL.md + 标准目录结构）
- 分发：npx skills CLI 生态 + Claude Code plugin marketplace（双兼容）

## 当前状态

state: active
- 阶段：**v1.0.6 发布完成**——补「手动保存怎么操作」定义（对话中对 agent 说 保存/退出，无按钮无命令）+ README 措辞修正（回顾→更新）；GIF 待续
- 最新进展：2026-08-08 | 保存项目：补录 README 措辞修正决策（回顾→更新），更新待办/下一步行动

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
- [✅已执行] 2026-08-08 — 图层编号统一：层3 → **层2**（层1 机械快照 + 层2 自动摘要）+ README 示例去硬编码（DeepSeek URL → 通用占位符）（原因：用户要求编号连贯（层1/层2），且 GitHub 示例不应绑定单一厂商；预期：文档/示例通用化，任何提供商可插拔）
- [✅已执行] 2026-08-08 — grilling 七问定方向：①目标用户=全球个人开发者（中英并行）②主定位=多项目管理，错位竞争 memory-mcp（原因：记忆赛道红海且官方 auto-memory 已覆盖，项目管理是空位；预期：差异化定位成立）③分发=双轨（npm 主 + marketplace 保留）（原因：竞品全 npm 分发，个人开发者安装习惯）④SessionStart 注入经三轮拷问**砍掉**（原因：cwd 匹配注入 80% 冗余于 CLAUDE.md 原生加载，兜底场景不存在，feature 对比是负分；预期：hooks 维持 Stop+SessionEnd 最简，不新增功能面）⑤验收=真实反馈为主 + npm 下载徽章展示，不追 star（原因：竞争力由"用的人觉得顺手"建立）
- [✅已执行] 2026-08-08 — README 双语重写：多项目管理主定位 + 电梯演讲 + Problem→Solution 表 + 对比表（vs auto-memory/memory-mcp）+ 架构分工表 + "意图驱动不打扰"哲学 + 层2 定位从卖点降级为"保鲜加分项"（原因：grilling 定位落地；预期：3 秒看懂 + 搜索命中面扩大）
- [✅已执行] 2026-08-08 — npm 安装器 @sunqsheng/project-registry v1.0.3：零依赖单文件 CLI（复制 skill + hooks 引导授权 + 幂等 + --remove），4 组测试通过（原因：双轨分发 npm 轨落地；预期：npx 一条命令安装）
- [✅已执行] 2026-08-08 — 保持命名 project-registry 不更名（原因：npm 包名已发布不可改 + 注册表即差异化标识 + 搜索不亏；预期：品牌资产延续）
- [✅已执行] 2026-08-08 — npm 发布流程定型：账号 2FA（Windows Hello 安全密钥）+ granular token（Read and write / All packages / 90 天上限）+ 真终端 EOTP 认证（原因：npm 2026-07 公告弃用 bypass2FA token、2026-08 账户变更生效，发布强制 2FA；预期：发布流程可复现）
- [✅已执行] 2026-08-08 — GitHub About 更新：description 电梯演讲 + topics 11 个（原因：主页门面对齐新定位；预期：搜索发现面扩大）
- [✅已执行] 2026-08-08 — 首次配置引导强制提醒机制：检查 2 无论是否配置 API 都必须告知用户一次「自动 API 保存不能代替手动保存」，卡片文案删误导句「无需手动保存」，「与手动保存的关系」明确不可互替、权威记录以手动保存为准（原因：用户实测发现卡片文案「无需手动保存」误导——配了 API 的用户可能误以为自动摘要可替代手动保存，导致 CLAUDE.md 权威整理缺失；预期：新用户不会跳过保存/退出时的强制整理）
- [✅已执行] 2026-08-08 — 打磨物料 grilling 决策链（9 项，grill-with-docs 产出）：①目标=GitHub 访客→星/安装转化率 ②执行顺序=GIF→对比表→徽章延后 ③GIF 工具=ScreenToGif ④GIF 演示环境=虚构数据（延续 ADR-0002 隐私防线）⑤GIF 脚本=5 镜头（清单→打开恢复→保存→强杀→重生）⑥GIF 位置=README Hero 位 ⑦对比表=加维度纵深封顶 10 行 ⑧对比表 9 行（+4：会话恢复/决策归因/健康检查/版本回滚，全切项目管理核心）⑨验收=并入 promo 复盘（4 周 checkpoint+8 周终检），徽章触发阈值=下载破百（原因：全部服务转化率目标；预期：README 门面 3 秒抓住访客）
- [✅已执行] 2026-08-08 — 对比表删除 memory-mcp 列（9 行→2 列：vs Claude Code auto-memory）（原因：官方文档核对发现「自动保鲜」行与 yuvalsuede/memory-mcp 实际能力矛盾——它核心功能就是 hooks+Haiku 自动提取到项目本地 .memory/，我们标 ❌(writes global memory) 双重错误，构成《反不正当竞争法》第 11 条商业诋毁要件（散布虚伪事实）；且 memory-mcp 同名项目 6+ 个指代不明。删列后不再指认第三方竞品，风险归零；预期：对比只对官方内置 auto-memory，无法律/声誉风险）
- [✅已执行] 2026-08-08 — README 强化「保鲜 ≠ 手动保存」段（双语，三种记忆职责段后）：层 2 自动摘要=增量草稿（实时保鲜），手动保存=权威整理（补录 WHY 决策+重排下一步），不可互替、权威版本=手动保存那份（原因：用户指出自动 API 保存命名易误导——配了 API 的用户可能跳过手动保存；与 SKILL.md v1.0.4 强制提醒形成 执行层+门面层 双重覆盖；预期：新用户明确知道保鲜不替代保存）
- [✅已执行] 2026-08-08 — **v1.0.5 全链术语改名：自动保存→自动备份（Auto-backup）**（原因：用户指出「自动保存（hooks）」名称本身误导——把数据备份（层1）与保存项目（手动权威整理）混为一谈，用户听到"自动保存"以为保存动作被自动化；改名从根上消除歧义，比加警示说明治本；范围=SKILL.md 真源/发布版/npm 副本 + README 双语 8 处 + setup.js 4 处 + session-end.py 提交消息 + npm keywords + version bump 1.0.5；预期：术语三层各司其职——自动备份（数据安全）≠保鲜（增量草稿）≠手动保存（权威整理））
- [✅已执行] 2026-08-08 — **v1.0.6 补「手动保存怎么操作」定义：手动保存 = 在对话中直接告诉 agent「保存」或「退出」（没有按钮、没有命令）**（原因：文档反复强调手动保存是权威整理、不可替代，但从未定义操作方式——新用户看到「手动保存」会以为有按钮/命令，实际就是对话里说一句话；范围=SKILL.md 两处（首次配置引导强制提醒 + 与手动保存的关系段补操作说明）+ README 双语各一处 + 四端同步（真源/发布快照/npm 副本）+ bump 1.0.6 + push/Release/npm 全链路（Release 经 git credential token 调 API 创建，gh 不可用）；预期：新用户明确知道手动保存的触发方式，不会困惑）
- [✅已执行] 2026-08-08 — README 表格措辞修正：「强制全面回顾 CLAUDE.md」→「强制全面更新 CLAUDE.md」（原因：保存动作实际是 agent 全面更新 CLAUDE.md（补录决策/重排下一步），「回顾」偏被动观察，语义不准确；范围=README 中英表格各一处，双语同步，未 bump 版本号（随下次发布一并带出），已提交推送 4248ba0）

- [🔄进行中] 2026-08-08 — 保持 skill 名称 project-registry 不变（原因：npm 包名已定死不可改，注册表是差异化标识，改名成本高收益低）
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
- [x] README 定位改为"多项目管理"并新增对比表（2026-08-08 完成，双语）
- [x] 发布 GitHub Releases v1.0.3（2026-08-08 完成）
- [x] npm 发布 @sunqsheng/project-registry v1.0.3（2026-08-08 完成，2FA+Windows Hello+granular token 全链路）
- [x] 层2 从卖点降级为加分项（2026-08-08 完成，README 定位为"保鲜"）
- [x] 重启 Claude Code 后实测 hooks（2026-08-08 完成：层1 transcript 20:00 更新、层2 last_summary 19:59、SessionEnd 提交正常）
- [x] 首次配置引导强制提醒「自动 API 保存 ≠ 手动保存」（2026-08-08 完成，v1.0.4：真源+发布快照+npm 包三处同步，push + Release + npm 发布全链路）
- [x] 竞品对比表扩到 9 行（2026-08-08 完成，双语，全切项目管理核心）→ 同日删除 memory-mcp 列（2 列：vs auto-memory）
- [x] v1.0.5 全链术语改名 自动保存→自动备份（2026-08-08 完成，push + Release + npm 全链路）
- [x] README 强化「保鲜≠手动保存」段（2026-08-08 完成，双语）
- [x] v1.0.6 补「手动保存怎么操作」说明（2026-08-08 完成：SKILL.md 两处 + README 双语 + 四端同步 + push/Release/npm 全链路）
- [x] README 表格措辞修正 回顾→更新（2026-08-08 完成，双语，已推送 4248ba0，未 bump）
- [ ] 竞品对比表完善（README 已有简版，可深化）
- [ ] 反馈渠道：issue 模板（bug/功能请求）
- [ ] README 挂 npm 下载徽章
- [ ] 上 skill 目录并在中文社区发帖引流（推广项目承载）
- [ ] token 到期续期提醒（2026-11-06，npm 90 天上限）
## 下一步行动

1. **npm 下载徽章**：下载量破百后挂（约 2 周后复查，promo 复盘时触发）
2. **反馈渠道**：建 issue 模板（bug/功能请求），开启 GitHub Discussions（如适用）
3. **token 续期提醒**：2026-11-06 到期前重新生成 npm token（90 天上限；生成后需用户在真终端跑一次发布验证，命令见已知问题——必须显式官方 registry）
4. **响应开源 issue/PR**，按真实反馈迭代（验收标准：2 周一检）
5. **推广执行**：见 project_registry_promo_20260808（中文文章 + 英文目录）
## 已知问题

- （已修复）原 SKILL.md 文档与实况不一致：写死路径、备份路径指向旧目录名——升级时统一修正
- 本地 git 身份与 GitHub 账号身份配置在发布前完成（git config，不落仓库）
- **npm token 90 天过期**（2026-11-06）：npm 对 Read and write granular token 的有效期上限，到期需重新生成
- **npm 2FA 发布必须在真终端执行**：EOTP 浏览器认证流程需要 TTY，Claude Code 内 `!` 命令无法完成
- **本机 npm 全局 registry 是 npmmirror（只读镜像）**：直接 `npm publish` 不会发布到官方且无显著报错（2026-08-08 实测 v1.0.4 首发失败）——必须显式 `npm publish --registry=https://registry.npmjs.org --https-proxy=http://127.0.0.1:10808`
- **Windows PowerShell 5.1 不支持 `&&` 分隔符**：发布命令需用 `;` 或分行（2026-08-08 实测报 ParserError）
- **demo-showcase/switch.sh 缺陷**：on 时若真实 `~/projects` 被进程占用，mv 会失败但脚本仍继续 cp → 演示数据复制成子目录污染真实目录（2026-08-08 实测，已清理）。修复方向：mv 失败即停 + 复制前检测 + 校验后置
- **gdigrab 窗口捕获依赖 wt 标题精确匹配**（`-i title=demo`）：wt 未打开或标题不符时 ffmpeg 直接 abort，录屏 0 字节且无告警衔接（2026-08-08 实测）
- **自动化驱动 Claude Code 交互会话触发安全分类器拦截**：自动 kill 进程/rm 脚本化操作需用户明确授权，否则会被 Auto-Mode 分类器拒绝（2026-08-08 实测）
- **~/demo-showcase/ 演示环境已备**（虚构 3 项目 + PROJECTS.json + switch.sh + demo_record.py + RECORDING.md），真实数据零污染已验证（PROJECTS.json 26 条 + 昌吉等抽查无改动）
- **npm bypass2FA token 已弃用**（2026-07 公告，2026-08 账户变更生效，2027-01 直接发布强制 2FA）——生成 token 勿再勾选 bypass 2FA

## 参考

- Keiji-Miyake/agent-skills: https://github.com/Keiji-Miyake/agent-skills
- britt/claude-code-skills（plugin marketplace 参考）: https://github.com/britt/claude-code-skills
- npx skills 生态: https://skills.so
