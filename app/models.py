from datetime import datetime, timezone
from .extentions import db, bcrypt




# ==============================================================================
# User Model
# ==============================================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"

# ==============================================================================
# Lead Model
# ==============================================================================

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(255))
    user_profile_url = db.Column(db.Text)

    # Intent & Content
    intent_category = db.Column(db.String(100))
    intent_score = db.Column(db.Float)
    conversation_snippet = db.Column(db.Text)
    post_url = db.Column(db.Text)
    keywords_matched = db.Column(db.JSON)

    # Status
    status = db.Column(db.String(20), default="new")
    routed = db.Column(db.Boolean, default=False)

    # Timestamp
    discovered_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    def __repr__(self) -> str:
        return f"<Lead {self.username} from:{self.platform}  >"

