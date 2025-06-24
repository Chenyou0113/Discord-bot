#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 邏輯修復驗證腳本
測試修復後的資料結構判斷邏輯
"""

import json
import os

def test_api_structure_logic():
    """測試修復後的 API 資料結構判斷邏輯"""
    
    print("🧪 測試 API 資料結構判斷邏輯修復")
    print("=" * 50)
      # 模擬有認證模式的回應結構 (根據實際 API 回應)
    auth_response = {
        "success": "true",
        "result": {
            "resource_id": "E-A0015-001",
            "fields": [
                {"id": "EarthquakeNo", "type": "Integer"},
                {"id": "ReportType", "type": "String"}
            ]
        },
        "records": {
            "datasetDescription": "地震報告",
            "Earthquake": [
                {
                    "EarthquakeNo": 114097,
                    "ReportType": "地震報告",
                    "ReportContent": "測試地震資料 (有認證模式)"
                }
            ]
        }
    }
    
    # 模擬無認證模式的回應結構
    no_auth_response = {
        "success": "true",
        "result": {
            "resource_id": "E-A0015-001",
            "fields": [
                {"id": "EarthquakeNo", "type": "Integer"},
                {"id": "ReportType", "type": "String"}
            ],
            "records": {
                "Earthquake": [
                    {
                        "EarthquakeNo": 114097,
                        "ReportType": "地震報告",
                        "ReportContent": "測試地震資料"
                    }
                ]
            }
        }
    }
    
    # 模擬異常回應結構（只有欄位定義）
    abnormal_response = {
        "success": "true",
        "result": {
            "resource_id": "E-A0015-001",
            "fields": [
                {"id": "EarthquakeNo", "type": "Integer"},
                {"id": "ReportType", "type": "String"}
            ]
        }
    }
    
    def check_response_structure(data, mode_name):
        """檢查回應結構的邏輯 (模擬修復後的邏輯)"""
        print(f"\n🔍 測試 {mode_name}")
        print("-" * 30)
        
        if 'success' in data and (data['success'] == 'true' or data['success'] is True):
            # 檢查是否為API異常格式（只有欄位定義，無實際資料）
            # 修復：有認證模式的 result 也會包含 records
            if ('result' in data and isinstance(data['result'], dict) and 
                set(data['result'].keys()) == {'resource_id', 'fields'} and 
                'records' not in data):
                print("❌ API回傳異常資料結構（只有欄位定義）")
                return False
            
            # 檢查是否有實際的地震資料 (支援兩種資料結構)
            records_data = None
            data_source = ""
            
            if 'records' in data:
                # 有認證模式：records 在根級別
                records_data = data['records']
                data_source = "根級別 records"
                print(f"✅ 使用有認證模式資料結構 ({data_source})")
            elif 'result' in data and 'records' in data.get('result', {}):
                # 無認證模式：records 在 result 內
                records_data = data['result']['records']
                data_source = "result.records"
                print(f"✅ 使用無認證模式資料結構 ({data_source})")
            
            if (records_data and isinstance(records_data, dict) and
                'Earthquake' in records_data and records_data['Earthquake']):
                
                print(f"✅ 成功獲取地震資料")
                print(f"   地震數量: {len(records_data['Earthquake'])}")
                print(f"   第一筆地震編號: {records_data['Earthquake'][0].get('EarthquakeNo', 'N/A')}")
                return True
            else:
                print("❌ 資料結構不完整")
                print(f"   records_data: {records_data}")
                return False
        else:
            print(f"❌ API 請求不成功: {data.get('success', 'unknown')}")
            return False
    
    # 測試三種情況
    results = []
    results.append(check_response_structure(auth_response, "有認證模式回應"))
    results.append(check_response_structure(no_auth_response, "無認證模式回應"))
    results.append(check_response_structure(abnormal_response, "異常回應結構"))
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結")
    print("=" * 50)
    
    test_cases = [
        ("有認證模式", results[0], True),
        ("無認證模式", results[1], True),
        ("異常資料結構", results[2], False)
    ]
    
    all_passed = True
    for case_name, actual, expected in test_cases:
        status = "✅ 通過" if actual == expected else "❌ 失敗"
        print(f"{case_name}: {status} (預期: {expected}, 實際: {actual})")
        if actual != expected:
            all_passed = False
    
    print(f"\n🎯 總體結果: {'✅ 所有測試通過' if all_passed else '❌ 部分測試失敗'}")
    
    return all_passed

if __name__ == "__main__":
    success = test_api_structure_logic()
    print(f"\n{'🎉 API 邏輯修復驗證成功！' if success else '❌ API 邏輯修復驗證失敗！'}")
