#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
降雨雷達 API 測試腳本
測試中央氣象署降雨雷達 API 的連線和資料格式
包含樹林、南屯、林園雷達站
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_rainfall_radar_api():
    """測試降雨雷達 API"""
    
    # 降雨雷達 API 配置
    radar_stations = {
        "樹林": {
            "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-001",
            "code": "O-A0084-001",
            "location": "新北樹林"
        },
        "南屯": {
            "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-002", 
            "code": "O-A0084-002",
            "location": "台中南屯"
        },
        "林園": {
            "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-003",
            "code": "O-A0084-003", 
            "location": "高雄林園"
        }
    }
    
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    print("=" * 80)
    print("降雨雷達 API 測試")
    print("=" * 80)
    print("測試雷達站: 樹林、南屯、林園")
    print("-" * 80)
    
    try:
        import ssl
        # 創建不驗證 SSL 的上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            results = {}
            
            for station_name, station_info in radar_stations.items():
                print(f"\n🔍 測試 {station_info['location']} 降雨雷達...")
                print(f"API URL: {station_info['api_url']}")
                print(f"資料集: {station_info['code']}")
                
                try:
                    async with session.get(station_info['api_url'], params=params) as response:
                        print(f"📊 HTTP 狀態碼: {response.status}")
                        
                        if response.status == 200:
                            print("✅ API 連線成功")
                            
                            # 獲取回應內容
                            response_text = await response.text()
                            
                            try:
                                data = json.loads(response_text)
                                results[station_name] = data
                                
                                print(f"✅ JSON 資料解析成功")
                                
                                # 分析資料結構
                                if isinstance(data, dict):
                                    print(f"📋 主要鍵值: {list(data.keys())}")
                                    
                                    # 檢查雷達圖資料結構
                                    if 'cwaopendata' in data:
                                        cwa_data = data['cwaopendata']
                                        print(f"🔍 cwaopendata 鍵值: {list(cwa_data.keys())}")
                                        
                                        # 檢查 dataset
                                        if 'dataset' in cwa_data:
                                            dataset = cwa_data['dataset']
                                            print(f"📊 dataset 鍵值: {list(dataset.keys())}")
                                            
                                            # 檢查資源資訊
                                            if 'resource' in dataset:
                                                resource = dataset['resource']
                                                print(f"🖼️ resource 資訊:")
                                                print(f"   描述: {resource.get('resourceDesc', 'N/A')}")
                                                print(f"   MIME類型: {resource.get('mimeType', 'N/A')}")
                                                print(f"   圖片URL: {resource.get('ProductURL', 'N/A')}")
                                            
                                            # 檢查觀測時間
                                            if 'DateTime' in dataset:
                                                datetime_str = dataset['DateTime']
                                                print(f"⏰ 觀測時間: {datetime_str}")
                                            
                                            # 檢查 datasetInfo
                                            if 'datasetInfo' in dataset:
                                                dataset_info = dataset['datasetInfo']
                                                print(f"📝 資料集描述: {dataset_info.get('datasetDescription', 'N/A')}")
                                                
                                                if 'parameterSet' in dataset_info:
                                                    param_set = dataset_info['parameterSet']
                                                    print(f"⚙️ 參數設定:")
                                                    print(f"   經度範圍: {param_set.get('LongitudeRange', 'N/A')}")
                                                    print(f"   緯度範圍: {param_set.get('LatitudeRange', 'N/A')}")
                                                    print(f"   圖像尺寸: {param_set.get('ImageDimension', 'N/A')}")
                                        
                                        # 檢查基本資訊
                                        print(f"📋 基本資訊:")
                                        print(f"   識別碼: {cwa_data.get('identifier', 'N/A')}")
                                        print(f"   發送時間: {cwa_data.get('sent', 'N/A')}")
                                        print(f"   資料ID: {cwa_data.get('dataid', 'N/A')}")
                                
                                # 保存個別雷達站回應
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"rainfall_radar_{station_name}_{timestamp}.json"
                                
                                with open(filename, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                                
                                print(f"💾 {station_info['location']} 資料已保存到: {filename}")
                                
                            except json.JSONDecodeError as e:
                                print(f"❌ JSON 解析失敗: {e}")
                                print("原始回應內容預覽:")
                                print(response_text[:300])
                                results[station_name] = None
                        
                        else:
                            print(f"❌ API 連線失敗: HTTP {response.status}")
                            error_text = await response.text()
                            print(f"錯誤回應: {error_text[:200]}")
                            results[station_name] = None
                
                except Exception as e:
                    print(f"❌ {station_info['location']} 測試發生錯誤: {e}")
                    results[station_name] = None
                
                print("-" * 60)
            
            # 總結測試結果
            print(f"\n📊 測試總結:")
            success_count = 0
            for station_name, result in results.items():
                status = "✅ 成功" if result else "❌ 失敗"
                station_info = radar_stations[station_name]
                print(f"   {station_info['location']} ({station_name}): {status}")
                if result:
                    success_count += 1
            
            print(f"\n成功率: {success_count}/{len(radar_stations)} ({success_count/len(radar_stations)*100:.1f}%)")
            
            return results
    
    except Exception as e:
        print(f"❌ 整體測試發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return {}

async def analyze_rainfall_radar_structure():
    """分析降雨雷達資料結構"""
    print("\n" + "=" * 80)
    print("降雨雷達資料結構分析")
    print("=" * 80)
    
    results = await test_rainfall_radar_api()
    
    if not results:
        print("❌ 無可用的測試結果進行分析")
        return
    
    # 分析成功的結果
    successful_results = {k: v for k, v in results.items() if v is not None}
    
    if not successful_results:
        print("❌ 沒有成功的 API 回應可供分析")
        return
    
    print(f"\n🔍 分析 {len(successful_results)} 個成功的雷達站資料...")
    
    # 比較不同雷達站的資料結構
    print("\n📊 雷達站比較:")
    print("-" * 60)
    
    for station_name, data in successful_results.items():
        if 'cwaopendata' in data:
            cwa_data = data['cwaopendata']
            dataset = cwa_data.get('dataset', {})
            dataset_info = dataset.get('datasetInfo', {})
            param_set = dataset_info.get('parameterSet', {})
            resource = dataset.get('resource', {})
            
            print(f"\n🏢 {station_name} 雷達站:")
            print(f"   資料集ID: {cwa_data.get('dataid', 'N/A')}")
            print(f"   描述: {resource.get('resourceDesc', 'N/A')}")
            print(f"   觀測時間: {dataset.get('DateTime', 'N/A')}")
            print(f"   經度範圍: {param_set.get('LongitudeRange', 'N/A')}")
            print(f"   緯度範圍: {param_set.get('LatitudeRange', 'N/A')}")
            print(f"   圖像尺寸: {param_set.get('ImageDimension', 'N/A')}")
            print(f"   圖片URL: {resource.get('ProductURL', 'N/A')}")
    
    # 檢查資料結構一致性
    print(f"\n🔧 資料結構一致性檢查:")
    
    first_data = list(successful_results.values())[0]
    if 'cwaopendata' in first_data:
        reference_structure = first_data['cwaopendata']['dataset'].keys()
        print(f"   參考結構鍵值: {list(reference_structure)}")
        
        all_consistent = True
        for station_name, data in successful_results.items():
            if 'cwaopendata' in data:
                current_structure = data['cwaopendata']['dataset'].keys()
                if set(current_structure) != set(reference_structure):
                    print(f"   ⚠️ {station_name} 結構不一致")
                    all_consistent = False
        
        if all_consistent:
            print("   ✅ 所有雷達站資料結構一致")
    
    return successful_results

def main():
    """主函數"""
    print("測試中央氣象署降雨雷達 API")
    print("API 來源: 中央氣象署")
    print("涵蓋雷達站: 新北樹林、台中南屯、高雄林園")
    
    try:
        results = asyncio.run(analyze_rainfall_radar_structure())
        
        print("\n" + "=" * 80)
        print("✅ 降雨雷達 API 測試完成")
        print("請檢查生成的 JSON 文件以了解完整的資料結構")
        
        if results:
            print(f"\n📁 生成的檔案:")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for station_name in results.keys():
                filename = f"rainfall_radar_{station_name}_{timestamp}.json"
                print(f"   {filename}")
        
        return bool(results)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
