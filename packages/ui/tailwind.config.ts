import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        gore: {
          brand: "#003366", // Azul institucional serio
          secondary: "#D4AF37", // Dorado/Ocre institucional
          success: "#10B981", // TDE Cumplimiento
          warning: "#F59E0B", // TDE Alerta
          error: "#EF4444", // TDE Error/Rechazo
          info: "#3B82F6", // TDE Info
          background: "#F3F4F6", // Gris muy claro fondo
          surface: "#FFFFFF",
          text: "#1F2937",
          "text-muted": "#6B7280",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
