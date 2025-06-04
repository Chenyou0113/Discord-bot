#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試無認證 CWA API
"""

import requests
import json
from datetime import datetime

def test_no_auth_api():
    """測試無認證的 CWA API"""
    print("🧪 測試無認證的中央氣象署 API")
    print("=" * 50)
    
    # API 設定
    base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    
    # 測試案例
    test_cases = [
        {
            "name": "一般地震 (無認證)",
            "endpoint": "E-A0015-001",
            "params": {
                "limit": 1,
                "format": "JSON"
            }
        },
        {
            "name": "小區域地震 (無認證)",
            "endpoint": "E-A0016-001", 
            "params": {
                "limit": 1,
                "format": "JSON"
            }
        }
    ]
    
    results = []
    
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
                                print("⚠️ 無認證也只回傳欄位定義")
                                results.append(False)
                            elif 'records' in result:
                                records = result['records']
                                print(f"📊 records 類型: {type(records)}")
                                if isinstance(records, dict) and 'Earthquake' in records:
                                    earthquakes = records['Earthquake']
                                    print(f"🌍 地震資料數量: {len(earthquakes) if isinstance(earthquakes, list) else 'N/A'}")
                                    if isinstance(earthquakes, list) and len(earthquakes) > 0:
                                        eq = earthquakes[0]
                                        if isinstance(eq, dict) and 'EarthquakeInfo' in eq:
                                            eq_info = eq['EarthquakeInfo']
                                            if 'OriginTime' in eq_info:
                                                print(f"⏰ 地震時間: {eq_info['OriginTime']}")
                                            if 'EarthquakeMagnitude' in eq_info:
                                                magnitude = eq_info['EarthquakeMagnitude']
                                                if 'MagnitudeValue' in magnitude:
                                                    print(f"📏 地震規模: {magnitude['MagnitudeValue']}")
                                        print("✅ 無認證 API 可獲取完整地震資料！")
                                        results.append(True)
                                    else:
                                        print("⚠️ 無地震資料")
                                        results.append(False)
                                else:
                                    print(f"⚠️ records 結構異常: {type(records)}")
                                    results.append(False)
                            else:
                                print("⚠️ 缺少 records 欄位")
                                results.append(False)
                    
                    # 儲存回應
                    filename = f"no_auth_test_{test_case['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"💾 回應已儲存至: {filename}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    results.append(False)
            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")
                print(f"📄 錯誤內容: {response.text[:200]}...")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 請求失敗: {e}")
            results.append(False)
        
        print()
    
    print("📋 測試結果總結:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失敗: {len(results) - sum(results)}/{len(results)}")
    
    if any(results):
        print("\n🎉 發現：無認證 API 可以獲取地震資料！")
        print("💡 建議修復方案：移除 API 金鑰認證，使用無認證模式")
        return True
    else:
        print("\n😞 無認證 API 也無法獲取完整資料")
        print("💡 建議方案：")
        print("  1. 聯絡 CWA 申請新的 API 金鑰")
        print("  2. 改善備用資料機制")
        print("  3. 考慮使用其他地震資料源")
        return False

if __name__ == "__main__":
    test_no_auth_api()
