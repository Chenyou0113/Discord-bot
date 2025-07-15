#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復 weather 指令衝突問題
"""

import sys
import os
import logging

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定日誌
logging.basicConfig(level=logging.INFO)

def test_cog_imports():
    """測試 Cog 匯入"""
    print("=" * 60)
    print("測試 Cog 匯入和指令衝突修復")
    print("=" * 60)
    
    try:
        # 測試匯入各個 Cog
        cogs_to_test = [
            'cogs.info_commands_fixed_v4_clean',
            'cogs.weather_commands',
            'cogs.reservoir_commands'
        ]
        
        for cog_name in cogs_to_test:
            try:
                print(f"\n📦 測試匯入 {cog_name}...")
                
                if cog_name == 'cogs.info_commands_fixed_v4_clean':
                    from cogs.info_commands_fixed_v4_clean import InfoCommands
                    print(f"✅ 成功匯入 InfoCommands")
                    
                    # 檢查是否還有 weather 指令
                    info_cog = InfoCommands(None)
                    commands = [cmd for cmd in dir(info_cog) if hasattr(getattr(info_cog, cmd), 'callback')]
                    print(f"   找到指令: {len(commands)} 個")
                    
                    weather_commands = [cmd for cmd in commands if 'weather' in cmd.lower()]
                    if weather_commands:
                        print(f"❌ 仍然找到 weather 相關指令: {weather_commands}")
                    else:
                        print(f"✅ 已移除所有 weather 相關指令")
                
                elif cog_name == 'cogs.weather_commands':
                    from cogs.weather_commands import WeatherCommands
                    print(f"✅ 成功匯入 WeatherCommands")
                    
                    # 檢查 weather 指令
                    weather_cog = WeatherCommands(None)
                    if hasattr(weather_cog, 'weather'):
                        print(f"✅ WeatherCommands 包含 weather 指令")
                    else:
                        print(f"❌ WeatherCommands 缺少 weather 指令")
                
                elif cog_name == 'cogs.reservoir_commands':
                    from cogs.reservoir_commands import ReservoirCommands
                    print(f"✅ 成功匯入 ReservoirCommands")
                    
                    # 檢查新的水利監視器功能
                    reservoir_cog = ReservoirCommands(None)
                    if hasattr(reservoir_cog, 'water_disaster_cameras'):
                        print(f"✅ ReservoirCommands 包含 water_cameras 指令")
                    else:
                        print(f"❌ ReservoirCommands 缺少 water_cameras 指令")
                
            except Exception as e:
                print(f"❌ 匯入 {cog_name} 失敗: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n" + "=" * 60)
        print("指令衝突檢查")
        print("=" * 60)
        
        # 檢查是否還有指令衝突
        try:
            from cogs.info_commands_fixed_v4_clean import InfoCommands
            from cogs.weather_commands import WeatherCommands
            
            info_cog = InfoCommands(None)
            weather_cog = WeatherCommands(None)
            
            # 檢查 weather 指令
            info_has_weather = hasattr(info_cog, 'weather')
            weather_has_weather = hasattr(weather_cog, 'weather')
            
            print(f"InfoCommands 有 weather 指令: {'是' if info_has_weather else '否'}")
            print(f"WeatherCommands 有 weather 指令: {'是' if weather_has_weather else '否'}")
            
            if info_has_weather and weather_has_weather:
                print("❌ 指令衝突仍然存在！")
            elif weather_has_weather and not info_has_weather:
                print("✅ 指令衝突已解決，weather 指令只在 WeatherCommands 中")
            else:
                print("⚠️ 可能存在其他問題")
        
        except Exception as e:
            print(f"❌ 指令衝突檢查失敗: {str(e)}")
        
        print(f"\n" + "=" * 60)
        print("測試完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    test_cog_imports()

if __name__ == "__main__":
    main()
