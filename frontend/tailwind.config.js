/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        slate: {
          950: "#05060A",
        },
        night: "#080b12",
        emerald: {
          400: "#2CFECB",
          500: "#14F195",
        },
        cyan: {
          400: "#3ABEF9",
          500: "#1EA7FF",
        },
        accent: "#6F7DFF",
      },
      fontFamily: {
        sans: ["'Inter'", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 10px 45px rgba(20, 241, 149, 0.25)",
      },
    },
  },
  plugins: [],
};
