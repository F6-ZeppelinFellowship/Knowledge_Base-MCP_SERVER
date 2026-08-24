/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#0B1120',
          900: '#0F172A',
          800: '#161F32',
          700: '#22304A',
        },
        match: {
          high: '#10B981',
          mid: '#F59E0B',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        glass: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      backgroundImage: {
        'grid-glow':
          'radial-gradient(circle at 20% 0%, rgba(16,185,129,0.08), transparent 40%), radial-gradient(circle at 80% 100%, rgba(245,158,11,0.06), transparent 40%)',
      },
      keyframes: {
        scan: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        pulseRing: {
          '0%': { transform: 'scale(0.9)', opacity: '0.6' },
          '100%': { transform: 'scale(1.6)', opacity: '0' },
        },
      },
      animation: {
        scan: 'scan 1.8s ease-in-out infinite',
        'pulse-ring': 'pulseRing 1.6s cubic-bezier(0.4,0,0.6,1) infinite',
      },
    },
  },
  plugins: [],
}
