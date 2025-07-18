import React, { useEffect, useState } from 'react';
import StrategyFormModal from './StrategyFormModal';
import StrategyDetailModal from './StrategyDetailModal';


// 定义资产类型到中文的映射
const assetClassMap = {
  STOCK: "股票",
  BOND: "债券",
  COMMODITY: "商品",
  CASH: "现金",
  REAL_ESTATE: "房地产",
  ALTERNATIVE: "另类投资"
};

const strategyTypeMap = {
  MACRO_TIMING: "宏观择时",
  SECTOR_ROTATION: "行业轮动",
  MULTI_FACTOR: "多因子",
  MOMENTUM: "动量",
  MEAN_REVERSION: "均值回归",
  ARBITRAGE: "套利",
  CUSTOM: "自定义"
};


// 策略管理页面
function StrategyPage() {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [editStrategy, setEditStrategy] = useState(null);

  const fetchStrategies = async () => {
    const token = localStorage.getItem('token');
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/strategy/', {
        headers: {
          'Authorization': token ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) throw new Error('登录状态已失效，请重新登录');
      const data = await res.json();
      setStrategies(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('确定要删除该策略吗？')) return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`/strategy/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
        },
      });
      if (!res.ok) throw new Error('删除失败');
      fetchStrategies();
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div className="strategy-page">
      <h2>策略管理</h2>
      <button onClick={() => setShowAdd(true)} style={{marginBottom:16}}>新增策略</button>
      {loading && <div>加载中...</div>}
      {error && <div style={{color: 'red'}}>错误: {error}</div>}
      {!loading && !error && (
        <table className="strategy-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>类型</th>
              <th>资产类别</th>
              <th>风险等级</th>
              <th>预期收益</th>
              <th>最大回撤</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map(s => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{strategyTypeMap[s.strategy_type]}</td>
                <td>{assetClassMap[s.asset_class]}</td>
                <td>{s.risk_level}</td>
                <td>{s.expected_return}</td>
                <td>{s.max_drawdown}</td>
                <td>
                  <button onClick={() => setSelected(s)}>详情</button>
                  <button onClick={() => setEditStrategy(s)} style={{marginLeft:8}}>编辑</button>
                  <button onClick={() => handleDelete(s.id)} style={{marginLeft:8, color:'red'}}>删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {selected && <StrategyDetailModal strategy={selected} onClose={() => setSelected(null)} />}
      {showAdd && <StrategyFormModal onClose={() => setShowAdd(false)} onSuccess={fetchStrategies} />}
      {editStrategy && <StrategyFormModal initial={editStrategy} onClose={() => setEditStrategy(null)} onSuccess={fetchStrategies} />}
    </div>
  );
}

export default StrategyPage; 