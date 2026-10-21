---
id: candidate-bb18d1e3f000abcf
title: 总应变裂缝模型（TSCR）常用参数的路径：转动裂缝、Hordijk 软化、抗拉强度、断裂能
type: parameter
status: draft
diana_version: "10.5"
triggers: [TSCR, TENCRV, HORDYK, TOTCRK]
tags: [材料, 混凝土, 开裂]
manual: []
evidence: []
related: []
source: migrated
created: "2026-09-22"
updated: "2026-09-22"
community_status: candidate
confidence: "0.10"
license: Apache-2.0
public_origin: local-redacted:fbeb37269dd4
requires_human_review: "true"
---

## 现象

不清楚脚本中如何设置总应变裂缝模型的各项参数。

## 原因

addMaterial(名称, "CONCR", "TSCR", []) 之后，参数都位于 TSCR 模型目录下。

## 解决

setParameter("MATERIAL", 名称, 路径, 值)：LINEAR/ELASTI/YOUNG、LINEAR/ELASTI/POISON；MODTYP/TOTCRK = "ROTATE"（转动裂缝）；TENSIL/TENCRV = "HORDYK"；TENSIL/TENSTR 抗拉强度；TENSIL/GF1 受拉断裂能；COMPRS/COMCRV = "ELASTI"（受压线弹性）。完整路径和可选值用 diana_parameters / diana_keywords 查看。

## 验证

简支梁非线性变体（fₜ = 2.5 MPa，G_F = 100 N/m）：开裂出现在 12.5–15 kN 之间，与理论开裂荷载 13.3 kN 吻合（2026-09-19）。
