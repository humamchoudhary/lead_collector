import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # It's recommended to set a strong, secret key in your environment variables for production
    SECRET_KEY = os.getenv("SECRET_KEY", "a_default_secret_key_for_development")
    SESSION_COOKIE_SAMESITE = 'Lax'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FB_VERIFY_TOKEN=os.getenv("FB_VERIFY_TOKEN")
    GRAPH_API_ACCESS_TOKEN=os.getenv("GRAPH_API_ACCESS_TOKEN")
    GRAPH_API_BASE_URI="https://graph.facebook.com/v24.0"
    FB_PAGE_ID="769888559550570"
