/**
 * 前端配置示例文件
 * 使用方法：复制此文件为 config.js 并根据实际环境修改配置
 */

const config = {
  // API基础URL
  apiBaseUrl: 'http://localhost:8000',
  
  // 功能开关
  features: {
    enableMock: false,     // 是否启用模拟数据
    enableAnalytics: true, // 是否启用分析追踪
    darkMode: 'system'     // 暗黑模式：'light', 'dark', 'system'
  },
  
  // 应用设置
  app: {
    title: '智能投顾系统',
    version: '0.1.0'
  }
};

export default config; 