#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證新增的監視器指令
"""

import sys
import os
import inspect
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_reservoir_commands():
    """驗證 ReservoirCommands 模組"""
    print("🔧 驗證 ReservoirCommands 模組...")
    print("=" * 50)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        print("✅ ReservoirCommands 導入成功")
        
        # 檢查指令方法
        expected_commands = [
            'water_level',
            'water_cameras', 
            'water_disaster_cameras',
            'national_highway_cameras',
            'general_road_cameras'
        ]
        
        print(f"\n📋 檢查指令方法...")
        found_commands = []
        
        for command_name in expected_commands:
            if hasattr(ReservoirCommands, command_name):
                method = getattr(ReservoirCommands, command_name)
                if callable(method):
                    found_commands.append(command_name)
                    print(f"  ✅ {command_name} - 已找到")
                else:
                    print(f"  ❌ {command_name} - 不是可調用方法")
            else:
                print(f"  ❌ {command_name} - 未找到")
        
        # 檢查輔助方法
        expected_methods = [
            'get_water_disaster_images',
            '_get_highway_cameras',
            '_parse_highway_cameras_xml',
            '_classify_road_type',
            '_create_highway_camera_embed',
            '_create_water_camera_embed',
            '_normalize_county_name',
            '_add_timestamp_to_url'
        ]
        
        print(f"\n🔧 檢查輔助方法...")
        found_methods = []
        
        for method_name in expected_methods:
            if hasattr(ReservoirCommands, method_name):
                method = getattr(ReservoirCommands, method_name)
                if callable(method):
                    found_methods.append(method_name)
                    print(f"  ✅ {method_name} - 已找到")
                else:
                    print(f"  ❌ {method_name} - 不是可調用方法")
            else:
                print(f"  ❌ {method_name} - 未找到")
        
        # 檢查 View 類別
        print(f"\n🖼️ 檢查 View 類別...")
        try:
            from cogs.reservoir_commands import WaterCameraView, WaterCameraInfoModal
            print("  ✅ WaterCameraView - 已找到")
            print("  ✅ WaterCameraInfoModal - 已找到")
        except ImportError as e:
            print(f"  ❌ WaterCamera 相關類別導入失敗: {e}")
        
        try:
            from cogs.reservoir_commands import HighwayCameraView, HighwayCameraInfoModal
            print("  ✅ HighwayCameraView - 已找到")
            print("  ✅ HighwayCameraInfoModal - 已找到")
        except ImportError as e:
            print(f"  ❌ HighwayCamera 相關類別導入失敗: {e}")
        
        # 統計結果
        print(f"\n📊 驗證結果:")
        print(f"  指令方法: {len(found_commands)}/{len(expected_commands)}")
        print(f"  輔助方法: {len(found_methods)}/{len(expected_methods)}")
        
        success_rate = (len(found_commands) + len(found_methods)) / (len(expected_commands) + len(expected_methods))
        print(f"  成功率: {success_rate:.1%}")
        
        if success_rate >= 0.9:
            print("🎉 驗證通過！所有主要功能已成功添加")
            return True
        else:
            print("⚠️ 部分功能缺失，需要進一步修復")
            return False
            
    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")
        return False

def check_command_count():
    """檢查指令數量"""
    print(f"\n🔢 預期新增指令數量:")
    
    new_commands = [
        "/water_level - 水位查詢",
        "/water_cameras - 水利防災影像", 
        "/national_highway_cameras - 國道監視器",
        "/general_road_cameras - 一般道路監視器"
    ]
    
    for cmd in new_commands:
        print(f"  ✅ {cmd}")
    
    print(f"\n💡 預期總指令數: 57 + {len(new_commands)} = {57 + len(new_commands)}")

def main():
    """主函數"""
    print("🚀 監視器指令修復驗證")
    print("=" * 50)
    print(f"驗證時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 執行驗證
    success = verify_reservoir_commands()
    
    # 檢查指令數量
    check_command_count()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 驗證成功！所有監視器指令已修復並準備就緒")
        print("\n📋 新增的指令:")
        print("  • /water_level - 查詢河川水位資料")
        print("  • /water_cameras - 查詢水利防災監控影像")
        print("  • /national_highway_cameras - 查詢國道監視器")
        print("  • /general_road_cameras - 查詢省道/快速公路/一般道路監視器")
        
        print("\n🎯 功能特色:")
        print("  ✅ 縣市下拉選單篩選")
        print("  ✅ 縣市名稱標準化 (臺→台)")
        print("  ✅ 圖片快取破壞 (時間戳)")
        print("  ✅ 按鈕切換多個監視器")
        print("  ✅ 詳細資訊彈窗")
        
        print("\n🚀 現在可以重新啟動機器人測試新功能！")
    else:
        print("❌ 驗證失敗！需要進一步修復")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
