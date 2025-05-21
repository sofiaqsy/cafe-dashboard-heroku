/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'coffee': {
          50: '#f9f5f1',
          100: '#e8d8c3',
          200: '#d7bc98',
          300: '#c6a16c',
          400: '#b58540',
          500: '#96732d',
          600: '#8a6023',
          700: '#7d4e1a',
          800: '#613c11',
          900: '#442a08',
        },
      },
    },
  },
  plugins: [],
}
