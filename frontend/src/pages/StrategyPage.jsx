import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';

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

function StrategyFormModal({ onClose, onSuccess, initial }) {
  const [form, setForm] = useState(initial || {
    name: '',
    description: '',
    strategy_type: 'MULTI_FACTOR',
    asset_class: 'STOCK',
    parameters: '{}',
    risk_level: 3,
    expected_return: '',
    max_drawdown: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isEdit = !!initial;

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    let paramsObj = {};
    try {
      paramsObj = form.parameters ? JSON.parse(form.parameters) : {};
    } catch {
      setError('参数必须为合法JSON');
      setLoading(false);
      return;
    }
    const body = {
      ...form,
      risk_level: Number(form.risk_level),
      expected_return: form.expected_return ? Number(form.expected_return) : undefined,
      max_drawdown: form.max_drawdown ? Number(form.max_drawdown) : undefined,
      parameters: paramsObj
    };
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(isEdit ? `/strategy/${initial.id}` : '/strategy', {
        method: isEdit ? 'PUT' : 'POST',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(isEdit ? '更新失败' : '创建失败');
      onSuccess();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initial) {
      setForm({
        ...initial,
        parameters: typeof initial.parameters === 'string' ? initial.parameters : JSON.stringify(initial.parameters || {}, null, 2),
        expected_return: initial.expected_return ?? '',
        max_drawdown: initial.max_drawdown ?? ''
      });
    }
  }, [initial]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth: 360, maxWidth: 480}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>{isEdit ? '编辑策略' : '新增策略'}</h3>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom: 12}}>
            <label>名称 <input name="name" value={form.name} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom: 12}}>
            <label>描述 <input name="description" value={form.description} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom: 12}}>
            <label>类型
              <select name="strategy_type" value={form.strategy_type} onChange={handleChange}>
                <option value="MULTI_FACTOR">多因子</option>
                <option value="MACRO_TIMING">宏观择时</option>
                <option value="SECTOR_ROTATION">行业轮动</option>
                <option value="MOMENTUM">动量</option>
                <option value="MEAN_REVERSION">均值回归</option>
                <option value="ARBITRAGE">套利</option>
                <option value="CUSTOM">自定义</option>
              </select>
            </label>
          </div>
          <div style={{marginBottom: 12}}>
            <label>资产类别
              <select name="asset_class" value={form.asset_class} onChange={handleChange}>
                <option value="STOCK">股票</option>
                <option value="BOND">债券</option>
                <option value="COMMODITY">商品</option>
                <option value="CASH">现金</option>
                <option value="REAL_ESTATE">地产</option>
                <option value="ALTERNATIVE">另类</option>
              </select>
            </label>
          </div>
          <div style={{marginBottom: 12}}>
            <label>参数(JSON)
              <input name="parameters" value={form.parameters} onChange={handleChange} placeholder='{"key": "value"}' />
            </label>
          </div>
          <div style={{marginBottom: 12}}>
            <label>风险等级 <input name="risk_level" type="number" min="1" max="5" value={form.risk_level} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom: 12}}>
            <label>预期收益 <input name="expected_return" type="number" step="0.01" value={form.expected_return} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom: 12}}>
            <label>最大回撤 <input name="max_drawdown" type="number" step="0.01" value={form.max_drawdown} onChange={handleChange} /></label>
          </div>
          <button type="submit" disabled={loading}>{loading ? (isEdit ? '提交中...' : '提交中...') : (isEdit ? '保存' : '提交')}</button>
          {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
        </form>
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:350px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
}

function SignalDetailModal({ signal, onClose }) {
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

function BacktestDetailModal({ backtest, onClose, onRetry }) {
  const [retrying, setRetrying] = useState(false);
  const [error, setError] = useState(null);
  const handleRetry = async () => {
    setRetrying(true);
    setError(null);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('/strategy/backtest', {
        method: 'POST',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          strategy_id: backtest.strategy_id,
          start_date: backtest.start_date,
          end_date: backtest.end_date,
          initial_capital: backtest.initial_capital
        })
      });
      if (!res.ok) throw new Error('重试回测失败');
      if (onRetry) onRetry();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setRetrying(false);
    }
  };
  if (!backtest) return null;
  // mock净值曲线数据
  const equityCurve = [
    { date: '2024-01-01', value: 1 },
    { date: '2024-01-02', value: 1.01 },
    { date: '2024-01-03', value: 1.03 },
    { date: '2024-01-04', value: 1.02 },
    { date: '2024-01-05', value: 1.05 },
    { date: '2024-01-06', value: 1.08 },
    { date: '2024-01-07', value: 1.07 },
    { date: '2024-01-08', value: 1.10 },
  ];
  const option = {
    title: { text: '净值曲线', left: 'center', textStyle: { color: '#fff' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: equityCurve.map(item => item.date),
      axisLabel: { color: '#fff' },
      axisLine: { lineStyle: { color: '#888' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#fff' },
      axisLine: { lineStyle: { color: '#888' } },
      splitLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      data: equityCurve.map(item => item.value),
      type: 'line',
      smooth: true,
      lineStyle: { color: '#4fd6ff' },
      areaStyle: { color: 'rgba(79,214,255,0.2)' }
    }],
    grid: { left: 40, right: 20, top: 60, bottom: 40 }
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:320,maxWidth:520}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>回测详情</h3>
        <div><b>ID:</b> {backtest.id}</div>
        <div><b>区间:</b> {backtest.start_date?.slice(0,10)} ~ {backtest.end_date?.slice(0,10)}</div>
        <div><b>初始资金:</b> {backtest.initial_capital}</div>
        <div><b>总收益:</b> {backtest.total_return}</div>
        <div><b>年化收益:</b> {backtest.annualized_return}</div>
        <div><b>波动率:</b> {backtest.volatility}</div>
        <div><b>夏普比率:</b> {backtest.sharpe_ratio}</div>
        <div><b>索提诺比率:</b> {backtest.sortino_ratio}</div>
        <div><b>最大回撤:</b> {backtest.max_drawdown}</div>
        <div><b>卡玛比率:</b> {backtest.calmar_ratio}</div>
        <div style={{marginTop:24,marginBottom:8}}>
          <ReactECharts option={option} style={{height:240, background:'#111', borderRadius:8}} />
        </div>
        {backtest.status === 'failed' && (
          <div style={{marginTop:16}}>
            <button onClick={handleRetry} disabled={retrying}>{retrying ? '重试中...' : '重试'}</button>
            {error && <div style={{color:'red',marginTop:8}}>{error}</div>}
          </div>
        )}
      </div>
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:320px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
}

function BacktestFormModal({ strategyId, onClose, onSuccess }) {
  const [form, setForm] = useState({
    start_date: '',
    end_date: '',
    initial_capital: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };
  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('/strategy/backtest', {
        method: 'POST',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          strategy_id: strategyId,
          start_date: form.start_date,
          end_date: form.end_date,
          initial_capital: Number(form.initial_capital)
        })
      });
      if (!res.ok) throw new Error('回测创建失败');
      onSuccess();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>新增回测</h3>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:12}}>
            <label>起始日期 <input name="start_date" type="date" value={form.start_date} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>结束日期 <input name="end_date" type="date" value={form.end_date} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>初始资金 <input name="initial_capital" type="number" min="1" value={form.initial_capital} onChange={handleChange} required /></label>
          </div>
          <button type="submit" disabled={loading}>{loading ? '回测中...' : '提交'}</button>
          {loading && <div style={{color:'#1976d2',marginTop:8}}>回测中，请稍候...</div>}
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

function SignalEditModal({ signal, onClose, onSuccess }) {
  const [form, setForm] = useState({ ...signal });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };
  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`/strategy/signals/${signal.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...form,
          signal_strength: Number(form.signal_strength),
          target_weight: Number(form.target_weight),
          confidence_score: Number(form.confidence_score)
        })
      });
      if (!res.ok) throw new Error('信号编辑失败');
      onSuccess();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>编辑信号</h3>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:12}}>
            <label>类型 <input name="signal_type" value={form.signal_type} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>强度 <input name="signal_strength" type="number" value={form.signal_strength} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>目标权重 <input name="target_weight" type="number" value={form.target_weight} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>置信度 <input name="confidence_score" type="number" value={form.confidence_score} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>推理 <input name="reasoning" value={form.reasoning || ''} onChange={handleChange} /></label>
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

function SignalAddModal({ strategyId, onClose, onSuccess }) {
  const [form, setForm] = useState({
    signal_type: '',
    signal_strength: '',
    target_weight: '',
    confidence_score: '',
    reasoning: '',
    market_data_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };
  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('/strategy/signals', {
        method: 'POST',
        headers: {
          'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...form,
          strategy_id: strategyId,
          signal_strength: Number(form.signal_strength),
          target_weight: Number(form.target_weight),
          confidence_score: Number(form.confidence_score),
          market_data_id: form.market_data_id ? Number(form.market_data_id) : undefined
        })
      });
      if (!res.ok) throw new Error('信号创建失败');
      onSuccess();
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{minWidth:320,maxWidth:400}}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>新增信号</h3>
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:12}}>
            <label>类型 <input name="signal_type" value={form.signal_type} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>强度 <input name="signal_strength" type="number" value={form.signal_strength} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>目标权重 <input name="target_weight" type="number" value={form.target_weight} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>置信度 <input name="confidence_score" type="number" value={form.confidence_score} onChange={handleChange} required /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>推理 <input name="reasoning" value={form.reasoning} onChange={handleChange} /></label>
          </div>
          <div style={{marginBottom:12}}>
            <label>市场数据ID <input name="market_data_id" type="number" value={form.market_data_id} onChange={handleChange} required /></label>
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

function StrategyDetailModal({ strategy, onClose }) {
  const [signals, setSignals] = useState([]);
  const [backtests, setBacktests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [signalDetail, setSignalDetail] = useState(null);
  const [backtestDetail, setBacktestDetail] = useState(null);
  const [showAddBacktest, setShowAddBacktest] = useState(false);
  const [editSignal, setEditSignal] = useState(null);
  const [showAddSignal, setShowAddSignal] = useState(false);

  useEffect(() => {
    if (!strategy) return;
    setLoading(true);
    setError(null);
    const token = localStorage.getItem('token');
    Promise.all([
      fetch(`/strategy/signals?strategy_id=${strategy.id}`, {
        headers: { 'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined }
      }).then(res => res.ok ? res.json() : []),
      fetch(`/strategy/backtest?strategy_id=${strategy.id}`, {
        headers: { 'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined }
      }).then(res => res.ok ? res.json() : [])
    ]).then(([signalsData, backtestData]) => {
      setSignals(signalsData);
      setBacktests(backtestData);
    }).catch(e => setError('加载详情失败')).finally(() => setLoading(false));
  }, [strategy]);

  if (!strategy) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        <h3>策略详情</h3>
        <div><b>ID:</b> {strategy.id}</div>
        <div><b>名称:</b> {strategy.name}</div>
        <div><b>类型:</b> {strategy.strategy_type}</div>
        <div><b>资产类别:</b> {strategy.asset_class}</div>
        <div><b>风险等级:</b> {strategy.risk_level}</div>
        <div><b>预期收益:</b> {strategy.expected_return}</div>
        <div><b>最大回撤:</b> {strategy.max_drawdown}</div>
        <div><b>参数:</b> <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(strategy.parameters, null, 2)}</pre></div>
        {loading && <div>加载中...</div>}
        {error && <div style={{color:'red'}}>错误: {error}</div>}
        {!loading && !error && (
          <>
            <h4 style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
              <span>信号列表</span>
              <button onClick={()=>setShowAddSignal(true)} style={{marginLeft:12}}>新增信号</button>
            </h4>
            <ul>
              {signals.length === 0 && <li>暂无信号</li>}
              {signals.map(sig => (
                <li key={sig.id} style={{cursor:'pointer',color:'#1976d2',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                  <span onClick={() => setSignalDetail(sig)} style={{flex:1}}>
                    [{sig.signal_date?.slice(0,10)}] {sig.signal_type} 权重: {sig.target_weight} 置信度: {sig.confidence_score}
                  </span>
                  <button style={{marginLeft:8}} onClick={e => {e.stopPropagation();setEditSignal(sig);}}>编辑</button>
                </li>
              ))}
            </ul>
            <h4 style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
              <span>回测结果</span>
              <button onClick={()=>setShowAddBacktest(true)} style={{marginLeft:12}}>新增回测</button>
            </h4>
            <ul>
              {backtests.length === 0 && <li>暂无回测</li>}
              {backtests.map(bt => (
                <li key={bt.id} style={{cursor:'pointer',color:'#1976d2'}} onClick={() => setBacktestDetail(bt)}>
                  {bt.start_date?.slice(0,10)} ~ {bt.end_date?.slice(0,10)} 收益: {bt.total_return} 夏普: {bt.sharpe_ratio}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
      {signalDetail && <SignalDetailModal signal={signalDetail} onClose={() => setSignalDetail(null)} />}
      {editSignal && <SignalEditModal signal={editSignal} onClose={()=>setEditSignal(null)} onSuccess={()=>{
        // 重新加载信号列表
        const token = localStorage.getItem('token');
        fetch(`/strategy/signals?strategy_id=${strategy.id}`, {
          headers: { 'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined }
        })
          .then(res => res.ok ? res.json() : [])
          .then(setSignals);
      }} />}
      {showAddSignal && <SignalAddModal strategyId={strategy.id} onClose={()=>setShowAddSignal(false)} onSuccess={()=>{
        setShowAddSignal(false);
        // 重新加载信号列表
        const token = localStorage.getItem('token');
        fetch(`/strategy/signals?strategy_id=${strategy.id}`, {
          headers: { 'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined }
        })
          .then(res => res.ok ? res.json() : [])
          .then(setSignals);
      }} />}
      {backtestDetail && <BacktestDetailModal backtest={backtestDetail} onClose={() => setBacktestDetail(null)} onRetry={() => {
        // 重新加载回测列表
        const token = localStorage.getItem('token');
        fetch(`/strategy/backtest?strategy_id=${strategy.id}`, {
          headers: { 'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined }
        })
          .then(res => res.ok ? res.json() : [])
          .then(setBacktests);
      }} />}
      {showAddBacktest && <BacktestFormModal strategyId={strategy.id} onClose={()=>setShowAddBacktest(false)} onSuccess={()=>{
        setShowAddBacktest(false);
        // 重新加载回测列表
        const token = localStorage.getItem('token');
        fetch(`/strategy/backtest?strategy_id=${strategy.id}`, {
          headers: { 'Authorization': token && token !== 'null' && token !== 'undefined' ? `Bearer ${token}` : undefined }
        })
          .then(res => res.ok ? res.json() : [])
          .then(setBacktests);
      }} />}
      <style>{`
        .modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.3); display:flex; align-items:center; justify-content:center; z-index:1000; }
        .modal { background:#000; padding:2rem; border-radius:8px; min-width:350px; max-width:90vw; max-height:90vh; overflow:auto; position:relative; }
        .modal-close { position:absolute; top:8px; right:12px; font-size:1.5rem; background:none; border:none; cursor:pointer; }
      `}</style>
    </div>
  );
}

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