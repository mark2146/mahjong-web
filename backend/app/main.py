# backend/app/__init__.py
import os
from flask import Flask, render_template, redirect
from backend.app.extensions import db, login_manager
from backend.app.models.user import User
from flask_login import current_user

# ===== 匯入 API blueprints =====
from backend.app.api.sessions import sessions_bp
from backend.app.api.auth_google import auth_google_bp
from backend.app.api.auth_me import auth_me_bp
from backend.app.api.health import health_bp
from backend.app.api.report import report_bp


def create_app():
    app = Flask(__name__)

    # ✅ 用同一個 SECRET_KEY（不要設兩次互蓋）
    app.config.update(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-change-me")),
        SESSION_COOKIE_SAMESITE="None",   # ✅ Railway/HTTPS 常需要
        SESSION_COOKIE_SECURE=True,       # ✅ SameSite=None 必須搭配 Secure
    )

    # ===== 資料庫設定 =====
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Railway 給的有時是 postgres://，SQLAlchemy 要 postgresql://
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        # 本機開發才用 sqlite
        database_url = "sqlite:///mahjong.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ===== 初始化 DB / LoginManager =====
    db.init_app(app)
    login_manager.init_app(app)

    # （可選）沒登入時的行為：回 401 / 或導頁
    # 你目前是前後端分離 + fetch，通常保持 401 比較好
    # login_manager.login_view = "auth_google.login"  # 如果你有這個 endpoint 才打開

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # ===== 註冊 API =====
    app.register_blueprint(sessions_bp)
    app.register_blueprint(auth_google_bp)
    app.register_blueprint(auth_me_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(report_bp)

    # ===== HTML routes（✅ 改成 Flask-Login 判斷，不用 session.get）=====
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect("/dashboard")
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        if not current_user.is_authenticated:
            return redirect("/")
        return render_template("dashboard.html")

    return app
