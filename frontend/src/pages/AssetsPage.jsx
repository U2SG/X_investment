import React, { useState, useEffect } from 'react';

function AssetsPage() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ code: '', name: '', asset_type: '', description: '' });
  const [formError, setFormError] = useState(null);
  const [formLoading, setFormLoading] = useState(false);

  const fetchAssets = () => {
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    fetch('/assets/', {
      headers: {
        'Authorization': token ? `Bearer ${token}` : undefined
      }
    })
      .then(res => {
        if (!res.ok) throw new Error('获取资产失败');
        return res.json();
      })
      .then(data => {
        setAssets(data);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAssets();
  }, []);

  const handleInputChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddAsset = e => {
    e.preventDefault();
    setFormError(null);
    setFormLoading(true);
    const token = localStorage.getItem('token');
    fetch('/assets/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : undefined
      },
      body: JSON.stringify(form)
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || '添加失败'); });
        return res.json();
      })
      .then(() => {
        setShowForm(false);
        setForm({ code: '', name: '', asset_type: '', description: '' });
        fetchAssets();
      })
      .catch(e => {
        setFormError(e.message);
      })
      .finally(() => setFormLoading(false));
  };

  const handleDeleteAsset = (assetId) => {
    if (!window.confirm('确定要删除该资产吗？')) return;
    setFormError(null);
    const token = localStorage.getItem('token');
    fetch(`/assets/${assetId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': token ? `Bearer ${token}` : undefined
      }
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw new Error(err.detail || '删除失败'); });
        fetchAssets();
      })
      .catch(e => {
        setFormError(e.message);
      });
  };

  if (loading) return <div>加载中...</div>;
  if (error) return <div style={{color: 'red'}}>错误: {error}</div>;

  return (
    <div>
      <h2>资产管理</h2>
      <button onClick={() => setShowForm(f => !f)}>{showForm ? '取消' : '新增资产'}</button>
      {showForm && (
        <form className="asset-form" onSubmit={handleAddAsset} style={{margin: '16px 0'}}>
          <input name="code" placeholder="资产代码" value={form.code} onChange={handleInputChange} required />
          <input name="name" placeholder="资产名称" value={form.name} onChange={handleInputChange} required />
          <input name="asset_type" placeholder="资产类型" value={form.asset_type} onChange={handleInputChange} required />
          <input name="description" placeholder="描述" value={form.description} onChange={handleInputChange} />
          <button type="submit" disabled={formLoading}>提交</button>
          {formError && <span style={{color: 'red', marginLeft: 8}}>{formError}</span>}
        </form>
      )}
      <table className="assets-table">
        <thead>
          <tr>
            <th>代码</th>
            <th>名称</th>
            <th>类型</th>
            <th>描述</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {assets.map(asset => (
            <tr key={asset.id}>
              <td>{asset.code}</td>
              <td>{asset.name}</td>
              <td>{asset.asset_type}</td>
              <td>{asset.description}</td>
              <td>
                <button onClick={() => handleDeleteAsset(asset.id)} style={{color: 'red'}}>删除</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AssetsPage; 