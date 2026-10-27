/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          deep: '#05060f',
          panel: '#0c0f1f',
          raised: '#11152a',
        },
        glass: {
          fill: 'rgba(255,255,255,0.045)',
          fillhover: 'rgba(255,255,255,0.07)',
          border: 'rgba(255,255,255,0.09)',
        },
        accent: {
          blue: '#4d7fff',
          purple: '#a56bff',
          teal: '#2dd9c0',
          amber: '#f5a623',
        },
        text: {
          hi: '#f2f4fb',
          lo: '#a3abc2',
          faint: '#6b7390',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #4d7fff 0%, #a56bff 55%, #2dd9c0 100%)',
        'brand-gradient-soft': 'linear-gradient(135deg, rgba(77,127,255,0.18), rgba(165,107,255,0.18) 55%, rgba(45,217,192,0.18) 100%)',
      },
      boxShadow: {
        glow: '0 0 40px rgba(165,107,255,0.15)',
        'glow-sm': '0 0 20px rgba(77,127,255,0.18)',
      },
      borderRadius: {
        xl2: '1.5rem',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-14px)' },
        },
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '50%': { transform: 'translateY(-10px) rotate(3deg)' },
        },
        fadeUp: {
          '0%': { opacity: 0, transform: 'translateY(16px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: 0.5 },
          '50%': { opacity: 1 },
        },
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        floatSlow: 'floatSlow 8s ease-in-out infinite',
        fadeUp: 'fadeUp 0.6s ease-out both',
        pulseGlow: 'pulseGlow 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
