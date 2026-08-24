# regulation-tracker（法规动态追踪）· 每日定时邮件

本仓库包含「法规动态追踪」skill，并通过 **GitHub Actions 每日定时** 启动 OpenCode 运行该 skill（联网抓取全球 16 个主要市场最新认证/法规动态），将生成的报告通过 **Brevo 免费 API** 发送到指定邮箱，并把进化后的知识库自动推回本仓库。

> 备选：仓库内仍保留 `.gitlab-ci.yml`（GitLab CI 版），作为另一可选运行器。当前主方案为 GitHub Actions（仓库已设为 **public**，Actions 免费可用）。**无需信用卡**。

## 工作流

```
GitHub Actions Schedule（cron 每天 01:00 UTC / 北京 09:00，或手动触发）
  → 拉取仓库（来自 GitHub 公开仓库）
  → 安装 OpenCode CLI（node:20）
  → opencode run --pure --auto --model opencode/hy3-free \
  →   读取 SKILL.md → 全球扫描模式 → 报告写入 reports/regulation-digest-YYYY-MM-DD.md
  → 将进化后的 knowledge base（memory/、MEMORY.md）与当日报告 git commit + push 回仓库（自动进化）
  → 上传报告为 Artifact（即使邮件失败也可在流水线页面下载）
  → python3 scripts/send-digest.py 通过 Brevo 免费 API 发送报告到 DIGEST_TO
```

发信优先级（`scripts/send-digest.py`）：QQ SMTP → Brevo API → Resend API。本方案仅配置 **Brevo**，故实际走 Brevo。

## 在 GitHub 上配置（无需信用卡）

仓库 **Settings → Secrets and variables → Actions**：

1. **Secrets**（加密）：
   | 名称 | 说明 |
   |------|------|
   | `BREVO_API_KEY` | Brevo 免费 API Key（Brevo 后台 → SMTP & API → API Keys） |
   | `BREVO_SENDER` | 在 Brevo **已验证**的发送邮箱（必须验证，否则发送被拒） |
   | `AGNES_API_KEY` | （可选）兜底模型密钥；主模型 `opencode/hy3-free` 免费无需密钥 |
   | `SMTP_USERNAME` / `SMTP_PASSWORD` | （可选）若设置则优先走 QQ SMTP 发信 |
2. **Variables**（明文）：
   | 名称 | 说明 |
   |------|------|
   | `DIGEST_TO` | 收件邮箱，逗号分隔，例如 `494237963@qq.com,254840491@qq.com`（**已设置**） |

> 无需设置 `GITHUB_TOKEN`：GitHub Actions 内置 `GITHUB_TOKEN`（已授予 `contents: write`）即可完成知识库回推。

3. **手动验证**：Actions 页面 → `regulation-digest-daily` → `Run workflow`。每日 01:00 UTC 自动运行。

## 你需要准备的账号

- **GitHub.com** 免费账号（仓库已 public，Actions 免费）。
- **Brevo** 免费账号（无需信用卡）：9,000 封/月；在 Senders 验证一个发送邮箱，拿到 API Key。
- （可选）**QQ 邮箱**授权码，用于 QQ SMTP 直发（送达率更高）。

### Brevo 配置步骤
1. 注册 https://brevo.com （免费、无需信用卡）。
2. Settings → SMTP & API → API Keys & MCP → Generate new API key → 得到 `BREVO_API_KEY`。
3. Settings → Senders, Domains, IPs → Senders → Add a sender（填写 From 名称 + From 邮箱），通过 6 位验证码验证 → 得到 `BREVO_SENDER`。
4. （可选）域名认证（DKIM/DMARC）提升送达率——免费邮箱域名（qq.com/gmail.com 等）无法做域名认证，只能单地址验证码验证，信任度较低，可能进 QQ 垃圾箱。

## 注意事项

- **CHECKPOINT 自动通过**：skill 中的 CHECKPOINT 本需人工确认，CI 用 `--auto` 无人值守自动继续。
- **免费模型优先**：主模型 `opencode/hy3-free`（OpenCode 免费、无需密钥）；仅当它未产出报告且配置了 `AGNES_API_KEY` 时，才切换到 `0815/agnes-2.5-flash` 兜底。
- **自动进化（知识库回写）★**：每次运行更新后的 `memory/*.md`、`MEMORY.md`、报告 `reports/regulation-digest-*.md` 会 `git commit + push` 回仓库；下一次运行从已进化的知识库出发，实现持续自我进化。
- **运行超时**：`opencode run` 设置 60 分钟超时；超时则邮件附件带上失败提示。
- **分支**：知识库回推到 `HEAD:master`（本仓库默认分支为 `master`）。
