#!/usr/bin/env python3
"""Send the regulation-tracker digest to one or more inboxes via Resend.

Two modes:
  1. Send an agent-generated report file:
       python send-digest.py --to a@example.com --report report.md
  2. Build a digest from the verified knowledge base (no report file needed):
       python send-digest.py --to a@example.com

Options:
  --to EMAIL       Recipient (repeatable). Falls back to DIGEST_TO env (comma-separated).
  --subject TEXT   Email subject (default: "法规动态摘要 <date>").
  --report PATH    Send this Markdown file instead of building from the KB.
  --kb PATH        Path to knowledge base (default: memory/regulation-knowledge-base.md).
  --from EMAIL     Sender address (default: digest@resend.dev — Resend test domain).
  --dry-run        Print the digest/subject instead of sending.

Requires env var RESEND_API_KEY. Uses only the Python standard library.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import date

# 强制 UTF-8 输出（Windows GBK 控制台无法打印 emoji/中文符号）
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except AttributeError:
    pass

RESEND_URL = "https://api.resend.com/emails"


def build_digest_from_kb(kb_path: str) -> str:
    """Parse the KB markdown table into a digest grouped by market."""
    if not os.path.exists(kb_path):
        raise SystemExit(f"知识库不存在: {kb_path}")

    rows = []
    with open(kb_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            # 跳过表头与分隔行（|---|）
            if len(cells) < 7 or cells[0] == "法规":
                continue
            if all(re.fullmatch(r"-{2,}", c or "-") for c in cells):
                continue
            rows.append(cells)

    if not rows:
        raise SystemExit("知识库无有效记录（表头或数据缺失）")

    # Group by market column (index 1)
    by_market: dict[str, list[list[str]]] = {}
    for r in rows:
        by_market.setdefault(r[1], []).append(r)

    digest = [
        "# 法规动态摘要（基于已核实知识库）",
        f"**生成日期**: {date.today().isoformat()}",
        "> ⚠️ 静态摘要（基于已核实知识库，未做增量网络搜索）；最新动态请运行 regulation-tracker skill 获取。",
        "",
    ]
    for market in sorted(by_market):
        digest.append(f"## {market}")
        for r in by_market[market]:
            # 法规 | 市场 | 状态 | 生效日期 | 要求 | 来源 | 更新日期
            digest.append(f"- **{r[0]}**（{r[2]}，{r[3]}）")
            digest.append(f"  - 要求: {r[4]}")
            digest.append(f"  - 来源: {r[5]}｜更新: {r[6]}")
        digest.append("")
    return "\n".join(digest)


def read_report(path: str) -> str:
    if not os.path.exists(path):
        raise SystemExit(f"报告文件不存在: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


def send(subject: str, body_md: str, to: list[str], sender: str) -> None:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise SystemExit("缺少环境变量 RESEND_API_KEY（Resend API key）")

    # Convert markdown to minimal HTML (escape + preserve line breaks / headings)
    html_parts = []
    for line in body_md.splitlines():
        if line.startswith("## "):
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_parts.append(f"<h1>{line[2:]}</h1>")
        elif line.strip().startswith("- "):
            html_parts.append(f"<li>{line.strip()[2:]}</li>")
        elif line.strip().startswith("  - "):
            html_parts.append(f"<li style='list-style:circle'>{line.strip()[4:]}</li>")
        elif line.strip():
            html_parts.append(f"<p>{line}</p>")
    html = "<html><body>" + "<br>".join(html_parts) + "</body></html>"

    payload = {
        "from": sender,
        "to": to,
        "subject": subject,
        "html": html,
        "text": body_md,
    }
    req = urllib.request.Request(
        RESEND_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Resend 发送失败 HTTP {e.code}: {detail}")


def main() -> None:
    parser = argparse.ArgumentParser(description="发送法规动态摘要邮件（Resend）")
    parser.add_argument("--to", action="append", default=[], help="收件邮箱（可多次指定）")
    parser.add_argument("--subject", default=f"法规动态摘要 {date.today().isoformat()}")
    parser.add_argument("--report", help="发送指定报告文件而非从知识库生成")
    parser.add_argument("--kb", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "memory", "regulation-knowledge-base.md"))
    parser.add_argument("--from", dest="sender", default="digest@resend.dev",
                        help="发件地址（默认 Resend 测试域 digest@resend.dev）")
    parser.add_argument("--dry-run", action="store_true", help="只打印摘要与收件人，不发送")
    args = parser.parse_args()

    to = list(args.to)
    env_to = os.environ.get("DIGEST_TO", "")
    if env_to:
        to.extend(e.strip() for e in env_to.split(",") if e.strip())
    to = list(dict.fromkeys(to))  # dedupe, keep order
    if not to:
        raise SystemExit("未指定收件人：用 --to 参数或 DIGEST_TO 环境变量")

    body = read_report(args.report) if args.report else build_digest_from_kb(args.kb)

    if args.dry_run:
        print(f"===== DRY RUN =====\n收件人: {to}\n主题: {args.subject}\n发件: {args.sender}\n---- 正文 ----\n{body}")
        return

    send(args.subject, body, to, args.sender)
    print(f"已发送到: {', '.join(to)}")


if __name__ == "__main__":
    main()
