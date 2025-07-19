#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索不同的TDX台鐵API端點
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

async def test_different_tra_apis():
    """測試不同的TDX台鐵API端點"""
    print("🔍 測試不同的TDX台鐵API端點...")
    
    access_token = await get_tdx_access_token()
    if not access_token:
        return
    
    # 不同的API端點
    api_endpoints = {
        "即時時刻表": "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/DailyTimetable/OD/2770/to/1000/2025-01-19?%24format=JSON",
        "車站資訊": "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/Station?%24format=JSON",
        "路線資訊": "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/Line?%24format=JSON",
        "即時車位資訊": "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/TrainLiveBoard?%24top=100&%24format=JSON",
        "電子看板(所有車站)": "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24format=JSON",
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
            
            for api_name, url in api_endpoints.items():
                print(f"\n🔍 測試 {api_name}:")
                print(f"URL: {url}")
                
                try:
                    async with session.get(url, headers=headers) as response:
                        print(f"回應狀態: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            
                            if isinstance(data, list):
                                print(f"資料筆數: {len(data)}")
                                if data:
                                    # 檢查是否有宜蘭相關資料
                                    yilan_found = False
                                    for item in data:
                                        # 檢查各種可能的宜蘭識別欄位
                                        text_fields = []
                                        if isinstance(item, dict):
                                            for key, value in item.items():
                                                if isinstance(value, str):
                                                    text_fields.append(value)
                                                elif isinstance(value, dict):
                                                    for sub_key, sub_value in value.items():
                                                        if isinstance(sub_value, str):
                                                            text_fields.append(sub_value)
                                        
                                        # 檢查是否包含宜蘭
                                        text_content = ' '.join(text_fields).lower()
                                        if '宜蘭' in text_content or 'yilan' in text_content:
                                            yilan_found = True
                                            print(f"✅ 找到宜蘭相關資料: {json.dumps(item, ensure_ascii=False)[:200]}...")
                                            break
                                    
                                    if not yilan_found:
                                        print("❌ 沒有找到宜蘭相關資料")
                                        # 顯示第一筆資料範例
                                        sample = data[0]
                                        print(f"資料範例: {json.dumps(sample, ensure_ascii=False)[:300]}...")
                            elif isinstance(data, dict):
                                print(f"回傳字典，鍵值: {list(data.keys())}")
                                print(f"內容範例: {json.dumps(data, ensure_ascii=False)[:300]}...")
                            else:
                                print(f"未知資料格式: {type(data)}")
                        else:
                            error_text = await response.text()
                            print(f"錯誤: {error_text[:200]}...")
                            
                except asyncio.TimeoutError:
                    print("❌ 請求超時")
                except Exception as e:
                    print(f"❌ 請求錯誤: {str(e)}")
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")

async def test_station_info():
    """專門測試車站資訊API"""
    print("\n🔍 詳細測試車站資訊API...")
    
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
            
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/Station?%24format=JSON"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    stations = await response.json()
                    print(f"📦 總車站數: {len(stations)}")
                    
                    yilan_stations = []
                    for station in stations:
                        station_name = station.get('StationName', {})
                        if isinstance(station_name, dict):
                            zh_name = station_name.get('Zh_tw', '')
                        else:
                            zh_name = str(station_name)
                        
                        if '宜蘭' in zh_name or any(keyword in zh_name for keyword in ['羅東', '蘇澳', '頭城', '礁溪']):
                            yilan_stations.append(station)
                    
                    if yilan_stations:
                        print(f"\n✅ 找到 {len(yilan_stations)} 個宜蘭相關車站:")
                        for station in yilan_stations:
                            station_id = station.get('StationID', 'N/A')
                            station_name = station.get('StationName', {})
                            if isinstance(station_name, dict):
                                zh_name = station_name.get('Zh_tw', 'N/A')
                            else:
                                zh_name = str(station_name)
                            print(f"  ID: {station_id}, 名稱: {zh_name}")
                    else:
                        print("❌ 沒有找到宜蘭相關車站")
                        # 顯示一些車站範例
                        print("\n車站範例:")
                        for station in stations[:10]:
                            station_id = station.get('StationID', 'N/A')
                            station_name = station.get('StationName', {})
                            if isinstance(station_name, dict):
                                zh_name = station_name.get('Zh_tw', 'N/A')
                            else:
                                zh_name = str(station_name)
                            print(f"  ID: {station_id}, 名稱: {zh_name}")
                else:
                    error_text = await response.text()
                    print(f"❌ 車站資訊API錯誤: {error_text[:200]}")
                    
    except Exception as e:
        print(f"❌ 車站資訊測試錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_different_tra_apis())
    asyncio.run(test_station_info())
