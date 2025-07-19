#!/usr/bin/env python3
"""
測試所有縣市的台鐵電子看板功能
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
        {"name": "中壢", "id": "1120"},
        {"name": "埔心", "id": "1130"},
        {"name": "楊梅", "id": "1140"},
        {"name": "富岡", "id": "1150"}
    ],
    "新竹縣": [
        {"name": "新富", "id": "1160"},
        {"name": "北湖", "id": "1170"},
        {"name": "湖口", "id": "1180"},
        {"name": "新豐", "id": "1190"},
        {"name": "竹北", "id": "1200"}
    ],
    "新竹市": [
        {"name": "北新竹", "id": "1210"},
        {"name": "新竹", "id": "1220"},
        {"name": "三姓橋", "id": "1230"},
        {"name": "香山", "id": "1240"}
    ],
    "苗栗縣": [
        {"name": "崎頂", "id": "1250"},
        {"name": "竹南", "id": "1260"},
        {"name": "談文", "id": "1270"},
        {"name": "大山", "id": "1280"},
        {"name": "後龍", "id": "1290"},
        {"name": "龍港", "id": "1300"},
        {"name": "白沙屯", "id": "1310"},
        {"name": "新埔", "id": "1320"},
        {"name": "通霄", "id": "1330"},
        {"name": "苑裡", "id": "1340"},
        {"name": "造橋", "id": "1351"},
        {"name": "豐富", "id": "1361"},
        {"name": "苗栗", "id": "1371"},
        {"name": "南勢", "id": "1381"},
        {"name": "銅鑼", "id": "1391"},
        {"name": "三義", "id": "1401"}
    ],
    "臺中市": [
        {"name": "日南", "id": "1350"},
        {"name": "大甲", "id": "1360"},
        {"name": "臺中港", "id": "1370"},
        {"name": "清水", "id": "1380"},
        {"name": "沙鹿", "id": "1390"},
        {"name": "龍井", "id": "1400"},
        {"name": "大肚", "id": "1410"},
        {"name": "追分", "id": "1420"},
        {"name": "泰安", "id": "1411"},
        {"name": "后里", "id": "1421"},
        {"name": "豐原", "id": "1431"},
        {"name": "栗林", "id": "1441"},
        {"name": "潭子", "id": "1451"},
        {"name": "頭家厝", "id": "1461"},
        {"name": "松竹", "id": "1471"},
        {"name": "太原", "id": "1481"},
        {"name": "精武", "id": "1491"},
        {"name": "臺中", "id": "1500"},
        {"name": "五權", "id": "1510"},
        {"name": "大慶", "id": "1520"},
        {"name": "烏日", "id": "1530"},
        {"name": "新烏日", "id": "1540"}
    ],
    "彰化縣": [
        {"name": "成功", "id": "1430"},
        {"name": "彰化", "id": "1550"},
        {"name": "花壇", "id": "1560"},
        {"name": "大村", "id": "1570"},
        {"name": "員林", "id": "1580"},
        {"name": "永靖", "id": "1590"},
        {"name": "社頭", "id": "1600"},
        {"name": "田中", "id": "1610"},
        {"name": "二水", "id": "1620"}
    ],
    "雲林縣": [
        {"name": "林內", "id": "1630"},
        {"name": "石榴", "id": "1640"},
        {"name": "斗六", "id": "1650"},
        {"name": "斗南", "id": "1660"},
        {"name": "石龜", "id": "1670"}
    ],
    "嘉義縣": [
        {"name": "大林", "id": "1680"},
        {"name": "民雄", "id": "1690"},
        {"name": "水上", "id": "1700"},
        {"name": "南靖", "id": "1710"}
    ],
    "嘉義市": [
        {"name": "嘉義", "id": "1720"}
    ],
    "臺南市": [
        {"name": "後壁", "id": "1730"},
        {"name": "新營", "id": "1740"},
        {"name": "柳營", "id": "1750"},
        {"name": "林鳳營", "id": "1760"},
        {"name": "隆田", "id": "1770"},
        {"name": "拔林", "id": "1780"},
        {"name": "善化", "id": "1790"},
        {"name": "南科", "id": "1800"},
        {"name": "新市", "id": "1810"},
        {"name": "永康", "id": "1820"},
        {"name": "大橋", "id": "1830"},
        {"name": "臺南", "id": "1840"},
        {"name": "保安", "id": "1850"},
        {"name": "仁德", "id": "1860"},
        {"name": "中洲", "id": "1870"},
        {"name": "長榮大學", "id": "1880"},
        {"name": "沙崙", "id": "1890"}
    ],
    "高雄市": [
        {"name": "大湖", "id": "1900"},
        {"name": "路竹", "id": "1910"},
        {"name": "岡山", "id": "1920"},
        {"name": "橋頭", "id": "1930"},
        {"name": "楠梓", "id": "1940"},
        {"name": "新左營", "id": "1950"},
        {"name": "左營", "id": "1960"},
        {"name": "內惟", "id": "1970"},
        {"name": "美術館", "id": "1980"},
        {"name": "鼓山", "id": "1990"},
        {"name": "三塊厝", "id": "2000"},
        {"name": "高雄", "id": "2010"},
        {"name": "民族", "id": "2020"},
        {"name": "科工館", "id": "2030"},
        {"name": "正義", "id": "2040"},
        {"name": "鳳山", "id": "2050"},
        {"name": "後庄", "id": "2060"},
        {"name": "九曲堂", "id": "2070"}
    ],
    "屏東縣": [
        {"name": "六塊厝", "id": "2080"},
        {"name": "屏東", "id": "2090"},
        {"name": "歸來", "id": "2100"},
        {"name": "麟洛", "id": "2110"},
        {"name": "西勢", "id": "2120"},
        {"name": "竹田", "id": "2130"},
        {"name": "潮州", "id": "2140"},
        {"name": "崁頂", "id": "2150"},
        {"name": "南州", "id": "2160"},
        {"name": "鎮安", "id": "2170"},
        {"name": "林邊", "id": "2180"},
        {"name": "佳冬", "id": "2190"},
        {"name": "東海", "id": "2200"},
        {"name": "枋寮", "id": "2210"},
        {"name": "加祿", "id": "2220"},
        {"name": "內獅", "id": "2230"},
        {"name": "枋山", "id": "2240"}
    ],
    "臺東縣": [
        {"name": "古莊", "id": "2250"},
        {"name": "大武", "id": "2260"},
        {"name": "瀧溪", "id": "2270"},
        {"name": "金崙", "id": "2280"},
        {"name": "太麻里", "id": "2290"},
        {"name": "知本", "id": "2300"},
        {"name": "康樂", "id": "2310"},
        {"name": "臺東", "id": "2320"},
        {"name": "山里", "id": "2330"},
        {"name": "鹿野", "id": "2340"},
        {"name": "瑞源", "id": "2350"},
        {"name": "瑞和", "id": "2360"},
        {"name": "關山", "id": "2370"},
        {"name": "海端", "id": "2380"},
        {"name": "池上", "id": "2390"},
        {"name": "富里", "id": "2400"}
    ],
    "花蓮縣": [
        {"name": "東竹", "id": "2410"},
        {"name": "東里", "id": "2420"},
        {"name": "玉里", "id": "2430"},
        {"name": "三民", "id": "2440"},
        {"name": "瑞穗", "id": "2450"},
        {"name": "富源", "id": "2460"},
        {"name": "大富", "id": "2470"},
        {"name": "光復", "id": "2480"},
        {"name": "萬榮", "id": "2490"},
        {"name": "鳳林", "id": "2500"},
        {"name": "南平", "id": "2510"},
        {"name": "林榮新光", "id": "2520"},
        {"name": "豐田", "id": "2530"},
        {"name": "壽豐", "id": "2540"},
        {"name": "平和", "id": "2550"},
        {"name": "志學", "id": "2560"},
        {"name": "吉安", "id": "2570"},
        {"name": "花蓮", "id": "2580"},
        {"name": "北埔", "id": "2590"},
        {"name": "景美", "id": "2600"},
        {"name": "新城", "id": "2610"},
        {"name": "崇德", "id": "2620"},
        {"name": "和仁", "id": "2630"},
        {"name": "和平", "id": "2640"}
    ],
    "宜蘭縣": [
        {"name": "漢本", "id": "7070"},
        {"name": "武塔", "id": "7080"},
        {"name": "南澳", "id": "7090"},
        {"name": "東澳", "id": "7100"},
        {"name": "永樂", "id": "7110"},
        {"name": "蘇澳", "id": "7120"},
        {"name": "蘇澳新", "id": "7130"},
        {"name": "新馬", "id": "7140"},
        {"name": "冬山", "id": "7150"},
        {"name": "羅東", "id": "7160"},
        {"name": "中里", "id": "7170"},
        {"name": "二結", "id": "7180"},
        {"name": "宜蘭", "id": "7190"},
        {"name": "四城", "id": "7200"},
        {"name": "礁溪", "id": "7210"},
        {"name": "頂埔", "id": "7220"},
        {"name": "頭城", "id": "7230"},
        {"name": "外澳", "id": "7240"},
        {"name": "龜山", "id": "7250"},
        {"name": "大溪", "id": "7260"},
        {"name": "大里", "id": "7270"},
        {"name": "石城", "id": "7280"}
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
        
        # 測試前幾個車站 (避免測試太多車站導致超時)
        test_stations = stations[:3]  # 每個縣市測試前3個車站
        
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
                        'trains': trains[:3]  # 只保存前3筆列車資料
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
            await asyncio.sleep(1)
        
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

    async def test_specific_counties(self, counties: List[str]):
        """測試指定縣市"""
        print(f"🚆 測試指定縣市: {', '.join(counties)}")
        print(f"📅 測試時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 取得 access token
        if not await self.get_tdx_access_token():
            print("❌ 無法取得 TDX API 存取權杖，測試中止")
            return
        
        print("✅ 成功取得 TDX API 存取權杖")
        
        for county in counties:
            if county in TRA_STATIONS:
                stations = TRA_STATIONS[county]
                result = await self.test_county_liveboard(county, stations)
                self.test_results[county] = result
            else:
                print(f"❌ 找不到縣市: {county}")

async def main():
    """主程式"""
    tester = TRALiveboardTester()
    
    print("🚆 台鐵電子看板測試程式")
    print("選擇測試模式:")
    print("1. 測試所有縣市")
    print("2. 測試指定縣市")
    print("3. 快速測試 (宜蘭縣)")
    
    try:
        choice = input("請輸入選擇 (1-3): ").strip()
        
        if choice == "1":
            await tester.test_all_counties()
        elif choice == "2":
            print("\n可用縣市:")
            for i, county in enumerate(TRA_STATIONS.keys(), 1):
                print(f"{i:2d}. {county}")
            
            county_input = input("\n請輸入縣市名稱 (多個用逗號分隔): ").strip()
            counties = [c.strip() for c in county_input.split(',')]
            await tester.test_specific_counties(counties)
        elif choice == "3":
            await tester.test_specific_counties(["宜蘭縣"])
        else:
            print("❌ 無效選擇")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 測試被使用者中斷")
    except Exception as e:
        print(f"\n❌ 程式執行時發生錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
