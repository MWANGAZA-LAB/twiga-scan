/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bitcoin: '#f7931a',
        'bitcoin-dark': '#181818',
        'bitcoin-glow': '#ffb347',
      },
      boxShadow: {
        'bitcoin': '0 0 24px 4px #f7931a55',
      }
    },
  },
  plugins: [],
}

