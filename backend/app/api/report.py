import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

report_bp = Blueprint("report", __name__)

@report_bp.route("/api/report", methods=["POST"])
def report_problem():
    try:
        data = request.json or {}
        content = data.get("content", "").strip()

        if not content:
            return jsonify({"error": "內容不能為空"}), 400

        mail_user = os.getenv("MAIL_USER")
        mail_password = os.getenv("MAIL_PASSWORD")

        print("MAIL_USER =", mail_user)
        print("MAIL_PASSWORD =", "有值" if mail_password else "❌ 沒有值")

        if not mail_user or not mail_password:
            raise RuntimeError("MAIL_USER 或 MAIL_PASSWORD 未設定")

        user_email = getattr(current_user, "email", "unknown")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = EmailMessage()
        msg["Subject"] = "【麻將日記】使用者問題回報"
        msg["From"] = mail_user
        msg["To"] = mail_user
        msg["Reply-To"] = user_email

        msg.set_content(f"""
回報時間：
{now}

使用者 Email：
{user_email}

問題描述：
{content}
""")

        print("📨 準備連線 Gmail SMTP…")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(mail_user, mail_password)
            smtp.send_message(msg)

        print("✅ 寄信成功")
        return jsonify({"ok": True})

    except Exception as e:
        print("❌ 寄信失敗：", repr(e))
        return jsonify({"error": "send mail failed"}), 500
