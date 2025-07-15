#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水庫水情 API
"""

import asyncio
import aiohttp
import json
import ssl

async def test_reservoir_api():
    """測試水庫水情 API"""
    print("🔍 測試水庫水情 API...")
    
    # 設定 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=1602CA19-B224-4CC3-AA31-11B1B124530F"
            
            print(f"📡 請求 URL: {url}")
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"📊 狀態碼: {response.status}")
                
                if response.status == 200:
                    # 處理 UTF-8 BOM 問題
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]  # 移除 BOM
                    
                    data = json.loads(text)
                    print(f"✅ 成功獲取資料")
                    print(f"📈 資料類型: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"📋 字典鍵值: {list(data.keys())}")
                        
                        # 檢查是否有常見的資料欄位
                        for key, value in data.items():
                            print(f"🔑 {key}: {type(value)}")
                            if isinstance(value, list):
                                print(f"   └── 列表長度: {len(value)}")
                                if len(value) > 0:
                                    print(f"   └── 第一個元素類型: {type(value[0])}")
                                    if isinstance(value[0], dict):
                                        print(f"   └── 第一個元素鍵值: {list(value[0].keys())}")
                            elif isinstance(value, str):
                                print(f"   └── 字串內容: {value[:100]}...")
                    
                    elif isinstance(data, list):
                        print(f"📈 資料筆數: {len(data)}")
                        if len(data) > 0:
                            print("\n🎯 第一筆資料樣本:")
                            sample = data[0]
                            for key, value in sample.items():
                                print(f"  {key}: {value}")
                    
                    else:
                        print(f"📈 未知資料格式: {str(data)[:200]}...")
                    
                else:
                    print(f"❌ API 請求失敗: {response.status}")
                    error_text = await response.text()
                    print(f"錯誤內容: {error_text[:200]}...")
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
    
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_reservoir_api())
