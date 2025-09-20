import asyncio
import aiohttp
import json
import sys
from datetime import datetime

async def test_tra_v3_api():
    """測試新的台鐵v3 API以了解資料結構"""
    
    try:
        # 測試不同的API端點
        test_urls = [
            "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard?$format=JSON&$filter=StationID eq '2560'",  # 志學站
            "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard?$format=JSON&$top=10",  # 取前10筆
            "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard?$format=JSON",  # 全部資料
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for i, url in enumerate(test_urls, 1):
                print(f"\n{'='*50}")
                print(f"測試 {i}: {url}")
                print(f"{'='*50}")
                
                try:
                    async with session.get(url, headers=headers) as response:
                        print(f"狀態碼: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            print(f"資料類型: {type(data)}")
                            
                            if isinstance(data, list):
                                print(f"列表長度: {len(data)}")
                                if data:
                                    print("第一筆資料:")
                                    print(json.dumps(data[0], ensure_ascii=False, indent=2))
                                    
                                    # 檢查是否有志學站的資料
                                    zhixue_data = [item for item in data if 
                                                 item.get('StationID') == '2560' or 
                                                 '志學' in str(item.get('StationName', {}))]
                                    print(f"志學站相關資料: {len(zhixue_data)} 筆")
                                    if zhixue_data:
                                        print("志學站資料:")
                                        print(json.dumps(zhixue_data[0], ensure_ascii=False, indent=2))
                                else:
                                    print("空列表")
                            elif isinstance(data, dict):
                                print("字典資料:")
                                data_str = json.dumps(data, ensure_ascii=False, indent=2)
                                print(data_str[:1000] + "..." if len(data_str) > 1000 else data_str)
                            else:
                                print(f"未預期的資料格式: {data}")
                        else:
                            print(f"錯誤狀態碼: {response.status}")
                            error_text = await response.text()
                            print(f"錯誤內容: {error_text}")
                            
                except Exception as e:
                    print(f"請求失敗: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                print("\n" + "="*50)
                
    except Exception as e:
        print(f"主函數錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test_tra_v3_api())
    except Exception as e:
        print(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
