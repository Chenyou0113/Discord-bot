#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水利防災影像 API
API 端點: https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_water_disaster_image_api():
    """測試水利防災影像 API"""
    print("📸 測試水利防災影像 API...")
    print("=" * 50)
    
    # 設定 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
            print(f"📡 請求 URL: {url}")
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    # 處理 UTF-8 BOM 問題
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    data = json.loads(text)
                    
                    print(f"✅ 成功獲取資料")
                    print(f"📈 資料類型: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"📈 資料筆數: {len(data)}")
                        if data:
                            print("\n🔍 第一筆資料結構分析:")
                            first_item = data[0]
                            print(f"{'欄位名稱':<40} {'值':<30} {'類型'}")
                            print("-" * 90)
                            
                            for key, value in first_item.items():
                                value_str = str(value)[:30] if value is not None else "None"
                                print(f"{key:<40} {value_str:<30} {type(value).__name__}")
                    
                    elif isinstance(data, dict):
                        print(f"📋 字典鍵值: {list(data.keys())}")
                        
                        # 檢查是否有嵌套的資料結構
                        for key, value in data.items():
                            print(f"🔑 {key}: {type(value)}")
                            if isinstance(value, list):
                                print(f"   └── 列表長度: {len(value)}")
                                if len(value) > 0:
                                    print(f"   └── 第一個元素類型: {type(value[0])}")
                                    if isinstance(value[0], dict):
                                        print(f"   └── 第一個元素鍵值: {list(value[0].keys())}")
                                        
                                        # 顯示第一筆詳細資料
                                        print("\n🔍 第一筆影像資料:")
                                        first_item = value[0]
                                        for k, v in first_item.items():
                                            print(f"  {k}: {v}")
                                        break
                    
                    # 儲存分析結果
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"water_disaster_images_{timestamp}.json"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        if len(str(data)) > 100000:  # 如果資料太大，只儲存前5筆
                            if isinstance(data, list):
                                json.dump(data[:5], f, ensure_ascii=False, indent=2)
                            elif isinstance(data, dict):
                                sample_data = {}
                                for k, v in data.items():
                                    if isinstance(v, list):
                                        sample_data[k] = v[:5]
                                    else:
                                        sample_data[k] = v
                                json.dump(sample_data, f, ensure_ascii=False, indent=2)
                        else:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n💾 分析結果已儲存至: {filename}")
                    
                    return True
                    
                else:
                    print(f"❌ API 請求失敗: {response.status}")
                    error_text = await response.text()
                    print(f"錯誤內容: {error_text[:200]}...")
                    return False
                    
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False
    
    finally:
        await connector.close()

if __name__ == "__main__":
    success = asyncio.run(test_water_disaster_image_api())
    
    if success:
        print("\n🎯 下一步:")
        print("  ✅ 水利防災影像 API 分析完成")
        print("  📝 準備開發 Discord 指令")
    else:
        print("  ❌ API 分析失敗，需要檢查網路或 API 狀態")
