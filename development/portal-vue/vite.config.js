import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  base: '/assets/university_erp/portal/',
  build: {
    outDir: path.resolve(__dirname, '../frappe-bench/apps/university_erp/university_erp/public/portal'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'index.html'),
    },
  },
})
