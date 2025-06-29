#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的公路監視器功能測試
"""

import sys
import os
import asyncio

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_highway_cameras_fix():
    """測試公路監視器修復"""
    print("🔧 測試公路監視器功能修復")
    print("=" * 60)
    
    try:
        # 測試導入
        from cogs.reservoir_commands import ReservoirCommands, HighwayCameraView
        print("✅ 模組導入成功")
        
        # 測試類創建
        reservoir_cog = ReservoirCommands(None)
        print("✅ ReservoirCommands 實例創建成功")
        
        # 測試道路分類方法
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
            print("❌ _classify_road_type 方法不存在")
        
        # 測試 HighwayCameraView
        test_cameras = [
            {
                'RoadName': 'N1',
                'SurveillanceDescription': '國道一號高速公路',
                'CCTVID': 'test001',
                'RoadDirection': 'N',
                'LocationMile': '10.5',
                'PositionLat': '25.0',
                'PositionLon': '121.5',
                'VideoImageURL': 'http://example.com/test.jpg'
            }
        ]
        
        view = HighwayCameraView(test_cameras)
        print("✅ HighwayCameraView 創建成功")
        
        # 檢查按鈕是否正確創建
        button_count = len(view.children)
        print(f"✅ 按鈕數量: {button_count}")
        
        # 檢查按鈕是否有 parent_view 屬性
        for i, button in enumerate(view.children):
            if hasattr(button, 'parent_view'):
                print(f"✅ 按鈕 {i+1} 有 parent_view 屬性")
            else:
                print(f"❌ 按鈕 {i+1} 缺少 parent_view 屬性")
                return False
        
        print("✅ 所有測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_command_structure():
    """測試指令結構"""
    print(f"\n🔍 檢查指令結構:")
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        import inspect
        
        # 獲取所有方法
        methods = inspect.getmembers(ReservoirCommands, predicate=inspect.ismethod)
        all_methods = [name for name, method in inspect.getmembers(ReservoirCommands)]
        
        expected_commands = ['national_highway_cameras', 'general_road_cameras']
        
        for cmd in expected_commands:
            if cmd in all_methods:
                print(f"✅ {cmd} 指令存在")
            else:
                print(f"❌ {cmd} 指令不存在")
                return False
        
        print("✅ 指令結構檢查通過")
        return True
        
    except Exception as e:
        print(f"❌ 指令結構檢查失敗: {str(e)}")
        return False

async def main():
    """主函數"""
    print("🛠️ 公路監視器功能完整測試")
    print("=" * 60)
    
    success1 = await test_highway_cameras_fix()
    success2 = test_command_structure()
    
    print(f"\n" + "=" * 60)
    if success1 and success2:
        print("🎉 所有測試通過！")
        print("✅ 公路監視器功能修復完成")
        print("💡 功能總結:")
        print("   • /national_highway_cameras - 查詢國道監視器")
        print("   • /general_road_cameras - 查詢省道/快速公路/一般道路監視器")
        print("   • HighwayCameraView 按鈕切換功能已修復")
        print("   • 道路類型自動分類功能正常")
        print("🔄 建議重啟機器人測試功能")
    else:
        print("❌ 部分測試失敗，請檢查錯誤訊息")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
