import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/assets': 'http://localhost:8000',
      '/tags': 'http://localhost:8000',
      '/portfolios': 'http://localhost:8000',
      '/strategy': 'http://localhost:8000',
      '/risk_assessment': 'http://localhost:8000',
      '/market-data': 'http://localhost:8000',
    }
  }
});
