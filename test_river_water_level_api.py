#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試河川水位資料 API
檢查資料結構以便實作新指令
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_river_water_level_api():
    """測試河川水位資料 API"""
    print("=" * 60)
    print("測試河川水位資料 API")
    print("=" * 60)
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
            
            print(f"API URL: {url}")
            print("📡 正在獲取河川水位資料...")
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"回應狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗: {response.status}")
                    return
                
                # 處理 UTF-8 BOM 問題
                text = await response.text()
                if text.startswith('\ufeff'):
                    text = text[1:]
                
                try:
                    data = json.loads(text)
                    print(f"✅ 成功獲取資料")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    return
                
                # 檢查資料結構
                print(f"\n📊 資料結構分析:")
                print(f"資料類型: {type(data)}")
                
                if isinstance(data, list):
                    print(f"資料數量: {len(data)}")
                    if data:
                        print(f"\n🔍 第一筆資料結構:")
                        first_item = data[0]
                        for key, value in first_item.items():
                            print(f"  {key}: {value}")
                        
                        # 分析前5筆資料
                        print(f"\n📋 前5筆資料概覽:")
                        for i, item in enumerate(data[:5], 1):
                            print(f"\n{i}. ")
                            station_name = item.get('StationName', 'N/A')
                            county = item.get('CountyName', 'N/A')
                            water_level = item.get('WaterLevel', 'N/A')
                            observation_time = item.get('ObservationTime', 'N/A')
                            
                            print(f"   測站名稱: {station_name}")
                            print(f"   縣市: {county}")
                            print(f"   水位: {water_level}")
                            print(f"   觀測時間: {observation_time}")
                            
                            # 顯示所有可用欄位
                            print(f"   所有欄位:")
                            for key, value in item.items():
                                if key not in ['StationName', 'CountyName', 'WaterLevel', 'ObservationTime']:
                                    print(f"     {key}: {value}")
                        
                        # 統計分析
                        print(f"\n📈 統計分析:")
                        
                        # 縣市分布
                        county_stats = {}
                        water_level_stats = []
                        
                        for item in data:
                            county = item.get('CountyName', '未知')
                            county_stats[county] = county_stats.get(county, 0) + 1
                            
                            water_level = item.get('WaterLevel', '')
                            if water_level and water_level != 'N/A':
                                try:
                                    water_level_stats.append(float(water_level))
                                except:
                                    pass
                        
                        print(f"縣市分布 (前10名):")
                        sorted_counties = sorted(county_stats.items(), key=lambda x: x[1], reverse=True)
                        for county, count in sorted_counties[:10]:
                            print(f"  {county}: {count} 個測站")
                        
                        if water_level_stats:
                            print(f"\n水位統計:")
                            print(f"  總測站數: {len(data)}")
                            print(f"  有水位資料: {len(water_level_stats)}")
                            print(f"  最高水位: {max(water_level_stats):.2f}")
                            print(f"  最低水位: {min(water_level_stats):.2f}")
                            print(f"  平均水位: {sum(water_level_stats)/len(water_level_stats):.2f}")
                        
                        # 尋找特定地區資料
                        print(f"\n🔍 台南地區測站:")
                        tainan_stations = [item for item in data if '台南' in item.get('CountyName', '')]
                        print(f"找到 {len(tainan_stations)} 個台南測站")
                        
                        for i, station in enumerate(tainan_stations[:3], 1):
                            station_name = station.get('StationName', 'N/A')
                            water_level = station.get('WaterLevel', 'N/A')
                            river_name = station.get('RiverName', 'N/A')
                            print(f"  {i}. {station_name} - {river_name} - 水位: {water_level}")
                        
                elif isinstance(data, dict):
                    print(f"字典結構:")
                    for key, value in data.items():
                        print(f"  {key}: {type(value)} - {str(value)[:100]}...")
                else:
                    print(f"未知資料格式: {data}")
                
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
    asyncio.run(test_river_water_level_api())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
