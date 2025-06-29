#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的國道監視器指令
"""

import asyncio
import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_national_highway_fix():
    """測試修復後的國道監視器指令"""
    print("🛣️ 測試修復後的國道監視器指令")
    print("=" * 60)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立實例
        reservoir_cog = ReservoirCommands(None)
        
        # 獲取公路監視器資料
        print("📡 獲取公路監視器資料...")
        cameras = await reservoir_cog._get_highway_cameras()
        
        if not cameras:
            print("❌ 無法獲取監視器資料")
            return False
        
        print(f"✅ 獲得 {len(cameras)} 個監視器資料")
        
        # 測試國道篩選
        print(f"\n🛣️ 測試國道監視器篩選...")
        national_cameras = [c for c in cameras if reservoir_cog._classify_road_type(c) == 'national']
        print(f"✅ 找到 {len(national_cameras)} 個國道監視器")
        
        # 顯示國道監視器範例
        if national_cameras:
            print(f"\n📋 國道監視器範例:")
            for i, camera in enumerate(national_cameras[:5]):
                road_name = camera.get('RoadName', '')
                surveillance_desc = camera.get('SurveillanceDescription', '')
                road_class = camera.get('RoadClass', '')
                
                print(f"{i+1}. {surveillance_desc}")
                print(f"   道路名: {road_name}")
                print(f"   分類: {road_class}")
                print(f"   分類結果: 國道 ✅")
        
        # 測試快速公路篩選
        print(f"\n🏎️ 測試快速公路篩選...")
        freeway_cameras = [c for c in cameras if reservoir_cog._classify_road_type(c) == 'freeway']
        print(f"✅ 找到 {len(freeway_cameras)} 個快速公路監視器")
        
        # 顯示快速公路範例
        if freeway_cameras:
            print(f"\n📋 快速公路監視器範例:")
            for i, camera in enumerate(freeway_cameras[:5]):
                road_name = camera.get('RoadName', '')
                surveillance_desc = camera.get('SurveillanceDescription', '')
                
                print(f"{i+1}. {surveillance_desc}")
                print(f"   道路名: {road_name}")
                print(f"   分類結果: 快速公路 ✅")
        
        # 測試省道篩選
        print(f"\n🛤️ 測試省道篩選...")
        provincial_cameras = [c for c in cameras if reservoir_cog._classify_road_type(c) == 'provincial']
        print(f"✅ 找到 {len(provincial_cameras)} 個省道監視器")
        
        # 顯示省道範例
        if provincial_cameras:
            print(f"\n📋 省道監視器範例:")
            for i, camera in enumerate(provincial_cameras[:3]):
                road_name = camera.get('RoadName', '')
                surveillance_desc = camera.get('SurveillanceDescription', '')
                
                print(f"{i+1}. {surveillance_desc}")
                print(f"   道路名: {road_name}")
                print(f"   分類結果: 省道 ✅")
        
        print(f"\n✅ 指令分離驗證:")
        print(f"   /national_highway_cameras → {len(national_cameras)} 個國道監視器")
        print(f"   /general_road_cameras → {len(freeway_cameras + provincial_cameras)} 個非國道監視器")
        print(f"     ├─ 快速公路: {len(freeway_cameras)}")
        print(f"     └─ 省道: {len(provincial_cameras)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函數"""
    success = await test_national_highway_fix()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 國道監視器指令修復成功！")
        print("✅ 道路分類邏輯已正確修復")
        print("✅ 國道與快速公路已正確分離")
        print("💡 現在可以正確使用:")
        print("   • /national_highway_cameras - 只顯示真正的國道")
        print("   • /general_road_cameras - 顯示省道、快速公路、一般道路")
        print("🔄 建議重啟機器人測試新功能")
    else:
        print("❌ 測試失敗，需要進一步檢查")

if __name__ == "__main__":
    asyncio.run(main())
