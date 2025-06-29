#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析自動氣象測站資料 API (O-A0001-001) 的正確資料結構
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def parse_weather_station_api():
    """解析自動氣象測站資料 API 的正確結構"""
    print("=" * 60)
    print("解析自動氣象測站資料 API 結構")
    print("=" * 60)
    
    api_base = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    endpoint = "O-A0001-001"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    url = f"{api_base}/{endpoint}"
    params = {
        "Authorization": authorization,
        "format": "JSON"
    }
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') == 'true':
                        records = data.get('records', {})
                        stations = records.get('Station', [])
                        
                        print(f"✅ 找到 {len(stations)} 個氣象測站")
                        
                        if stations:
                            # 分析前幾個測站的結構
                            print("\n分析測站資料結構:")
                            print("-" * 40)
                            
                            first_station = stations[0]
                            print("第一個測站的欄位:")
                            for key in first_station.keys():
                                print(f"  - {key}")
                            
                            print(f"\n前 5 個測站的詳細資訊:")
                            print("-" * 50)
                            
                            for i, station in enumerate(stations[:5], 1):
                                station_name = station.get('StationName', 'N/A')
                                station_id = station.get('StationId', 'N/A')
                                obs_time = station.get('ObsTime', {}).get('DateTime', 'N/A')
                                
                                print(f"{i}. {station_name} ({station_id})")
                                print(f"   觀測時間: {obs_time}")
                                
                                # 解析氣象要素
                                weather_elements = station.get('WeatherElement', {})
                                
                                if weather_elements:
                                    # 主要天氣資訊
                                    temp = weather_elements.get('AirTemperature', 'N/A')  # 氣溫
                                    humidity = weather_elements.get('RelativeHumidity', 'N/A')  # 相對濕度
                                    pressure = weather_elements.get('AirPressure', 'N/A')  # 氣壓
                                    wind_speed = weather_elements.get('WindSpeed', 'N/A')  # 風速
                                    wind_dir = weather_elements.get('WindDirection', 'N/A')  # 風向
                                    rainfall = weather_elements.get('Now', {}).get('Precipitation', 'N/A')  # 降雨量
                                    
                                    # 顯示天氣資訊
                                    if temp != 'N/A':
                                        print(f"   🌡️ 氣溫: {temp}°C")
                                    if humidity != 'N/A':
                                        print(f"   💧 相對濕度: {humidity}%")
                                    if pressure != 'N/A':
                                        print(f"   📊 氣壓: {pressure} hPa")
                                    if wind_speed != 'N/A':
                                        print(f"   💨 風速: {wind_speed} m/s")
                                    if wind_dir != 'N/A':
                                        print(f"   🧭 風向: {wind_dir}°")
                                    if rainfall != 'N/A':
                                        print(f"   🌧️ 降雨量: {rainfall} mm")
                                
                                print()
                            
                            # 搜尋測試
                            print("測試搜尋功能:")
                            print("-" * 30)
                            
                            search_terms = ["板橋", "台北", "淡水", "桃園", "新竹"]
                            
                            for term in search_terms:
                                matches = []
                                for station in stations:
                                    station_name = station.get('StationName', '')
                                    if term in station_name:
                                        matches.append(station)
                                
                                print(f"搜尋 '{term}': 找到 {len(matches)} 個測站")
                                
                                for match in matches[:2]:
                                    name = match.get('StationName', 'N/A')
                                    station_id = match.get('StationId', 'N/A')
                                    weather_elements = match.get('WeatherElement', {})
                                    temp = weather_elements.get('AirTemperature', 'N/A')
                                    
                                    print(f"  • {name} ({station_id}) - 🌡️ {temp}°C")
                            
                            # 儲存樣本資料
                            sample_data = {
                                "total_stations": len(stations),
                                "sample_stations": stations[:3],
                                "timestamp": datetime.now().isoformat()
                            }
                            
                            with open("weather_station_sample.json", "w", encoding="utf-8") as f:
                                json.dump(sample_data, f, ensure_ascii=False, indent=2)
                            
                            print(f"\n💾 樣本資料已儲存至: weather_station_sample.json")
                            
                        else:
                            print("❌ 無測站資料")
                    else:
                        print("❌ API 回應格式錯誤")
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    asyncio.run(parse_weather_station_api())

if __name__ == "__main__":
    main()
