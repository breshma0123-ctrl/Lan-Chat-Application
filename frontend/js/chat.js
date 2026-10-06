/**
 * LAN Chat Application - Client-side WebSocket & Dashboard Logic
 * Demonstrates real-time Socket.IO communication, room switching,
 * message rendering, online presence detection, and typing indicators.
 */

let currentUser = null;
let activeChat = 'general'; // 'general' or username of private chat partner
let socket = null;
let typingTimeout = null;
let isCurrentlyTyping = false;
let allUsers = [];
let unreadCounts = {}; // { username: count, 'general': count }

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Verify user session and fetch current profile
    const authenticated = await fetchCurrentUser();
    if (!authenticated) {
        window.location.href = '/login';
        return;
    }

    // 2. Fetch server network status (LAN IP & port)
    fetchServerStatus();

    // 3. Initialize WebSocket (Socket.IO)
    initSocket();

    // 4. Load initial users list & general chat history
    await loadUsers();
    await loadChatHistory();

    // 5. Setup event listeners
    setupEventListeners();

    // Periodic poll for user statuses every 10 seconds as backup
    setInterval(loadUsers, 10000);
});

// ==============================================================================
// Authentication & Server Network Status
// ==============================================================================

async function fetchCurrentUser() {
    try {
        const res = await fetch('/api/profile');
        if (!res.ok) return false;
        const data = await res.json();
        if (data.success && data.profile) {
            currentUser = data.profile;
            document.getElementById('currentUserName').textContent = currentUser.username;
            document.getElementById('currentUserAvatar').textContent = currentUser.username.charAt(0).toUpperCase();
            return true;
        }
        return false;
    } catch (err) {
        console.error('Error fetching current user profile:', err);
        return false;
    }
}

async function fetchServerStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.success) {
            const ipDisplay = document.getElementById('serverIpDisplay');
            ipDisplay.textContent = `${data.lan_ip}:${data.port}`;
            document.getElementById('serverPill').title = `LAN IP: ${data.lan_ip} | Local: ${data.local_url}`;
        }
    } catch (err) {
        console.error('Failed to fetch server status:', err);
    }
}

// ==============================================================================
// Socket.IO Initialization & Event Handlers
// ==============================================================================

function initSocket() {
    // Connect to the same host/port serving this page
    socket = io();

    socket.on('connect', () => {
        console.log('[WEBSOCKET] Connected to LAN server with SID:', socket.id);
        // Announce user presence on the network
        socket.emit('join', { username: currentUser.username });
    });

    socket.on('disconnect', () => {
        console.warn('[WEBSOCKET] Disconnected from server. Reconnecting...');
        appendSystemMessage('Disconnected from server. Attempting to reconnect...');
    });

    // Group broadcast message received
    socket.on('receive_message', (msg) => {
        if (activeChat === 'general') {
            appendMessage(msg, msg.sender === currentUser.username);
        } else {
            // Increment unread count for General chat
            incrementUnread('general');
        }
    });

    // 1-on-1 private message received
    socket.on('private_message', (msg) => {
        const isFromMe = msg.sender === currentUser.username;
        const chatPartner = isFromMe ? msg.receiver : msg.sender;

        if (activeChat === chatPartner) {
            appendMessage(msg, isFromMe);
        } else {
            // Increment unread count for this user
            incrementUnread(chatPartner);
        }
    });

    // Another user joined / came online
    socket.on('user_online', (data) => {
        if (data.username !== currentUser.username) {
            appendSystemMessage(`🟢 ${data.username} is now online on LAN (${data.ip_address || 'LAN'})`);
        }
        loadUsers();
    });

    // Another user disconnected / went offline
    socket.on('user_offline', (data) => {
        if (data.username !== currentUser.username) {
            appendSystemMessage(`🔴 ${data.username} went offline`);
        }
        loadUsers();
    });

    // Full online users list broadcast
    socket.on('online_users_list', () => {
        loadUsers();
    });

    // Typing indicators
    socket.on('typing', (data) => {
        if (data.username === currentUser.username) return;

        if (activeChat === 'general' && data.room === 'general') {
            showTypingIndicator(`${data.username} is typing...`);
        } else if (activeChat === data.username) {
            showTypingIndicator(`${data.username} is typing...`);
        }
    });

    socket.on('stop_typing', (data) => {
        if (data.username === currentUser.username) return;

        if ((activeChat === 'general' && data.room === 'general') || activeChat === data.username) {
            hideTypingIndicator();
        }
    });
}

// ==============================================================================
// Users Management & Sidebar Rendering
// ==============================================================================

async function loadUsers() {
    try {
        const res = await fetch('/api/users');
        const data = await res.json();
        if (data.success && data.users) {
            allUsers = data.users;
            renderUserLists();
        }
    } catch (err) {
        console.error('Error loading users:', err);
    }
}

function renderUserLists() {
    const filterQuery = (document.getElementById('userSearchInput').value || '').toLowerCase();
    const onlineContainer = document.getElementById('onlineUsersList');
    const offlineContainer = document.getElementById('offlineUsersList');

    onlineContainer.innerHTML = '';
    offlineContainer.innerHTML = '';

    let onlineCount = 0;
    let offlineCount = 0;

    allUsers.forEach(user => {
        // Skip current user in the messaging directory
        if (user.is_current_user) return;

        if (filterQuery && !user.username.toLowerCase().includes(filterQuery)) {
            return;
        }

        const isOnline = user.status === 'online';
        if (isOnline) onlineCount++;
        else offlineCount++;

        const unread = unreadCounts[user.username] || 0;
        const isActive = activeChat === user.username;

        const userItem = document.createElement('div');
        userItem.className = `sidebar-item ${isActive ? 'active' : ''}`;
        userItem.onclick = () => switchChat(user.username);

        userItem.innerHTML = `
            <div class="item-avatar">
                ${user.username.charAt(0).toUpperCase()}
                <span class="status-indicator ${isOnline ? 'online' : 'offline'}"></span>
            </div>
            <div class="item-info">
                <div class="item-name">
                    <span>${escapeHtml(user.username)}</span>
                    ${unread > 0 ? `<span class="unread-badge">${unread}</span>` : ''}
                </div>
                <div class="item-subtext">${isOnline ? 'IP: ' + (user.ip_address || 'LAN') : 'Offline'}</div>
            </div>
        `;

        if (isOnline) {
            onlineContainer.appendChild(userItem);
        } else {
            offlineContainer.appendChild(userItem);
        }
    });

    document.getElementById('onlineCountBadge').textContent = onlineCount;
    document.getElementById('offlineCountBadge').textContent = offlineCount;
}

// ==============================================================================
// Chat Switching & History Loading
// ==============================================================================

async function switchChat(target) {
    if (activeChat === target) return;

    activeChat = target;

    // Reset unread count for this target
    unreadCounts[target] = 0;
    if (target === 'general') {
        const badge = document.getElementById('generalUnread');
        badge.style.display = 'none';
        badge.textContent = '0';
    }

    // Update active class on General tab
    const genTab = document.getElementById('generalChatTab');
    if (target === 'general') {
        genTab.classList.add('active');
    } else {
        genTab.classList.remove('active');
    }

    // Re-render sidebar to highlight active user
    renderUserLists();

    // Update Chat Header
    const avatar = document.getElementById('chatHeaderAvatar');
    const title = document.getElementById('chatHeaderTitle');
    const subtitle = document.getElementById('chatHeaderSubtitle');

    if (target === 'general') {
        avatar.textContent = '📢';
        avatar.style.background = 'var(--accent-gradient)';
        title.textContent = 'General LAN Chat';
        subtitle.textContent = 'Broadcast channel for all connected network clients';
    } else {
        avatar.textContent = target.charAt(0).toUpperCase();
        avatar.style.background = '#4f46e5';
        title.textContent = `Private Chat: ${target}`;
        const targetUserObj = allUsers.find(u => u.username === target);
        const statusText = (targetUserObj && targetUserObj.status === 'online') ? '🟢 Online' : '🔴 Offline';
        subtitle.textContent = `Direct private channel &bull; ${statusText}`;
    }

    // Clear and load messages
    hideTypingIndicator();
    await loadChatHistory();
}

async function loadChatHistory() {
    const container = document.getElementById('messagesContainer');
    container.innerHTML = '';

    const url = activeChat === 'general' ? '/api/messages' : `/api/messages/${encodeURIComponent(activeChat)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();

        if (data.success && data.messages) {
            if (data.messages.length === 0) {
                appendSystemMessage(
                    activeChat === 'general' 
                        ? 'No messages yet in General LAN Chat. Say hello!' 
                        : `No previous private messages with ${activeChat}. Start the conversation!`
                );
            } else {
                data.messages.forEach(msg => {
                    appendMessage(msg, msg.sender === currentUser.username);
                });
            }
        }
    } catch (err) {
        console.error('Error fetching chat history:', err);
        appendSystemMessage('Failed to load message history.');
    }

    scrollToBottom();
}

// ==============================================================================
// Message Rendering & UI Helpers
// ==============================================================================

function appendMessage(msg, isSelf) {
    const container = document.getElementById('messagesContainer');

    const row = document.createElement('div');
    row.className = `message-row ${isSelf ? 'self' : 'other'}`;

    const senderInitial = (msg.sender || 'U').charAt(0).toUpperCase();

    row.innerHTML = `
        <div class="message-avatar">${senderInitial}</div>
        <div class="message-content">
            ${!isSelf ? `<div class="message-sender">${escapeHtml(msg.sender)}</div>` : ''}
            <div class="message-bubble">
                <div class="message-text">${escapeHtml(msg.message)}</div>
                <div class="message-meta">
                    <span>${msg.time || 'Now'}</span>
                </div>
            </div>
        </div>
    `;

    container.appendChild(row);
    scrollToBottom();
}

function appendSystemMessage(text) {
    const container = document.getElementById('messagesContainer');
    const pill = document.createElement('div');
    pill.className = 'system-pill';
    pill.textContent = text;
    container.appendChild(pill);
    scrollToBottom();
}

function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    container.scrollTop = container.scrollHeight;
}

function incrementUnread(target) {
    unreadCounts[target] = (unreadCounts[target] || 0) + 1;
    if (target === 'general') {
        const badge = document.getElementById('generalUnread');
        badge.textContent = unreadCounts['general'];
        badge.style.display = 'inline-block';
    } else {
        renderUserLists();
    }
}

function showTypingIndicator(text) {
    const indicator = document.getElementById('typingIndicator');
    const typingText = document.getElementById('typingText');
    typingText.textContent = text;
    indicator.style.visibility = 'visible';
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    indicator.style.visibility = 'hidden';
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, function(match) {
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
        return map[match];
    });
}

// ==============================================================================
// Event Listeners (Sending Messages, Typing, Search, Logout)
// ==============================================================================

function setupEventListeners() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const generalChatTab = document.getElementById('generalChatTab');
    const userSearchInput = document.getElementById('userSearchInput');
    const refreshBtn = document.getElementById('refreshBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    // Send on button click
    sendBtn.addEventListener('click', handleSendMessage);

    // Send on Enter keypress
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Typing debounce
    messageInput.addEventListener('input', () => {
        if (!socket || !currentUser) return;

        if (!isCurrentlyTyping) {
            isCurrentlyTyping = true;
            socket.emit('typing', {
                room: activeChat === 'general' ? 'general' : activeChat,
                username: currentUser.username
            });
        }

        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            isCurrentlyTyping = false;
            socket.emit('stop_typing', {
                room: activeChat === 'general' ? 'general' : activeChat,
                username: currentUser.username
            });
        }, 1500);
    });

    // General chat switch
    generalChatTab.addEventListener('click', () => {
        switchChat('general');
    });

    // User search filter
    userSearchInput.addEventListener('input', () => {
        renderUserLists();
    });

    // Manual refresh
    refreshBtn.addEventListener('click', () => {
        loadUsers();
        loadChatHistory();
    });

    // Logout
    logoutBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to log out of the LAN chat?')) {
            try {
                if (socket) socket.disconnect();
                await fetch('/api/logout', { method: 'POST' });
            } catch (err) {
                console.error('Logout error:', err);
            }
            localStorage.removeItem('lan_chat_user');
            window.location.href = '/login';
        }
    });
}

function handleSendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();

    if (!text || !socket || !currentUser) return;

    if (activeChat === 'general') {
        socket.emit('send_message', {
            message: text,
            sender: currentUser.username
        });
    } else {
        socket.emit('private_message', {
            receiver: activeChat,
            message: text,
            sender: currentUser.username
        });
    }

    // Clear typing state & input box
    if (isCurrentlyTyping) {
        isCurrentlyTyping = false;
        socket.emit('stop_typing', {
            room: activeChat === 'general' ? 'general' : activeChat,
            username: currentUser.username
        });
    }

    input.value = '';
    input.focus();
}
