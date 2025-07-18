/**
 * 前端配置文件
 * 从环境变量加载配置，如未设置则使用默认值
 */

// 环境变量获取函数，支持回退到默认值
const getEnv = (key, defaultValue) => {
  // Vite环境变量必须以VITE_开头
  const envKey = `VITE_${key}`;
  return import.meta.env[envKey] || defaultValue;
};

const config = {
  // API基础URL
  apiBaseUrl: getEnv('API_BASE_URL', 'http://localhost:8000'),
  
  // 功能开关
  features: {
    enableMock: getEnv('ENABLE_MOCK', 'false') === 'true',
    enableAnalytics: getEnv('ENABLE_ANALYTICS', 'true') === 'true',
    darkMode: getEnv('DARK_MODE', 'system')
  },
  
  // 应用设置
  app: {
    title: '智能投顾系统',
    version: '0.1.0'
  },

  // 开发环境标志
  isDevelopment: import.meta.env.DEV
};

// 开发环境日志
if (config.isDevelopment) {
  console.log('当前配置:', config);
}

export default config; 