#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大範圍雷達圖 API 測試腳本
測試中央氣象署大範圍雷達圖 API (O-A0058-001) 的連線和資料格式
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_large_radar_api():
    """測試大範圍雷達圖 API"""
    
    # API 配置
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-001"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    print("=" * 60)
    print("大範圍雷達圖 API 測試")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"資料集: O-A0058-001 (大範圍雷達圖)")
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
            print("🔍 正在連接大範圍雷達圖 API...")
            
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
                            if 'cwaopendata' in data:
                                cwa_data = data['cwaopendata']
                                print(f"\n🔍 cwaopendata 結構:")
                                print(f"  鍵值: {list(cwa_data.keys())}")
                                
                                # 檢查 dataset
                                if 'dataset' in cwa_data:
                                    dataset = cwa_data['dataset']
                                    print(f"\n📊 dataset 結構:")
                                    print(f"  鍵值: {list(dataset.keys())}")
                                    
                                    # 檢查 datasetInfo
                                    if 'datasetInfo' in dataset:
                                        dataset_info = dataset['datasetInfo']
                                        print(f"\n📝 datasetInfo:")
                                        print(f"  描述: {dataset_info.get('datasetDescription', 'N/A')}")
                                        
                                        # 檢查 parameterSet
                                        if 'parameterSet' in dataset_info:
                                            param_set = dataset_info['parameterSet']
                                            print(f"\n⚙️ parameterSet:")
                                            print(f"  經度範圍: {param_set.get('LongitudeRange', 'N/A')}")
                                            print(f"  緯度範圍: {param_set.get('LatitudeRange', 'N/A')}")
                                            print(f"  圖像尺寸: {param_set.get('ImageDimension', 'N/A')}")
                                            
                                            if 'parameter' in param_set:
                                                parameter = param_set['parameter']
                                                print(f"  參數名稱: {parameter.get('parameterName', 'N/A')}")
                                                print(f"  雷達名稱: {parameter.get('radarName', 'N/A')}")
                                    
                                    # 檢查 resource
                                    if 'resource' in dataset:
                                        resource = dataset['resource']
                                        print(f"\n🖼️ resource 資源:")
                                        print(f"  描述: {resource.get('resourceDesc', 'N/A')}")
                                        print(f"  MIME類型: {resource.get('mimeType', 'N/A')}")
                                        print(f"  圖片URL: {resource.get('ProductURL', 'N/A')}")
                                    
                                    # 檢查觀測時間
                                    if 'DateTime' in dataset:
                                        datetime_str = dataset['DateTime']
                                        print(f"\n⏰ 觀測時間: {datetime_str}")
                                
                                # 檢查基本資訊
                                print(f"\n📋 基本資訊:")
                                print(f"  識別碼: {cwa_data.get('identifier', 'N/A')}")
                                print(f"  發送者: {cwa_data.get('sender', 'N/A')}")
                                print(f"  發送時間: {cwa_data.get('sent', 'N/A')}")
                                print(f"  資料ID: {cwa_data.get('dataid', 'N/A')}")
                                print(f"  來源: {cwa_data.get('source', 'N/A')}")
                        
                        # 保存完整回應到文件
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"large_radar_api_test_{timestamp}.json"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        print(f"\n💾 完整 API 回應已保存到: {filename}")
                        
                        return data
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON 解析失敗: {e}")
                        print("原始回應內容預覽:")
                        print(response_text[:500])
                        return None
                
                else:
                    print(f"❌ API 連線失敗: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"錯誤回應: {error_text[:200]}")
                    return None
    
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

async def compare_apis():
    """比較兩個雷達圖 API 的差異"""
    print("\n" + "=" * 60)
    print("比較兩個雷達圖 API")
    print("=" * 60)
    
    print("\n1️⃣ 測試大範圍雷達圖 (O-A0058-001)...")
    large_data = await test_large_radar_api()
    
    print("\n" + "-" * 60)
    print("\n2️⃣ 測試原始雷達圖 (O-A0058-003)...")
    
    # 測試原始 API
    api_url_003 = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-003"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    try:
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url_003, params=params) as response:
                if response.status == 200:
                    original_data = await response.json()
                    print("✅ 原始雷達圖 API 連線成功")
                    
                    # 比較兩個 API 的資料
                    if large_data and original_data:
                        print("\n📊 API 比較結果:")
                        
                        # 比較覆蓋範圍
                        if 'cwaopendata' in large_data and 'cwaopendata' in original_data:
                            large_dataset = large_data['cwaopendata'].get('dataset', {})
                            original_dataset = original_data['cwaopendata'].get('dataset', {})
                            
                            large_param = large_dataset.get('datasetInfo', {}).get('parameterSet', {})
                            original_param = original_dataset.get('datasetInfo', {}).get('parameterSet', {})
                            
                            print(f"\n🗺️ 覆蓋範圍比較:")
                            print(f"  大範圍雷達圖:")
                            print(f"    經度: {large_param.get('LongitudeRange', 'N/A')}")
                            print(f"    緯度: {large_param.get('LatitudeRange', 'N/A')}")
                            print(f"    尺寸: {large_param.get('ImageDimension', 'N/A')}")
                            
                            print(f"  原始雷達圖:")
                            print(f"    經度: {original_param.get('LongitudeRange', 'N/A')}")
                            print(f"    緯度: {original_param.get('LatitudeRange', 'N/A')}")
                            print(f"    尺寸: {original_param.get('ImageDimension', 'N/A')}")
                            
                            # 比較雷達站
                            large_radar = large_param.get('parameter', {}).get('radarName', '')
                            original_radar = original_param.get('parameter', {}).get('radarName', '')
                            
                            print(f"\n📡 雷達站比較:")
                            print(f"  大範圍: {large_radar}")
                            print(f"  原始: {original_radar}")
                            
                            # 比較圖片 URL
                            large_url = large_dataset.get('resource', {}).get('ProductURL', '')
                            original_url = original_dataset.get('resource', {}).get('ProductURL', '')
                            
                            print(f"\n🖼️ 圖片 URL 比較:")
                            print(f"  大範圍: {large_url}")
                            print(f"  原始: {original_url}")
                
                else:
                    print(f"❌ 原始雷達圖 API 連線失敗: HTTP {response.status}")
    
    except Exception as e:
        print(f"❌ 比較過程發生錯誤: {e}")

def main():
    """主函數"""
    print("測試中央氣象署大範圍雷達圖 API")
    print("API 來源: 中央氣象署")
    print("資料集: O-A0058-001 vs O-A0058-003")
    
    try:
        asyncio.run(compare_apis())
        print("\n" + "=" * 60)
        print("✅ API 測試與比較完成")
        print("請檢查生成的 JSON 文件以了解完整的資料結構")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
