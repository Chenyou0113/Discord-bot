#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試宜蘭台鐵電子看板功能
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
        
        # 讀取環境變數
        client_id = os.getenv('TDX_CLIENT_ID')
        client_secret = os.getenv('TDX_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ TDX API憑證未設定")
            print("請確保.env檔案中有設定 TDX_CLIENT_ID 和 TDX_CLIENT_SECRET")
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

async def test_yilan_tra_liveboard():
    """測試宜蘭台鐵電子看板"""
    print("🔍 測試宜蘭台鐵電子看板功能...")
    
    # 取得存取權杖
    access_token = await get_tdx_access_token()
    if not access_token:
        return
    
    # 宜蘭縣的台鐵車站
    yilan_stations = {
        '1810': '宜蘭',
        '1820': '四城', 
        '1830': '礁溪',
        '1840': '頂埔',
        '1850': '頭城',
        '1860': '外澳',
        '1870': '龜山',
        '1880': '大溪',
        '1890': '大里',
        '1900': '石城',
        '7360': '二結',
        '7370': '中里',
        '7380': '羅東',
        '7390': '冬山',
        '7400': '新馬',
        '7410': '蘇澳',
        '7420': '蘇澳新',
        '7430': '永樂',
        '7440': '東澳',
        '7450': '南澳'
    }
    
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
            
            # 使用新的全域API端點
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=500&%24format=JSON"
            
            print(f"📡 請求URL: {url}")
            
            async with session.get(url, headers=headers) as response:
                print(f"📊 回應狀態: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📦 總資料筆數: {len(data) if isinstance(data, list) else '非陣列資料'}")
                    
                    if isinstance(data, list):
                        # 篩選宜蘭縣的車站資料
                        yilan_trains = []
                        for train in data:
                            station_id = train.get('StationID', '')
                            if station_id in yilan_stations:
                                yilan_trains.append(train)
                        
                        print(f"🚆 宜蘭縣台鐵資料筆數: {len(yilan_trains)}")
                        
                        if yilan_trains:
                            print("\n📋 宜蘭縣台鐵電子看板資料:")
                            
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
                                
                                for i, train in enumerate(trains[:5]):  # 只顯示前5筆
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
                            print("❌ 沒有找到宜蘭縣的台鐵資料")
                            
                            # 檢查整體資料結構
                            if data:
                                print("\n🔍 檢查資料結構範例:")
                                sample = data[0]
                                print(f"範例資料鍵值: {list(sample.keys())}")
                                print(f"StationID: {sample.get('StationID', 'N/A')}")
                                print(f"StationName: {sample.get('StationName', 'N/A')}")
                                
                                # 統計所有車站ID
                                all_station_ids = set()
                                for train in data:
                                    station_id = train.get('StationID', '')
                                    if station_id:
                                        all_station_ids.add(station_id)
                                
                                print(f"\n📊 全部車站ID統計: {len(all_station_ids)}個")
                                print("前20個車站ID:", sorted(list(all_station_ids))[:20])
                                
                                # 檢查是否有宜蘭相關的車站ID
                                yilan_found = []
                                for station_id in all_station_ids:
                                    if station_id in yilan_stations:
                                        yilan_found.append(station_id)
                                
                                if yilan_found:
                                    print(f"✅ 找到宜蘭車站ID: {yilan_found}")
                                else:
                                    print("❌ 未找到任何宜蘭車站ID")
                    else:
                        print("❌ API回傳的資料格式不是陣列")
                        print(f"資料類型: {type(data)}")
                        if isinstance(data, dict):
                            print(f"字典鍵值: {list(data.keys())}")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ API請求失敗: {response.status}")
                    print(f"錯誤內容: {error_text[:500]}")
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")

async def test_specific_yilan_station():
    """測試特定宜蘭車站(宜蘭站)"""
    print("\n🔍 測試特定宜蘭車站...")
    
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
            
            # 測試舊的單站API（如果還有效）
            yilan_station_id = "1810"  # 宜蘭車站
            old_url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard/Station/{yilan_station_id}?%24format=JSON"
            
            print(f"📡 測試舊API: {old_url}")
            
            async with session.get(old_url, headers=headers) as response:
                print(f"📊 舊API回應狀態: {response.status}")
                
                if response.status == 200:
                    old_data = await response.json()
                    print(f"📦 舊API資料筆數: {len(old_data) if isinstance(old_data, list) else '非陣列資料'}")
                    
                    if isinstance(old_data, list) and old_data:
                        print("✅ 舊API有資料，顯示範例:")
                        sample = old_data[0]
                        print(f"範例資料: {json.dumps(sample, ensure_ascii=False, indent=2)[:500]}...")
                    else:
                        print("❌ 舊API沒有資料或格式異常")
                else:
                    error_text = await response.text()
                    print(f"❌ 舊API請求失敗: {error_text[:200]}")
            
            # 測試新的全域API並篩選
            new_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=500&%24format=JSON"
            print(f"\n📡 測試新API並篩選宜蘭: {new_url}")
            
            async with session.get(new_url, headers=headers) as response:
                if response.status == 200:
                    new_data = await response.json()
                    if isinstance(new_data, list):
                        yilan_filtered = [train for train in new_data if train.get('StationID') == yilan_station_id]
                        print(f"📦 新API篩選後宜蘭資料筆數: {len(yilan_filtered)}")
                        
                        if yilan_filtered:
                            print("✅ 新API篩選有資料，顯示範例:")
                            sample = yilan_filtered[0]
                            print(f"範例資料: {json.dumps(sample, ensure_ascii=False, indent=2)[:500]}...")
                        else:
                            print("❌ 新API篩選後沒有宜蘭資料")
                    else:
                        print("❌ 新API資料格式異常")
                        
    except Exception as e:
        print(f"❌ 特定車站測試錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔍 開始測試宜蘭台鐵電子看板...")
    asyncio.run(test_yilan_tra_liveboard())
    asyncio.run(test_specific_yilan_station())
    print("\n✅ 測試完成")
