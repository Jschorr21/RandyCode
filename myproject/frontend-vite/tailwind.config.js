/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
              brand: {
                primary: "#1D4ED8",   // blue-600
                hover: "#1E40AF",     // blue-700
                light: "#DBEAFE",     // blue-100
                dark: "#172554",      // blue-900
              },
              gray: {
                border: "#D1D5DB",    // gray-300
                background: "#F9FAFB",// gray-50
              },
            },
          },
    },
    plugins: [],
  };