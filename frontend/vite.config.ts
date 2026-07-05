import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // The third parameter '' loads all env variables regardless of the VITE_ prefix.
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: true, 
    port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000', 
          changeOrigin: true,
        },
      },
    },
  }
})
