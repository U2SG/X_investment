import React, { useState, useEffect } from 'react';
import HealthCheck from './HealthCheck';
import LoginForm from './LoginForm';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import AssetsPage from './pages/AssetsPage';
import TagsPage from './pages/TagsPage';
import PortfoliosPage from './pages/PortfoliosPage';
import RiskAssessmentPage from './pages/RiskAssessmentPage';
import StrategyPage from './pages/StrategyPage';
import MarketDataPage from './pages/MarketDataPage';
import FeatureStorePage from './pages/FeatureStorePage';

function App() {
  // 用户认证状态
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  
  // 检查是否已登录
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
      // 可以在这里获取用户信息
    }
  }, []);
  
  // 处理登录成功
  const handleLoginSuccess = (data) => {
    setIsLoggedIn(true);
    // 可以在这里获取并设置用户数据
  };
  
  // 处理登出
  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setUserData(null);
  };

  return (
    <Router>
      <div className="app-container"> {/* 居中容器 */}
        <div className="app">
          <header className="app-header">
            <h1>X-智投</h1>
            {isLoggedIn && (
              <button onClick={handleLogout} className="logout-button">
                退出账户
              </button>
            )}
          </header>
          {isLoggedIn && (
            <nav className="app-nav">
              <Link to="/assets">资产管理</Link>
              <Link to="/tags">标签管理</Link>
              <Link to="/portfolios">投资组合管理</Link>
              <Link to="/strategy">策略管理</Link>
              <Link to="/risk">风险测评</Link>
              <Link to="/market-data">市场数据</Link>
              <Link to="/feature-store">特征库</Link>
            </nav>
          )}
          <main className="app-content">
            {isLoggedIn ? (
              <Routes>
                <Route path="/assets" element={<AssetsPage />} />
                <Route path="/tags" element={<TagsPage />} />
                <Route path="/portfolios" element={<PortfoliosPage />} />
                <Route path="/strategy" element={<StrategyPage />} />
                <Route path="/risk" element={<RiskAssessmentPage />} />
                <Route path="/market-data" element={<MarketDataPage />} />
                <Route path="/feature-store" element={<FeatureStorePage />} />
              </Routes>
            ) : (
              <LoginForm onLoginSuccess={handleLoginSuccess} />
            )}
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;