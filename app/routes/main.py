from flask import Blueprint, request, jsonify
from ..models import User, Lead
from ..extentions import db

main_bp = Blueprint("main", __name__)


# -------------------------
# User Authentication
# -------------------------

@main_bp.post("/register")
def register():
    data =  request.json or {}
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201


@main_bp.post("/login")
def login():
    data =  request.json or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


# -------------------------
# Lead endpoints
# -------------------------

@main_bp.post("/leads")
def create_lead():
    data =  request.json or {}
    lead = Lead(**data)
    db.session.add(lead)
    db.session.commit()
    return jsonify({"message": "Lead created", "id": lead.id}), 201


@main_bp.get("/leads")
def get_leads():
    leads = Lead.query.all()
    return jsonify([
        {
            "id": l.id,
            "platform": l.platform,
            "username": l.username,
            "status": l.status,
            "discovered_at": l.discovered_at.isoformat(),
        } for l in leads
    ])

