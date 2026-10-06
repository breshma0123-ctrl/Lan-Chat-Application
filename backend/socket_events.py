"""
Socket.IO Event Handlers for LAN Chat Application.
Manages real-time bidirectional WebSocket events: group chat, private chat,
typing notifications, user presence (online/offline), and room routing.
"""

from datetime import datetime
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from database import db
from models import User, Message, OnlineUser

# In-memory tracking: maps socket ID (sid) to username, and username to set of active sids
sid_to_username = {}
username_to_sids = {}

def register_socket_events(socketio):
    """Binds all WebSocket event listeners to the Flask-SocketIO instance."""

    @socketio.on('connect')
    def handle_connect():
        sid = request.sid
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '127.0.0.1'
        print(f"[SOCKET CONNECT] Client connected: SID={sid}, IP={client_ip}")

    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        username = sid_to_username.pop(sid, None)

        if username:
            if username in username_to_sids:
                username_to_sids[username].discard(sid)
                # If no more active sockets for this user, mark them offline
                if not username_to_sids[username]:
                    del username_to_sids[username]

                    # Update database status
                    online_rec = OnlineUser.query.filter_by(username=username).first()
                    if online_rec:
                        online_rec.status = 'offline'
                        online_rec.last_seen = datetime.utcnow()
                        db.session.commit()

                    print(f"[SOCKET DISCONNECT] User '{username}' is now OFFLINE.")
                    # Broadcast offline status to all clients
                    emit('user_offline', {
                        'username': username,
                        'status': 'offline',
                        'last_seen': datetime.utcnow().strftime('%I:%M %p')
                    }, broadcast=True)

    @socketio.on('join')
    def handle_join(data):
        """
        User joins the network.
        Data: { "username": "..." }
        """
        sid = request.sid
        username = data.get('username') or session.get('username')

        if not username:
            return

        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '127.0.0.1'

        # Track session
        sid_to_username[sid] = username
        if username not in username_to_sids:
            username_to_sids[username] = set()
        username_to_sids[username].add(sid)

        # Join rooms:
        # 1. Personal room named by their username (for direct private messages)
        # 2. 'general' room for LAN broadcast messages
        join_room(username)
        join_room('general')

        # Update database
        online_rec = OnlineUser.query.filter_by(username=username).first()
        if not online_rec:
            online_rec = OnlineUser(username=username, ip_address=client_ip, status='online', last_seen=datetime.utcnow())
            db.session.add(online_rec)
        else:
            online_rec.status = 'online'
            online_rec.ip_address = client_ip
            online_rec.last_seen = datetime.utcnow()
        db.session.commit()

        print(f"[SOCKET JOIN] User '{username}' joined general room and personal room. Total online: {len(username_to_sids)}")

        # Broadcast user online to everyone
        emit('user_online', {
            'username': username,
            'ip_address': client_ip,
            'status': 'online'
        }, broadcast=True)

        # Send current online users list back to the newly connected client
        active_users = list(username_to_sids.keys())
        emit('online_users_list', {'online_users': active_users})

    @socketio.on('leave')
    def handle_leave(data):
        """User leaves a room."""
        room = data.get('room', 'general')
        leave_room(room)
        print(f"[SOCKET LEAVE] SID {request.sid} left room {room}")

    @socketio.on('send_message')
    def handle_send_message(data):
        """
        Broadcast message to General LAN Chat.
        Data: { "message": "...", "sender": "..." }
        """
        sid = request.sid
        sender_username = sid_to_username.get(sid) or data.get('sender') or session.get('username')
        msg_text = (data.get('message') or '').strip()

        if not sender_username or not msg_text:
            return

        sender = User.query.filter_by(username=sender_username).first()
        if not sender:
            return

        # Persist message to SQLite
        new_msg = Message(
            sender_id=sender.id,
            receiver_id=None,  # None means General LAN room
            message=msg_text,
            message_type='public',
            timestamp=datetime.utcnow()
        )
        db.session.add(new_msg)
        db.session.commit()

        msg_payload = new_msg.to_dict()

        # Broadcast to all clients in 'general' room
        emit('receive_message', msg_payload, room='general')
        print(f"[GENERAL MESSAGE] [{sender_username}]: {msg_text[:30]}")

    @socketio.on('private_message')
    def handle_private_message(data):
        """
        Send a 1-on-1 private message.
        Data: { "receiver": "...", "message": "...", "sender": "..." }
        """
        sid = request.sid
        sender_username = sid_to_username.get(sid) or data.get('sender') or session.get('username')
        receiver_username = data.get('receiver')
        msg_text = (data.get('message') or '').strip()

        if not sender_username or not receiver_username or not msg_text:
            return

        sender = User.query.filter_by(username=sender_username).first()
        receiver = User.query.filter_by(username=receiver_username).first()

        if not sender or not receiver:
            emit('error_message', {'error': 'Recipient or sender not found.'})
            return

        # Persist private message to SQLite
        new_msg = Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            message=msg_text,
            message_type='private',
            timestamp=datetime.utcnow()
        )
        db.session.add(new_msg)
        db.session.commit()

        msg_payload = new_msg.to_dict()

        # Emit to recipient's personal room
        emit('private_message', msg_payload, room=receiver_username)

        # Also emit back to sender's personal room (so sender's other tabs or confirmation updates)
        emit('private_message', msg_payload, room=sender_username)

        print(f"[PRIVATE MESSAGE] [{sender_username} -> {receiver_username}]: {msg_text[:30]}")

    @socketio.on('typing')
    def handle_typing(data):
        """
        Relays typing indicator.
        Data: { "room": "general" or recipient_username, "username": "..." }
        """
        sid = request.sid
        username = sid_to_username.get(sid) or data.get('username') or session.get('username')
        target = data.get('room', 'general')

        if not username:
            return

        payload = {'username': username, 'room': target}

        if target == 'general':
            # Broadcast to general room, skipping the sender
            emit('typing', payload, room='general', include_self=False)
        else:
            # Emit directly to the private chat recipient
            emit('typing', payload, room=target)

    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """
        Relays stop typing indicator.
        Data: { "room": "general" or recipient_username, "username": "..." }
        """
        sid = request.sid
        username = sid_to_username.get(sid) or data.get('username') or session.get('username')
        target = data.get('room', 'general')

        if not username:
            return

        payload = {'username': username, 'room': target}

        if target == 'general':
            emit('stop_typing', payload, room='general', include_self=False)
        else:
            emit('stop_typing', payload, room=target)
