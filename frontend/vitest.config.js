import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.js',
  },
  resolve: {
    alias: {
      'react': path.resolve(process.cwd(), 'node_modules/react'),
      'react-dom': path.resolve(process.cwd(), 'node_modules/react-dom'),
      'react/jsx-dev-runtime': path.resolve(process.cwd(), 'node_modules/react/jsx-dev-runtime.js'),
      'lucide-react': path.resolve(process.cwd(), 'node_modules/lucide-react'),
      'react-router-dom': path.resolve(process.cwd(), 'node_modules/react-router-dom'),
    },
  },
})
