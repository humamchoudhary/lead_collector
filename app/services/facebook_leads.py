import requests
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Lead, Post, Comment, Reaction
from app.config import Config

"""
Background scheduler service for extracting Facebook data
No Flask app context needed - uses SQLAlchemy directly
"""

# Create engine and session factory
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = scoped_session(sessionmaker(bind=engine))


def get_facebook_data(uri):
    """Make GET request to Facebook Graph API"""
    req = requests.get(uri)
    if req.status_code == 200:
        return req.json().get("data", [])
    else:
        raise Exception(f"Facebook API Error: {req.status_code}")


def get_or_create_lead(session, user_id, username):
    """Get existing lead or create new one"""
    lead = session.query(Lead).filter_by(platform_user_id=user_id).first()
    if not lead:
        lead = Lead(
            platform_user_id=user_id,
            username=username,
            platform='facebook'
        )
        session.add(lead)
        session.flush()
    return lead


def get_or_create_post(session, post_id, message, created_time, post_url):
    """Get existing post or create new one"""
    post = session.query(Post).filter_by(platform_post_id=post_id).first()
    if not post:
        if isinstance(created_time, str):
            created_time = datetime.fromisoformat(created_time.replace('+0000', '+00:00'))
        
        post = Post(
            platform_post_id=post_id,
            message=message,
            created_time=created_time,
            post_url=post_url
        )
        session.add(post)
        session.flush()
    return post


def add_comment_if_new(session, post, lead, comment_id, message, created_time):
    """Add comment if it doesn't exist"""
    existing = session.query(Comment).filter_by(platform_comment_id=comment_id).first()
    if existing:
        return False
    
    if isinstance(created_time, str):
        created_time = datetime.fromisoformat(created_time.replace('+0000', '+00:00'))
    
    comment = Comment(
        platform_comment_id=comment_id,
        message=message,
        created_time=created_time,
        post_id=post.id,
        lead_id=lead.id
    )
    session.add(comment)
    
    # Update counters
    post.total_comments += 1
    lead.total_comments += 1
    lead.total_interactions += 1
    return True


def add_reaction_if_new(session, post, lead, reaction_type):
    """Add reaction if it doesn't exist"""
    existing = session.query(Reaction).filter_by(post_id=post.id, lead_id=lead.id).first()
    if existing:
        return False
    
    reaction = Reaction(
        reaction_type=reaction_type,
        post_id=post.id,
        lead_id=lead.id
    )
    session.add(reaction)
    
    # Update counters
    post.total_reactions += 1
    lead.total_reactions += 1
    lead.total_interactions += 1
    return True


def extract_facebook_leads():
    """Main extraction function - call this from your scheduler"""
    session = SessionLocal()
    
    print(f"\n{'='*60}")
    print(f"Starting Facebook extraction at {datetime.now()}")
    print(f"{'='*60}\n")
    
    stats = {
        'posts': 0,
        'new_comments': 0,
        'new_reactions': 0,
        'total_leads': 0
    }
    
    try:
        base_uri = Config.GRAPH_API_BASE_URI
        token = Config.GRAPH_API_ACCESS_TOKEN
        page_id = Config.FB_PAGE_ID
        
        # Get all posts
        posts_uri = f"{base_uri}/{page_id}/posts?fields=id,message,created_time,permalink_url&access_token={token}"
        posts = get_facebook_data(posts_uri)
        
        print(f"Found {len(posts)} posts\n")
        
        for post_data in posts:
            # Create/get post
            post = get_or_create_post(
                session=session,
                post_id=post_data['id'],
                message=post_data.get('message'),
                created_time=post_data.get('created_time'),
                post_url=post_data.get('permalink_url')
            )
            stats['posts'] += 1
            
            # Get comments
            comments_uri = f"{base_uri}/{post_data['id']}/comments?fields=id,message,created_time,from&access_token={token}"
            comments = get_facebook_data(comments_uri)
            
            for comment_data in comments:
                lead = get_or_create_lead(
                    session=session,
                    user_id=comment_data['from']['id'],
                    username=comment_data['from']['name']
                )
                
                if add_comment_if_new(
                    session=session,
                    post=post,
                    lead=lead,
                    comment_id=comment_data['id'],
                    message=comment_data.get('message', ''),
                    created_time=comment_data.get('created_time')
                ):
                    stats['new_comments'] += 1
            
            # Get reactions
            reactions_uri = f"{base_uri}/{post_data['id']}/reactions?fields=id,name,type&access_token={token}"
            reactions = get_facebook_data(reactions_uri)
            
            for reaction_data in reactions:
                lead = get_or_create_lead(
                    session=session,
                    user_id=reaction_data['id'],
                    username=reaction_data['name']
                )
                
                if add_reaction_if_new(
                    session=session,
                    post=post,
                    lead=lead,
                    reaction_type=reaction_data['type']
                ):
                    stats['new_reactions'] += 1
        
        # Commit everything
        session.commit()
        
        stats['total_leads'] = session.query(Lead).count()
        
        print(f"\n{'='*60}")
        print(f"Extraction completed!")
        print(f"Posts: {stats['posts']}")
        print(f"New comments: {stats['new_comments']}")
        print(f"New reactions: {stats['new_reactions']}")
        print(f"Total leads: {stats['total_leads']}")
        print(f"{'='*60}\n")
        
        return stats
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {str(e)}\n")
        raise
    finally:
        session.close()


# For manual testing
if __name__ == "__main__":
    extract_facebook_leads()
