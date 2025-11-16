/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./pages/**/*.html",
    "./src/**/*.{html,js}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
        benzin: ['Benzin', 'sans-serif'],
      },
    }
  },
  plugins: [],
}