import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  build: {
    outDir: 'static/dist',
    emptyOutDir: false
  }
})
