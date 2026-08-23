#!/usr/bin/env python3
"""Send the daily regulation digest report via email.

Delivery order (first configured wins):
  1. QQ SMTP  (smtp.qq.com:465, SSL)  - best deliverability to QQ inboxes
  2. Brevo API (HTTPS/443)            - works even if SMTP port is blocked
  3. Resend API (HTTPS/443)           - optional tertiary

Required env (at least one method must be configured):
  SMTP_USERNAME, SMTP_PASSWORD        -> QQ SMTP
  BREVO_API_KEY                        -> Brevo (sender must be verified in Brevo)
  RESEND_API_KEY                       -> Resend (sender must be verified in Resend)

Usage:
  send-digest.py <report.md> <subject> <to_csv> [sender_name]
"""
import os
import sys
import smtplib
import ssl
import json
import base64
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def build_message(subject, recipients, body_text, attachment_path, sender_name):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender_name
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    if attachment_path and os.path.isfile(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        fname = os.path.basename(attachment_path)
        part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", fname))
        msg.attach(part)
    return msg


def send_qq_smtp(subject, recipients, body_text, attachment_path, sender_name):
    user = os.environ.get("SMTP_USERNAME")
    pwd = os.environ.get("SMTP_PASSWORD")
    if not (user and pwd):
        return False
    try:
        msg = build_message(subject, recipients, body_text, attachment_path, user)
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.qq.com", 465, context=ctx, timeout=30) as s:
            s.login(user, pwd)
            s.sendmail(user, recipients, msg.as_string())
        print("[email] sent via QQ SMTP")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[email] QQ SMTP failed: {e}")
        return False


def send_brevo(subject, recipients, body_text, attachment_path, sender_name):
    key = os.environ.get("BREVO_API_KEY")
    if not key:
        return False
    sender_email = os.environ.get("BREVO_SENDER", os.environ.get("SMTP_USERNAME", "noreply@example.com"))
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": r} for r in recipients],
        "subject": subject,
        "textContent": body_text,
    }
    if attachment_path and os.path.isfile(attachment_path):
        with open(attachment_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        payload["attachment"] = [{"content": b64, "name": os.path.basename(attachment_path)}]
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={"api-key": key, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"[email] sent via Brevo (HTTP {resp.status})")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[email] Brevo failed: {e}")
        return False


def send_resend(subject, recipients, body_text, attachment_path, sender_name):
    key = os.environ.get("RESEND_API_KEY")
    if not key:
        return False
    sender_email = os.environ.get("RESEND_SENDER", os.environ.get("SMTP_USERNAME", "noreply@example.com"))
    payload = {
        "from": f"{sender_name} <{sender_email}>",
        "to": recipients,
        "subject": subject,
        "text": body_text,
    }
    if attachment_path and os.path.isfile(attachment_path):
        with open(attachment_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        payload["attachments"] = [{"content": b64, "filename": os.path.basename(attachment_path)}]
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"[email] sent via Resend (HTTP {resp.status})")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[email] Resend failed: {e}")
        return False


def main():
    if len(sys.argv) < 4:
        print("Usage: send-digest.py <report.md> <subject> <to_csv> [sender_name]")
        sys.exit(2)
    report_path = sys.argv[1]
    subject = sys.argv[2]
    recipients = [r.strip() for r in sys.argv[3].split(",") if r.strip()]
    sender_name = sys.argv[4] if len(sys.argv) > 4 else "法规动态追踪"

    if not recipients:
        print("[email] no recipients provided")
        sys.exit(1)
    if not os.path.isfile(report_path):
        print(f"[email] report not found: {report_path}")
        sys.exit(1)

    with open(report_path, encoding="utf-8") as f:
        body = f.read()

    for fn in (send_qq_smtp, send_brevo, send_resend):
        if fn(subject, recipients, body, report_path, sender_name):
            return
    print("[email] all methods failed or unconfigured")
    sys.exit(1)


if __name__ == "__main__":
    main()
