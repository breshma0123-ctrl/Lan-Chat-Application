"""
Database setup for LAN Chat Application.
Initializes SQLAlchemy instance and provides helper to create tables.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database and create all tables if they don't exist."""
    db.init_app(app)
    with app.app_context():
        # Import models so SQLAlchemy registers them before create_all
        import models
        db.create_all()
        print("[DATABASE] SQLite database and tables verified successfully.")
