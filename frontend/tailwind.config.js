/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        'display': ['Playfair Display', 'Georgia', 'serif'],
        'body': ['Source Sans 3', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      colors: {
        'ink': {
          50: '#f7f7f5',
          100: '#eeeee9',
          200: '#ddddd3',
          300: '#c5c4b5',
          400: '#a9a793',
          500: '#94917a',
          600: '#87836d',
          700: '#716d5b',
          800: '#5e5b4d',
          900: '#4d4b40',
          950: '#292821',
        },
        'sage': {
          50: '#f4f7f4',
          100: '#e3ebe3',
          200: '#c8d7c8',
          300: '#a1b9a1',
          400: '#769576',
          500: '#567856',
          600: '#446044',
          700: '#384d38',
          800: '#2f3f2f',
          900: '#283428',
          950: '#121b12',
        },
        'amber': {
          50: '#fefbec',
          100: '#fcf4cb',
          200: '#f9e793',
          300: '#f5d55a',
          400: '#f2c32e',
          500: '#eba519',
          600: '#cf7e12',
          700: '#ac5a13',
          800: '#8c4716',
          900: '#733b15',
          950: '#421d07',
        },
        'coral': {
          50: '#fef3f2',
          100: '#fee4e2',
          200: '#fececa',
          300: '#fcaba4',
          400: '#f87c71',
          500: '#ef5544',
          600: '#dc3626',
          700: '#b92a1c',
          800: '#99261b',
          900: '#7f261d',
          950: '#450f0a',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'bounce-light': 'bounceLight 1s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        bounceLight: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
    },
  },
  plugins: [],
}
