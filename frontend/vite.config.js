import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return defineConfig({
    plugins: [react()],
    define: {
      __SUPABASE_URL__: JSON.stringify(env.VITE_SUPABASE_URL || ''),
      __SUPABASE_KEY__: JSON.stringify(env.VITE_SUPABASE_KEY || ''),
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
        }
      }
    }
  })
}

