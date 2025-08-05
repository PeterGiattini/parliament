/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        parliament: {
          blue: '#2563eb',
          purple: '#7c3aed', 
          green: '#059669',
          red: '#dc2626'
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
} 
