#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空氣品質 API 測試腳本
測試環保署空氣品質監測 API 的連線和資料格式
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_air_quality_api():
    """測試空氣品質 API"""
    
    # API 配置
    api_url = "https://data.epa.gov.tw/api/v2/aqx_p_432"
    api_key = "94650864-6a80-4c58-83ce-fd13e7ef0504"
    
    params = {
        "api_key": api_key,
        "limit": 10,  # 先測試少量資料
        "sort": "ImportDate desc",
        "format": "JSON"
    }
    
    print("=" * 60)
    print("空氣品質 API 測試")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"參數: {params}")
    print("-" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🔍 正在連接 API...")
            
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
                              # 檢查是否有 records 欄位
                            if 'records' in data:
                                records = data['records']
                                print(f"記錄數量: {len(records)}")
                                
                                if records:
                                    print(f"\n📍 第一筆記錄的欄位:")
                                    first_record = records[0]
                                    for key, value in first_record.items():
                                        print(f"  {key}: {value}")
                                    
                                    print(f"\n🏆 前 3 筆記錄範例:")
                                    for i, record in enumerate(records[:3]):
                                        site_name = record.get('sitename', record.get('SiteName', 'N/A'))
                                        county = record.get('county', record.get('County', 'N/A'))
                                        aqi = record.get('aqi', record.get('AQI', 'N/A'))
                                        status = record.get('status', record.get('Status', 'N/A'))
                                        import_date = record.get('importdate', record.get('ImportDate', 'N/A'))
                                        
                                        print(f"  {i+1}. {site_name} ({county}) - AQI: {aqi}, 狀態: {status}")
                                        print(f"     更新時間: {import_date}")
                            
                            else:
                                print("⚠️  回應中沒有 'records' 欄位")
                                print("回應內容預覽:")
                                print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
                        
                        elif isinstance(data, list):
                            print(f"陣列長度: {len(data)}")
                            if data:
                                print(f"第一個元素的欄位: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")
                        
                        # 保存完整回應到文件
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"air_quality_api_test_{timestamp}.json"
                        
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
    print("測試環保署空氣品質監測 API")
    print("API 來源: 行政院環境保護署")
    print("資料集: 空氣品質監測網")
    
    try:
        asyncio.run(test_air_quality_api())
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
