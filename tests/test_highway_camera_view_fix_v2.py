#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試公路監視器 View 修復 - 版本 2
修復 HighwayCameraView 的 self.view 問題
"""

import sys
import os

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_highway_camera_view_fix():
    """測試 HighwayCameraView 修復"""
    print("🔧 測試 HighwayCameraView 修復")
    print("=" * 60)
    
    try:
        from cogs.reservoir_commands import HighwayCameraView
        
        # 模擬監視器資料
        test_cameras = [
            {
                'RoadName': 'N1',
                'SurveillanceDescription': '國道一號高速公路(基隆-高雄)',
                'LocationX': '25.0123',
                'LocationY': '121.5123',
                'RoadDirection': 'N',
                'SurveillanceVideoURL': 'http://example.com/video1.jpg',
                'RoadClass': '1',
                'RoadID': '10001'
            },
            {
                'RoadName': 'N3',
                'SurveillanceDescription': '國道三號高速公路(基隆-屏東)',
                'LocationX': '25.0234',
                'LocationY': '121.5234',
                'RoadDirection': 'S',
                'SurveillanceVideoURL': 'http://example.com/video2.jpg',
                'RoadClass': '1',
                'RoadID': '10003'
            }
        ]
        
        # 建立 View 實例
        view = HighwayCameraView(test_cameras)
        print("✅ HighwayCameraView 建立成功")
        
        # 檢查基本屬性
        assert view.cameras == test_cameras, "cameras 屬性設置錯誤"
        assert view.current_index == 0, "current_index 應該為 0"
        assert view.total_cameras == 2, "total_cameras 應該為 2"
        print("✅ 基本屬性檢查通過")
        
        # 檢查按鈕創建
        buttons = [item for item in view.children if hasattr(item, 'callback')]
        print(f"✅ 創建了 {len(buttons)} 個按鈕")
        
        # 檢查每個按鈕都有 parent_view 屬性
        for i, button in enumerate(buttons):
            if hasattr(button, 'parent_view'):
                print(f"   按鈕 {i+1}: {button.label} - ✅ 有 parent_view 屬性")
                assert button.parent_view is view, f"按鈕 {i+1} 的 parent_view 應該是 view 實例"
            else:
                print(f"   按鈕 {i+1}: {button.label} - ❌ 缺少 parent_view 屬性")
                return False
        
        print("✅ 所有按鈕的 parent_view 屬性檢查通過")
        
        # 測試 _update_buttons 方法
        original_button_count = len(view.children)
        view._update_buttons()
        new_button_count = len(view.children)
        
        print(f"✅ _update_buttons 方法測試通過 (按鈕數量: {original_button_count} -> {new_button_count})")
        
        # 測試按鈕類型
        button_types = {}
        for button in view.children:
            if hasattr(button, 'label'):
                if '上一個' in button.label:
                    button_types['previous'] = True
                elif '下一個' in button.label:
                    button_types['next'] = True
                elif '刷新' in button.label:
                    button_types['refresh'] = True
                elif '詳細' in button.label:
                    button_types['info'] = True
        
        print(f"✅ 按鈕類型檢查:")
        print(f"   刷新按鈕: {'✅' if button_types.get('refresh') else '❌'}")
        print(f"   下一個按鈕: {'✅' if button_types.get('next') else '❌'}")
        print(f"   詳細按鈕: {'✅' if button_types.get('info') else '❌'}")
        print(f"   上一個按鈕: {'❌' if not button_types.get('previous') else '✅'} (預期不存在，因為 current_index=0)")
        
        # 測試切換到下一個
        view.current_index = 1
        view._update_buttons()
        
        # 重新檢查按鈕
        button_types = {}
        for button in view.children:
            if hasattr(button, 'label'):
                if '上一個' in button.label:
                    button_types['previous'] = True
                elif '下一個' in button.label:
                    button_types['next'] = True
                elif '刷新' in button.label:
                    button_types['refresh'] = True
                elif '詳細' in button.label:
                    button_types['info'] = True
        
        print(f"\n✅ 切換到索引 1 後的按鈕檢查:")
        print(f"   上一個按鈕: {'✅' if button_types.get('previous') else '❌'}")
        print(f"   刷新按鈕: {'✅' if button_types.get('refresh') else '❌'}")
        print(f"   下一個按鈕: {'❌' if not button_types.get('next') else '✅'} (預期不存在，因為到達最後一個)")
        print(f"   詳細按鈕: {'✅' if button_types.get('info') else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_button_class_structure():
    """測試按鈕類結構"""
    print(f"\n🔍 檢查按鈕類結構:")
    
    try:
        from cogs.reservoir_commands import HighwayCameraView
        
        # 檢查按鈕類是否存在且有正確的 __init__ 方法
        button_classes = [
            'PreviousButton',
            'NextButton', 
            'RefreshButton',
            'InfoButton'
        ]
        
        for button_name in button_classes:
            if hasattr(HighwayCameraView, button_name):
                button_class = getattr(HighwayCameraView, button_name)
                
                # 檢查 __init__ 方法參數
                import inspect
                init_signature = inspect.signature(button_class.__init__)
                params = list(init_signature.parameters.keys())
                
                if 'parent_view' in params:
                    print(f"   ✅ {button_name}: 有 parent_view 參數")
                else:
                    print(f"   ❌ {button_name}: 缺少 parent_view 參數")
                    return False
            else:
                print(f"   ❌ {button_name}: 類不存在")
                return False
        
        print("✅ 所有按鈕類結構檢查通過")
        return True
        
    except Exception as e:
        print(f"❌ 按鈕類結構檢查失敗: {str(e)}")
        return False

def main():
    """主函數"""
    print("🛠️ HighwayCameraView 修復測試 - 版本 2")
    print("修復目標: 解決 'HighwayCameraView' object has no attribute 'view' 錯誤")
    print("=" * 60)
    
    success1 = test_button_class_structure()
    success2 = test_highway_camera_view_fix()
    
    print(f"\n" + "=" * 60)
    if success1 and success2:
        print("🎉 HighwayCameraView 修復測試全部通過！")
        print("💡 修復重點:")
        print("   • 移除對 self.view 的依賴")
        print("   • 改用 parent_view 參數直接傳遞視圖實例")
        print("   • 所有按鈕現在都有穩定的父視圖引用")
        print("🔄 建議重啟機器人測試修復效果")
    else:
        print("❌ 測試失敗，請檢查錯誤訊息")
    print("=" * 60)

if __name__ == "__main__":
    main()
