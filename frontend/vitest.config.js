// 最小化Vitest配置
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'happy-dom', // 使用happy-dom替代jsdom
    globals: true
  },
}); 