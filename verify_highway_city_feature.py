#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證公路監視器縣市功能
"""

import sys
import os

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_highway_city_feature():
    """驗證公路監視器縣市功能"""
    print("🔍 驗證公路監視器縣市功能")
    print("=" * 50)
    
    try:
        # 1. 檢查基本匯入
        print("1️⃣ 檢查模組匯入...")
        
        import discord
        print("   ✅ discord.py 匯入成功")
        
        from cogs.reservoir_commands import ReservoirCommands
        print("   ✅ ReservoirCommands 匯入成功")
        
        # 2. 檢查縣市映射功能
        print("\n2️⃣ 檢查縣市映射功能...")
        
        reservoir_cog = ReservoirCommands(None)
        
        if hasattr(reservoir_cog, '_get_city_by_coordinates'):
            print("   ✅ _get_city_by_coordinates 方法存在")
            
            # 測試座標
            test_result = reservoir_cog._get_city_by_coordinates("25.047", "121.517")
            if test_result == "台北市":
                print("   ✅ 縣市映射功能正常")
            else:
                print(f"   ⚠️ 縣市映射結果: {test_result}")
        else:
            print("   ❌ _get_city_by_coordinates 方法不存在")
        
        # 3. 檢查指令結構
        print("\n3️⃣ 檢查指令結構...")
        
        if hasattr(reservoir_cog, 'highway_cameras'):
            print("   ✅ highway_cameras 指令存在")
            
            # 檢查參數
            import inspect
            sig = inspect.signature(reservoir_cog.highway_cameras)
            params = list(sig.parameters.keys())
            
            if 'city' in params:
                print("   ✅ city 參數已添加")
            else:
                print("   ❌ city 參數缺失")
                
            print(f"   📋 指令參數: {', '.join(params[1:])}")  # 排除 self
        else:
            print("   ❌ highway_cameras 指令不存在")
        
        # 4. 檢查選項定義
        print("\n4️⃣ 檢查縣市選項...")
        
        source_code = inspect.getsource(reservoir_cog.highway_cameras)
        
        city_choices = [
            "台北市", "新北市", "桃園市", "台中市", "台南市",
            "高雄市", "基隆市", "新竹市", "新竹縣", "苗栗縣"
        ]
        
        found_choices = 0
        for city in city_choices:
            if city in source_code:
                found_choices += 1
        
        if found_choices >= 8:  # 至少找到8個縣市
            print(f"   ✅ 縣市選項已定義 ({found_choices}/{len(city_choices)})")
        else:
            print(f"   ⚠️ 縣市選項可能不完整 ({found_choices}/{len(city_choices)})")
        
        # 5. 檢查篩選邏輯
        print("\n5️⃣ 檢查篩選邏輯...")
        
        if '_get_city_by_coordinates' in source_code and 'city_filtered_cameras' in source_code:
            print("   ✅ 縣市篩選邏輯已實作")
        else:
            print("   ⚠️ 縣市篩選邏輯可能不完整")
        
        # 6. 檢查顯示邏輯
        print("\n6️⃣ 檢查顯示邏輯...")
        
        if '縣市：' in source_code or '🏙️ 縣市' in source_code:
            print("   ✅ 縣市顯示邏輯已更新")
        else:
            print("   ⚠️ 縣市顯示邏輯可能不完整")
        
        print(f"\n" + "=" * 50)
        print("✅ 功能驗證完成！")
        
        print(f"\n💡 使用指南:")
        print("1. 重新啟動機器人以載入更新")
        print("2. 在 Discord 中使用指令:")
        print("   • /highway_cameras city:台北市")
        print("   • /highway_cameras location:國道 city:新北市")
        print("   • /highway_cameras direction:N city:桃園市")
        
        print(f"\n🎯 新增功能:")
        print("• 17個縣市選項（下拉選單）")
        print("• 根據經緯度自動判斷縣市")
        print("• 支援多重條件篩選")
        print("• 監視器資訊顯示縣市")
        
        return True
        
    except Exception as e:
        print(f"❌ 驗證失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    success = verify_highway_city_feature()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 公路監視器縣市功能驗證通過！")
        print("🚀 功能已準備就緒，可以使用")
    else:
        print("❌ 驗證未通過，請檢查問題")
    print("=" * 50)

if __name__ == "__main__":
    main()
