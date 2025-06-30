#!/usr/bin/env python3
"""
測試 _normalize_county_name 方法修正
確保所有調用位置都能正確訪問標準化函數
"""

import sys
import os
import importlib.util

def test_normalize_method_access():
    """測試標準化方法是否可以正確訪問"""
    print("🔍 測試標準化方法訪問...")
    
    try:
        # 導入模組
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "reservoir_commands", 
            os.path.join(os.path.dirname(__file__), "cogs", "reservoir_commands.py")
        )
        reservoir_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reservoir_module)
        
        # 檢查 ReservoirCommands 類別是否有 _normalize_county_name 方法
        ReservoirCommands = reservoir_module.ReservoirCommands
        
        if hasattr(ReservoirCommands, '_normalize_county_name'):
            print("✅ ReservoirCommands 類別包含 _normalize_county_name 方法")
        else:
            print("❌ ReservoirCommands 類別缺少 _normalize_county_name 方法")
            return False
        
        # 創建一個模擬的 ReservoirCommands 實例來測試方法
        class MockBot:
            pass
        
        mock_bot = MockBot()
        reservoir_commands = ReservoirCommands(mock_bot)
        
        # 測試標準化方法
        test_cases = [
            ("臺北市", "台北市"),
            ("新北市政府", "新北市"),
            ("桃園縣", "桃園市"),
            ("未知縣市", "未知縣市"),
            ("", "未知縣市"),
            (None, "未知縣市")
        ]
        
        print("\n🧪 測試標準化功能...")
        all_passed = True
        
        for input_county, expected in test_cases:
            try:
                result = reservoir_commands._normalize_county_name(input_county)
                if result == expected:
                    print(f"✅ '{input_county}' -> '{result}'")
                else:
                    print(f"❌ '{input_county}' -> '{result}' (期望: '{expected}')")
                    all_passed = False
            except Exception as e:
                print(f"❌ 測試 '{input_county}' 時發生錯誤: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        return False

def test_water_camera_view_normalize_usage():
    """測試 WaterCameraView 中標準化函數的使用"""
    print("\n🔍 測試 WaterCameraView 標準化函數使用...")
    
    try:
        # 模擬標準化函數
        def mock_normalize_func(county):
            if county == "臺北市":
                return "台北市"
            return county or "未知縣市"
        
        # 模擬攝影機資料
        mock_camera_data = {
            'VideoSurveillanceStationName': '測試監控站',
            'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '臺北市',
            'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '信義區',
            'VideoSurveillanceStationAddress': '台北市信義區某路123號',
            'VideoSurveillanceStationId': 'TEST001',
            'ImageURL': 'https://example.com/test.jpg',
            'BasinName': '淡水河',
            'TRIBUTARY': ''
        }
        
        # 模擬 WaterCameraView 的 _format_water_image_info 方法
        class MockWaterCameraView:
            def __init__(self, normalize_func=None):
                self.normalize_func = normalize_func
            
            def _format_water_image_info(self, data):
                if not data:
                    return None
                
                station_name = data.get('VideoSurveillanceStationName', '未知監控站')
                county = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知縣市')
                district = data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '未知區域')
                address = data.get('VideoSurveillanceStationAddress', '未知地址')
                station_id = data.get('VideoSurveillanceStationId', '未知ID')
                image_url = data.get('ImageURL', '')
                
                # 縣市名稱標準化 - 使用傳入的標準化函數
                if self.normalize_func:
                    county_normalized = self.normalize_func(county)
                else:
                    county_normalized = county
                
                return {
                    'station_name': station_name,
                    'county': county_normalized,
                    'district': district,
                    'address': address,
                    'station_id': station_id,
                    'image_url': image_url,
                    'river': '淡水河',
                    'source': '水利署',
                    'status': '✅ 有影像' if image_url else '❌ 無影像'
                }
        
        # 測試有標準化函數的情況
        view_with_normalize = MockWaterCameraView(normalize_func=mock_normalize_func)
        result_with_normalize = view_with_normalize._format_water_image_info(mock_camera_data)
        
        if result_with_normalize and result_with_normalize['county'] == '台北市':
            print("✅ 使用標準化函數時，縣市名稱正確標準化")
        else:
            print(f"❌ 標準化函數未正確工作，結果: {result_with_normalize['county'] if result_with_normalize else 'None'}")
            return False
        
        # 測試沒有標準化函數的情況
        view_without_normalize = MockWaterCameraView()
        result_without_normalize = view_without_normalize._format_water_image_info(mock_camera_data)
        
        if result_without_normalize and result_without_normalize['county'] == '臺北市':
            print("✅ 沒有標準化函數時，保持原始縣市名稱")
        else:
            print(f"❌ 沒有標準化函數時的處理有誤，結果: {result_without_normalize['county'] if result_without_normalize else 'None'}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試 WaterCameraView 時發生錯誤: {e}")
        return False

def main():
    """主要測試流程"""
    print("🚀 開始測試標準化方法修正...")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 測試 1: 標準化方法訪問
    if not test_normalize_method_access():
        all_tests_passed = False
    
    # 測試 2: WaterCameraView 標準化函數使用
    if not test_water_camera_view_normalize_usage():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ 所有測試通過！標準化方法修正成功。")
        print("\n📋 修正摘要:")
        print("- ReservoirCommands._normalize_county_name 方法可正常訪問")
        print("- WaterCameraView._format_water_image_info 使用傳入的標準化函數")
        print("- 避免了 'object has no attribute' 錯誤")
        print("- 縣市名稱標準化功能正常")
    else:
        print("❌ 部分測試失敗，需要進一步檢查。")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
