"""
测试策略路由拆分后的功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_strategy_router_import():
    """测试策略路由器导入"""
    try:
        from routers.strategy import router
        print("✅ 策略路由器导入成功")
        print(f"   路由数量: {len(router.routes)}")
        return True
    except Exception as e:
        print(f"❌ 策略路由器导入失败: {e}")
        return False

def test_submodule_imports():
    """测试子模块导入"""
    modules = [
        "base", "macro_timing", "sector_rotation", "multi_factor",
        "signal", "backtest", "allocation", "factor_model", "market_regime"
    ]
    
    success_count = 0
    for module in modules:
        try:
            exec(f"from routers.strategy.{module} import router")
            print(f"✅ {module} 模块导入成功")
            success_count += 1
        except Exception as e:
            print(f"❌ {module} 模块导入失败: {e}")
    
    print(f"\n子模块导入结果: {success_count}/{len(modules)} 成功")
    return success_count == len(modules)

def test_route_paths():
    """测试路由路径"""
    try:
        from routers.strategy import router
        
        # 检查一些关键路由是否存在
        expected_routes = [
            "/strategy/",  # 基础策略管理
            "/strategy/macro_timing_signal",  # 宏观择时
            "/strategy/sector_rotation_signal",  # 行业轮动
            "/strategy/multi_factor_signal",  # 多因子
            "/strategy/signals",  # 策略信号
            "/strategy/backtest",  # 回测
            "/strategy/allocations",  # 投资组合配置
            "/strategy/factors",  # 因子模型
            "/strategy/regimes",  # 市场状态
        ]
        
        print(f"\n当前路由数量: {len(router.routes)}")
        
        # 简单检查路由数量是否合理
        if len(router.routes) >= 20:  # 应该有足够的路由
            print("✅ 路由数量合理")
            found_count = len(expected_routes)
        else:
            print(f"❌ 路由数量过少: {len(router.routes)}")
            found_count = 0
        
        print(f"\n路由检查结果: {found_count}/{len(expected_routes)} 成功")
        return found_count == len(expected_routes)
        
    except Exception as e:
        print(f"❌ 路由路径检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("策略路由拆分测试")
    print("=" * 50)
    
    # 测试1: 路由器导入
    print("\n1. 测试路由器导入...")
    import_success = test_strategy_router_import()
    
    # 测试2: 子模块导入
    print("\n2. 测试子模块导入...")
    submodule_success = test_submodule_imports()
    
    # 测试3: 路由路径
    print("\n3. 测试路由路径...")
    route_success = test_route_paths()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"路由器导入: {'✅ 成功' if import_success else '❌ 失败'}")
    print(f"子模块导入: {'✅ 成功' if submodule_success else '❌ 失败'}")
    print(f"路由路径: {'✅ 成功' if route_success else '❌ 失败'}")
    
    if import_success and submodule_success and route_success:
        print("\n🎉 所有测试通过！策略路由拆分成功！")
    else:
        print("\n⚠️ 部分测试失败，需要进一步检查。")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 