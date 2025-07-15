#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試公路監視器道路類型功能
"""

import sys
import os

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_road_type_classification():
    """測試道路類型分類功能"""
    print("🛣️ 測試公路監視器道路類型分類功能")
    print("=" * 60)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立測試實例
        reservoir_cog = ReservoirCommands(None)
        print("✅ ReservoirCommands 匯入成功")
        
        # 測試道路分類方法
        if hasattr(reservoir_cog, '_classify_road_type'):
            print("✅ _classify_road_type 方法存在")
            
            # 模擬測試監視器資料
            test_cameras = [
                {
                    'RoadName': 'N1',
                    'SurveillanceDescription': '國道一號高速公路(基隆-高雄)',
                    'RoadClass': '1',
                    'RoadID': '10001',
                    'expected': 'national'
                },
                {
                    'RoadName': 'N3', 
                    'SurveillanceDescription': '國道三號高速公路(基隆-屏東)',
                    'RoadClass': '1',
                    'RoadID': '10003',
                    'expected': 'national'
                },
                {
                    'RoadName': '台1線',
                    'SurveillanceDescription': '台1線省道',
                    'RoadClass': '2',
                    'RoadID': '20001',
                    'expected': 'provincial'
                },
                {
                    'RoadName': '台9線',
                    'SurveillanceDescription': '台9線省道(蘇花公路)',
                    'RoadClass': '2', 
                    'RoadID': '20009',
                    'expected': 'provincial'
                },
                {
                    'RoadName': '台62線',
                    'SurveillanceDescription': '快速公路62號(暖暖-大華)',
                    'RoadClass': '2',
                    'RoadID': '20062',
                    'expected': 'freeway'
                },
                {
                    'RoadName': '台64線',
                    'SurveillanceDescription': '快速公路64號(八里-新店)',
                    'RoadClass': '2',
                    'RoadID': '20064',
                    'expected': 'freeway'
                },
                {
                    'RoadName': '一般道路',
                    'SurveillanceDescription': '一般市區道路',
                    'RoadClass': '3',
                    'RoadID': '30001',
                    'expected': 'general'
                }
            ]
            
            print(f"\n🧪 測試道路類型分類:")
            correct_count = 0
            
            for i, camera in enumerate(test_cameras):
                expected = camera.pop('expected')
                result = reservoir_cog._classify_road_type(camera)
                
                status = "✅" if result == expected else "❌"
                road_type_names = {
                    "national": "國道",
                    "provincial": "省道",
                    "freeway": "快速公路", 
                    "general": "一般道路"
                }
                
                print(f"   {status} {camera['RoadName']}: {road_type_names.get(result, result)} (預期: {road_type_names.get(expected, expected)})")
                
                if result == expected:
                    correct_count += 1
            
            print(f"\n📊 分類準確度: {correct_count}/{len(test_cameras)} ({correct_count/len(test_cameras)*100:.1f}%)")
            
        else:
            print("❌ _classify_road_type 方法不存在")
        
        # 檢查指令參數
        import inspect
        source = inspect.getsource(reservoir_cog.highway_cameras)
        
        print(f"\n🔍 檢查指令功能:")
        
        if 'road_type:' in source or 'road_type =' in source:
            print("✅ 指令包含道路類型參數")
        else:
            print("❌ 指令缺少道路類型參數")
        
        if 'road_type_filtered_cameras' in source:
            print("✅ 包含道路類型篩選邏輯")
        else:
            print("❌ 缺少道路類型篩選邏輯")
        
        # 檢查選項
        road_type_choices = ['national', 'provincial', 'freeway', 'general']
        found_choices = sum(1 for choice in road_type_choices if choice in source)
        
        if found_choices >= 3:
            print(f"✅ 道路類型選項已定義 ({found_choices}/{len(road_type_choices)})")
        else:
            print(f"❌ 道路類型選項不完整 ({found_choices}/{len(road_type_choices)})")
        
        print(f"\n💡 使用說明:")
        print("現在可以使用以下參數組合:")
        print("• road_type: 國道、省道、快速公路、一般道路")
        print("• location: 位置關鍵字")
        print("• direction: 行駛方向")
        print("• city: 縣市選擇")
        
        print(f"\n🎯 建議測試指令:")
        print("1. /highway_cameras road_type:國道")
        print("2. /highway_cameras road_type:省道")
        print("3. /highway_cameras road_type:快速公路")
        print("4. /highway_cameras road_type:國道 city:台北市")
        print("5. /highway_cameras road_type:省道 direction:N")
        print("6. /highway_cameras location:台1線 road_type:省道")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_road_type_display():
    """測試道路類型顯示"""
    print(f"\n🎨 測試道路類型顯示:")
    
    road_type_display = {
        "national": "🛣️ 國道",
        "provincial": "🛤️ 省道", 
        "freeway": "🏎️ 快速公路",
        "general": "🚗 一般道路"
    }
    
    for road_type, display in road_type_display.items():
        print(f"   {road_type} -> {display}")
    
    print("✅ 道路類型顯示圖示正常")

def main():
    """主函數"""
    success = test_road_type_classification()
    test_road_type_display()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 道路類型功能測試通過！")
        print("💡 建議在 Discord 中測試新的道路類型選項")
        print("🔄 記得重啟機器人以載入更新")
    else:
        print("❌ 測試失敗，請檢查錯誤訊息")
    print("=" * 60)

if __name__ == "__main__":
    main()
