// API Client
// ============================================
// Handles all API calls to the backend

const API_BASE_URL = 'http://localhost:8000/api/v1';
const API_KEY = 'your-api-key-here-change-in-production'; // Default API key (must match backend config)

class APIClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.apiKey = this.getApiKey();
        console.log('API Client initialized with key:', this.apiKey ? '✓ Present' : '✗ Missing');
    }
    
    getApiKey() {
        // Always use the default API key for now
        console.log('Using API key:', API_KEY);
        return API_KEY;
    }
    
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey
        };
        console.log('Request headers:', headers);
        return headers;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            
            // Provide more helpful error messages
            if (error.message === 'Failed to fetch') {
                throw new Error('Cannot connect to backend server. Make sure the backend is running at http://localhost:8000 and you are accessing the frontend via http://localhost:3000 (not file://)');
            }
            
            throw error;
        }
    }
    
    // Video endpoints
    async generateVideo(prompt, options = {}) {
        const body = {
            prompt,
            num_frames: options.numFrames || 16,
            height: options.height || 256,
            width: options.width || 256
        };
        
        return this.request('/video/generate', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }
    
    async getVideoStatus(videoId) {
        return this.request(`/video/${videoId}/status`);
    }
    
    // Script endpoints
    async generateScript(topic, platform = 'instagram', variants = 3) {
        const body = {
            topic: topic,
            platform: platform,
            num_variants: variants,
            target_duration: 30
        };
        
        return this.request('/content/generate-script', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }
    
    // Caption endpoints
    async generateCaption(script, platform = 'instagram', includeHashtags = true) {
        const body = {
            script: script,
            platform: platform,
            include_hashtags: includeHashtags,
            max_length: null
        };
        
        return this.request('/content/generate-caption', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }
    
    // Workflow endpoints
    async executeWorkflow(topic, platform = 'instagram', includeVideo = true, requireApproval = true) {
        return this.request('/workflow/execute-direct', {
            method: 'POST',
            body: JSON.stringify({
                topic,
                platform,
                include_video: includeVideo,
                require_approval: requireApproval
            })
        });
    }
    
    async getWorkflowStatus(workflowId) {
        return this.request(`/workflow/${workflowId}/status`);
    }
    
    // Analytics endpoints
    async getAnalytics() {
        return this.request('/analytics/summary');
    }
    
    async getRecentActivity(limit = 10) {
        return this.request(`/analytics/recent?limit=${limit}`);
    }
}

// Create singleton instance
const api = new APIClient();

// Export for use in other scripts
window.api = api;
