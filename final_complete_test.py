#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整功能測試腳本
測試地震功能和氣象站功能是否正常工作
"""

import asyncio
import sys
import os

# 添加專案根目錄到 sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from cogs.info_commands_fixed_v4_clean import InfoCommands
from unittest.mock import AsyncMock, MagicMock

class MockBot:
    """模擬 Discord Bot"""
    def __init__(self):
        self.session = None
        self.loop = asyncio.get_event_loop()

class MockInteraction:
    """模擬 Discord Interaction"""
    def __init__(self):
        self.response = AsyncMock()
        self.followup = AsyncMock()

async def test_earthquake_functionality():
    """測試地震功能"""
    print("🔍 測試地震功能...")
    
    # 建立模擬環境
    mock_bot = MockBot()
    cog = InfoCommands(mock_bot)
    
    # 初始化 session
    await cog.init_aiohttp_session()
    
    try:
        # 測試一般地震資料獲取
        print("  ▶ 測試一般地震資料獲取...")
        eq_data = await cog.fetch_earthquake_data(small_area=False)
        if eq_data:
            print("  ✅ 一般地震資料獲取成功")
            
            # 測試地震資料格式化
            print("  ▶ 測試地震資料格式化...")
            embed = await cog.format_earthquake_data(eq_data)
            if embed:
                print("  ✅ 地震資料格式化成功")
                print(f"     標題: {embed.title}")
                print(f"     欄位數: {len(embed.fields)}")
            else:
                print("  ❌ 地震資料格式化失敗")
        else:
            print("  ❌ 一般地震資料獲取失敗")
        
        # 測試小區域地震資料獲取
        print("  ▶ 測試小區域地震資料獲取...")
        small_eq_data = await cog.fetch_earthquake_data(small_area=True)
        if small_eq_data:
            print("  ✅ 小區域地震資料獲取成功")
        else:
            print("  ❌ 小區域地震資料獲取失敗")
            
    except Exception as e:
        print(f"  ❌ 地震功能測試失敗: {str(e)}")
    
    finally:
        # 清理 session
        await cog.cog_unload()

async def test_weather_station_functionality():
    """測試氣象站功能"""
    print("\n🌡️ 測試氣象站功能...")
    
    # 建立模擬環境
    mock_bot = MockBot()
    cog = InfoCommands(mock_bot)
    
    # 初始化 session
    await cog.init_aiohttp_session()
    
    try:
        # 測試氣象站資料獲取
        print("  ▶ 測試氣象站資料獲取...")
        weather_data = await cog.fetch_weather_station_data()
        if weather_data:
            print("  ✅ 氣象站資料獲取成功")
            
            # 檢查資料結構
            records = weather_data.get('records', {})
            stations = records.get('Station', [])            print(f"     獲取到 {len(stations)} 個氣象站資料")
            
            if stations:
                # 測試格式化功能
                print("  ▶ 測試氣象站資料格式化...")
                
                # 測試全台概況
                embed = await cog.format_weather_station_data()
                if embed:
                    print("  ✅ 全台概況格式化成功")
                    print(f"     標題: {embed.title}")
                
                # 測試單一測站
                test_station_id = stations[0].get('StationId', '')
                if test_station_id:
                    embed = await cog.format_weather_station_data(station_id=test_station_id)
                    if embed:
                        print("  ✅ 單一測站格式化成功")
                    else:
                        print("  ❌ 單一測站格式化失敗")
                
                # 測試地區查詢
                embed = await cog.format_weather_station_data(location="台北")
                if embed:
                    print("  ✅ 地區查詢格式化成功")
                else:
                    print("  ❌ 地區查詢格式化失敗")
            else:
                print("  ⚠️  未獲取到氣象站資料")
        else:
            print("  ❌ 氣象站資料獲取失敗")
            
    except Exception as e:
        print(f"  ❌ 氣象站功能測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理 session
        await cog.cog_unload()

async def test_commands():
    """測試指令功能"""
    print("\n⚡ 測試指令功能...")
    
    # 建立模擬環境
    mock_bot = MockBot()
    cog = InfoCommands(mock_bot)
    
    # 初始化 session
    await cog.init_aiohttp_session()
    
    try:
        # 測試地震指令
        print("  ▶ 測試地震指令...")
        mock_interaction = MockInteraction()
        await cog.earthquake(mock_interaction, "normal")
        print("  ✅ 地震指令執行完成")
        
        # 測試氣象站指令
        print("  ▶ 測試氣象站指令...")
        mock_interaction = MockInteraction()
        await cog.weather_station(mock_interaction)
        print("  ✅ 氣象站指令執行完成")
        
    except Exception as e:
        print(f"  ❌ 指令測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理 session
        await cog.cog_unload()

async def main():
    """主要測試函數"""
    print("🚀 開始完整功能測試...")
    print("=" * 50)
    
    # 依序測試各項功能
    await test_earthquake_functionality()
    await test_weather_station_functionality()
    await test_commands()
    
    print("\n" + "=" * 50)
    print("✨ 完整功能測試完成！")

if __name__ == "__main__":
    asyncio.run(main())
