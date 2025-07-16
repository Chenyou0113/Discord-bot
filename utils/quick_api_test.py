#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速新 API 測試
"""

import requests
import json

try:
    print("正在請求新水利防災監控影像 API...")
    url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    response = requests.get(url, timeout=60)
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        if content.startswith('\ufeff'):
            content = content[1:]
        
        data = json.loads(content)
        print(f"資料筆數: {len(data)}")
        
        if data:
            first = data[0]
            print("第一筆資料欄位:")
            for k, v in first.items():
                if len(str(v)) > 50:
                    v = str(v)[:50] + "..."
                print(f"  {k}: {v}")
            
            # 檢查是否有名稱
            name_fields = ['VideoSurveillanceStationName', 'CameraName', 'name', 'title']
            found_name = False
            for field in name_fields:
                if first.get(field):
                    print(f"\n找到名稱欄位: {field} = {first[field]}")
                    found_name = True
                    break
            
            if not found_name:
                print("\n未找到名稱欄位")
            
            # 檢查縣市資訊
            county_field = 'CountiesAndCitiesWhereTheMonitoringPointsAreLocated'
            if first.get(county_field):
                print(f"縣市欄位: {county_field} = {first[county_field]}")
            
except Exception as e:
    print(f"錯誤: {e}")

print("測試完成")
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
