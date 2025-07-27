#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速檢查TDX API中的宜蘭資料
"""

import asyncio
import aiohttp
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

async def quick_check():
    """快速檢查宜蘭資料"""
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ TDX憑證未設定")
        return
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            # 取得token
            auth_data = {
                'grant_type': 'client_credentials', 
                'client_id': client_id, 
                'client_secret': client_secret
            }
            
            async with session.post('https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token', data=auth_data) as response:
                if response.status != 200:
                    print(f"❌ 認證失敗: {response.status}")
                    return
                    
                token_data = await response.json()
                access_token = token_data.get('access_token')
                if not access_token:
                    print("❌ 無法取得access token")
                    return
                    
                print("✅ 認證成功")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # 查詢電子看板
            url = 'https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=100&%24format=JSON'
            async with session.get(url, headers=headers) as response:
                print(f"📡 API回應: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📦 資料筆數: {len(data)}")
                    
                    yilan_trains = []
                    station_ids = set()
                    
                    for train in data:
                        station_name = train.get('StationName', {})
                        station_id = train.get('StationID', '')
                        
                        if isinstance(station_name, dict):
                            zh_name = station_name.get('Zh_tw', '')
                        else:
                            zh_name = str(station_name)
                        
                        station_ids.add(station_id)
                        
                        # 檢查宜蘭相關關鍵字
                        keywords = ['宜蘭', '羅東', '蘇澳', '頭城', '礁溪', '冬山', '二結']
                        for keyword in keywords:
                            if keyword in zh_name:
                                yilan_trains.append({
                                    'station_id': station_id,
                                    'station_name': zh_name,
                                    'train_no': train.get('TrainNo', 'N/A')
                                })
                                break
                    
                    if yilan_trains:
                        print(f"\n✅ 找到 {len(yilan_trains)} 筆宜蘭相關資料:")
                        for train in yilan_trains[:10]:  # 只顯示前10筆
                            print(f"  ID: {train['station_id']} | 車站: {train['station_name']} | 車次: {train['train_no']}")
                    else:
                        print("\n❌ 沒有找到宜蘭相關車站")
                        print(f"📊 API中的車站ID範圍: {min(station_ids)} ~ {max(station_ids)}")
                        print(f"前10個車站ID: {sorted(list(station_ids))[:10]}")
                        
                        # 檢查是否有27xx系列
                        has_27xx = any(sid.startswith('27') for sid in station_ids)
                        print(f"是否有27xx系列車站: {'是' if has_27xx else '否'}")
                        
                elif response.status == 429:
                    print("❌ API請求頻率過高")
                else:
                    error_text = await response.text()
                    print(f"❌ API錯誤: {error_text[:200]}")
                    
    except Exception as e:
        print(f"❌ 測試錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(quick_check())
