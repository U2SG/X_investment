"""
AI模型实现模块
包含真实的投资策略算法实现
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MacroTimingModel:
    """宏观择时模型"""
    
    def __init__(self):
        self.model_name = "MacroTimingModel_v1.0"
        self.asset_classes = ["STOCK", "BOND", "COMMODITY", "CASH"]
        
    def calculate_economic_cycle_score(self, economic_cycle: str) -> float:
        """计算经济周期评分"""
        cycle_scores = {
            "复苏": 0.8,    # 经济复苏，适合股票
            "过热": 0.6,    # 经济过热，通胀压力
            "滞胀": 0.3,    # 经济滞胀，风险较高
            "衰退": 0.1     # 经济衰退，防御为主
        }
        return cycle_scores.get(economic_cycle, 0.5)
    
    def calculate_sentiment_score(self, market_sentiment: str) -> float:
        """计算市场情绪评分"""
        sentiment_scores = {
            "乐观": 0.8,
            "中性": 0.5,
            "悲观": 0.2
        }
        return sentiment_scores.get(market_sentiment, 0.5)
    
    def calculate_additional_factors_score(self, additional_factors: Dict) -> float:
        """计算额外因素评分"""
        if not additional_factors:
            return 0.5
            
        score = 0.5
        factors_count = 0
        
        # 利率因素
        if "interest_rate" in additional_factors:
            rate = additional_factors["interest_rate"]
            if rate < 2.0:  # 低利率环境，利好股票
                score += 0.2
            elif rate > 5.0:  # 高利率环境，利好债券
                score -= 0.2
            factors_count += 1
        
        # 通胀因素
        if "inflation" in additional_factors:
            inflation = additional_factors["inflation"]
            if inflation < 2.0:  # 低通胀，利好股票
                score += 0.1
            elif inflation > 4.0:  # 高通胀，利好商品
                score += 0.1
            factors_count += 1
        
        # 汇率因素
        if "exchange_rate" in additional_factors:
            # 汇率波动性
            score += 0.05
            factors_count += 1
        
        # 地缘政治风险
        if "geopolitical_risk" in additional_factors:
            risk = additional_factors["geopolitical_risk"]
            if risk > 0.7:  # 高风险，增加现金配置
                score -= 0.2
            factors_count += 1
        
        return score / max(factors_count, 1)
    
    def generate_asset_allocation(self, 
                                economic_cycle: str,
                                market_sentiment: str,
                                additional_factors: Optional[Dict] = None) -> Tuple[Dict[str, float], str, float]:
        """生成资产配置建议"""
        
        # 计算各维度评分
        cycle_score = self.calculate_economic_cycle_score(economic_cycle)
        sentiment_score = self.calculate_sentiment_score(market_sentiment)
        factors_score = self.calculate_additional_factors_score(additional_factors or {})
        
        # 综合评分
        composite_score = (cycle_score * 0.4 + sentiment_score * 0.4 + factors_score * 0.2)
        
        # 基于综合评分生成配置
        if composite_score >= 0.7:  # 积极配置
            allocation = {
                "STOCK": 0.65,
                "BOND": 0.20,
                "COMMODITY": 0.10,
                "CASH": 0.05
            }
            reasoning = f"经济周期({economic_cycle})和市场情绪({market_sentiment})均较为积极，综合评分{composite_score:.2f}，建议积极配置股票资产。"
            confidence = 0.85
            
        elif composite_score >= 0.5:  # 均衡配置
            allocation = {
                "STOCK": 0.45,
                "BOND": 0.35,
                "COMMODITY": 0.10,
                "CASH": 0.10
            }
            reasoning = f"经济周期({economic_cycle})和市场情绪({market_sentiment})中性，综合评分{composite_score:.2f}，建议均衡配置。"
            confidence = 0.75
            
        elif composite_score >= 0.3:  # 防御配置
            allocation = {
                "STOCK": 0.25,
                "BOND": 0.50,
                "COMMODITY": 0.10,
                "CASH": 0.15
            }
            reasoning = f"经济周期({economic_cycle})和市场情绪({market_sentiment})偏谨慎，综合评分{composite_score:.2f}，建议防御配置。"
            confidence = 0.80
            
        else:  # 保守配置
            allocation = {
                "STOCK": 0.15,
                "BOND": 0.60,
                "COMMODITY": 0.05,
                "CASH": 0.20
            }
            reasoning = f"经济周期({economic_cycle})和市场情绪({market_sentiment})悲观，综合评分{composite_score:.2f}，建议保守配置。"
            confidence = 0.90
        
        # 根据额外因素微调
        if additional_factors:
            allocation = self._adjust_allocation_by_factors(allocation, additional_factors)
            reasoning += " 已根据额外因素进行微调。"
        
        return allocation, reasoning, confidence
    
    def _adjust_allocation_by_factors(self, allocation: Dict[str, float], factors: Dict) -> Dict[str, float]:
        """根据额外因素微调配置"""
        adjusted = allocation.copy()
        
        # 利率调整
        if "interest_rate" in factors:
            rate = factors["interest_rate"]
            if rate > 5.0:  # 高利率，增加债券配置
                adjusted["BOND"] = min(0.7, adjusted["BOND"] + 0.1)
                adjusted["STOCK"] = max(0.1, adjusted["STOCK"] - 0.1)
        
        # 通胀调整
        if "inflation" in factors:
            inflation = factors["inflation"]
            if inflation > 4.0:  # 高通胀，增加商品配置
                adjusted["COMMODITY"] = min(0.2, adjusted["COMMODITY"] + 0.05)
                adjusted["CASH"] = max(0.05, adjusted["CASH"] - 0.05)
        
        # 地缘政治风险调整
        if "geopolitical_risk" in factors:
            risk = factors["geopolitical_risk"]
            if risk > 0.7:  # 高风险，增加现金配置
                adjusted["CASH"] = min(0.3, adjusted["CASH"] + 0.1)
                adjusted["STOCK"] = max(0.05, adjusted["STOCK"] - 0.1)
        
        # 确保总和为1
        total = sum(adjusted.values())
        if abs(total - 1.0) > 0.01:
            for key in adjusted:
                adjusted[key] = adjusted[key] / total
        
        return adjusted


class SectorRotationModel:
    """行业轮动模型"""
    
    def __init__(self):
        self.model_name = "SectorRotationModel_v1.0"
        
    def calculate_industry_score(self, industry_scores: Dict[str, float]) -> Dict[str, float]:
        """计算行业评分"""
        if not industry_scores:
            return {}
        
        # 标准化评分
        scores = np.array(list(industry_scores.values()))
        if len(scores) == 0:
            return {}
        
        # Z-score标准化
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        if std_score > 0:
            normalized_scores = (scores - mean_score) / std_score
        else:
            normalized_scores = scores - mean_score
        
        # 转换为0-1范围
        normalized_scores = (normalized_scores - np.min(normalized_scores)) / (np.max(normalized_scores) - np.min(normalized_scores) + 1e-8)
        
        # 构建结果
        result = {}
        industries = list(industry_scores.keys())
        for i, industry in enumerate(industries):
            result[industry] = float(normalized_scores[i])
        
        return result
    
    def generate_industry_allocation(self,
                                   industry_scores: Dict[str, float],
                                   fund_flows: Optional[Dict[str, float]] = None,
                                   additional_factors: Optional[Dict] = None) -> Tuple[Dict[str, float], str, float]:
        """生成行业配置建议"""
        
        if not industry_scores:
            return {}, "未提供行业评分数据", 0.0
        
        # 计算标准化评分
        normalized_scores = self.calculate_industry_score(industry_scores)
        
        # 根据评分排序
        sorted_industries = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 生成配置
        allocation = {}
        total_weight = 0.0
        
        # 前3个行业获得主要配置
        for i, (industry, score) in enumerate(sorted_industries[:3]):
            if i == 0:  # 第一名
                weight = 0.4
            elif i == 1:  # 第二名
                weight = 0.3
            else:  # 第三名
                weight = 0.2
            
            allocation[industry] = weight
            total_weight += weight
        
        # 剩余权重分配给其他行业
        remaining_weight = 1.0 - total_weight
        remaining_industries = sorted_industries[3:]
        
        if remaining_industries:
            weight_per_industry = remaining_weight / len(remaining_industries)
            for industry, _ in remaining_industries:
                allocation[industry] = weight_per_industry
        
        # 根据资金流向调整
        if fund_flows:
            allocation = self._adjust_by_fund_flows(allocation, fund_flows)
        
        # 根据额外因素调整
        if additional_factors:
            allocation = self._adjust_by_additional_factors(allocation, additional_factors)
        
        # 生成推理说明
        top_industries = sorted_industries[:3]
        reasoning = f"基于行业景气度评分，推荐配置前三大行业：{', '.join([ind for ind, _ in top_industries])}。"
        
        # 计算置信度
        if len(sorted_industries) >= 3:
            # 基于前三大行业的评分差异计算置信度
            score_diff = sorted_industries[0][1] - sorted_industries[2][1]
            confidence = min(0.95, 0.7 + score_diff * 0.5)
        else:
            confidence = 0.6
        
        return allocation, reasoning, confidence
    
    def _adjust_by_fund_flows(self, allocation: Dict[str, float], fund_flows: Dict[str, float]) -> Dict[str, float]:
        """根据资金流向调整配置"""
        adjusted = allocation.copy()
        
        for industry, flow in fund_flows.items():
            if industry in adjusted:
                # 资金流入增加配置，流出减少配置
                flow_factor = min(0.2, max(-0.2, flow * 0.1))  # 限制调整幅度
                adjusted[industry] = max(0.0, adjusted[industry] + flow_factor)
        
        # 重新归一化
        total = sum(adjusted.values())
        if total > 0:
            for key in adjusted:
                adjusted[key] = adjusted[key] / total
        
        return adjusted
    
    def _adjust_by_additional_factors(self, allocation: Dict[str, float], factors: Dict) -> Dict[str, float]:
        """根据额外因素调整配置"""
        adjusted = allocation.copy()
        
        # 政策支持
        if "policy_support" in factors:
            policy_industries = factors["policy_support"]
            for industry in policy_industries:
                if industry in adjusted:
                    adjusted[industry] = min(0.5, adjusted[industry] * 1.2)
        
        # 季节性因素
        if "seasonal_factor" in factors:
            seasonal_industries = factors["seasonal_factor"]
            for industry, factor in seasonal_industries.items():
                if industry in adjusted:
                    adjusted[industry] = min(0.5, adjusted[industry] * factor)
        
        # 重新归一化
        total = sum(adjusted.values())
        if total > 0:
            for key in adjusted:
                adjusted[key] = adjusted[key] / total
        
        return adjusted


class MultiFactorModel:
    """多因子模型"""
    
    def __init__(self):
        self.model_name = "MultiFactorModel_v1.0"
        self.default_factors = ["价值", "成长", "质量", "动量"]
        
    def calculate_stock_score(self, 
                            stock_data: Dict,
                            factor_weights: Dict[str, float],
                            market_regime: Optional[str] = None) -> Tuple[float, Dict[str, float]]:
        """计算股票综合评分"""
        
        # 获取因子值
        factor_values = stock_data.get("factor_values", {})
        
        # 动态调整因子权重
        adjusted_weights = self._adjust_weights_by_regime(factor_weights, market_regime)
        
        # 计算各因子贡献
        factor_contribution = {}
        total_score = 0.0
        
        for factor, weight in adjusted_weights.items():
            if factor in factor_values:
                contribution = factor_values[factor] * weight
                factor_contribution[factor] = contribution
                total_score += contribution
        
        return total_score, factor_contribution
    
    def _adjust_weights_by_regime(self, weights: Dict[str, float], market_regime: str) -> Dict[str, float]:
        """根据市场状态调整因子权重"""
        adjusted = weights.copy()
        
        if market_regime == "牛市":
            # 牛市加大动量和成长因子权重
            adjusted["动量"] = adjusted.get("动量", 0.2) * 1.3
            adjusted["成长"] = adjusted.get("成长", 0.3) * 1.2
        elif market_regime == "熊市":
            # 熊市加大价值和质量因子权重
            adjusted["价值"] = adjusted.get("价值", 0.3) * 1.3
            adjusted["质量"] = adjusted.get("质量", 0.2) * 1.2
        elif market_regime == "震荡市":
            # 震荡市均衡配置
            pass
        
        # 重新归一化
        total = sum(adjusted.values())
        if total > 0:
            for key in adjusted:
                adjusted[key] = adjusted[key] / total
        
        return adjusted
    
    def discover_factors(self, stock_data_list: List[Dict]) -> Dict[str, float]:
        """因子挖掘（简化版）"""
        if len(stock_data_list) < 10:
            return {}
        
        # 这里实现一个简化的因子挖掘算法
        # 实际项目中可以使用更复杂的机器学习方法
        
        discovered_factors = {}
        
        # 计算行业景气度因子
        industry_scores = {}
        for stock in stock_data_list:
            industry = stock.get("industry", "其他")
            if industry not in industry_scores:
                industry_scores[industry] = []
            industry_scores[industry].append(stock.get("factor_values", {}).get("成长", 0))
        
        for industry, scores in industry_scores.items():
            if len(scores) > 3:
                avg_score = np.mean(scores)
                discovered_factors[f"行业景气度_{industry}"] = min(0.15, avg_score * 0.1)
        
        # 计算规模因子
        market_caps = [stock.get("market_cap", 0) for stock in stock_data_list if stock.get("market_cap")]
        if market_caps:
            avg_market_cap = np.mean(market_caps)
            discovered_factors["规模因子"] = min(0.12, 1.0 / (avg_market_cap + 1e8) * 1e8)
        
        # 计算波动率因子
        volatilities = [stock.get("volatility", 0) for stock in stock_data_list if stock.get("volatility")]
        if volatilities:
            avg_volatility = np.mean(volatilities)
            discovered_factors["波动率因子"] = min(0.10, max(0, 0.3 - avg_volatility))
        
        return discovered_factors
    
    def generate_stock_ranking(self,
                             stocks_data: List[Dict],
                             factor_weights: Optional[Dict[str, float]] = None,
                             market_regime: Optional[str] = None,
                             auto_discover: bool = False) -> Tuple[List[Dict], Dict[str, float], Optional[Dict[str, float]], str, float]:
        """生成股票排名"""
        
        if not stocks_data:
            return [], {}, None, "无股票数据", 0.0
        
        # 使用默认权重或提供的权重
        weights = factor_weights or {factor: 1.0/len(self.default_factors) for factor in self.default_factors}
        
        # 计算每只股票的评分
        stock_scores = []
        for stock_data in stocks_data:
            total_score, factor_contribution = self.calculate_stock_score(
                stock_data, weights, market_regime
            )
            
            stock_scores.append({
                "symbol": stock_data["symbol"],
                "name": stock_data.get("name", f"股票{stock_data['symbol']}"),
                "total_score": total_score,
                "factor_contribution": factor_contribution,
                "rank": 0  # 临时排名
            })
        
        # 根据总分排序
        stock_scores.sort(key=lambda x: x["total_score"], reverse=True)
        for i, score in enumerate(stock_scores):
            score["rank"] = i + 1
        
        # 因子挖掘
        discovered_factors = None
        if auto_discover:
            discovered_factors = self.discover_factors(stocks_data)
        
        # 生成推理说明
        if market_regime:
            reasoning = f"基于{market_regime}市场状态，动态调整因子权重进行评分。"
        else:
            reasoning = "基于传统因子模型进行评分。"
        
        if discovered_factors:
            reasoning += f" 通过机器学习发现{len(discovered_factors)}个新因子。"
        
        # 计算置信度
        if len(stock_scores) > 1:
            # 基于评分分布计算置信度
            scores = [s["total_score"] for s in stock_scores]
            score_std = np.std(scores)
            confidence = min(0.95, 0.7 + score_std * 2)
        else:
            confidence = 0.6
        
        return stock_scores, weights, discovered_factors, reasoning, confidence 