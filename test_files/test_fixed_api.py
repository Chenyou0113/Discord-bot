#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的地震API功能
"""

import asyncio
import sys
import os
import importlib.util

# 添加當前目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fixed_earthquake_api():
    """測試修復後的地震API功能"""
    print("🧪 測試修復後的地震API功能")
    print("=" * 50)
    
    try:
        # 動態導入cogs模組
        spec = importlib.util.spec_from_file_location(
            "info_commands", 
            r"c:\Users\xiaoy\Desktop\Discord bot\cogs\info_commands_fixed_v4_clean.py"
        )
        info_commands_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(info_commands_module)
        
        # 創建InfoCommands實例（模擬bot環境）
        class MockBot:
            def __init__(self):
                pass
        
        mock_bot = MockBot()
        info_commands = info_commands_module.InfoCommands(mock_bot)
        
        # 初始化連線
        await info_commands.init_aiohttp_session()
        
        print("\n🔍 測試一般地震資料獲取...")
        normal_data = await info_commands.fetch_earthquake_data(small_area=False)
        
        if normal_data:
            print("✅ 一般地震資料獲取成功")
            # 檢查資料結構
            if ('result' in normal_data and 
                'records' in normal_data.get('result', {}) and 
                'Earthquake' in normal_data['result']['records'] and
                normal_data['result']['records']['Earthquake']):
                print("✅ 資料結構完整，包含地震資訊")
                earthquake_info = normal_data['result']['records']['Earthquake'][0]
                print(f"   - 地震時間: {earthquake_info.get('EarthquakeInfo', {}).get('OriginTime', 'N/A')}")
                print(f"   - 震央位置: {earthquake_info.get('EarthquakeInfo', {}).get('Epicenter', {}).get('Location', 'N/A')}")
                print(f"   - 地震規模: {earthquake_info.get('EarthquakeInfo', {}).get('EarthquakeMagnitude', {}).get('MagnitudeValue', 'N/A')}")
            else:
                print("⚠️  資料結構不完整或異常")
                print(f"   - 回傳資料鍵值: {list(normal_data.get('result', {}).keys())}")
        else:
            print("❌ 一般地震資料獲取失敗")
        
        print("\n🔍 測試小區域地震資料獲取...")
        small_data = await info_commands.fetch_earthquake_data(small_area=True)
        
        if small_data:
            print("✅ 小區域地震資料獲取成功")
            # 檢查資料結構
            if ('result' in small_data and 
                'records' in small_data.get('result', {}) and 
                'Earthquake' in small_data['result']['records'] and
                small_data['result']['records']['Earthquake']):
                print("✅ 資料結構完整，包含地震資訊")
                earthquake_info = small_data['result']['records']['Earthquake'][0]
                print(f"   - 地震時間: {earthquake_info.get('EarthquakeInfo', {}).get('OriginTime', 'N/A')}")
                print(f"   - 震央位置: {earthquake_info.get('EarthquakeInfo', {}).get('Epicenter', {}).get('Location', 'N/A')}")
                print(f"   - 地震規模: {earthquake_info.get('EarthquakeInfo', {}).get('EarthquakeMagnitude', {}).get('MagnitudeValue', 'N/A')}")
            else:
                print("⚠️  資料結構不完整或異常")
                print(f"   - 回傳資料鍵值: {list(small_data.get('result', {}).keys())}")
        else:
            print("❌ 小區域地震資料獲取失敗")
            
        # 清理資源
        if hasattr(info_commands, 'session') and info_commands.session:
            await info_commands.session.close()
            
        print("\n" + "=" * 50)
        print("✅ 測試完成")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_earthquake_api())
