/**
 * ===========================================
 * SMART INVOICE - ADVANCED ANIMATION SYSTEM
 * Modern UI/UX with GSAP-like Animations
 * ===========================================
 */

class AnimationEngine {
  constructor() {
    this.observers = new Map();
    this.animations = new Set();
    this.debug = true; // Enable console logging
    this.log('🎨 Animation Engine initialized');
    this.init();
  }

  log(message, data = null) {
    if (this.debug) {
      const timestamp = new Date().toLocaleTimeString();
      console.log(`[${timestamp}] 🎨 AnimationEngine:`, message, data || '');
    }
  }

  init() {
    this.log('⚙️ Initializing Animation Engine...');
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.log('🚀 Setting up all animation modules...');
    this.setupScrollReveal();
    this.setupParallax();
    this.setupCountUp();
    this.setupPageTransitions();
    this.setupLoadingStates();
    this.setupRippleEffect();
    this.setupNavbarScroll();
    this.setupSmoothScroll();
    this.setupFormEnhancements();
    this.setupCardAnimations();
    this.setupMagneticButtons();
    this.log('✅ All animation modules ready');
  }

  setupScrollReveal() {
    const elements = document.querySelectorAll('[data-reveal]');
    this.log('📜 Setting up Scroll Reveal', `${elements.length} elements found`);
    
    if (this.prefersReducedMotion()) {
      this.log('⚠️ Reduced motion preference detected - skipping animations');
      elements.forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
      return;
    }

    const options = {
      root: null,
      rootMargin: '0px 0px -100px 0px',
      threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const delay = entry.target.dataset.delay || 0;
          this.log('👁️ Element revealed', entry.target.className);
          setTimeout(() => {
            entry.target.classList.add('revealed');
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0) scale(1)';
          }, delay);
          observer.unobserve(entry.target);
        }
      });
    }, options);

    elements.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(30px) scale(0.95)';
      el.style.transition = 'opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94), transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      observer.observe(el);
    });

    this.observers.set('scrollReveal', observer);
  }

  setupParallax() {
    if (this.prefersReducedMotion()) return;

    const parallaxElements = document.querySelectorAll('[data-parallax]');
    if (!parallaxElements.length) return;
    
    this.log('🌊 Setting up Parallax', `${parallaxElements.length} elements`);

    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      parallaxElements.forEach(el => {
        const speed = parseFloat(el.dataset.parallax) || 0.5;
        const yPos = -(scrolled * speed);
        el.style.transform = `translateY(${yPos}px)`;
      });
    }, { passive: true });
  }

  setupCountUp() {
    const countUpElements = document.querySelectorAll('[data-count]');
    if (!countUpElements.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateNumber(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    countUpElements.forEach(el => observer.observe(el));
  }

  animateNumber(element) {
    const target = parseInt(element.dataset.count);
    const duration = parseInt(element.dataset.duration) || 2000;
    const increment = target / (duration / 16);
    let current = 0;

    const updateCount = () => {
      current += increment;
      if (current < target) {
        element.textContent = Math.floor(current).toLocaleString();
        requestAnimationFrame(updateCount);
      } else {
        element.textContent = target.toLocaleString();
      }
    };

    requestAnimationFrame(updateCount);
  }

  setupPageTransitions() {
    if (this.prefersReducedMotion()) return;

    const overlay = document.createElement('div');
    overlay.id = 'page-transition-overlay';
    overlay.className = 'fixed inset-0 z-[9999] pointer-events-none opacity-0 transition-opacity duration-500';
    overlay.innerHTML = `
      <div class="absolute inset-0 bg-gradient-to-br from-primary-900 via-secondary-900 to-primary-900"></div>
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="loader-spinner"></div>
      </div>
    `;
    document.body.appendChild(overlay);

    document.querySelectorAll('a[href^="/"]').forEach(link => {
      if (link.target === '_blank' || link.download) return;

      link.addEventListener('click', (e) => {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1) {
          return;
        }

        const href = link.getAttribute('href');
        if (!href || href === '#' || href.startsWith('#')) return;

        e.preventDefault();
        overlay.classList.remove('pointer-events-none');
        overlay.style.opacity = '1';

        setTimeout(() => {
          window.location.href = href;
        }, 300);
      });
    });

    window.addEventListener('pageshow', () => {
      overlay.style.opacity = '0';
      setTimeout(() => {
        overlay.classList.add('pointer-events-none');
      }, 500);
    });
  }

  prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  setupLoadingStates() {
    const forms = document.querySelectorAll('form[data-loading]');
    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
          submitBtn.disabled = true;
          submitBtn.dataset.originalText = submitBtn.innerHTML;
          submitBtn.innerHTML = `
            <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          `;
        }
      });
    });
  }

  setupRippleEffect() {
    document.querySelectorAll('.ripple-effect, [data-ripple]').forEach(element => {
      element.style.position = 'relative';
      element.style.overflow = 'hidden';

      element.addEventListener('click', (e) => {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.className = 'ripple-animation';

        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
      });
    });
  }

  setupNavbarScroll() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    let lastScroll = 0;
    window.addEventListener('scroll', () => {
      const currentScroll = window.pageYOffset;

      if (currentScroll > 100) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }

      if (currentScroll > lastScroll && currentScroll > 500) {
        navbar.style.transform = 'translateY(-100%)';
      } else {
        navbar.style.transform = 'translateY(0)';
      }

      lastScroll = currentScroll;
    }, { passive: true });
  }

  setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#' || !href) return;

        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          const offsetTop = target.getBoundingClientRect().top + window.pageYOffset - 80;
          window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
          });
        }
      });
    });
  }

  setupFormEnhancements() {
    const inputs = document.querySelectorAll('input[data-validate], textarea[data-validate]');
    inputs.forEach(input => {
      const container = input.closest('.form-group') || input.parentElement;
      
      input.addEventListener('input', () => {
        this.validateInput(input, container);
      });

      input.addEventListener('blur', () => {
        this.validateInput(input, container);
      });

      input.addEventListener('focus', () => {
        container.classList.add('focused');
      });

      input.addEventListener('blur', () => {
        container.classList.remove('focused');
      });
    });

    const numberInputs = document.querySelectorAll('input[data-calculate]');
    numberInputs.forEach(input => {
      input.addEventListener('input', () => {
        this.triggerCalculation();
      });
    });
  }

  validateInput(input, container) {
    const value = input.value.trim();
    const type = input.dataset.validate;
    let isValid = true;
    let message = '';

    switch (type) {
      case 'email':
        isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        message = isValid ? '' : 'Please enter a valid email address';
        break;
      case 'phone':
        isValid = /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/.test(value);
        message = isValid ? '' : 'Please enter a valid phone number';
        break;
      case 'required':
        isValid = value.length > 0;
        message = isValid ? '' : 'This field is required';
        break;
      case 'number':
        isValid = !isNaN(value) && value !== '';
        message = isValid ? '' : 'Please enter a valid number';
        break;
    }

    this.updateValidationUI(container, isValid, message);
  }

  updateValidationUI(container, isValid, message) {
    let feedback = container.querySelector('.validation-feedback');
    
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.className = 'validation-feedback';
      container.appendChild(feedback);
    }

    if (isValid) {
      container.classList.remove('invalid');
      container.classList.add('valid');
      feedback.style.maxHeight = '0';
      feedback.style.opacity = '0';
    } else if (message) {
      container.classList.remove('valid');
      container.classList.add('invalid');
      feedback.textContent = message;
      feedback.style.maxHeight = '40px';
      feedback.style.opacity = '1';
    }
  }

  triggerCalculation() {
    const event = new CustomEvent('formCalculate', { bubbles: true });
    document.dispatchEvent(event);
  }

  setupCardAnimations() {
    document.querySelectorAll('[data-card-3d]').forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      });
    });
  }

  setupMagneticButtons() {
    document.querySelectorAll('[data-magnetic]').forEach(button => {
      button.addEventListener('mousemove', (e) => {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        button.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
      });

      button.addEventListener('mouseleave', () => {
        button.style.transform = 'translate(0, 0)';
      });
    });
  }

  showToast(message, type = 'success') {
    this.log('🔔 Showing toast notification', { message, type });
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-icon">${this.getToastIcon(type)}</span>
        <span class="toast-message">${message}</span>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;

    const container = document.getElementById('toast-container') || this.createToastContainer();
    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }

  createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-20 right-4 z-[9999] space-y-2';
    document.body.appendChild(container);
    return container;
  }

  getToastIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    return icons[type] || icons.info;
  }

  createLoadingSkeleton(parent, config = {}) {
    const skeleton = document.createElement('div');
    skeleton.className = `skeleton-loader ${config.className || ''}`;
    skeleton.innerHTML = `
      <div class="skeleton-item" style="height: ${config.height || '200px'}">
        <div class="skeleton-shimmer"></div>
      </div>
    `;
    parent.appendChild(skeleton);
    return skeleton;
  }

  showSuccessAnimation(element) {
    element.classList.add('success-pulse');
    setTimeout(() => element.classList.remove('success-pulse'), 1000);
  }
}

const animationEngine = new AnimationEngine();

window.AnimationEngine = animationEngine;

document.addEventListener('DOMContentLoaded', () => {
  const progressBar = document.getElementById('progressBar');
  if (progressBar) {
    window.addEventListener('scroll', () => {
      const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (window.pageYOffset / windowHeight) * 100;
      progressBar.style.width = scrolled + '%';
    }, { passive: true });
  }

  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileOverlay = document.getElementById('mobileOverlay');
  const closeMobileMenu = document.getElementById('closeMobileMenu');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.remove('translate-x-full');
      mobileOverlay.classList.remove('opacity-0', 'pointer-events-none');
    });

    const closeMenu = () => {
      mobileMenu.classList.add('translate-x-full');
      mobileOverlay.classList.add('opacity-0', 'pointer-events-none');
    };

    closeMobileMenu?.addEventListener('click', closeMenu);
    mobileOverlay?.addEventListener('click', closeMenu);

    document.querySelectorAll('.mobile-link').forEach(link => {
      link.addEventListener('click', closeMenu);
    });
  }
});
