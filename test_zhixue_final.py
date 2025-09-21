import asyncio
import aiohttp

async def test_tra_v3():
    station_id = '6240'  # 志學站
    url = f'https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/LiveBoard/Station/{station_id}'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f'志學站 API 測試成功！')
                    if isinstance(data, dict):
                        print(f'資料結構: {list(data.keys())}')
                        if 'StationLiveBoards' in data:
                            boards = data['StationLiveBoards']
                            print(f'找到 {len(boards)} 個班次')
                            if boards:
                                first_train = boards[0]
                                print(f'第一班車: {first_train.get("TrainNo", "N/A")} - {first_train.get("Direction", "N/A")}')
                    else:
                        print('資料格式: list')
                        if data:
                            print(f'第一筆資料: {data[0]}')
                else:
                    print(f'API 錯誤: HTTP {response.status}')
    except Exception as e:
        print(f'測試失敗: {e}')

asyncio.run(test_tra_v3())
