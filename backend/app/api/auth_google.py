import os
import hmac
import secrets
from urllib.parse import urlencode
import requests
from flask import Blueprint, request, jsonify, redirect, url_for, session

from backend.app.models.user import User
from backend.app.extensions import db

# ✅ 1️⃣ 先宣告 Blueprint（一定要在最上面）
auth_google_bp = Blueprint("auth_google", __name__, url_prefix="/auth/google")

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@auth_google_bp.post("/logout")
def logout():
    session.clear()
    return jsonify(success=True)

# ✅ 2️⃣ login route
@auth_google_bp.get("/login")
def google_login():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    url = GOOGLE_AUTH_URL + "?" + urlencode(params)

    # 🔥 關鍵就在這一行
    return redirect(url)

# ✅ 3️⃣ callback route（這裡才開始用 auth_google_bp）
@auth_google_bp.get("/callback")
def google_callback():
    expected_state = session.pop("oauth_state", "")
    supplied_state = request.args.get("state", "")
    if not expected_state or not hmac.compare_digest(expected_state, supplied_state):
        return jsonify(error="Invalid OAuth state"), 400

    code = request.args.get("code")
    if not code:
        return jsonify(error="Missing code"), 400

    # 交換 token
    token_resp = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if not token_resp.ok:
        return jsonify(error="OAuth token exchange failed"), 400
    token_data = token_resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return jsonify(error="Failed to obtain access token"), 400

    # 取得 Google 使用者資訊
    userinfo_resp = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    userinfo = userinfo_resp.json()

    google_id = str(userinfo.get("id"))
    email = userinfo.get("email")

    if not google_id or not email:
        return jsonify(error="Invalid Google user data"), 400

    # 查或建立使用者
    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        user = User(
            google_id=google_id,
            email=email,
            name=userinfo.get("name"),
            avatar=userinfo.get("picture"),
        )
        db.session.add(user)
    else:
        user.name = userinfo.get("name")
        user.avatar = userinfo.get("picture")

    db.session.commit()
    session["user_id"] = user.id  

    return redirect("/dashboard")
