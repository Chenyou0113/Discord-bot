#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空氣品質修復驗證
"""

import asyncio
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_air_quality_fix():
    """測試空氣品質修復"""
    
    print("🌬️ 測試空氣品質 API 修復")
    print("-" * 30)
    
    try:
        from cogs.air_quality_commands import AirQualityCommands
        
        class MockBot:
            pass
        
        bot = MockBot()
        air_cog = AirQualityCommands(bot)
        
        print("✅ 模組載入成功")
        print("🔍 測試 API 連線...")
        
        data = await air_cog.fetch_air_quality_data()
        
        if data and 'records' in data:
            records = data['records']
            print(f"✅ API 連線成功！")
            print(f"📊 獲得 {len(records)} 筆空氣品質記錄")
            
            if records:
                first_record = records[0]
                site_name = first_record.get('sitename', 'N/A')
                aqi = first_record.get('aqi', 'N/A')
                print(f"📍 範例測站: {site_name}, AQI: {aqi}")
                
            return True
        else:
            print("❌ API 連線失敗或無資料")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

async def main():
    """主函數"""
    success = await test_air_quality_fix()
    
    print("\n" + "-" * 30)
    if success:
        print("🎉 空氣品質 API 修復成功！")
        print("💡 你現在可以使用 /air_quality 指令")
    else:
        print("⚠️ 空氣品質 API 仍有問題")
        print("🔧 可能需要進一步排查網路問題")

if __name__ == "__main__":
    asyncio.run(main())
