/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Design system tokens
        bg: '#F7F5FA',
        surface: '#FFFFFF',
        'brand-primary': '#8B7BA8',
        'brand-primary-light': '#A89BC8',
        'brand-accent': '#E8918A',
        'brand-accent-light': '#F0A8A0',
        'text-primary': '#3A3542',
        'text-secondary': '#5A5462',
        'text-muted': '#8B8494',
        'risk-low': '#7FA98D',
        'risk-low-light': '#A8C9B8',
        'risk-medium': '#E8A94C',
        'risk-medium-light': '#F0C98A',
        'risk-high': '#D2685F',
        'risk-high-light': '#E0A098',
        'border-light': '#E8E4ED',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px rgba(58, 53, 66, 0.08), 0 4px 12px rgba(58, 53, 66, 0.05)',
        'card-hover': '0 4px 16px rgba(58, 53, 66, 0.1), 0 8px 24px rgba(58, 53, 66, 0.06)',
        'card-xl': '0 8px 24px rgba(58, 53, 66, 0.1), 0 16px 40px rgba(58, 53, 66, 0.12)',
      },
      borderRadius: {
        'card': '12px',
        'xl': '16px',
        '2xl': '20px',
      },
      animation: {
        'fade-in': 'fade-in 0.4s ease-out forwards',
        'slide-in-right': 'slide-in-right 0.4s ease-out forwards',
        'slide-in-left': 'slide-in-left 0.4s ease-out forwards',
        'scale-in': 'scale-in 0.3s ease-out forwards',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s infinite',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'slide-in-left': {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        'shimmer': {
          '0%': { 'background-position': '-200% 0' },
          '100%': { 'background-position': '200% 0' },
        },
      },
    },
  },
  plugins: [],
}