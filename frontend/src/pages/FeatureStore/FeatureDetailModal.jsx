import React from 'react';

export default function FeatureDetailModal({ feature, onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e=>e.stopPropagation()} style={{minWidth:340,maxWidth:480}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>特征详情</h3>
        <div><b>ID:</b> {feature.id}</div>
        <div><b>特征名称:</b> {feature.name}</div>
        <div><b>类型:</b> {feature.type}</div>
        <div><b>版本:</b> {feature.version}</div>
        <div><b>创建人:</b> {feature.created_by}</div>
        <div><b>创建时间:</b> {feature.created_at}</div>
        <div><b>状态:</b> {feature.status === 'active' ? '启用' : '停用'}</div>
        <div><b>描述:</b> {feature.description}</div>
        <div><b>血缘:</b> {feature.lineage}</div>
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:340px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
} 