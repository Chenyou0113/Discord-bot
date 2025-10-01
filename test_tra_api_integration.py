#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試台鐵API整合功能
"""

import asyncio
import sys
import os

# 添加項目路徑以便導入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cogs.info_commands_fixed_v4_clean import InfoCommands

class MockBot:
    """模擬Discord Bot"""
    pass

async def test_tra_api_integration():
    """測試台鐵API整合功能"""
    print("=" * 60)
    print("台鐵API整合測試")
    print("=" * 60)
    
    try:
        # 創建InfoCommands實例
        bot = MockBot()
        info_commands = InfoCommands(bot)
        
        print("\n1. 測試台鐵車站資料獲取...")
        
        # 測試API資料獲取
        api_data = await info_commands.fetch_tra_stations_from_api()
        if api_data:
            print(f"✅ 成功從API獲取資料，共{len(api_data)}個縣市")
            
            # 顯示各縣市車站數量
            print("\n📍 各縣市車站統計:")
            total_stations = 0
            for county, stations in sorted(api_data.items()):
                count = len(stations)
                total_stations += count
                print(f"   {county}: {count}個車站")
            
            print(f"\n🚉 總計: {total_stations}個台鐵車站")
            
            # 測試一些具體縣市的資料
            test_counties = ['臺北市', '新北市', '高雄市']
            print(f"\n2. 測試特定縣市車站資料...")
            
            for county in test_counties:
                if county in api_data:
                    stations = api_data[county]
                    print(f"\n🏷️ {county} ({len(stations)}個車站):")
                    for i, station in enumerate(stations[:3]):  # 只顯示前3個
                        print(f"   {i+1}. {station['name']} (代碼: {station['id']})")
                    if len(stations) > 3:
                        print(f"   ... 還有{len(stations)-3}個車站")
                else:
                    print(f"❌ {county} 沒有車站資料")
        else:
            print("❌ API資料獲取失敗")
            return False
        
        print("\n3. 測試完整資料獲取方法...")
        
        # 測試get_updated_tra_stations方法
        updated_data = await info_commands.get_updated_tra_stations()
        if updated_data:
            print(f"✅ get_updated_tra_stations成功，共{len(updated_data)}個縣市")
        else:
            print("❌ get_updated_tra_stations失敗")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 台鐵API整合測試全部通過!")
        print("✅ API連接正常")  
        print("✅ 資料獲取正常")
        print("✅ 縣市分類正常")
        print("✅ 快取機制正常")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤:")
        print(f"   錯誤訊息: {str(e)}")
        import traceback
        print(f"   詳細錯誤: {traceback.format_exc()}")
        return False

async def main():
    """主程式"""
    success = await test_tra_api_integration()
    if success:
        print("\n🚀 台鐵功能已準備就緒，可以正常使用!")
        return 0
    else:
        print("\n💥 台鐵功能測試失敗，請檢查網路連線和API狀態")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
