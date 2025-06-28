#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雷達圖 API 測試腳本
測試中央氣象署雷達圖 API 的連線和資料格式
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_radar_api():
    """測試雷達圖 API"""
    
    # API 配置
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-003"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    print("=" * 60)
    print("雷達圖 API 測試")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"參數: {params}")
    print("-" * 60)
    
    try:
        import ssl
        # 創建不驗證 SSL 的上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("🔍 正在連接雷達圖 API...")
            
            async with session.get(api_url, params=params) as response:
                print(f"📊 HTTP 狀態碼: {response.status}")
                
                if response.status == 200:
                    print("✅ API 連線成功")
                    
                    # 獲取回應內容
                    response_text = await response.text()
                    
                    try:
                        data = json.loads(response_text)
                        
                        print(f"\n📋 回應資料結構:")
                        print(f"資料類型: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"主要鍵值: {list(data.keys())}")
                            
                            # 檢查雷達圖資料結構
                            for key, value in data.items():
                                print(f"\n🔍 {key}:")
                                if isinstance(value, dict):
                                    print(f"  類型: dict, 鍵值: {list(value.keys())}")
                                    # 深入檢查重要欄位
                                    if key == 'cwaopendata':
                                        cwa_data = value
                                        if 'resources' in cwa_data:
                                            resources = cwa_data['resources']
                                            print(f"  resources 類型: {type(resources)}")
                                            if isinstance(resources, dict):
                                                print(f"  resources 鍵值: {list(resources.keys())}")
                                                if 'resource' in resources:
                                                    resource_list = resources['resource']
                                                    print(f"  resource 清單長度: {len(resource_list) if isinstance(resource_list, list) else 'Not a list'}")
                                                    if isinstance(resource_list, list) and resource_list:
                                                        first_resource = resource_list[0]
                                                        print(f"  第一個 resource 欄位: {list(first_resource.keys()) if isinstance(first_resource, dict) else 'Not a dict'}")
                                elif isinstance(value, list):
                                    print(f"  類型: list, 長度: {len(value)}")
                                    if value and isinstance(value[0], dict):
                                        print(f"  第一個元素欄位: {list(value[0].keys())}")
                                else:
                                    print(f"  值: {value}")
                            
                            # 特別檢查圖片資源
                            if 'cwaopendata' in data:
                                cwa_data = data['cwaopendata']
                                if 'resources' in cwa_data and 'resource' in cwa_data['resources']:
                                    resources = cwa_data['resources']['resource']
                                    print(f"\n🖼️ 雷達圖資源分析:")
                                    for i, resource in enumerate(resources[:3]):  # 顯示前3個
                                        if isinstance(resource, dict):
                                            resource_id = resource.get('resourceid', 'N/A')
                                            description = resource.get('description', 'N/A')
                                            format_type = resource.get('format', 'N/A')
                                            url = resource.get('url', 'N/A')
                                            
                                            print(f"  資源 {i+1}:")
                                            print(f"    ID: {resource_id}")
                                            print(f"    描述: {description}")
                                            print(f"    格式: {format_type}")
                                            print(f"    URL: {url}")
                        
                        elif isinstance(data, list):
                            print(f"陣列長度: {len(data)}")
                            if data and isinstance(data[0], dict):
                                print(f"第一個元素欄位: {list(data[0].keys())}")
                        
                        # 保存完整回應到文件
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"radar_api_test_{timestamp}.json"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        print(f"\n💾 完整 API 回應已保存到: {filename}")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON 解析失敗: {e}")
                        print("原始回應內容預覽:")
                        print(response_text[:500])
                
                else:
                    print(f"❌ API 連線失敗: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"錯誤回應: {error_text[:200]}")
    
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print("測試中央氣象署雷達圖 API")
    print("API 來源: 中央氣象署")
    print("資料集: 台灣附近雷達圖整合無地形")
    
    try:
        asyncio.run(test_radar_api())
        print("\n" + "=" * 60)
        print("✅ API 測試完成")
        print("請檢查生成的 JSON 文件以了解完整的資料結構")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
