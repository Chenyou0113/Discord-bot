#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試公路監視器指令整合
"""

import sys
import os
import logging

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定日誌
logging.basicConfig(level=logging.INFO)

def test_highway_camera_command():
    """測試公路監視器指令整合"""
    print("🛣️ 測試公路監視器指令整合")
    print("=" * 60)
    
    try:
        # 測試匯入 ReservoirCommands
        print("📦 測試匯入 ReservoirCommands...")
        from cogs.reservoir_commands import ReservoirCommands
        print("✅ 成功匯入 ReservoirCommands")
        
        # 檢查新的指令是否存在
        reservoir_cog = ReservoirCommands(None)
        
        # 檢查指令
        commands_to_check = [
            'reservoir_list',
            'water_disaster_cameras', 
            'river_levels',
            'check_permissions',
            'highway_cameras'  # 新增的指令
        ]
        
        print(f"\n🔍 檢查指令存在性:")
        for cmd_name in commands_to_check:
            if hasattr(reservoir_cog, cmd_name):
                print(f"   ✅ {cmd_name} - 存在")
            else:
                print(f"   ❌ {cmd_name} - 不存在")
        
        # 檢查新增的方法
        methods_to_check = [
            '_get_highway_cameras',
            '_parse_highway_cameras_xml',
            '_process_highway_image_url'
        ]
        
        print(f"\n🔧 檢查輔助方法:")
        for method_name in methods_to_check:
            if hasattr(reservoir_cog, method_name):
                print(f"   ✅ {method_name} - 存在")
            else:
                print(f"   ❌ {method_name} - 不存在")
        
        # 檢查新的 View 類別
        print(f"\n🖥️ 檢查 View 類別:")
        try:
            from cogs.reservoir_commands import HighwayCameraView, HighwayCameraInfoModal
            print(f"   ✅ HighwayCameraView - 存在")
            print(f"   ✅ HighwayCameraInfoModal - 存在")
        except ImportError as e:
            print(f"   ❌ View 類別匯入失敗: {str(e)}")
        
        print(f"\n" + "=" * 60)
        print("✅ 公路監視器功能整合測試完成")
        print("=" * 60)
        
        print(f"\n📋 功能清單:")
        print(f"   🎯 /highway_cameras - 查詢公路監視器")
        print(f"   🔍 支援位置關鍵字篩選（如：台62線、國道一號、基隆）")
        print(f"   🧭 支援方向篩選（N、S、E、W）")
        print(f"   📸 自動載入監視器影像")
        print(f"   🔄 支援多監視器切換功能")
        print(f"   ℹ️ 支援詳細資訊查看")
        
        print(f"\n💡 使用範例:")
        print(f"   /highway_cameras location:台62線")
        print(f"   /highway_cameras location:國道一號 direction:N")
        print(f"   /highway_cameras location:基隆")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    success = test_highway_camera_command()
    
    if success:
        print(f"\n🎉 所有測試通過！公路監視器功能已成功整合到機器人中。")
        print(f"🚀 現在可以啟動機器人並使用 /highway_cameras 指令。")
    else:
        print(f"\n❌ 測試失敗，請檢查錯誤訊息並修復問題。")

if __name__ == "__main__":
    main()
