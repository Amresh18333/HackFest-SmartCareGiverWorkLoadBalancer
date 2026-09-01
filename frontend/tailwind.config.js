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
        'brand-accent': '#E8918A',
        'text-primary': '#3A3542',
        'text-muted': '#8B8494',
        'risk-low': '#7FA98D',
        'risk-medium': '#E8A94C',
        'risk-high': '#D2685F',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px rgba(58, 53, 66, 0.08), 0 4px 12px rgba(58, 53, 66, 0.05)',
        'card-hover': '0 4px 16px rgba(58, 53, 66, 0.1), 0 8px 24px rgba(58, 53, 66, 0.06)',
      },
      borderRadius: {
        'card': '12px',
      },
    },
  },
  plugins: [],
}