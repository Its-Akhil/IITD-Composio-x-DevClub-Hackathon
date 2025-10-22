// Dashboard JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!window.auth.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }
    
    initDashboard();
});

async function initDashboard() {
    // Load user info
    loadUserInfo();
    
    // Load dashboard data
    await loadDashboardData();
    
    // Initialize event listeners
    initEventListeners();
    
    // Load recent activity
    loadRecentActivity();
}

function loadUserInfo() {
    const user = window.auth.getCurrentUser();
    
    if (user) {
        // Update user name in header
        const userNameEl = document.getElementById('userName');
        if (userNameEl) {
            userNameEl.textContent = user.fullName || user.email;
        }
        
        // Update avatar initials
        const userAvatarEl = document.getElementById('userAvatar');
        if (userAvatarEl && user.fullName) {
            const initials = user.fullName
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase()
                .slice(0, 2);
            userAvatarEl.textContent = initials;
        }
        
        // Update plan badge
        const planBadgeEl = document.getElementById('userPlanBadge');
        if (planBadgeEl && user.plan) {
            const planNames = {
                free: 'Free Plan',
                pro: 'Pro Plan',
                enterprise: 'Enterprise'
            };
            planBadgeEl.textContent = planNames[user.plan] || 'Free Plan';
        }
        
        // Update usage
        updateUsageDisplay(user);
    }
}

function updateUsageDisplay(user) {
    const plan = user.plan || 'free';
    const limits = {
        free: 5,
        pro: 50,
        enterprise: 999999
    };
    
    const videosGenerated = user.videosGenerated || 0;
    const limit = limits[plan];
    
    const usageCountEl = document.getElementById('usageCount');
    const usageLimitEl = document.getElementById('usageLimit');
    const usageBarEl = document.getElementById('usageBar');
    
    if (usageCountEl) usageCountEl.textContent = videosGenerated;
    if (usageLimitEl) usageLimitEl.textContent = limit === 999999 ? '∞' : limit;
    
    if (usageBarEl) {
        const percentage = limit === 999999 ? 0 : (videosGenerated / limit) * 100;
        usageBarEl.style.width = `${Math.min(percentage, 100)}%`;
    }
}

async function loadDashboardData() {
    try {
        // Try to load analytics from backend
        const analytics = await window.api.getAnalytics().catch(() => null);
        
        if (analytics) {
            updateStats(analytics);
        } else {
            // Use mock data from user object
            const user = window.auth.getCurrentUser();
            updateStats({
                total_videos: user.videosGenerated || 0,
                total_scripts: user.scriptsGenerated || 0,
                api_calls: (user.videosGenerated || 0) + (user.scriptsGenerated || 0),
                storage_mb: Math.round((user.videosGenerated || 0) * 12.4)
            });
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        // Show mock data
        updateStats({
            total_videos: 0,
            total_scripts: 0,
            api_calls: 0,
            storage_mb: 0
        });
    }
}

function updateStats(data) {
    const totalVideosEl = document.getElementById('totalVideos');
    const totalScriptsEl = document.getElementById('totalScripts');
    const totalApiCallsEl = document.getElementById('totalApiCalls');
    
    if (totalVideosEl) {
        animateNumber(totalVideosEl, data.total_videos || 0);
    }
    
    if (totalScriptsEl) {
        animateNumber(totalScriptsEl, data.total_scripts || 0);
    }
    
    if (totalApiCallsEl) {
        animateNumber(totalApiCallsEl, data.api_calls || 0);
    }
}

function animateNumber(element, targetNumber, duration = 1000) {
    const start = parseInt(element.textContent) || 0;
    const increment = (targetNumber - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= targetNumber) || (increment < 0 && current <= targetNumber)) {
            element.textContent = targetNumber;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

async function loadRecentActivity() {
    const activityListEl = document.getElementById('activityList');
    
    if (!activityListEl) return;
    
    try {
        // Try to load from backend
        const activities = await window.api.getRecentActivity(10).catch(() => null);
        
        if (activities && activities.length > 0) {
            displayActivities(activities);
        } else {
            // Check if user has generated any content
            const user = window.auth.getCurrentUser();
            if ((user.videosGenerated || 0) > 0 || (user.scriptsGenerated || 0) > 0) {
                // Show mock activity
                displayMockActivities();
            }
            // Otherwise, keep empty state
        }
    } catch (error) {
        console.error('Failed to load recent activity:', error);
    }
}

function displayActivities(activities) {
    const activityListEl = document.getElementById('activityList');
    
    activityListEl.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon">
                ${getActivityIcon(activity.type)}
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-time">${formatTime(activity.created_at)}</div>
            </div>
            <div class="activity-status">
                ${getStatusBadge(activity.status)}
            </div>
        </div>
    `).join('');
}

function displayMockActivities() {
    const activityListEl = document.getElementById('activityList');
    const user = window.auth.getCurrentUser();
    
    const mockActivities = [];
    
    if (user.videosGenerated > 0) {
        mockActivities.push({
            type: 'video',
            title: 'Generated AI video',
            created_at: new Date(Date.now() - 3600000).toISOString(),
            status: 'completed'
        });
    }
    
    if (user.scriptsGenerated > 0) {
        mockActivities.push({
            type: 'script',
            title: 'Created script',
            created_at: new Date(Date.now() - 7200000).toISOString(),
            status: 'completed'
        });
    }
    
    if (mockActivities.length > 0) {
        displayActivities(mockActivities);
    }
}

function getActivityIcon(type) {
    const icons = {
        video: '<svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>',
        script: '<svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>',
        caption: '<svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/></svg>',
        workflow: '<svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>'
    };
    return icons[type] || icons.video;
}

function getStatusBadge(status) {
    const badges = {
        completed: '<span class="badge badge-success">Completed</span>',
        processing: '<span class="badge badge-warning">Processing</span>',
        failed: '<span class="badge badge-error">Failed</span>'
    };
    return badges[status] || badges.completed;
}

function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
}

function initEventListeners() {
    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
        });
    }
    
    // Profile dropdown
    const profileDropdown = document.getElementById('profileDropdown');
    if (profileDropdown) {
        profileDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                window.auth.logout();
            }
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
        const profileMenu = document.getElementById('profileMenu');
        if (profileMenu) {
            profileMenu.style.opacity = '0';
            profileMenu.style.visibility = 'hidden';
        }
    });
}

// Export for use in other scripts
window.dashboard = {
    loadDashboardData,
    loadRecentActivity,
    updateUsageDisplay
};
