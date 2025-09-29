"""
使用TDX認證測試捷運即時電子看板API
"""
import asyncio
import aiohttp
import json
import ssl
import os
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def get_tdx_access_token():
    """取得TDX API存取權杖"""
    client_id = os.getenv('TDX_CLIENT_ID')
    client_secret = os.getenv('TDX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ 找不到TDX API憑證")
        return None
    
    # OAuth 2.0認證
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(auth_url, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    print("✅ 成功取得TDX存取權杖")
                    return token_data.get('access_token')
                else:
                    print(f"❌ 取得權杖失敗: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ 認證錯誤: {str(e)}")
        return None

async def test_metro_apis_with_auth():
    """使用認證測試各捷運系統的即時電子看板API"""
    
    print("🚇 使用TDX認證測試捷運即時電子看板API")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 取得認證Token
    access_token = await get_tdx_access_token()
    if not access_token:
        print("無法取得認證，停止測試")
        return
    
    # API網址
    apis = {
        "台北捷運 (TRTC)": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?$format=JSON",
        "高雄捷運 (KRTC)": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?$format=JSON", 
        "高雄輕軌 (KLRT)": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KLRT?$format=JSON"
    }
    
    # 設定headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # SSL設定
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for system_name, api_url in apis.items():
            print(f"📡 測試 {system_name}")
            print(f"URL: {api_url}")
            
            try:
                async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    print(f"HTTP 狀態碼: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if isinstance(data, list):
                            total_records = len(data)
                            print(f"✅ 成功取得資料，共 {total_records} 筆記錄")
                            
                            if total_records > 0:
                                # 分析資料結構
                                line_stats = {}
                                station_stats = set()
                                trains_with_estimate = 0
                                trains_with_liveboards = 0
                                
                                # 記錄詳細資料結構
                                sample_record = data[0]
                                print(f"   📄 資料欄位: {list(sample_record.keys())}")
                                
                                for record in data:
                                    line_id = record.get('LineID', 'Unknown')
                                    station_id = record.get('StationID', 'Unknown')
                                    station_name = record.get('StationName', {})
                                    
                                    # 統計路線
                                    if line_id not in line_stats:
                                        line_stats[line_id] = 0
                                    line_stats[line_id] += 1
                                    
                                    # 統計車站
                                    if isinstance(station_name, dict):
                                        name = station_name.get('Zh_tw', station_id)
                                    else:
                                        name = str(station_name)
                                    station_stats.add(f"{line_id}-{name}")
                                    
                                    # 檢查即時資料
                                    estimate_time = record.get('EstimateTime')
                                    live_boards = record.get('LiveBoards', [])
                                    
                                    if estimate_time is not None:
                                        trains_with_estimate += 1
                                    
                                    if live_boards:
                                        trains_with_liveboards += 1
                                
                                print(f"   📊 路線分布: {dict(line_stats)}")
                                print(f"   🚉 不重複車站: {len(station_stats)}")
                                print(f"   🚆 有EstimateTime: {trains_with_estimate} 筆")
                                print(f"   📋 有LiveBoards: {trains_with_liveboards} 筆")
                                
                                # 顯示資料範例
                                print(f"   📄 前3筆資料範例:")
                                for i, record in enumerate(data[:3]):
                                    station_name = record.get('StationName', {})
                                    if isinstance(station_name, dict):
                                        name = station_name.get('Zh_tw', '未知')
                                    else:
                                        name = str(station_name)
                                    
                                    # 檢查不同的目的地欄位
                                    dest_name = "未知"
                                    if 'DestinationStationName' in record:
                                        dest = record['DestinationStationName']
                                        if isinstance(dest, dict):
                                            dest_name = dest.get('Zh_tw', '未知')
                                        else:
                                            dest_name = str(dest)
                                    
                                    estimate_time = record.get('EstimateTime', 'N/A')
                                    live_boards = record.get('LiveBoards', [])
                                    
                                    print(f"      {i+1}. {record.get('LineID', 'N/A')}線 {name}")
                                    print(f"         → {dest_name} (預估:{estimate_time}秒)")
                                    print(f"         LiveBoards數量: {len(live_boards)}")
                                    
                                    if live_boards and len(live_boards) > 0:
                                        first_board = live_boards[0]
                                        print(f"         LiveBoard範例: {first_board}")
                                
                                # 檢查完整資料結構
                                print(f"\n   🔍 完整第一筆資料:")
                                print(json.dumps(data[0], indent=4, ensure_ascii=False))
                                
                        else:
                            print(f"❌ 資料格式異常: {type(data)}")
                            print(f"內容: {data}")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP 錯誤: {response.status}")
                        print(f"錯誤內容: {error_text[:500]}...")
                        
            except asyncio.TimeoutError:
                print("❌ 連線超時")
            except aiohttp.ClientError as e:
                print(f"❌ 連線錯誤: {str(e)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析錯誤: {str(e)}")
            except Exception as e:
                print(f"❌ 未知錯誤: {str(e)}")
            
            print("-" * 50)
            print()
    
    print("🎯 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_metro_apis_with_auth())
