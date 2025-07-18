import React, { useState } from 'react';

const mockFeatures = [
  { id: 1, name: '动量因子', type: '数值', version: 'v1.0', created_by: 'Alice', created_at: '2024-01-01', status: 'active', description: '近20日收益率', lineage: 'price->return->momentum' },
  { id: 2, name: '市盈率', type: '数值', version: 'v1.1', created_by: 'Bob', created_at: '2024-01-10', status: 'active', description: '市值/净利润', lineage: 'market_cap->net_income->pe' },
  { id: 3, name: '行业哑变量', type: '分类', version: 'v1.0', created_by: 'Carol', created_at: '2024-01-15', status: 'inactive', description: '行业one-hot', lineage: 'industry->onehot' },
];

function AddFeatureModal({ onClose, onAdd }) {
  const [form, setForm] = useState({
    name: '',
    type: '数值',
    version: 'v1.0',
    created_by: '',
    status: 'active',
    description: '',
    lineage: ''
  });
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
      onAdd({ ...form, created_at: new Date().toISOString().slice(0,10) });
      setLoading(false);
      onClose();
    }, 500);
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>新增特征</h3>
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

function EditFeatureModal({ feature, onClose, onEdit }) {
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

export default function FeatureStorePage() {
  const [features, setFeatures] = useState(mockFeatures);
  const [showAdd, setShowAdd] = useState(false);
  const [editFeature, setEditFeature] = useState(null);
  const [deleteFeature, setDeleteFeature] = useState(null);
  return (
    <div style={{padding:24}}>
      <h2>特征工程平台</h2>
      <button onClick={()=>setShowAdd(true)} style={{marginBottom:16}}>新增特征</button>
      <table style={{width:'100%',background:'#111',color:'#fff',borderRadius:8}}>
        <thead>
          <tr>
            <th>ID</th>
            <th>特征名称</th>
            <th>类型</th>
            <th>版本</th>
            <th>创建人</th>
            <th>创建时间</th>
            <th>状态</th>
            <th>描述</th>
            <th>血缘</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {features.map(f => (
            <tr key={f.id}>
              <td>{f.id}</td>
              <td>{f.name}</td>
              <td>{f.type}</td>
              <td>{f.version}</td>
              <td>{f.created_by}</td>
              <td>{f.created_at}</td>
              <td>{f.status === 'active' ? '启用' : '停用'}</td>
              <td>{f.description}</td>
              <td>{f.lineage}</td>
              <td>
                <button onClick={()=>setEditFeature(f)}>编辑</button>
                <button style={{marginLeft:8}} onClick={()=>setDeleteFeature(f)}>删除</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {showAdd && <AddFeatureModal onClose={()=>setShowAdd(false)} onAdd={item=>{
        setFeatures(f=>[...f, { ...item, id: f.length ? Math.max(...f.map(x=>x.id))+1 : 1 }]);
      }} />}
      {editFeature && <EditFeatureModal feature={editFeature} onClose={()=>setEditFeature(null)} onEdit={item=>{
        setFeatures(f=>f.map(x=>x.id===item.id ? item : x));
      }} />}
      {deleteFeature && (
        <div className="modal-overlay" onClick={()=>setDeleteFeature(null)}>
          <div className="modal" onClick={e=>e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
            <h3>确认删除</h3>
            <div style={{margin:'16px 0'}}>确定要删除“{deleteFeature.name}”吗？</div>
            <button onClick={()=>{
              setFeatures(f=>f.filter(x=>x.id!==deleteFeature.id));
              setDeleteFeature(null);
            }} style={{marginRight:16}}>确认</button>
            <button onClick={()=>setDeleteFeature(null)}>取消</button>
          </div>
          <style>{`
            .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
            .modal { background:#000; padding:2rem; border-radius:8px; min-width:320px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
          `}</style>
        </div>
      )}
    </div>
  );
} 