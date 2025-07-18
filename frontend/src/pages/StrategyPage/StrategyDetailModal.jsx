// 策略详情弹窗组件
// props:
//   strategy: 当前策略对象
//   onClose: 关闭弹窗回调

import React, { useState, useEffect } from 'react';
import SignalDetailModal from './SignalDetailModal';
import SignalEditModal from './SignalEditModal';
import SignalAddModal from './SignalAddModal';
import BacktestDetailModal from './BacktestDetailModal';
import BacktestFormModal from './BacktestFormModal';

// StrategyDetailModal: 策略详情弹窗，含信号、回测列表及相关弹窗
export default function StrategyDetailModal({ strategy, onClose }) {
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