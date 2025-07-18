import React, { useState, useEffect } from 'react';

const mockData = [
  { id: 1, name: '上证指数', type: '指数', source: 'Wind', date: '2024-01-01', value: 3200.5 },
  { id: 2, name: 'AAPL', type: '股票', source: 'Yahoo', date: '2024-01-01', value: 180.2 },
  { id: 3, name: 'GDP', type: '宏观', source: '国家统计局', date: '2023-12-31', value: 120000 },
];

function AddMarketDataModal({ onClose, onAdd }) {
  const [form, setForm] = useState({
    symbol: '',
    name: '',
    asset_type: 'STOCK',
    exchange: '',
    currency: 'CNY',
    is_active: true,
    industry: '',
    sector: '',
    market_cap: '',
    pe_ratio: '',
    pb_ratio: '',
    dividend_yield: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };
  const handleSubmit = e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    // 构造提交对象，去除空字符串和转换number
    const submitObj = {
      ...form,
      market_cap: form.market_cap ? Number(form.market_cap) : undefined,
      pe_ratio: form.pe_ratio ? Number(form.pe_ratio) : undefined,
      pb_ratio: form.pb_ratio ? Number(form.pb_ratio) : undefined,
      dividend_yield: form.dividend_yield ? Number(form.dividend_yield) : undefined,
      industry: form.industry || undefined,
      sector: form.sector || undefined
    };
    onAdd(submitObj);
    setLoading(false);
    onClose();
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:340,maxWidth:480}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>新增市场数据</h3>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:12}}>
            <label>证券代码 <input name="symbol" value={form.symbol} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>证券名称 <input name="name" value={form.name} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>资产类型
              <select name="asset_type" value={form.asset_type} onChange={handleChange} required>
                <option value="STOCK">股票</option>
                <option value="BOND">债券</option>
                <option value="FUND">基金</option>
                <option value="ETF">ETF</option>
                <option value="FUTURES">期货</option>
                <option value="OPTIONS">期权</option>
                <option value="FOREX">外汇</option>
                <option value="COMMODITY">商品</option>
              </select>
            </label>
          </div>
          <div style={{marginBottom:12}}>
            <label>交易所 <input name="exchange" value={form.exchange} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>货币 <input name="currency" value={form.currency} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>是否活跃 <input name="is_active" type="checkbox" checked={form.is_active} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>行业 <input name="industry" value={form.industry} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>板块 <input name="sector" value={form.sector} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>市值 <input name="market_cap" type="number" value={form.market_cap} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>市盈率 <input name="pe_ratio" type="number" value={form.pe_ratio} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>市净率 <input name="pb_ratio" type="number" value={form.pb_ratio} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>股息率 <input name="dividend_yield" type="number" value={form.dividend_yield} onChange={handleChange} /></label>
          </div>
          <button type="submit" disabled={loading}>{loading ? '提交中...' : '提交'}</button>
          {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
        </form>
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:340px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
}

function EditMarketDataModal({ data, onClose, onEdit }) {
  const [form, setForm] = useState({ ...data });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };
  const handleSubmit = e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    // 构造提交对象，去除空字符串和转换number
    const submitObj = {
      ...form,
      market_cap: form.market_cap ? Number(form.market_cap) : undefined,
      pe_ratio: form.pe_ratio ? Number(form.pe_ratio) : undefined,
      pb_ratio: form.pb_ratio ? Number(form.pb_ratio) : undefined,
      dividend_yield: form.dividend_yield ? Number(form.dividend_yield) : undefined,
      industry: form.industry || undefined,
      sector: form.sector || undefined
    };
    onEdit(submitObj);
    setLoading(false);
    onClose();
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:340,maxWidth:480}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>编辑市场数据</h3>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:12}}>
            <label>证券代码 <input name="symbol" value={form.symbol} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>证券名称 <input name="name" value={form.name} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>资产类型
              <select name="asset_type" value={form.asset_type} onChange={handleChange} required>
                <option value="STOCK">股票</option>
                <option value="BOND">债券</option>
                <option value="FUND">基金</option>
                <option value="ETF">ETF</option>
                <option value="FUTURES">期货</option>
                <option value="OPTIONS">期权</option>
                <option value="FOREX">外汇</option>
                <option value="COMMODITY">商品</option>
              </select>
            </label>
          </div>
          <div style={{marginBottom:12}}>
            <label>交易所 <input name="exchange" value={form.exchange} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>货币 <input name="currency" value={form.currency} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>是否活跃 <input name="is_active" type="checkbox" checked={form.is_active} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>行业 <input name="industry" value={form.industry} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>板块 <input name="sector" value={form.sector} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>市值 <input name="market_cap" type="number" value={form.market_cap} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>市盈率 <input name="pe_ratio" type="number" value={form.pe_ratio} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>市净率 <input name="pb_ratio" type="number" value={form.pb_ratio} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>股息率 <input name="dividend_yield" type="number" value={form.dividend_yield} onChange={handleChange} /></label>
          </div>
          <button type="submit" disabled={loading}>{loading ? '提交中...' : '提交'}</button>
          {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
        </form>
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:340px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
}

export default function MarketDataPage() {
  const [data, setData] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [editRow, setEditRow] = useState(null);
  const [deleteRow, setDeleteRow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 新增后刷新数据
  const fetchData = () => {
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    fetch('/market-data/', {
      headers: {
        'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined
      }
    })
      .then(res => {
        if (!res.ok) throw new Error('加载失败');
        return res.json();
      })
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(fetchData, []);

  return (
    <div style={{padding:24}}>
      <h2>市场数据管理</h2>
      <button onClick={()=>setShowAdd(true)} style={{marginBottom:16}}>新增数据</button>
      {loading && <div>加载中...</div>}
      {error && <div style={{color:'red'}}>错误: {error}</div>}
      {!loading && !error && (
        <table style={{width:'100%',background:'#111',color:'#fff',borderRadius:8}}>
          <thead>
            <tr>
              <th>ID</th>
              <th>证券代码</th>
              <th>证券名称</th>
              <th>资产类型</th>
              <th>交易所</th>
              <th>货币</th>
              <th>活跃</th>
              <th>行业</th>
              <th>板块</th>
              <th>市值</th>
              <th>市盈率</th>
              <th>市净率</th>
              <th>股息率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.symbol}</td>
                <td>{row.name}</td>
                <td>{row.asset_type}</td>
                <td>{row.exchange}</td>
                <td>{row.currency}</td>
                <td>{row.is_active ? '是' : '否'}</td>
                <td>{row.industry || '-'}</td>
                <td>{row.sector || '-'}</td>
                <td>{row.market_cap ?? '-'}</td>
                <td>{row.pe_ratio ?? '-'}</td>
                <td>{row.pb_ratio ?? '-'}</td>
                <td>{row.dividend_yield ?? '-'}</td>
                <td>
                  <button onClick={()=>setEditRow(row)}>编辑</button>
                  <button style={{marginLeft:8}} onClick={()=>setDeleteRow(row)}>删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {showAdd && <AddMarketDataModal onClose={()=>setShowAdd(false)} onAdd={async item=>{
        const token = localStorage.getItem('token');
        try {
          const res = await fetch('/market-data/', {
            method: 'POST',
            headers: {
              'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(item)
          });
          if (!res.ok) throw new Error('新增失败');
          fetchData();
        } catch (e) {
          alert(e.message);
        }
      }} />}
      {editRow && <EditMarketDataModal data={editRow} onClose={()=>setEditRow(null)} onEdit={async item=>{
        const token = localStorage.getItem('token');
        try {
          const res = await fetch(`/market-data/${item.id}`, {
            method: 'PUT',
            headers: {
              'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(item)
          });
          if (!res.ok) throw new Error('编辑失败');
          fetchData();
        } catch (e) {
          alert(e.message);
        }
      }} />}
      {deleteRow && (
        <div className="modal-overlay" onClick={()=>setDeleteRow(null)}>
          <div className="modal" onClick={e=>e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
            <h3>确认删除</h3>
            <div style={{margin:'16px 0'}}>确定要删除“{deleteRow.name}”吗？</div>
            <button onClick={async ()=>{
              const token = localStorage.getItem('token');
              try {
                const res = await fetch(`/market-data/${deleteRow.id}`, {
                  method: 'DELETE',
                  headers: {
                    'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined
                  }
                });
                if (!res.ok) throw new Error('删除失败');
                fetchData();
              } catch (e) {
                alert(e.message);
              }
              setDeleteRow(null);
            }} style={{marginRight:16}}>确认</button>
            <button onClick={()=>setDeleteRow(null)}>取消</button>
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