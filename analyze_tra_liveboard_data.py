#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細分析TDX台鐵電子看板API資料
"""

import asyncio
import aiohttp
import ssl
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

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

async def analyze_tra_liveboard_data():
    """詳細分析台鐵電子看板資料"""
    print("🔍 詳細分析台鐵電子看板資料...")
    
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
                    
                    if isinstance(data, list) and data:
                        # 分析車站ID和車站名稱
                        station_info = defaultdict(set)
                        station_names = {}
                        
                        for train in data:
                            station_id = train.get('StationID', '')
                            station_name = train.get('StationName', {})
                            
                            if isinstance(station_name, dict):
                                zh_name = station_name.get('Zh_tw', '')
                                en_name = station_name.get('En', '')
                            else:
                                zh_name = str(station_name)
                                en_name = ''
                            
                            if station_id:
                                station_info[station_id].add(zh_name)
                                if zh_name:
                                    station_names[station_id] = zh_name
                        
                        print(f"\n📊 發現 {len(station_info)} 個不同車站:")
                        
                        # 尋找包含宜蘭的車站
                        yilan_stations = {}
                        for station_id, names in station_info.items():
                            for name in names:
                                if '宜蘭' in name or 'yilan' in name.lower() or 'ilan' in name.lower():
                                    yilan_stations[station_id] = name
                                    print(f"🎯 找到可能的宜蘭車站: ID={station_id}, 名稱={name}")
                        
                        # 顯示所有車站列表（按ID排序）
                        print(f"\n📋 所有車站列表:")
                        sorted_stations = sorted(station_names.items())
                        
                        for i, (station_id, name) in enumerate(sorted_stations):
                            if i < 50:  # 只顯示前50個
                                print(f"  {station_id}: {name}")
                            elif i == 50:
                                print(f"  ... 還有 {len(sorted_stations) - 50} 個車站")
                                break
                        
                        # 檢查是否有東部線路的車站
                        east_keywords = ['花蓮', '台東', '臺東', '宜蘭', '羅東', '蘇澳', '瑞芳', '基隆']
                        east_stations = {}
                        for station_id, name in station_names.items():
                            for keyword in east_keywords:
                                if keyword in name:
                                    east_stations[station_id] = name
                                    break
                        
                        if east_stations:
                            print(f"\n🏔️ 東部相關車站 ({len(east_stations)}個):")
                            for station_id, name in sorted(east_stations.items()):
                                print(f"  {station_id}: {name}")
                        
                        # 分析資料範例
                        print(f"\n🔍 資料結構範例:")
                        sample = data[0]
                        print(f"範例資料鍵值: {list(sample.keys())}")
                        print(f"StationID: {sample.get('StationID')}")
                        print(f"StationName: {sample.get('StationName')}")
                        print(f"TrainNo: {sample.get('TrainNo')}")
                        print(f"Direction: {sample.get('Direction')}")
                        print(f"ScheduledArrivalTime: {sample.get('ScheduledArrivalTime')}")
                        print(f"ScheduledDepartureTime: {sample.get('ScheduledDepartureTime')}")
                        
                        # 如果沒有找到宜蘭車站，嘗試其他可能的模糊搜尋
                        if not yilan_stations:
                            print(f"\n🔍 進行模糊搜尋...")
                            possible_matches = []
                            search_terms = ['宜', '蘭', 'yi', 'lan', '頭城', '羅東', '蘇澳', '礁溪']
                            
                            for station_id, name in station_names.items():
                                for term in search_terms:
                                    if term in name.lower():
                                        possible_matches.append((station_id, name))
                                        break
                            
                            if possible_matches:
                                print(f"🎯 可能的宜蘭相關車站:")
                                for station_id, name in possible_matches:
                                    print(f"  {station_id}: {name}")
                            else:
                                print("❌ 未找到任何可能的宜蘭相關車站")
                    else:
                        print("❌ API回傳資料格式異常")
                else:
                    error_text = await response.text()
                    print(f"❌ API請求失敗: {response.status}")
                    print(f"錯誤內容: {error_text[:500]}")
                    
    except Exception as e:
        print(f"❌ 分析過程發生錯誤: {str(e)}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(analyze_tra_liveboard_data())
