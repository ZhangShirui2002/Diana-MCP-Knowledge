# DIANA-MCP Community Knowledge

[中文](#中文) · [English](#english)

## 中文

这是 [DIANA-MCP](https://github.com/ZhangShirui2002/Diana-MCP) 的可选公共经验层。它只保存经过脱敏的通用建模经验、结构化复现反馈和自动生成的可信度索引；不保存 DIANA 软件、用户手册、客户模型、原始日志或求解结果。

社区仓库由自动化维护，但“自动合并”不等于“自动认定正确”：

- 新经验经过 schema、DCO、许可证、隐私、提示注入和可执行内容检查后，只能进入 `candidate`；
- 贡献内容永远不会作为代码执行；PR 只允许修改 `experiences/candidate/*.md` 或 `confirmations/*.json`；
- 三个独立贡献者/环境成功复现且没有失败记录时，索引可提升为 `community-confirmed`；
- 成功与失败反馈冲突时自动标为 `disputed`；
- `reproducibly-verified` 仅保留给受信、声明式 DIANA 测试，普通 PR 不能自行声明；
- DIANA-MCP 默认不联网，只有用户显式执行 `knowledge community sync` 才同步此仓库。

### 推荐贡献流程

```powershell
python -m diana_mcp knowledge community status
python -m diana_mcp knowledge community redact <本地经验-id>
python -m diana_mcp knowledge community preview <batch-id>
# 完整审阅后，确认短语必须逐字匹配：
python -m diana_mcp knowledge community contribute <batch-id> --confirm "UPLOAD <batch-id>"
```

本地 `knowledge/` 永不直接连接到本仓库。脱敏候选会写入独立 staging 目录，并删除原始证据路径、审批记录、检查记录和可执行验证脚本。自动脱敏仍不能识别所有项目语义；提交前必须人工检查几何、材料、荷载、结果值、试验编号和版权内容。

贡献即表示你拥有提交内容的权利，并同意以 Apache-2.0 许可发布。每个提交须带 `Signed-off-by`，参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## English

This is the optional public experience layer for [DIANA-MCP](https://github.com/ZhangShirui2002/Diana-MCP). It stores only redacted, reusable lessons, structured reproduction reports, and a generated trust index. It does not contain DIANA software or manuals, customer models, raw logs, or solver results.

Data-only pull requests are checked and may be merged automatically, but new lessons remain low-trust `candidate` entries. Community confirmation requires independent successful reproductions; conflicting outcomes become `disputed`. No contributed code is executed. See [CONTRIBUTING.md](CONTRIBUTING.md) before contributing.

## Repository layout

```text
experiences/candidate/       redacted, unverified lessons
confirmations/               structured success/failure reproductions
schema/                      public data contracts
scripts/                     trusted validators from the default branch
index.json                   generated effective status and confidence
.github/workflows/           data-only acceptance and index rebuild
```

## License and trademark

Community-authored content in this repository is licensed under Apache-2.0. DIANA is a product and trademark of its respective owner. This independent repository grants no rights to DIANA software, manuals, licenses, trademarks, or third-party engineering data.
