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
        'altmx-pink': '#ff0080',
        'altmx-green': '#00ff88',
        'altmx-yellow': '#ffff00',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'cyberpunk-pulse': 'cyberpunk-pulse 2s ease-in-out infinite',
        'cyberpunk-glow': 'cyberpunk-glow 1.5s ease-in-out infinite alternate',
        'cyberpunk-scan': 'cyberpunk-scan 3s linear infinite',
        'cyberpunk-fade-in': 'cyberpunk-fade-in 1s ease-out',
      },
      keyframes: {
        'cyberpunk-pulse': {
          '0%, 100%': { opacity: 0.7, transform: 'scale(1)' },
          '50%': { opacity: 1, transform: 'scale(1.05)' },
        },
        'cyberpunk-glow': {
          '0%': { boxShadow: '0 0 5px #00d4ff, 0 0 10px #00d4ff' },
          '100%': { boxShadow: '0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 30px #00d4ff' },
        },
        'cyberpunk-scan': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        'cyberpunk-fade-in': {
          '0%': { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        'cyberpunk-glow-blue': '0 0 10px #00d4ff, 0 0 20px #00d4ff',
        'cyberpunk-glow-pink': '0 0 10px #ff0080, 0 0 20px #ff0080',
        'cyberpunk-glow-green': '0 0 10px #00ff88, 0 0 20px #00ff88',
      }
    },
  },
  plugins: [],
}