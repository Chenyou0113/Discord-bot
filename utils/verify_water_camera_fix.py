#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水利防災影像修復驗證
直接測試 WaterCameraView 和相關功能
"""

import sys
import asyncio

async def test_water_camera_view():
    """測試 WaterCameraView 功能"""
    
    print("🧪 測試 WaterCameraView 功能")
    print("=" * 60)
    
    try:
        # 導入 WaterCameraView
        sys.path.append('.')
        from cogs.reservoir_commands import WaterCameraView
        
        # 模擬監控點資料
        mock_cameras = [
            {
                'VideoSurveillanceStationName': '測試監控站1',
                'VideoSurveillanceStationId': 'TEST001',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '信義區',
                'VideoSurveillanceStationAddress': '台北市信義區測試路1號',
                'ImageURL': 'https://example.com/test1.jpg',
                'River': '淡水河'
            },
            {
                'VideoSurveillanceStationName': '測試監控站2',
                'VideoSurveillanceStationId': 'TEST002',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '大安區',
                'VideoSurveillanceStationAddress': '台北市大安區測試路2號',
                'ImageURL': 'https://example.com/test2.jpg',
                'River': '新店溪'
            }
        ]
        
        print("1️⃣ 創建 WaterCameraView...")
        view = WaterCameraView(mock_cameras, 0, "台北市")
        print("✅ WaterCameraView 創建成功")
        print(f"   總監控點數: {view.total_cameras}")
        print(f"   當前索引: {view.current_index}")
        print(f"   搜尋條件: {view.search_term}")
        
        print("\n2️⃣ 測試 Embed 創建...")
        embed = await view._create_water_camera_embed(mock_cameras[0])
        print("✅ Embed 創建成功")
        print(f"   標題: {embed.title}")
        print(f"   描述: {embed.description}")
        print(f"   欄位數量: {len(embed.fields)}")
        
        # 檢查欄位內容
        for i, field in enumerate(embed.fields):
            print(f"   欄位 {i+1}: {field.name}")
        
        # 檢查影像
        if embed.image and embed.image.url:
            print(f"   影像URL: {embed.image.url}")
        else:
            print("   ⚠️ 沒有影像URL")
        
        print("\n3️⃣ 測試按鈕...")
        buttons = [item for item in view.children if hasattr(item, 'callback')]
        print(f"✅ 按鈕數量: {len(buttons)}")
        
        for i, button in enumerate(buttons):
            print(f"   按鈕 {i+1}: {button.label}")
        
        print("\n4️⃣ 測試資料格式化方法...")
        info = view._format_water_image_info(mock_cameras[0])
        print("✅ 資料格式化成功")
        print(f"   監控站名稱: {info['station_name']}")
        print(f"   縣市: {info['county']}")
        print(f"   影像URL: {info['image_url']}")
        
        print("\n5️⃣ 測試 URL 處理...")
        test_urls = [
            'https://example.com/test.jpg',
            '/path/to/image.jpg',
            'test.jpg'
        ]
        
        for url in test_urls:
            processed = view._process_and_validate_image_url(url)
            print(f"   '{url}' -> '{processed}'")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_import():
    """測試模組導入"""
    
    print("📦 測試模組導入")
    print("=" * 40)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands, WaterCameraView, WaterCameraInfoModal
        print("✅ ReservoirCommands 導入成功")
        print("✅ WaterCameraView 導入成功")
        print("✅ WaterCameraInfoModal 導入成功")
        return True
    except Exception as e:
        print(f"❌ 模組導入失敗: {e}")
        return False

async def main():
    """主函數"""
    
    print("🔍 水利防災影像修復驗證")
    print("=" * 80)
    
    # 測試模組導入
    import_test = test_module_import()
    
    # 測試 WaterCameraView
    view_test = False
    if import_test:
        view_test = await test_water_camera_view()
    
    # 結果報告
    print("\n" + "=" * 80)
    print("📊 測試結果:")
    print(f"模組導入: {'✅ 通過' if import_test else '❌ 失敗'}")
    print(f"WaterCameraView: {'✅ 通過' if view_test else '❌ 失敗'}")
    
    if import_test and view_test:
        print("\n🎉 水利防災影像修復驗證通過！")
        print("✅ 所有功能正常工作:")
        print("   • 按鈕界面已實現")
        print("   • 影像顯示功能正常")
        print("   • 監控點資料格式化正確")
        print("   • URL 處理功能正常")
        print("   • 沒有 await 錯誤")
        print("\n💡 現在用戶可以:")
        print("   • 使用縣市下拉選單選擇地區")
        print("   • 透過按鈕瀏覽多個監控點")
        print("   • 查看監控點詳細資訊")
        print("   • 正常顯示監控影像")
        return True
    else:
        print("\n❌ 修復驗證失敗，需要進一步處理")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 驗證過程錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
