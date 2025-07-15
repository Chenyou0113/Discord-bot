#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試自動氣象測站資料 API (O-A0001-001)
這個 API 應該包含實際的天氣觀測資料
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_weather_station_api():
    """測試自動氣象測站資料 API"""
    print("=" * 60)
    print("測試自動氣象測站資料 API (O-A0001-001)")
    print("=" * 60)
    
    # API 設定
    api_base = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    endpoint = "O-A0001-001"  # 自動氣象測站資料
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    url = f"{api_base}/{endpoint}"
    params = {
        "Authorization": authorization,
        "format": "JSON"
    }
    
    print(f"API URL: {url}")
    print("-" * 40)
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("正在發送 API 請求...")
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"回應狀態碼: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    print("✅ API 請求成功!")
                    print("-" * 40)
                    
                    # 檢查回應結構
                    if data.get('success') == 'true':
                        print("✅ API 回應格式正確")
                        
                        # 獲取觀測資料
                        records = data.get('records', {})
                        
                        # 先看看整體結構
                        print(f"Records 結構: {list(records.keys())}")
                        
                        # 檢查是否有 location 或其他資料
                        if 'location' in records:
                            location_data = records.get('location', [])
                            print(f"✅ 測站資料數量: {len(location_data)}")
                            
                            if location_data:
                                # 顯示前 3 個測站的詳細資訊
                                print("\n前 3 個測站的天氣觀測資料:")
                                print("-" * 60)
                                
                                for i, location in enumerate(location_data[:3], 1):
                                    location_name = location.get('locationName', 'N/A')
                                    station_id = location.get('stationId', 'N/A')
                                    
                                    print(f"{i}. {location_name} ({station_id})")
                                    
                                    # 檢查時間資訊
                                    time_info = location.get('time', {})
                                    if time_info:
                                        obs_time = time_info.get('obsTime', 'N/A')
                                        print(f"   觀測時間: {obs_time}")
                                    
                                    # 解析天氣要素
                                    weather_elements = location.get('weatherElement', [])
                                    
                                    if weather_elements:
                                        print("   天氣要素:")
                                        weather_info = {}
                                        
                                        for element in weather_elements:
                                            element_name = element.get('elementName', '')
                                            element_value = element.get('elementValue', 'N/A')
                                            unit = element.get('unit', '')
                                            weather_info[element_name] = {'value': element_value, 'unit': unit}
                                        
                                        # 顯示主要天氣資訊
                                        important_elements = [
                                            ('TEMP', '🌡️ 溫度'),
                                            ('HUMD', '💧 相對濕度'), 
                                            ('PRES', '📊 氣壓'),
                                            ('24R', '🌧️ 24小時累積雨量'),
                                            ('WDSD', '💨 風速'),
                                            ('WDIR', '🧭 風向'),
                                            ('WSGust', '💨 最大陣風'),
                                            ('Weather', '☁️ 天氣現象')
                                        ]
                                        
                                        for code, description in important_elements:
                                            if code in weather_info:
                                                value = weather_info[code]['value']
                                                unit = weather_info[code]['unit']
                                                if value != 'N/A' and value != '-99' and value != '-999':
                                                    print(f"     {description}: {value} {unit}")
                                    
                                    print()
                                
                                # 測試搜尋功能
                                print("測試搜尋功能 - 尋找包含特定關鍵字的測站:")
                                print("-" * 50)
                                
                                search_terms = ["台北", "板橋", "淡水", "桃園", "新竹"]
                                
                                for term in search_terms:
                                    matches = []
                                    for location in location_data:
                                        location_name = location.get('locationName', '')
                                        if term in location_name:
                                            matches.append(location)
                                    
                                    if matches:
                                        print(f"搜尋 '{term}': 找到 {len(matches)} 個測站")
                                        for match in matches[:2]:  # 顯示前2個
                                            name = match.get('locationName', 'N/A')
                                            station_id = match.get('stationId', 'N/A')
                                            
                                            # 獲取溫度資訊
                                            weather_elements = match.get('weatherElement', [])
                                            temp = 'N/A'
                                            for element in weather_elements:
                                                if element.get('elementName') == 'TEMP':
                                                    temp = element.get('elementValue', 'N/A')
                                                    break
                                            
                                            print(f"  • {name} ({station_id}) - 溫度: {temp}°C")
                                    else:
                                        print(f"搜尋 '{term}': 無符合結果")
                                print()
                        else:
                            print("❌ 回應中沒有 location 資料")
                            print(f"可用的資料結構: {list(records.keys())}")
                            
                            # 如果有其他結構，顯示一些資訊
                            for key, value in records.items():
                                if isinstance(value, list) and value:
                                    print(f"{key}: {len(value)} 項目")
                                elif isinstance(value, dict):
                                    print(f"{key}: {list(value.keys())}")
                    else:
                        print("❌ API 回應格式錯誤")
                        print(f"Success 狀態: {data.get('success')}")
                        
                        # 顯示部分回應內容用於調試
                        print("回應內容預覽:")
                        preview = json.dumps(data, ensure_ascii=False, indent=2)[:500]
                        print(preview + "...")
                        
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    content = await response.text()
                    print(f"錯誤內容: {content[:200]}...")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(test_weather_station_api())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
