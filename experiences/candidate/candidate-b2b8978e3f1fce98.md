---
id: candidate-b2b8978e3f1fce98
title: 批处理求解时用 COMMUNICATOR_CONNECTION=server=NONE 关闭 communicator
type: workflow
status: draft
diana_version: "10.5"
triggers: [communicator]
tags: [批处理, 求解]
manual: [Theory/Theoryse777.html]
evidence: []
related: []
source: migrated
created: "2026-09-22"
updated: "2026-09-22"
community_status: candidate
confidence: "0.10"
license: Apache-2.0
public_origin: local-redacted:75a624747a3b
requires_human_review: "true"
---

## 现象

批处理作业结束或被强制终止后残留 communicator.exe，或与 DianaIE 正在使用的 communicator 相互影响。

## 原因

diana.exe 默认会连接或启动 Diana Portal Communicator（本地存储服务）。

## 解决

在作业进程的环境变量中设置 COMMUNICATOR_CONNECTION=server=NONE（手册 K.7）；diana-mcp 的后台作业默认如此。

## 验证

2026-09-19：关闭 communicator 后求解正常，结果一致。
