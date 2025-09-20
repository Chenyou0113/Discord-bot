import asyncio
import aiohttp
import json

async def check_station_ids():
    """檢查台鐵所有車站資料來確認志學站的正確ID"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 查詢台鐵車站基本資料
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/Station?$format=JSON"
    
    async with aiohttp.ClientSession() as session:
        print("正在查詢台鐵車站基本資料...")
        
        try:
            async with session.get(url, headers=headers) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status == 200:
                    stations = await response.json()
                    print(f"總共取得 {len(stations)} 個車站資料")
                    
                    # 查找志學站
                    zhixue_stations = [station for station in stations 
                                     if '志學' in station.get('StationName', {}).get('Zh_tw', '')]
                    
                    print(f"\n找到 {len(zhixue_stations)} 個志學相關車站:")
                    for station in zhixue_stations:
                        print(f"車站名稱: {station.get('StationName', {}).get('Zh_tw')}")
                        print(f"車站ID: {station.get('StationID')}")
                        print(f"車站地址: {station.get('StationAddress', '')}")
                        print(f"經緯度: {station.get('StationPosition', {})}")
                        print("-" * 50)
                    
                    # 查找所有花蓮縣的車站
                    hualien_stations = [station for station in stations 
                                      if '花蓮' in station.get('StationAddress', '')]
                    
                    print(f"\n花蓮縣相關車站 ({len(hualien_stations)} 個):")
                    for station in hualien_stations:
                        station_name = station.get('StationName', {}).get('Zh_tw', 'N/A')
                        station_id = station.get('StationID', 'N/A')
                        print(f"  {station_name} (ID: {station_id})")
                        
                else:
                    print(f"API 請求失敗，狀態碼: {response.status}")
                    
        except Exception as e:
            print(f"請求時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_station_ids())
