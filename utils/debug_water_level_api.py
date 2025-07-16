#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水位 API 回應格式，診斷 'str' object has no attribute 'get' 錯誤
"""

import aiohttp
import asyncio
import ssl
import json

async def test_water_level_api():
    # 使用正確的河川水位 API
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f'狀態碼: {response.status}')
                
                # 處理 UTF-8 BOM 問題
                text = await response.text()
                if text.startswith('\ufeff'):
                    text = text[1:]
                
                try:
                    data = json.loads(text)
                    print(f'✅ JSON 解析成功')
                except json.JSONDecodeError as e:
                    print(f'❌ JSON 解析失敗: {e}')
                    return
                
                print(f'回應類型: {type(data)}')
                print(f'回應鍵: {list(data.keys()) if isinstance(data, dict) else "非字典"}')
                
                # 檢查資料結構
                print(f'records 類型: {type(data)}')
                if isinstance(data, dict):
                    print(f'data 鍵: {list(data.keys())}')
                    for key, value in data.items():
                        print(f'  {key}: {type(value)} (長度: {len(value) if isinstance(value, (list, dict, str)) else "N/A"})')
                        # 如果是列表，顯示第一個元素的結構
                        if isinstance(value, list) and value:
                            print(f'    第一個元素類型: {type(value[0])}')
                            if isinstance(value[0], dict):
                                print(f'    第一個元素鍵: {list(value[0].keys())}')
                elif isinstance(data, list):
                    print(f'data 列表長度: {len(data)}')
                    if data:
                        print(f'第一個元素類型: {type(data[0])}')
                        if isinstance(data[0], dict):
                            print(f'第一個元素鍵: {list(data[0].keys())}')
                else:
                    print(f'data 是字串或其他類型: {type(data)}')
                    print(f'data 內容 (前100字元): {str(data)[:100]}')
                        
                # 輸出完整 JSON 結構（前1000字元）
                print(f'\n完整回應結構 (前1500字元):\n{json.dumps(data, ensure_ascii=False, indent=2)[:1500]}')
                        
    except Exception as e:
        print(f'錯誤: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_water_level_api())
