import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        mist: "#f4f7f9",
        pine: "#1e6f5c",
        signal: "#d97706"
      }
    }
  },
  plugins: []
};

export default config;

