#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正確的宜蘭車站ID測試台鐵電子看板
"""

import asyncio
import aiohttp
import ssl
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def get_tdx_access_token():
    """取得TDX存取權杖"""
    try:
        auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        
        client_id = os.getenv('TDX_CLIENT_ID')
        client_secret = os.getenv('TDX_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ TDX API憑證未設定")
            return None
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            async with session.post(auth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data.get('access_token')
                    print(f"✅ TDX認證成功")
                    return access_token
                else:
                    print(f"❌ TDX認證失敗: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ TDX認證錯誤: {str(e)}")
        return None

async def test_correct_yilan_stations():
    """使用正確的宜蘭車站ID測試"""
    print("🔍 使用正確的宜蘭車站ID測試...")
    
    # 正確的宜蘭縣台鐵車站ID（從機器人程式碼複製）
    yilan_stations = {
        "2650": "漢本",
        "2660": "武塔", 
        "2670": "南澳",
        "2680": "東澳",
        "2690": "永樂",
        "2700": "蘇澳",
        "2710": "蘇澳新",
        "2720": "新馬",
        "2730": "冬山",
        "2740": "羅東",
        "2750": "中里",
        "2760": "二結",
        "2770": "宜蘭",     # 宜蘭車站
        "2780": "四城",
        "2790": "礁溪",
        "2800": "頂埔",
        "2810": "頭城",
        "2820": "外澳",
        "2830": "龜山",
        "2840": "大溪",
        "2850": "大里",
        "2860": "石城"
    }
    
    access_token = await get_tdx_access_token()
    if not access_token:
        return
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=500&%24format=JSON"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"📦 總資料筆數: {len(data)}")
                    
                    if isinstance(data, list):
                        # 篩選宜蘭縣的車站資料
                        yilan_trains = []
                        for train in data:
                            station_id = train.get('StationID', '')
                            if station_id in yilan_stations:
                                yilan_trains.append(train)
                        
                        print(f"🚆 宜蘭縣台鐵資料筆數: {len(yilan_trains)}")
                        
                        if yilan_trains:
                            print("\n✅ 成功找到宜蘭縣台鐵電子看板資料!")
                            
                            # 按車站分組顯示
                            station_groups = {}
                            for train in yilan_trains:
                                station_id = train.get('StationID', '')
                                station_name = yilan_stations.get(station_id, station_id)
                                if station_name not in station_groups:
                                    station_groups[station_name] = []
                                station_groups[station_name].append(train)
                            
                            for station_name, trains in station_groups.items():
                                print(f"\n🚉 {station_name} 車站 ({len(trains)}筆資料):")
                                
                                for i, train in enumerate(trains[:3]):  # 只顯示前3筆
                                    train_no = train.get('TrainNo', 'N/A')
                                    train_type = train.get('TrainTypeName', {})
                                    if isinstance(train_type, dict):
                                        train_type_name = train_type.get('Zh_tw', 'N/A')
                                    else:
                                        train_type_name = str(train_type)
                                    
                                    direction = train.get('Direction', 0)
                                    direction_str = "順行(南下)" if direction == 0 else "逆行(北上)"
                                    
                                    scheduled_arrival = train.get('ScheduledArrivalTime', 'N/A')
                                    scheduled_departure = train.get('ScheduledDepartureTime', 'N/A')
                                    delay_time = train.get('DelayTime', 0)
                                    
                                    end_station = train.get('EndingStationName', {})
                                    if isinstance(end_station, dict):
                                        end_station_name = end_station.get('Zh_tw', 'N/A')
                                    else:
                                        end_station_name = str(end_station)
                                    
                                    print(f"  {i+1}. 車次: {train_no} ({train_type_name})")
                                    print(f"     方向: {direction_str}")
                                    print(f"     終點: {end_station_name}")
                                    print(f"     到站: {scheduled_arrival}")
                                    print(f"     離站: {scheduled_departure}")
                                    if delay_time > 0:
                                        print(f"     誤點: {delay_time}分鐘")
                                    print()
                        else:
                            print("❌ 仍然沒有找到宜蘭縣的台鐵資料")
                            print("可能原因:")
                            print("1. 目前時間沒有宜蘭線班車")
                            print("2. API資料更新延遲")
                            print("3. 車站ID定義可能有變化")
                            
                            # 檢查是否有其他27xx系列的車站
                            found_27xx = []
                            for train in data:
                                station_id = train.get('StationID', '')
                                if station_id.startswith('27'):
                                    found_27xx.append(station_id)
                            
                            if found_27xx:
                                unique_27xx = list(set(found_27xx))
                                print(f"\n🔍 發現27xx系列車站ID: {sorted(unique_27xx)}")
                            else:
                                print("\n❌ 沒有發現任何27xx系列車站ID")
                    else:
                        print("❌ API回傳資料格式異常")
                else:
                    error_text = await response.text()
                    print(f"❌ API請求失敗: {response.status}")
                    print(f"錯誤內容: {error_text[:500]}")
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")

async def test_single_yilan_station():
    """測試單一宜蘭車站(宜蘭站 2770)"""
    print("\n🔍 測試宜蘭車站 (ID: 2770)...")
    
    access_token = await get_tdx_access_token()
    if not access_token:
        return
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            # 使用全域API並篩選宜蘭站
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=500&%24format=JSON"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        yilan_station_trains = [train for train in data if train.get('StationID') == '2770']
                        print(f"📦 宜蘭車站資料筆數: {len(yilan_station_trains)}")
                        
                        if yilan_station_trains:
                            print("✅ 找到宜蘭車站電子看板資料:")
                            for i, train in enumerate(yilan_station_trains[:5]):
                                print(f"\n第{i+1}筆資料:")
                                print(f"車次: {train.get('TrainNo', 'N/A')}")
                                print(f"車種: {train.get('TrainTypeName', {}).get('Zh_tw', 'N/A')}")
                                print(f"方向: {'順行' if train.get('Direction', 0) == 0 else '逆行'}")
                                print(f"終點: {train.get('EndingStationName', {}).get('Zh_tw', 'N/A')}")
                                print(f"預定到站: {train.get('ScheduledArrivalTime', 'N/A')}")
                                print(f"預定開車: {train.get('ScheduledDepartureTime', 'N/A')}")
                                if train.get('DelayTime', 0) > 0:
                                    print(f"誤點: {train.get('DelayTime')}分鐘")
                        else:
                            print("❌ 宜蘭車站目前沒有電子看板資料")
                            
                            # 嘗試查看是否有其他宜蘭相關車站有資料
                            yilan_related = ['2770', '2740', '2790']  # 宜蘭、羅東、礁溪
                            for station_id in yilan_related:
                                station_trains = [train for train in data if train.get('StationID') == station_id]
                                if station_trains:
                                    station_name = {'2770': '宜蘭', '2740': '羅東', '2790': '礁溪'}[station_id]
                                    print(f"✅ {station_name}車站有 {len(station_trains)} 筆資料")
                    else:
                        print("❌ API資料格式異常")
                        
    except Exception as e:
        print(f"❌ 單站測試錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 開始測試正確的宜蘭台鐵電子看板...")
    asyncio.run(test_correct_yilan_stations())
    asyncio.run(test_single_yilan_station())
    print("\n✅ 測試完成")
