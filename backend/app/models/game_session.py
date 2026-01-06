from backend.app.extensions import db
from datetime import date

class GameSession(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)

    # 關聯使用者
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 對局資訊
    date = db.Column(db.Date, nullable=False)
    players = db.Column(db.String(255), nullable=False)
    stake = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(255))
    rounds = db.Column(db.Integer, nullable=False)

    # ⭐⭐⭐ 關鍵欄位：本局輸贏
    profit = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
