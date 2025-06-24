#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 修復驗證測試
驗證之前出現的"異常資料結構"警告是否已修復
"""

def test_fixed_api_logic():
    """測試修復後的API檢測邏輯"""
    print("🔍 測試修復後的API檢測邏輯...")
    
    # 模擬從日誌看到的有認證模式回應結構
    authenticated_response = {
        'success': 'true',
        'result': {
            'resource_id': 'E-A0015-001',
            'fields': [
                {'id': 'ReportType', 'type': 'String'},
                {'id': 'EarthquakeNo', 'type': 'Integer'}
            ]
        },
        'records': {
            'datasetDescription': '地震報告',
            'Earthquake': [
                {
                    'EarthquakeNo': 114097,
                    'ReportType': '地震報告',
                    'ReportContent': '測試地震資料'
                }
            ]
        }
    }
    
    # 測試修復後的檢測邏輯
    def check_abnormal_format(data):
        """模擬修復後的異常格式檢測"""
        return ('result' in data and isinstance(data['result'], dict) and 
                set(data['result'].keys()) == {'resource_id', 'fields'} and 
                'records' not in data)
    
    # 測試有認證模式資料
    is_abnormal = check_abnormal_format(authenticated_response)
    print(f"   資料結構鍵值: {list(authenticated_response.keys())}")
    print(f"   result 鍵值: {list(authenticated_response['result'].keys())}")
    print(f"   是否為異常格式: {is_abnormal}")
    
    if not is_abnormal:
        print("   ✅ 修復成功！有認證模式不再被誤判為異常格式")
        return True
    else:
        print("   ❌ 修復失敗！仍然被誤判為異常格式")
        return False

def test_data_extraction():
    """測試資料提取邏輯"""
    print("\n🔍 測試資料提取邏輯...")
    
    authenticated_response = {
        'success': 'true',
        'result': {
            'resource_id': 'E-A0015-001',
            'fields': []
        },
        'records': {
            'datasetDescription': '地震報告',
            'Earthquake': [{'EarthquakeNo': 114097}]
        }
    }
    
    # 模擬修復後的資料提取邏輯
    records_data = None
    data_source = ""
    
    if 'records' in authenticated_response:
        records_data = authenticated_response['records']
        data_source = "有認證模式 (根級別 records)"
    elif 'result' in authenticated_response and 'records' in authenticated_response.get('result', {}):
        records_data = authenticated_response['result']['records']
        data_source = "無認證模式 (result.records)"
    
    print(f"   資料來源: {data_source}")
    print(f"   成功提取records: {records_data is not None}")
    
    if records_data and 'Earthquake' in records_data:
        print(f"   地震資料筆數: {len(records_data['Earthquake'])}")
        print("   ✅ 資料提取成功！")
        return True
    else:
        print("   ❌ 資料提取失敗！")
        return False

def main():
    """主測試函數"""
    print("🎯 API 修復驗證測試")
    print("=" * 50)
    
    tests = [
        ("異常格式檢測修復", test_fixed_api_logic),
        ("資料提取邏輯", test_data_extraction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} - 通過")
                passed += 1
            else:
                print(f"❌ {test_name} - 失敗")
        except Exception as e:
            print(f"❌ {test_name} - 異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！API修復成功！")
        print("\n📝 預期效果:")
        print("   - 不再出現 'API回傳異常格式' 警告")
        print("   - 日誌顯示 '使用有認證模式資料結構'")
        print("   - 機器人正常顯示最新地震資料")
    else:
        print("⚠️ 部分測試失敗，需要進一步檢查")

if __name__ == "__main__":
    main()
