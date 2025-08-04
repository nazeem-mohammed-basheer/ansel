document.addEventListener('DOMContentLoaded', function() {
    // Get references to HTML elements
    const adminUsernameInput = document.getElementById('adminUsername'); // New: for username
    const adminPasswordInput = document.getElementById('adminPassword');
    const loginBtn = document.getElementById('loginBtn');
    const passwordPrompt = document.getElementById('passwordPrompt');
    const adminPanel = document.getElementById('adminPanel');
    const mediaForm = document.getElementById('mediaForm');
    const mediaTitleInput = document.getElementById('mediaTitle');
    const mediaDescriptionTextarea = document.getElementById('mediaDescription');
    const mediaTypeSelect = document.getElementById('mediaType');
    const mediaFileInput = document.getElementById('mediaFile');
    const mediaDisplay = document.getElementById('mediaDisplay');
    const messageBox = document.getElementById('messageBox');
    const logoutBtn = document.getElementById('logoutBtn'); // New: Logout button

    // --- Configuration for your Django API ---
    const API_BASE_URL = 'http://127.0.0.1:8000/api/media/';
    const LOGIN_API_URL = 'http://127.0.0.1:8000/api/auth/token/'; // Login API endpoint
    const REGISTER_API_URL = 'http://127.0.0.1:8000/api/auth/register/'; // Registration API endpoint
    const EVENTS_CREATE_API_URL = 'http://127.0.0.1:8000/api/media/events/create/'; // New: Event creation API

    let authToken = null; // Store the authentication token
    let isUserAdmin = false; // Store admin status

    // --- Helper function to get CSRF token from cookies ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- Message Box Function ---
    function showMessage(message, type = 'success') {
        messageBox.textContent = message;
        messageBox.className = 'message-box show';
        if (type === 'error') {
            messageBox.classList.add('error');
        } else {
            messageBox.classList.remove('error');
        }

        setTimeout(() => {
            messageBox.classList.remove('show');
        }, 3000);
    }

    // --- Authentication Flow ---

    // Function to check if a token exists and attempt to log in
    function checkLoginStatus() {
        authToken = localStorage.getItem('authToken');
        isUserAdmin = (localStorage.getItem('isStaff') === 'true'); // Retrieve admin status

        if (authToken && isUserAdmin) { // Only show admin panel if authenticated AND admin
            passwordPrompt.style.display = 'none';
            adminPanel.style.display = 'block';
            showMessage('Welcome back, Admin!', 'success');
            loadMediaFromBackend(); // Load existing media
            // Potentially load events for admin panel here as well if you add an event management section
        } else if (authToken && !isUserAdmin) {
            // User is logged in but not an admin, redirect or show message
            showMessage('Logged in as a regular user. Admin access denied.', 'error');
            window.location.href = '/'; // Redirect regular users from admin page
        }
        else {
            // No token, show login prompt
            passwordPrompt.style.display = 'block';
            adminPanel.style.display = 'none';
        }
    }

    // Login event listener
    loginBtn.addEventListener('click', async function() {
        const username = adminUsernameInput.value.trim();
        const password = adminPasswordInput.value.trim();

        if (!username || !password) {
            showMessage('Please enter both username and password.', 'error');
            return;
        }

        try {
            const response = await fetch(LOGIN_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();
            if (response.ok) {
                authToken = data.token;
                // We need to fetch user details to get is_staff status, as CustomAuthToken doesn't return it by default
                // For now, we'll assume if they log in via admin panel, they might be admin.
                // A better way is to extend CustomAuthToken to return is_staff.
                // Let's modify CustomAuthToken in api_views.py to return is_staff.
                isUserAdmin = data.is_staff; // Assuming is_staff is returned from CustomAuthToken

                localStorage.setItem('authToken', authToken);
                localStorage.setItem('isStaff', isUserAdmin); // Store admin status
                localStorage.setItem('username', data.username); // Store username

                if (isUserAdmin) {
                    passwordPrompt.style.display = 'none';
                    adminPanel.style.display = 'block';
                    showMessage('Login successful! Welcome, Admin.', 'success');
                    loadMediaFromBackend();
                    adminUsernameInput.value = '';
                    adminPasswordInput.value = '';
                } else {
                    showMessage('Login successful, but you are not an administrator. Redirecting...', 'error');
                    authToken = null; // Clear token for non-admin on admin page
                    localStorage.removeItem('authToken');
                    localStorage.removeItem('isStaff');
                    localStorage.removeItem('username');
                    window.location.href = '/'; // Redirect non-admin users
                }
            } else {
                // Use showMessage for authentication messages
                showMessage(data.non_field_errors ? data.non_field_errors[0] : 'Login failed.', 'error');
            }
        } catch (error) {
            console.error('Login request failed:', error);
            showMessage(`Login failed: ${error.message || 'Invalid credentials'}`, 'error');
        }
    });

    // Logout event listener
    logoutBtn.addEventListener('click', function() {
        authToken = null;
        isUserAdmin = false;
        localStorage.removeItem('authToken');
        localStorage.removeItem('isStaff');
        localStorage.removeItem('username');
        showMessage('Logged out successfully.', 'success');
        checkLoginStatus(); // Go back to login prompt
    });

    // Handle Enter key for login form
    adminPasswordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loginBtn.click();
        }
    });
    adminUsernameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            adminPasswordInput.focus();
        }
    });


    // --- Helper function to get headers with authorization token ---
    function getAuthHeaders(contentType = 'application/json') {
        const headers = {};
        if (contentType) {
            headers['Content-Type'] = contentType;
        }
        if (authToken) {
            headers['Authorization'] = `Token ${authToken}`;
        }
        // Include CSRF token for all authenticated POST/PUT/DELETE requests if not using FormData
        // For FormData, the browser sets Content-Type automatically, so don't set it manually.
        // The CSRF token is still needed for non-GET requests.
        const csrftoken = getCookie('csrftoken');
        if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken;
        }
        return headers;
    }


    // --- Media Management with Django Backend ---

    function renderMediaItem(media) {
        const mediaItemDiv = document.createElement('div');
        mediaItemDiv.classList.add('admin-media-item');
        mediaItemDiv.dataset.id = media.id;

        let mediaPreviewHtml = '';
        if (media.file) {
            if (media.media_type === 'image') {
                mediaPreviewHtml = `<img src="${media.file}" alt="${media.title}" class="media-preview">`;
            } else if (media.media_type === 'audio') {
                mediaPreviewHtml = `<div class="media-preview placeholder">🎵</div>`;
            } else if (media.media_type === 'video') {
                mediaPreviewHtml = `<div class="media-preview placeholder">🎬</div>`;
            }
        } else {
            mediaPreviewHtml = `<div class="media-preview placeholder">?</div>`;
        }

        mediaItemDiv.innerHTML = `
            ${mediaPreviewHtml}
            <div class="media-info">
                <h4>${media.title} (${media.media_type})</h4>
                <p>${media.description || 'No description'}</p>
                <p>File: ${media.file ? media.file.split('/').pop() : 'N/A'}</p>
            </div>
            <button class="delete-btn">Delete</button>
        `;

        mediaItemDiv.querySelector('.delete-btn').addEventListener('click', function() {
            deleteMediaItem(media.id);
        });

        mediaDisplay.appendChild(mediaItemDiv);
    }

    async function loadMediaFromBackend() {
        mediaDisplay.innerHTML = '';
        try {
            const response = await fetch(API_BASE_URL, {
                method: 'GET',
                headers: getAuthHeaders(''), // No Content-Type for GET
            });
            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    showMessage('Unauthorized. Please log in.', 'error');
                    authToken = null;
                    localStorage.removeItem('authToken');
                    checkLoginStatus();
                    return;
                }
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const mediaList = await response.json();
            mediaList.forEach(media => renderMediaItem(media));
            if (mediaList.length === 0) {
                mediaDisplay.innerHTML = '<p style="text-align: center; color: #666;">No media found. Add some above!</p>';
            }
        } catch (error) {
            console.error('Error fetching media:', error);
            showMessage('Failed to load media. Please check backend connection.', 'error');
        }
    }

    mediaForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const title = mediaTitleInput.value.trim();
        const description = mediaDescriptionTextarea.value.trim();
        const media_type = mediaTypeSelect.value;
        const file = mediaFileInput.files[0];

        if (!title || !file) {
            showMessage('Please provide a title and select a file.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', description);
        formData.append('media_type', media_type);
        formData.append('file', file);

        try {
            const response = await fetch(API_BASE_URL, {
                method: 'POST',
                // For FormData, DO NOT set 'Content-Type', the browser handles it.
                // Just include 'Authorization' and 'X-CSRFToken'.
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'X-CSRFToken': getCookie('csrftoken') // <-- CSRF token for FormData
                },
                body: formData,
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    showMessage('Unauthorized. Please log in again.', 'error');
                    authToken = null;
                    localStorage.removeItem('authToken');
                    checkLoginStatus();
                    return;
                }
                const errorData = await response.json();
                console.error('Error adding media:', errorData);
                throw new Error(`Failed to add media: ${JSON.stringify(errorData)}`);
            }

            const newMedia = await response.json();
            renderMediaItem(newMedia);
            showMessage('Media added successfully!', 'success');
            mediaForm.reset();
        } catch (error) {
            console.error('Error submitting media:', error);
            showMessage('Failed to add media. Please check your input and backend.', 'error');
        }
    });

    async function deleteMediaItem(idToDelete) {
        try {
            const response = await fetch(`${API_BASE_URL}${idToDelete}/`, {
                method: 'DELETE',
                headers: getAuthHeaders(), // getAuthHeaders will now include CSRF
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    showMessage('Unauthorized. Please log in again.', 'error');
                    authToken = null;
                    localStorage.removeItem('authToken');
                    checkLoginStatus();
                    return;
                }
                throw new Error(`Failed to delete media. Status: ${response.status}`);
            }

            const itemToRemove = mediaDisplay.querySelector(`[data-id="${idToDelete}"]`);
            if (itemToRemove) {
                itemToRemove.remove();
            }
            showMessage('Media deleted successfully!', 'success');
        } catch (error) {
            console.error('Error deleting media:', error);
            showMessage('Failed to delete media. Please try again.', 'error');
        }
    }

    // --- HYPOTHETICAL REGISTRATION SECTION (for demonstration of CSRF) ---
    // You would integrate this with your actual registration form elements.
    const registerUsernameInput = document.getElementById('registerUsername'); // Assume these exist in your HTML
    const registerEmailInput = document.getElementById('registerEmail');
    const registerPasswordInput = document.getElementById('registerPassword');
    const registerPassword2Input = document.getElementById('registerPassword2');
    const registerBtn = document.getElementById('registerBtn'); // Assume a button with this ID

    if (registerBtn) {
        registerBtn.addEventListener('click', async function() {
            const username = registerUsernameInput.value.trim();
            const email = registerEmailInput.value.trim();
            const password = registerPasswordInput.value.trim();
            const password2 = registerPassword2Input.value.trim();

            if (!username || !email || !password || !password2) {
                showMessage('All registration fields are required.', 'error');
                return;
            }

            if (password !== password2) {
                showMessage('Passwords do not match.', 'error');
                return;
            }

            const csrftoken = getCookie('csrftoken'); // Get the CSRF token

            try {
                const response = await fetch(REGISTER_API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken, // <-- IMPORTANT: Include the CSRF token here for registration
                    },
                    body: JSON.stringify({ username, email, password, password2 })
                });

                const data = await response.json();

                if (response.ok) { // Status code 200-299
                    showMessage(data.message || 'Registration successful!', 'success');
                    // Clear form or redirect to login page
                    registerUsernameInput.value = '';
                    registerEmailInput.value = '';
                    registerPasswordInput.value = '';
                    registerPassword2Input.value = '';
                } else { // Status code 400, 403, 500, etc.
                    let errorMessage = 'Registration failed. An unknown error occurred.';
                    if (response.status === 403) {
                        errorMessage = 'Registration forbidden. Please refresh the page and try again.';
                    } else if (data.detail) {
                        errorMessage = data.detail;
                    } else if (data.email && data.email.length > 0) {
                        errorMessage = `Email: ${data.email[0]}`; // Specific email error
                    } else if (data.username && data.username.length > 0) {
                        errorMessage = `Username: ${data.username[0]}`; // Specific username error
                    } else if (data.password && data.password.length > 0) {
                        errorMessage = `Password: ${data.password[0]}`; // Specific password error
                    }
                    showMessage(errorMessage, 'error');
                }
            } catch (error) {
                console.error('Registration request failed:', error);
                showMessage('Registration failed: Could not connect to the server.', 'error');
            }
        });
    }
    // --- END HYPOTHETICAL REGISTRATION SECTION ---


    // --- Initial check on page load ---
    checkLoginStatus();
});
