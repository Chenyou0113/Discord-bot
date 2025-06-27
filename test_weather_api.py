#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試氣象 API 功能
驗證無人氣象測站資料 API 是否正常工作
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_weather_api():
    """測試氣象 API"""
    print("=" * 60)
    print("測試氣象 API 功能")
    print("=" * 60)
    
    # API 設定
    api_base = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    endpoint = "C-B0074-002"  # 無人氣象測站基本資料
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
        # 設定 SSL 上下文（與機器人相同的設定）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("正在發送 API 請求...")
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"回應狀態碼: {response.status}")
                print(f"回應標頭: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    print("✅ API 請求成功!")
                    print("-" * 40)
                    
                    # 檢查回應結構
                    if data.get('success') == 'true':
                        print("✅ API 回應格式正確")
                        
                        # 獲取測站資料
                        records = data.get('records', {})
                        station_data = records.get('data', {}).get('stationStatus', {})
                        stations = station_data.get('station', [])
                        
                        print(f"✅ 測站資料數量: {len(stations)}")
                        
                        if stations:
                            # 顯示前 5 個測站的基本資訊
                            print("\n前 5 個測站的基本資訊:")
                            print("-" * 40)
                            
                            for i, station in enumerate(stations[:5], 1):
                                station_id = station.get('StationID', 'N/A')
                                station_name = station.get('StationName', 'N/A')
                                county = station.get('CountyName', 'N/A')
                                status = station.get('status', 'N/A')
                                location = station.get('Location', 'N/A')
                                
                                print(f"{i}. {station_name} ({station_id})")
                                print(f"   縣市: {county}")
                                print(f"   狀態: {status}")
                                print(f"   位置: {location[:50]}{'...' if len(location) > 50 else ''}")
                                print()
                            
                            # 測試搜尋功能
                            print("測試搜尋功能:")
                            print("-" * 40)
                            
                            test_queries = ["台北", "新北市", "板橋", "C0A940"]
                            
                            for query in test_queries:
                                matches = []
                                query_lower = query.lower()
                                
                                for station in stations:
                                    searchable_fields = [
                                        station.get('StationID', '').lower(),
                                        station.get('StationName', '').lower(),
                                        station.get('CountyName', '').lower(),
                                        station.get('Location', '').lower(),
                                    ]
                                    
                                    if any(query_lower in field for field in searchable_fields):
                                        matches.append(station)
                                
                                print(f"搜尋 '{query}': 找到 {len(matches)} 個結果")
                                
                                if matches:
                                    for j, match in enumerate(matches[:3], 1):
                                        name = match.get('StationName', 'N/A')
                                        station_id = match.get('StationID', 'N/A')
                                        county = match.get('CountyName', 'N/A')
                                        status = match.get('status', 'N/A')
                                        print(f"  {j}. {name} ({station_id}) - {county} - {status}")
                                print()
                            
                            # 統計資訊
                            print("統計資訊:")
                            print("-" * 40)
                            
                            status_count = {}
                            county_count = {}
                            
                            for station in stations:
                                status = station.get('status', '未知')
                                county = station.get('CountyName', '未知')
                                
                                status_count[status] = status_count.get(status, 0) + 1
                                county_count[county] = county_count.get(county, 0) + 1
                            
                            print("測站狀態統計:")
                            for status, count in sorted(status_count.items()):
                                print(f"  {status}: {count} 個")
                            
                            print("\n縣市分布統計 (前 10 名):")
                            sorted_counties = sorted(county_count.items(), key=lambda x: x[1], reverse=True)
                            for county, count in sorted_counties[:10]:
                                print(f"  {county}: {count} 個")
                            
                        else:
                            print("❌ 無測站資料")
                            
                    else:
                        print("❌ API 回應格式錯誤")
                        print(f"回應內容: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    content = await response.text()
                    print(f"錯誤內容: {content}")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(test_weather_api())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
