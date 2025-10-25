/**
 * ================================================
 * INTERACTIVE PRICING & CAROUSEL SYSTEM
 * Professional pricing tables and testimonials
 * ================================================
 */

class InteractivePricing {
  constructor() {
    this.init();
  }

  init() {
    this.setupTestimonialsCarousel();
    this.setupFAQAccordion();
    this.setupConfettiEffect();
    this.setupNewsletterForm();
  }

  setupTestimonialsCarousel() {
    const carousel = document.getElementById('testimonials-carousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('[data-testimonial-slide]');
    const dots = carousel.querySelectorAll('[data-testimonial-dot]');
    const prevBtn = document.getElementById('testimonial-prev');
    const nextBtn = document.getElementById('testimonial-next');
    let currentSlide = 0;
    let autoplayInterval = null;

    const showSlide = (index) => {
      slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
      });

      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
      });

      currentSlide = index;
    };

    const nextSlide = () => {
      const next = (currentSlide + 1) % slides.length;
      showSlide(next);
    };

    const prevSlide = () => {
      const prev = (currentSlide - 1 + slides.length) % slides.length;
      showSlide(prev);
    };

    const startAutoplay = () => {
      stopAutoplay();
      autoplayInterval = setInterval(nextSlide, 6000);
    };

    const stopAutoplay = () => {
      if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
      }
    };

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        nextSlide();
        stopAutoplay();
        startAutoplay();
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        prevSlide();
        stopAutoplay();
        startAutoplay();
      });
    }

    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        showSlide(index);
        stopAutoplay();
        startAutoplay();
      });
    });

    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);

    startAutoplay();
  }

  setupNewsletterForm() {
    const form = document.getElementById('newsletter-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const emailInput = document.getElementById('newsletter-email');
      const submitBtn = form.querySelector('[type="submit"]');
      const successMsg = document.getElementById('newsletter-success');
      
      if (!emailInput || !submitBtn) return;

      const email = emailInput.value.trim();
      
      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        this.showToast('Please enter a valid email address', 'error');
        return;
      }

      // Disable submit button
      submitBtn.disabled = true;
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Subscribing...';

      // Simulate API call (replace with actual backend endpoint)
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Show success
      emailInput.value = '';
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      
      if (successMsg) {
        successMsg.classList.remove('hidden');
        setTimeout(() => {
          successMsg.classList.add('hidden');
        }, 5000);
      }

      this.showToast('Successfully subscribed to newsletter!', 'success');
      this.createConfetti(
        window.innerWidth / 2,
        submitBtn.getBoundingClientRect().top + window.scrollY
      );
    });
  }

  showToast(message, type = 'success') {
    const toast = document.createElement('div');
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    
    toast.className = `fixed top-24 right-4 z-[9999] glass-card px-6 py-4 rounded-xl border-2 ${
      type === 'success' ? 'border-success-500/50' :
      type === 'error' ? 'border-danger-500/50' :
      type === 'warning' ? 'border-warning-500/50' :
      'border-primary-500/50'
    } shadow-glow animate-slide-left`;
    
    toast.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="text-2xl">${icons[type]}</span>
        <span class="text-white font-semibold">${message}</span>
      </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  setupFAQAccordion() {
    const accordionItems = document.querySelectorAll('[data-faq-item]');
    const searchInput = document.getElementById('faq-search');
    const categoryButtons = document.querySelectorAll('.faq-category-btn');
    let currentCategory = 'all';

    // Accordion toggle functionality
    accordionItems.forEach(item => {
      const trigger = item.querySelector('[data-faq-trigger]');
      const content = item.querySelector('[data-faq-content]');
      const icon = item.querySelector('[data-faq-icon]');

      if (!trigger || !content) return;

      trigger.addEventListener('click', () => {
        const isOpen = item.classList.contains('active');

        accordionItems.forEach(otherItem => {
          if (otherItem !== item) {
            otherItem.classList.remove('active');
            const otherContent = otherItem.querySelector('[data-faq-content]');
            const otherIcon = otherItem.querySelector('[data-faq-icon]');
            if (otherContent) otherContent.style.maxHeight = '0';
            if (otherIcon) otherIcon.style.transform = 'rotate(0deg)';
          }
        });

        if (!isOpen) {
          item.classList.add('active');
          content.style.maxHeight = content.scrollHeight + 'px';
          if (icon) icon.style.transform = 'rotate(180deg)';
        } else {
          item.classList.remove('active');
          content.style.maxHeight = '0';
          if (icon) icon.style.transform = 'rotate(0deg)';
        }
      });
    });

    // Search functionality
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filterFAQs(e.target.value, currentCategory);
      });
    }

    // Category filter functionality
    categoryButtons.forEach(button => {
      button.addEventListener('click', () => {
        categoryButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        currentCategory = button.dataset.category;
        this.filterFAQs(searchInput ? searchInput.value : '', currentCategory);
      });
    });
  }

  filterFAQs(searchQuery, category) {
    const accordionItems = document.querySelectorAll('[data-faq-item]');
    const query = searchQuery.toLowerCase().trim();
    let visibleCount = 0;

    accordionItems.forEach(item => {
      const question = item.querySelector('[data-faq-question]');
      const content = item.querySelector('[data-faq-content]');
      const itemCategory = item.dataset.category || 'all';
      
      if (!question) return;

      const questionText = question.textContent.toLowerCase();
      const contentText = content ? content.textContent.toLowerCase() : '';
      
      const matchesSearch = !query || questionText.includes(query) || contentText.includes(query);
      const matchesCategory = category === 'all' || itemCategory === category;
      
      if (matchesSearch && matchesCategory) {
        item.style.display = 'block';
        item.style.opacity = '1';
        item.style.transform = 'translateY(0)';
        visibleCount++;
      } else {
        item.style.display = 'none';
        item.style.opacity = '0';
        item.style.transform = 'translateY(-10px)';
        
        // Close item if it's hidden
        if (item.classList.contains('active')) {
          item.classList.remove('active');
          const itemContent = item.querySelector('[data-faq-content]');
          const icon = item.querySelector('[data-faq-icon]');
          if (itemContent) itemContent.style.maxHeight = '0';
          if (icon) icon.style.transform = 'rotate(0deg)';
        }
      }
    });

    // Show "no results" message if needed
    this.showNoResultsMessage(visibleCount);
  }

  showNoResultsMessage(visibleCount) {
    const faqList = document.getElementById('faq-list');
    if (!faqList) return;

    let noResultsMsg = faqList.querySelector('.no-results-message');
    
    if (visibleCount === 0) {
      if (!noResultsMsg) {
        noResultsMsg = document.createElement('div');
        noResultsMsg.className = 'no-results-message glass-card p-8 text-center';
        noResultsMsg.innerHTML = `
          <div class="text-6xl mb-4">🔍</div>
          <h3 class="text-2xl font-bold text-white mb-2">No questions found</h3>
          <p class="text-gray-400">Try adjusting your search or filter criteria</p>
        `;
        faqList.appendChild(noResultsMsg);
      }
      noResultsMsg.style.display = 'block';
    } else {
      if (noResultsMsg) {
        noResultsMsg.style.display = 'none';
      }
    }
  }

  setupConfettiEffect() {
    const confettiButtons = document.querySelectorAll('[data-confetti]');

    confettiButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        this.createConfetti(e.clientX, e.clientY);
      });
    });
  }

  createConfetti(x, y) {
    const colors = ['#a855f7', '#ec4899', '#3b82f6', '#10b981', '#f59e0b'];
    const confettiCount = 30;

    for (let i = 0; i < confettiCount; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti-piece';
      confetti.style.left = x + 'px';
      confetti.style.top = y + 'px';
      confetti.style.setProperty('--color', colors[Math.floor(Math.random() * colors.length)]);
      confetti.style.setProperty('--duration', (Math.random() * 0.5 + 0.5) + 's');
      confetti.style.setProperty('--delay', (Math.random() * 0.1) + 's');
      confetti.style.setProperty('--distance', (Math.random() * 200 + 100) + 'px');
      confetti.style.setProperty('--rotation', (Math.random() * 720 - 360) + 'deg');

      document.body.appendChild(confetti);

      setTimeout(() => confetti.remove(), 1500);
    }
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new InteractivePricing();
  });
} else {
  new InteractivePricing();
}
