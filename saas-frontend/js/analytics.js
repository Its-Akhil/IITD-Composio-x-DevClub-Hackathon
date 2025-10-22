// Analytics Page JavaScript

// Chart instances
let performanceChart = null;
let platformChart = null;
let contentTypeChart = null;

// State
let currentDateRange = 30;
let analyticsData = null;

// Initialize analytics page
function initAnalytics() {
    // Check authentication
    if (!window.auth.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }

    // Load user info
    loadUserInfo();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load analytics data
    loadAnalyticsData();
    
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
    // Date range selector
    document.getElementById('dateRangeSelect').addEventListener('change', (e) => {
        currentDateRange = e.target.value === 'all' ? 365 : parseInt(e.target.value);
        loadAnalyticsData();
    });
    
    // Export button
    document.getElementById('exportBtn').addEventListener('click', exportReport);
    
    // Top content metric selector
    document.getElementById('topContentMetric').addEventListener('change', () => {
        updateTopContentTable();
    });
    
    // Chart legend toggles
    document.getElementById('toggleViews').addEventListener('change', (e) => {
        toggleChartDataset(performanceChart, 0, e.target.checked);
    });
    
    document.getElementById('toggleEngagement').addEventListener('change', (e) => {
        toggleChartDataset(performanceChart, 1, e.target.checked);
    });
    
    document.getElementById('toggleReach').addEventListener('change', (e) => {
        toggleChartDataset(performanceChart, 2, e.target.checked);
    });
    
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

// Load analytics data
async function loadAnalyticsData() {
    try {
        // Try to load from backend
        // const data = await window.api.getAnalytics(currentDateRange);
        // analyticsData = data;
        
        // For now, use mock data
        analyticsData = generateMockAnalytics();
        
        // Update UI
        updateOverviewCards();
        initializeCharts();
        updateTopContentTable();
        generateInsights();
        
    } catch (error) {
        console.error('Error loading analytics:', error);
        analyticsData = generateMockAnalytics();
        updateOverviewCards();
        initializeCharts();
        updateTopContentTable();
        generateInsights();
    }
}

// Generate mock analytics data
function generateMockAnalytics() {
    const days = currentDateRange === 365 ? 30 : currentDateRange;
    const labels = [];
    const views = [];
    const engagement = [];
    const reach = [];
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        views.push(Math.floor(Math.random() * 5000) + 1000);
        engagement.push(Math.floor(Math.random() * 3000) + 500);
        reach.push(Math.floor(Math.random() * 8000) + 2000);
    }
    
    return {
        overview: {
            totalViews: 45678,
            viewsTrend: 12,
            engagementRate: 6.8,
            engagementTrend: 8,
            totalReach: 125430,
            reachTrend: 15,
            conversionRate: 2.4,
            conversionTrend: -3
        },
        timeline: {
            labels,
            views,
            engagement,
            reach
        },
        platforms: {
            instagram: 18500,
            tiktok: 15200,
            youtube: 8900,
            twitter: 3078
        },
        contentTypes: {
            videos: 42,
            scripts: 78,
            captions: 135,
            workflows: 23
        },
        topContent: [
            { id: 1, title: 'Summer Product Launch', type: 'video', platform: 'Instagram', views: 12500, engagement: '8.5%', date: '2024-10-15' },
            { id: 2, title: 'Behind the Scenes', type: 'video', platform: 'TikTok', views: 9800, engagement: '7.2%', date: '2024-10-18' },
            { id: 3, title: 'Tutorial Series Ep 1', type: 'video', platform: 'YouTube', views: 8200, engagement: '6.9%', date: '2024-10-12' },
            { id: 4, title: 'Quick Tips Script', type: 'script', platform: 'Twitter', views: 5600, engagement: '5.4%', date: '2024-10-20' },
            { id: 5, title: 'Motivational Caption', type: 'caption', platform: 'Instagram', views: 4200, engagement: '9.1%', date: '2024-10-19' }
        ]
    };
}

// Update overview cards
function updateOverviewCards() {
    const { overview } = analyticsData;
    
    document.getElementById('totalViews').textContent = formatNumber(overview.totalViews);
    document.getElementById('viewsTrend').textContent = `${overview.viewsTrend > 0 ? '+' : ''}${overview.viewsTrend}%`;
    document.getElementById('viewsTrend').className = `analytics-card-trend ${overview.viewsTrend >= 0 ? 'positive' : 'negative'}`;
    
    document.getElementById('engagementRate').textContent = `${overview.engagementRate}%`;
    document.getElementById('engagementTrend').textContent = `${overview.engagementTrend > 0 ? '+' : ''}${overview.engagementTrend}%`;
    document.getElementById('engagementTrend').className = `analytics-card-trend ${overview.engagementTrend >= 0 ? 'positive' : 'negative'}`;
    
    document.getElementById('totalReach').textContent = formatNumber(overview.totalReach);
    document.getElementById('reachTrend').textContent = `${overview.reachTrend > 0 ? '+' : ''}${overview.reachTrend}%`;
    document.getElementById('reachTrend').className = `analytics-card-trend ${overview.reachTrend >= 0 ? 'positive' : 'negative'}`;
    
    document.getElementById('conversionRate').textContent = `${overview.conversionRate}%`;
    document.getElementById('conversionTrend').textContent = `${overview.conversionTrend > 0 ? '+' : ''}${overview.conversionTrend}%`;
    document.getElementById('conversionTrend').className = `analytics-card-trend ${overview.conversionTrend >= 0 ? 'positive' : 'negative'}`;
}

// Initialize charts
function initializeCharts() {
    createPerformanceChart();
    createPlatformChart();
    createContentTypeChart();
}

// Create performance over time chart
function createPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    if (performanceChart) {
        performanceChart.destroy();
    }
    
    const { timeline } = analyticsData;
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeline.labels,
            datasets: [
                {
                    label: 'Views',
                    data: timeline.views,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Engagement',
                    data: timeline.engagement,
                    borderColor: '#f093fb',
                    backgroundColor: 'rgba(240, 147, 251, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Reach',
                    data: timeline.reach,
                    borderColor: '#4facfe',
                    backgroundColor: 'rgba(79, 172, 254, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Create platform breakdown chart
function createPlatformChart() {
    const ctx = document.getElementById('platformChart');
    if (!ctx) return;
    
    if (platformChart) {
        platformChart.destroy();
    }
    
    const { platforms } = analyticsData;
    
    platformChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Instagram', 'TikTok', 'YouTube', 'Twitter'],
            datasets: [{
                data: [platforms.instagram, platforms.tiktok, platforms.youtube, platforms.twitter],
                backgroundColor: [
                    '#667eea',
                    '#f093fb',
                    '#4facfe',
                    '#fa709a'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${formatNumber(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Update platform stats
    document.getElementById('instagramViews').textContent = formatNumber(platforms.instagram);
    document.getElementById('tiktokViews').textContent = formatNumber(platforms.tiktok);
    document.getElementById('youtubeViews').textContent = formatNumber(platforms.youtube);
    document.getElementById('twitterViews').textContent = formatNumber(platforms.twitter);
}

// Create content type chart
function createContentTypeChart() {
    const ctx = document.getElementById('contentTypeChart');
    if (!ctx) return;
    
    if (contentTypeChart) {
        contentTypeChart.destroy();
    }
    
    const { contentTypes } = analyticsData;
    
    contentTypeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Videos', 'Scripts', 'Captions', 'Workflows'],
            datasets: [{
                data: [contentTypes.videos, contentTypes.scripts, contentTypes.captions, contentTypes.workflows],
                backgroundColor: [
                    '#667eea',
                    '#f093fb',
                    '#4facfe',
                    '#fa709a'
                ],
                borderRadius: 8,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Toggle chart dataset visibility
function toggleChartDataset(chart, index, visible) {
    if (chart) {
        chart.data.datasets[index].hidden = !visible;
        chart.update();
    }
}

// Update top content table
function updateTopContentTable() {
    const metric = document.getElementById('topContentMetric').value;
    const tbody = document.getElementById('topContentBody');
    const emptyState = document.getElementById('tableEmptyState');
    
    if (!analyticsData || !analyticsData.topContent || analyticsData.topContent.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    // Sort content based on selected metric
    let sortedContent = [...analyticsData.topContent];
    if (metric === 'engagement') {
        sortedContent.sort((a, b) => parseFloat(b.engagement) - parseFloat(a.engagement));
    } else if (metric === 'reach') {
        sortedContent.sort((a, b) => b.views - a.views); // Using views as proxy for reach
    }
    
    tbody.innerHTML = sortedContent.map(item => `
        <tr>
            <td>
                <div class="content-name">
                    <div class="content-thumbnail-small"></div>
                    <span class="content-name-text">${item.title}</span>
                </div>
            </td>
            <td><span class="type-badge ${item.type}">${item.type}</span></td>
            <td><span class="platform-badge">${item.platform}</span></td>
            <td>${formatNumber(item.views)}</td>
            <td><span class="engagement-value">${item.engagement}</span></td>
            <td><span class="date-text">${formatDate(item.date)}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="action-icon-btn" title="View">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
                            <circle cx="12" cy="12" r="3" stroke-width="2"/>
                        </svg>
                    </button>
                    <button class="action-icon-btn" title="Download">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke-width="2"/>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Generate AI insights
function generateInsights() {
    const insights = [
        {
            type: 'success',
            icon: '📈',
            title: 'Strong Performance',
            description: 'Your content engagement is 23% above average. Keep creating similar content to maintain this growth.',
            action: 'View Best Performing Content'
        },
        {
            type: 'info',
            icon: '⏰',
            title: 'Optimal Posting Time',
            description: 'Your audience is most active between 6-9 PM. Schedule posts during these hours for better reach.',
            action: 'Adjust Schedule'
        },
        {
            type: 'warning',
            icon: '⚠️',
            title: 'Platform Opportunity',
            description: 'Your Twitter engagement is lower than other platforms. Consider focusing more on this channel.',
            action: 'View Twitter Strategy'
        },
        {
            type: 'info',
            icon: '🎯',
            title: 'Content Mix',
            description: 'Videos are driving 68% of your engagement. Consider creating more video content for better results.',
            action: 'Create Video'
        }
    ];
    
    const insightsGrid = document.getElementById('insightsGrid');
    insightsGrid.innerHTML = insights.map(insight => `
        <div class="insight-card ${insight.type}">
            <div class="insight-header">
                <div class="insight-icon">${insight.icon}</div>
                <h4 class="insight-title">${insight.title}</h4>
            </div>
            <p class="insight-description">${insight.description}</p>
            <a href="#" class="insight-action">
                ${insight.action}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2"/>
                </svg>
            </a>
        </div>
    `).join('');
}

// Export report
function exportReport() {
    // Create CSV content
    const csv = generateCSVReport();
    
    // Create download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    showSuccess('Report exported successfully!');
}

function generateCSVReport() {
    const { overview, topContent } = analyticsData;
    
    let csv = 'AI Social Factory - Analytics Report\n\n';
    csv += 'Overview\n';
    csv += 'Metric,Value,Trend\n';
    csv += `Total Views,${overview.totalViews},${overview.viewsTrend}%\n`;
    csv += `Engagement Rate,${overview.engagementRate}%,${overview.engagementTrend}%\n`;
    csv += `Total Reach,${overview.totalReach},${overview.reachTrend}%\n`;
    csv += `Conversion Rate,${overview.conversionRate}%,${overview.conversionTrend}%\n\n`;
    
    csv += 'Top Performing Content\n';
    csv += 'Title,Type,Platform,Views,Engagement,Date\n';
    topContent.forEach(item => {
        csv += `"${item.title}",${item.type},${item.platform},${item.views},${item.engagement},${item.date}\n`;
    });
    
    return csv;
}

// Helper functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
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
    document.addEventListener('DOMContentLoaded', initAnalytics);
} else {
    initAnalytics();
}
