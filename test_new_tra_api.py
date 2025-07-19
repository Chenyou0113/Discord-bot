#!/usr/bin/env python3
"""
測試新的台鐵電子看板 API
檢查新 API 端點的資料格式和篩選功能
"""

import asyncio
import aiohttp
import ssl
import os
import base64
import time
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class TRANewAPITest:
    def __init__(self):
        self.tdx_client_id = os.getenv('TDX_CLIENT_ID')
        self.tdx_client_secret = os.getenv('TDX_CLIENT_SECRET')
        self.tdx_access_token = None
        self.tdx_token_expires_at = 0
        
    async def get_tdx_access_token(self):
        """取得 TDX API 存取權杖"""
        try:
            # 檢查是否有有效的權杖
            current_time = time.time()
            if (self.tdx_access_token and 
                current_time < self.tdx_token_expires_at - 60):
                return self.tdx_access_token
            
            # 準備認證資料
            auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
            
            # 建立 Basic Authentication
            credentials = f"{self.tdx_client_id}:{self.tdx_client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            data = 'grant_type=client_credentials'
            
            print("🔑 正在取得 TDX 存取權杖...")
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.post(auth_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        
                        self.tdx_access_token = token_data.get('access_token')
                        expires_in = token_data.get('expires_in', 3600)
                        self.tdx_token_expires_at = current_time + expires_in
                        
                        print("✅ 成功取得 TDX 存取權杖")
                        return self.tdx_access_token
                    else:
                        error_text = await response.text()
                        print(f"❌ 取得 TDX 存取權杖失敗: {response.status}")
                        print(f"  錯誤訊息: {error_text}")
                        return None
                        
        except Exception as e:
            print(f"❌ TDX 認證過程發生錯誤: {str(e)}")
            return None

    async def test_new_liveboard_api(self):
        """測試新的台鐵電子看板 API"""
        try:
            access_token = await self.get_tdx_access_token()
            if not access_token:
                print("❌ 無法取得存取權杖，停止測試")
                return False
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=500&%24format=JSON"
            print(f"🚆 測試新的台鐵電子看板 API...")
            print(f"  API URL: {url}")
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.get(url, headers=headers) as response:
                    print(f"  HTTP 狀態碼: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 成功取得台鐵電子看板資料")
                        print(f"  總資料筆數: {len(data) if isinstance(data, list) else 0}")
                        
                        if isinstance(data, list) and len(data) > 0:
                            # 分析資料結構
                            print("\n📊 資料結構分析:")
                            sample = data[0]
                            print(f"  範例資料鍵值: {list(sample.keys())}")
                            
                            # 統計各車站的資料筆數
                            station_counts = {}
                            for record in data:
                                station_id = record.get('StationID', 'unknown')
                                station_name = record.get('StationName', {}).get('Zh_tw', 'unknown')
                                key = f"{station_name}({station_id})"
                                station_counts[key] = station_counts.get(key, 0) + 1
                            
                            print(f"\n📈 各車站資料統計 (前10個):")
                            sorted_stations = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)
                            for i, (station, count) in enumerate(sorted_stations[:10]):
                                print(f"  {i+1}. {station}: {count} 筆")
                            
                            # 測試特定車站篩選
                            test_stations = [
                                {"name": "台北", "id": "1020"},
                                {"name": "板橋", "id": "1040"},
                                {"name": "桃園", "id": "1100"}
                            ]
                            
                            print(f"\n🎯 測試車站篩選功能:")
                            for station in test_stations:
                                station_data = [train for train in data if train.get('StationID') == station['id']]
                                print(f"  {station['name']}車站 (ID: {station['id']}): {len(station_data)} 筆資料")
                                
                                if len(station_data) > 0:
                                    print(f"    範例資料:")
                                    sample_train = station_data[0]
                                    train_no = sample_train.get('TrainNo', 'N/A')
                                    direction = sample_train.get('Direction', 'N/A')
                                    scheduled_arrival = sample_train.get('ScheduledArrivalTime', 'N/A')
                                    print(f"      車次: {train_no}, 方向: {direction}, 到站時間: {scheduled_arrival}")
                        
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ API 請求失敗: {response.status}")
                        print(f"  錯誤訊息: {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ 測試新 API 時發生錯誤: {str(e)}")
            import traceback
            print(f"  詳細錯誤: {traceback.format_exc()}")
            return False

    async def compare_apis(self):
        """比較新舊 API 的差異"""
        print("\n🔍 比較新舊 API:")
        
        # 測試新 API
        print("\n1️⃣ 測試新 API (所有車站資料)")
        new_api_success = await self.test_new_liveboard_api()
        
        # 測試舊 API (台北車站)
        print("\n2️⃣ 測試舊 API (單一車站)")
        old_api_success = await self.test_old_liveboard_api("1020")
        
        print(f"\n📊 測試結果比較:")
        print(f"  新 API: {'✅ 成功' if new_api_success else '❌ 失敗'}")
        print(f"  舊 API: {'✅ 成功' if old_api_success else '❌ 失敗'}")

    async def test_old_liveboard_api(self, station_id="1020"):
        """測試舊的台鐵電子看板 API (單一車站)"""
        try:
            access_token = await self.get_tdx_access_token()
            if not access_token:
                return False
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard/Station/{station_id}?%24format=JSON"
            print(f"  舊 API URL: {url}")
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.get(url, headers=headers) as response:
                    print(f"  HTTP 狀態碼: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"  台北車站資料筆數: {len(data) if isinstance(data, list) else 0}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"  錯誤: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            print(f"  測試舊 API 錯誤: {str(e)}")
            return False

async def main():
    print("=" * 60)
    print("🚆 台鐵電子看板新 API 測試")
    print("=" * 60)
    
    tester = TRANewAPITest()
    
    # 執行比較測試
    await tester.compare_apis()
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
