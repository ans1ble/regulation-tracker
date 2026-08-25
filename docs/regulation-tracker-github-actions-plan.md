
> ⚠️ 本文档为早期设计参考稿，已被实际实现取代。当前仓库使用 5 套 GitHub Actions 工作流（日报 / 周报 / 月报 / 季报 / 年报），详见 .github/workflows/ 与 index.md。此处保留仅供历史参考，请勿据此部署。
# regulation-tracker × GitHub Actions × OpenCode 自动化方案

> 状态：**设计参考稿**。本项目实际采用 `.github/workflows/regulation-digest.yml`（GitHub Actions 每周日运行，输出周报到 `reports/2026/weekly/`）。本文件记录最初的方案推演，软链接方案未落地（实际 workflow 直接读取仓库根目录 SKILL.md），发信走 Brevo（见 `scripts/send-digest.py`）。

> 目标：GitHub Actions 每周自动启动 OpenCode CLI 执行 regulation-tracker skill，实时抓取全球法规动态 → 生成报告 → Brevo 发信。

---

## 1. 架构总览

```
GitHub Actions (cron 每周日 00:00 / 手动触发)
    │
    ├─ 1. checkout 仓库
    ├─ 2. 安装 OpenCode CLI (npm i -g opencode-ai)
    ├─ 3. 注入密钥（GitHub Secrets → 环境变量）
    ├─ 4. opencode run --auto "读取 SKILL.md 并按流程执行全球法规扫描"
    │        ├─ agent 读 SKILL.md（软链接 → .trae 单份维护）
    │        ├─ websearch/webfetch 实时抓取 16 市场法规
    │        ├─ 按追踪流程筛选→定级→5步法→CHECKPOINT（自动确认）
    │        ├─ 更新知识库 memory/*.md
    │        └─ 输出报告 → reports/regulation-digest-YYYY-MM-DD.md
    ├─ 5. send-digest.py --report 报告文件 发信（Resend）
    └─ 6. （可选）git commit 知识库更新
```

## 2. 需要新增/修改的文件（3 个）

### 2.1 `.opencode/opencode.json`（新增）— provider 配置

复刻本机 `~/.config/opencode/opencode.json` 的 provider，**apiKey 改为 `{env:AGNES_API_KEY}` 引用**，不落盘：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "0815": {
      "models": {
        "agnes-2.5-flash": { "name": "" }
      },
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "apiKey": "{env:AGNES_API_KEY}",
        "baseURL": "https://apihub.agnes-ai.com/v1",
        "setCacheKey": true
      }
    }
  }
}
```

### 2.2 `.opencode/skills/regulation-tracker`（新增）— 软链接

OpenCode 的 skill 发现路径**不含 `.trae/`**（只搜 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/`）。用软链接指向单份维护的 skill：

```bash
mkdir -p .opencode/skills
ln -s ../../.trae/skills/regulation-tracker .opencode/skills/regulation-tracker
```

⚠️ **frontmatter name 需匹配目录名**（OpenCode 硬性要求）：当前 `name: aily-regulation-tracker` 与 `regulation-tracker` 不匹配，需改为 `name: regulation-tracker`（全小写连字符，符合 `^[a-z0-9]+(-[a-z0-9]+)*$`）。**注意：这会改动 `.trae/skills/regulation-tracker/SKILL.md` 的 frontmatter**，是唯一需要动源文件的点。

> Windows 注意：软链接在 Windows 上创建需管理员权限或开发者模式；CI 的 ubuntu runner 无此问题。若本机测试，可用 `cmd //c mklink //D`（管理员）或直接复制（放弃单份维护）。

### 2.3 `.github/workflows/regulation-digest.yml`（改造现有）— 加 OpenCode 执行步骤

在现有「Setup Python」之后、发信之前，插入 OpenCode 执行：

```yaml
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install OpenCode CLI
        run: npm install -g opencode-ai

      - name: Run regulation-tracker skill (OpenCode)
        env:
          AGNES_API_KEY: ${{ secrets.AGNES_API_KEY }}
        run: |
          mkdir -p reports
          opencode run --auto \
            "读取 .trae/skills/regulation-tracker/SKILL.md，按其中『追踪流程』执行全球扫描模式（16 市场批量抓取最新法规动态）。完成筛选/定级/5步法分析后，更新 memory/ 知识库，并按『报告模板』输出报告保存到 reports/regulation-digest-$(date +%F).md。网络不可达时按失败模式表标注待核实，不编造数据。"
```

完整 workflow 见文末附录（含 Secrets 配置说明）。

## 3. 你需要做的配置（GitHub 仓库 Settings）

| Secret / Variable | 值 | 用途 |
|---|---|---|
| `AGNES_API_KEY`（Secret） | 你本机 opencode 用的那个 key | OpenCode 模型调用（agnes hub，免费额度） |
| `RESEND_API_KEY`（Secret） | Resend API key | 邮件发送 |
| `DIGEST_TO`（Variable） | 收件邮箱（逗号分隔可多个） | send-digest.py 收件人 |

配好后 workflow 无需再改。

## 4. 风险与注意事项

1. **CHECKPOINT 在无人值守下自动通过**：skill 的 🔴 CHECKPOINT 是给人确认的；CI 里 `--auto` 自动批准工具权限，agent 会把 CHECKPOINT 当作流程节点直接继续。如需人审，改为两步 workflow（生成后停在报告，人工确认后手动触发发送 job）。
2. **成本**：agnes-2.5-flash 免费额度内运行；每周一次全球扫描约几十次搜索调用，注意免费额度限制。
3. **websearch 工具可用性**：OpenCode 原生支持 websearch/webfetch 工具（agent 权限含 `websearch`）。若 agnes hub 模型不支持工具调用，降级方案：prompt 要求 agent 用 `webfetch` 直接抓取官方源 URL（EUR-Lex/FCC/CNCA 等），仍走失败模式表兜底。
4. **知识库变更回写**：CI 里 agent 更新的 `memory/*.md` 在 runner 上是临时文件，job 结束即消失。如需保留，加一步 `git add + commit + push`（需要 `GITHUB_TOKEN` 写权限，见附录）。**默认不自动推送**，避免 CI 产生噪音提交。
5. **Windows 软链接**：本机建软链接需管理员/开发者模式；CI ubuntu 无此限制。
6. **`name` 字段改动影响**：改 frontmatter name 后，其他 runtime（Claude Code/Codex）按目录名引用不受影响（目录名未变）；但 OpenCode 的 skill 权限配置、以及依赖 `aily-regulation-tracker` 名字的任何现有引用需检查。

## 5. 验证方式

1. 本地验证：装 opencode → 建软链接 → `opencode run --auto "读取 SKILL.md 执行全球扫描，仅输出候选清单"` → 确认 agent 能加载 skill 并抓取
2. CI 验证：先 `workflow_dispatch` 手动触发一次 → 检查 Actions 日志 → 确认报告生成 + 邮件送达
3. 全流程验证：观察每周 cron 运行，核对知识库是否有增量更新

---

## 附录：完整 workflow 参考（含知识库回写可选步骤）

```yaml
name: regulation-digest-weekly

on:
  schedule:
    - cron: "0 0 * * 0"   # 每周日 00:00 UTC
  workflow_dispatch: {}

permissions:
  contents: write        # 仅当启用知识库回写时需要

jobs:
  run-skill-and-send:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install OpenCode CLI
        run: npm install -g opencode-ai

      - name: Run regulation-tracker skill (OpenCode)
        env:
          AGNES_API_KEY: ${{ secrets.AGNES_API_KEY }}
        run: |
          mkdir -p reports
          opencode run --auto \
            "读取 .trae/skills/regulation-tracker/SKILL.md，按『追踪流程』执行全球扫描模式（16 市场批量抓取）。筛选/定级/5步法分析后更新 memory/ 知识库，按『报告模板』输出报告到 reports/regulation-digest-$(date +%F).md。网络不可达时按失败模式表标注待核实，不编造。"
        timeout-minutes: 30

      - name: Send digest via Resend
        env:
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          DIGEST_TO: ${{ vars.DIGEST_TO }}
        run: |
          python .trae/skills/regulation-tracker/scripts/send-digest.py \
            --subject "法规动态摘要 $(date +%F)" \
            --report reports/regulation-digest-$(date +%F).md

      # --- 可选：知识库回写（默认注释，需确认后启用）---
      # - name: Commit knowledge base updates
      #   run: |
      #     git config user.name "regulation-bot"
      #     git config user.email "bot@users.noreply.github.com"
      #     git add .trae/skills/regulation-tracker/memory/
      #     git diff --cached --quiet || git commit -m "chore: 法规知识库自动更新 $(date +%F)"
      #     git push
```

---

*文档版本：2026-08-16 · 待用户确认后实施*

