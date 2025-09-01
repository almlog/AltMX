/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'altmx-blue': '#00d4ff',
        'altmx-dark': '#0a0a0a',
        'altmx-gray': '#1a1a1a',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}