import React, { useEffect, useState } from 'react';
import config from './config'; // 导入配置文件

function HealthCheck() {
  // 状态变量：存储后端返回的状态和可能的错误信息
  const [status, setStatus] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    // 组件挂载时，请求后端健康检查接口
    // 使用config中的apiBaseUrl替代硬编码地址
    fetch(`${config.apiBaseUrl}/health`)
      .then((res) => res.json())
      .then((data) => setStatus(data.status)) // 成功时更新状态
      .catch((err) => setError('无法连接后端服务')); // 捕获网络错误或解析错误
  }, []); // 空依赖数组确保仅在组件挂载时执行一次

  return (
    <div>
      <h2>后端健康检查</h2>
      {error ? (
        // 错误状态：显示错误信息
        <p style={{ color: 'red' }}>{error}</p>
      ) : (
        // 正常状态：显示后端状态或加载中提示
        <p>后端状态: {status || '检查中...'}</p>
      )}
    </div>
  );
}

export default HealthCheck; 