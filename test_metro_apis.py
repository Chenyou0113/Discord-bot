"""
測試捷運即時電子看板 API
"""
import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_metro_apis():
    """測試各捷運系統的即時電子看板 API"""
    
    # API 網址
    apis = {
        "台北捷運 (TRTC)": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?$format=JSON",
        "高雄捷運 (KRTC)": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?$format=JSON", 
        "高雄輕軌 (KLRT)": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KLRT?$format=JSON"  # 修正為 KLRT
    }
    
    # 創建 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # 設定連接器
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        ttl_dns_cache=300,
        use_dns_cache=True,
        limit=100,
        limit_per_host=20
    )
    
    print("🚇 測試捷運即時電子看板 API")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for system_name, api_url in apis.items():
            print(f"📡 測試 {system_name}")
            print(f"URL: {api_url}")
            
            try:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    print(f"HTTP 狀態碼: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # 分析資料結構
                        if isinstance(data, list):
                            total_records = len(data)
                            print(f"✅ 成功取得資料，共 {total_records} 筆記錄")
                            
                            # 分析路線分布
                            if total_records > 0:
                                line_stats = {}
                                station_stats = {}
                                trains_with_data = 0
                                
                                for record in data:
                                    line_id = record.get('LineID', 'Unknown')
                                    station_id = record.get('StationID', 'Unknown')
                                    station_name = record.get('StationName', {})
                                    
                                    # 統計路線
                                    if line_id not in line_stats:
                                        line_stats[line_id] = 0
                                    line_stats[line_id] += 1
                                    
                                    # 統計車站
                                    if station_id not in station_stats:
                                        if isinstance(station_name, dict):
                                            name = station_name.get('Zh_tw', station_id)
                                        else:
                                            name = str(station_name)
                                        station_stats[station_id] = name
                                    
                                    # 檢查是否有列車資料
                                    if record.get('EstimateTime') is not None:
                                        trains_with_data += 1
                                
                                print(f"   📊 路線分布: {dict(line_stats)}")
                                print(f"   🚉 車站數量: {len(station_stats)}")
                                print(f"   🚆 有列車資料: {trains_with_data} 筆")
                                
                                # 顯示前3筆資料範例
                                print(f"   📄 資料範例 (前3筆):")
                                for i, record in enumerate(data[:3]):
                                    station_name = record.get('StationName', {})
                                    if isinstance(station_name, dict):
                                        name = station_name.get('Zh_tw', '未知')
                                    else:
                                        name = str(station_name)
                                    
                                    dest_name = record.get('DestinationStationName', {})
                                    if isinstance(dest_name, dict):
                                        dest = dest_name.get('Zh_tw', '未知')
                                    else:
                                        dest = str(dest_name)
                                    
                                    estimate_time = record.get('EstimateTime', 'N/A')
                                    
                                    print(f"      {i+1}. {record.get('LineID', 'N/A')}線 {name} → {dest} ({estimate_time}秒)")
                            
                        else:
                            print(f"❌ 資料格式異常: {type(data)}")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP 錯誤: {response.status}")
                        print(f"錯誤內容: {error_text[:200]}...")
                        
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

async def test_specific_station_data():
    """測試特定車站的資料結構"""
    print("\n🔍 詳細資料結構分析")
    print("=" * 40)
    
    # 創建 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # 測試台北捷運
        url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?$format=JSON"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        print("📄 台北捷運資料欄位結構:")
                        sample = data[0]
                        for key, value in sample.items():
                            print(f"   {key}: {type(value)} = {value}")
                        print()
        except Exception as e:
            print(f"無法取得台北捷運資料: {e}")

if __name__ == "__main__":
    asyncio.run(test_metro_apis())
    asyncio.run(test_specific_station_data())
