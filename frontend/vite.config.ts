import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/


export default defineConfig(({ mode }) => {
    const envDirectory = path.resolve(__dirname, '../')
     const env = loadEnv(mode, envDirectory, '')

  return {
        envDir: envDirectory,

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
          target: env.VITE_API_BASE_URL || 'http://localhost:8000', 
          changeOrigin: true,
        },
      },
    },
  }
})
