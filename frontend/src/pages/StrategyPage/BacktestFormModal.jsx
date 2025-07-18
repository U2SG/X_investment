// 新增回测弹窗组件
// props:
//   strategyId: 策略ID
//   onClose: 关闭弹窗回调
//   onSuccess: 操作成功后回调（如刷新列表）

import React, { useState } from 'react';
import Modal from '../../components/Modal';

// BacktestFormModal: 新增回测弹窗
export default function BacktestFormModal({ strategyId, onClose, onSuccess }) {
  const [form, setForm] = useState({
    start_date: '',
    end_date: '',
    initial_capital: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };
  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('/strategy/backtest', {
        method: 'POST',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          strategy_id: strategyId,
          start_date: form.start_date,
          end_date: form.end_date,
          initial_capital: Number(form.initial_capital)
        })
      });
      if (!res.ok) throw new Error('回测创建失败');
      onSuccess();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <Modal onClose={onClose} width={400}>
      <h3>新增回测</h3>
      <form onSubmit={handleSubmit}>
        <div style={{marginBottom:12}}>
          <label>起始日期 <input name="start_date" type="date" value={form.start_date} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom:12}}>
          <label>结束日期 <input name="end_date" type="date" value={form.end_date} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom:12}}>
          <label>初始资金 <input name="initial_capital" type="number" min="1" value={form.initial_capital} onChange={handleChange} required /></label>
        </div>
        <button type="submit" disabled={loading}>{loading ? '回测中...' : '提交'}</button>
      </form>
      {loading && <div style={{color:'#1976d2',marginTop:8}}>回测中，请稍候...</div>}
      {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
    </Modal>
  );
} 