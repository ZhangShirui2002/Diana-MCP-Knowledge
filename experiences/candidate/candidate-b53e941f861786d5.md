---
id: candidate-b53e941f861786d5
title: DIANA 没有固定单位制，所有输入必须使用同一套单位
type: modeling-pitfall
status: draft
diana_version: "10.5"
triggers: [setUnit, setUnitSet]
tags: [单位, 建模]
manual: [Theory/Theorych5.html, Theory/Theoryse587.html]
evidence: []
related: []
source: migrated
created: "2026-09-22"
updated: "2026-09-22"
community_status: candidate
confidence: "0.10"
license: Apache-2.0
public_origin: local-redacted:ad50193aa22e
requires_human_review: "true"
---

## 现象

同一模型中混用 m 与 mm（或 N 与 kN），计算能正常结束，但位移、应力相差若干数量级；重力加速度、密度、弹性模量最容易出错。

## 原因

DIANA 不做单位换算，数值按当前单位制原样使用（unit(q) 查询，setUnit / setUnitSet 设置）。手册第 5 章表 5.1 列出一致的单位制组合。

## 解决

建模前先确认或设置单位（diana_model_summary 会列出当前单位），所有参数换算到同一单位制后再输入。例如 m-N-kg 制：E = 3e10 Pa，重力 -9.81，密度 2400；mm-N-t 制：E = 3e4 MPa，重力 -9810，密度 2.4e-9。

## 验证

简支梁示例采用 m-N-kg 制，跨中挠度与 Timoshenko 理论解相差 +0.8%（2026-09-19）。
