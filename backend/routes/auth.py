from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bson import ObjectId
import bcrypt

from database import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _user_to_dict(u: dict) -> dict:
    return {"id": str(u["_id"]), "username": u["username"], "role": u.get("role", "membro")}


def _require_admin():
    """Retorna (uid, erro). Se erro for não-None, retorne-o direto."""
    db = get_db()
    uid = get_jwt_identity()
    try:
        user = db.users.find_one({"_id": ObjectId(uid)})
    except Exception:
        return None, (jsonify({"error": "Token inválido"}), 401)
    if not user or user.get("role") != "admin":
        return None, (jsonify({"error": "Acesso negado"}), 403)
    return uid, None


def ensure_first_user():
    """Cria o usuário padrão se não existir nenhum."""
    db = get_db()
    if db.users.count_documents({}) == 0:
        db.users.insert_one({
            "username": "admin",
            "password": _hash("admin123"),
            "role": "admin",
        })


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Usuário e senha obrigatórios"}), 400

    db = get_db()
    user = db.users.find_one({"username": username})
    if not user or not _verify(password, user["password"]):
        return jsonify({"error": "Usuário ou senha incorretos"}), 401

    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token, "user": _user_to_dict(user)})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    db = get_db()
    uid = get_jwt_identity()
    try:
        user = db.users.find_one({"_id": ObjectId(uid)})
    except Exception:
        return jsonify({"error": "Token inválido"}), 401
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(_user_to_dict(user))


@auth_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    _, err = _require_admin()
    if err:
        return err
    db = get_db()
    users = list(db.users.find({}, {"password": 0}))
    return jsonify([_user_to_dict(u) for u in users])


@auth_bp.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    _, err = _require_admin()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "membro")
    if role not in ("admin", "membro"):
        return jsonify({"error": "Role inválido"}), 400

    if not username or not password:
        return jsonify({"error": "Usuário e senha obrigatórios"}), 400
    if len(password) < 6:
        return jsonify({"error": "Senha deve ter no mínimo 6 caracteres"}), 400

    db = get_db()
    if db.users.find_one({"username": username}):
        return jsonify({"error": "Usuário já existe"}), 409

    result = db.users.insert_one({
        "username": username,
        "password": _hash(password),
        "role": role,
    })
    user = db.users.find_one({"_id": result.inserted_id})
    return jsonify(_user_to_dict(user)), 201




@auth_bp.route("/users/<user_id>", methods=["PATCH"])
@jwt_required()
def update_user(user_id):
    uid, err = _require_admin()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    if role not in ("admin", "membro"):
        return jsonify({"error": "Role inválido"}), 400
    db = get_db()
    try:
        result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    except Exception:
        return jsonify({"error": "ID inválido"}), 400
    if result.matched_count == 0:
        return jsonify({"error": "Usuário não encontrado"}), 404
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return jsonify(_user_to_dict(user))

@auth_bp.route("/users/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    uid, err = _require_admin()
    if err:
        return err
    # não pode deletar a si mesmo
    if uid == user_id:
        return jsonify({"error": "Não é possível remover o próprio usuário"}), 400
    db = get_db()
    try:
        result = db.users.delete_one({"_id": ObjectId(user_id)})
    except Exception:
        return jsonify({"error": "ID inválido"}), 400
    if result.deleted_count == 0:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify({"ok": True})
