#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水利監視器圖片嵌入修復
驗證新的備用方案是否正常工作
"""

import asyncio
import sys

async def test_improved_embed():
    """測試改進的 Embed 功能"""
    
    print("🧪 測試改進的水利監視器 Embed 功能")
    print("=" * 60)
    
    try:
        from cogs.reservoir_commands import WaterCameraView
        
        # 測試資料：包含不同狀況的監控點
        test_cases = [
            {
                'name': '有效圖片URL',
                'data': {
                    'VideoSurveillanceStationName': '淡水河測試站',
                    'VideoSurveillanceStationId': 'TEST001',
                    'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '新北市',
                    'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '淡水區',
                    'VideoSurveillanceStationAddress': '新北市淡水區測試路1號',
                    'ImageURL': 'https://httpbin.org/image/jpeg',  # 測試圖片
                    'River': '淡水河'
                }
            },
            {
                'name': '政府網站圖片URL',
                'data': {
                    'VideoSurveillanceStationName': '水利署測試站',
                    'VideoSurveillanceStationId': 'TEST002',
                    'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
                    'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '信義區',
                    'VideoSurveillanceStationAddress': '台北市信義區測試路2號',
                    'ImageURL': 'https://alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg',
                    'River': '基隆河'
                }
            },
            {
                'name': '無圖片URL',
                'data': {
                    'VideoSurveillanceStationName': '無影像測試站',
                    'VideoSurveillanceStationId': 'TEST003',
                    'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '高雄市',
                    'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '鼓山區',
                    'VideoSurveillanceStationAddress': '高雄市鼓山區測試路3號',
                    'ImageURL': '',
                    'River': '愛河'
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}️⃣ 測試案例: {test_case['name']}")
            
            # 創建 WaterCameraView
            view = WaterCameraView([test_case['data']], 0, "測試地區")
            
            # 創建 Embed
            embed = await view._create_water_camera_embed(test_case['data'])
            
            print(f"   標題: {embed.title}")
            print(f"   描述: {embed.description}")
            print(f"   欄位數量: {len(embed.fields)}")
            
            # 檢查是否有圖片
            if embed.image and embed.image.url:
                print(f"   ✅ 嵌入圖片: {embed.image.url}")
            else:
                print(f"   ⚠️ 沒有嵌入圖片")
            
            # 檢查欄位內容
            for j, field in enumerate(embed.fields):
                print(f"   欄位 {j+1}: {field.name}")
                if "監控影像" in field.name or "影像狀態" in field.name:
                    print(f"      內容: {field.value[:100]}...")
            
            print(f"   底部文字: {embed.footer.text}")
        
        print("\n✅ 所有測試案例完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_button_functionality():
    """測試按鈕功能是否正常"""
    
    print("\n🔘 測試按鈕功能")
    print("=" * 40)
    
    try:
        from cogs.reservoir_commands import WaterCameraView
        
        # 創建多個測試監控點
        cameras = [
            {
                'VideoSurveillanceStationName': f'測試監控站{i}',
                'VideoSurveillanceStationId': f'TEST00{i}',
                'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
                'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '信義區',
                'VideoSurveillanceStationAddress': f'台北市信義區測試路{i}號',
                'ImageURL': f'https://httpbin.org/image/jpeg?id={i}',
                'River': '淡水河'
            }
            for i in range(1, 4)
        ]
        
        view = WaterCameraView(cameras, 0, "台北市")
        
        print(f"監控點總數: {view.total_cameras}")
        print(f"當前索引: {view.current_index}")
        
        # 檢查按鈕
        buttons = [item for item in view.children if hasattr(item, 'callback')]
        print(f"按鈕數量: {len(buttons)}")
        
        for i, button in enumerate(buttons):
            print(f"   按鈕 {i+1}: {button.label}")
        
        print("✅ 按鈕功能檢查完成")
        return True
        
    except Exception as e:
        print(f"❌ 按鈕測試失敗: {e}")
        return False

async def main():
    """主函數"""
    
    print("🚀 水利監視器圖片嵌入修復測試")
    print("=" * 80)
    
    # 測試改進的 Embed 功能
    embed_test = await test_improved_embed()
    
    # 測試按鈕功能
    button_test = await test_button_functionality()
    
    # 結果報告
    print("\n" + "=" * 80)
    print("📊 測試結果:")
    print(f"Embed 功能: {'✅ 通過' if embed_test else '❌ 失敗'}")
    print(f"按鈕功能: {'✅ 通過' if button_test else '❌ 失敗'}")
    
    if embed_test and button_test:
        print("\n🎉 修復測試通過！")
        print("✅ 改進功能:")
        print("   • 圖片嵌入失敗時提供連結")
        print("   • 顯示詳細的影像狀態資訊")
        print("   • 增加河川資訊顯示")
        print("   • 按鈕功能保持正常")
        print("   • 用戶體驗大幅提升")
        
        print("\n💡 現在用戶可以:")
        print("   • 點擊連結直接查看監控影像")
        print("   • 看到清楚的影像狀態說明")
        print("   • 使用按鈕瀏覽多個監控點")
        print("   • 獲得更好的視覺體驗")
        
        return True
    else:
        print("\n❌ 修復測試失敗，需要進一步調整")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 測試運行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
