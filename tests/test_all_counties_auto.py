#!/usr/bin/env python3
"""
自動測試所有縣市的台鐵電子看板功能 (非互動模式)
"""

import aiohttp
import asyncio
import ssl
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
import json
import datetime

# 載入環境變數
load_dotenv()

# 台鐵車站資料按縣市分類 (從主程式複製)
TRA_STATIONS = {
    "基隆市": [
        {"name": "基隆", "id": "0900"},
        {"name": "三坑", "id": "0910"},
        {"name": "八堵", "id": "0920"}
    ],
    "臺北市": [
        {"name": "七堵", "id": "0930"},
        {"name": "百福", "id": "0940"},
        {"name": "五堵", "id": "0950"},
        {"name": "汐止", "id": "0960"},
        {"name": "汐科", "id": "0970"},
        {"name": "南港", "id": "1000"},
        {"name": "松山", "id": "1010"},
        {"name": "臺北", "id": "1020"},
        {"name": "萬華", "id": "1030"}
    ],
    "新北市": [
        {"name": "板橋", "id": "1040"},
        {"name": "浮洲", "id": "1050"},
        {"name": "樹林", "id": "1060"},
        {"name": "南樹林", "id": "1070"},
        {"name": "山佳", "id": "1080"},
        {"name": "鶯歌", "id": "1090"},
        {"name": "福隆", "id": "0140"},
        {"name": "貢寮", "id": "0150"},
        {"name": "雙溪", "id": "0160"},
        {"name": "牡丹", "id": "0170"},
        {"name": "三貂嶺", "id": "0180"},
        {"name": "大華", "id": "0190"},
        {"name": "十分", "id": "0200"},
        {"name": "望古", "id": "0210"},
        {"name": "嶺腳", "id": "0220"},
        {"name": "平溪", "id": "0230"},
        {"name": "菁桐", "id": "0240"}
    ],
    "桃園市": [
        {"name": "桃園", "id": "1100"},
        {"name": "內壢", "id": "1110"},
        {"name": "中壢", "id": "1120"}
    ],
    "新竹縣": [
        {"name": "新富", "id": "1160"},
        {"name": "北湖", "id": "1170"},
        {"name": "湖口", "id": "1180"}
    ],
    "新竹市": [
        {"name": "北新竹", "id": "1210"},
        {"name": "新竹", "id": "1220"},
        {"name": "三姓橋", "id": "1230"}
    ],
    "苗栗縣": [
        {"name": "崎頂", "id": "1250"},
        {"name": "竹南", "id": "1260"},
        {"name": "談文", "id": "1270"}
    ],
    "臺中市": [
        {"name": "日南", "id": "1350"},
        {"name": "大甲", "id": "1360"},
        {"name": "臺中港", "id": "1370"}
    ],
    "彰化縣": [
        {"name": "成功", "id": "1430"},
        {"name": "彰化", "id": "1550"},
        {"name": "花壇", "id": "1560"}
    ],
    "雲林縣": [
        {"name": "林內", "id": "1630"},
        {"name": "石榴", "id": "1640"},
        {"name": "斗六", "id": "1650"}
    ],
    "嘉義縣": [
        {"name": "大林", "id": "1680"},
        {"name": "民雄", "id": "1690"},
        {"name": "水上", "id": "1700"}
    ],
    "嘉義市": [
        {"name": "嘉義", "id": "1720"}
    ],
    "臺南市": [
        {"name": "後壁", "id": "1730"},
        {"name": "新營", "id": "1740"},
        {"name": "柳營", "id": "1750"}
    ],
    "高雄市": [
        {"name": "大湖", "id": "1900"},
        {"name": "路竹", "id": "1910"},
        {"name": "岡山", "id": "1920"}
    ],
    "屏東縣": [
        {"name": "六塊厝", "id": "2080"},
        {"name": "屏東", "id": "2090"},
        {"name": "歸來", "id": "2100"}
    ],
    "臺東縣": [
        {"name": "古莊", "id": "2250"},
        {"name": "大武", "id": "2260"},
        {"name": "瀧溪", "id": "2270"}
    ],
    "花蓮縣": [
        {"name": "東竹", "id": "2410"},
        {"name": "東里", "id": "2420"},
        {"name": "玉里", "id": "2430"}
    ],
    "宜蘭縣": [
        {"name": "漢本", "id": "7070"},
        {"name": "武塔", "id": "7080"},
        {"name": "南澳", "id": "7090"}
    ]
}

class TRALiveboardTester:
    def __init__(self):
        self.tdx_client_id = os.getenv('TDX_CLIENT_ID')
        self.tdx_client_secret = os.getenv('TDX_CLIENT_SECRET')
        self.access_token = None
        self.test_results = {}
        
    async def get_tdx_access_token(self) -> Optional[str]:
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.post(auth_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get('access_token')
                        return self.access_token
                    else:
                        print(f"❌ 無法取得存取權杖，狀態碼: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ 取得存取權杖時發生錯誤: {str(e)}")
            return None

    async def test_county_liveboard(self, county: str, stations: List[Dict[str, str]]) -> Dict[str, Any]:
        """測試指定縣市的台鐵電子看板功能"""
        print(f"\n🔍 測試 {county} 台鐵電子看板...")
        
        result = {
            'county': county,
            'total_stations': len(stations),
            'tested_stations': 0,
            'successful_stations': 0,
            'failed_stations': 0,
            'total_trains': 0,
            'station_results': [],
            'errors': []
        }
        
        # 測試前2個車站 (避免測試太多車站導致超時)
        test_stations = stations[:2]
        
        for station in test_stations:
            station_name = station['name']
            station_id = station['id']
            
            try:
                result['tested_stations'] += 1
                print(f"  📍 測試 {station_name} (ID: {station_id})...")
                
                # 取得該車站的電子看板資料
                trains = await self.get_station_liveboard(station_id)
                
                if trains is not None:
                    result['successful_stations'] += 1
                    result['total_trains'] += len(trains)
                    
                    station_result = {
                        'name': station_name,
                        'id': station_id,
                        'status': 'success',
                        'train_count': len(trains),
                        'sample_trains': trains[:2] if trains else []  # 只保存前2筆列車資料
                    }
                    result['station_results'].append(station_result)
                    
                    print(f"    ✅ 成功！找到 {len(trains)} 筆列車資料")
                    
                else:
                    result['failed_stations'] += 1
                    station_result = {
                        'name': station_name,
                        'id': station_id,
                        'status': 'failed',
                        'train_count': 0,
                        'error': '無法取得資料'
                    }
                    result['station_results'].append(station_result)
                    print(f"    ❌ 失敗！無法取得資料")
                    
            except Exception as e:
                result['failed_stations'] += 1
                error_msg = f"測試 {station_name} 時發生錯誤: {str(e)}"
                result['errors'].append(error_msg)
                print(f"    ❌ 錯誤: {str(e)}")
                
                station_result = {
                    'name': station_name,
                    'id': station_id,
                    'status': 'error',
                    'train_count': 0,
                    'error': str(e)
                }
                result['station_results'].append(station_result)
            
            # 避免請求過於頻繁
            await asyncio.sleep(0.5)
        
        return result

    async def get_station_liveboard(self, station_id: str) -> Optional[List[Dict[str, Any]]]:
        """取得指定車站的電子看板資料"""
        try:
            if not self.access_token:
                await self.get_tdx_access_token()
                
            if not self.access_token:
                return None
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=1000&%24format=JSON"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
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
                        
                        return station_trains
                    else:
                        print(f"    API 回應狀態碼: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"    取得車站資料時發生錯誤: {str(e)}")
            return None

    async def test_all_counties(self):
        """測試所有縣市的台鐵電子看板功能"""
        print("🚆 開始測試所有縣市的台鐵電子看板功能")
        print(f"📅 測試時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 取得 access token
        if not await self.get_tdx_access_token():
            print("❌ 無法取得 TDX API 存取權杖，測試中止")
            return
        
        print("✅ 成功取得 TDX API 存取權杖")
        
        total_counties = len(TRA_STATIONS)
        successful_counties = 0
        total_stations_tested = 0
        total_trains_found = 0
        
        # 測試每個縣市
        for county, stations in TRA_STATIONS.items():
            try:
                result = await self.test_county_liveboard(county, stations)
                self.test_results[county] = result
                
                if result['successful_stations'] > 0:
                    successful_counties += 1
                
                total_stations_tested += result['tested_stations']
                total_trains_found += result['total_trains']
                
            except Exception as e:
                print(f"❌ 測試 {county} 時發生錯誤: {str(e)}")
                self.test_results[county] = {
                    'county': county,
                    'status': 'error',
                    'error': str(e)
                }
        
        # 顯示總結報告
        print("\n" + "="*60)
        print("📊 測試總結報告")
        print("="*60)
        print(f"🏢 總縣市數: {total_counties}")
        print(f"✅ 成功縣市數: {successful_counties}")
        print(f"❌ 失敗縣市數: {total_counties - successful_counties}")
        print(f"🚉 總測試車站數: {total_stations_tested}")
        print(f"🚆 總找到列車數: {total_trains_found}")
        
        # 顯示詳細結果
        print("\n📋 詳細結果:")
        for county, result in self.test_results.items():
            if isinstance(result, dict) and 'successful_stations' in result:
                status = "✅" if result['successful_stations'] > 0 else "❌"
                print(f"{status} {county}: {result['successful_stations']}/{result['tested_stations']} 車站成功, 共 {result['total_trains']} 筆列車")
                
                # 顯示成功的車站詳情
                for station_result in result.get('station_results', []):
                    if station_result['status'] == 'success' and station_result['train_count'] > 0:
                        print(f"    🚉 {station_result['name']}: {station_result['train_count']} 筆列車")
            else:
                print(f"❌ {county}: 測試失敗")
        
        # 儲存結果到檔案
        await self.save_results()

    async def save_results(self):
        """儲存測試結果到檔案"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tra_liveboard_test_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 測試結果已儲存至: {filename}")
            
        except Exception as e:
            print(f"❌ 儲存結果時發生錯誤: {str(e)}")

async def main():
    """主程式"""
    tester = TRALiveboardTester()
    await tester.test_all_counties()

if __name__ == "__main__":
    asyncio.run(main())
