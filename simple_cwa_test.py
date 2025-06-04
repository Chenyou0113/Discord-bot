#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的 CWA API 測試工具
"""

import requests
import json
from datetime import datetime

def test_cwa_api():
    """測試不同的 CWA API 端點"""
    print("🧪 簡化的中央氣象署 API 測試")
    print("=" * 50)
    
    # API 設定
    api_key = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    
    # 測試案例
    test_cases = [
        {
            "name": "一般地震 (有認證)",
            "endpoint": "E-A0015-001",
            "params": {
                "Authorization": api_key,
                "limit": 1,
                "format": "JSON"
            }
        },
        {
            "name": "小區域地震 (有認證)",
            "endpoint": "E-A0016-001", 
            "params": {
                "Authorization": api_key,
                "limit": 1,
                "format": "JSON"
            }
        },
        {
            "name": "一般地震 (無認證測試)",
            "endpoint": "E-A0015-001",
            "params": {
                "limit": 1,
                "format": "JSON"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 測試: {test_case['name']}")
        print("-" * 30)
        
        url = f"{base_url}/{test_case['endpoint']}"
        
        try:
            response = requests.get(url, params=test_case['params'], timeout=10)
            print(f"📊 HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON 解析成功")
                    print(f"📦 根層級鍵: {list(data.keys())}")
                    
                    if 'success' in data:
                        print(f"🎯 success: {data['success']}")
                    
                    if 'result' in data:
                        result = data['result']
                        print(f"📂 result 類型: {type(result)}")
                        
                        if isinstance(result, dict):
                            print(f"🔑 result 鍵: {list(result.keys())}")
                            
                            # 檢查是否為異常結構
                            if set(result.keys()) == {'resource_id', 'fields'}:
                                print("⚠️ 發現異常資料結構！只有 resource_id 和 fields")
                                print("📌 這正是造成警告的原因")
                                print(f"🆔 resource_id: {result.get('resource_id')}")
                                print(f"📋 fields 數量: {len(result.get('fields', []))}")
                            elif 'records' in result:
                                records = result['records']
                                print(f"📊 records 類型: {type(records)}")
                                if isinstance(records, dict) and 'Earthquake' in records:
                                    earthquakes = records['Earthquake']
                                    print(f"🌍 地震資料數量: {len(earthquakes) if isinstance(earthquakes, list) else 'N/A'}")
                    
                    # 儲存回應
                    filename = f"api_test_{test_case['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"💾 回應已儲存至: {filename}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    print(f"📄 原始回應: {response.text[:200]}...")
            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")
                print(f"📄 錯誤內容: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 請求失敗: {e}")
        
        print()
    
    print("🔧 建議解決方案:")
    print("1. 如果有認證版本失敗但無認證版本成功，表示 API 金鑰有問題")
    print("2. 如果所有版本都失敗，可能是網路或 API 服務問題")
    print("3. 如果回應只有 resource_id 和 fields，表示認證失敗")
    print("4. 可以嘗試申請新的 API 金鑰或聯絡 CWA 支援")

if __name__ == "__main__":
    test_cwa_api()
