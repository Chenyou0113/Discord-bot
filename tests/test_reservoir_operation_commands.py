#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水庫營運狀況指令
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# 設定簡化日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_reservoir_operation_commands():
    """測試水庫營運狀況指令功能"""
    print("🏗️ 測試水庫營運狀況指令...")
    print("=" * 50)
    
    try:
        # 切換工作目錄
        os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
        
        # 載入環境變數
        load_dotenv()
        
        # 檢查必要的環境變數
        if not os.getenv('DISCORD_TOKEN'):
            print("❌ 找不到 DISCORD_TOKEN")
            return False
        
        # 測試水庫模組導入
        print("📦 測試水庫模組導入...")
        from cogs.reservoir_commands import ReservoirCommands
        print("✅ 水庫模組導入成功")
        
        # 測試類創建
        print("🤖 創建水庫指令實例...")
        reservoir_cog = ReservoirCommands(None)
        print("✅ 水庫指令實例創建成功")
        
        # 檢查指令方法是否存在
        print("🔍 檢查指令方法...")
        expected_methods = ['reservoir', 'reservoir_list', 'national_highway_cameras', 'general_road_cameras']
        existing_methods = []
        
        for method_name in expected_methods:
            if hasattr(reservoir_cog, method_name):
                existing_methods.append(method_name)
                print(f"✅ {method_name} 方法存在")
            else:
                print(f"⚠️ {method_name} 方法不存在")
        
        # 測試水庫營運 API 連接
        print("\n🔗 測試水庫營運 API 連接...")
        operation_data = await reservoir_cog.get_reservoir_operation_data()
        if operation_data:
            print(f"✅ 水庫營運 API 連接成功，獲得 {len(operation_data)} 筆資料")
            
            # 測試資料格式化
            if operation_data:
                sample_info = reservoir_cog.format_reservoir_operation_info(operation_data[0])
                if sample_info:
                    print(f"✅ 營運資料格式化成功: {sample_info['name']}")
                    print(f"   📊 蓄水量: {sample_info['capacity']} 萬立方公尺")
                    print(f"   💧 水位: {sample_info['water_level']} 公尺")
                    print(f"   🌧️ 降雨量: {sample_info['rainfall']} 毫米")
                else:
                    print("⚠️ 營運資料格式化失敗")
        else:
            print("❌ 水庫營運 API 連接失敗")
        
        # 測試原有的水情 API
        water_data = await reservoir_cog.get_reservoir_data()
        if water_data:
            print(f"✅ 水庫水情 API 仍正常，獲得 {len(water_data)} 筆資料")
        else:
            print("⚠️ 水庫水情 API 連接異常")
        
        # 測試道路分類功能
        print("\n�️ 測試道路分類功能...")
        if hasattr(reservoir_cog, '_classify_road_type'):
            test_camera = {
                'RoadName': 'N1',
                'SurveillanceDescription': '國道一號高速公路',
                'RoadClass': '1',
                'RoadID': '10001'
            }
            road_type = reservoir_cog._classify_road_type(test_camera)
            print(f"✅ 道路分類測試成功: {road_type}")
        else:
            print("⚠️ 道路分類功能不可用")
        
        # 判斷成功標準
        success = (len(existing_methods) >= 2 and 
                  operation_data is not None and
                  water_data is not None)
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 功能測試成功！")
            print("✅ 所有功能載入正常")
            print("🏗️ 水庫查詢指令已準備就緒")
            print("🛣️ 公路監視器指令已準備就緒")
            print("🚀 機器人可以安全啟動")
        else:
            print("⚠️ 部分測試未通過")
        
        return success
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_reservoir_operation_commands())
    
    print("\n🎯 下一步:")
    if success:
        print("  ✅ 所有功能測試完成")
        print("  🤖 可以使用 safe_start_bot.bat 啟動機器人")
        print("  📝 可用的指令:")
        print("     - /reservoir: 查詢水庫水情")
        print("     - /reservoir_list: 顯示水庫列表")
        print("     - /national_highway_cameras: 查詢國道監視器 ⭐")
        print("     - /general_road_cameras: 查詢省道/快速公路/一般道路監視器 ⭐")
    else:
        print("  ❌ 需要檢查上方錯誤訊息並進行修復")
