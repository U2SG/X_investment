// 信号编辑弹窗组件
// props:
//   signal: 信号对象
//   onClose: 关闭弹窗回调
//   onSuccess: 操作成功后回调（如刷新列表）

import React, { useState } from 'react';
import Modal from '../../components/Modal';

// SignalEditModal: 信号编辑弹窗
export default function SignalEditModal({ signal, onClose, onSuccess }) {
    const [form, setForm] = useState({ ...signal });
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
        const res = await fetch(`/strategy/signals/${signal.id}`, {
          method: 'PUT',
          headers: {
            'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...form,
            signal_strength: Number(form.signal_strength),
            target_weight: Number(form.target_weight),
            confidence_score: Number(form.confidence_score)
          })
        });
        if (!res.ok) throw new Error('信号编辑失败');
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
        <h3>编辑信号</h3>
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
              <label>推理 <input name="reasoning" value={form.reasoning || ''} onChange={handleChange} /></label>
            </div>
            <button type="submit" disabled={loading}>{loading ? '提交中...' : '提交'}</button>
            {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
          </form>
      </Modal>
    );
  }
  