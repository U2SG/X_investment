import React, { useState } from 'react';

export default function EditFeatureModal({ feature, onClose, onEdit }) {
  const [form, setForm] = useState({ ...feature });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };
  const validate = () => {
    if (!form.name.trim()) return '特征名称为必填项';
    if (!form.type) return '类型为必选项';
    if (!form.version.trim()) return '版本为必填项';
    if (!form.created_by.trim()) return '创建人为必填项';
    if (form.name.length > 50) return '特征名称不能超过50字';
    if (form.version.length > 20) return '版本不能超过20字';
    if (form.created_by.length > 20) return '创建人不能超过20字';
    return null;
  };
  const handleSubmit = e => {
    e.preventDefault();
    const err = validate();
    if (err) { setError(err); return; }
    setLoading(true);
    setError(null);
    setTimeout(() => {
      onEdit(form);
      setLoading(false);
      onClose();
    }, 500);
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>编辑特征</h3>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:12}}>
            <label>特征名称 <input name="name" value={form.name} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>类型
              <select name="type" value={form.type} onChange={handleChange}>
                <option value="数值">数值</option>
                <option value="分类">分类</option>
              </select>
            </label>
          </div>
          <div style={{marginBottom:12}}>
            <label>版本 <input name="version" value={form.version} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>创建人 <input name="created_by" value={form.created_by} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>状态
              <select name="status" value={form.status} onChange={handleChange}>
                <option value="active">启用</option>
                <option value="inactive">停用</option>
              </select>
            </label>
          </div>
          <div style={{marginBottom:12}}>
            <label>描述 <input name="description" value={form.description} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>血缘 <input name="lineage" value={form.lineage} onChange={handleChange} /></label>
          </div>
          <button type="submit" disabled={loading}>{loading ? '提交中...' : '提交'}</button>
          {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
        </form>
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:320px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
} 