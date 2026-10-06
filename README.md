# 🌐 LAN Chat Application
### A Full-Stack Real-Time Local Area Network Messaging System
**College-Level Computer Networks (CN) Capstone Project**

---

## 📋 Table of Contents
1. [Project Title & Overview](#1-project-title--overview)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Features](#4-features)
5. [Technologies Used](#5-technologies-used)
6. [System Architecture](#6-system-architecture)
7. [Network Architecture & TCP/IP Flow](#7-network-architecture--tcpip-flow)
8. [Database Design & Schema](#8-database-design--schema)
9. [REST API Documentation](#9-rest-api-documentation)
10. [WebSocket & Socket.IO Events](#10-websocket--socketio-events)
11. [Folder Structure](#11-folder-structure)
12. [Installation Guide](#12-installation-guide)
13. [Windows Setup Instructions](#13-windows-setup-instructions)
14. [How to Start the Server](#14-how-to-start-the-server)
15. [How to Connect Another Computer / Phone on LAN](#15-how-to-connect-another-computer--phone-on-lan)
16. [Windows Firewall Configuration](#16-windows-firewall-configuration)
17. [Testing & Verification Guide](#17-testing--verification-guide)
18. [User Interface & Layout](#18-user-interface--layout)
19. [Computer Networks Viva Questions & Answers](#19-computer-networks-viva-questions--answers)
20. [Future Enhancements](#20-future-enhancements)

---

## 1. Project Title & Overview
* **Project Name**: LAN Chat Application
* **Domain**: Computer Networks / Distributed Systems / Web Engineering
* **Level**: Undergraduate Engineering / Bachelor of Computer Science

The **LAN Chat Application** is a decentralized, client-server messaging system that enables multiple computers and mobile devices connected to the same Local Area Network (Wi-Fi or Ethernet switch) to exchange text messages, private 1-on-1 messages, and presence indicators in real time without needing active internet access or external cloud services.

---

## 2. Problem Statement
Most modern messaging applications (WhatsApp, Slack, Discord) depend entirely on central public cloud servers and constant internet connectivity. In isolated environments—such as:
* College computer laboratories during exams or intranet evaluations
* Disaster recovery zones with disrupted cellular infrastructure
* High-security corporate intranets with strict firewall restrictions

Users cannot communicate without a local network solution. The **LAN Chat Application** solves this problem by turning any standard computer into a local communication server accessible to all peers in the LAN.

---

## 3. Objectives
1. Implement a complete **Client-Server Architecture** using Python Flask and WebSockets.
2. Demonstrate **IP addressing and socket binding** (`0.0.0.0` vs `127.0.0.1`) on port `5000`.
3. Provide **real-time bidirectional communication** using WebSocket protocols without page reloads.
4. Manage persistent message history and user credentials using **SQLite and SQLAlchemy ORM**.
5. Implement security practices including **PBKDF2/SHA-256 password hashing** and input validation.
6. Design an intuitive, responsive dark-mode chat interface accessible on desktops, laptops, and mobile phones.

---

## 4. Features
* 🔐 **User Registration & Login**: Secure account creation with PBKDF2 password hashing and duplicate username prevention.
* 📢 **General LAN Group Chat**: Public broadcast channel where all connected devices can converse.
* 💬 **Direct 1-on-1 Private Messaging**: Select any online user to engage in private end-to-end messaging isolated by dedicated Socket.IO rooms.
* 🟢 **Real-Time Online Presence**: Live status badges (Online 🟢 / Offline 🔴) updating dynamically when users connect or disconnect.
* ⌨️ **Live Typing Indicators**: Displays `User is typing...` in real-time with automatic timeout debouncing.
* 🗃️ **Message History Persistence**: All group and private messages stored permanently in SQLite with timestamps.
* 🔍 **User Search & Directory**: Instant search filter in the sidebar to find registered colleagues.
* 👤 **Profile & Latency Diagnostics**: Built-in HTTP round-trip latency meter and LAN IP diagnostics.
* 📚 **Interactive Computer Networks Educational Page**: Interactive reference explaining LAN, TCP/IP, Sockets, and WebSockets.

---

## 5. Technologies Used

### Frontend
* **HTML5**: Semantic web markup and document structures.
* **CSS3**: Modern dark theme, CSS custom properties (variables), Flexbox, CSS Grid, animations.
* **JavaScript (ES6+)**: Asynchronous `fetch` API, DOM manipulation, Socket.IO client library.

### Backend
* **Python 3.9 - 3.14**: Core backend language.
* **Flask 3.x**: Lightweight WSGI micro-framework for routing and REST endpoints.
* **Flask-SocketIO 5.x**: WebSocket abstraction providing event-driven bidirectional transport.
* **Flask-SQLAlchemy 3.x**: Object-Relational Mapping (ORM) for database abstraction.
* **Werkzeug**: Cryptographic password hashing (`generate_password_hash`, `check_password_hash`).

### Database
* **SQLite3**: Serverless, zero-configuration relational database stored as `chat.db`.

---

## 6. System Architecture

```
+-------------------------------------------------------------------+
|                     LOCAL AREA NETWORK (LAN)                      |
|                                                                   |
|   +--------------------+                   +------------------+   |
|   |  Client Laptop A   |                   |  Client Laptop B |   |
|   | (192.168.1.15:*)   |                   | (192.168.1.22:*) |   |
|   +---------+----------+                   +--------+---------+   |
|             \                                      /              |
|   HTTP GET   \          WebSocket (Full Duplex)   /    HTTP/WS    |
|   Static/API  \                                  /                |
|                v                                v                 |
|             +--------------------------------------+              |
|             |       SERVER COMPUTER (0.0.0.0:5000) |              |
|             |          LAN IP: 192.168.1.10        |              |
|             |                                      |              |
|             |  +--------------------------------+  |              |
|             |  | Flask Web Server (HTTP)        |  |              |
|             |  | - Auth & REST API              |  |              |
|             |  | - Serves HTML / CSS / JS       |  |              |
|             |  +--------------------------------+  |              |
|             |  | Flask-SocketIO Engine (WS)     |  |              |
|             |  | - Room-based routing (General) |  |              |
|             |  | - Private room routing (User)  |  |              |
|             |  | - Online presence & typing     |  |              |
|             |  +--------------------------------+  |              |
|             |  | SQLite Relational DB (chat.db) |  |              |
|             |  | - users, messages, sessions    |  |              |
|             |  +--------------------------------+  |              |
|             +--------------------------------------+              |
+-------------------------------------------------------------------+
```

---

## 7. Network Architecture & TCP/IP Flow

### 1. TCP 3-Way Handshake
Before any data packet is exchanged, the client operating system establishes a reliable connection to the server:
1. `Client -> Server` : **SYN** (Synchronize sequence number)
2. `Server -> Client` : **SYN-ACK** (Acknowledge and synchronize)
3. `Client -> Server` : **ACK** (Connection Established)

### 2. HTTP to WebSocket Upgrade
1. Client sends an HTTP GET request with upgrade headers:
   ```http
   GET /socket.io/?EIO=4&transport=websocket HTTP/1.1
   Host: 192.168.1.10:5000
   Upgrade: websocket
   Connection: Upgrade
   ```
2. Server responds with HTTP status `101 Switching Protocols`:
   ```http
   HTTP/1.1 101 Switching Protocols
   Upgrade: websocket
   Connection: Upgrade
   ```
3. The TCP socket remains continuously open for real-time bidirectional message framing.

---

## 8. Database Design & Schema

### Table: `users`
Stores user credentials and registration metadata.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| `username` | VARCHAR(80) | UNIQUE, NOT NULL | Login username |
| `password` | VARCHAR(256) | NOT NULL | PBKDF2/SHA-256 hashed password |
| `created_at` | DATETIME | DEFAULT UTC NOW | Account creation timestamp |

### Table: `messages`
Stores both broadcast (public) and private messages.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique message identifier |
| `sender_id` | INTEGER | FOREIGN KEY -> `users.id` | User who sent the message |
| `receiver_id` | INTEGER | FOREIGN KEY -> `users.id`, NULLABLE | NULL for general broadcast, user ID for private |
| `message` | TEXT | NOT NULL | Message text body |
| `timestamp` | DATETIME | DEFAULT UTC NOW | Time of sending |
| `message_type`| VARCHAR(20)| DEFAULT 'public' | `'public'` or `'private'` |

### Table: `online_users`
Tracks real-time network presence and client IP addresses.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Record ID |
| `username` | VARCHAR(80) | UNIQUE, NOT NULL | Registered username |
| `ip_address` | VARCHAR(50) | NULLABLE | Remote client IPv4 address |
| `status` | VARCHAR(20) | DEFAULT 'offline' | `'online'` or `'offline'` |
| `last_seen` | DATETIME | DEFAULT UTC NOW | Last activity timestamp |

---

## 9. REST API Documentation

| Method | Endpoint | Description | Request Body / Parameters | Response |
|---|---|---|---|---|
| `POST` | `/api/register` | Register new account | `{"username": "..", "password": "..", "confirm_password": ".."}` | `{"success": true, "message": "..."}` |
| `POST` | `/api/login` | Authenticate user | `{"username": "..", "password": ".."}` | `{"success": true, "user": {...}}` |
| `POST` | `/api/logout` | End session & mark offline | None | `{"success": true}` |
| `GET` | `/api/users` | List all registered users | None | `{"success": true, "users": [...]}` |
| `GET` | `/api/messages` | Get General LAN messages | None | `{"success": true, "messages": [...]}` |
| `GET` | `/api/messages/<user>` | Get private chat history | `<user>` in URL | `{"success": true, "messages": [...]}` |
| `POST` | `/api/messages` | Fallback REST message send | `{"message": "..", "receiver": ".."}` | `{"success": true, "message": {...}}` |
| `GET` | `/api/status` | Server network diagnostic | None | `{"lan_ip": "..", "port": 5000, ...}` |
| `GET` | `/api/profile` | Current user profile stats | None | `{"profile": {...}}` |

---

## 10. WebSocket & Socket.IO Events

| Event Name | Direction | Payload | Description |
|---|---|---|---|
| `connect` | Client -> Server | None | Triggered when client establishes WebSocket connection. |
| `disconnect`| Client -> Server | None | Triggered on socket termination; marks user offline. |
| `join` | Client -> Server | `{"username": "Suba"}` | Enters user into `general` room and personal private room. |
| `send_message` | Client -> Server | `{"message": "Hello", "sender": "Suba"}` | Broadcasts message to room `general`. |
| `receive_message` | Server -> Client | Message object | Emitted to all clients in `general`. |
| `private_message` | Bidirectional | `{"receiver": "Priya", "message": "Hi"}` | Delivered exclusively to recipient's and sender's rooms. |
| `typing` | Bidirectional | `{"room": "general", "username": "Suba"}` | Notifies room participants that a user is typing. |
| `stop_typing`| Bidirectional | `{"room": "general", "username": "Suba"}` | Removes the typing indicator. |
| `user_online`| Server -> All | `{"username": "Suba", "ip": "..."}` | Broadcast when user comes online. |
| `user_offline`| Server -> All | `{"username": "Suba"}` | Broadcast when user goes offline. |

---

## 11. Folder Structure

```
LAN-Chat-Application/
│
├── backend/
│   ├── app.py              # Main Flask server & SocketIO entry point
│   ├── database.py         # SQLAlchemy instance & table initializer
│   ├── models.py           # User, Message, OnlineUser ORM models
│   ├── routes.py           # HTTP routes & REST API endpoints
│   ├── auth.py             # Password hashing, verification & session handling
│   ├── socket_events.py    # WebSocket event handlers (chat, presence, typing)
│   ├── requirements.txt    # Backend Python package list
│   └── chat.db             # Auto-generated SQLite database
│
├── frontend/
│   ├── login.html          # Authentication page
│   ├── register.html       # User sign up page
│   ├── chat.html           # Full-featured modern chat dashboard
│   ├── profile.html        # User profile & network latency diagnostics
│   ├── about.html          # Computer Networks educational concepts guide
│   │
│   ├── css/
│   │   └── style.css       # Responsive dark-theme stylesheet
│   │
│   └── js/
│       ├── login.js        # Login form handler & validation
│       ├── register.js     # Registration form handler & validation
│       └── chat.js         # Socket.IO client, presence, & UI controller
│
├── run_server.bat          # 1-Click Windows server startup script
├── setup.bat               # 1-Click Windows virtual environment setup script
├── requirements.txt        # Root dependency list
└── README.md               # Project documentation
```

---

## 12. Installation Guide

### Prerequisites
* Windows 10 or 11 (also runs on Linux or macOS)
* Python 3.9 or higher (Python 3.14 fully supported)

### Method A: 1-Click Automatic Setup (Recommended for Windows)
1. Double-click `setup.bat`.
2. The script will automatically create a Python virtual environment (`venv`) and install all required libraries.
3. Once completed, double-click `run_server.bat` to launch the server.

### Method B: Manual Command-Line Setup (PowerShell / CMD)
Open Windows PowerShell inside the project directory:

```powershell
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
venv\Scripts\activate

# 3. Upgrade pip and install dependencies
pip install -r requirements.txt
```

---

## 13. Windows Setup Instructions

### What each command does:
1. `python -m venv venv`:
   Creates an isolated environment for Python packages so they do not conflict with system-wide software.
2. `venv\Scripts\activate`:
   Points your current terminal session to use the Python binary inside the virtual environment.
3. `pip install -r requirements.txt`:
   Downloads and installs Flask, Flask-SocketIO, SQLAlchemy, and simple-websocket.

> [!NOTE]
> If PowerShell shows an `Execution_Policies` script error when running `activate`, run this command once:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## 14. How to Start the Server

1. Open PowerShell in the project directory and run:
   ```powershell
   cd backend
   python app.py
   ```
2. You will see the server startup banner:
   ```
   ====================================================================
         LAN CHAT APPLICATION - COMPUTER NETWORKS PROJECT
   ====================================================================
     * Local Access (This PC) : http://127.0.0.1:5000
     * LAN Access (Other PCs) : http://192.168.1.10:5000
     * Bound Interface        : 0.0.0.0 (All Network Interfaces)
     * Port                   : 5000
   ====================================================================
   ```
3. Open your browser on the host PC and go to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 15. How to Connect Another Computer / Phone on LAN

1. **Connect to the same Wi-Fi / Router**:
   Ensure both the Server PC and Client devices (Laptop 2, Smartphone, Tablet) are connected to the exact same Wi-Fi network or Ethernet router.

2. **Note the Server's LAN IP**:
   Check the console banner when running `app.py`. For example: `http://192.168.1.10:5000`.

3. **Open Browser on Other Devices**:
   On Computer 2 or your smartphone, open Chrome, Edge, or Safari, and enter:
   ```
   http://192.168.1.10:5000
   ```
   *(Replace `192.168.1.10` with your server's actual LAN IP).*

4. **Register & Chat**:
   * Create an account (e.g. `Priya` on Computer 2).
   * Notice how both `Suba` and `Priya` instantly appear with 🟢 indicators in real time!

---

## 16. Windows Firewall Configuration

When connecting from another computer, Windows Defender Firewall might block incoming connections on port 5000. 

### Quick PowerShell Fix (Run as Administrator):
Open PowerShell as Administrator and run:
```powershell
New-NetFirewallRule -DisplayName "LAN Chat Server (Port 5000)" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### Manual GUI Method:
1. Press `Win + R`, type `firewall.cpl`, and hit Enter.
2. Click **Advanced settings** on the left panel.
3. Click **Inbound Rules** -> **New Rule...**
4. Select **Port** -> click **Next**.
5. Choose **TCP**, specify **Specific local ports: 5000** -> click **Next**.
6. Select **Allow the connection** -> click **Next**.
7. Keep Domain, Private, and Public checked -> name it `LAN Chat Server` -> click **Finish**.

---

## 17. Testing & Verification Guide

| Test Scenario | Steps | Expected Outcome |
|---|---|---|
| **1. User Registration** | Go to `/register`, enter `Suba` and password. | Successful registration, redirected to `/login`. Password stored hashed in `chat.db`. |
| **2. Dual Client Login** | Open Browser 1 (Normal) as `Suba`. Open Browser 2 (Incognito) as `Priya`. | Both users show 🟢 Online status in the sidebar. |
| **3. Broadcast Chat** | `Suba` types "Hello LAN!" in General Chat. | "Hello LAN!" appears instantly on `Priya`'s screen without page refresh. |
| **4. Private Chat** | `Suba` clicks `Priya` in the sidebar and sends "Are you free?". | Only `Priya` receives the message. Other users in the room do not see it. |
| **5. Typing Indicator** | `Priya` starts typing in message box. | `Suba` sees "Priya is typing..." with animated bouncing dots. |
| **6. User Disconnect** | Close `Priya`'s browser tab. | Status updates dynamically to 🔴 Offline for `Suba`. |
| **7. Chat Persistence** | Refresh browser or restart server. | All historical messages reload cleanly from `chat.db`. |

---

## 18. User Interface & Layout

```
-----------------------------------------------------------------------------
| 🌐 LAN CHAT APPLICATION    [Server: 192.168.1.10:5000]   👤 Suba   🚪 Logout |
-----------------------------------------------------------------------------
| [🔍 Search users... ]   | 📢 General LAN Chat                              |
|                         | Broadcast channel for all connected clients       |
| LAN CHANNELS            |--------------------------------------------------|
| 📢 General LAN Chat     | Priya: Hello everyone!                  10:30 AM |
|                         | Suba: Welcome to our Computer Networks project!  |
| ONLINE USERS (2)        |                                         10:31 AM |
| 🟢 Priya  (192.168.1.15)| Priya: Let's test private messaging.    10:32 AM |
|                         |                                                  |
| OFFLINE USERS (1)       |                                                  |
| 🔴 Anu    (Last seen)   |                                                  |
|                         |--------------------------------------------------|
|                         | [ Priya is typing... ]                           |
|                         | [Type a message...                 ]  [ ➤ SEND ] |
-----------------------------------------------------------------------------
```

---

## 19. Computer Networks Viva Questions & Answers

### Q1: Why did you bind the server to `0.0.0.0` instead of `127.0.0.1`?
**Ans**: `127.0.0.1` is the loopback interface, meaning the operating system only accepts connections originating from the exact same local machine. `0.0.0.0` is a meta-address instructing the network layer to listen on *all* configured IPv4 network interfaces (Ethernet, Wi-Fi, loopback), allowing external LAN clients to reach port 5000.

### Q2: What is the difference between WebSockets and HTTP Polling?
**Ans**: HTTP is half-duplex and request-response driven: every update requires the client to initiate a new TCP connection or send repeated HTTP requests (polling), creating severe packet overhead. WebSockets perform an initial HTTP handshake and upgrade to a persistent, full-duplex TCP channel over a single socket, allowing the server to push messages immediately upon receipt with minimal framing overhead.

### Q3: What transport protocol does your application use?
**Ans**: It uses **TCP (Transmission Control Protocol)**. Chat applications require reliable, ordered byte delivery without lost characters or out-of-order sentences, which TCP guarantees via acknowledgments and retransmissions.

### Q4: How does private messaging work under Socket.IO?
**Ans**: When a client joins, they are placed in a logical room named after their unique `username` (`join_room(username)`). When User A sends a private message to User B, the server routes the packet specifically to `room=User_B` and `room=User_A`, bypassing the general broadcast room.

### Q5: How is data stored and preserved?
**Ans**: The backend utilizes **SQLite** relational database managed through **SQLAlchemy ORM**. Every incoming socket event triggers an insert transaction into the `messages` table with sender ID, receiver ID, timestamp, and message text before emission.

---

## 20. Future Enhancements
1. **File & Image Transfer**: Chunked binary transfer over WebSockets or multipart upload to share documents over LAN.
2. **Audio/Video Calls**: Integrating WebRTC peer-to-peer media streams with Flask-SocketIO acting as the signaling server.
3. **End-to-End Encryption (E2EE)**: Implementing Diffie-Hellman key exchange and AES-256 in client-side JavaScript.
4. **Voice Notes**: Recording audio clips via MediaRecorder API and streaming them locally.

---
*Created for Computer Networks Laboratory Evaluation & Project Presentation.*
