# backend/app/__init__.py
import os
from flask import Flask, render_template, session, redirect
from backend.app.extensions import db

# ===== 匯入 API blueprints =====
from backend.app.api.sessions import sessions_bp
from backend.app.api.auth_google import auth_google_bp
from backend.app.api.auth_me import auth_me_bp
from backend.app.api.health import health_bp
from backend.app.api.report import report_bp

from backend.app.extensions import db, login_manager
from backend.app.models.user import User

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SESSION_COOKIE_SAMESITE="None",   # ⭐⭐⭐ 關鍵
        SESSION_COOKIE_SECURE=True,       # ⭐⭐⭐ 關鍵
    )
    # ===== 基本設定 =====
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    # ===== 資料庫設定（關鍵）=====
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Railway 給的有時是 postgres://，SQLAlchemy 要 postgresql://
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        # 本機開發才用 sqlite
        database_url = "sqlite:///mahjong.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ===== 初始化 DB =====
    db.init_app(app)
    
    login_manager.init_app(app)

    # user loader（一定要有）
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ===== 註冊 API =====
    app.register_blueprint(sessions_bp)
    app.register_blueprint(auth_google_bp)
    app.register_blueprint(auth_me_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(report_bp)

    # ===== HTML routes =====
    @app.route("/")
    def index():
        if session.get("user_id"):
            return redirect("/dashboard")
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        if not session.get("user_id"):
            return redirect("/")
        return render_template("dashboard.html")

    return app
