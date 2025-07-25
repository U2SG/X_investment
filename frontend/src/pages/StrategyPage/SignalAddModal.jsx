// 新增信号弹窗组件
// props:
//   strategyId: 策略ID
//   onClose: 关闭弹窗回调
//   onSuccess: 操作成功后回调（如刷新列表）

import React, { useState } from 'react';
import Modal from '../../components/Modal';

// SignalAddModal: 新增信号弹窗
export default function SignalAddModal({ strategyId, onClose, onSuccess }) {
  const [form, setForm] = useState({
    signal_type: '',
    signal_strength: '',
    target_weight: '',
    confidence_score: '',
    reasoning: '',
    market_data_id: ''
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
      const res = await fetch('/strategy/signals', {
        method: 'POST',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...form,
          strategy_id: strategyId,
          signal_strength: Number(form.signal_strength),
          target_weight: Number(form.target_weight),
          confidence_score: Number(form.confidence_score),
          market_data_id: form.market_data_id ? Number(form.market_data_id) : undefined
        })
      });
      if (!res.ok) throw new Error('信号创建失败');
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
      <h3>新增信号</h3>
      <form onSubmit={handleSubmit}>
        <div style={{marginBottom:12}}>
          <label>类型 <input name="signal_type" value={form.signal_type} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom:12}}>
          <label>强度 <input name="signal_strength" type="number" value={form.signal_strength} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom:12}}>
          <label>目标权重 <input name="target_weight" type="number" value={form.target_weight} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom:12}}>
          <label>置信度 <input name="confidence_score" type="number" value={form.confidence_score} onChange={handleChange} required /></label>
        </div>
        <div style={{marginBottom:12}}>
          <label>推理 <input name="reasoning" value={form.reasoning} onChange={handleChange} /></label>
        </div>
        <div style={{marginBottom:12}}>
          <label>市场数据ID <input name="market_data_id" type="number" value={form.market_data_id} onChange={handleChange} required /></label>
        </div>
        <button type="submit" disabled={loading}>{loading ? '提交中...' : '提交'}</button>
        {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
      </form>
    </Modal>
  );
} 