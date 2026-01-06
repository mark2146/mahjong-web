# app/api/sessions.py
from flask import Blueprint, request, session, jsonify
from app.models.game_session import GameSession
from app.extensions import db
from datetime import datetime
from sqlalchemy import func, case

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

@sessions_bp.post("")
def create_session():
    # 1️⃣ 一定要先驗證登入
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error="Unauthorized"), 401

    # 2️⃣ 保證 data 一定是 dict
    data = request.get_json() or {}

    # 3️⃣ 必填欄位檢查（防止空資料塞 DB）
    required_fields = ["date", "players", "stake", "rounds", "profit"]
    for field in required_fields:
        if field not in data or data[field] in ("", None):
            return jsonify(error=f"Missing field: {field}"), 400

    # 4️⃣ 型別與格式驗證
    try:
        game_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        rounds = int(data["rounds"])
        profit = int(data["profit"])
    except Exception:
        return jsonify(error="Invalid data format"), 400

    if rounds <= 0:
        return jsonify(error="Rounds must be greater than 0"), 400

    # 5️⃣ 建立 Session
    game = GameSession(
        user_id=user_id,
        date=datetime.strptime(data["date"], "%Y-%m-%d").date(),  # ✅ 用 date
        players=data["players"],
        stake=data["stake"],
        location=data.get("location"),
        rounds=data["rounds"],
        profit=data["profit"],
    )

    db.session.add(game)
    db.session.commit()

    return jsonify(success=True, id=game.id), 201
@sessions_bp.get("")
def list_sessions():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])

    date = request.args.get("date")

    query = GameSession.query.filter_by(user_id=user_id)

    if date:
        query = query.filter(GameSession.date == date)

    games = query.order_by(GameSession.date).all()

    return jsonify([
        {
            "id": g.id,
            "date": g.date.isoformat(),
            "players": g.players,
            "stake": g.stake,
            "location": g.location,
            "rounds": g.rounds,
            "profit": g.profit,
        }
        for g in games
    ])
    
@sessions_bp.delete("/<int:id>")
def delete_session(id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error="Unauthorized"), 401

    game = GameSession.query.filter_by(id=id, user_id=user_id).first()
    if not game:
        return jsonify(error="Not found"), 404

    db.session.delete(game)
    db.session.commit()

    return jsonify(success=True)

@sessions_bp.get("/<int:id>")
def get_session(id):
    user_id = session.get("user_id")
    game = GameSession.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify({
        "id": game.id,
        "date": game.date.isoformat(),
        "players": game.players,
        "stake": game.stake,
        "location": game.location,
        "rounds": game.rounds,
        "profit": game.profit,
    })



@sessions_bp.put("/<int:id>")
def update_session(id):
    user_id = session.get("user_id")
    game = GameSession.query.filter_by(id=id, user_id=user_id).first_or_404()

    data = request.json
    game.date = data["date"]
    game.players = data["players"]
    game.stake = data["stake"]
    game.location = data.get("location")
    game.rounds = data["rounds"]
    game.profit = data["profit"]

    db.session.commit()
    return jsonify(success=True)

# =====================
# Dashboard / Summary
# =====================

@sessions_bp.get("/summary")
def sessions_summary():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error="Unauthorized"), 401

    year = request.args.get("year", type=int)
    if not year:
        return jsonify(error="year required"), 400

    start = f"{year}-01-01"
    end = f"{year}-12-31"

    q = (
        db.session.query(
            func.sum(GameSession.profit).label("total_profit"),
            func.sum(
                case((GameSession.profit > 0, GameSession.profit), else_=0)
            ).label("win_profit"),
            func.sum(
                case((GameSession.profit < 0, GameSession.profit), else_=0)
            ).label("lose_profit"),
            func.sum(GameSession.rounds).label("total_rounds"),
        )
        .filter(GameSession.user_id == user_id)
        .filter(GameSession.date >= start)
        .filter(GameSession.date <= end)
    )

    r = q.first()

    return jsonify({
        "total_profit": r.total_profit or 0,
        "win_profit": r.win_profit or 0,
        "lose_profit": r.lose_profit or 0,
        "total_rounds": r.total_rounds or 0,
    })