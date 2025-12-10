/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2D3748', // Dark gray for primary elements
        secondary: '#4A5568', // Lighter gray for secondary elements
        accent: '#38A169', // Green for accents/buttons
        'accent-dark': '#2F855A', // Darker green for hover states
        background: '#F7FAFC', // Light background
        text: '#1A202C', // Dark text
        'text-light': '#718096', // Lighter text
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}