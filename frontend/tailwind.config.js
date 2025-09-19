/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
      colors: {
        'tier-bronze': '#cd7f32',
        'tier-silver': '#c0c0c0', 
        'tier-gold': '#ffd700',
        'tier-platinum': '#00ff9f',
        'tier-diamond': '#85d8ff',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      }
    },
  },
  plugins: [],
}