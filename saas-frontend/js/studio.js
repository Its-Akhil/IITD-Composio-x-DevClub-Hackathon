// Studio JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!window.auth.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }
    
    initStudio();
});

function initStudio() {
    // Load user info (reuse from dashboard)
    if (window.dashboard && window.dashboard.loadUserInfo) {
        loadUserInfo();
    }
    
    // Initialize tabs
    initTabs();
    
    // Initialize forms
    initVideoForm();
    initScriptForm();
    initCaptionForm();
    initWorkflowForm();
    
    // Initialize event listeners
    initEventListeners();
}

function loadUserInfo() {
    const user = window.auth.getCurrentUser();
    
    if (user) {
        const userNameEl = document.getElementById('userName');
        if (userNameEl) userNameEl.textContent = user.fullName || user.email;
        
        const userAvatarEl = document.getElementById('userAvatar');
        if (userAvatarEl && user.fullName) {
            const initials = user.fullName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
            userAvatarEl.textContent = initials;
        }
        
        const planBadgeEl = document.getElementById('userPlanBadge');
        if (planBadgeEl && user.plan) {
            const planNames = { free: 'Free Plan', pro: 'Pro Plan', enterprise: 'Enterprise' };
            planBadgeEl.textContent = planNames[user.plan] || 'Free Plan';
        }
        
        updateUsageDisplay(user);
    }
}

function updateUsageDisplay(user) {
    const plan = user.plan || 'free';
    const limits = { free: 5, pro: 50, enterprise: 999999 };
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

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Remove active class from all tabs
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            btn.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
}

function initVideoForm() {
    const form = document.getElementById('videoForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const prompt = document.getElementById('videoPrompt').value.trim();
        const resolution = parseInt(document.getElementById('videoResolution').value);
        const frames = parseInt(document.getElementById('videoFrames').value);
        
        const btn = document.getElementById('generateVideoBtn');
        const btnText = document.getElementById('generateVideoBtnText');
        const spinner = document.getElementById('generateVideoSpinner');
        
        // Show loading
        setButtonLoading(btn, btnText, spinner, true);
        
        try {
            const result = await window.api.generateVideo(prompt, {
                height: resolution,
                width: resolution,
                numFrames: frames
            });
            
            // Display video
            displayVideo(result);
            
            // Update user stats
            incrementVideoCount();
            
            showSuccess('Video generated successfully!');
        } catch (error) {
            console.error('Video generation error:', error);
            const errorMsg = error.message || error.toString() || 'Unknown error occurred';
            showError('Failed to generate video: ' + errorMsg);
        } finally {
            setButtonLoading(btn, btnText, spinner, false);
        }
    });
}

function initScriptForm() {
    const form = document.getElementById('scriptForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const topic = document.getElementById('scriptTopic').value.trim();
        const platform = document.getElementById('scriptPlatform').value;
        const variants = parseInt(document.getElementById('scriptVariants').value);
        
        const btn = document.getElementById('generateScriptBtn');
        const btnText = document.getElementById('generateScriptBtnText');
        const spinner = document.getElementById('generateScriptSpinner');
        
        setButtonLoading(btn, btnText, spinner, true);
        
        try {
            const result = await window.api.generateScript(topic, platform, variants);
            
            // Backend returns { topic, variants: [{variant_id, script, style, duration_estimate}], metadata }
            displayScripts(result.variants);
            showSuccess('Scripts generated successfully!');
        } catch (error) {
            console.error('Script generation error:', error);
            const errorMsg = error.message || error.toString() || 'Unknown error occurred';
            showError('Failed to generate scripts: ' + errorMsg);
        } finally {
            setButtonLoading(btn, btnText, spinner, false);
        }
    });
}

function initCaptionForm() {
    const form = document.getElementById('captionForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const contentType = document.getElementById('captionContentType').value;
        const topic = document.getElementById('captionTopic').value.trim();
        const platform = document.getElementById('captionPlatform').value;
        const tone = document.getElementById('captionTone').value;
        
        const btn = document.getElementById('generateCaptionBtn');
        const btnText = document.getElementById('generateCaptionBtnText');
        const spinner = document.getElementById('generateCaptionSpinner');
        
        setButtonLoading(btn, btnText, spinner, true);
        
        try {
            // First, generate a script based on the topic
            btnText.textContent = 'Generating script...';
            const scriptResult = await window.api.generateScript(topic, platform, 1);
            
            // Use the first script variant to generate caption
            btnText.textContent = 'Creating caption...';
            const script = scriptResult.variants[0].script;
            const result = await window.api.generateCaption(script, platform, true);
            
            displayCaption(result);
            showSuccess('Caption generated successfully!');
        } catch (error) {
            console.error('Caption generation error:', error);
            const errorMsg = error.message || error.toString() || 'Unknown error occurred';
            showError('Failed to generate caption: ' + errorMsg);
        } finally {
            btnText.textContent = 'Generate Caption';
            setButtonLoading(btn, btnText, spinner, false);
        }
    });
}

function initWorkflowForm() {
    const form = document.getElementById('workflowForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const topic = document.getElementById('workflowTopic').value.trim();
        const platform = document.getElementById('workflowPlatform').value;
        const includeVideo = document.getElementById('workflowIncludeVideo').checked;
        const requireApproval = document.getElementById('workflowRequireApproval').checked;
        
        const btn = document.getElementById('executeWorkflowBtn');
        const btnText = document.getElementById('executeWorkflowBtnText');
        const spinner = document.getElementById('executeWorkflowSpinner');
        
        setButtonLoading(btn, btnText, spinner, true);
        
        // Show progress
        showWorkflowProgress();
        
        try {
            const result = await window.api.executeWorkflow(topic, platform, includeVideo, requireApproval);
            
            displayWorkflowResults(result);
            showSuccess('Workflow completed successfully!');
        } catch (error) {
            console.error('Workflow execution error:', error);
            const errorMsg = error.message || error.toString() || 'Unknown error occurred';
            showError('Workflow failed: ' + errorMsg);
            updateWorkflowStep('failed', 'Workflow failed');
        } finally {
            setButtonLoading(btn, btnText, spinner, false);
        }
    });
}

function displayVideo(result) {
    const previewArea = document.getElementById('videoPreviewArea');
    const videoInfo = document.getElementById('videoInfo');
    
    previewArea.innerHTML = `
        <div class="video-display">
            <video controls autoplay loop>
                <source src="http://localhost:8000${result.video_url}" type="video/mp4">
                Your browser does not support video playback.
            </video>
        </div>
    `;
    
    document.getElementById('videoStatus').textContent = 'Completed';
    document.getElementById('videoStatus').className = 'badge badge-success';
    document.getElementById('videoId').textContent = result.video_id || result.id;
    document.getElementById('videoTime').textContent = new Date().toLocaleTimeString();
    
    videoInfo.style.display = 'block';
}

function displayScripts(variants) {
    const container = document.getElementById('scriptsContainer');
    
    // variants is an array of {variant_id, script, style, duration_estimate}
    container.innerHTML = variants.map((variant, index) => `
        <div class="script-variant">
            <div class="script-header">
                <span class="variant-number">Variant ${index + 1} (${variant.style || 'Standard'}) - ~${variant.duration_estimate}s</span>
                <button class="copy-btn" data-script="${escapeHtml(variant.script)}" onclick="copyScriptText(this)">
                    Copy
                </button>
            </div>
            <div class="script-text">${escapeHtml(variant.script)}</div>
        </div>
    `).join('');
}

function displayCaption(result) {
    const container = document.getElementById('captionContainer');
    
    const fullText = result.caption + '\n\n' + result.hashtags.join(' ');
    
    container.innerHTML = `
        <div class="caption-result">
            <div class="caption-text">${escapeHtml(result.caption)}</div>
            <div class="caption-hashtags">
                ${result.hashtags.map(tag => `<span class="hashtag">${tag}</span>`).join('')}
            </div>
            <button class="btn btn-secondary" data-text="${escapeHtml(fullText)}" onclick="copyCaptionText(this)" style="margin-top: 1rem; width: 100%;">
                Copy Caption & Hashtags
            </button>
        </div>
    `;
}

function showWorkflowProgress() {
    const progressEl = document.getElementById('workflowProgress');
    const stepsEl = document.getElementById('progressSteps');
    
    stepsEl.innerHTML = `
        <div class="progress-step active" id="step-script">
            <div class="step-icon">1</div>
            <div class="step-content">
                <div class="step-title">Generating Script</div>
                <div class="step-description">Creating engaging content...</div>
            </div>
        </div>
        <div class="progress-step" id="step-caption">
            <div class="step-icon">2</div>
            <div class="step-content">
                <div class="step-title">Generating Caption</div>
                <div class="step-description">Writing perfect caption with hashtags...</div>
            </div>
        </div>
        <div class="progress-step" id="step-video">
            <div class="step-icon">3</div>
            <div class="step-content">
                <div class="step-title">Creating Video</div>
                <div class="step-description">Generating AI video...</div>
            </div>
        </div>
        <div class="progress-step" id="step-publish">
            <div class="step-icon">4</div>
            <div class="step-content">
                <div class="step-title">Publishing</div>
                <div class="step-description">Sending to platforms...</div>
            </div>
        </div>
    `;
    
    progressEl.style.display = 'block';
}

function displayWorkflowResults(result) {
    // Mark all steps as completed
    ['script', 'caption', 'video', 'publish'].forEach(step => {
        const stepEl = document.getElementById(`step-${step}`);
        if (stepEl) {
            stepEl.classList.remove('active');
            // Check if step was actually completed
            const stepStatus = result.steps[`${step}_generation`] || result.steps[step];
            if (stepStatus && stepStatus.includes('completed')) {
                stepEl.classList.add('completed');
            } else if (stepStatus && stepStatus.includes('skipped')) {
                stepEl.classList.add('skipped');
            } else if (stepStatus && stepStatus.includes('failed')) {
                stepEl.classList.add('failed');
            } else {
                stepEl.classList.add('completed'); // Default to completed
            }
        }
    });
    
    // Show results in a summary
    const stepsEl = document.getElementById('progressSteps');
    stepsEl.innerHTML += `
        <div class="workflow-summary" style="margin-top: 2rem; padding: 1.5rem; background: var(--gray-50); border-radius: var(--radius-md);">
            <h4 style="margin-bottom: 1rem;">Workflow Complete! 🎉</h4>
            <p><strong>Script:</strong> ${result.results.script ? '✅ Generated' : '❌ Skipped'}</p>
            <p><strong>Caption:</strong> ${result.results.caption ? '✅ ' + result.results.caption.substring(0, 50) + '...' : '❌ N/A'}</p>
            <p><strong>Hashtags:</strong> ${result.results.hashtags ? result.results.hashtags.join(' ') : 'None'}</p>
            <p><strong>Video:</strong> ${result.results.video_url ? '✅ Generated' : '⚠️ ' + (result.steps.video_generation || 'Skipped')}</p>
            <p><strong>Status:</strong> <span style="color: var(--success);">${result.status}</span></p>
            ${result.message ? `<p style="margin-top: 1rem; font-style: italic; color: var(--gray-600);">${result.message}</p>` : ''}
        </div>
    `;
}

function incrementVideoCount() {
    const user = window.auth.getCurrentUser();
    if (user) {
        user.videosGenerated = (user.videosGenerated || 0) + 1;
        localStorage.setItem('aisf_user', JSON.stringify(user));
        updateUsageDisplay(user);
    }
}

function setButtonLoading(button, textElement, spinner, isLoading) {
    if (isLoading) {
        button.disabled = true;
        textElement.style.display = 'none';
        spinner.style.display = 'inline-block';
    } else {
        button.disabled = false;
        textElement.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccess('Copied to clipboard!');
    }).catch(() => {
        showError('Failed to copy to clipboard');
    });
}

function copyScriptText(button) {
    const text = button.getAttribute('data-script');
    // Decode HTML entities back to text
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    const decodedText = textarea.value;
    copyToClipboard(decodedText);
}

function copyCaptionText(button) {
    const text = button.getAttribute('data-text');
    // Decode HTML entities back to text
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    const decodedText = textarea.value;
    copyToClipboard(decodedText);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(message) {
    // Simple alert for now - can be replaced with toast notification
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.style.position = 'fixed';
    alert.style.top = '2rem';
    alert.style.right = '2rem';
    alert.style.zIndex = '10000';
    alert.innerHTML = `<strong>Success!</strong> ${message}`;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 3000);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.style.position = 'fixed';
    alert.style.top = '2rem';
    alert.style.right = '2rem';
    alert.style.zIndex = '10000';
    alert.innerHTML = `<strong>Error!</strong> ${message}`;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
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
}

// Export for global access
window.copyToClipboard = copyToClipboard;
window.copyScriptText = copyScriptText;
window.copyCaptionText = copyCaptionText;
window.studio = {
    displayVideo,
    displayScripts,
    displayCaption,
    showSuccess,
    showError
};
