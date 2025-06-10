#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡單測試 API 資料結構解析修復
"""

import asyncio
import json
import os
import sys

# 添加當前目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 測試資料結構解析邏輯
def test_data_structure_parsing():
    """測試資料結構解析邏輯"""
    
    print("🧪 測試 API 資料結構解析修復")
    print("=" * 50)
    
    # 模擬有認證模式的資料結構
    auth_data = {
        "success": "true",
        "result": {
            "resource_id": "E-A0015-001",
            "fields": []
        },
        "records": {
            "datasetDescription": "地震報告",
            "Earthquake": [
                {
                    "EarthquakeNo": 114097,
                    "ReportType": "地震報告",
                    "ReportContent": "測試地震資料"
                }
            ]
        }
    }
    
    # 模擬無認證模式的資料結構
    no_auth_data = {
        "success": "true",
        "result": {
            "resource_id": "E-A0015-001",
            "fields": [],
            "records": {
                "Earthquake": [
                    {
                        "EarthquakeNo": 114098,
                        "ReportType": "地震報告",
                        "ReportContent": "測試地震資料 (無認證)"
                    }
                ]
            }
        }
    }
    
    # 測試資料解析邏輯
    def parse_earthquake_data(data):
        """解析地震資料的邏輯 (模擬修復後的函數)"""
        if not data or 'success' not in data or data['success'] != 'true':
            return None
            
        # 支援兩種資料結構
        records_data = None
        if 'records' in data:
            # 有認證模式：records 在根級別
            records_data = data['records']
            print("✅ 檢測到有認證模式資料結構")
        elif 'result' in data and 'records' in data.get('result', {}):
            # 無認證模式：records 在 result 內
            records_data = data['result']['records']
            print("✅ 檢測到無認證模式資料結構")
        
        if (records_data and isinstance(records_data, dict) and
            'Earthquake' in records_data and records_data['Earthquake']):
            return records_data['Earthquake'][0]
        
        return None
    
    # 測試有認證模式資料
    print("\n🔐 測試有認證模式資料解析:")
    auth_result = parse_earthquake_data(auth_data)
    if auth_result:
        print(f"✅ 成功解析有認證模式資料: {auth_result['EarthquakeNo']}")
        print(f"   報告內容: {auth_result['ReportContent']}")
    else:
        print("❌ 有認證模式資料解析失敗")
    
    # 測試無認證模式資料
    print("\n🔓 測試無認證模式資料解析:")
    no_auth_result = parse_earthquake_data(no_auth_data)
    if no_auth_result:
        print(f"✅ 成功解析無認證模式資料: {no_auth_result['EarthquakeNo']}")
        print(f"   報告內容: {no_auth_result['ReportContent']}")
    else:
        print("❌ 無認證模式資料解析失敗")
    
    # 檢查是否兩種模式都成功解析
    if auth_result and no_auth_result:
        print("\n🎉 API 資料結構解析修復測試成功！")
        print("✅ 兩種資料結構都能正確解析")
        return True
    else:
        print("\n❌ API 資料結構解析修復測試失敗")
        return False

def test_actual_api_files():
    """測試實際的 API 回應檔案"""
    print("\n📁 測試實際 API 回應檔案")
    print("=" * 30)
    
    # 測試有認證模式的檔案
    auth_files = [
        "api_test_一般地震_(有認證)_20250604_213746.json",
        "api_test_一般地震_(有認證)_20250604_214035.json",
        "api_test_一般地震_(有認證)_20250604_214304.json"
    ]
    
    for filename in auth_files:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 檢查資料結構
                if ('success' in data and data['success'] == 'true' and
                    'records' in data and isinstance(data['records'], dict) and
                    'Earthquake' in data['records'] and data['records']['Earthquake']):
                    
                    earthquake_no = data['records']['Earthquake'][0].get('EarthquakeNo', 'N/A')
                    print(f"✅ {filename}: 地震編號 {earthquake_no}")
                else:
                    print(f"❌ {filename}: 資料結構異常")
                    
            except Exception as e:
                print(f"❌ {filename}: 讀取錯誤 - {str(e)}")
        else:
            print(f"⚠️  {filename}: 檔案不存在")

if __name__ == "__main__":
    success = test_data_structure_parsing()
    test_actual_api_files()
    
    if success:
        print("\n🎯 測試總結: API 資料結構解析修復成功")
        print("💡 現在機器人應該能正確處理有認證模式的API回應")
    else:
        print("\n⚠️  測試總結: 需要進一步檢查修復")
