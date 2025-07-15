#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水利防災監視器 API
"""

import asyncio
import aiohttp
import ssl
import xml.etree.ElementTree as ET

async def test_water_cameras_api():
    """測試水利防災監視器 API"""
    print("=" * 60)
    print("測試水利防災監視器 API")
    print("=" * 60)
    
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"API URL: {api_url}")
            print("📡 正在獲取監視器資料...")
            
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                content = await response.text()
                print(f"回應長度: {len(content)} 字元")
                print(f"回應前200字元: {content[:200]}")
                
                # 處理 BOM 編碼問題
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                # 嘗試解析 JSON（而不是 XML）
                try:
                    import json
                    data = json.loads(content)
                    print(f"✅ JSON 解析成功")
                    print(f"資料類型: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"JSON 鍵: {list(data.keys())}")
                        
                        # 查找可能的監視器資料
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"\n找到列表 '{key}' 包含 {len(value)} 個項目")
                                if value:
                                    print(f"第一個項目的鍵: {list(value[0].keys()) if isinstance(value[0], dict) else '非字典'}")
                                    if isinstance(value[0], dict):
                                        print(f"第一個項目內容:")
                                        for k, v in list(value[0].items())[:5]:  # 只顯示前5個欄位
                                            print(f"  {k}: {v}")
                    elif isinstance(data, list):
                        print(f"資料是列表，包含 {len(data)} 個項目")
                        if data and isinstance(data[0], dict):
                            print(f"第一個項目的鍵: {list(data[0].keys())}")
                
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    # 如果不是 JSON，嘗試 XML
                    try:
                        root = ET.fromstring(content)
                        print(f"✅ XML 解析成功")
                        print(f"根元素: {root.tag}")
                        
                        # 查找 item 元素
                        items = root.findall('.//item')
                        print(f"找到 {len(items)} 個 item 元素")
                        
                        if items:
                            print(f"\n前3個 item 的結構:")
                            for i, item in enumerate(items[:3], 1):
                                print(f"\nItem {i}:")
                                for child in item:
                                    print(f"  {child.tag}: {child.text[:100] if child.text else 'None'}")
                        
                    except ET.ParseError as e:
                        print(f"❌ XML 解析也失敗: {e}")
                        print(f"內容既不是有效的 JSON 也不是有效的 XML")
                
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_water_cameras_api())
