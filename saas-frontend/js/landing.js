// Landing Page JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initSmoothScroll();
    initScrollEffects();
    initVideoPreview();
});

// Mobile Menu
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }
}

// Smooth Scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            // Skip if href is just "#"
            if (href === '#') {
                e.preventDefault();
                return;
            }
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                const offsetTop = target.offsetTop - 80; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll effects - navbar background on scroll
function initScrollEffects() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });
    
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe feature cards, pricing cards, testimonials
    document.querySelectorAll('.feature-card, .pricing-card, .testimonial-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Video Preview Demo
function initVideoPreview() {
    const playButton = document.querySelector('.play-button');
    const videoPreview = document.querySelector('.video-preview');
    
    if (playButton && videoPreview) {
        playButton.addEventListener('click', () => {
            // In a real implementation, this would open a modal with an actual demo video
            showDemoModal();
        });
    }
}

function showDemoModal() {
    // Create modal for demo video
    const modal = document.createElement('div');
    modal.className = 'demo-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="this.parentElement.remove()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>AI Social Factory Demo</h3>
                    <button class="modal-close" onclick="this.closest('.demo-modal').remove()">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="demo-placeholder">
                        <div class="demo-icon">
                            <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                                <circle cx="40" cy="40" r="40" fill="#667eea" opacity="0.1"/>
                                <path d="M30 25L55 40L30 55V25Z" fill="#667eea"/>
                            </svg>
                        </div>
                        <h4>Demo Video Coming Soon</h4>
                        <p>Watch how AI Social Factory can transform your content creation workflow in just a few clicks.</p>
                        <a href="signup.html" class="btn btn-primary" style="margin-top: 1rem;">
                            Try It Free Instead
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add styles for demo modal
    const style = document.createElement('style');
    style.textContent = `
        .demo-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 9999;
            animation: fadeIn 0.3s;
        }
        
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .modal-content {
            background: white;
            border-radius: 1rem;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow: auto;
            animation: slideUp 0.3s;
        }
        
        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.5rem 2rem;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .modal-header h3 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .modal-close {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            color: #6b7280;
            transition: color 0.2s;
        }
        
        .modal-close:hover {
            color: #111827;
        }
        
        .modal-body {
            padding: 2rem;
        }
        
        .demo-placeholder {
            text-align: center;
            padding: 3rem 2rem;
        }
        
        .demo-icon {
            margin-bottom: 1.5rem;
        }
        
        .demo-placeholder h4 {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .demo-placeholder p {
            color: #6b7280;
            margin-bottom: 0;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    `;
    
    document.head.appendChild(style);
}

// Track CTA button clicks (for analytics)
document.querySelectorAll('.btn-primary, .btn-secondary').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const buttonText = e.target.textContent.trim();
        console.log('CTA clicked:', buttonText);
        
        // In production, send to analytics
        // analytics.track('CTA Clicked', { button: buttonText, page: 'landing' });
    });
});

// Newsletter signup (if added later)
function handleNewsletterSignup(email) {
    console.log('Newsletter signup:', email);
    // In production, send to backend
    return fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
}

// Export for use in other scripts
window.landingPage = {
    showDemoModal,
    handleNewsletterSignup
};
