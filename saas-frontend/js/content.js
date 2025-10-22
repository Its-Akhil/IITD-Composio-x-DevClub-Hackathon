// Content Library JavaScript

// State management
let currentView = 'grid';
let currentFilters = {
    type: 'all',
    platform: 'all',
    sort: 'recent'
};
let currentPage = 1;
const itemsPerPage = 12;
let allContent = [];
let currentContentId = null;

// Initialize content library
function initContent() {
    // Check authentication
    if (!window.auth.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }

    // Load user info
    loadUserInfo();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load content
    loadContent();
    
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
        
        // Update usage display
        const usagePercent = (user.videosGenerated / user.videoLimit) * 100;
        document.getElementById('sidebarUsageCount').textContent = `${user.videosGenerated}/${user.videoLimit}`;
        document.getElementById('sidebarUsageProgress').style.width = `${usagePercent}%`;
    }
}

// Setup event listeners
function setupEventListeners() {
    // View toggle
    document.getElementById('gridViewBtn').addEventListener('click', () => setView('grid'));
    document.getElementById('listViewBtn').addEventListener('click', () => setView('list'));
    
    // Filters
    document.getElementById('filterType').addEventListener('change', (e) => {
        currentFilters.type = e.target.value;
        currentPage = 1;
        filterContent();
    });
    
    document.getElementById('filterPlatform').addEventListener('change', (e) => {
        currentFilters.platform = e.target.value;
        currentPage = 1;
        filterContent();
    });
    
    document.getElementById('filterSort').addEventListener('change', (e) => {
        currentFilters.sort = e.target.value;
        currentPage = 1;
        filterContent();
    });
    
    // Search
    document.getElementById('searchInput').addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        if (query) {
            const filtered = allContent.filter(item => 
                item.title.toLowerCase().includes(query) ||
                (item.description && item.description.toLowerCase().includes(query))
            );
            displayContent(filtered);
        } else {
            filterContent();
        }
    });
    
    // Pagination
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            filterContent();
        }
    });
    
    document.getElementById('nextBtn').addEventListener('click', () => {
        const totalPages = Math.ceil(getFilteredContent().length / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            filterContent();
        }
    });
    
    // Modals
    document.getElementById('modalClose').addEventListener('click', closeContentModal);
    document.getElementById('modalOverlay').addEventListener('click', closeContentModal);
    document.getElementById('deleteModalClose').addEventListener('click', closeDeleteModal);
    document.getElementById('deleteOverlay').addEventListener('click', closeDeleteModal);
    document.getElementById('cancelDelete').addEventListener('click', closeDeleteModal);
    document.getElementById('confirmDelete').addEventListener('click', confirmDelete);
    
    // Modal actions
    document.getElementById('modalDownload').addEventListener('click', downloadContent);
    document.getElementById('modalCopy').addEventListener('click', copyContent);
    
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

// Load content from backend or mock data
async function loadContent() {
    try {
        // Try to load from backend
        // const response = await window.api.getContent();
        // allContent = response.content;
        
        // For now, use mock data
        allContent = generateMockContent();
        
        // Initial display
        filterContent();
        updateStats();
        
    } catch (error) {
        console.error('Error loading content:', error);
        // Use mock data on error
        allContent = generateMockContent();
        filterContent();
        updateStats();
    }
}

// Generate mock content
function generateMockContent() {
    const types = ['video', 'script', 'caption', 'workflow'];
    const platforms = ['instagram', 'tiktok', 'youtube', 'twitter'];
    const mockContent = [];
    
    for (let i = 1; i <= 24; i++) {
        const type = types[Math.floor(Math.random() * types.length)];
        const platform = platforms[Math.floor(Math.random() * platforms.length)];
        
        mockContent.push({
            id: i,
            type: type,
            title: `${type.charAt(0).toUpperCase() + type.slice(1)} ${i}`,
            description: `Sample ${type} content for ${platform}`,
            platform: platform,
            thumbnail: type === 'video' ? `https://picsum.photos/seed/${i}/400/300` : null,
            views: Math.floor(Math.random() * 10000),
            engagement: Math.floor(Math.random() * 100) + '%',
            createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
            content: type === 'script' ? `This is a sample script for ${platform}...` : 
                     type === 'caption' ? `This is a sample caption for ${platform} #hashtag` : null,
            hashtags: type === 'caption' ? ['#viral', '#trending', '#content', '#ai'] : null,
            videoUrl: type === 'video' ? `https://example.com/video${i}.mp4` : null
        });
    }
    
    return mockContent;
}

// Filter content
function getFilteredContent() {
    let filtered = [...allContent];
    
    // Filter by type
    if (currentFilters.type !== 'all') {
        filtered = filtered.filter(item => item.type === currentFilters.type);
    }
    
    // Filter by platform
    if (currentFilters.platform !== 'all') {
        filtered = filtered.filter(item => item.platform === currentFilters.platform);
    }
    
    // Sort
    switch (currentFilters.sort) {
        case 'recent':
            filtered.sort((a, b) => b.createdAt - a.createdAt);
            break;
        case 'oldest':
            filtered.sort((a, b) => a.createdAt - b.createdAt);
            break;
        case 'name':
            filtered.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'views':
            filtered.sort((a, b) => b.views - a.views);
            break;
    }
    
    return filtered;
}

function filterContent() {
    const filtered = getFilteredContent();
    displayContent(filtered);
}

// Display content
function displayContent(content) {
    const grid = document.getElementById('contentGrid');
    const emptyState = document.getElementById('emptyState');
    const pagination = document.getElementById('pagination');
    
    // Pagination
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedContent = content.slice(startIndex, endIndex);
    
    if (paginatedContent.length === 0) {
        grid.innerHTML = '';
        emptyState.style.display = 'flex';
        pagination.style.display = 'none';
        return;
    }
    
    emptyState.style.display = 'none';
    
    grid.innerHTML = paginatedContent.map(item => `
        <div class="content-item" onclick="openContentModal(${item.id})">
            <div class="content-thumbnail">
                ${item.thumbnail ? 
                    `<img src="${item.thumbnail}" alt="${item.title}">` :
                    `<div class="content-thumbnail-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            ${getTypeIcon(item.type)}
                        </svg>
                        <span>${item.type}</span>
                    </div>`
                }
                <div class="content-type-badge">${item.type}</div>
            </div>
            <div class="content-info">
                <h3 class="content-title">${item.title}</h3>
                <div class="content-meta">
                    <div class="content-meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <rect x="3" y="4" width="18" height="18" rx="2" stroke-width="2"/>
                            <path d="M16 2v4M8 2v4M3 10h18" stroke-width="2"/>
                        </svg>
                        ${formatDate(item.createdAt)}
                    </div>
                    <div class="content-meta-item">
                        <span class="platform-badge">${item.platform}</span>
                    </div>
                </div>
                <div class="content-stats">
                    <div class="content-stat">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
                            <circle cx="12" cy="12" r="3" stroke-width="2"/>
                        </svg>
                        ${item.views.toLocaleString()}
                    </div>
                    <div class="content-stat">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke-width="2"/>
                        </svg>
                        ${item.engagement}
                    </div>
                </div>
            </div>
            <div class="content-actions" onclick="event.stopPropagation()">
                <button class="content-action-btn" onclick="viewContent(${item.id})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
                        <circle cx="12" cy="12" r="3" stroke-width="2"/>
                    </svg>
                    View
                </button>
                <button class="content-action-btn" onclick="downloadContentById(${item.id})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    Download
                </button>
                <button class="content-action-btn delete" onclick="openDeleteModal(${item.id})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    Delete
                </button>
            </div>
        </div>
    `).join('');
    
    // Update pagination
    const totalPages = Math.ceil(content.length / itemsPerPage);
    document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('prevBtn').disabled = currentPage === 1;
    document.getElementById('nextBtn').disabled = currentPage === totalPages;
    pagination.style.display = totalPages > 1 ? 'flex' : 'none';
}

// Update stats
function updateStats() {
    const videos = allContent.filter(item => item.type === 'video').length;
    const scripts = allContent.filter(item => item.type === 'script').length;
    const captions = allContent.filter(item => item.type === 'caption').length;
    const storage = (allContent.length * 2.5).toFixed(1); // Mock storage calculation
    
    document.getElementById('totalItems').textContent = allContent.length;
    document.getElementById('totalVideos').textContent = videos;
    document.getElementById('totalScripts').textContent = scripts;
    document.getElementById('totalCaptions').textContent = captions;
    document.getElementById('storageUsed').textContent = `${storage} MB`;
}

// Set view
function setView(view) {
    currentView = view;
    const grid = document.getElementById('contentGrid');
    const gridBtn = document.getElementById('gridViewBtn');
    const listBtn = document.getElementById('listViewBtn');
    
    if (view === 'grid') {
        grid.classList.remove('list-view');
        gridBtn.classList.add('active');
        listBtn.classList.remove('active');
    } else {
        grid.classList.add('list-view');
        listBtn.classList.add('active');
        gridBtn.classList.remove('active');
    }
}

// Open content modal
function openContentModal(id) {
    const item = allContent.find(c => c.id === id);
    if (!item) return;
    
    currentContentId = id;
    const modal = document.getElementById('contentModal');
    const modalBody = document.getElementById('modalBody');
    const modalTitle = document.getElementById('modalTitle');
    
    modalTitle.textContent = item.title;
    
    let bodyHTML = '';
    
    if (item.type === 'video') {
        bodyHTML = `
            <video class="modal-video" controls>
                <source src="${item.videoUrl}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="modal-detail-section">
                <h4>Description</h4>
                <p>${item.description}</p>
            </div>
            <div class="modal-detail-section">
                <h4>Stats</h4>
                <p>Views: ${item.views.toLocaleString()} | Engagement: ${item.engagement}</p>
            </div>
        `;
    } else if (item.type === 'script') {
        bodyHTML = `
            <div class="modal-detail-section">
                <h4>Script Content</h4>
                <p>${item.content}</p>
            </div>
            <div class="modal-detail-section">
                <h4>Platform</h4>
                <p>${item.platform}</p>
            </div>
        `;
    } else if (item.type === 'caption') {
        bodyHTML = `
            <div class="modal-detail-section">
                <h4>Caption</h4>
                <p>${item.content}</p>
            </div>
            <div class="modal-detail-section">
                <h4>Hashtags</h4>
                <div class="modal-hashtags">
                    ${item.hashtags.map(tag => `<span class="modal-hashtag">${tag}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    modalBody.innerHTML = bodyHTML;
    modal.classList.add('active');
}

function closeContentModal() {
    document.getElementById('contentModal').classList.remove('active');
    currentContentId = null;
}

// Delete modal
function openDeleteModal(id) {
    currentContentId = id;
    document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('active');
    currentContentId = null;
}

async function confirmDelete() {
    if (!currentContentId) return;
    
    try {
        // Call backend API
        // await window.api.deleteContent(currentContentId);
        
        // Remove from local array
        allContent = allContent.filter(item => item.id !== currentContentId);
        
        // Refresh display
        filterContent();
        updateStats();
        
        closeDeleteModal();
        showSuccess('Content deleted successfully');
    } catch (error) {
        console.error('Error deleting content:', error);
        showError('Failed to delete content');
    }
}

// Download content
function downloadContentById(id) {
    const item = allContent.find(c => c.id === id);
    if (!item) return;
    
    downloadContent(item);
}

function downloadContent(item = null) {
    if (!item && currentContentId) {
        item = allContent.find(c => c.id === currentContentId);
    }
    
    if (!item) return;
    
    // Create download based on type
    if (item.type === 'video' && item.videoUrl) {
        window.open(item.videoUrl, '_blank');
    } else if (item.type === 'script' || item.type === 'caption') {
        const blob = new Blob([item.content || ''], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${item.title}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    showSuccess('Download started');
}

// Copy content
function copyContent() {
    if (!currentContentId) return;
    
    const item = allContent.find(c => c.id === currentContentId);
    if (!item) return;
    
    const textToCopy = item.content || item.title;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        showSuccess('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showError('Failed to copy content');
    });
}

// View content (same as opening modal)
function viewContent(id) {
    openContentModal(id);
}

// Helper functions
function getTypeIcon(type) {
    const icons = {
        video: '<rect x="2" y="2" width="20" height="20" rx="2.18" stroke-width="2"/><path d="m7 2 5 10-5 10" stroke-width="2"/>',
        script: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke-width="2"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke-width="2"/>',
        caption: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke-width="2"/>',
        workflow: '<rect x="3" y="3" width="7" height="7" stroke-width="2"/><rect x="14" y="3" width="7" height="7" stroke-width="2"/><rect x="14" y="14" width="7" height="7" stroke-width="2"/><rect x="3" y="14" width="7" height="7" stroke-width="2"/>'
    };
    return icons[type] || icons.video;
}

function formatDate(date) {
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    return date.toLocaleDateString();
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
    document.addEventListener('DOMContentLoaded', initContent);
} else {
    initContent();
}
