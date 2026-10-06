// JavaScript for register.html
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
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

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideAlert();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Front-end validations
        if (!username || !password || !confirmPassword) {
            showAlert('Please fill in all fields.');
            return;
        }

        if (password.length < 4) {
            showAlert('Password must be at least 4 characters long.');
            return;
        }

        if (password !== confirmPassword) {
            showAlert('Passwords do not match! Please check again.');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Registering User...';

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    confirm_password: confirmPassword
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showAlert('Account created successfully! Redirecting to login...', 'success');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1200);
            } else {
                showAlert(data.error || 'Failed to create account.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span>Create Account</span> &rarr;';
            }
        } catch (err) {
            showAlert('Cannot communicate with Flask server. Check server connection.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>Create Account</span> &rarr;';
        }
    });
});
