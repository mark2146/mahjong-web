import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

report_bp = Blueprint("report", __name__)

@report_bp.route("/api/report", methods=["POST"])
@login_required
def report_problem():
    data = request.json or {}
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"error": "內容不能為空"}), 400

    user_email = current_user.email
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL"),
        to_emails=os.getenv("SENDGRID_FROM_EMAIL"),  # 寄給你自己
        subject="【麻將日記】使用者問題回報",
        plain_text_content=f"""
回報時間：
{now}

使用者 Email：
{user_email}

問題描述：
{content}
"""
    )
    # 讓你可以直接回信給使用者
    message.reply_to = user_email

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
        return jsonify({"ok": True})
    except Exception as e:
        print("❌ SendGrid error:", e)
        return jsonify({"error": "寄信失敗"}), 500
