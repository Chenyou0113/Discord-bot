#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速 API 修復測試
"""

import asyncio
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def quick_test():
    """快速測試"""
    
    print("🔧 快速 API 修復測試")
    print("=" * 30)
    
    # 測試雷達圖模組載入
    try:
        from cogs.radar_commands import RadarCommands
        print("✅ 雷達圖模組載入成功")
        
        class MockBot:
            pass
        
        bot = MockBot()
        radar_cog = RadarCommands(bot)
        
        # 快速測試樹林雷達
        data = await radar_cog.fetch_rainfall_radar_data("樹林")
        if data:
            info = radar_cog.parse_rainfall_radar_data(data)
            if info and info.get('image_url'):
                print("✅ 降雨雷達功能正常")
            else:
                print("⚠️ 降雨雷達解析問題")
        else:
            print("❌ 降雨雷達連線失敗")
            
    except Exception as e:
        print(f"❌ 雷達圖測試失敗: {e}")
        
    # 測試空氣品質模組載入
    try:
        from cogs.air_quality_commands import AirQualityCommands
        print("✅ 空氣品質模組載入成功")
        
        air_cog = AirQualityCommands(bot)
        
        # 快速測試API連線
        data = await air_cog.fetch_air_quality_data()
        if data and 'records' in data and data['records']:
            print("✅ 空氣品質 API 連線正常")
        else:
            print("⚠️ 空氣品質 API 可能有問題")
            
    except Exception as e:
        print(f"❌ 空氣品質測試失敗: {e}")
    
    print("\n✅ 快速測試完成")

if __name__ == "__main__":
    asyncio.run(quick_test())
