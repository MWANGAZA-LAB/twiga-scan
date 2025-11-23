// Tailwind CSS config - Enhanced Responsive Design System
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    // Custom Responsive Breakpoints
    screens: {
      'xs': '475px',     // Small phones landscape
      'sm': '640px',     // Tablets portrait
      'md': '768px',     // Tablets landscape
      'lg': '1024px',    // Desktop
      'xl': '1280px',    // Large desktop
      '2xl': '1536px',   // Extra large
      // Custom breakpoints
      'tablet': '640px',
      'laptop': '1024px',
      'desktop': '1280px',
      // Height-based breakpoints for landscape detection
      'tall': {'raw': '(min-height: 800px)'},
      'short': {'raw': '(max-height: 600px)'},
    },
    extend: {
      colors: {
        bitcoin: '#f7931a',
        'bitcoin-dark': '#181818',
        'bitcoin-glow': '#ffb347',
        'bitcoin-orange': '#ff9500',
        'lightning-blue': '#00c3ff',
      },
      boxShadow: {
        'bitcoin': '0 0 24px 4px #f7931a55',
        'touch': '0 2px 8px rgba(0, 0, 0, 0.15)',
        'touch-active': '0 1px 4px rgba(0, 0, 0, 0.2)',
      },
      // Fluid Spacing Scale
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
        '18': '4.5rem',
        '88': '22rem',
        '100': '25rem',
        '112': '28rem',
        '128': '32rem',
      },
      // Fluid Typography
      fontSize: {
        'fluid-xs': 'clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)',
        'fluid-sm': 'clamp(0.875rem, 0.8rem + 0.35vw, 1rem)',
        'fluid-base': 'clamp(1rem, 0.95rem + 0.5vw, 1.125rem)',
        'fluid-lg': 'clamp(1.125rem, 1rem + 0.75vw, 1.5rem)',
        'fluid-xl': 'clamp(1.5rem, 1.2rem + 1.5vw, 2.5rem)',
        'fluid-2xl': 'clamp(2rem, 1.5rem + 2.5vw, 4rem)',
        'fluid-3xl': 'clamp(2.5rem, 2rem + 3vw, 5rem)',
      },
      // Touch-Friendly Sizing
      minHeight: {
        'touch': '44px',
        'touch-comfortable': '48px',
        'touch-large': '56px',
      },
      minWidth: {
        'touch': '44px',
        'touch-comfortable': '48px',
        'touch-large': '56px',
      },
      // Aspect Ratios
      aspectRatio: {
        'square': '1',
        'video': '16/9',
        'portrait': '3/4',
        'ultrawide': '21/9',
      },
      // Animation & Transitions
      transitionDuration: {
        '250': '250ms',
        '350': '350ms',
      },
      // Container Queries
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '1.5rem',
          lg: '2rem',
          xl: '3rem',
          '2xl': '4rem',
        },
      },
      // Z-Index Scale
      zIndex: {
        '100': '100',
        '200': '200',
        '300': '300',
        '400': '400',
        '500': '500',
      },
      // Grid Template Columns (responsive)
      gridTemplateColumns: {
        'auto-fit': 'repeat(auto-fit, minmax(0, 1fr))',
        'auto-fill': 'repeat(auto-fill, minmax(0, 1fr))',
        'auto-fit-xs': 'repeat(auto-fit, minmax(200px, 1fr))',
        'auto-fit-sm': 'repeat(auto-fit, minmax(250px, 1fr))',
        'auto-fit-md': 'repeat(auto-fit, minmax(300px, 1fr))',
        'auto-fit-lg': 'repeat(auto-fit, minmax(350px, 1fr))',
      },
      // Line Clamp (for text truncation)
      lineClamp: {
        7: '7',
        8: '8',
        9: '9',
        10: '10',
      },
    },
  },
  plugins: [
    // Custom plugin for touch-action utilities
    function({ addUtilities }) {
      const touchUtilities = {
        '.touch-manipulation': {
          'touch-action': 'manipulation',
        },
        '.touch-none': {
          'touch-action': 'none',
        },
        '.touch-pan-x': {
          'touch-action': 'pan-x',
        },
        '.touch-pan-y': {
          'touch-action': 'pan-y',
        },
        // Disable tap highlight on mobile
        '.tap-transparent': {
          '-webkit-tap-highlight-color': 'transparent',
        },
      };
      addUtilities(touchUtilities);
    },
  ],
}

