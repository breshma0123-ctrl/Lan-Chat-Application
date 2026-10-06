"""
Database Models for LAN Chat Application.
Defines User, Message, and OnlineUser models using SQLAlchemy.
"""

from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to messages
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender_user', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver_user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # None = General Chat
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.String(20), default='public')  # 'public' or 'private'

    def to_dict(self):
        sender = User.query.get(self.sender_id)
        receiver = User.query.get(self.receiver_id) if self.receiver_id else None

        # Format readable time e.g., "10:35 AM"
        formatted_time = self.timestamp.strftime('%I:%M %p') if self.timestamp else ''
        formatted_date = self.timestamp.strftime('%Y-%m-%d') if self.timestamp else ''

        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender': sender.username if sender else 'Unknown',
            'receiver_id': self.receiver_id,
            'receiver': receiver.username if receiver else 'general',
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else '',
            'time': formatted_time,
            'date': formatted_date,
            'message_type': self.message_type
        }

    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.receiver_id}: {self.message[:20]}>'


class OnlineUser(db.Model):
    __tablename__ = 'online_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='offline')  # 'online' or 'offline'
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'ip_address': self.ip_address,
            'status': self.status,
            'last_seen': self.last_seen.strftime('%I:%M %p, %b %d') if self.last_seen else ''
        }

    def __repr__(self):
        return f'<OnlineUser {self.username} ({self.status})>'
