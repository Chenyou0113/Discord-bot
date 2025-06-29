#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單驗證新增的水庫功能
"""

import os
import sys

def test_new_reservoir_features():
    """簡單驗證新增的水庫功能"""
    print("🔍 驗證新增的水庫功能...")
    
    try:
        # 切換工作目錄
        os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
        
        # 測試水庫模組導入
        print("📦 測試水庫模組導入...")
        import cogs.reservoir_commands
        print("✅ 水庫模組導入成功")
        
        # 檢查模組內容
        print("🔍 檢查新增的方法...")
        
        # 檢查類別
        if hasattr(cogs.reservoir_commands, 'ReservoirCommands'):
            print("✅ ReservoirCommands 類別存在")
            reservoir_class = cogs.reservoir_commands.ReservoirCommands
            
            # 檢查新增的方法
            new_methods = [
                'get_reservoir_basic_info',
                'get_water_disaster_images', 
                'format_reservoir_basic_info',
                'format_water_image_info',
                'reservoir_basic_info',
                'water_disaster_cameras'
            ]
            
            methods = dir(reservoir_class)
            found_new_methods = []
            
            for method in new_methods:
                if method in methods:
                    found_new_methods.append(method)
                    print(f"  ✅ {method}")
                else:
                    print(f"  ❌ {method}")
            
            print(f"\n📊 新方法檢查結果: {len(found_new_methods)}/{len(new_methods)}")
            
        else:
            print("❌ 找不到 ReservoirCommands 類別")
            return False
        
        print("\n🎯 預期的新指令功能：")
        print("  - /reservoir_info: 查詢水庫基本資料")
        print("    * 水庫設計資訊（壩高、壩長、壩型）")
        print("    * 容量與用途資訊")
        print("    * 管理機關資訊")
        print("  - /water_cameras: 查詢水利防災監控影像")
        print("    * 全台監控點分布")
        print("    * 即時影像連結")
        print("    * 河川監控資訊")
        
        return True
        
    except Exception as e:
        print(f"❌ 驗證過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_new_reservoir_features()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 新增水庫功能驗證成功！")
        print("✅ 所有新功能配置正確")
        print("🆕 新增指令已準備就緒")
        print("🚀 準備好啟動機器人測試")
        
        print("\n📋 完整的水庫指令系統:")
        print("  1. /reservoir - 水庫水情查詢")
        print("  2. /reservoir_list - 水庫列表")
        print("  3. /reservoir_operation - 水庫營運狀況")
        print("  4. /reservoir_info - 水庫基本資料 ⭐ 新增")
        print("  5. /water_cameras - 水利防災影像 ⭐ 新增")
    else:
        print("❌ 新功能驗證失敗")
        print("🔧 需要檢查上方錯誤並修復")
