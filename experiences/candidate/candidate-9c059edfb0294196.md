---
id: candidate-9c059edfb0294196
title: 设置函数使用内部关键字；中文版 DianaIE 的查询函数返回中文名称
type: api-usage
status: draft
diana_version: "10.5"
triggers: [modelDimensions, modelAnalysisAspects, setModelDimension, setModelAnalysisAspects]
tags: [脚本, 中文界面]
manual: []
evidence: []
related: []
source: migrated
created: "2026-09-22"
updated: "2026-09-22"
community_status: candidate
confidence: "0.10"
license: Apache-2.0
public_origin: local-redacted:540e94a58f04
requires_human_review: "true"
---

## 现象

拿 modelDimensions() 的返回值（如 ['二维']）去比较或传给设置函数，结果不对或报错。

## 原因

中文界面下查询函数返回翻译后的名称，而设置函数只认内部关键字（"2D"、"STRUCT"、"MEMBRA" 等）。

## 解决

设置时一律使用内部关键字；判断状态时不要依赖查询函数返回的中文名，需要对照时用 diana_glossary。

## 验证

2026-09-19 在 DIANA 10.5 中实测：modelDimensions() 返回 ['二维']，modelAnalysisAspects() 返回 ['结构']，setModelDimension("2D") 正常。
