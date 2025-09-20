import asyncio
import aiohttp
import json

async def test_zhixue_6240():
    """測試志學站正確ID 6240"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    urls = [
        "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard?$format=JSON&$filter=StationID eq '6240'",
        "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard?$format=JSON"
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*50}")
            print(f"測試 {i}: {url[:80]}{'...' if len(url) > 80 else ''}")
            print(f"{'='*50}")
            
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if isinstance(data, dict) and 'StationLiveBoards' in data:
                            all_trains = data['StationLiveBoards']
                            
                            if i == 1:  # 第一個測試：直接查詢志學站
                                print(f"志學站直接查詢結果: {len(all_trains)} 筆")
                                if all_trains:
                                    print("志學站電子看板資料:")
                                    for train in all_trains[:3]:  # 顯示前3筆
                                        print(json.dumps(train, ensure_ascii=False, indent=2))
                                        print("-" * 30)
                                else:
                                    print("志學站沒有電子看板資料")
                                    
                            else:  # 第二個測試：從全部資料中篩選志學站
                                zhixue_trains = [train for train in all_trains if train.get('StationID') == '6240']
                                print(f"從全部資料篩選志學站 (6240): {len(zhixue_trains)} 筆")
                                if zhixue_trains:
                                    print("志學站電子看板資料:")
                                    for train in zhixue_trains[:3]:  # 顯示前3筆
                                        print(json.dumps(train, ensure_ascii=False, indent=2))
                                        print("-" * 30)
                                else:
                                    print("在全部資料中也沒有找到志學站資料")
                        else:
                            print("資料結構不符預期")
                            
                    else:
                        print(f"HTTP錯誤: {response.status}")
                        
            except Exception as e:
                print(f"請求錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_zhixue_6240())
