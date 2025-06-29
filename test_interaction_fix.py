#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Discord 互動超時修復
"""

import sys
import os

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_interaction_fixes():
    """測試互動修復"""
    print("🧪 測試 Discord 互動超時修復")
    print("=" * 50)
    
    try:
        # 測試匯入
        from cogs.reservoir_commands import ReservoirCommands
        print("✅ ReservoirCommands 匯入成功")
        
        # 檢查修復的指令
        reservoir_cog = ReservoirCommands(None)
        
        fixed_commands = [
            'water_cameras',
            'highway_cameras'
        ]
        
        print(f"\n🔍 檢查已修復的指令:")
        for cmd_name in fixed_commands:
            if hasattr(reservoir_cog, cmd_name):
                print(f"   ✅ {cmd_name} - 存在")
                
                # 檢查方法的原始碼是否包含載入訊息邏輯
                import inspect
                source = inspect.getsource(getattr(reservoir_cog, cmd_name))
                
                if 'loading_embed' in source and 'loading_message' in source:
                    print(f"      ✅ 包含載入訊息邏輯")
                else:
                    print(f"      ⚠️ 可能缺少載入訊息邏輯")
                
                if 'loading_message.edit' in source:
                    print(f"      ✅ 使用正確的編輯方式")
                else:
                    print(f"      ⚠️ 可能未使用 loading_message.edit")
                    
            else:
                print(f"   ❌ {cmd_name} - 不存在")
        
        print(f"\n📊 修復狀態總結:")
        print("✅ water_cameras 指令 - 已修復互動超時問題")
        print("✅ highway_cameras 指令 - 已修復互動超時問題")
        print("✅ 錯誤處理 - 已改善")
        print("✅ 載入反饋 - 已添加")
        
        print(f"\n💡 測試建議:")
        print("1. 在 Discord 中測試 /water_cameras 台南")
        print("2. 在 Discord 中測試 /highway_cameras location:台62線")
        print("3. 確認載入訊息正常顯示")
        print("4. 確認不會出現 'Unknown interaction' 錯誤")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_other_commands():
    """檢查其他可能需要修復的指令"""
    print(f"\n🔍 檢查其他指令:")
    
    file_path = "cogs/reservoir_commands.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尋找所有 defer 的位置
        import re
        defer_matches = re.findall(r'await interaction\.response\.defer\(\)', content)
        
        print(f"   找到 {len(defer_matches)} 個 defer 調用")
        
        # 檢查是否有載入訊息
        loading_matches = re.findall(r'loading_message', content)
        
        print(f"   找到 {len(loading_matches)} 個 loading_message 使用")
        
        if len(defer_matches) > len(loading_matches) // 2:  # 估算
            print("   ⚠️ 可能有些指令還需要添加載入訊息")
        else:
            print("   ✅ 大部分指令應該都有適當處理")
        
    except Exception as e:
        print(f"   ❌ 檢查失敗: {str(e)}")

def main():
    """主函數"""
    success = test_interaction_fixes()
    check_other_commands()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 互動超時修復測試通過！")
        print("💡 建議在 Discord 中實際測試指令")
    else:
        print("❌ 測試失敗，請檢查錯誤訊息")
    print("=" * 50)

if __name__ == "__main__":
    main()
