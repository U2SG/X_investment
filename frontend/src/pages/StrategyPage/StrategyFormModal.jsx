// 策略新增/编辑弹窗组件
// props:
//   onClose: 关闭弹窗回调
//   onSuccess: 操作成功后回调（如刷新列表）
//   initial: （可选）要编辑的策略对象，若无则为新增

import React, { useState, useEffect } from 'react';
import Modal from '../../components/Modal';

// StrategyFormModal: 策略新增/编辑弹窗
export default function StrategyFormModal({ onClose, onSuccess, initial }) {
  const [form, setForm] = useState(initial || {
    name: '',
    description: '',
    strategy_type: 'MULTI_FACTOR',
    asset_class: 'STOCK',
    parameters: '{}',
    risk_level: 3,
    expected_return: '',
    max_drawdown: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isEdit = !!initial;

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    let paramsObj = {};
    try {
      paramsObj = form.parameters ? JSON.parse(form.parameters) : {};
    } catch {
      setError('参数必须为合法JSON');
      setLoading(false);
      return;
    }
    const body = {
      ...form,
      risk_level: Number(form.risk_level),
      expected_return: form.expected_return ? Number(form.expected_return) : undefined,
      max_drawdown: form.max_drawdown ? Number(form.max_drawdown) : undefined,
      parameters: paramsObj
    };
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(isEdit ? `/strategy/${initial.id}` : '/strategy', {
        method: isEdit ? 'PUT' : 'POST',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(isEdit ? '更新失败' : '创建失败');
      onSuccess();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initial) {
      setForm({
        ...initial,
        parameters: typeof initial.parameters === 'string' ? initial.parameters : JSON.stringify(initial.parameters || {}, null, 2),
        expected_return: initial.expected_return ?? '',
        max_drawdown: initial.max_drawdown ?? ''
      });
    }
  }, [initial]);

  return (
    <Modal onClose={onClose} width={480}>
      <h3>{isEdit ? '编辑策略' : '新增策略'}</h3>
      <form onSubmit={handleSubmit}>
        <div style={{marginBottom: 12}}>
          <label>名称 <input name="name" value={form.name} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom: 12}}>
          <label>描述 <input name="description" value={form.description} onChange={handleChange} /></label>
        </div>
        <div style={{marginBottom: 12}}>
          <label>类型
            <select name="strategy_type" value={form.strategy_type} onChange={handleChange}>
              <option value="MULTI_FACTOR">多因子</option>
              <option value="MACRO_TIMING">宏观择时</option>
              <option value="SECTOR_ROTATION">行业轮动</option>
              <option value="MOMENTUM">动量</option>
              <option value="MEAN_REVERSION">均值回归</option>
              <option value="ARBITRAGE">套利</option>
              <option value="CUSTOM">自定义</option>
            </select>
          </label>
        </div>
        <div style={{marginBottom: 12}}>
          <label>资产类别
            <select name="asset_class" value={form.asset_class} onChange={handleChange}>
              <option value="STOCK">股票</option>
              <option value="BOND">债券</option>
              <option value="COMMODITY">商品</option>
              <option value="CASH">现金</option>
              <option value="REAL_ESTATE">地产</option>
              <option value="ALTERNATIVE">另类</option>
            </select>
          </label>
        </div>
        <div style={{marginBottom: 12}}>
          <label>参数(JSON)
            <input name="parameters" value={form.parameters} onChange={handleChange} placeholder='{"key": "value"}' />
          </label>
        </div>
        <div style={{marginBottom: 12}}>
          <label>风险等级 <input name="risk_level" type="number" min="1" max="5" value={form.risk_level} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom: 12}}>
          <label>预期收益 <input name="expected_return" type="number" step="0.01" value={form.expected_return} onChange={handleChange} /></label>
        </div>
        <div style={{marginBottom: 12}}>
          <label>最大回撤 <input name="max_drawdown" type="number" step="0.01" value={form.max_drawdown} onChange={handleChange} /></label>
        </div>
        <button type="submit" disabled={loading}>{loading ? (isEdit ? '提交中...' : '提交中...') : (isEdit ? '保存' : '提交')}</button>
        {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
      </form>
    </Modal>
  );
} 