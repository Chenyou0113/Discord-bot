#!/usr/bin/env python3
"""
重點縣市台鐵電子看板驗證測試
"""

import aiohttp
import asyncio
import ssl
import os
from dotenv import load_dotenv
import datetime

# 載入環境變數
load_dotenv()

async def test_key_stations():
    """測試關鍵車站"""
    
    # 關鍵測試車站
    test_stations = [
        {"county": "宜蘭縣", "name": "宜蘭", "id": "7190"},  # 已修正的宜蘭縣
        {"county": "臺北市", "name": "臺北", "id": "1020"},
        {"county": "高雄市", "name": "高雄", "id": "2010"},
        {"county": "臺中市", "name": "臺中", "id": "1500"},
        {"county": "花蓮縣", "name": "花蓮", "id": "2580"},
    ]
    
    print("🚆 台鐵電子看板關鍵車站驗證測試")
    print(f"📅 測試時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # 取得TDX權杖
    tdx_client_id = os.getenv('TDX_CLIENT_ID')
    tdx_client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 取得權杖
        auth_url = 'https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token'
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': tdx_client_id,
            'client_secret': tdx_client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as auth_session:
            async with auth_session.post(auth_url, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data.get('access_token')
                    print("✅ 成功取得 TDX API 權杖\n")
                else:
                    print(f"❌ 無法取得權杖，狀態碼: {response.status}")
                    return
        
        # 測試各車站
        successful_tests = 0
        total_trains = 0
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            for station in test_stations:
                county = station['county']
                name = station['name']
                station_id = station['id']
                
                print(f"🔍 測試 {county} - {name} (ID: {station_id})")
                
                try:
                    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=1000&%24format=JSON"
                    
                    api_headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
            async with session.get(url, headers=api_headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 篩選車站資料
                    if isinstance(data, list):
                        station_trains = [
                            train for train in data
                            if train.get('StationID') == station_id
                        ]
                    else:
                        station_trains = []
                    
                    train_count = len(station_trains)
                    
                    if train_count > 0:
                        print(f"  ✅ 成功！找到 {train_count} 筆列車資料")
                        successful_tests += 1
                        total_trains += train_count
                        
                        # 顯示前2筆列車
                        for i, train in enumerate(station_trains[:2], 1):
                            train_no = train.get('TrainNo', 'N/A')
                            train_type = train.get('TrainTypeName', {}).get('Zh_tw', 'N/A')
                            delay = train.get('DelayTime', 0)
                            delay_str = f"誤點{delay}分" if delay > 0 else "準點"
                            print(f"    🚆 {train_no}車次 ({train_type}) - {delay_str}")
                    else:
                        print(f"  🔍 目前無列車資訊")
                        
                elif response.status == 429:
                    print(f"  ⏱️ API 請求頻率限制")
                else:
                    print(f"  ❌ API 錯誤 (狀態碼: {response.status})")
                    
            except Exception as e:
                print(f"  ❌ 測試錯誤: {str(e)}")
            
            print()
            await asyncio.sleep(2)  # 避免請求過快
        
        # 總結
        print("="*50)
        print("📊 測試總結")
        print("="*50)
        print(f"🚉 測試車站數: {len(test_stations)}")
        print(f"✅ 成功車站數: {successful_tests}")
        print(f"🚆 總列車數: {total_trains}")
        print(f"📊 成功率: {(successful_tests/len(test_stations))*100:.1f}%")
        
        if successful_tests >= 3:
            print("\n🎉 台鐵電子看板功能運作正常！")
            print("✅ 宜蘭縣車站ID修正成功")
        else:
            print("\n⚠️ 部分車站可能需要進一步檢查")
            
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")

# 執行測試
if __name__ == "__main__":
    asyncio.run(test_key_stations())
