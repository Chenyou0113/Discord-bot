#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 修復驗證腳本
測試修復後的雷達圖和空氣品質 API 連線
"""

import asyncio
import sys
import os
import json

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_radar_api_fix():
    """測試雷達圖 API 修復"""
    print("🌩️ 測試雷達圖 API 修復")
    print("-" * 40)
    
    try:
        from cogs.radar_commands import RadarCommands
        
        class MockBot:
            pass
        
        bot = MockBot()
        radar_cog = RadarCommands(bot)
        
        # 測試一般雷達圖
        print("🔍 測試一般雷達圖 API...")
        data = await radar_cog.fetch_radar_data()
        
        if data:
            print("✅ 一般雷達圖 API 連線成功")
            radar_info = radar_cog.parse_radar_data(data)
            if radar_info:
                print(f"  觀測時間: {radar_info.get('datetime', 'N/A')}")
                print(f"  圖片連結: {'有' if radar_info.get('image_url') else '無'}")
            else:
                print("⚠️ 資料解析失敗")
        else:
            print("❌ 一般雷達圖 API 連線失敗")
            
        # 測試大範圍雷達圖
        print("\n🔍 測試大範圍雷達圖 API...")
        large_data = await radar_cog.fetch_large_radar_data()
        
        if large_data:
            print("✅ 大範圍雷達圖 API 連線成功")
            large_radar_info = radar_cog.parse_radar_data(large_data)
            if large_radar_info:
                print(f"  觀測時間: {large_radar_info.get('datetime', 'N/A')}")
                print(f"  圖片連結: {'有' if large_radar_info.get('image_url') else '無'}")
            else:
                print("⚠️ 資料解析失敗")
        else:
            print("❌ 大範圍雷達圖 API 連線失敗")
            
        # 測試降雨雷達
        print("\n🔍 測試降雨雷達 API (樹林)...")
        rainfall_data = await radar_cog.fetch_rainfall_radar_data("樹林")
        
        if rainfall_data:
            print("✅ 降雨雷達 API 連線成功")
            rainfall_info = radar_cog.parse_rainfall_radar_data(rainfall_data)
            if rainfall_info:
                print(f"  觀測時間: {rainfall_info.get('datetime', 'N/A')}")
                print(f"  圖片連結: {'有' if rainfall_info.get('image_url') else '無'}")
            else:
                print("⚠️ 資料解析失敗")
        else:
            print("❌ 降雨雷達 API 連線失敗")
            
        return data and large_data and rainfall_data
        
    except Exception as e:
        print(f"❌ 雷達圖測試發生錯誤: {e}")
        return False

async def test_air_quality_api_fix():
    """測試空氣品質 API 修復"""
    print("\n🌬️ 測試空氣品質 API 修復")
    print("-" * 40)
    
    try:
        from cogs.air_quality_commands import AirQualityCommands
        
        class MockBot:
            pass
        
        bot = MockBot()
        air_cog = AirQualityCommands(bot)
        
        print("🔍 測試空氣品質 API...")
        data = await air_cog.fetch_air_quality_data()
        
        if data and 'records' in data:
            records = data['records']
            print(f"✅ 空氣品質 API 連線成功")
            print(f"  獲得 {len(records)} 筆記錄")
            
            if records:
                first_record = records[0]
                site_name = first_record.get('sitename', 'N/A')
                aqi = first_record.get('aqi', 'N/A')
                print(f"  範例測站: {site_name}, AQI: {aqi}")
                
            return True
        else:
            print("❌ 空氣品質 API 連線失敗或無資料")
            return False
            
    except Exception as e:
        print(f"❌ 空氣品質測試發生錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    print("🔧 API 修復驗證測試")
    print("=" * 50)
    
    # 測試雷達圖 API
    radar_success = await test_radar_api_fix()
    
    # 測試空氣品質 API
    air_success = await test_air_quality_api_fix()
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 測試結果摘要")
    print("=" * 50)
    
    print(f"🌩️ 雷達圖 API: {'✅ 修復成功' if radar_success else '❌ 仍有問題'}")
    print(f"🌬️ 空氣品質 API: {'✅ 修復成功' if air_success else '❌ 仍有問題'}")
    
    if radar_success and air_success:
        print("\n🎉 所有 API 修復成功！")
        print("💡 你現在可以正常使用以下指令：")
        print("  - /radar - 一般雷達圖")
        print("  - /radar_large - 大範圍雷達圖") 
        print("  - /rainfall_radar - 降雨雷達圖")
        print("  - /air_quality - 空氣品質查詢")
        return True
    else:
        print("\n⚠️ 部分 API 仍有問題，請檢查網路連線或 API 金鑰")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 執行測試時發生錯誤: {e}")
        sys.exit(1)
