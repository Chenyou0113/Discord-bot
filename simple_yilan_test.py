#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試宜蘭台鐵電子看板，避免API限制
"""

import asyncio
import aiohttp
import ssl
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import time

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

async def find_yilan_in_liveboard():
    """在電子看板API中尋找宜蘭相關資料"""
    print("🔍 在電子看板API中尋找宜蘭相關資料...")
    
    access_token = await get_tdx_access_token()
    if not access_token:
        return
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 增加延遲避免API限制
        await asyncio.sleep(2)
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            # 只取前200筆資料避免API限制
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=200&%24format=JSON"
            
            async with session.get(url, headers=headers) as response:
                print(f"回應狀態: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📦 取得資料筆數: {len(data)}")
                    
                    if isinstance(data, list):
                        # 尋找宜蘭相關車站
                        yilan_keywords = ['宜蘭', '羅東', '蘇澳', '頭城', '礁溪', '冬山', '二結', '中里', '四城', '頂埔', '永樂', '南澳', '東澳']
                        yilan_trains = []
                        yilan_stations = {}
                        
                        for train in data:
                            station_name = train.get('StationName', {})
                            if isinstance(station_name, dict):
                                zh_name = station_name.get('Zh_tw', '')
                            else:
                                zh_name = str(station_name)
                            
                            # 檢查是否為宜蘭相關車站
                            for keyword in yilan_keywords:
                                if keyword in zh_name:
                                    yilan_trains.append(train)
                                    station_id = train.get('StationID', '')
                                    if station_id not in yilan_stations:
                                        yilan_stations[station_id] = zh_name
                                    break
                        
                        if yilan_trains:
                            print(f"\n✅ 找到 {len(yilan_trains)} 筆宜蘭相關電子看板資料!")
                            print(f"📍 涉及車站: {len(yilan_stations)} 個")
                            
                            # 顯示車站對應表
                            print(f"\n🚉 宜蘭車站ID對應表:")
                            for station_id, station_name in sorted(yilan_stations.items()):
                                print(f"  {station_id}: {station_name}")
                            
                            # 按車站分組顯示資料
                            station_groups = {}
                            for train in yilan_trains:
                                station_id = train.get('StationID', '')
                                station_name = train.get('StationName', {})
                                if isinstance(station_name, dict):
                                    zh_name = station_name.get('Zh_tw', '')
                                else:
                                    zh_name = str(station_name)
                                
                                if zh_name not in station_groups:
                                    station_groups[zh_name] = []
                                station_groups[zh_name].append(train)
                            
                            print(f"\n🚆 各車站電子看板資料:")
                            for station_name, trains in station_groups.items():
                                print(f"\n  📍 {station_name} ({len(trains)}筆):")
                                
                                for i, train in enumerate(trains[:3]):  # 只顯示前3筆
                                    train_no = train.get('TrainNo', 'N/A')
                                    train_type = train.get('TrainTypeName', {})
                                    if isinstance(train_type, dict):
                                        train_type_name = train_type.get('Zh_tw', 'N/A')
                                    else:
                                        train_type_name = str(train_type)
                                    
                                    direction = train.get('Direction', 0)
                                    direction_str = "順行" if direction == 0 else "逆行"
                                    
                                    scheduled_arrival = train.get('ScheduledArrivalTime', 'N/A')
                                    scheduled_departure = train.get('ScheduledDepartureTime', 'N/A')
                                    delay_time = train.get('DelayTime', 0)
                                    
                                    end_station = train.get('EndingStationName', {})
                                    if isinstance(end_station, dict):
                                        end_station_name = end_station.get('Zh_tw', 'N/A')
                                    else:
                                        end_station_name = str(end_station)
                                    
                                    delay_info = f" (誤點{delay_time}分)" if delay_time > 0 else ""
                                    print(f"    {i+1}. {train_no}車次 ({train_type_name}) → {end_station_name}")
                                    print(f"       {direction_str} | 到站:{scheduled_arrival} | 開車:{scheduled_departure}{delay_info}")
                        else:
                            print("❌ 沒有找到宜蘭相關電子看板資料")
                            
                            # 顯示所有車站列表供參考
                            print("\n📋 前20個車站供參考:")
                            stations_shown = set()
                            count = 0
                            for train in data:
                                if count >= 20:
                                    break
                                station_name = train.get('StationName', {})
                                if isinstance(station_name, dict):
                                    zh_name = station_name.get('Zh_tw', '')
                                else:
                                    zh_name = str(station_name)
                                
                                if zh_name and zh_name not in stations_shown:
                                    station_id = train.get('StationID', '')
                                    print(f"  {station_id}: {zh_name}")
                                    stations_shown.add(zh_name)
                                    count += 1
                    else:
                        print("❌ API回傳資料格式異常")
                        
                elif response.status == 429:
                    print("❌ API請求頻率過高，請稍後再試")
                else:
                    error_text = await response.text()
                    print(f"❌ API請求失敗: {response.status}")
                    print(f"錯誤內容: {error_text[:200]}")
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(find_yilan_in_liveboard())
