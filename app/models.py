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
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    platform_user_id = db.Column(db.String(255), unique=True, nullable=False, index=True)  # Facebook user ID
    platform = db.Column(db.String(50), nullable=False, default='facebook')
    username = db.Column(db.String(255))
    user_profile_url = db.Column(db.Text)
    
    # Intent & Content
    intent_category = db.Column(db.String(100))
    intent_score = db.Column(db.Float)
    keywords_matched = db.Column(db.JSON)
    
    # Aggregated metrics
    total_interactions = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_reactions = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), default="new")
    routed = db.Column(db.Boolean, default=False)
    
    # Timestamp
    discovered_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    comments = db.relationship('Comment', back_populates='lead', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', back_populates='lead', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_interactions=True):
        """Convert lead to dictionary with optional interactions"""
        data = {
            'id': self.id,
            'platform_user_id': self.platform_user_id,
            'platform': self.platform,
            'username': self.username,
            'user_profile_url': self.user_profile_url,
            'intent_category': self.intent_category,
            'intent_score': self.intent_score,
            'keywords_matched': self.keywords_matched,
            'total_interactions': self.total_interactions,
            'total_comments': self.total_comments,
            'total_reactions': self.total_reactions,
            'status': self.status,
            'routed': self.routed,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_interactions:
            data['comments'] = [comment.to_dict() for comment in self.comments.all()]
            data['reactions'] = [reaction.to_dict() for reaction in self.reactions.all()]
        
        return data
    
    def __repr__(self):
        return f"<Lead {self.username} from:{self.platform} (ID: {self.platform_user_id})>"

# ==============================================================================
# Posts Model
# ==============================================================================

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    platform_post_id = db.Column(db.String(255), unique=True, nullable=False, index=True)  # Facebook post ID
    post_url = db.Column(db.Text)
    message = db.Column(db.Text)
    created_time = db.Column(db.DateTime)
    
    # Post metrics
    total_comments = db.Column(db.Integer, default=0)
    total_reactions = db.Column(db.Integer, default=0)
    
    # Metadata
    discovered_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    comments = db.relationship('Comment', back_populates='post', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', back_populates='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_interactions=True):
        """Convert post to dictionary with optional interactions"""
        data = {
            'id': self.id,
            'platform_post_id': self.platform_post_id,
            'post_url': self.post_url,
            'message': self.message,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'total_comments': self.total_comments,
            'total_reactions': self.total_reactions,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
        }
        
        if include_interactions:
            data['comments'] = [comment.to_dict() for comment in self.comments.all()]
            data['reactions'] = [reaction.to_dict() for reaction in self.reactions.all()]
        
        return data
    
    def __repr__(self):
        return f"<Post {self.platform_post_id}>"

# ==============================================================================
# Posts Model
# ==============================================================================

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    platform_comment_id = db.Column(db.String(255), unique=True, nullable=False, index=True)  # Facebook comment ID
    message = db.Column(db.Text)
    created_time = db.Column(db.DateTime)
    
    # Foreign Keys
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False, index=True)
    
    # Intent analysis
    intent_score = db.Column(db.Float)
    keywords_matched = db.Column(db.JSON)
    
    # Timestamp
    discovered_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    post = db.relationship('Post', back_populates='comments')
    lead = db.relationship('Lead', back_populates='comments')
    
    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'platform_comment_id': self.platform_comment_id,
            'message': self.message,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'post_id': self.post_id,
            'lead_id': self.lead_id,
            'intent_score': self.intent_score,
            'keywords_matched': self.keywords_matched,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
        }
    
    def __repr__(self):
        return f"<Comment {self.platform_comment_id} by Lead:{self.lead_id}>"

# ==============================================================================
# Posts Model
# ==============================================================================

class Reaction(db.Model):
    __tablename__ = 'reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(50), nullable=False)  # LIKE, LOVE, WOW, HAHA, SAD, ANGRY
    
    # Foreign Keys
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False, index=True)
    
    # Timestamp
    discovered_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    post = db.relationship('Post', back_populates='reactions')
    lead = db.relationship('Lead', back_populates='reactions')
    
    # Unique constraint: one user can only have one reaction per post
    __table_args__ = (
        db.UniqueConstraint('post_id', 'lead_id', name='unique_reaction_per_user_per_post'),
    )
    
    def to_dict(self):
        """Convert reaction to dictionary"""
        return {
            'id': self.id,
            'reaction_type': self.reaction_type,
            'post_id': self.post_id,
            'lead_id': self.lead_id,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
        }
    
    def __repr__(self):
        return f"<Reaction {self.reaction_type} by Lead:{self.lead_id} on Post:{self.post_id}>"

