/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        pokemon: {
          red: '#EE1515',
          blue: '#3B4CCA',
          yellow: '#FFDE00',
          gold: '#B3A125',
        },
        grass: '#78C850',
        fire: '#F08030',
        water: '#6890F0',
        lightning: '#F8D030',
        psychic: '#F85888',
        fighting: '#C03028',
        darkness: '#705848',
        metal: '#B8B8D0',
        dragon: '#7038F8',
        colorless: '#A8A878',
        fairy: '#EE99AC',
      },
    },
  },
  plugins: [],
};
