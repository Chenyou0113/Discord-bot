#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的降雨雷達 API 連線測試
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_single_rainfall_radar():
    """測試單一降雨雷達 API"""
    
    # 測試樹林站
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-001"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    print("測試新北樹林降雨雷達 API")
    print(f"URL: {api_url}")
    print("-" * 50)
    
    try:
        # 創建不驗證 SSL 的上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("🔍 正在連接 API...")
            
            async with session.get(api_url, params=params) as response:
                print(f"📊 HTTP 狀態碼: {response.status}")
                
                if response.status == 200:
                    print("✅ API 連線成功")
                    
                    # 獲取回應內容
                    data = await response.json()
                    
                    print(f"資料類型: {type(data)}")
                    
                    if isinstance(data, dict) and 'cwaopendata' in data:
                        cwa_data = data['cwaopendata']
                        dataset = cwa_data.get('dataset', {})
                        
                        # 檢查基本資訊
                        datetime_str = dataset.get('DateTime', 'N/A')
                        print(f"觀測時間: {datetime_str}")
                        
                        # 檢查資源
                        resource = dataset.get('resource', {})
                        if resource:
                            url = resource.get('ProductURL', '')
                            print(f"圖片URL: {url[:100]}..." if len(url) > 100 else f"圖片URL: {url}")
                            
                            if url:
                                print("✅ 成功獲取雷達圖片連結")
                            else:
                                print("⚠️ 未找到圖片連結")
                        
                        # 保存資料樣本
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"rainfall_radar_test_{timestamp}.json"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        print(f"💾 資料已保存到: {filename}")
                        return True
                    else:
                        print("❌ 資料結構不符合預期")
                        return False
                
                else:
                    print(f"❌ API 連線失敗: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"錯誤回應: {error_text[:200]}")
                    return False
    
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False

def main():
    """主函數"""
    try:
        success = asyncio.run(test_single_rainfall_radar())
        print("-" * 50)
        if success:
            print("✅ 降雨雷達 API 測試成功")
        else:
            print("❌ 降雨雷達 API 測試失敗")
        return success
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    main()
