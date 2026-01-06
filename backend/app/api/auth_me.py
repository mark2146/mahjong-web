from flask import Blueprint, session, jsonify
from app.models.user import User

auth_me_bp = Blueprint("auth_me", __name__, url_prefix="/auth")

@auth_me_bp.get("/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error="Not logged in"), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify(error="User not found"), 404

    return jsonify(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar=user.avatar,
    )
