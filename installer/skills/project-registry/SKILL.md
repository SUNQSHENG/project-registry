---
name: project-registry
description: "Use when the user asks to list, create, delete, modify, search, view project details, save a project, exit a project, roll back a version, or update project development records for projects managed in ~/projects/PROJECTS.json. Triggers: \"查看/列出项目\", \"新建/创建项目\", \"删除项目\", \"修改项目\", \"搜索项目\", \"项目详情\", \"项目统计\", \"项目清单\", \"项目列表\", \"保存项目\", \"退出\", \"返回\", \"更新记录\", \"开发记录\", \"项目上下文\", \"进度记录\", \"回滚\", \"恢复版本\", \"版本回滚\", \"撤销保存\", \"检查项目\", \"体检\", \"为什么\", \"归因\", \"决策背景\", \"audit\". English triggers: \"list/create/delete/save project\", \"project registry\", \"project status\", \"progress record\", \"project context\", \"rollback\", \"restore version\", \"why\", \"attribution\", \"audit\", \"project check\"."
---

# project-registry

> **EN** — A Claude Code skill that manages a personal project registry (`~/projects/PROJECTS.json`) with per-project AI-readable development logs (CLAUDE.md): list, create, delete, save, session-resume, decision attribution, health check and version rollback from one menu. The UI text is Chinese-first, but **triggers work in both Chinese and English and every feature is fully functional regardless of language** (the AI understands both). Install: `npx skills add SUNQSHENG/project-registry` or `/plugin marketplace add SUNQSHENG/project-registry`.

> 📚 **外置文档索引（触发时先读对应文档再执行）**：首配引导/设置项目路径 → `docs/first-run.md` ｜ 版本回滚 → `docs/rollback.md` ｜ 归因调查/项目检查 → `docs/attribution.md` ｜ 重决策 ADR → `docs/adr-guide.md` ｜ 可选文档骨架 → `docs/doc-skeleton.md` ｜ 自动备份 hooks 细节/check_unread 判定要点 → `docs/hooks.md` ｜ 决策纪律分层/归档规则 → `docs/decision-discipline.md` ｜ 记忆管理/CLAUDE.md 维护 → `docs/memory.md` ｜ 新建项目模板 → `docs/template.md`

## 概述

管理 `~/projects/PROJECTS.json` 注册的项目清单，提供项目的增删改查和统计功能。项目以 `<key>/` 子目录形式存放在 `~/projects/` 下，每个项目包含 README.md 记录背景和范围。

操作项目时自动 `cd` 到对应项目目录。

## 数据源

```
<项目根>/
  PROJECTS.json    # 项目注册清单（唯一权威来源）
  <key>/           # 项目目录
    README.md      # 项目背景和范围说明（面向人）
    CLAUDE.md      # 项目开发记录（面向 AI，每次对话自动加载）
```

所有项目**必须**存放在**项目根**目录下。项目根**默认 `~/projects/`**，可在首次引导「检查 2」或说「设置项目路径」自定义（写入 skill config.json 的 `projectsRoot`，hooks 脚本自动读取；流程见 `docs/first-run.md`）。本文档所有 `~/projects/` 均指项目根。

> **区别：** README.md 给开发者/协作者看项目概况；CLAUDE.md 给 AI 看，记录开发过程中的决策、状态、上下文，确保长项目不丢失信息。

### PROJECTS.json 结构

```json
{
  "description": "项目清单 — 所有项目在此登记",
  "updated": "2026-03-01",
  "nextSeq": 3,
  "projects": [
    {
      "seq": 1,
      "key": "pet_hospital_crm_20260301",
      "name": "宠物医院CRM",
      "status": "已完成",
      "created": "2026-03-01"
    }
  ]
}
```

## 操作入口

每次进入 skill 时，先 `cd ~` 回到用户根目录，然后读取 PROJECTS.json 展示清单和精简菜单（不做目录级检测）：

```
📋 当前项目清单（共 N 个）
┌─────┬────────────────────┬────────────┬──────────────┬──────────┐
│ 序号 │ key                │ 名称       │ 状态         │ 创建日期  │
├─────┼────────────────────┼────────────┼──────────────┼──────────┤
│ 1   │ pet_hospital_crm_… │ 宠物医院CRM│ ✅ 已完成     │ 2026-03-01│
│ 2   │ gym_members_app_…  │ 健身房会员App│ 🔄 进行中   │ 2026-03-15│
└─────┴────────────────────┴────────────┴──────────────┴──────────┘

> 初始展示仅读 JSON 不做目录检测（目录状态 MD检查 时检测）。

请选择操作（或直接说需求）：
 - 输入项目**序号**（1-99）→ 打开对应项目
 - 🆕 N. 新建项目 ｜ 🗑️ D. 删除项目 ｜ 🔍 C. MD检查

> 其他需求（修改/搜索/统计/更新记录/保存/退出/**检查项目**/**为什么 XX**）直接在对话中说即可
> ⚠️ **保存/退出时会自动更新 CLAUDE.md**（强制规则）
```

## ⚙️ 首次配置引导

第一次进入 skill 时**逐项检查两项配置**（hooks 是否启用、项目根路径是否自定义；每项 AskUserQuestion 卡片询问，跳过即记录只问一次）——**先读 `docs/first-run.md` 按完整流程执行**。

> 随时说「设置项目路径」可重新引导迁移（流程同 docs/first-run.md）。

## 🔍 自动识别当前项目

> 每次进入 skill 时已自动 `cd ~`。需要定位项目的操作（检测/修改/保存/更新记录等）自动识别当前目录：

```
1. pwd 检查是否匹配 <项目根>/<key>/（项目根默认 `~/projects/`）
2. 匹配 → 自动选定该项目
3. 不匹配 → 手动选择（按序号或 key）
```

## 🧭 会话开始流程（上下文恢复）

**仅对「进入项目工作」类操作触发**：打开项目 / 检测 / 修改 / 更新记录 / 保存 / 退出。查看详情、搜索、统计等轻操作**不触发**。

进入项目后、执行操作前，**先回顾上下文再续接**（防止长项目信息丢失、中断后重新进入不知从何下手）：

1. 读取该项目的 CLAUDE.md（若存在）
2. 摘要上次进展：引用「当前状态 / 最新进展」，必要时结合 git log 最近提交
3. 列出「下一步行动」（按优先级 1. 2. 3. …）
4. **不弹续接卡片**——直接等用户说需求；用户未指明时按优先级 1 开始
5. **transcript 兜底判定**（未入账检测，双重保险）——**调用 `scripts/check_unread.py <项目目录>` 单次完成**：
   - 输出 `UNREAD=0/1`（saved_at 之后是否存在实质 user 消息；脚本逻辑/双格式兼容见 `docs/hooks.md`）+ 有则尾部 30 条快览
   - `UNREAD=0` → **残留同步** → **静默跳过**，不读尾部
   - `UNREAD=1` → **触发** → 尾部快览入摘要；未入账量大（>30 条）→ **弹 AskUserQuestion 卡片**：完整读 / 读尾部 / 跳过（成本用户决策）
   - ⚠️ **串扰分辨（先行）**：存档为整个会话（跨项目时会含其他项目对话）——读取时**分辨内容归属**，只提取当前项目相关内容并入摘要，其他项目内容忽略；**若 saved_at 后实质 user 消息均为「非未入账内容」→ 视为无未入账，静默跳过（不弹卡、不入摘要）**。「非未入账内容」= 其他项目内容（跨项目串扰，判定阶段无法自动切分消息归属，已定案）+ 保存/退出流程命令及流程自身响应（**旧版保存的项目 saved_at 未校准，命令在基准后**，迁移兼容）。误触发成本=一次毫秒级尾部读取
   - **不触发** → 只读 CLAUDE.md（常态，零额外成本）

示例话术：`📌 上次进展摘要：…` + `📌 当前项目：<key>（会话归档写入此项目，transcript 兜底激活）` + `➡️ 下一步行动（按优先级）：1. … 2. …` + `请直接说需求`

> 新项目（CLAUDE.md 刚创建）可跳过回顾，直接进入操作。

### 📂 打开项目

1. 按序号或 key 定位项目 → 校验 `<项目根>/<key>/` 目录存在（项目根默认 `~/projects/`）
2. `cd` 到项目目录
3. **触发「🧭 会话开始流程」**（回顾上次进展）
4. **声明当前项目**：「📌 当前项目：`<key>`，会话归档写入此项目，transcript 兜底激活」——会话级显式绑定，操作聚焦本项目
5. 用户在项目内开始工作后，按需操作（修改/更新记录/保存/退出）

### 🔄 项目切换（保存提醒）

会话中从项目 A 切到项目 B（cwd 变更）时，**必须弹 AskUserQuestion 卡片**：「项目 A 有未保存工作——保存 / 稍后」：

- **保存** → 按「💾 保存项目」流程执行 A 的 CLAUDE.md 全面更新（全面回顾 + 决策补录 + 下一步行动），再切换
- **稍后** → 直接切换，并把「切回 A 时优先保存」记入当前待办

切换完成后，**按 A2 声明新项目**（「📌 当前项目：`<B>`」）。

## 操作详情

> 📌 **交互规则（强制）**：所有需要用户「是/否」或「多选一」的询问，**必须使用 AskUserQuestion 工具以选项卡片呈现**（两个及以上选项按钮），**禁止用纯文本提问**。适用场景：是否引入 grill-with-docs、是否建立文档骨架、项目类型确认、key/背景确认（按建议 or 修改）、删除确认、**项目切换保存提醒**、路径自定义与迁移确认等。

### 🆕 新建项目

1. 询问项目名称 + 背景说明，生成 key：`<英文缩写>_<YYYYMMDD>`
2. 备份 PROJECTS.json → 创建目录 → 写入 README.md + CLAUDE.md + `.gitignore`（含 `PROJECTS.json`、`backups/`、`*.bak`、`.memory/`、`.archive/`）
3. 注册到 PROJECTS.json（seq = nextSeq, 之后 nextSeq +1）
4. `cd` 到项目目录，`git init`
5. 必须询问是否引入 grill-with-docs skill（**AskUserQuestion 卡片：引入 / 不引入**）：
   - **同意** → 落实三个动作（不是口头"已引入"）：
     ① CLAUDE.md「依赖关系」表记录：`| grill-with-docs | 引入 | 设计拷问流程（需用户手动调用 /grill-with-docs）|`
     ② 初始待办顶部加**一条提醒**（标注「手动」，非可执行任务）：`- [ ] 📌 提醒（手动）：设计/规划时输入 /grill-with-docs 启动拷问（该 skill 仅限用户手动调用，AI 无法代激活）`
     ③ 明确告知调用方式：「首次设计/规划时**手动输入** /grill-with-docs」
   - **拒绝** → 不记录、不加入待办，正常继续
6. **代码/工程类项目**：询问是否建立可选文档骨架（**AskUserQuestion 卡片：建立 / 跳过**；结构见 `docs/doc-skeleton.md`）；业务/文档类项目跳过

CLAUDE.md 初始模板见 `docs/template.md`。

### 🗑️ 删除项目

1. 定位项目 → 列出 JSON 条目 + 目录文件清单 → 标注不可逆风险
2. 用户确认后：备份 PROJECTS.json → 删除 JSON 条目 → 删除项目目录 → 剩余项目从 1 连续重编号 → nextSeq = max(seq) + 1

### 📂 设置项目路径

用户说「设置项目路径 / 更改项目目录」时触发——**先读 `docs/first-run.md` 按完整流程执行**（卡片询问 → 写入 projectsRoot → 存量迁移确认 → 校验）。

### 💾 保存项目

1. **备份** CLAUDE.md（到 `<skill 目录>/backups/`，即 `~/.claude/skills/project-registry/backups/`）
2. **写保存时刻**（transcript 兜底基准）：`.memory/state.json` 写 `saved_at` = 当前最新 transcript 存档的 mtime（与当前时间偏差 >5 分钟则告警；文件不存在则记当前时间）。**结束时校准**：步骤 4 提交后，再读一次最新存档 mtime 写回 `saved_at`（原因：「保存/退出」命令本身的 user 消息 timestamp 可能晚于开始时写入的 saved_at——不校准则下次进入必误报「未入账」）
3. **回顾本次对话**，将以下内容追加或更新到 CLAUDE.md：
   - **归档检查（前置）**：若「架构决策记录」>30 条 或 CLAUDE.md >20KB → **先归档**最旧批次到 `.archive/decision-archive-<YYYYMMDD>.md`（同日可多次追加），CLAUDE.md 决策记录顶部留索引行（规则见 `docs/decision-discipline.md`）
   - 最新进展和完成事项
   - 新增的架构决策（日常决策按「📜 决策记录纪律」格式补录，**原因不可省略**）
   - 更新待办列表（已完成项标记 ✅，新增项添加）
   - 更新已知问题
   - ⚠️ **「下一步行动」必须按优先级列出（1. 2. 3.），不可省略**（下次会话从这里续接）
   - ⚠️ **写入侧归属核查（硬防线）**：待办 / 下一步行动 / 已知问题写入前**逐条验证归属**——条目须能从本项目上下文解释；无法解释的条目 = 疑似跨项目串扰 → **禁止写入**，单独列出询问用户归属（实证：本项目曾混入量化项目待办长期未察觉）
4. **提交** CLAUDE.md 变更到 git
5. **建议下一步工具**：根据项目内容和待办，提示可能用到的 skill（如 ppt-master / docx / xlsx / pdf 等），供用户决定
6. **保存后不退出，留在当前目录**

> ⚠️ CLAUDE.md 自动更新是强制规则，不可跳过。

### 🚪 退出项目

同保存操作，但最后一步**退回 `~`**：

1. **备份** CLAUDE.md
2. **回顾本次对话**更新 CLAUDE.md（含「下一步行动」按优先级）
3. **提交** 变更到 git
4. **建议下一步工具**（同保存流程）
5. **退出后直接退回 `~`**

### 🔍 MD检查（批量检测所有项目 CLAUDE.md 状态）

对所有已注册项目批量检查 CLAUDE.md 是否有效（无需手动选择）：

1. 遍历所有项目目录，检查以下 3 项：
   - 目录是否存在
   - CLAUDE.md 是否存在
   - `.git` 是否存在（CLAUDE.md 生效前提：必须与 `.git` 同级）
2. 输出汇总表格：

```
🔍 MD 健康检查（共 N 个项目）
┌─────┬────────────────────┬────────────┬──────────┬──────────┬──────────┬──────────┐
│ 序号 │ key                │ 项目名称   │ 目录存在 │ CLAUDE.md│ .git     │ 有效?   │
├─────┼────────────────────┼────────────┼──────────┼──────────┼──────────┼──────────┤
│ 1   │ pet_hospital_crm_… │ 宠物医院CRM│ ✅       │ ✅       │ ✅       │ ✅      │
│ ... │ ...                │ ...        │ ...      │ ...      │ ...      │ ...      │
└─────┴────────────────────┴────────────┴──────────┴──────────┴──────────┴──────────┘
```

3. 对「有效?」为 ❌ 的项目，逐个定位问题：
   - 目录不存在 → 检查 JSON 注册是否有残留
   - CLAUDE.md 缺失 → 用模板补创建
   - `.git` 缺失 → 执行 `git init`
4. 自动 `cd` 到用户根目录（不进入具体项目）

## 自动 cd + CLAUDE.md 自动更新

| 操作 | cd | CLAUDE.md 自动更新 |
|:---|:---|:---:|
| 新建 | 进入项目目录 | ✅ 自动创建初始模板 |
| 检测/修改 | 进入项目目录 | ❌ 不自动更新 |
| 更新记录 | 进入项目目录 | ✅ 手动触发更新 |
| 保存 | 进入项目目录，**保存后不退出，留在目录** | ✅ 自动更新 |
| 退出/返回 | **先更新 CLAUDE.md，再退回 `~`** | ✅ 自动更新 |

### 📌 cwd 纪律（强制）

打开项目后**持续保持 cwd 在项目根目录**；临时读外部文件优先用**绝对路径**；确需 cd 离开时，读完**立即切回项目根**。任何跨目录操作结束时，`pwd` 确认在项目根。

> **原理**：hooks 脚本定位项目**不依赖进程 cwd**（v1.2.4 起）——hook stdin 的 `transcript_path` 含项目目录编码，脚本按项目清单编码名反推并校验目录存在（stdin `cwd` 二级 fallback；仅手动运行才用 `os.getcwd()`）。cwd 纪律保留为**操作习惯**（避免单条命令 cd 混乱、保持上下文聚焦），不再是备份生效的唯一决定因素。

## 安全机制

**写操作必先备份**（PROJECTS.json 的新建/修改/删除；CLAUDE.md 的更新/保存自动更新），备份到 `<skill 目录>/backups/`（即 `~/.claude/skills/<skill-name>/backups/`），文件名 `<目标>.<YYYYMMDD_HHMMSS>.bak`（目录不存在自动创建）。

**备份自动轮转**：每次新建备份后按文件类型清理，每种类型保留最近 **10 份**：

```
备份类型前缀：PROJECTS.json.*.bak（注册表）| CLAUDE.md.*.bak（开发记录）| SKILL.md.*.bak（skill 自身）
```

清理规则：按文件名**末尾**的 `YYYYMMDD_HHMMSS` 提取时间戳排序（注意：`CLAUDE.md.<项目名>.<时间戳>.bak` 特殊命名备份，时间戳在末尾，不能用整名字符串排序），保留最晚 10 份，其余删除。

## 🔁 自动备份（hooks，静默执行）

两层机制后台静默运行（层1 机械快照：Stop transcript 存档 + SessionEnd 备份提交；transcript 历史存档兜底原文），只在项目根项目目录生效。**细节/排障见 `docs/hooks.md`**。

> **手动保存怎么操作？** 在对话中对 agent 说「保存」或「退出」即可——没有独立按钮或命令。agent 会执行 CLAUDE.md 全面更新（全面回顾 + 补录决策及原因 + 按优先级重排下一步行动）。**随时可以说**。

## 📜 决策记录纪律（查必有据）

所有决策必须可回溯：**「为什么这么做」永远可查，原因不可省略**。

**轻决策一行式格式：**

```
- [状态] YYYY-MM-DD — <决策>（原因：<理由>）（预期：<效果>）
```

- 状态标记：`✅已执行` / `🔄进行中` / `⛔被推翻` / `⏸️搁置`
- 原因**强制**：无原因不上记录
- 预期**可选**：记录时已知预期效果则补上（归因时用于验证效果）
- **记录时机分层**见 `docs/decision-discipline.md`（重大决策对话中即时确认 / 日常决策保存补录）
- **决策滚动归档**：决策记录 >30 条 或 CLAUDE.md >20KB → 归档最旧批次到 `.archive/`，CLAUDE.md 留索引行（规则见 `docs/decision-discipline.md`）
- **重决策 → ADR**：难逆转、有真实权衡的决策落 `docs/adr/`（结构见 `docs/adr-guide.md`）

CLAUDE.md 初始模板见 `docs/template.md`（新建项目时读取，逐字使用）。

## key 命名规则

```
<英文/拼音缩写>_<YYYYMMDD>

示例:
  宠物医院CRM      → pet_hospital_crm_20260301
  健身房会员App    → gym_members_app_20260315
```

- 英文优先，拼音备选
- 全小写，下划线分隔
- 尾部加日期

## 序号管理规则

| 操作 | 规则 |
|------|------|
| 新建 | 读取 `nextSeq` 作为新项目的 seq，注册后 `nextSeq` +1 |
| 删除 | 删除后剩余项目从 1 开始连续重新编号，`nextSeq` 设为 `max(seq) + 1` |
| seq | 始终连续，永不跳号 |

## 🔎 归因调查 / 📋 项目检查

用户说「为什么 X / 归因 / 决策背景」或「检查项目 / 体检 / audit」时触发——**先读 `docs/attribution.md` 按完整流程执行**（归因调查四步流程 + 项目检查 5 维度；含决策滚动归档的顺读规则）。

## ↩️ 版本回滚

用户说「回滚 / 恢复版本 / 退回 / 撤销保存」时触发——**先读 `docs/rollback.md` 按完整流程执行**（双通道数据源 git+备份快照，三个回滚对象：CLAUDE.md / 项目文件 / 注册表；安全规则：先备份、差异摘要卡片确认、新提交不改写历史）。

## 🧠 记忆管理 / CLAUDE.md 维护

记忆三层机制 / 生命周期 / 记忆边界 / 与全局记忆分工 / CLAUDE.md 维护规则——**见 `docs/memory.md`**（记录：决策及原因/约定/术语/待办/状态/下一步行动；不记录：详细实现/git 可回溯变更/临时讨论；CLAUDE.md 生效条件：与 `.git` 同级）。

## 常见问题

- **PROJECTS.json 不存在**：用默认模板创建空清单
- **目录已存在**：复用现有目录，仅注册 JSON
- **删除时找不到项目**：先列出清单让用户确认
