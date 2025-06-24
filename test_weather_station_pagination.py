#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
氣象站翻頁功能測試腳本
測試新增的翻頁按鈕功能
"""

import asyncio
import sys
import os

# 添加專案根目錄到 sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from cogs.info_commands_fixed_v4_clean import InfoCommands, WeatherStationView
from unittest.mock import AsyncMock, MagicMock

class MockBot:
    """模擬 Discord Bot"""
    def __init__(self):
        self.session = None
        self.loop = asyncio.get_event_loop()

async def test_weather_station_pagination():
    """測試氣象站翻頁功能"""
    print("🌡️ 測試氣象站翻頁功能...")
    print("=" * 50)
    
    # 建立模擬環境
    mock_bot = MockBot()
    cog = InfoCommands(mock_bot)
    
    # 初始化 session
    await cog.init_aiohttp_session()
    
    try:
        # 獲取氣象站資料
        print("  ▶ 獲取氣象站資料...")
        weather_data = await cog.fetch_weather_station_data()
        
        if weather_data and 'records' in weather_data:
            records = weather_data['records']
            stations = records.get('Station', [])
            print(f"  ✅ 獲取到 {len(stations)} 個氣象站資料")
            
            if len(stations) > 0:
                # 測試篩選台北地區的測站
                print("  ▶ 測試地區篩選（台北）...")
                taipei_stations = []
                for station in stations:
                    station_name = station.get('StationName', '')
                    county_name = station.get('GeoInfo', {}).get('CountyName', '')
                    if ('台北' in station_name or '台北' in county_name or 
                        '臺北' in station_name or '臺北' in county_name):
                        taipei_stations.append(station)
                
                print(f"  📊 找到 {len(taipei_stations)} 個台北地區測站")
                
                if len(taipei_stations) > 5:
                    # 測試翻頁功能
                    print("  ▶ 測試翻頁 View 建立...")
                    view = WeatherStationView(
                        cog=cog,
                        user_id=12345,  # 模擬用戶ID
                        stations=taipei_stations,
                        query_type="multiple",
                        location="台北"
                    )
                    
                    print(f"  📄 總頁數: {view.total_pages}")
                    print(f"  📄 每頁顯示: {view.stations_per_page} 個測站")
                    
                    # 測試第一頁
                    print("  ▶ 測試第一頁 Embed 生成...")
                    embed_page1 = view._create_current_page_embed()
                    if embed_page1:
                        print("  ✅ 第一頁 Embed 生成成功")
                        print(f"     標題: {embed_page1.title}")
                        print(f"     欄位數: {len(embed_page1.fields)}")
                    
                    # 測試切換到第二頁（如果有的話）
                    if view.total_pages > 1:
                        print("  ▶ 測試切換到第二頁...")
                        view.current_page = 1
                        embed_page2 = view._create_current_page_embed()
                        if embed_page2:
                            print("  ✅ 第二頁 Embed 生成成功")
                            print(f"     標題: {embed_page2.title}")
                            print(f"     欄位數: {len(embed_page2.fields)}")
                        
                        # 測試回到第一頁
                        view.current_page = 0
                        print("  ✅ 頁面切換測試完成")
                    
                    print("  ✅ 翻頁功能測試完成")
                else:
                    print("  ⚠️  台北地區測站數量不足，無法測試翻頁功能")
                
                # 測試單一測站
                print("  ▶ 測試單一測站顯示...")
                single_station = stations[0]
                single_embed = cog._create_single_station_embed(single_station)
                if single_embed:
                    print("  ✅ 單一測站 Embed 生成成功")
                    station_name = single_station.get('StationName', '未知')
                    print(f"     測站名稱: {station_name}")
                
                # 測試全台概況
                print("  ▶ 測試全台概況顯示...")
                overview_embed = cog._create_overview_embed(stations)
                if overview_embed:
                    print("  ✅ 全台概況 Embed 生成成功")
                    print(f"     標題: {overview_embed.title}")
                    print(f"     欄位數: {len(overview_embed.fields)}")
            else:
                print("  ❌ 未獲取到氣象站資料")
        else:
            print("  ❌ 氣象站資料獲取失敗")
            
    except Exception as e:
        print(f"  ❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理 session
        await cog.cog_unload()

async def test_view_functionality():
    """測試 View 功能"""
    print("\n🔘 測試 View 按鈕功能...")
    print("=" * 50)
    
    try:
        # 建立測試資料
        test_stations = []
        for i in range(12):  # 建立12個測試測站
            test_stations.append({
                'StationId': f'TEST{i:03d}',
                'StationName': f'測試測站{i+1}',
                'WeatherElement': {
                    'AirTemperature': 20 + i,
                    'RelativeHumidity': 60 + i,
                    'Weather': '晴'
                },
                'GeoInfo': {
                    'CountyName': '台北市',
                    'TownName': f'測試區{i+1}'
                },
                'ObsTime': {
                    'DateTime': '2025-06-24T12:00:00+08:00'
                }
            })
        
        print(f"  📊 建立 {len(test_stations)} 個測試測站")
        
        # 建立 View
        view = WeatherStationView(
            cog=None,  # 測試用，不需要實際 cog
            user_id=12345,
            stations=test_stations,
            query_type="multiple",
            location="台北"
        )
        
        print(f"  📄 View 設定: {view.total_pages} 頁，每頁 {view.stations_per_page} 個測站")
        
        # 測試按鈕狀態更新
        print("  ▶ 測試按鈕狀態更新...")
        view._update_buttons()
        button_count = len(view.children)
        print(f"  🔘 按鈕數量: {button_count}")
        
        # 測試頁面邊界
        print("  ▶ 測試頁面邊界...")
        print(f"     當前頁面: {view.current_page}")
        print(f"     總頁數: {view.total_pages}")
        print(f"     是否第一頁: {view.current_page == 0}")
        print(f"     是否最後一頁: {view.current_page >= view.total_pages - 1}")
        
        print("  ✅ View 功能測試完成")
        
    except Exception as e:
        print(f"  ❌ View 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """主要測試函數"""
    print("🚀 開始氣象站翻頁功能測試...")
    print("=" * 60)
    
    await test_weather_station_pagination()
    await test_view_functionality()
    
    print("\n" + "=" * 60)
    print("✨ 氣象站翻頁功能測試完成！")

if __name__ == "__main__":
    asyncio.run(main())
