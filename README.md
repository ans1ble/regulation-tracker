# regulation-tracker（法规动态追踪 · 每日定时邮件）

本仓库包含「法规动态追踪」skill，并通过 **GitLab CI 每日定时** 启动 OpenCode 运行该 skill（联网抓取全球 16 个市场最新认证法规），将生成的报告通过 **Brevo 免费 API** 发送到指定邮箱，并把进化后的知识库自动推回 GitHub 私有仓库。

> 备选：仓库里仍保留 `.github/workflows/regulation-digest.yml`（GitHub Actions 版），但因私有仓库 GitHub Actions 被账户账单限制挡住（需付费计划/提升支出限额），改用 GitLab CI 作为可用的运行器。**无需信用卡**。

## 工作流程

```
GitLab CI Schedule（cron 每天 01:00 UTC / 北京 09:00，或手动触发）
  ├─ 拉取仓库（来自 GitHub 私有仓库的镜像或同仓库）
  ├─ 安装 OpenCode CLI（node:20 镜像）
  ├─ opencode run --pure --auto --model opencode/hy3-free \
  │     读取 SKILL.md → 全球扫描模式 → 报告写入 reports/regulation-digest-YYYY-MM-DD.md
  ├─ 将进化后的 knowledge base（memory/、MEMORY.md）与当日报告 git commit + push 回 GitHub 私有仓库（自动进化）
  ├─ 上传报告为 Artifact（即使邮件失败也可在流水线页面下载）
  └─ python3 scripts/send-digest.py 通过 Brevo 免费 API 发送报告到 DIGEST_TO
```

发信优先级（`scripts/send-digest.py`）：QQ SMTP → Brevo API → Resend API。本方案只配置 **Brevo**，因此实际走 Brevo。

## 在 GitLab 上配置（无需信用卡）

1. 把本仓库推到 GitLab（新建 Project → Import → 从 GitHub 导入，或 `git push` 到 GitLab）。
2. **Settings → CI/CD → Variables**（逐项添加，勾选 `Masked`）：
   | 名称 | 说明 |
   |------|------|
   | `GITHUB_TOKEN` | GitHub 个人访问令牌（勾选 `repo` 权限），用于把知识库推回 GitHub 私有仓库 |
   | `BREVO_API_KEY` | Brevo 免费 API Key（Brevo 后台 → SMTP & API → API Keys） |
   | `BREVO_SENDER` | 在 Brevo **已验证**的发件邮箱（必须验证，否则发送被拒） |
   | `DIGEST_TO` | 收件邮箱，逗号分隔，例如 `494237963@qq.com,254840491@qq.com` |
   | `AGNES_API_KEY` | （可选）兜底模型密钥；主模型 `opencode/hy3-free` 免费无需密钥 |
3. **CI/CD → Schedules** 新建定时任务：Cron `0 1 * * *`、时区 UTC，对应北京 09:00。也可在流水线页面点 `Run pipeline`（来源 `web`）手动触发。

## 你需要准备的账号

- **GitLab.com** 免费账号（无需信用卡）：免费私有仓库 + 400 分钟/月 CI。
- **Brevo** 免费账号（无需信用卡）：9,000 封/月；在 Senders 里验证一个发件邮箱，拿到 API Key。
- **GitHub 个人访问令牌**：用于知识库回推（在 GitHub → Settings → Developer settings → PAT 生成，勾 `repo`）。

## 注意事项

- **CHECKPOINT 自动通过**：skill 中的 🔴 CHECKPOINT 本需人工确认，CI 用 `--auto` 无人值守自动继续。
- **免费模型优先**：主模型 `opencode/hy3-free`（OpenCode 免费、无需密钥）；仅当它未产出报告且配置了 `AGNES_API_KEY` 时，才切换到 `0815/agnes-2.5-flash` 兜底。
- **自动进化（知识库回写）**：每次运行更新的 `memory/*.md`、`MEMORY.md`、报告 `reports/regulation-digest-*.md` 会 `git commit + push` 回 GitHub 私有仓库；下一次运行从已进化的知识库出发，实现持续自我进化。
- **运行超时**：`opencode run` 设置 60 分钟超时；超时则邮件附上失败提示。
- **GitHub 默认分支**：本流水线推回 `HEAD:master`（本仓库默认分支为 `master`）；若你的 GitHub 仓库默认分支不同，请相应修改 `.gitlab-ci.yml` 里的 `git push origin HEAD:master`。
