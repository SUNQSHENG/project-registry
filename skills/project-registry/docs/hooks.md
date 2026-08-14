# 自动备份 hooks 细节（排障向）

> 来源：SKILL.md「🔁 自动备份（hooks，静默执行）」（v1.3.0 外置，真源同步）。
> 触发时机：用户咨询自动备份机制、排障（备份没生效/报错）时读取。
> 本文件为 skill 操作指令，由 SKILL.md 索引行引用，勿单独修改。

两层机制，全部后台静默、失败静默重试、只在**项目根**（默认 `~/projects/`）项目目录生效。

### 层 1 机械快照（零依赖，默认开启）

| Hook | 动作 |
|:---|:---|
| Stop（每次响应后） | transcript 存档到 `<项目>/.memory/transcripts/`（秒级，按会话幂等） |
| SessionEnd（会话结束） | CLAUDE.md 备份（10 份轮转）+ git 提交（有变更才提交） |

- 定位方式：hook stdin `transcript_path` 反推项目目录（不依赖进程 cwd，CLI/IDE 扩展通吃，见 SKILL.md「cwd 纪律」原理）
- ⚠️ **已知限制（IDE 扩展）**：VSCode 扩展下 Stop hook 存在官方已知 bug 可能不触发（anthropics/claude-code#49851，随 Claude Code 版本修复）——该环境下自动备份可能暂停；CLI 环境不受影响
- ⚠️ **隐私**：`.memory/` 含对话原文——**必须 gitignore 排除**（新建项目自动生成 .gitignore 含 `.memory/`），绝不进仓库
- 强杀终端时 SessionEnd 不触发，但 Stop 的秒级同步仍在——数据不丢

### transcript 历史存档（兜底原文）

- **写入**：Stop 同步时按会话存档到 `<项目>/.memory/transcripts/<会话ID>.jsonl`（幂等，同一会话覆盖；跨会话保留原文）
- **用途**：会话回顾的「未入账兜底」——CLAUDE.md 保存时刻（saved_at）之后的对话原文可查（见 SKILL.md「会话开始流程」步骤 5）
- **隐私**：`.memory/` 已 gitignore，对话原文永不进仓库

### check_unread.py 判定要点（脚本逻辑/排障）

`scripts/check_unread.py <项目目录>` 一次输出判定结果 + 尾部快览，**双格式兼容**：

- 读 `.memory/state.json` 的 `saved_at` → 缺失（旧项目）→ `UNREAD=1` 保守触发 → 存在 → **单步判定**：最新存档中是否存在 `saved_at` 之后产生的实质 user 消息 → `UNREAD=0/1` + 有则尾部 30 条快览
- **双格式兼容**：Claude Code transcript 两种格式——
  - 旧格式（≤2.1.x 早期）：消息体在顶层 `content`、`timestamp` 为数字
  - 新格式（v2.1.226+）：消息体在 `message` 字段（两种形态：直接 dict 对象取 `content`；字符串化 dict 用 `ast.literal_eval`/`json.loads` 解析后取）、`timestamp` 为 ISO 字符串（转 epoch 秒与 saved_at 同基准比较）
  - 两者都要求：type=user、content 非空文本、**跳过 `isMeta` 消息**；解析失败保守跳过（宁漏勿误）
- **排障**：判定恒空 → 检查存档是否为 v2.1.226+ 新格式（message 字段）；`saved_at` 类型异常（字符串）→ 脚本已 isinstance 兜底，非数字一律 UNREAD=1 保守触发
