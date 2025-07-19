#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證宜蘭台鐵電子看板修正
"""

import asyncio
import aiohttp
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_yilan_fix():
    """驗證宜蘭車站修正"""
    print("🔍 驗證宜蘭車站ID修正...")
    
    yilan_station_id = "7190"  # 修正後的宜蘭車站ID
    
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ TDX憑證未設定")
        return
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            # 認證
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
                print("✅ TDX認證成功")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            # 查詢電子看板
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=1000&%24format=JSON"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 篩選宜蘭車站資料
                    station_trains = [train for train in data if train.get('StationID') == yilan_station_id]
                    
                    print(f"📦 API總資料: {len(data)} 筆")
                    print(f"🚉 宜蘭車站資料: {len(station_trains)} 筆")
                    
                    if station_trains:
                        print("\n✅ 宜蘭電子看板修正成功!")
                        print("🚆 當前班車資訊:")
                        
                        for i, train in enumerate(station_trains[:5]):
                            train_no = train.get('TrainNo', 'N/A')
                            train_type = train.get('TrainTypeName', {})
                            if isinstance(train_type, dict):
                                train_type_name = train_type.get('Zh_tw', 'N/A')
                            else:
                                train_type_name = str(train_type)
                            
                            direction = train.get('Direction', 0)
                            direction_str = "順行(南下)" if direction == 0 else "逆行(北上)"
                            
                            arrival = train.get('ScheduledArrivalTime', 'N/A')
                            departure = train.get('ScheduledDepartureTime', 'N/A')
                            delay = train.get('DelayTime', 0)
                            
                            end_station = train.get('EndingStationName', {})
                            if isinstance(end_station, dict):
                                end_name = end_station.get('Zh_tw', 'N/A')
                            else:
                                end_name = str(end_station)
                            
                            delay_text = f" (誤點{delay}分)" if delay > 0 else ""
                            
                            print(f"  {i+1}. {train_no}車次 ({train_type_name}) → {end_name}")
                            print(f"     {direction_str} | 到站:{arrival} 開車:{departure}{delay_text}")
                        
                        print(f"\n🎉 修復完成！現在用戶可以正常查詢宜蘭台鐵電子看板了。")
                    else:
                        print("❌ 仍無宜蘭車站資料")
                else:
                    print(f"❌ API錯誤: {response.status}")
                    
    except Exception as e:
        print(f"❌ 驗證錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_yilan_fix())
