---
title: 法规动态追踪
---

# 法规动态追踪 (Regulation Tracker)

本仓库自动追踪全球产品法规动态（产品安全 / 无线 / 电池 / RoHS·REACH·PFAS / 能效 / AI 等）， 按日 / 周 / 月 / 季 / 年五种节奏自动生成报告。

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

## 📡 认证信息获取途径（官方渠道）

> 搜索法规动态时优先使用的一手官方入口（更新：2026-08-26；完整版含二手权威渠道见 [仓库知识库](https://github.com/ans1ble/regulation-tracker/blob/master/regulation-tracker/memory/certification-sources-and-platforms.md)）。

| 市场 | 官方机构 / 查询入口 | URL |
|------|---------------------|-----|
| 🇨🇳 中国 | 市监总局/认监委 · CCC 证书查询 · SRRC(工信部) | samr.gov.cn · cx.cnca.cn · miit.gov.cn |
| 🇪🇺 欧盟 | EUR-Lex 法规原文 · Safety Gate 预警 | eur-lex.europa.eu · ec.europa.eu/safety-gate |
| 🇺🇸 美国 | FCC 设备授权/FCC ID 查询/KDB · CPSC | fcc.gov/oet/ea · apps.fcc.gov/kdb · cpsc.gov |
| 🇯🇵 日本 | METI · MIC · TELEC 认证机构 | meti.go.jp · soumu.go.jp · telec.or.jp |
| 🇰🇷 韩国 | RRA 无线电研究院 · KC 认证查询 ⚠️域名待复核 | rra.go.kr |
| 🇦🇺 澳洲 | ACMA · 能效标识 GEMS | acma.gov.au · energyrating.gov.au |
| 🇧🇷 巴西 | ANATEL · INMETRO | gov.br/anatel · inmetro.gov.br |
| 🇮🇳 印度 | BIS(CRS) · TEC · WPC(Dot) | bis.gov.in · tec.gov.in · dot.gov.in |
| 🇷🇺 EAEU | 欧亚经济委员会技术法规 | eurasiancommission.org |
| 🇻🇳🇮🇩🇹🇭 越/印尼/泰 | MIC · KOMDIGI ⚠️ · NBTC | mic.gov.vn · komdigi.go.id · nbtc.go.th |
| 🇲🇽 墨西哥 | 经济部 NOM · ANCE/NYCE | gob.mx/se |
| 🇸🇦 沙特 | SASO · SABER 平台 | saso.gov.sa · saber.sa |
| 🇨🇦 加拿大 | ISED（RSS 标准/合格设备库） | ised-isde.canada.ca |
| 🇹🇷 土耳其 | 商务部 · 官方公报 | ticaret.gov.tr · resmigazete.gov.tr |
| 🇨🇱 智利 | SEC 电气监察 · SUBTEL | sec.cl · subtel.gob.cl |
| 🇳🇬 尼日利亚 | SON(SONCAP) · NCC | son.gov.ng · ncc.gov.ng |
| 🇬🇧🇭🇰🇸🇬🇹🇼 英/港/新/台 | GOV.UK · OFCA · IMDA · NCC | gov.uk · ofca.gov.hk · imda.gov.sg · ncc.gov.tw |

## 🛒 电商平台合规要求（Amazon / Temu / SHEIN / Shopee）

> 平台资质要求往往早于或严于当地法规，且 FCC 26-50 已将「平台 FCC ID 展示」写为法定义务。逐站点细则见 [仓库知识库](https://github.com/ans1ble/regulation-tracker/blob/master/regulation-tracker/memory/certification-sources-and-platforms.md)。

| 平台 | 合规要点 | 卖家中心 / 官方入口 |
|------|----------|---------------------|
| Amazon | 类目合规文件审核（CPC/FCC ID/能效/GPSR 欧代）；FCC 26-50 平台 FCC ID 展示义务适用（Cat1 2027-03-01 起） | sellercentral.amazon.com ✅ |
| Temu | 资质上传+平台审核抽检（CCC/CE/CPC/RSL），资质过期管控 | seller.temu.com ✅（海外）· seller.kuajingmaihuo.com ✅（中国商家） |
| SHEIN Marketplace | 卖家教育 Hub 分市场分品类指引；美国站门槛年营收 ≥$500 万+本土主体；与 BV/Intertek/SGS/TÜV SÜD 合办合规培训 ⚠️ 欧洲站注册清单为第三方解读 | seller-us/eu/me.shein.com ✅ |
| Shopee | 各站点强制资质差异大：印尼 NIB ✅ · 马来 MCMC/SIRIM ✅ · 泰国 TISI 链接 ⚠️ · 菲律宾 ITA PS/ICC/FDA ✅ · 越南实名核验 ⚠️ | 各站点 /edu/ 卖家教育页（如 co.id/edu/article/28082、com.my/edu/article/26534）✅ |

## 说明

- 内容含来源链接、发布日期与可信度标注（⚠️ 待核实）；不虚构。
- 知识库随时间自动进化，回写至本仓库 `memory/`。
