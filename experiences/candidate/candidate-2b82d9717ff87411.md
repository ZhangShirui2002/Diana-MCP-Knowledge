---
id: candidate-2b82d9717ff87411
title: 共用同一 FILOS 数据库的分析块要放在同一个分析里，或在保留的 .ff 上续算
type: workflow
status: draft
diana_version: "10.5"
triggers: [REDUCT, ELIQUE, ECREEP, RESTOR]
tags: [分析设置, 续算, 批处理]
manual: [Theory/Theoryse713.html]
evidence: []
related: []
source: migrated
created: "2026-09-22"
updated: "2026-09-22"
community_status: candidate
confidence: "0.10"
license: Apache-2.0
public_origin: local-redacted:51c5a8dd0cc8
requires_human_review: "true"
---

## 现象

把 *NONLIN 和随后的 *REDUCT（或 *ELIQUE、*ECREEP、分阶段分析）拆成两个 DianaIE 分析分别求解，后一个读不到前一个的结果。

## 原因

这些块通过 .ff（FILOS 数据库）传递状态；每个分析单独导出、单独求解时会各自新建 .ff。

## 解决

作为同一个分析中的多个命令一起求解；或先求解并保留 .ff（keep_ff=true），再用 diana_run_solver(restart_ff=…) 在其上运行后续块。

## 验证

依据手册附录 H.2 和 2026-09-19 的手册审查（docs/manual-audit.md）；续算功能有单元测试（tests/test_jobs.py）。尚未在真实模型上做反例对比。
