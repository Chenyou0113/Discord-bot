#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專門測試宜蘭台鐵電子看板資料
"""

import asyncio
import aiohttp
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

class YilanTraTester:
    def __init__(self):
        self.tdx_client_id = os.getenv('TDX_CLIENT_ID')
        self.tdx_client_secret = os.getenv('TDX_CLIENT_SECRET')
        self.tdx_access_token = None
        
    async def get_tdx_access_token(self):
        """取得TDX存取權杖"""
        if not self.tdx_client_id or not self.tdx_client_secret:
            print("❌ TDX憑證未設定")
            return None
            
        try:
            auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.tdx_client_id,
                'client_secret': self.tdx_client_secret
            }
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.post(auth_url, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.tdx_access_token = token_data.get('access_token')
                        print("✅ TDX認證成功")
                        return self.tdx_access_token
                    else:
                        print(f"❌ TDX認證失敗: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ TDX認證錯誤: {str(e)}")
            return None
    
    async def search_yilan_stations(self):
        """搜尋宜蘭相關車站"""
        print("🔍 搜尋宜蘭相關車站...")
        
        access_token = await self.get_tdx_access_token()
        if not access_token:
            return
        
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            
            # 使用新的全域API端點
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard?%24top=1000&%24format=JSON"
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.get(url, headers=headers) as response:
                    print(f"📡 API回應: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"📦 總資料筆數: {len(data)}")
                        
                        # 宜蘭相關關鍵字
                        yilan_keywords = [
                            '宜蘭', '羅東', '蘇澳', '頭城', '礁溪', '冬山', 
                            '二結', '中里', '四城', '頂埔', '永樂', '南澳', 
                            '東澳', '新馬', '武塔', '漢本', '大溪', '大里', 
                            '石城', '外澳', '龜山'
                        ]
                        
                        yilan_stations = {}
                        all_stations = {}
                        
                        for train in data:
                            station_id = train.get('StationID', '')
                            station_name = train.get('StationName', {})
                            
                            if isinstance(station_name, dict):
                                zh_name = station_name.get('Zh_tw', '')
                            else:
                                zh_name = str(station_name)
                            
                            # 記錄所有車站
                            if station_id and zh_name:
                                all_stations[station_id] = zh_name
                            
                            # 檢查是否為宜蘭相關車站
                            for keyword in yilan_keywords:
                                if keyword in zh_name:
                                    if station_id not in yilan_stations:
                                        yilan_stations[station_id] = {
                                            'name': zh_name,
                                            'trains': []
                                        }
                                    
                                    yilan_stations[station_id]['trains'].append({
                                        'train_no': train.get('TrainNo', 'N/A'),
                                        'direction': train.get('Direction', 0),
                                        'arrival_time': train.get('ScheduledArrivalTime', 'N/A'),
                                        'departure_time': train.get('ScheduledDepartureTime', 'N/A'),
                                        'delay': train.get('DelayTime', 0),
                                        'ending_station': train.get('EndingStationName', {}).get('Zh_tw', 'N/A') if isinstance(train.get('EndingStationName', {}), dict) else train.get('EndingStationName', 'N/A')
                                    })
                                    break
                        
                        if yilan_stations:
                            print(f"\n✅ 找到 {len(yilan_stations)} 個宜蘭相關車站!")
                            
                            for station_id, station_info in yilan_stations.items():
                                station_name = station_info['name']
                                trains = station_info['trains']
                                print(f"\n🚉 {station_name} (ID: {station_id}) - {len(trains)} 筆班車資料")
                                
                                # 顯示前5筆班車資料
                                for i, train in enumerate(trains[:5]):
                                    direction_str = "順行(南下)" if train['direction'] == 0 else "逆行(北上)"
                                    delay_str = f" 誤點{train['delay']}分" if train['delay'] > 0 else ""
                                    
                                    print(f"  {i+1}. 車次:{train['train_no']} | {direction_str} | 終點:{train['ending_station']}")
                                    print(f"     到站:{train['arrival_time']} | 開車:{train['departure_time']}{delay_str}")
                                
                                if len(trains) > 5:
                                    print(f"     ... 還有 {len(trains) - 5} 筆資料")
                            
                            # 生成修正建議
                            print(f"\n💡 修正建議:")
                            print(f"機器人程式碼中的宜蘭車站ID可能需要更新:")
                            
                            # 機器人程式碼中的宜蘭車站定義
                            bot_yilan_stations = {
                                "2650": "漢本", "2660": "武塔", "2670": "南澳", "2680": "東澳",
                                "2690": "永樂", "2700": "蘇澳", "2710": "蘇澳新", "2720": "新馬",
                                "2730": "冬山", "2740": "羅東", "2750": "中里", "2760": "二結",
                                "2770": "宜蘭", "2780": "四城", "2790": "礁溪", "2800": "頂埔",
                                "2810": "頭城", "2820": "外澳", "2830": "龜山", "2840": "大溪",
                                "2850": "大里", "2860": "石城"
                            }
                            
                            print(f"\n📊 ID對照表:")
                            print(f"{'車站名稱':<8} | {'機器人ID':<8} | {'實際API ID':<10} | 狀態")
                            print("-" * 50)
                            
                            for bot_id, bot_name in bot_yilan_stations.items():
                                actual_id = None
                                for api_id, api_name in yilan_stations.items():
                                    if bot_name == api_name:
                                        actual_id = api_id
                                        break
                                
                                if actual_id:
                                    status = "✅ 匹配" if bot_id == actual_id else "❌ 不匹配"
                                    print(f"{bot_name:<8} | {bot_id:<8} | {actual_id:<10} | {status}")
                                else:
                                    print(f"{bot_name:<8} | {bot_id:<8} | {'無資料':<10} | ❌ 無資料")
                        
                        else:
                            print("\n❌ 沒有找到宜蘭相關車站資料")
                            print("可能原因:")
                            print("1. 當前時間宜蘭線沒有班車")
                            print("2. TDX API不包含宜蘭線電子看板資料") 
                            print("3. API資料更新延遲")
                            
                            # 顯示車站ID範圍供參考
                            if all_stations:
                                station_ids = list(all_stations.keys())
                                print(f"\n📊 API中的車站統計:")
                                print(f"總車站數: {len(station_ids)}")
                                print(f"車站ID範圍: {min(station_ids)} ~ {max(station_ids)}")
                                
                                # 按ID範圍分組
                                id_ranges = {
                                    '0xxx': [sid for sid in station_ids if sid.startswith('0')],
                                    '1xxx': [sid for sid in station_ids if sid.startswith('1')],
                                    '2xxx': [sid for sid in station_ids if sid.startswith('2')],
                                    '3xxx': [sid for sid in station_ids if sid.startswith('3')],
                                    '4xxx': [sid for sid in station_ids if sid.startswith('4')],
                                    '5xxx': [sid for sid in station_ids if sid.startswith('5')],
                                    '6xxx': [sid for sid in station_ids if sid.startswith('6')],
                                    '7xxx': [sid for sid in station_ids if sid.startswith('7')],
                                }
                                
                                for range_name, ids in id_ranges.items():
                                    if ids:
                                        print(f"{range_name}系列: {len(ids)}個車站")
                                        if range_name == '2xxx':
                                            print(f"  27xx系列: {len([sid for sid in ids if sid.startswith('27')])}個")
                                            print(f"  範例: {sorted(ids)[:5]}")
                    
                    elif response.status == 429:
                        print("❌ API請求頻率過高，請稍後再試")
                    else:
                        error_text = await response.text()
                        print(f"❌ API請求失敗: {error_text[:200]}")
                        
        except Exception as e:
            print(f"❌ 搜尋過程發生錯誤: {str(e)}")
            import traceback
            print(f"詳細錯誤: {traceback.format_exc()}")

async def main():
    print("=" * 60)
    print("🚆 宜蘭台鐵電子看板專項測試")
    print("=" * 60)
    
    tester = YilanTraTester()
    await tester.search_yilan_stations()
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
