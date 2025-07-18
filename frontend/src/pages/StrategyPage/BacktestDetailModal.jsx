// 回测详情弹窗组件
// props:
//   backtest: 回测对象
//   onClose: 关闭弹窗回调
//   onRetry: （可选）重试回测回调

import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';

// BacktestDetailModal: 回测详情弹窗，含净值曲线和重试功能
export default function BacktestDetailModal({ backtest, onClose, onRetry }) {
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