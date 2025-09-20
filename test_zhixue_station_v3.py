import asyncio
import aiohttp
import json

async def test_zhixue_station():
    """專門測試志學站資料"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 測試全部資料以查找志學站
    url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard?$format=JSON"
    
    async with aiohttp.ClientSession() as session:
        print("正在查詢所有台鐵電子看板資料...")
        
        try:
            async with session.get(url, headers=headers) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, dict) and 'StationLiveBoards' in data:
                        all_trains = data['StationLiveBoards']
                        print(f"總共取得 {len(all_trains)} 筆電子看板資料")
                        
                        # 查找志學站相關資料 (ID: 2560)
                        zhixue_trains = [train for train in all_trains if train.get('StationID') == '2560']
                        print(f"志學站 (ID: 2560) 的資料: {len(zhixue_trains)} 筆")
                        
                        if zhixue_trains:
                            print("\n志學站電子看板資料:")
                            for train in zhixue_trains[:5]:  # 只顯示前5筆
                                print(json.dumps(train, ensure_ascii=False, indent=2))
                                print("-" * 50)
                        else:
                            print("志學站目前沒有電子看板資料")
                            
                            # 檢查其他東部車站是否有資料
                            east_stations = ['2550', '2560', '2570', '2580', '2590']  # 志學周邊車站
                            for station_id in east_stations:
                                station_trains = [train for train in all_trains if train.get('StationID') == station_id]
                                if station_trains:
                                    station_name = station_trains[0].get('StationName', {}).get('Zh_tw', station_id)
                                    print(f"車站 {station_name} ({station_id}): {len(station_trains)} 筆資料")
                        
                        # 統計所有有資料的車站
                        station_counts = {}
                        for train in all_trains:
                            station_id = train.get('StationID')
                            station_name = train.get('StationName', {}).get('Zh_tw', station_id)
                            if station_id:
                                if station_id not in station_counts:
                                    station_counts[station_id] = {'name': station_name, 'count': 0}
                                station_counts[station_id]['count'] += 1
                        
                        print(f"\n目前有電子看板資料的車站共 {len(station_counts)} 個:")
                        sorted_stations = sorted(station_counts.items(), key=lambda x: x[1]['count'], reverse=True)
                        for station_id, info in sorted_stations[:10]:  # 顯示前10個
                            print(f"  {info['name']} ({station_id}): {info['count']} 筆")
                        
                    else:
                        print("API 資料結構不符預期")
                        print(f"資料內容: {data}")
                        
                else:
                    print(f"API 請求失敗，狀態碼: {response.status}")
                    error_text = await response.text()
                    print(f"錯誤內容: {error_text}")
                    
        except Exception as e:
            print(f"請求時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_zhixue_station())
