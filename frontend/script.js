// Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'your-api-key-here-change-in-production'; // Replace with your actual API key

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Check health every 30 seconds
    setInterval(checkHealth, 30000);
}

// Utility Functions
function showResult(stepNumber, content, type = 'info') {
    const resultDiv = document.getElementById(`result-${stepNumber}`);
    const stepCard = document.querySelector(`[data-step="${stepNumber}"]`);
    
    resultDiv.innerHTML = content;
    resultDiv.classList.add('show');
    
    if (type === 'success') {
        stepCard.classList.remove('error');
        stepCard.classList.add('success');
    } else if (type === 'error') {
        stepCard.classList.remove('success');
        stepCard.classList.add('error');
    }
}

function showLoading(stepNumber) {
    const content = `
        <div class="result-info">
            <div class="result-title">
                <div class="loading"></div>
                Processing...
            </div>
            <div class="result-content">Please wait while we process your request...</div>
        </div>
    `;
    showResult(stepNumber, content);
}

function formatJSON(obj) {
    return JSON.stringify(obj, null, 2);
}

async function apiRequest(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const data = await response.json();
    
    if (!response.ok) {
        // Handle detailed error messages from FastAPI validation errors
        let errorMessage = 'Request failed';
        
        if (data.detail) {
            if (typeof data.detail === 'string') {
                errorMessage = data.detail;
            } else if (Array.isArray(data.detail)) {
                // FastAPI validation errors are arrays
                errorMessage = data.detail.map(err => {
                    const location = err.loc ? err.loc.join(' -> ') : 'unknown';
                    return `${location}: ${err.msg}`;
                }).join('; ');
            } else if (typeof data.detail === 'object') {
                errorMessage = JSON.stringify(data.detail, null, 2);
            }
        }
        
        throw new Error(errorMessage);
    }
    
    return data;
}

// Step 1: Health Check
async function checkHealth() {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    try {
        const data = await fetch(`${API_BASE_URL}/health`).then(r => r.json());
        
        statusDot.className = 'status-dot online';
        statusText.textContent = 'Server Online';
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Server is Healthy</div>
                <div class="result-content">
                    <strong>Status:</strong> ${data.status}<br>
                    <strong>Video Service:</strong> ${data.video_service ? 'Available' : 'Not Available'}<br>
                    <strong>Model Loaded:</strong> ${data.model_loaded ? 'Yes' : 'No (will load on first use)'}
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">ℹ️ What This Means</div>
                <div class="result-content">
                    Your FastAPI backend is running successfully. All services are initialized and ready to process requests.
                </div>
            </div>
        `;
        
        showResult(1, content, 'success');
    } catch (error) {
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'Server Offline';
        
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Server Connection Failed</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    <strong>Troubleshooting:</strong>
                    <ul class="result-list">
                        <li>Make sure the backend server is running</li>
                        <li>Run: <code>uvicorn app.main:app --reload</code></li>
                        <li>Check if port 8000 is available</li>
                        <li>Verify no firewall is blocking the connection</li>
                    </ul>
                </div>
            </div>
        `;
        
        showResult(1, content, 'error');
    }
}

// Step 2: Test Gemini
async function testGemini() {
    showLoading(2);
    
    try {
        const data = await apiRequest('/api/v1/content/test');
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Gemini API Connected</div>
                <div class="result-content">
                    Successfully generated AI content using Google Gemini API.
                </div>
            </div>
            <div class="result-json">${formatJSON(data)}</div>
            <div class="result-info">
                <div class="result-title">ℹ️ Configuration Check</div>
                <div class="result-content">
                    <strong>Status:</strong> GEMINI_API_KEY is properly configured<br>
                    <strong>Model:</strong> ${data.model || 'gemini-2.0-flash-exp'}<br>
                    <strong>Check:</strong> .env file contains valid API key
                </div>
            </div>
        `;
        
        showResult(2, content, 'success');
    } catch (error) {
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Gemini API Error</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    <strong>Troubleshooting:</strong>
                    <ul class="result-list">
                        <li>Check GEMINI_API_KEY in .env file</li>
                        <li>Verify API key is valid at <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a></li>
                        <li>Ensure API key has proper permissions</li>
                        <li>Check if you've exceeded rate limits</li>
                    </ul>
                </div>
            </div>
        `;
        
        showResult(2, content, 'error');
    }
}

// Step 3: Generate Script
function showScriptForm() {
    const form = document.getElementById('form-3');
    form.style.display = form.style.display === 'none' ? 'flex' : 'none';
}

async function generateScript() {
    const topic = document.getElementById('scriptTopic').value;
    const platform = document.getElementById('scriptPlatform').value;
    const duration = parseInt(document.getElementById('scriptDuration').value);
    
    if (!topic) {
        alert('Please enter a topic');
        return;
    }
    
    showLoading(3);
    
    try {
        const data = await apiRequest('/api/v1/content/generate-script', 'POST', {
            topic,
            platform,
            target_duration: duration,
            num_variants: 3
        });
        
        const variantsHtml = data.variants.map((v, i) => `
            <div class="result-info" style="margin-top: ${i > 0 ? '12px' : '0'};">
                <div class="result-title">📝 Variant ${v.variant_id}: ${v.style}</div>
                <div class="result-content">
                    <strong>Script:</strong><br>
                    ${v.script.replace(/\n/g, '<br>')}<br><br>
                    <strong>Duration Estimate:</strong> ${v.duration_estimate} seconds
                </div>
            </div>
        `).join('');
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Generated ${data.variants.length} Script Variants</div>
                <div class="result-content">
                    <strong>Topic:</strong> ${data.topic}<br>
                    <strong>Platform:</strong> ${platform}
                </div>
            </div>
            ${variantsHtml}
            <div class="result-json">${formatJSON(data)}</div>
        `;
        
        showResult(3, content, 'success');
        document.getElementById('form-3').style.display = 'none';
    } catch (error) {
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Script Generation Failed</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    Check that the Gemini API is properly configured and has sufficient quota.
                </div>
            </div>
        `;
        
        showResult(3, content, 'error');
    }
}

// Step 4: Generate Caption
function showCaptionForm() {
    const form = document.getElementById('form-4');
    form.style.display = form.style.display === 'none' ? 'flex' : 'none';
}

async function generateCaption() {
    const script = document.getElementById('captionScript').value;
    const platform = document.getElementById('captionPlatform').value;
    
    if (!script) {
        alert('Please enter a script or description');
        return;
    }
    
    showLoading(4);
    
    try {
        const data = await apiRequest('/api/v1/content/generate-caption', 'POST', {
            script,
            platform,
            include_hashtags: true
        });
        
        const hashtagsHtml = data.hashtags.map(tag => `#${tag}`).join(' ');
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Caption Generated</div>
                <div class="result-content">
                    <strong>Platform:</strong> ${data.platform}<br>
                    <strong>Character Count:</strong> ${data.character_count}
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">📱 Generated Caption</div>
                <div class="result-content">
                    ${data.caption}<br><br>
                    <strong>Hashtags:</strong> ${hashtagsHtml}
                </div>
            </div>
            <div class="result-json">${formatJSON(data)}</div>
        `;
        
        showResult(4, content, 'success');
        document.getElementById('form-4').style.display = 'none';
    } catch (error) {
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Caption Generation Failed</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}
                </div>
            </div>
        `;
        
        showResult(4, content, 'error');
    }
}

// Step 5: Check Google Sheets
async function checkSheets() {
    showLoading(5);
    
    try {
        const data = await apiRequest('/api/v1/content/pending');
        
        const itemsHtml = data.items && data.items.length > 0 
            ? data.items.map((item, i) => `
                <div class="result-info" style="margin-top: ${i > 0 ? '12px' : '0'};">
                    <div class="result-title">📄 Item ${i + 1}</div>
                    <div class="result-content">
                        ${Object.entries(item).map(([key, value]) => 
                            `<strong>${key}:</strong> ${value}`
                        ).join('<br>')}
                    </div>
                </div>
            `).join('')
            : '<div class="result-info"><div class="result-content">No pending items found in the sheet.</div></div>';
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Google Sheets Connected</div>
                <div class="result-content">
                    <strong>Found:</strong> ${data.count || 0} pending items<br>
                    <strong>Sheet:</strong> Configured and accessible
                </div>
            </div>
            ${itemsHtml}
            <div class="result-info">
                <div class="result-title">ℹ️ Configuration</div>
                <div class="result-content">
                    <strong>Credentials:</strong> credentials.json is loaded<br>
                    <strong>Check:</strong> Sheet must be shared with service account email<br>
                    <strong>Service Account:</strong> Found in credentials.json
                </div>
            </div>
        `;
        
        showResult(5, content, 'success');
    } catch (error) {
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Google Sheets Error</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    <strong>Troubleshooting:</strong>
                    <ul class="result-list">
                        <li>Verify credentials.json exists in project root</li>
                        <li>Check GOOGLE_SHEET_ID in .env file</li>
                        <li>Share the sheet with service account email</li>
                        <li>Enable Google Sheets API in Google Cloud Console</li>
                    </ul>
                </div>
            </div>
        `;
        
        showResult(5, content, 'error');
    }
}

// Step 6: Test Slack
async function testSlack() {
    showLoading(6);
    
    try {
        const data = await apiRequest('/api/v1/workflow/test-slack', 'POST');
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Slack Notification Sent</div>
                <div class="result-content">
                    Test notification successfully sent to configured Slack channel.
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">ℹ️ Where to Check</div>
                <div class="result-content">
                    <strong>Channel:</strong> Check the Slack channel configured in SLACK_WEBHOOK_URL<br>
                    <strong>Message:</strong> Look for a test notification message<br>
                    <strong>Timestamp:</strong> ${new Date().toLocaleString()}
                </div>
            </div>
            <div class="result-json">${formatJSON(data)}</div>
        `;
        
        showResult(6, content, 'success');
    } catch (error) {
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Slack Notification Failed</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    <strong>Troubleshooting:</strong>
                    <ul class="result-list">
                        <li>Check SLACK_WEBHOOK_URL in .env file</li>
                        <li>Verify webhook URL is correct</li>
                        <li>Ensure Slack app has proper permissions</li>
                        <li>Test webhook URL directly in browser</li>
                    </ul>
                </div>
            </div>
        `;
        
        showResult(6, content, 'error');
    }
}

// Step 7: Generate Video
function showVideoForm() {
    const form = document.getElementById('form-7');
    form.style.display = form.style.display === 'none' ? 'flex' : 'none';
}

async function generateVideo() {
    const prompt = document.getElementById('videoPrompt').value;
    const frames = parseInt(document.getElementById('videoFrames').value);
    
    if (!prompt) {
        alert('Please enter a video description');
        return;
    }
    
    showLoading(7);
    
    try {
        const data = await apiRequest('/api/v1/video/generate', 'POST', {
            prompt: prompt,
            num_frames: frames,
            height: 256,
            width: 256
        });
        
        const videoUrl = `${API_BASE_URL}${data.video_url}`;
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Video Generated Successfully!</div>
                <div class="result-content">
                    <strong>Video ID:</strong> ${data.video_id}<br>
                    <strong>Status:</strong> ${data.status}<br>
                    <strong>Generation Time:</strong> ${data.generation_time.toFixed(2)} seconds<br>
                    <strong>Resolution:</strong> ${data.resolution}<br>
                    <strong>Frames:</strong> ${data.num_frames}
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">🎬 Video Preview</div>
                <div class="result-content" style="text-align: center;">
                    <video id="generated-video" controls autoplay loop muted 
                           onerror="this.style.display='none'; document.getElementById('video-error-msg').style.display='block';">
                        <source src="${videoUrl}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <div id="video-error-msg" style="display: none; padding: 20px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; color: #856404;">
                        <strong>⚠️ Video Preview Unavailable</strong><br>
                        The video was generated successfully, but the preview couldn't load. 
                        Please use the download link below to view the video.
                    </div>
                    <br>
                    <strong>Prompt Used:</strong> ${data.prompt}
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">📹 Video Details</div>
                <div class="result-content">
                    <strong>Download URL:</strong> <a href="${videoUrl}" download="${data.video_id}.mp4" style="color: #667eea; text-decoration: underline;">Download Video</a><br>
                    <strong>Direct Link:</strong> <a href="${videoUrl}" target="_blank" style="color: #667eea; text-decoration: underline;">${data.video_url}</a><br>
                    <strong>File Location:</strong> generated_videos/${data.video_id}.mp4<br>
                    <strong>File Size:</strong> Check file properties for actual size
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">ℹ️ Important Notes</div>
                <div class="result-content">
                    <strong>First Time:</strong> If this was your first video generation, the model (~6GB) was downloaded automatically.<br>
                    <strong>GPU vs CPU:</strong> Generation time varies: 5-10 min on GPU, 30+ min on CPU<br>
                    <strong>Video Quality:</strong> This is a basic AI-generated video for demonstration purposes<br>
                    <strong>Playback:</strong> Video plays automatically in loop mode. Use controls to pause/replay.
                </div>
            </div>
            <div class="result-json">${formatJSON(data)}</div>
        `;
        
        showResult(7, content, 'success');
        document.getElementById('form-7').style.display = 'none';
    } catch (error) {
        // Log full error to console for debugging
        console.error('Video generation error:', error);
        
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Video Generation Failed</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    <strong>Common Issues:</strong>
                    <ul class="result-list">
                        <li>Insufficient GPU/CPU memory</li>
                        <li>Model not downloaded yet (check logs)</li>
                        <li>CUDA not available (will fallback to CPU)</li>
                        <li>Prompt too long (max 500 characters)</li>
                        <li>Invalid prompt format or validation failed</li>
                        <li>Check logs/ folder for detailed error messages</li>
                        <li><strong>Check browser console (F12) for full error details</strong></li>
                    </ul>
                </div>
            </div>
        `;
        
        showResult(7, content, 'error');
    }
}

// Step 8: Analytics
async function checkAnalytics() {
    showLoading(8);
    
    try {
        const data = await apiRequest('/api/v1/analytics/summary?days=7');
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Analytics Retrieved</div>
                <div class="result-content">
                    <strong>Period:</strong> Last 7 days<br>
                    <strong>Total Videos:</strong> ${data.total_videos || 0}<br>
                    <strong>Total Workflows:</strong> ${data.total_workflows || 0}
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">📊 Database Status</div>
                <div class="result-content">
                    <strong>Database File:</strong> ai_social_factory.db<br>
                    <strong>Tables:</strong> video_generations, workflow_executions<br>
                    <strong>Location:</strong> Project root directory<br><br>
                    You can query the database directly using SQLite tools for detailed analysis.
                </div>
            </div>
            <div class="result-json">${formatJSON(data)}</div>
        `;
        
        showResult(8, content, 'success');
    } catch (error) {
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Analytics Error</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    Check that the database is properly initialized: <code>python scripts/setup_db.py</code>
                </div>
            </div>
        `;
        
        showResult(8, content, 'error');
    }
}

// Step 9: Complete Workflow
function showWorkflowForm() {
    const form = document.getElementById('form-9');
    form.style.display = form.style.display === 'none' ? 'flex' : 'none';
}

async function executeWorkflow() {
    const topic = document.getElementById('workflowTopic').value;
    const platform = document.getElementById('workflowPlatform').value;
    
    if (!topic) {
        alert('Please enter a content topic');
        return;
    }
    
    showLoading(9);
    
    try {
        const data = await apiRequest('/api/v1/workflow/execute-direct', 'POST', {
            topic,
            platform,
            include_video: true
        });
        
        const stepsHtml = data.steps ? Object.entries(data.steps).map(([step, status]) => `
            <li><strong>${step.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${status}</li>
        `).join('') : '';
        
        const resultsHtml = data.results ? `
            <div class="result-info">
                <div class="result-title">📝 Generated Content</div>
                <div class="result-content">
                    <strong>Script:</strong><br>
                    ${data.results.script.replace(/\n/g, '<br>')}<br><br>
                    <strong>Caption:</strong><br>
                    ${data.results.caption}<br><br>
                    <strong>Hashtags:</strong> ${data.results.hashtags.map(h => '#' + h).join(' ')}<br><br>
                    ${data.results.video_url ? `<strong>Video:</strong> <a href="${API_BASE_URL}${data.results.video_url}" target="_blank">View Video</a>` : ''}
                </div>
            </div>
        ` : '';
        
        const content = `
            <div class="result-success">
                <div class="result-title">✅ Workflow Execution Completed!</div>
                <div class="result-content">
                    <strong>Workflow ID:</strong> ${data.workflow_id}<br>
                    <strong>Status:</strong> ${data.status}<br>
                    <strong>Topic:</strong> ${data.topic}<br>
                    <strong>Platform:</strong> ${data.platform}
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">🔄 Workflow Steps Completed</div>
                <div class="result-content">
                    <ul class="result-list">
                        ${stepsHtml}
                    </ul>
                </div>
            </div>
            ${resultsHtml}
            <div class="result-info">
                <div class="result-title">📍 Where to Check Results</div>
                <div class="result-content">
                    <ul class="result-list">
                        <li><strong>Video:</strong> Check generated_videos/ folder or click link above</li>
                        <li><strong>WordPress:</strong> Check your WordPress dashboard for draft post</li>
                        <li><strong>Slack:</strong> Check configured Slack channel for completion notification</li>
                        <li><strong>Database:</strong> Workflow saved in workflow_executions table</li>
                        <li><strong>Logs:</strong> Detailed logs in logs/ folder</li>
                    </ul>
                </div>
            </div>
            <div class="result-info">
                <div class="result-title">ℹ️ Important Notes</div>
                <div class="result-content">
                    ${data.message || 'Workflow completed successfully!'}<br><br>
                    <strong>Processing Time:</strong> Total workflow took several minutes to complete<br>
                    <strong>Video Generation:</strong> This step takes the longest (5-10 min on GPU, 30+ min on CPU)<br>
                    <strong>WordPress Post:</strong> Created as DRAFT for your review before publishing
                </div>
            </div>
            <div class="result-json">${formatJSON(data)}</div>
        `;
        
        showResult(9, content, 'success');
        document.getElementById('form-9').style.display = 'none';
    } catch (error) {
        console.error('Workflow execution error:', error);
        
        const content = `
            <div class="result-error">
                <div class="result-title">❌ Workflow Execution Failed</div>
                <div class="result-content">
                    <strong>Error:</strong> ${error.message}<br><br>
                    <strong>Troubleshooting:</strong>
                    <ul class="result-list">
                        <li>Ensure all previous steps are working (test each one individually)</li>
                        <li>Check GEMINI_API_KEY in .env file (required for script/caption)</li>
                        <li>Slack/WordPress failures are logged but won't stop workflow</li>
                        <li>Check logs/ folder for detailed error information</li>
                        <li>Check browser console (F12) for full error details</li>
                        <li>Try running steps individually first to identify issues</li>
                    </ul>
                </div>
            </div>
        `;
        
        showResult(9, content, 'error');
    }
}
