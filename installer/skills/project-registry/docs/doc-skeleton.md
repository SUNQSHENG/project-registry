# 可选文档骨架（代码/工程类项目）

> 来源：SKILL.md「📁 可选文档骨架」（v1.3.0 外置，真源同步）。
> 触发时机：新建代码/工程类项目，询问是否建立骨架时读取；用户确认建立后按此结构落盘。
> 本文件为 skill 操作指令，由 SKILL.md 索引行引用，勿单独修改。

新建代码类项目时询问是否建立（业务/文档类项目跳过）。建立后与 CLAUDE.md 分工：CLAUDE.md 记录状态和决策，骨架文档记录设计细节：

```
<项目目录>/
├── CLAUDE.md              # 开发记录（状态/决策/待办）
└── docs/
    ├── ARCHITECTURE.md    # 整体架构说明（可选）
    ├── adr/               # 架构决策记录（可选，与 grill-with-docs/domain-modeling 的 ADR 输出衔接）
    └── dev/
        ├── README.md      # 功能索引
        └── <feature>/
            ├── SPEC.md    # 功能规格
            └── DESIGN.md  # 实现设计
```

> 轻量原则：仅在用户确认时创建，不强制、不默认。
> **与 grill-with-docs 衔接**：grill-with-docs（拷问+术语+ADR）是设计**流程**，骨架是**落盘结构**——先拷问清楚，再按骨架存储。分工：轻决策记入 CLAUDE.md「架构决策记录」（一行式）；难逆转、有真实权衡的决策落 `docs/adr/`（见 docs/adr-guide.md）；术语表 CONTEXT.md 由 domain-modeling 专属维护，骨架不重复建。
