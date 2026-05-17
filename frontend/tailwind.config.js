/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        theme: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          bg: 'var(--bg-primary)',
          card: 'var(--bg-secondary)',
          border: 'var(--border-color)',
          accent: 'var(--accent)',
          'accent-hover': 'var(--accent-hover)',
        }
      },
      backgroundColor: {
        'theme-base': 'var(--bg-primary)',
        'theme-card': 'var(--bg-secondary)',
        'theme-input': 'var(--bg-tertiary)',
      },
      borderColor: {
        'theme-base': 'var(--border-color)',
      }
    },
  },
  plugins: [],
}
