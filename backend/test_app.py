"""
Automated Verification Test Suite for LAN Chat Application.
Tests database creation, user registration, authentication, message exchange,
and server status.
"""

import os
import sys
import json

# Ensure backend directory is in python module search path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from database import db
from models import User, Message, OnlineUser

def run_tests():
    print("\n" + "=" * 60)
    print("      RUNNING LAN CHAT APPLICATION VERIFICATION TESTS")
    print("=" * 60)

    client = app.test_client()

    with app.app_context():
        # Clean test tables
        db.drop_all()
        db.create_all()
        print("[PASS] Database tables created successfully.")

    # 1. Test Server Status Endpoint
    res = client.get('/api/status')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    status_data = res.get_json()
    assert status_data['success'] is True
    print(f"[PASS] /api/status endpoint OK. Detected LAN IP: {status_data['lan_ip']}:{status_data['port']}")

    # 2. Test User Registration - Suba
    res = client.post('/api/register',
                      data=json.dumps({
                          'username': 'Suba',
                          'password': 'password123',
                          'confirm_password': 'password123'
                      }),
                      content_type='application/json')
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.data}"
    reg_data = res.get_json()
    assert reg_data['success'] is True
    print("[PASS] User 'Suba' registered successfully.")

    # 3. Test Duplicate Registration Prevention
    res = client.post('/api/register',
                      data=json.dumps({
                          'username': 'Suba',
                          'password': 'password123',
                          'confirm_password': 'password123'
                      }),
                      content_type='application/json')
    assert res.status_code == 409, f"Expected 409, got {res.status_code}"
    print("[PASS] Duplicate registration correctly rejected with 409 Conflict.")

    # 4. Test Registration - Priya
    res = client.post('/api/register',
                      data=json.dumps({
                          'username': 'Priya',
                          'password': 'secret456',
                          'confirm_password': 'secret456'
                      }),
                      content_type='application/json')
    assert res.status_code == 201
    print("[PASS] User 'Priya' registered successfully.")

    # 5. Test Invalid Login
    res = client.post('/api/login',
                      data=json.dumps({'username': 'Suba', 'password': 'wrongpassword'}),
                      content_type='application/json')
    assert res.status_code == 401
    print("[PASS] Invalid password correctly rejected with 401 Unauthorized.")

    # 6. Test Valid Login - Suba
    res = client.post('/api/login',
                      data=json.dumps({'username': 'Suba', 'password': 'password123'}),
                      content_type='application/json')
    assert res.status_code == 200
    login_data = res.get_json()
    assert login_data['success'] is True
    print(f"[PASS] Login successful for user: {login_data['user']['username']}.")

    # 7. Test Get Users List
    res = client.get('/api/users')
    assert res.status_code == 200
    users_data = res.get_json()
    assert len(users_data['users']) == 2
    print(f"[PASS] /api/users returned {len(users_data['users'])} registered users.")

    # 8. Test Send General Broadcast Message
    res = client.post('/api/messages',
                      data=json.dumps({
                          'message': 'Hello everyone on LAN!',
                          'receiver': None
                      }),
                      content_type='application/json')
    assert res.status_code == 201
    print("[PASS] Broadcast message saved to database.")

    # 9. Test Fetch General Messages
    res = client.get('/api/messages')
    assert res.status_code == 200
    msg_data = res.get_json()
    assert len(msg_data['messages']) == 1
    assert msg_data['messages'][0]['sender'] == 'Suba'
    print(f"[PASS] /api/messages verified: [{msg_data['messages'][0]['sender']}]: {msg_data['messages'][0]['message']}")

    # 10. Test Send Private Message: Suba -> Priya
    res = client.post('/api/messages',
                      data=json.dumps({
                          'message': 'Hi Priya, this is a private test!',
                          'receiver': 'Priya'
                      }),
                      content_type='application/json')
    assert res.status_code == 201
    print("[PASS] Private message Suba -> Priya stored successfully.")

    # 11. Test Fetch Private Message History
    res = client.get('/api/messages/Priya')
    assert res.status_code == 200
    priv_data = res.get_json()
    assert len(priv_data['messages']) == 1
    assert priv_data['messages'][0]['message_type'] == 'private'
    print(f"[PASS] /api/messages/Priya returned {len(priv_data['messages'])} private message(s).")

    # 12. Test User Profile Endpoint
    res = client.get('/api/profile')
    assert res.status_code == 200
    profile_data = res.get_json()
    assert profile_data['profile']['username'] == 'Suba'
    assert profile_data['profile']['total_messages_sent'] == 2
    print(f"[PASS] /api/profile verified. Total messages sent: {profile_data['profile']['total_messages_sent']}")

    # 13. Test Logout
    res = client.post('/api/logout')
    assert res.status_code == 200
    print("[PASS] User logged out successfully.")

    # 14. Verify Static Pages Serve Correctly
    for page in ['/', '/login', '/register', '/about']:
        res = client.get(page)
        assert res.status_code in [200, 302], f"Failed to serve {page}, got {res.status_code}"
    print("[PASS] HTML web pages (login, register, about, chat) serve successfully.")

    print("\n" + "=" * 60)
    print("      [SUCCESS] ALL 14 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    run_tests()
