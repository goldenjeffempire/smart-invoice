# Smart Invoice

## Overview
Smart Invoice is an enterprise-grade Django-based invoice management platform for freelancers, startups, and growing businesses. It features a modern, professional UI/UX with advanced animations and glassmorphism design to attract businesses. The platform provides comprehensive invoice management, secure payment processing via Paystack, advanced analytics and reporting, and robust client management. Its core purpose is to streamline invoicing, payment collection, and financial tracking for businesses.

## Recent Changes (October 2025)
**Production-Ready Enhancements:**
- ✅ Implemented production-ready settings architecture (base, dev, prod configurations)
- ✅ Enhanced authentication system with modern glassmorphism UI for login/signup
- ✅ Built complete client management system (CRUD operations with search/filter)
- ✅ Configured deployment infrastructure for Render (Gunicorn, build scripts, caching)
- ✅ Optimized security settings for production (HSTS, SSL, secure cookies)
- ✅ Fixed critical bugs in client views and status update logic

## User Preferences
- The user wants iterative development.
- The user prefers clear and concise explanations.
- The user wants to be asked before making major changes.
- The user wants the agent to focus on creating production-ready, enterprise-grade solutions.
- The user wants the agent to prioritize modern UI/UX design with advanced animations and glassmorphism.
- The user wants the agent to use a purple/pink gradient aesthetic for the design.
- The user wants the agent to ensure all static files are properly collected and optimized.
- The user wants the agent to ensure all security headers are configured and production settings are separated from development.
- The user wants the agent to use PostgreSQL for production and SQLite for local development.

## System Architecture
**UI/UX Decisions:**
The application features a fully modernized, ultra-professional UI/UX design with advanced animations, interactive elements, and enterprise-grade polish. Key design principles include glassmorphism, a purple/pink gradient aesthetic, and a dark theme. Specific UI/UX features include:
- **Landing Page:** Parallax effects, smooth scroll animations, interactive statistics, professional testimonials, trust badges, animated background orbs, and mobile-responsive navigation.
- **Invoice Dashboard:** Card-based grid layout with hover effects, real-time stats cards, advanced search/filter, skeleton loading, and micro-interactions.
- **Invoice Form:** Multi-step wizard interface with progress tracking, real-time calculation/validation, live preview, and smooth step transitions.
- **Invoice Detail Page:** Timeline view of invoice lifecycle, action cards for download/email/WhatsApp, share modal, and gradient status badges.
- **Global Enhancements:** Professional footer, scroll progress bar, ripple effects on buttons, gradient text animations, and smooth page transitions.

**Technical Implementations & Design System:**
- **Backend Framework:** Django 5.2.7.
- **Styling:** TailwindCSS with a custom, comprehensive configuration for an extended color palette (primary purple, secondary pink), advanced typography, custom spacing, glow shadow system, and an advanced animation library (fade-in, slide, scale, float, pulse-glow, shimmer, gradient-shift).
- **CSS Architecture:** Modernized input.css using design tokens (CSS custom properties), a robust glassmorphism system (.glass, .glass-strong, .glass-subtle, .glass-card, .glass-nav), a versatile button component system (.btn-primary, .btn-outline, .btn-ghost with size variants), styled form components, and a status badge system.
- **Animation Utilities:** .animated-bg, .bg-orb, .scroll-reveal, .ripple-effect, .hover-lift, .hover-glow, .skeleton for dynamic and interactive user experience.
- **Accessibility:** WCAG-compliant focus rings, optimized contrast ratios, and prefers-reduced-motion support.
- **Responsiveness:** Mobile-first approach.
- **Authentication:** Django's built-in authentication with user signup, login, logout, login-required decorators, user-specific invoice filtering, and dynamic navigation.
- **PDF Generation:** Utilizes xhtml2pdf, reportlab, and pycairo.
- **Static Files:** WhiteNoise for efficient serving of collected and compressed static assets.

**Feature Specifications:**
- **Invoice Management:** Create, update, track invoices (draft, sent, paid, overdue, cancelled) with multi-line item support.
- **Payment Processing:** Paystack integration with transaction verification, webhook support, and detailed transaction tracking via `PaymentTransaction` model.
- **Analytics & Reporting:** `AnalyticsService` for revenue metrics, trends, client statistics, payment statistics, monthly trends, and CSV export functionality.
- **Client Management:** `Client` model for comprehensive customer information, linked to invoices for tracking.
- **Multi-currency Support:** USD, EUR, GBP, NGN, CAD, AUD.
- **Payment Terms:** Flexible options (immediate, net 15/30/60/90).

**System Design Choices:**
- **Database:** PostgreSQL for production, SQLite for development.
- **Secrets Management:** Environment variables and Replit Secrets for sensitive data (e.g., Paystack API keys).
- **Deployment:** Optimized for Render with `render.yaml`, `runtime.txt`, and production build configurations.
- **Security:** HSTS, SSL, CSRF headers configured.
- **Performance:** Gunicorn with optimal worker settings, database connection pooling, and indexed database models (`Invoice`, `PaymentTransaction`, `Client`).

## External Dependencies
- **Database:** PostgreSQL (production), SQLite (development)
- **Payment Gateway:** Paystack API (for online payment processing and webhooks)
- **PDF Generation Libraries:** xhtml2pdf, reportlab, pycairo
- **Styling Framework:** TailwindCSS
- **Static File Serving:** WhiteNoise
- **Email:** Django SMTP backend (configured for production)
- **WhatsApp Integration:** Twilio API