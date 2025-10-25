/**
 * ================================================
 * ADVANCED CURSOR EFFECTS SYSTEM
 * Professional cursor follower with magnetic attraction
 * ================================================
 */

class AdvancedCursor {
  constructor() {
    this.cursor = null;
    this.cursorDot = null;
    this.trail = [];
    this.mouseX = 0;
    this.mouseY = 0;
    this.cursorX = 0;
    this.cursorY = 0;
    this.magneticElements = [];
    this.isHovering = false;
    this.trailLength = 12;
    
    if (this.isTouchDevice()) return;
    
    this.init();
  }

  isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  }

  init() {
    this.createCursor();
    this.createTrail();
    this.setupEventListeners();
    this.findMagneticElements();
    this.animate();
  }

  createCursor() {
    this.cursor = document.createElement('div');
    this.cursor.className = 'custom-cursor';
    this.cursor.innerHTML = `
      <div class="cursor-ring"></div>
      <div class="cursor-glow"></div>
    `;
    
    this.cursorDot = document.createElement('div');
    this.cursorDot.className = 'custom-cursor-dot';
    
    document.body.appendChild(this.cursor);
    document.body.appendChild(this.cursorDot);
  }

  createTrail() {
    for (let i = 0; i < this.trailLength; i++) {
      const trail = document.createElement('div');
      trail.className = 'cursor-trail';
      trail.style.opacity = (1 - i / this.trailLength) * 0.5;
      trail.style.transform = `scale(${1 - i / this.trailLength * 0.5})`;
      document.body.appendChild(trail);
      this.trail.push({
        element: trail,
        x: 0,
        y: 0
      });
    }
  }

  setupEventListeners() {
    document.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
    });

    document.addEventListener('mouseenter', () => {
      this.cursor.classList.add('active');
      this.cursorDot.classList.add('active');
    });

    document.addEventListener('mouseleave', () => {
      this.cursor.classList.remove('active');
      this.cursorDot.classList.remove('active');
    });

    document.addEventListener('mousedown', () => {
      this.cursor.classList.add('click');
      this.cursorDot.classList.add('click');
    });

    document.addEventListener('mouseup', () => {
      this.cursor.classList.remove('click');
      this.cursorDot.classList.remove('click');
    });

    document.querySelectorAll('a, button, [data-cursor="pointer"]').forEach(el => {
      el.addEventListener('mouseenter', () => {
        this.cursor.classList.add('hover');
        this.cursorDot.classList.add('hover');
      });
      
      el.addEventListener('mouseleave', () => {
        this.cursor.classList.remove('hover');
        this.cursorDot.classList.remove('hover');
      });
    });

    document.querySelectorAll('input, textarea').forEach(el => {
      el.addEventListener('mouseenter', () => {
        this.cursor.classList.add('input');
        this.cursorDot.classList.add('input');
      });
      
      el.addEventListener('mouseleave', () => {
        this.cursor.classList.remove('input');
        this.cursorDot.classList.remove('input');
      });
    });
  }

  findMagneticElements() {
    this.magneticElements = Array.from(
      document.querySelectorAll('[data-magnetic], .btn-primary, .glass-card')
    );
  }

  checkMagneticAttraction() {
    this.magneticElements.forEach(el => {
      const rect = el.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const distance = Math.hypot(
        this.mouseX - centerX,
        this.mouseY - centerY
      );
      
      const magneticRadius = Math.max(rect.width, rect.height) * 0.8;
      
      if (distance < magneticRadius) {
        const pullStrength = 1 - distance / magneticRadius;
        const pullX = (centerX - this.mouseX) * pullStrength * 0.3;
        const pullY = (centerY - this.mouseY) * pullStrength * 0.3;
        
        this.cursorX += pullX;
        this.cursorY += pullY;
        
        this.cursor.classList.add('magnetic');
        return true;
      }
    });
    
    this.cursor.classList.remove('magnetic');
    return false;
  }

  updateTrail() {
    for (let i = this.trail.length - 1; i > 0; i--) {
      this.trail[i].x = this.trail[i - 1].x;
      this.trail[i].y = this.trail[i - 1].y;
    }
    
    this.trail[0].x = this.cursorX;
    this.trail[0].y = this.cursorY;
    
    this.trail.forEach((item, index) => {
      item.element.style.transform = `translate(${item.x}px, ${item.y}px) scale(${1 - index / this.trailLength * 0.5})`;
    });
  }

  animate() {
    const ease = 0.15;
    
    const dx = this.mouseX - this.cursorX;
    const dy = this.mouseY - this.cursorY;
    
    this.cursorX += dx * ease;
    this.cursorY += dy * ease;
    
    this.checkMagneticAttraction();
    
    this.cursor.style.transform = `translate(${this.cursorX}px, ${this.cursorY}px)`;
    this.cursorDot.style.transform = `translate(${this.mouseX}px, ${this.mouseY}px)`;
    
    this.updateTrail();
    
    requestAnimationFrame(() => this.animate());
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new AdvancedCursor();
  });
} else {
  new AdvancedCursor();
}
