#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版功能測試腳本
測試地震功能和氣象站功能是否正常工作
"""

import asyncio
import sys
import os

# 添加專案根目錄到 sys.path (從 tests 目錄往上一層)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from cogs.info_commands_fixed_v4_clean import InfoCommands
from unittest.mock import AsyncMock, MagicMock

class MockBot:
    """模擬 Discord Bot"""
    def __init__(self):
        self.session = None
        self.loop = asyncio.get_event_loop()

async def test_basic_functionality():
    """基本功能測試"""
    print("🚀 開始基本功能測試...")
    print("=" * 50)
    
    # 建立模擬環境
    mock_bot = MockBot()
    cog = InfoCommands(mock_bot)
    
    # 初始化 session
    await cog.init_aiohttp_session()
    
    try:
        # 測試地震資料獲取
        print("🔍 測試地震資料獲取...")
        eq_data = await cog.fetch_earthquake_data(small_area=False)
        if eq_data:
            print("  ✅ 地震資料獲取成功")
        else:
            print("  ❌ 地震資料獲取失敗")
        
        # 測試氣象站資料獲取
        print("\n🌡️ 測試氣象站資料獲取...")
        weather_data = await cog.fetch_weather_station_data()
        if weather_data:
            print("  ✅ 氣象站資料獲取成功")
            records = weather_data.get('records', {})
            stations = records.get('Station', [])
            print(f"  📊 獲取到 {len(stations)} 個氣象站資料")
        else:
            print("  ❌ 氣象站資料獲取失敗")
        
        # 測試氣象站格式化
        print("\n📋 測試氣象站格式化...")
        embed = await cog.format_weather_station_data()
        if embed:
            print("  ✅ 氣象站格式化成功")
            print(f"  📝 標題: {embed.title}")
        else:
            print("  ❌ 氣象站格式化失敗")
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理 session
        await cog.cog_unload()
    
    print("\n" + "=" * 50)
    print("✨ 基本功能測試完成！")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
