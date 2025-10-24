/**
 * ===========================================
 * CHART ANIMATIONS & VISUALIZATIONS
 * Animated data visualization system
 * ===========================================
 */

class ChartAnimator {
  constructor() {
    this.charts = new Map();
    this.init();
  }

  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.setupStatCards();
    this.setupProgressBars();
    this.setupMetricAnimations();
  }

  setupStatCards() {
    const statCards = document.querySelectorAll('[data-stat-card]');
    if (!statCards.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateStatCard(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });

    statCards.forEach(card => observer.observe(card));
  }

  animateStatCard(card) {
    const valueElement = card.querySelector('[data-value]');
    const chartElement = card.querySelector('[data-chart]');
    
    if (valueElement) {
      const targetValue = parseFloat(valueElement.dataset.value);
      const isCurrency = valueElement.dataset.currency === 'true';
      const isPercentage = valueElement.dataset.percentage === 'true';
      
      this.animateValue(valueElement, 0, targetValue, 2000, {
        isCurrency,
        isPercentage
      });
    }

    if (chartElement) {
      this.animateMiniChart(chartElement);
    }

    card.classList.add('stat-revealed');
  }

  animateValue(element, start, end, duration, options = {}) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const animate = () => {
      current += increment;
      if ((increment > 0 && current < end) || (increment < 0 && current > end)) {
        this.updateValueDisplay(element, current, options);
        requestAnimationFrame(animate);
      } else {
        this.updateValueDisplay(element, end, options);
      }
    };

    requestAnimationFrame(animate);
  }

  updateValueDisplay(element, value, options) {
    let displayValue = Math.abs(value).toFixed(options.decimals || 0);
    
    if (options.isCurrency) {
      displayValue = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    } else if (options.isPercentage) {
      displayValue = `${Math.round(value)}%`;
    } else {
      displayValue = Math.round(value).toLocaleString();
    }

    element.textContent = displayValue;
  }

  animateMiniChart(chartElement) {
    const bars = chartElement.querySelectorAll('[data-bar]');
    bars.forEach((bar, index) => {
      setTimeout(() => {
        const height = bar.dataset.bar;
        bar.style.height = height;
        bar.classList.add('bar-animated');
      }, index * 100);
    });
  }

  setupProgressBars() {
    const progressBars = document.querySelectorAll('[data-progress]');
    if (!progressBars.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateProgressBar(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    progressBars.forEach(bar => observer.observe(bar));
  }

  animateProgressBar(progressElement) {
    const targetWidth = parseFloat(progressElement.dataset.progress);
    const fill = progressElement.querySelector('.progress-fill');
    
    if (fill) {
      setTimeout(() => {
        fill.style.width = `${targetWidth}%`;
        fill.classList.add('progress-animated');
      }, 100);
    }
  }

  setupMetricAnimations() {
    const metrics = document.querySelectorAll('[data-metric]');
    metrics.forEach(metric => {
      metric.addEventListener('mouseenter', () => {
        metric.classList.add('metric-hover');
      });

      metric.addEventListener('mouseleave', () => {
        metric.classList.remove('metric-hover');
      });
    });
  }

  createSparkline(container, data, options = {}) {
    const width = options.width || 100;
    const height = options.height || 30;
    const color = options.color || '#a855f7';

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    }).join(' ');

    container.innerHTML = `
      <svg width="${width}" height="${height}" class="sparkline">
        <polyline
          fill="none"
          stroke="${color}"
          stroke-width="2"
          points="${points}"
          class="sparkline-line"
        />
      </svg>
    `;

    const line = container.querySelector('.sparkline-line');
    const length = line.getTotalLength();
    
    line.style.strokeDasharray = length;
    line.style.strokeDashoffset = length;

    setTimeout(() => {
      line.style.strokeDashoffset = '0';
    }, 100);
  }

  animateDonutChart(container, percentage, options = {}) {
    const size = options.size || 120;
    const strokeWidth = options.strokeWidth || 10;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (percentage / 100) * circumference;

    container.innerHTML = `
      <svg width="${size}" height="${size}" class="donut-chart">
        <circle
          cx="${size / 2}"
          cy="${size / 2}"
          r="${radius}"
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          stroke-width="${strokeWidth}"
        />
        <circle
          cx="${size / 2}"
          cy="${size / 2}"
          r="${radius}"
          fill="none"
          stroke="url(#gradient)"
          stroke-width="${strokeWidth}"
          stroke-dasharray="${circumference}"
          stroke-dashoffset="${circumference}"
          stroke-linecap="round"
          transform="rotate(-90 ${size / 2} ${size / 2})"
          class="donut-progress"
        />
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#a855f7;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
          </linearGradient>
        </defs>
        <text x="${size / 2}" y="${size / 2}" text-anchor="middle" dy="0.3em" class="donut-text">
          ${Math.round(percentage)}%
        </text>
      </svg>
    `;

    setTimeout(() => {
      const circle = container.querySelector('.donut-progress');
      circle.style.strokeDashoffset = offset;
    }, 100);
  }
}

const chartAnimator = new ChartAnimator();
window.ChartAnimator = chartAnimator;
