import React from 'react';

// 通用Modal组件
// props:
//   visible: 是否显示（可选，默认true）
//   onClose: 关闭回调
//   width: 宽度（可选，默认400）
//   children: 内容
export default function Modal({ visible = true, onClose, width = 400, children }) {
  if (visible === false) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal"
        onClick={e => e.stopPropagation()}
        style={{ minWidth: width, maxWidth: 0.9 * width + 100 }}
      >
        <button className="modal-close" onClick={onClose}>×</button>
        {children}
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
} 