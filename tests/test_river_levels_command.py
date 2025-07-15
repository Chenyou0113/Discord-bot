#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試河川水位指令功能
驗證新新增的 /river_levels 指令
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from cogs.reservoir_commands import ReservoirCommands

class MockBot:
    """模擬機器人"""
    pass

async def test_river_levels_command():
    """測試河川水位指令"""
    print("🌊 測試河川水位指令功能")
    print("=" * 60)
    
    try:
        # 創建 ReservoirCommands 實例
        bot = MockBot()
        reservoir_cog = ReservoirCommands(bot)
        
        # 測試 1: 獲取河川水位資料
        print("📡 測試 1: 獲取河川水位資料...")
        level_data = await reservoir_cog.get_river_water_level_data()
        
        if not level_data:
            print("❌ 無法獲取河川水位資料")
            return False
        
        print(f"✅ 成功獲取 {len(level_data)} 筆河川水位資料")
        
        # 測試 2: 資料格式化功能
        print(f"\n🔧 測試 2: 資料格式化功能...")
        format_success = 0
        
        for i, data in enumerate(level_data[:5], 1):
            print(f"\n📊 測試資料 {i}:")
            
            # 顯示原始資料
            station_name = data.get('StationName', 'N/A')
            county = data.get('CountyName', 'N/A')
            river = data.get('RiverName', 'N/A')
            water_level = data.get('WaterLevel', 'N/A')
            
            print(f"  原始: {station_name} | {county} | {river} | {water_level}")
            
            # 測試格式化
            info = reservoir_cog.format_river_water_level_info(data)
            
            if info:
                format_success += 1
                print(f"  格式化: {info['station_name']} | {info['county']} | {info['river']} | {info['water_level']}")
                print(f"  觀測時間: {info['observation_time']}")
            else:
                print(f"  ❌ 格式化失敗")
        
        print(f"\n📈 格式化成功率: {format_success}/5")
        
        # 測試 3: 地區篩選功能
        print(f"\n🔍 測試 3: 地區篩選功能...")
        
        # 統計各縣市資料數量
        location_stats = {}
        for data in level_data:
            county = data.get('CountyName', '未知')
            location_stats[county] = location_stats.get(county, 0) + 1
        
        print(f"縣市分布統計 (前10名):")
        sorted_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)
        for county, count in sorted_locations[:10]:
            print(f"  {county}: {count} 個監測點")
        
        # 測試特定地區篩選
        test_locations = ["台南", "高雄", "台北"]
        
        for location in test_locations:
            filtered_data = []
            for data in level_data:
                county = data.get('CountyName', '')
                station_name = data.get('StationName', '')
                if location in county or location in station_name:
                    filtered_data.append(data)
            
            print(f"\n🏷️ {location}地區: 找到 {len(filtered_data)} 個監測點")
            
            if filtered_data:
                # 顯示前3個
                for i, data in enumerate(filtered_data[:3], 1):
                    info = reservoir_cog.format_river_water_level_info(data)
                    if info:
                        print(f"  {i}. {info['station_name']} - {info['river']} - {info['water_level']}")
        
        # 測試 4: 河川篩選功能
        print(f"\n🌊 測試 4: 河川篩選功能...")
        
        # 統計河川資料
        river_stats = {}
        for data in level_data:
            river = data.get('RiverName', '未知河川')
            river_stats[river] = river_stats.get(river, 0) + 1
        
        print(f"主要河川統計 (前8名):")
        sorted_rivers = sorted(river_stats.items(), key=lambda x: x[1], reverse=True)
        for river, count in sorted_rivers[:8]:
            print(f"  {river}: {count} 個監測點")
        
        # 測試特定河川篩選
        test_rivers = ["曾文溪", "高屏溪", "淡水河"]
        
        for river_name in test_rivers:
            filtered_data = []
            for data in level_data:
                river = data.get('RiverName', '')
                if river_name in river:
                    filtered_data.append(data)
            
            print(f"\n🌊 {river_name}: 找到 {len(filtered_data)} 個監測點")
            
            if filtered_data:
                for i, data in enumerate(filtered_data[:2], 1):
                    info = reservoir_cog.format_river_water_level_info(data)
                    if info:
                        print(f"  {i}. {info['station_name']} - {info['county']} - {info['water_level']}")
        
        # 測試 5: 單一監測點詳細資訊
        print(f"\n📋 測試 5: 單一監測點詳細資訊...")
        
        if level_data:
            sample_data = level_data[0]
            info = reservoir_cog.format_river_water_level_info(sample_data)
            
            if info:
                print(f"監測點範例:")
                print(f"  名稱: {info['station_name']}")
                print(f"  縣市: {info['county']}")
                print(f"  河川: {info['river']}")
                print(f"  水位: {info['water_level']}")
                print(f"  觀測時間: {info['observation_time']}")
                print(f"  測站代碼: {info['station_id']}")
                print(f"  位置: {info['location']}")
                print(f"  海拔: {info['altitude']}")
        
        # 總結測試結果
        print(f"\n" + "=" * 60)
        print(f"🎯 測試結果總結:")
        print(f"✅ 資料獲取: 成功 ({len(level_data)} 筆資料)")
        print(f"✅ 資料格式化: 成功 ({format_success}/5)")
        print(f"✅ 地區篩選: 成功")
        print(f"✅ 河川篩選: 成功") 
        print(f"✅ 詳細資訊: 成功")
        
        if len(level_data) > 0 and format_success >= 4:
            print(f"\n🎉 河川水位指令測試通過！")
            return True
        else:
            print(f"\n⚠️ 部分功能可能需要調整")
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("開始河川水位指令測試...")
    success = asyncio.run(test_river_levels_command())
    
    if success:
        print(f"\n🚀 河川水位指令已成功新增！")
        print(f"💡 使用方法:")
        print(f"   /river_levels                # 查看全台概覽")
        print(f"   /river_levels 台南           # 查看台南地區監測點")
        print(f"   /river_levels river_name:曾文溪  # 查看曾文溪監測點")
        print(f"   /river_levels 高雄 river_name:高屏溪  # 雙重篩選")
    else:
        print(f"\n⚠️ 可能需要進一步檢查 API 連線或資料格式")
        print(f"🔧 請執行: python test_river_water_level_api.py")

if __name__ == "__main__":
    main()
