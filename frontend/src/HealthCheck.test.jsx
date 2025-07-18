import React from 'react'; // 添加React导入
import { render } from '@testing-library/react';
import HealthCheck from './HealthCheck';
import { describe, it, expect } from 'vitest';

// 最小化测试：只验证组件能否正常渲染，不依赖DOM API
describe('HealthCheck', () => {
  it('可以正常渲染', () => {
    // 如果组件能渲染而不报错，测试就通过
    const { container } = render(<HealthCheck />);
    expect(container).toBeDefined();
  });
}); 