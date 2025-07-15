#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試公路監視器縣市選項功能
"""

import sys
import os
import asyncio

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_city_mapper():
    """測試縣市映射功能"""
    print("🗺️ 測試縣市映射功能")
    print("=" * 40)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立測試實例
        reservoir_cog = ReservoirCommands(None)
        
        # 測試一些已知座標
        test_coordinates = [
            ("25.047", "121.517", "台北市"),  # 台北101
            ("22.627", "120.301", "高雄市"),  # 高雄市中心
            ("24.147", "120.674", "台中市"),  # 台中市中心
            ("23.000", "120.227", "台南市"),  # 台南市中心
            ("24.956", "121.225", "桃園市"),  # 桃園市中心
            ("25.128", "121.739", "基隆市"),  # 基隆市中心
        ]
        
        print("🧪 測試座標映射:")
        success_count = 0
        
        for lat, lon, expected_city in test_coordinates:
            result_city = reservoir_cog._get_city_by_coordinates(lat, lon)
            
            if result_city == expected_city:
                print(f"   ✅ ({lat}, {lon}) -> {result_city}")
                success_count += 1
            else:
                print(f"   ❌ ({lat}, {lon}) -> {result_city} (預期: {expected_city})")
        
        print(f"\n📊 測試結果: {success_count}/{len(test_coordinates)} 通過")
        
        return success_count == len(test_coordinates)
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_highway_api():
    """測試公路監視器 API"""
    print(f"\n🛣️ 測試公路監視器 API")
    print("=" * 40)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立測試實例
        reservoir_cog = ReservoirCommands(None)
        
        print("📡 正在獲取監視器資料...")
        cameras = await reservoir_cog._get_highway_cameras()
        
        if not cameras:
            print("❌ 無法獲取監視器資料")
            return False
        
        print(f"✅ 成功獲取 {len(cameras)} 個監視器")
        
        # 測試縣市分布
        print(f"\n🏙️ 分析縣市分布:")
        city_count = {}
        
        for camera in cameras[:100]:  # 只分析前100個
            lat = camera.get('PositionLat')
            lon = camera.get('PositionLon')
            
            if lat and lon:
                city = reservoir_cog._get_city_by_coordinates(lat, lon)
                if city:
                    city_count[city] = city_count.get(city, 0) + 1
        
        # 顯示結果
        for city, count in sorted(city_count.items(), key=lambda x: x[1], reverse=True):
            print(f"   {city}: {count} 個")
        
        print(f"\n💡 測試建議:")
        print("   可以使用以下縣市進行測試:")
        for city in list(city_count.keys())[:5]:
            print(f"   • /highway_cameras city:{city}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_command_options():
    """測試指令選項"""
    print(f"\n🎯 測試指令選項")
    print("=" * 40)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 檢查指令是否有縣市選項
        reservoir_cog = ReservoirCommands(None)
        
        if hasattr(reservoir_cog, 'highway_cameras'):
            print("✅ highway_cameras 指令存在")
            
            # 檢查原始碼中是否包含縣市相關邏輯
            import inspect
            source = inspect.getsource(reservoir_cog.highway_cameras)
            
            if 'city' in source:
                print("✅ 包含縣市參數邏輯")
            else:
                print("❌ 缺少縣市參數邏輯")
            
            if '_get_city_by_coordinates' in source:
                print("✅ 使用縣市映射功能")
            else:
                print("❌ 未使用縣市映射功能")
            
            return True
        else:
            print("❌ highway_cameras 指令不存在")
            return False
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

async def main():
    """主函數"""
    print("🧪 公路監視器縣市功能測試")
    print("=" * 50)
    
    # 測試縣市映射
    mapper_ok = await test_city_mapper()
    
    # 測試 API
    api_ok = await test_highway_api()
    
    # 測試指令選項
    command_ok = test_command_options()
    
    print(f"\n" + "=" * 50)
    print("📊 測試總結:")
    print(f"   縣市映射: {'✅ 通過' if mapper_ok else '❌ 失敗'}")
    print(f"   API 測試: {'✅ 通過' if api_ok else '❌ 失敗'}")
    print(f"   指令選項: {'✅ 通過' if command_ok else '❌ 失敗'}")
    
    if all([mapper_ok, api_ok, command_ok]):
        print("\n🎉 所有測試通過！")
        print("💡 現在可以在 Discord 中使用以下指令:")
        print("   • /highway_cameras city:台北市")
        print("   • /highway_cameras location:國道一號 city:新北市")
        print("   • /highway_cameras direction:N city:桃園市")
    else:
        print("\n❌ 部分測試失敗，請檢查錯誤訊息")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
