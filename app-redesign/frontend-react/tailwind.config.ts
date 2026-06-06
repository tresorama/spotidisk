import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        spotify: '#1DB954',
        youtube: '#FF0000',
        background: '#1a1a1a',
        surface: '#2a2a2a',
        'surface-light': '#3a3a3a',
      },
    },
  },
  plugins: [],
}

export default config
