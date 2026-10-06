"""
Main Application Entry Point for LAN Chat Application.
Configures Flask, SQLite database, Flask-SocketIO, and starts the server
listening on 0.0.0.0:5000 so any computer on the local network can connect.
"""

import os
import socket
from flask import Flask
from flask_socketio import SocketIO
from database import db, init_db
from routes import routes_bp
from socket_events import register_socket_events

def get_lan_ip():
    """
    Discovers the actual Local Area Network (LAN) IP of this computer.
    Uses UDP socket to identify the outbound interface without sending data.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 8.8.8.8 does not need to be reachable; kernel picks the outgoing interface
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def create_app():
    """Application factory for Flask and SocketIO."""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'lan-chat-secret-key-2026-secure-cn-project'
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Database
    init_db(app)

    # Initialize SocketIO with threading mode (compatible with Python 3.14 & Windows)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    # Register Blueprints & WebSocket Events
    app.register_blueprint(routes_bp)
    register_socket_events(socketio)

    return app, socketio

app, socketio = create_app()

if __name__ == '__main__':
    lan_ip = get_lan_ip()
    port = 5000

    print("\n" + "=" * 68)
    print("      LAN CHAT APPLICATION - COMPUTER NETWORKS PROJECT")
    print("=" * 68)
    print(f"  * Local Access (This PC) : http://127.0.0.1:{port}")
    print(f"  * LAN Access (Other PCs) : http://{lan_ip}:{port}")
    print(f"  * Bound Interface        : 0.0.0.0 (All Network Interfaces)")
    print(f"  * Port                   : {port}")
    print("=" * 68)
    print("  Instructions for Other Computers on Same Wi-Fi/LAN:")
    print(f"  Open web browser and visit: http://{lan_ip}:{port}")
    print("=" * 68 + "\n")

    # Run SocketIO server on all interfaces
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
