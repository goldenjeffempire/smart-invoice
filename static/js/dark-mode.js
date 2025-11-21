/**
 * Dark Mode Toggle for Smart Invoice
 * Implements theme switching with localStorage persistence
 */

class DarkModeManager {
    constructor() {
        this.darkModeKey = 'smartinvoice-dark-mode';
        this.init();
    }

    init() {
        const savedTheme = localStorage.getItem(this.darkModeKey);
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        const isDark = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);
        
        if (isDark) {
            this.enableDarkMode();
        } else {
            this.enableLightMode();
        }
        
        this.setupToggleButton();
        
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(this.darkModeKey)) {
                if (e.matches) {
                    this.enableDarkMode();
                } else {
                    this.enableLightMode();
                }
            }
        });
    }

    enableDarkMode() {
        document.documentElement.classList.add('dark');
        localStorage.setItem(this.darkModeKey, 'dark');
        this.updateToggleButton(true);
    }

    enableLightMode() {
        document.documentElement.classList.remove('dark');
        localStorage.setItem(this.darkModeKey, 'light');
        this.updateToggleButton(false);
    }

    toggle() {
        if (document.documentElement.classList.contains('dark')) {
            this.enableLightMode();
        } else {
            this.enableDarkMode();
        }
    }

    setupToggleButton() {
        const toggleButton = document.getElementById('dark-mode-toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', () => this.toggle());
        }
    }

    updateToggleButton(isDark) {
        const toggleButton = document.getElementById('dark-mode-toggle');
        if (toggleButton) {
            const sunIcon = toggleButton.querySelector('.sun-icon');
            const moonIcon = toggleButton.querySelector('.moon-icon');
            
            if (sunIcon && moonIcon) {
                if (isDark) {
                    sunIcon.classList.remove('hidden');
                    moonIcon.classList.add('hidden');
                } else {
                    sunIcon.classList.add('hidden');
                    moonIcon.classList.remove('hidden');
                }
            }
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new DarkModeManager();
    });
} else {
    new DarkModeManager();
}
