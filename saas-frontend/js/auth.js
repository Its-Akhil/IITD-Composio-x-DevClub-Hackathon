// Authentication JavaScript
// ============================================
// Mock authentication using LocalStorage
// In production, replace with real JWT authentication

// Check if user is already logged in
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const isAuthPage = currentPath.includes('login.html') || currentPath.includes('signup.html');
    
    // If on auth page and already logged in, redirect to dashboard
    if (isAuthPage && isLoggedIn()) {
        window.location.href = 'dashboard.html';
    }
    
    // Initialize form handlers
    if (document.getElementById('loginForm')) {
        initLoginForm();
    }
    
    if (document.getElementById('signupForm')) {
        initSignupForm();
    }
    
    // Handle plan pre-selection from URL
    const urlParams = new URLSearchParams(window.location.search);
    const plan = urlParams.get('plan');
    if (plan && document.getElementById('plan')) {
        document.getElementById('plan').value = plan;
    }
});

// Check if user is logged in
function isLoggedIn() {
    const user = localStorage.getItem('aisf_user');
    const token = localStorage.getItem('aisf_token');
    return user && token;
}

// Get current user
function getCurrentUser() {
    const userJson = localStorage.getItem('aisf_user');
    return userJson ? JSON.parse(userJson) : null;
}

// Login Form Handler
function initLoginForm() {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const rememberCheckbox = document.getElementById('remember');
    const loginBtn = document.getElementById('loginBtn');
    const loginBtnText = document.getElementById('loginBtnText');
    const loginSpinner = document.getElementById('loginSpinner');
    const loginError = document.getElementById('loginError');
    const loginErrorMessage = document.getElementById('loginErrorMessage');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous errors
        hideError(loginError);
        clearFieldErrors();
        
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const remember = rememberCheckbox.checked;
        
        // Validate
        if (!validateEmail(email)) {
            showFieldError('email', 'Please enter a valid email address');
            return;
        }
        
        if (password.length < 8) {
            showFieldError('password', 'Password must be at least 8 characters');
            return;
        }
        
        // Show loading state
        setButtonLoading(loginBtn, loginBtnText, loginSpinner, true);
        
        try {
            // Simulate API call
            await delay(1000);
            
            // Mock login logic
            const mockUser = loginUser(email, password, remember);
            
            if (mockUser) {
                // Success - redirect to dashboard
                window.location.href = 'dashboard.html';
            } else {
                // Failed - show error
                showError(loginError, loginErrorMessage, 'Invalid email or password');
                setButtonLoading(loginBtn, loginBtnText, loginSpinner, false);
            }
        } catch (error) {
            showError(loginError, loginErrorMessage, 'An error occurred. Please try again.');
            setButtonLoading(loginBtn, loginBtnText, loginSpinner, false);
        }
    });
}

// Signup Form Handler
function initSignupForm() {
    const form = document.getElementById('signupForm');
    const fullNameInput = document.getElementById('fullName');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const planSelect = document.getElementById('plan');
    const termsCheckbox = document.getElementById('terms');
    const newsletterCheckbox = document.getElementById('newsletter');
    const signupBtn = document.getElementById('signupBtn');
    const signupBtnText = document.getElementById('signupBtnText');
    const signupSpinner = document.getElementById('signupSpinner');
    const signupError = document.getElementById('signupError');
    const signupErrorMessage = document.getElementById('signupErrorMessage');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous errors
        hideError(signupError);
        clearFieldErrors();
        
        const fullName = fullNameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const plan = planSelect.value;
        const acceptedTerms = termsCheckbox.checked;
        const newsletter = newsletterCheckbox.checked;
        
        // Validate
        let hasError = false;
        
        if (fullName.length < 2) {
            showFieldError('fullName', 'Please enter your full name');
            hasError = true;
        }
        
        if (!validateEmail(email)) {
            showFieldError('email', 'Please enter a valid email address');
            hasError = true;
        }
        
        if (password.length < 8) {
            showFieldError('password', 'Password must be at least 8 characters');
            hasError = true;
        }
        
        if (password !== confirmPassword) {
            showFieldError('confirmPassword', 'Passwords do not match');
            hasError = true;
        }
        
        if (!acceptedTerms) {
            showError(signupError, signupErrorMessage, 'You must accept the Terms of Service');
            hasError = true;
        }
        
        if (hasError) return;
        
        // Show loading state
        setButtonLoading(signupBtn, signupBtnText, signupSpinner, true);
        
        try {
            // Simulate API call
            await delay(1500);
            
            // Check if user already exists
            const existingUsers = JSON.parse(localStorage.getItem('aisf_users') || '[]');
            if (existingUsers.find(u => u.email === email)) {
                showError(signupError, signupErrorMessage, 'An account with this email already exists');
                setButtonLoading(signupBtn, signupBtnText, signupSpinner, false);
                return;
            }
            
            // Create new user
            const newUser = createUser({
                fullName,
                email,
                password,
                plan,
                newsletter
            });
            
            if (newUser) {
                // Success - redirect to dashboard
                window.location.href = 'dashboard.html';
            } else {
                showError(signupError, signupErrorMessage, 'Failed to create account. Please try again.');
                setButtonLoading(signupBtn, signupBtnText, signupSpinner, false);
            }
        } catch (error) {
            showError(signupError, signupErrorMessage, 'An error occurred. Please try again.');
            setButtonLoading(signupBtn, signupBtnText, signupSpinner, false);
        }
    });
}

// Mock Authentication Functions
function loginUser(email, password, remember) {
    // In mock mode, check if user exists in localStorage
    const users = JSON.parse(localStorage.getItem('aisf_users') || '[]');
    const user = users.find(u => u.email === email && u.password === password);
    
    if (user) {
        // Create session
        const token = generateMockToken();
        const sessionUser = {
            id: user.id,
            email: user.email,
            fullName: user.fullName,
            plan: user.plan,
            createdAt: user.createdAt,
            videosGenerated: user.videosGenerated || 0,
            scriptsGenerated: user.scriptsGenerated || 0
        };
        
        localStorage.setItem('aisf_token', token);
        localStorage.setItem('aisf_user', JSON.stringify(sessionUser));
        
        if (remember) {
            localStorage.setItem('aisf_remember', 'true');
        }
        
        return sessionUser;
    }
    
    return null;
}

function createUser({ fullName, email, password, plan, newsletter }) {
    const users = JSON.parse(localStorage.getItem('aisf_users') || '[]');
    
    const newUser = {
        id: generateId(),
        fullName,
        email,
        password, // In production, NEVER store plain passwords!
        plan,
        newsletter,
        createdAt: new Date().toISOString(),
        videosGenerated: 0,
        scriptsGenerated: 0,
        apiKey: generateApiKey()
    };
    
    users.push(newUser);
    localStorage.setItem('aisf_users', JSON.stringify(users));
    
    // Create session
    const token = generateMockToken();
    const sessionUser = {
        id: newUser.id,
        email: newUser.email,
        fullName: newUser.fullName,
        plan: newUser.plan,
        createdAt: newUser.createdAt,
        videosGenerated: 0,
        scriptsGenerated: 0
    };
    
    localStorage.setItem('aisf_token', token);
    localStorage.setItem('aisf_user', JSON.stringify(sessionUser));
    
    return sessionUser;
}

function logout() {
    const remember = localStorage.getItem('aisf_remember');
    
    localStorage.removeItem('aisf_token');
    localStorage.removeItem('aisf_user');
    
    if (!remember) {
        // Don't clear users database, just session
    }
    
    window.location.href = 'login.html';
}

// Utility Functions
function generateMockToken() {
    return 'mock_token_' + Math.random().toString(36).substr(2, 9);
}

function generateId() {
    return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function generateApiKey() {
    return 'aisf_' + Math.random().toString(36).substr(2, 9) + '_' + Math.random().toString(36).substr(2, 9);
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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

function showError(errorElement, messageElement, message) {
    messageElement.textContent = message;
    errorElement.style.display = 'block';
    errorElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError(errorElement) {
    errorElement.style.display = 'none';
}

function showFieldError(fieldName, message) {
    const input = document.getElementById(fieldName);
    const errorElement = document.getElementById(fieldName + 'Error');
    
    if (input && errorElement) {
        input.classList.add('error');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        errorElement.classList.add('error');
    }
}

function clearFieldErrors() {
    document.querySelectorAll('.form-input').forEach(input => {
        input.classList.remove('error');
    });
    
    document.querySelectorAll('.form-help-text').forEach(helpText => {
        if (helpText.classList.contains('error') || helpText.id.includes('Error')) {
            helpText.style.display = 'none';
            helpText.classList.remove('error');
        }
    });
}

// Export for use in other scripts
window.auth = {
    isLoggedIn,
    getCurrentUser,
    logout,
    loginUser,
    createUser
};
