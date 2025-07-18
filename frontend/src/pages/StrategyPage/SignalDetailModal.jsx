// 信号详情弹窗组件
// props:
//   signal: 信号对象
//   onClose: 关闭弹窗回调

import React from 'react';
import Modal from '../../components/Modal';

// SignalDetailModal: 信号详情弹窗
export default function SignalDetailModal({ signal, onClose }) {
  if (!signal) return null;
  return (
    <Modal onClose={onClose} width={480}>
      <button className="modal-close" onClick={onClose}>×</button>
      <h3>信号详情</h3>
      <div><b>ID:</b> {signal.id}</div>
      <div><b>类型:</b> {signal.signal_type}</div>
      <div><b>强度:</b> {signal.signal_strength}</div>
      <div><b>目标权重:</b> {signal.target_weight}</div>
      <div><b>置信度:</b> {signal.confidence_score}</div>
      <div><b>推理:</b> {signal.reasoning}</div>
      <div><b>因子:</b> <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(signal.factors, null, 2)}</pre></div>
      <div><b>信号日期:</b> {signal.signal_date}</div>
      <div><b>创建时间:</b> {signal.created_at}</div>
    </Modal>
  );
} 