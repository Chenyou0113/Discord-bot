#!/usr/bin/env python3
"""
台鐵到站資訊錯誤診斷腳本
檢查 TDX API 連接和台鐵電子看板功能
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

class TRADiagnostic:
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
                        print(f"  權杖長度: {len(self.tdx_access_token) if self.tdx_access_token else 0}")
                        print(f"  有效期限: {expires_in} 秒")
                        return self.tdx_access_token
                    else:
                        error_text = await response.text()
                        print(f"❌ 取得 TDX 存取權杖失敗: {response.status}")
                        print(f"  錯誤訊息: {error_text}")
                        return None
                        
        except Exception as e:
            print(f"❌ TDX 認證過程發生錯誤: {str(e)}")
            return None

    async def test_tra_liveboard(self, station_id="1020"):  # 預設台北車站
        """測試台鐵電子看板 API"""
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
            
            url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard/Station/{station_id}?%24format=JSON"
            print(f"🚆 測試台鐵電子看板 API...")
            print(f"  車站 ID: {station_id}")
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
                        print(f"  資料筆數: {len(data) if isinstance(data, list) else 0}")
                        
                        if isinstance(data, list) and len(data) > 0:
                            print("  範例資料:")
                            for i, train in enumerate(data[:3]):  # 顯示前3筆
                                print(f"    {i+1}. 車次: {train.get('TrainNo', 'N/A')}")
                                print(f"       方向: {train.get('Direction', 'N/A')}")
                                print(f"       到站時間: {train.get('ScheduledArrivalTime', 'N/A')}")
                                print(f"       月台: {train.get('Platform', 'N/A')}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ API 請求失敗: {response.status}")
                        print(f"  錯誤訊息: {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ 測試台鐵電子看板時發生錯誤: {str(e)}")
            import traceback
            print(f"  詳細錯誤: {traceback.format_exc()}")
            return False

    async def test_multiple_stations(self):
        """測試多個車站的電子看板"""
        test_stations = [
            {"name": "台北", "id": "1020"},
            {"name": "板橋", "id": "1040"},
            {"name": "桃園", "id": "1100"},
            {"name": "新竹", "id": "1220"}
        ]
        
        print("\n🧪 測試多個車站的電子看板:")
        results = {}
        
        for station in test_stations:
            print(f"\n--- 測試 {station['name']} 車站 ---")
            success = await self.test_tra_liveboard(station['id'])
            results[station['name']] = success
            await asyncio.sleep(1)  # 避免請求過於頻繁
        
        print("\n📊 測試結果摘要:")
        for station, success in results.items():
            status = "✅ 成功" if success else "❌ 失敗"
            print(f"  {station}: {status}")
        
        return results

    async def check_api_credentials(self):
        """檢查 API 憑證設定"""
        print("🔍 檢查 TDX API 憑證設定:")
        
        if not self.tdx_client_id:
            print("❌ TDX_CLIENT_ID 未設定")
            return False
        else:
            print(f"✅ TDX_CLIENT_ID: {self.tdx_client_id[:8]}...")
        
        if not self.tdx_client_secret:
            print("❌ TDX_CLIENT_SECRET 未設定")
            return False
        else:
            print(f"✅ TDX_CLIENT_SECRET: {self.tdx_client_secret[:8]}...")
        
        return True

async def main():
    print("=" * 60)
    print("🔧 台鐵到站資訊錯誤診斷")
    print("=" * 60)
    
    diagnostic = TRADiagnostic()
    
    # 1. 檢查憑證設定
    print("\n1️⃣ 檢查 API 憑證設定")
    if not await diagnostic.check_api_credentials():
        print("\n❌ API 憑證設定有問題，無法繼續測試")
        return
    
    # 2. 測試 TDX 認證
    print("\n2️⃣ 測試 TDX API 認證")
    token = await diagnostic.get_tdx_access_token()
    if not token:
        print("\n❌ TDX API 認證失敗，無法繼續測試")
        return
    
    # 3. 測試單一車站
    print("\n3️⃣ 測試台北車站電子看板")
    single_test = await diagnostic.test_tra_liveboard("1020")
    
    # 4. 測試多個車站
    if single_test:
        print("\n4️⃣ 測試多個車站")
        await diagnostic.test_multiple_stations()
    
    print("\n" + "=" * 60)
    print("診斷完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
