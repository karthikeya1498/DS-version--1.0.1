import { defineConfig } from "vite";

/**
 * Vite development configuration for the OPTIMA-X dashboard.
 * Author: Karthikeya
 */
export default defineConfig({
  server: {
    allowedHosts: [".manus.computer", "localhost"],
  },
});
