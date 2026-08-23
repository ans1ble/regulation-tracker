# regulation-tracker（法规动态追踪 · 每日定时邮件）

本仓库包含「法规动态追踪」skill，并通过 **GitHub Actions 每日定时** 启动 OpenCode 运行该 skill（联网抓取全球 16 个市场最新认证法规），将生成的报告通过邮件发送到指定邮箱。

## 工作流程

```
GitHub Actions（cron 每天 01:00 UTC / 北京 09:00，或手动触发）
  ├─ checkout 仓库
  ├─ 安装 OpenCode CLI
  ├─ 写入 provider 配置（引用 AGNES_API_KEY）
  ├─ opencode run --pure --auto --model 0815/agnes-2.5-flash \
  │     读取 SKILL.md → 全球扫描模式 → 报告写入 reports/regulation-digest-YYYY-MM-DD.md
  ├─ 上传报告为 Artifact（即使邮件失败也可在 Actions 页面下载）
  ├─ 将进化后的 knowledge base（memory/、MEMORY.md、SKILL.md）与当日报告 git commit + push 回仓库（自动进化）
  └─ dawidd6/action-send-mail 通过 SMTP 发送报告到 DIGEST_TO
```

## 你需要配置的 Secrets / Variables

在仓库 **Settings → Secrets and variables → Actions** 中配置：

| 名称 | 类型 | 说明 |
|------|------|------|
| `AGNES_API_KEY` | Secret（可选） | **兜底模型**密钥（agnes hub，对应 provider `0815`）。主模型用 OpenCode 免费模型 `opencode/hy3-free`（无需密钥）；仅当免费模型未产出报告且该密钥已配置时，才切换到 `0815/agnes-2.5-flash` 兜底。 |
| `SMTP_SERVER` | Secret | 发件 SMTP 服务器，例如 `smtp.qq.com` |
| `SMTP_PORT` | Secret | SMTP 端口，QQ 为 `465`（SSL） |
| `SMTP_USERNAME` | Secret | 发件邮箱完整地址，例如 `xxxx@qq.com` |
| `SMTP_PASSWORD` | Secret | 发件邮箱的**授权码**（非登录密码；QQ 邮箱在「设置→账户→开启SMTP」获取） |
| `DIGEST_TO` | Variable | 收件邮箱，逗号分隔，例如 `494237963@qq.com,254840491@qq.com` |

> 邮件发送使用 `dawidd6/action-send-mail`（SMTP 方式）。GitHub Actions 本身**没有**内置邮件服务器，
> 必须提供一个发件邮箱的 SMTP 凭证。对 QQ 收件箱而言，用 QQ 邮箱 `smtp.qq.com` 发信送达率最高。
>
> 若你更想用 Resend：本仓库 `scripts/send-digest.py` 已支持 Resend（`RESEND_API_KEY` + `DIGEST_TO`），
> 可在 workflow 中替换最后的发信步骤调用该脚本（需自行调整）。

## 手动触发

仓库 **Actions → regulation-digest-daily → Run workflow**。

## 注意事项

- **CHECKPOINT 自动通过**：skill 中的 🔴 CHECKPOINT 本需人工确认，CI 用 `--auto` 无人值守自动继续。
- **成本**：每次运行会做大量模型调用（16 市场扫描），注意 agnes 免费额度。
- **自动进化（知识库回写）**：agent 运行中更新的 `memory/*.md`、`MEMORY.md`、报告 `reports/regulation-digest-*.md`
  会在每次运行后自动 `git commit + push` 回本仓库（需要 `contents: write` 权限，已开启）。
  因此下一次定时运行会从**已进化的知识库**出发，实现持续自我进化；你也可以在 GitHub 上直接看到知识库与历史报告的累积。
- **运行超时**：`opencode run` 设置了 60 分钟超时；超时则邮件会附上失败提示。
