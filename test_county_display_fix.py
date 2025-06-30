#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水利監視器縣市顯示修復
"""

import sys
import os

# 添加 cogs 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'cogs'))

# 模擬 Discord 相關模組
class MockBot:
    pass

class MockInteraction:
    pass

# 模擬 Discord 模組
class discord:
    class Embed:
        def __init__(self, **kwargs):
            self.title = kwargs.get('title', '')
            self.description = kwargs.get('description', '')
            self.color = kwargs.get('color', None)
            self.fields = []
        
        def add_field(self, **kwargs):
            self.fields.append(kwargs)
    
    class Color:
        @staticmethod
        def blue():
            return 'blue'
        @staticmethod  
        def red():
            return 'red'
    
    class ui:
        class View:
            pass
        class Button:
            pass

# 將模擬的 discord 模組加入 sys.modules
sys.modules['discord'] = discord
sys.modules['discord.ext'] = type(sys)('discord.ext')
sys.modules['discord.ext.commands'] = type(sys)('discord.ext.commands')

# 模擬其他需要的模組
class commands:
    class Cog:
        pass

class app_commands:
    @staticmethod
    def command(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def describe(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    class Choice:
        def __init__(self, name, value):
            self.name = name
            self.value = value

sys.modules['discord.ext.commands'].Cog = commands.Cog
sys.modules['discord'].app_commands = app_commands

try:
    from reservoir_commands import ReservoirCommands
    
    def test_water_camera_county_display():
        """測試水利監視器縣市顯示"""
        print("=== 水利監視器縣市顯示測試 ===")
        
        # 創建 ReservoirCommands 實例
        bot = MockBot()
        reservoir_cmd = ReservoirCommands(bot)
        
        # 測試資料 - 模擬 API 回傳的各種縣市格式
        test_data_cases = [
            {
                'VideoSurveillanceStationName': '測試監控站1',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '臺北市',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '中正區',
                'VideoSurveillanceStationAddress': '台北市中正區測試路123號',
                'BasinName': '淡水河',
                'ImageURL': 'http://test.com/image1.jpg'
            },
            {
                'VideoSurveillanceStationName': '測試監控站2', 
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '新北市政府',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '板橋區',
                'VideoSurveillanceStationAddress': '',
                'BasinName': '大漢溪',
                'ImageURL': 'http://test.com/image2.jpg'
            },
            {
                'VideoSurveillanceStationName': '測試監控站3',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '桃園縣',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '桃園區',
                'VideoSurveillanceStationAddress': '桃園市桃園區測試路456號',
                'BasinName': '老街溪',
                'ImageURL': ''
            },
            {
                'VideoSurveillanceStationName': '測試監控站4',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '苗栗',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '苗栗市',
                'VideoSurveillanceStationAddress': '',
                'BasinName': '後龍溪',
                'ImageURL': 'http://test.com/image4.jpg'
            }
        ]
        
        print("測試不同格式的縣市名稱:")
        all_passed = True
        
        for i, test_data in enumerate(test_data_cases, 1):
            print(f"\n--- 測試案例 {i} ---")
            original_county = test_data['CountiesAndCitiesWhereTheMonitoringPointsAreLocated']
            print(f"原始縣市: '{original_county}'")
            
            # 測試主要格式化函數
            try:
                formatted_info = reservoir_cmd.format_water_image_info(test_data)
                print(f"主要函數結果: '{formatted_info['county']}'")
                
                # 測試 View 使用的格式化函數
                view_formatted_info = reservoir_cmd._format_water_image_info(test_data)
                print(f"View函數結果: '{view_formatted_info['county']}'")
                
                # 檢查兩個函數結果是否一致
                if formatted_info['county'] != view_formatted_info['county']:
                    print("❌ 兩個格式化函數結果不一致！")
                    all_passed = False
                else:
                    print("✅ 格式化結果一致")
                
                # 檢查是否正確標準化
                expected_results = {
                    '臺北市': '台北市',
                    '新北市政府': '新北市', 
                    '桃園縣': '桃園市',
                    '苗栗': '苗栗縣'
                }
                
                expected = expected_results.get(original_county, original_county)
                if formatted_info['county'] == expected:
                    print(f"✅ 縣市標準化正確: '{expected}'")
                else:
                    print(f"❌ 縣市標準化錯誤，預期: '{expected}'，實際: '{formatted_info['county']}'")
                    all_passed = False
                
            except Exception as e:
                print(f"❌ 格式化過程發生錯誤: {e}")
                all_passed = False
        
        print(f"\n=== 測試結果: {'全部通過' if all_passed else '部分失敗'} ===")
        return all_passed
    
    if __name__ == "__main__":
        success = test_water_camera_county_display()
        print(f"\n縣市顯示修復測試: {'成功' if success else '失敗'}")
        
except ImportError as e:
    print(f"無法導入 reservoir_commands: {e}")
    print("請確保 cogs/reservoir_commands.py 文件存在")
except Exception as e:
    print(f"測試過程發生錯誤: {e}")
    import traceback
    traceback.print_exc()
