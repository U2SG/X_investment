// 信号详情弹窗组件
// props:
//   signal: 信号对象
//   onClose: 关闭弹窗回调

import React from 'react';

// SignalDetailModal: 信号详情弹窗
export default function SignalDetailModal({ signal, onClose }) {
  if (!signal) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:320,maxWidth:480}}>
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
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:320px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
} 