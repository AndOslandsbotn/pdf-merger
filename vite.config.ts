import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Project Pages: https://<user>.github.io/pdf-merger/
export default defineConfig({
  plugins: [react()],
  base: "/pdf-merger/",
});
