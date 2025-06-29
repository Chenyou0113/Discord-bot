#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試水利監視器修復效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from cogs.reservoir_commands import ReservoirCommands

class MockBot:
    """模擬機器人"""
    pass

async def quick_test_camera_fix():
    """快速測試監視器修復"""
    print("🔧 測試水利監視器圖片顯示修復")
    print("=" * 50)
    
    try:
        # 創建 ReservoirCommands 實例
        bot = MockBot()
        reservoir_cog = ReservoirCommands(bot)
        
        # 獲取監視器資料
        print("📡 正在獲取監視器資料...")
        image_data = await reservoir_cog.get_water_disaster_images()
        
        if not image_data:
            print("❌ 無法獲取監視器資料")
            return False
        
        print(f"✅ 成功獲取 {len(image_data)} 個監視器資料")
        
        # 測試格式化函數
        print("\n🔍 測試前5個監視器的格式化...")
        success_count = 0
        image_count = 0
        
        for i, data in enumerate(image_data[:5], 1):
            print(f"\n📸 監視器 {i}:")
            
            # 使用修復後的格式化函數
            info = reservoir_cog.format_water_image_info(data)
            
            if info:
                success_count += 1
                station_name = info['station_name']
                location = info['location']
                image_url = info['image_url']
                status = info['status']
                
                print(f"  名稱: {station_name}")
                print(f"  位置: {location}")
                print(f"  狀態: {status}")
                print(f"  圖片: {image_url}")
                
                if image_url != 'N/A':
                    image_count += 1
                    print(f"  ✅ 有圖片 URL")
                else:
                    print(f"  ⚠️ 無圖片 URL")
            else:
                print(f"  ❌ 格式化失敗")
        
        print(f"\n📊 測試結果:")
        print(f"成功格式化: {success_count}/5")
        print(f"有圖片 URL: {image_count}/5")
        
        # 測試台南地區監視器
        print(f"\n🏷️ 測試台南地區監視器...")
        tainan_cameras = []
        for data in image_data:
            location = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
            if '台南' in location:
                tainan_cameras.append(data)
        
        print(f"找到 {len(tainan_cameras)} 個台南監視器")
        
        if tainan_cameras:
            print(f"台南監視器範例:")
            info = reservoir_cog.format_water_image_info(tainan_cameras[0])
            if info:
                print(f"  📸 {info['station_name']}")
                print(f"  📍 {info['location']}")
                print(f"  🌊 {info['river']}")
                print(f"  📡 {info['status']}")
                print(f"  🖼️ 圖片: {info['image_url']}")
                
                if info['image_url'] != 'N/A':
                    print(f"  ✅ 已修復圖片 URL 格式")
                else:
                    print(f"  ⚠️ 此監視器無圖片")
        
        if success_count >= 4 and image_count >= 1:
            print(f"\n🎉 修復測試通過！")
            print(f"✅ 格式化功能正常")
            print(f"✅ 圖片 URL 處理正常")
            return True
        else:
            print(f"\n⚠️ 修復可能需要進一步調整")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("開始快速測試...")
    success = asyncio.run(quick_test_camera_fix())
    
    if success:
        print(f"\n🚀 監視器功能已修復，可以正常使用 /water_cameras 指令！")
        print(f"💡 使用方法:")
        print(f"   /water_cameras 台南  # 查看台南地區監視器")
        print(f"   /water_cameras 高雄  # 查看高雄地區監視器")
        print(f"   /water_cameras       # 查看所有地區概覽")
    else:
        print(f"\n⚠️ 可能需要進一步檢查 API 連線或資料品質")
        print(f"🔧 請執行完整診斷: python diagnose_camera_images.py")

if __name__ == "__main__":
    main()
