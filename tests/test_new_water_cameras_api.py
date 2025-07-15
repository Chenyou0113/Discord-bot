#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的水利防災監控影像 JSON API
API URL: https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52
"""

import asyncio
import aiohttp
import json
import ssl

async def test_new_water_cameras_api():
    """測試新的 JSON API"""
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    print("🔍 測試新的水利防災監控影像 JSON API...")
    print(f"API URL: {api_url}")
    print("-" * 60)
    
    try:
        # 設定 SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"HTTP 狀態碼: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                content = await response.text()
                print(f"回應長度: {len(content)} 字元")
                
                if not content or len(content.strip()) == 0:
                    print("❌ API 回應為空")
                    return
                
                # 解析 JSON（處理 BOM）
                try:
                    # 移除可能的 BOM
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    data = json.loads(content)
                    print("✅ JSON 解析成功")
                    print(f"資料類型: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"資料筆數: {len(data)}")
                        if len(data) > 0:
                            print("\n📋 第一筆資料結構:")
                            first_item = data[0]
                            print(json.dumps(first_item, ensure_ascii=False, indent=2))
                            
                            print("\n🔑 所有可用欄位:")
                            for key in first_item.keys():
                                print(f"  - {key}: {type(first_item[key])}")
                                
                            print("\n📊 前 5 筆資料摘要:")
                            for i, item in enumerate(data[:5]):
                                title = item.get('Name', item.get('title', item.get('StationName', 'Unknown')))
                                location = item.get('County', item.get('Location', item.get('Address', 'Unknown')))
                                url = item.get('Url', item.get('ImageUrl', item.get('Link', 'No URL')))
                                print(f"  {i+1}. {title} - {location} - {url}")
                                
                    elif isinstance(data, dict):
                        print("資料為字典格式")
                        print("\n🔑 頂層欄位:")
                        for key, value in data.items():
                            print(f"  - {key}: {type(value)}")
                            if isinstance(value, list) and len(value) > 0:
                                print(f"    (列表長度: {len(value)})")
                        
                        # 如果有包含列表的欄位，顯示第一筆
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                print(f"\n📋 {key} 第一筆資料:")
                                print(json.dumps(value[0], ensure_ascii=False, indent=2))
                                break
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    print("前 500 字元內容:")
                    print(content[:500])
                    
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_new_water_cameras_api())
