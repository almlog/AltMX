import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    testTimeout: 10000, // 10秒タイムアウト
    hookTimeout: 10000, // フック用タイムアウト
    pool: 'forks',      // プロセス分離でメモリ節約
    poolOptions: {
      forks: {
        singleFork: true  // シングルプロセスで実行
      }
    }
  },
})