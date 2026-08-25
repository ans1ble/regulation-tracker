---
title: 法规动态追踪
---

# 法规动态追踪 (Regulation Tracker)

本仓库自动追踪全球产品法规动态（产品安全 / 无线 / 电池 / RoHS·REACH·PFAS / 能效 / AI 等），由 GitHub Actions 按五种节奏生成报告：

| 节奏 | 触发时间（北京时间） | 输出目录 | 文件名格式 |
|------|----------------------|----------|------------|
| 日报 | 每天 09:00（UTC 01:00） | `reports/<年>/daily/` | `regulation-digest-YYYY-MM-DD.md` |
| 周报 | 每周日 09:00（UTC 01:00） | `reports/<年>/weekly/` | `regulation-digest-YYYY-Www.md` |
| 月报 | 每月 1 日 10:00（UTC 02:00） | `reports/<年>/monthly/` | `regulation-digest-YYYY-MM.md` |
| 季报 | 每季首月 1 日 10:00（UTC 02:00） | `reports/<年>/quarterly/` | `regulation-digest-YYYY-Qn.md` |
| 年报 | 每年 1 月 1 日 11:00（UTC 03:00） | `reports/<年>/annual/` | `regulation-digest-YYYY.md` |

> 日报/周报联网检索最新动态；月报/季报/年报为基于已有报告的**离线聚合**，不联网。年份由 `date` 动态决定，跨年自动归档到对应目录。

## 报告入口

- 周报（最新示例）：[regulation-digest-2026-W28](reports/2026/weekly/regulation-digest-2026-W28.md)
- 其余节奏的报告在对应目录中按文件名归档。

## 说明

- 内容含来源链接、发布日期与可信度标注（⚠️ 待核实）；不虚构。
- 知识库随时间自动进化，回写至本仓库 `memory/`。

<!-- 重建触发 2026-08-25 -->
