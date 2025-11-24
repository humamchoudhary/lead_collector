#!/usr/bin/env python
"""
Simple script to create a new user
Usage: python -m app.services.create_user
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.config import Config

# Create engine and session
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

def create_user(email, password):
    """Create a new user"""
    session = Session()
    
    try:
        # Check if user already exists
        existing = session.query(User).filter_by(email=email).first()
        if existing:
            print(f"❌ User '{email}' already exists!")
            return
        
        # Create user
        user = User(email=email)
        user.set_password(password)
        
        session.add(user)
        session.commit()
        
        print(f"✓ User created: {user.email}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    email = input("Email: ")
    password = input("Password: ")
    
    create_user(email, password)
