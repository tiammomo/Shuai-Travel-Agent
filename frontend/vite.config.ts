import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 使用IPv4地址避免IPv6解析问题
        changeOrigin: true,
        secure: false,
        ws: true,  // 支持WebSocket（用于SSE）
      }
    }
  }
})
