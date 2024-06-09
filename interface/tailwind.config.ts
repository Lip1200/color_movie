import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}", // Ensure this matches your actual paths
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      colors: {
        primary: '#4CAF50', // Couleur primaire pour les boutons
        secondary: '#FF5722', // Couleur secondaire pour les boutons
        highlight: '#FFFF00', // Couleur de surlignement
      },
    },
  },
  plugins: [],
};

export default config;
