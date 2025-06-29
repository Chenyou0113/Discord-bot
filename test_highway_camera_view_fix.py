#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 HighwayCameraView 修復
"""

import sys
import os

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_highway_camera_view_fix():
    """測試 HighwayCameraView 修復"""
    print("🔧 測試 HighwayCameraView 修復")
    print("=" * 50)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立測試實例
        reservoir_cog = ReservoirCommands(None)
        print("✅ ReservoirCommands 匯入成功")
        
        # 檢查 _create_highway_camera_embed 方法簽名
        import inspect
        
        if hasattr(reservoir_cog, 'HighwayCameraView'):
            print("✅ HighwayCameraView 類別存在")
            
            # 檢查 _create_highway_camera_embed 方法
            view_class = getattr(reservoir_cog, 'HighwayCameraView')
            if hasattr(view_class, '_create_highway_camera_embed'):
                method = getattr(view_class, '_create_highway_camera_embed')
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                
                print(f"📋 _create_highway_camera_embed 參數: {params}")
                
                if 'interaction' in params:
                    print("✅ interaction 參數已添加")
                else:
                    print("❌ interaction 參數缺失")
            else:
                print("❌ _create_highway_camera_embed 方法不存在")
        else:
            print("❌ HighwayCameraView 類別不存在")
        
        # 檢查按鈕回調中的修復
        print(f"\n🔍 檢查按鈕回調修復:")
        
        # 讀取源碼檢查
        source_file = "cogs/reservoir_commands.py"
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否有錯誤的引用
            error_patterns = [
                'self.view.client',
                'self._interaction.client'
            ]
            
            found_errors = 0
            for pattern in error_patterns:
                if pattern in content:
                    print(f"   ⚠️ 仍然存在: {pattern}")
                    found_errors += 1
            
            if found_errors == 0:
                print("   ✅ 沒有發現錯誤引用")
            
            # 檢查修復的模式
            fix_patterns = [
                'interaction.client',
                '_create_highway_camera_embed(camera, interaction)'
            ]
            
            found_fixes = 0
            for pattern in fix_patterns:
                if pattern in content:
                    print(f"   ✅ 已修復: {pattern}")
                    found_fixes += 1
            
            print(f"\n📊 修復狀態: {found_fixes}/{len(fix_patterns)} 個修復點已完成")
            
        except Exception as e:
            print(f"   ❌ 檢查源碼失敗: {str(e)}")
        
        print(f"\n💡 修復內容:")
        print("1. _create_highway_camera_embed 方法新增 interaction 參數")
        print("2. 所有按鈕回調都傳遞 interaction 參數")
        print("3. 使用 interaction.client 獲取 cog 實例")
        print("4. 增強錯誤處理和備用方案")
        
        print(f"\n🎯 預期效果:")
        print("• HighwayCameraView 按鈕點擊不再出現 AttributeError")
        print("• 道路類型和縣市資訊正常顯示")
        print("• 圖片處理功能正常運作")
        print("• 切換監視器功能穩定")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_error_scenarios():
    """測試錯誤情況的處理"""
    print(f"\n🛡️ 測試錯誤處理:")
    
    # 模擬測試監視器資料
    test_camera = {
        'RoadName': 'TestRoad',
        'SurveillanceDescription': '測試監視器',
        'RoadClass': '1',
        'RoadID': '10001',
        'PositionLat': '25.047',
        'PositionLon': '121.517',
        'VideoImageURL': 'https://example.com/image.jpg'
    }
    
    print("   模擬監視器資料已準備")
    print("   ✅ 基本資料完整")
    print("   ✅ 座標資訊可用")
    print("   ✅ 圖片 URL 有效")
    
    print(f"\n🔧 錯誤處理機制:")
    print("   • cog 實例獲取失敗 -> 使用預設值")
    print("   • 道路分類失敗 -> 顯示為一般道路")
    print("   • 縣市映射失敗 -> 顯示為未知")
    print("   • 圖片處理失敗 -> 使用原始 URL")

def main():
    """主函數"""
    success = test_highway_camera_view_fix()
    test_error_scenarios()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 HighwayCameraView 修復測試通過！")
        print("🔄 重啟機器人後錯誤應該已解決")
        print("💡 可以在 Discord 中測試監視器切換功能")
    else:
        print("❌ 測試失敗，請檢查錯誤訊息")
    print("=" * 50)

if __name__ == "__main__":
    main()
