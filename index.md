---
title: 法规动态追踪
---

# 法规动态追踪 (Regulation Tracker)

本仓库自动追踪全球产品法规动态（产品安全 / 无线 / 电池 / RoHS·REACH·PFAS / 能效 / AI 等），由 GitHub Actions 按日 / 周 / 月 / 季 / 年五种节奏自动生成报告。

> 日报/周报联网检索最新动态；月报/季报/年报为基于已有报告的**离线聚合**，不联网。年份由 `date` 动态决定，跨年自动归档到对应目录。

## 报告索引

{% assign report_pages = site.pages | where_exp: "item", "item.path contains 'reports/'" %}
{% if report_pages.size == 0 %}
暂无报告。
{% else %}
{% assign years = "" | split: "," %}
{% for p in report_pages %}
{% assign parts = p.path | split: "/" %}
{% unless years contains parts[1] %}{% assign years = years | push: parts[1] %}{% endunless %}
{% endfor %}
{% assign years = years | sort | reverse %}
{% assign type_defs = "daily:日报|weekly:周报|monthly:月报|quarterly:季报|annual:年报" | split: "|" %}
{% for y in years %}
### {{ y }} 年
{% for td in type_defs %}
{% assign kv = td | split: ":" %}
{% assign t_key = kv[0] %}
{% assign t_label = kv[1] %}
{% assign prefix = "reports/" | append: y | append: "/" | append: t_key | append: "/" %}
{% assign group = report_pages | where_exp: "item", "item.path contains prefix" | sort: "path" | reverse %}
{% if group.size > 0 %}
**{{ t_label }}**（{{ group.size }} 篇）
{% for p in group %}
- [{{ p.path | split: "/" | last | replace: ".md", "" }}]({{ p.url | relative_url }})
{% endfor %}
{% endif %}
{% endfor %}
{% endfor %}
{% endif %}

## 说明

- 内容含来源链接、发布日期与可信度标注（⚠️ 待核实）；不虚构。
- 知识库随时间自动进化，回写至本仓库 `memory/`。
