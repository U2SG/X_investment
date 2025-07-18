import React, { useState } from 'react';

export default function DeleteFeatureModal({ feature, onClose, onDelete }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleDelete = () => {
    setLoading(true);
    setError(null);
    setTimeout(() => {
      // mock: 90%成功，10%失败
      if (Math.random() < 0.9) {
        onDelete(feature.id);
      } else {
        setError('删除失败，请重试');
        setLoading(false);
      }
    }, 600);
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e=>e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
        <h3>确认删除</h3>
        <div style={{margin:'16px 0'}}>确定要删除“{feature.name}”吗？</div>
        <button onClick={handleDelete} disabled={loading} style={{marginRight:16}}>{loading ? '删除中...' : '确认'}</button>
        <button onClick={onClose} disabled={loading}>取消</button>
        {error && <div style={{color:'red',marginTop:12}}>{error}</div>}
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:320px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
      `}</style>
    </div>
  );
} 