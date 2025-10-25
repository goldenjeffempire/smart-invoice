/**
 * ===========================================
 * INVOICE FORM - SMART VALIDATIONS & CALCULATIONS
 * Real-time feedback and interactive enhancements
 * ===========================================
 */

class InvoiceFormManager {
  constructor() {
    this.debug = true; // Enable console logging
    this.log('📝 Invoice Form Manager initializing...');
    
    this.form = document.querySelector('form[data-invoice-form]');
    this.lineItems = [];
    this.totals = {
      subtotal: 0,
      tax: 0,
      total: 0
    };
    
    if (this.form) {
      this.log('✅ Form found, setting up...');
      this.init();
    } else {
      this.log('⚠️ No invoice form found on this page');
    }
  }

  log(message, data = null) {
    if (this.debug) {
      const timestamp = new Date().toLocaleTimeString();
      console.log(`[${timestamp}] 📝 InvoiceForm:`, message, data || '');
    }
  }

  init() {
    this.log('🚀 Initializing form features...');
    this.setupRealTimeCalculations();
    this.setupSmartValidation();
    this.setupDynamicLineItems();
    this.setupFormSubmission();
    this.setupAutoSave();
    this.showWelcomeAnimation();
    this.log('✅ All form features ready');
  }

  setupRealTimeCalculations() {
    document.addEventListener('formCalculate', () => {
      this.calculateTotals();
    });

    const quantityInputs = document.querySelectorAll('[data-line-item-quantity]');
    const priceInputs = document.querySelectorAll('[data-line-item-price]');
    const taxInput = document.getElementById('tax_rate');

    [...quantityInputs, ...priceInputs, taxInput].forEach(input => {
      if (input) {
        input.addEventListener('input', () => {
          this.calculateLineItemTotal(input);
          this.calculateTotals();
          this.animateTotalUpdate();
        });

        input.addEventListener('blur', () => {
          this.formatCurrency(input);
        });
      }
    });

    this.calculateTotals();
  }

  calculateLineItemTotal(input) {
    const row = input.closest('[data-line-item-row]');
    if (!row) return;

    const quantityInput = row.querySelector('[data-line-item-quantity]');
    const priceInput = row.querySelector('[data-line-item-price]');
    const totalElement = row.querySelector('[data-line-item-total]');

    if (quantityInput && priceInput && totalElement) {
      const quantity = parseFloat(quantityInput.value) || 0;
      const price = parseFloat(priceInput.value) || 0;
      const total = quantity * price;

      totalElement.textContent = this.formatMoney(total);
      
      totalElement.classList.add('success-pulse');
      setTimeout(() => totalElement.classList.remove('success-pulse'), 600);
    }
  }

  calculateTotals() {
    const rows = document.querySelectorAll('[data-line-item-row]');
    let subtotal = 0;

    rows.forEach(row => {
      const quantityInput = row.querySelector('[data-line-item-quantity]');
      const priceInput = row.querySelector('[data-line-item-price]');
      
      if (quantityInput && priceInput) {
        const quantity = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        subtotal += quantity * price;
      }
    });

    const taxInput = document.getElementById('tax_rate');
    const taxRate = taxInput ? parseFloat(taxInput.value) || 0 : 0;
    const tax = (subtotal * taxRate) / 100;
    const total = subtotal + tax;

    this.totals = { subtotal, tax, total };
    
    this.log('💰 Totals calculated', { subtotal, tax, total });

    this.updateTotalDisplays();
  }

  updateTotalDisplays() {
    const subtotalEl = document.querySelector('[data-display-subtotal]');
    const taxEl = document.querySelector('[data-display-tax]');
    const totalEl = document.querySelector('[data-display-total]');

    if (subtotalEl) {
      this.animateValue(subtotalEl, this.totals.subtotal);
    }
    if (taxEl) {
      this.animateValue(taxEl, this.totals.tax);
    }
    if (totalEl) {
      this.animateValue(totalEl, this.totals.total);
    }
  }

  animateValue(element, targetValue) {
    const currentValue = parseFloat(element.dataset.currentValue) || 0;
    const duration = 500;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const easedProgress = this.easeOutCubic(progress);
      const value = currentValue + (targetValue - currentValue) * easedProgress;
      
      element.textContent = this.formatMoney(value);
      element.dataset.currentValue = value;

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        element.textContent = this.formatMoney(targetValue);
        element.dataset.currentValue = targetValue;
      }
    };

    requestAnimationFrame(animate);
  }

  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  animateTotalUpdate() {
    const totalContainer = document.querySelector('[data-totals-container]');
    if (totalContainer) {
      totalContainer.classList.add('hover-scale-sm');
      setTimeout(() => totalContainer.classList.remove('hover-scale-sm'), 300);
    }
  }

  formatCurrency(input) {
    if (!input.value) return;
    
    const value = parseFloat(input.value);
    if (!isNaN(value)) {
      input.value = value.toFixed(2);
    }
  }

  formatMoney(value) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }

  setupSmartValidation() {
    const requiredInputs = this.form.querySelectorAll('[required]');
    
    requiredInputs.forEach(input => {
      const formGroup = input.closest('.form-group') || this.createFormGroup(input);
      
      input.addEventListener('blur', () => {
        this.validateField(input, formGroup);
      });

      input.addEventListener('input', () => {
        if (formGroup.classList.contains('invalid')) {
          this.validateField(input, formGroup);
        }
      });
    });

    const emailInputs = this.form.querySelectorAll('[type="email"]');
    emailInputs.forEach(input => {
      input.dataset.validate = 'email';
    });

    const numberInputs = this.form.querySelectorAll('[type="number"]');
    numberInputs.forEach(input => {
      input.dataset.validate = 'number';
    });
  }

  createFormGroup(input) {
    const wrapper = document.createElement('div');
    wrapper.className = 'form-group';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    return wrapper;
  }

  validateField(input, formGroup) {
    const value = input.value.trim();
    let isValid = true;
    let message = '';

    if (input.hasAttribute('required') && !value) {
      isValid = false;
      message = 'This field is required';
    } else if (input.type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      isValid = emailRegex.test(value);
      message = isValid ? '' : 'Please enter a valid email address';
    } else if (input.type === 'number' && value) {
      const numberValue = parseFloat(value);
      if (isNaN(numberValue)) {
        isValid = false;
        message = 'Please enter a valid number';
      } else if (input.min && numberValue < parseFloat(input.min)) {
        isValid = false;
        message = `Value must be at least ${input.min}`;
      }
    }

    this.updateFieldValidation(formGroup, isValid, message);
  }

  updateFieldValidation(formGroup, isValid, message) {
    let feedback = formGroup.querySelector('.validation-feedback');
    
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.className = 'validation-feedback text-sm text-red-400 mt-1';
      formGroup.appendChild(feedback);
    }

    if (isValid) {
      formGroup.classList.remove('invalid');
      formGroup.classList.add('valid');
      feedback.style.maxHeight = '0';
      feedback.style.opacity = '0';
    } else if (message) {
      formGroup.classList.remove('valid');
      formGroup.classList.add('invalid');
      feedback.textContent = message;
      feedback.style.maxHeight = '40px';
      feedback.style.opacity = '1';
      
      formGroup.querySelector('input, textarea, select')?.classList.add('error-shake');
      setTimeout(() => {
        formGroup.querySelector('input, textarea, select')?.classList.remove('error-shake');
      }, 500);
    }
  }

  setupDynamicLineItems() {
    const addButton = document.querySelector('[data-add-line-item]');
    const removeButtons = document.querySelectorAll('[data-remove-line-item]');

    if (addButton) {
      addButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.addLineItem();
      });
    }

    removeButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.removeLineItem(button);
      });
    });
  }

  addLineItem() {
    const container = document.querySelector('[data-line-items-container]');
    if (!container) return;

    const templateRow = container.querySelector('[data-line-item-row]');
    if (!templateRow) return;

    const newRow = templateRow.cloneNode(true);
    
    newRow.querySelectorAll('input').forEach(input => {
      input.value = '';
    });
    
    newRow.classList.add('bounce-in');
    container.appendChild(newRow);

    const removeButton = newRow.querySelector('[data-remove-line-item]');
    if (removeButton) {
      removeButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.removeLineItem(removeButton);
      });
    }

    this.setupRealTimeCalculations();
    
    if (window.AnimationEngine) {
      window.AnimationEngine.showToast('Line item added', 'success');
    }
  }

  removeLineItem(button) {
    const row = button.closest('[data-line-item-row]');
    const container = document.querySelector('[data-line-items-container]');
    
    if (row && container && container.querySelectorAll('[data-line-item-row]').length > 1) {
      row.style.opacity = '0';
      row.style.transform = 'scale(0.8)';
      row.style.transition = 'all 0.3s ease';
      
      setTimeout(() => {
        row.remove();
        this.calculateTotals();
        
        if (window.AnimationEngine) {
          window.AnimationEngine.showToast('Line item removed', 'info');
        }
      }, 300);
    }
  }

  setupFormSubmission() {
    this.form.addEventListener('submit', (e) => {
      const submitButton = this.form.querySelector('[type="submit"]');
      
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add('btn-loading');
        
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = `
          <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="ml-2">Saving...</span>
        `;
      }
    });
  }

  setupAutoSave() {
    let saveTimeout;
    const inputs = this.form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      input.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
          this.showAutoSaveIndicator();
        }, 2000);
      });
    });
  }

  showAutoSaveIndicator() {
    const indicator = document.getElementById('autosave-indicator');
    if (indicator) {
      indicator.classList.remove('opacity-0');
      indicator.classList.add('opacity-100');
      
      setTimeout(() => {
        indicator.classList.remove('opacity-100');
        indicator.classList.add('opacity-0');
      }, 2000);
    }
  }

  showWelcomeAnimation() {
    const mainCard = this.form.closest('.glass-card, .glass');
    if (mainCard) {
      mainCard.classList.add('page-enter');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new InvoiceFormManager();
});
