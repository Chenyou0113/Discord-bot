import asyncio
import aiohttp
import json

async def get_all_tra_stations():
    """獲取所有台鐵車站的正確資料"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 查詢台鐵車站基本資料
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/Station?$format=JSON"
    
    async with aiohttp.ClientSession() as session:
        print("正在獲取台鐵所有車站資料...")
        
        try:
            async with session.get(url, headers=headers) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status == 200:
                    stations = await response.json()
                    print(f"總共取得 {len(stations)} 個車站資料")
                    
                    # 按縣市分類車站
                    stations_by_county = {}
                    
                    for station in stations:
                        station_name = station.get('StationName', {}).get('Zh_tw', '')
                        station_id = station.get('StationID', '')
                        station_address = station.get('StationAddress', '')
                        
                        # 解析縣市
                        county = None
                        if station_address:
                            for county_name in ['基隆市', '臺北市', '新北市', '桃園市', '新竹市', '新竹縣', 
                                              '苗栗縣', '臺中市', '彰化縣', '南投縣', '雲林縣', '嘉義市', 
                                              '嘉義縣', '臺南市', '高雄市', '屏東縣', '臺東縣', '花蓮縣', 
                                              '宜蘭縣', '連江縣', '金門縣', '澎湖縣']:
                                if county_name in station_address:
                                    county = county_name
                                    break
                        
                        if not county:
                            # 如果無法從地址解析，嘗試從車站ID範圍推測
                            station_id_int = int(station_id) if station_id.isdigit() else 0
                            if 0 <= station_id_int <= 999:
                                county = "基隆市/臺北市/新北市"
                            elif 1000 <= station_id_int <= 1999:
                                county = "桃園市/新竹市/新竹縣"
                            elif 2000 <= station_id_int <= 2999:
                                county = "苗栗縣/臺中市"
                            elif 3000 <= station_id_int <= 3999:
                                county = "彰化縣/南投縣/雲林縣"
                            elif 4000 <= station_id_int <= 4999:
                                county = "嘉義市/嘉義縣/臺南市/高雄市"
                            elif 5000 <= station_id_int <= 5999:
                                county = "屏東縣"
                            elif 6000 <= station_id_int <= 6999:
                                county = "臺東縣/花蓮縣"
                            elif 7000 <= station_id_int <= 7999:
                                county = "宜蘭縣"
                            else:
                                county = "其他"
                        
                        if county not in stations_by_county:
                            stations_by_county[county] = []
                        
                        stations_by_county[county].append({
                            'name': station_name,
                            'id': station_id,
                            'address': station_address
                        })
                    
                    # 輸出結果
                    print("\n===== 台鐵車站資料 (按縣市分類) =====")
                    for county, station_list in sorted(stations_by_county.items()):
                        print(f"\n{county} ({len(station_list)} 個車站):")
                        for station in sorted(station_list, key=lambda x: int(x['id']) if x['id'].isdigit() else 0):
                            print(f"  {station['name']} (ID: {station['id']})")
                    
                    # 生成Python程式碼格式
                    print("\n\n===== Python程式碼格式 =====")
                    print("TAIWAN_COUNTIES_STATIONS = {")
                    
                    # 重新整理為符合原程式碼的縣市分類
                    target_counties = {
                        "基隆市": [],
                        "臺北市": [],
                        "新北市": [],
                        "桃園市": [],
                        "新竹市": [],
                        "新竹縣": [],
                        "苗栗縣": [],
                        "臺中市": [],
                        "彰化縣": [],
                        "南投縣": [],
                        "雲林縣": [],
                        "嘉義市": [],
                        "嘉義縣": [],
                        "臺南市": [],
                        "高雄市": [],
                        "屏東縣": [],
                        "臺東縣": [],
                        "花蓮縣": [],
                        "宜蘭縣": []
                    }
                    
                    for station in stations:
                        station_name = station.get('StationName', {}).get('Zh_tw', '')
                        station_id = station.get('StationID', '')
                        station_address = station.get('StationAddress', '')
                        
                        # 精確匹配縣市
                        matched_county = None
                        for county_name in target_counties.keys():
                            if county_name in station_address:
                                matched_county = county_name
                                break
                        
                        if matched_county:
                            target_counties[matched_county].append({
                                'name': station_name,
                                'id': station_id
                            })
                    
                    for county, station_list in target_counties.items():
                        if station_list:  # 只輸出有車站的縣市
                            print(f'    "{county}": [')
                            for station in sorted(station_list, key=lambda x: int(x['id']) if x['id'].isdigit() else 0):
                                print(f'        {{"name": "{station["name"]}", "id": "{station["id"]}"}},')
                            print('    ],')
                    
                    print("}")
                    
                    return target_counties
                    
                else:
                    print(f"API 請求失敗，狀態碼: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"請求時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    result = asyncio.run(get_all_tra_stations())
    
    if result:
        # 保存結果到檔案
        with open('correct_tra_stations.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\n結果已保存到 correct_tra_stations.json")
