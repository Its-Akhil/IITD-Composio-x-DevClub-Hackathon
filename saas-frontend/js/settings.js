// Settings Page JavaScript

// Initialize settings page
function initSettings() {
    // Check authentication
    if (!window.auth.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }

    // Load user info
    loadUserInfo();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load settings data
    loadSettingsData();
    
    // Setup mobile menu
    setupMobileMenu();
}

// Load user info
function loadUserInfo() {
    const user = window.auth.getCurrentUser();
    if (user) {
        document.getElementById('dropdownName').textContent = user.name;
        document.getElementById('dropdownEmail').textContent = user.email;
        document.getElementById('headerAvatar').src = user.avatar;
        document.getElementById('dropdownAvatar').src = user.avatar;
        document.getElementById('avatarPreview').src = user.avatar;
        
        // Update usage display
        const usagePercent = (user.videosGenerated / user.videoLimit) * 100;
        document.getElementById('sidebarUsageCount').textContent = `${user.videosGenerated}/${user.videoLimit}`;
        document.getElementById('sidebarUsageProgress').style.width = `${usagePercent}%`;
        
        // Populate profile form
        document.getElementById('fullName').value = user.name;
        document.getElementById('email').value = user.email;
        
        // Update billing info
        document.getElementById('currentPlanName').textContent = `${user.plan} Plan`;
        document.getElementById('currentPlanPrice').textContent = getPlanPrice(user.plan);
        
        // Update usage stats
        document.getElementById('videosUsed').textContent = user.videosGenerated;
        document.getElementById('videosLimit').textContent = user.videoLimit;
        const videoUsagePercent = (user.videosGenerated / user.videoLimit) * 100;
        document.getElementById('videoProgress').style.width = `${videoUsagePercent}%`;
        
        // Mock script and API usage
        const scriptsUsed = Math.floor(Math.random() * 10);
        const scriptsLimit = 10;
        document.getElementById('scriptsUsed').textContent = scriptsUsed;
        document.getElementById('scriptsLimit').textContent = scriptsLimit;
        document.getElementById('scriptProgress').style.width = `${(scriptsUsed / scriptsLimit) * 100}%`;
        
        const apiCalls = Math.floor(Math.random() * 100);
        const apiLimit = 100;
        document.getElementById('apiCalls').textContent = apiCalls;
        document.getElementById('apiLimit').textContent = apiLimit;
        document.getElementById('apiProgress').style.width = `${(apiCalls / apiLimit) * 100}%`;
    }
}

// Get plan price
function getPlanPrice(plan) {
    const prices = {
        'Free': '$0/month',
        'Pro': '$29/month',
        'Enterprise': '$199/month'
    };
    return prices[plan] || '$0/month';
}

// Setup event listeners
function setupEventListeners() {
    // Tab switching
    const tabs = document.querySelectorAll('.settings-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Profile form
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
    document.getElementById('uploadAvatarBtn').addEventListener('click', handleAvatarUpload);
    document.getElementById('removeAvatarBtn').addEventListener('click', handleAvatarRemove);
    
    // Password form
    document.getElementById('passwordForm').addEventListener('submit', handlePasswordChange);
    
    // Delete account
    document.getElementById('deleteAccountBtn').addEventListener('click', handleDeleteAccount);
    
    // Generate API key
    document.getElementById('generateApiKeyBtn').addEventListener('click', handleGenerateApiKey);
    
    // User dropdown
    document.getElementById('userMenuBtn').addEventListener('click', () => {
        document.getElementById('userDropdown').classList.toggle('show');
    });
    
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        if (confirm('Are you sure you want to logout?')) {
            window.auth.logout();
            window.location.href = 'login.html';
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-menu')) {
            document.getElementById('userDropdown').classList.remove('show');
        }
    });
}

// Switch tabs
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update panels
    document.querySelectorAll('.settings-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`${tabName}-panel`).classList.add('active');
}

// Load settings data
function loadSettingsData() {
    // Load API keys
    loadApiKeys();
}

// Load API keys
function loadApiKeys() {
    const user = window.auth.getCurrentUser();
    const apiKeysList = document.getElementById('apiKeysList');
    
    if (user && user.apiKey) {
        apiKeysList.innerHTML = `
            <div class="api-key-item">
                <div class="api-key-info">
                    <h4>Production API Key</h4>
                    <p>Created on ${new Date().toLocaleDateString()}</p>
                    <div class="api-key-value">
                        <code class="api-key-text">${maskApiKey(user.apiKey)}</code>
                        <button class="icon-btn" onclick="copyApiKey('${user.apiKey}')" title="Copy">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <rect x="9" y="9" width="13" height="13" rx="2" stroke-width="2"/>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/>
                            </svg>
                        </button>
                        <button class="icon-btn" onclick="showApiKey('${user.apiKey}')" title="Show">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
                                <circle cx="12" cy="12" r="3" stroke-width="2"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="api-key-actions">
                    <button class="btn btn-ghost btn-sm" onclick="revokeApiKey()">Revoke</button>
                </div>
            </div>
        `;
    } else {
        apiKeysList.innerHTML = '<p class="text-muted">No API keys yet. Generate one to get started.</p>';
    }
}

// Mask API key
function maskApiKey(key) {
    if (!key) return '';
    return key.substring(0, 8) + '••••••••••••••••' + key.substring(key.length - 4);
}

// Copy API key
function copyApiKey(key) {
    navigator.clipboard.writeText(key).then(() => {
        showSuccess('API key copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showError('Failed to copy API key');
    });
}

// Show API key
function showApiKey(key) {
    alert(`Your API Key:\n\n${key}\n\nKeep this secret and never share it publicly!`);
}

// Revoke API key
function revokeApiKey() {
    if (confirm('Are you sure you want to revoke this API key? Applications using this key will stop working.')) {
        const user = window.auth.getCurrentUser();
        user.apiKey = null;
        localStorage.setItem('aisf_user', JSON.stringify(user));
        loadApiKeys();
        showSuccess('API key revoked successfully');
    }
}

// Handle profile update
function handleProfileUpdate(e) {
    e.preventDefault();
    
    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const company = document.getElementById('company').value;
    const phone = document.getElementById('phone').value;
    const bio = document.getElementById('bio').value;
    
    // Update user data
    const user = window.auth.getCurrentUser();
    user.name = fullName;
    user.email = email;
    user.company = company;
    user.phone = phone;
    user.bio = bio;
    
    localStorage.setItem('aisf_user', JSON.stringify(user));
    
    // Update UI
    document.getElementById('dropdownName').textContent = fullName;
    document.getElementById('dropdownEmail').textContent = email;
    
    showSuccess('Profile updated successfully!');
}

// Handle avatar upload
function handleAvatarUpload() {
    // In a real app, this would open a file picker
    // For now, just generate a new random avatar
    const seed = Math.random().toString(36).substring(7);
    const newAvatar = `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}`;
    
    document.getElementById('avatarPreview').src = newAvatar;
    document.getElementById('headerAvatar').src = newAvatar;
    document.getElementById('dropdownAvatar').src = newAvatar;
    
    const user = window.auth.getCurrentUser();
    user.avatar = newAvatar;
    localStorage.setItem('aisf_user', JSON.stringify(user));
    
    showSuccess('Avatar updated successfully!');
}

// Handle avatar remove
function handleAvatarRemove() {
    const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default';
    
    document.getElementById('avatarPreview').src = defaultAvatar;
    document.getElementById('headerAvatar').src = defaultAvatar;
    document.getElementById('dropdownAvatar').src = defaultAvatar;
    
    const user = window.auth.getCurrentUser();
    user.avatar = defaultAvatar;
    localStorage.setItem('aisf_user', JSON.stringify(user));
    
    showSuccess('Avatar removed');
}

// Handle password change
function handlePasswordChange(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
        showError('Please fill in all password fields');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showError('New passwords do not match');
        return;
    }
    
    if (newPassword.length < 8) {
        showError('Password must be at least 8 characters long');
        return;
    }
    
    // In a real app, verify current password with backend
    // For now, just update it
    showSuccess('Password updated successfully!');
    
    // Clear form
    document.getElementById('passwordForm').reset();
}

// Handle delete account
function handleDeleteAccount() {
    const confirmed = confirm(
        'Are you sure you want to delete your account?\n\n' +
        'This action cannot be undone. All your data will be permanently deleted.'
    );
    
    if (confirmed) {
        const doubleConfirm = confirm('This is your last chance. Delete account permanently?');
        
        if (doubleConfirm) {
            // In a real app, call API to delete account
            // For now, just logout and clear data
            window.auth.logout();
            showSuccess('Account deleted. Redirecting...');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }
    }
}

// Handle generate API key
function handleGenerateApiKey() {
    const user = window.auth.getCurrentUser();
    
    if (user.apiKey) {
        const confirmed = confirm('You already have an API key. Generating a new one will revoke the old one. Continue?');
        if (!confirmed) return;
    }
    
    // Generate new API key
    const newApiKey = window.auth.generateApiKey();
    user.apiKey = newApiKey;
    localStorage.setItem('aisf_user', JSON.stringify(user));
    
    loadApiKeys();
    showSuccess('New API key generated successfully!');
}

// Mobile menu
function setupMobileMenu() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const menuClose = document.getElementById('mobileMenuClose');
    const sidebar = document.getElementById('sidebar');
    
    menuBtn.addEventListener('click', () => {
        sidebar.classList.add('active');
    });
    
    menuClose.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });
}

// Notifications
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 3000);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSettings);
} else {
    initSettings();
}
