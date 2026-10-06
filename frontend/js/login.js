// JavaScript for login.html
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const alertBox = document.getElementById('alertBox');
    const submitBtn = document.getElementById('submitBtn');

    function showAlert(message, type = 'danger') {
        alertBox.className = `alert alert-${type}`;
        alertBox.textContent = message;
        alertBox.style.display = 'block';
    }

    function hideAlert() {
        alertBox.style.display = 'none';
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !password) {
            showAlert('Please enter both username and password.');
            return;
        }

        // Disable button while processing
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Signing In...';

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showAlert('Login successful! Redirecting to LAN chat...', 'success');
                // Store active username in localStorage for frontend state
                localStorage.setItem('lan_chat_user', data.user.username);
                setTimeout(() => {
                    window.location.href = '/chat';
                }, 600);
            } else {
                showAlert(data.error || 'Login failed. Please check credentials.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span>Sign In to LAN</span> &rarr;';
            }
        } catch (err) {
            showAlert('Cannot connect to Flask server. Please make sure the server is running on the LAN.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>Sign In to LAN</span> &rarr;';
        }
    });
});
