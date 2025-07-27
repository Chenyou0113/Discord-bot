#!/usr/bin/env python3
"""
簡化版台鐵電子看板全縣市測試
"""

import aiohttp
import asyncio
import ssl
import os
from dotenv import load_dotenv
import datetime

# 載入環境變數
load_dotenv()

# 簡化的車站測試清單 (每個縣市選1-2個主要車站)
TEST_STATIONS = {
    "基隆市": [{"name": "基隆", "id": "0900"}],
    "臺北市": [{"name": "臺北", "id": "1020"}],
    "新北市": [{"name": "板橋", "id": "1040"}],
    "桃園市": [{"name": "桃園", "id": "1100"}],
    "新竹市": [{"name": "新竹", "id": "1220"}],
    "新竹縣": [{"name": "湖口", "id": "1180"}],
    "苗栗縣": [{"name": "苗栗", "id": "1371"}],
    "臺中市": [{"name": "臺中", "id": "1500"}],
    "彰化縣": [{"name": "彰化", "id": "1550"}],
    "雲林縣": [{"name": "斗六", "id": "1650"}],
    "嘉義市": [{"name": "嘉義", "id": "1720"}],
    "嘉義縣": [{"name": "民雄", "id": "1690"}],
    "臺南市": [{"name": "臺南", "id": "1840"}],
    "高雄市": [{"name": "高雄", "id": "2010"}],
    "屏東縣": [{"name": "屏東", "id": "2090"}],
    "臺東縣": [{"name": "臺東", "id": "2320"}],
    "花蓮縣": [{"name": "花蓮", "id": "2580"}],
    "宜蘭縣": [{"name": "宜蘭", "id": "7190"}]
}

class QuickTester:
    def __init__(self):
        self.tdx_client_id = os.getenv('TDX_CLIENT_ID')
        self.tdx_client_secret = os.getenv('TDX_CLIENT_SECRET')
        self.access_token = None
        
    async def get_access_token(self):
        """取得 TDX API 存取權杖"""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            auth_url = 'https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token'
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.tdx_client_id,
                'client_secret': self.tdx_client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.post(auth_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get('access_token')
                        return True
                    else:
                        print(f"❌ 無法取得權杖，狀態碼: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ 取得權杖時發生錯誤: {str(e)}")
            return False

    async def test_station(self, county, station_name, station_id):
        """測試單一車站"""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=1000&%24format=JSON"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 篩選出指定車站的資料
                        if isinstance(data, list):
                            station_trains = [
                                train for train in data
                                if train.get('StationID') == station_id
                            ]
                        else:
                            station_trains = []
                        
                        train_count = len(station_trains)
                        print(f"  🚉 {station_name} (ID: {station_id}): {train_count} 筆列車資料")
                        return train_count
                    else:
                        print(f"  ❌ {station_name}: API 錯誤 (狀態碼: {response.status})")
                        return 0
                        
        except Exception as e:
            print(f"  ❌ {station_name}: 發生錯誤 - {str(e)}")
            return 0

    async def run_test(self):
        """執行測試"""
        print("🚆 台鐵電子看板全縣市快速測試")
        print(f"📅 測試時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # 取得權杖
        print("🔑 正在取得 TDX API 存取權杖...")
        if not await self.get_access_token():
            print("❌ 無法取得權杖，測試中止")
            return
        
        print("✅ 成功取得權杖\n")
        
        total_counties = len(TEST_STATIONS)
        successful_counties = 0
        total_trains = 0
        
        # 測試每個縣市
        for county, stations in TEST_STATIONS.items():
            print(f"🔍 測試 {county}:")
            county_trains = 0
            
            for station in stations:
                train_count = await self.test_station(county, station['name'], station['id'])
                county_trains += train_count
                await asyncio.sleep(0.5)  # 避免請求過快
            
            if county_trains > 0:
                successful_counties += 1
                print(f"  ✅ 成功！共 {county_trains} 筆列車資料")
            else:
                print(f"  ❌ 無列車資料")
            
            total_trains += county_trains
            print()
        
        # 總結報告
        print("="*50)
        print("📊 測試總結")
        print("="*50)
        print(f"🏢 總縣市數: {total_counties}")
        print(f"✅ 有資料縣市: {successful_counties}")
        print(f"❌ 無資料縣市: {total_counties - successful_counties}")
        print(f"🚆 總列車數: {total_trains}")
        print(f"📊 成功率: {(successful_counties/total_counties)*100:.1f}%")

async def main():
    tester = QuickTester()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())
