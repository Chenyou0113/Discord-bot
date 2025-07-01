#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析新 API 的實際欄位結構
"""

import asyncio
import aiohttp
import json
import ssl

async def analyze_api_fields():
    """分析 API 欄位結構"""
    
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                content = await response.text()
                
                # 處理 BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                data = json.loads(content)
                
                if len(data) > 0:
                    first_item = data[0]
                    print("🔍 第一筆資料的所有欄位:")
                    print("=" * 50)
                    
                    for key, value in first_item.items():
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:100] + "..."
                        print(f"{key}: {value_str}")
                    
                    print(f"\n📊 欄位總數: {len(first_item)}")
                    
                    # 尋找可能的影像 URL 欄位
                    print("\n🔗 尋找影像 URL 相關欄位:")
                    url_fields = []
                    for key, value in first_item.items():
                        if 'url' in key.lower() or 'image' in key.lower() or 'link' in key.lower():
                            url_fields.append((key, value))
                            print(f"  {key}: {value}")
                    
                    if not url_fields:
                        print("  ❌ 未找到明顯的 URL 欄位")
                        print("  所有欄位:")
                        for key in first_item.keys():
                            print(f"    {key}")
                    
                    # 檢查前幾筆資料
                    print(f"\n📋 前 3 筆資料摘要:")
                    for i, item in enumerate(data[:3], 1):
                        print(f"\n第 {i} 筆:")
                        # 尋找名稱欄位
                        name_candidates = ['name', 'title', 'station', 'camera']
                        name = "未知"
                        for key, value in item.items():
                            if any(candidate in key.lower() for candidate in name_candidates):
                                name = value
                                break
                        
                        # 尋找位置欄位
                        location_candidates = ['county', 'city', 'location', 'address']
                        location = "未知"
                        for key, value in item.items():
                            if any(candidate in key.lower() for candidate in location_candidates):
                                location = value
                                break
                        
                        print(f"  名稱: {name}")
                        print(f"  位置: {location}")
                        
                        # 顯示所有欄位名稱
                        print(f"  所有欄位: {list(item.keys())}")
                
    except Exception as e:
        print(f"❌ 分析失敗: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_api_fields())
