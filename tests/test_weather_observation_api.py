#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試中央氣象署天氣觀測資料 API
查詢實際的天氣資訊（溫度、濕度、降雨量等）
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_weather_observation_api():
    """測試天氣觀測資料 API"""
    print("=" * 60)
    print("測試天氣觀測資料 API")
    print("=" * 60)
    
    # API 設定 - 自動氣象測站觀測資料
    api_base = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    endpoint = "O-A0003-001"  # 自動氣象測站觀測資料
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    url = f"{api_base}/{endpoint}"
    params = {
        "Authorization": authorization,
        "format": "JSON"
    }
    
    print(f"API URL: {url}")
    print(f"參數: {params}")
    print("-" * 40)
    
    try:
        # 設定 SSL 上下文
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
                        location_data = records.get('location', [])
                        
                        print(f"✅ 測站資料數量: {len(location_data)}")
                        
                        if location_data:
                            # 顯示前 5 個測站的天氣資訊
                            print("\n前 5 個測站的天氣觀測資料:")
                            print("-" * 60)
                            
                            for i, location in enumerate(location_data[:5], 1):
                                location_name = location.get('locationName', 'N/A')
                                station_id = location.get('stationId', 'N/A')
                                obs_time = location.get('time', {}).get('obsTime', 'N/A')
                                
                                print(f"{i}. {location_name} ({station_id})")
                                print(f"   觀測時間: {obs_time}")
                                
                                # 解析天氣要素
                                weather_elements = location.get('weatherElement', [])
                                weather_data = {}
                                
                                for element in weather_elements:
                                    element_name = element.get('elementName', '')
                                    element_value = element.get('elementValue', 'N/A')
                                    weather_data[element_name] = element_value
                                
                                # 顯示主要天氣資訊
                                temp = weather_data.get('TEMP', 'N/A')  # 溫度
                                humidity = weather_data.get('HUMD', 'N/A')  # 濕度
                                pressure = weather_data.get('PRES', 'N/A')  # 氣壓
                                wind_speed = weather_data.get('WDSD', 'N/A')  # 風速
                                wind_dir = weather_data.get('WDIR', 'N/A')  # 風向
                                rainfall = weather_data.get('H_24R', 'N/A')  # 24小時累積雨量
                                
                                print(f"   🌡️ 溫度: {temp}°C")
                                print(f"   💧 濕度: {humidity}%")
                                print(f"   📊 氣壓: {pressure} hPa")
                                print(f"   💨 風速: {wind_speed} m/s")
                                print(f"   🧭 風向: {wind_dir}°")
                                print(f"   🌧️ 24小時雨量: {rainfall} mm")
                                print()
                            
                            # 測試特定測站搜尋
                            print("測試特定測站搜尋:")
                            print("-" * 40)
                            
                            test_stations = ["板橋", "台北", "淡水", "桃園"]
                            
                            for station_name in test_stations:
                                matches = []
                                for location in location_data:
                                    if station_name in location.get('locationName', ''):
                                        matches.append(location)
                                
                                print(f"搜尋 '{station_name}': 找到 {len(matches)} 個結果")
                                
                                for match in matches[:2]:  # 顯示前2個結果
                                    name = match.get('locationName', 'N/A')
                                    station_id = match.get('stationId', 'N/A')
                                    obs_time = match.get('time', {}).get('obsTime', 'N/A')
                                    
                                    weather_elements = match.get('weatherElement', [])
                                    weather_data = {}
                                    
                                    for element in weather_elements:
                                        element_name = element.get('elementName', '')
                                        element_value = element.get('elementValue', 'N/A')
                                        weather_data[element_name] = element_value
                                    
                                    temp = weather_data.get('TEMP', 'N/A')
                                    humidity = weather_data.get('HUMD', 'N/A')
                                    
                                    print(f"  • {name} ({station_id})")
                                    print(f"    🌡️ {temp}°C  💧 {humidity}%  ⏰ {obs_time}")
                                print()
                            
                        else:
                            print("❌ 無觀測資料")
                    else:
                        print("❌ API 回應格式錯誤")
                        print(f"回應內容: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                        
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    content = await response.text()
                    print(f"錯誤內容: {content[:200]}...")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_multiple_weather_apis():
    """測試多個天氣相關 API"""
    print("\n" + "=" * 60)
    print("測試多個天氣相關 API")
    print("=" * 60)
    
    apis_to_test = [
        ("O-A0003-001", "自動氣象測站觀測資料"),
        ("O-A0001-001", "自動氣象測站資料"),
        ("F-C0032-001", "一般天氣預報"),
    ]
    
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    api_base = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for endpoint, description in apis_to_test:
            print(f"\n測試 {description} ({endpoint}):")
            print("-" * 40)
            
            url = f"{api_base}/{endpoint}"
            params = {
                "Authorization": authorization,
                "format": "JSON"
            }
            
            try:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success') == 'true':
                            print(f"✅ {description} - API 正常")
                            
                            # 簡單統計
                            records = data.get('records', {})
                            if 'location' in records:
                                locations = records.get('location', [])
                                print(f"   📍 地點數量: {len(locations)}")
                            elif 'data' in records:
                                print(f"   📊 包含資料結構")
                            
                        else:
                            print(f"❌ {description} - 回應格式錯誤")
                    else:
                        print(f"❌ {description} - HTTP {response.status}")
                        
            except Exception as e:
                print(f"❌ {description} - 錯誤: {str(e)}")

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    asyncio.run(test_weather_observation_api())
    asyncio.run(test_multiple_weather_apis())
    
    print(f"\n結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 60)
    print("建議: 如果測試成功，可以將 O-A0003-001 API 整合到 Discord 指令中")
    print("=" * 60)

if __name__ == "__main__":
    main()
