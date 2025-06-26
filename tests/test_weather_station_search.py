#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的氣象站測試 - 直接測試查詢不到地區的處理邏輯
"""

import sys
import os
import asyncio
import logging

# 設定路徑以導入主程式模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_weather_station_search_logic():
    """測試氣象站搜尋邏輯"""
    
    print("🔍 氣象站搜尋邏輯測試")
    print("=" * 50)
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock
        
        # 創建模擬的 bot 和 cog
        mock_bot = MagicMock()
        info_cog = InfoCommands(mock_bot)
        
        # 獲取真實的氣象站資料
        print("📡 獲取真實氣象站資料...")
        station_data = await info_cog.fetch_weather_station_data()
        
        if not station_data or 'records' not in station_data:
            print("❌ 無法獲取氣象站資料")
            return
            
        stations = station_data['records']['Station']
        print(f"✅ 成功獲取 {len(stations)} 個氣象站資料")
        
        # 測試查詢不存在的地區
        print(f"\n🧪 測試查詢不存在的地區")
        print("-" * 30)
        
        test_locations = [
            "火星市",
            "月球基地", 
            "不存在的地方",
            "XYZ市",
            "南極洲",
            "虛構城市",
            "外太空",
            "阿凡達星球"
        ]
        
        for location in test_locations:
            print(f"\n🔍 測試地區: '{location}'")
            
            # 模擬指令中的搜尋邏輯
            target_stations = []
            for station in stations:
                station_name = station.get('StationName', '')
                county_name = station.get('GeoInfo', {}).get('CountyName', '')
                if (location in station_name or station_name in location or 
                    location in county_name or county_name in location):
                    target_stations.append(station)
            
            if target_stations:
                print(f"   ✅ 找到 {len(target_stations)} 個相關測站:")
                for station in target_stations[:3]:  # 只顯示前3個
                    name = station.get('StationName', '未知')
                    station_id = station.get('StationId', '未知')
                    county = station.get('GeoInfo', {}).get('CountyName', '未知')
                    print(f"      - {name} ({station_id}) - {county}")
            else:
                print(f"   ❌ 找不到相關測站")
                print(f"   💬 系統會回應: '❌ 找不到 {location} 地區的氣象站資料'")
        
        # 測試查詢不存在的氣象站代碼
        print(f"\n🧪 測試查詢不存在的氣象站代碼")
        print("-" * 30)
        
        test_station_ids = [
            "999999",
            "000000", 
            "ABCDEF",
            "123ABC",
            "NOTFOUND",
            "",
            "   ",
            "火星001"
        ]
        
        for station_id in test_station_ids:
            print(f"\n🔍 測試代碼: '{station_id}'")
            
            # 模擬指令中的搜尋邏輯
            target_station = None
            for station in stations:
                if station.get('StationId') == station_id:
                    target_station = station
                    break
            
            if target_station:
                name = target_station.get('StationName', '未知')
                county = target_station.get('GeoInfo', {}).get('CountyName', '未知')
                print(f"   ✅ 找到測站: {name} - {county}")
            else:
                print(f"   ❌ 找不到測站")
                print(f"   💬 系統會回應: '❌ 找不到測站代碼 {station_id} 的觀測資料'")
        
        # 顯示實際存在的一些氣象站資料作為對比
        print(f"\n📊 實際存在的氣象站範例（供對比）")
        print("-" * 30)
        
        example_stations = stations[:10]  # 前10個
        for i, station in enumerate(example_stations, 1):
            name = station.get('StationName', '未知')
            station_id = station.get('StationId', '未知')
            county = station.get('GeoInfo', {}).get('CountyName', '未知')
            town = station.get('GeoInfo', {}).get('TownName', '')
            print(f"{i:2d}. {name} ({station_id}) - {county} {town}")
        
        # 測試部分匹配的搜尋
        print(f"\n🧪 測試部分匹配搜尋")
        print("-" * 30)
        
        partial_searches = ["台北", "高雄", "台中", "花蓮", "山"]
        
        for search_term in partial_searches:
            print(f"\n🔍 搜尋關鍵字: '{search_term}'")
            
            matches = []
            for station in stations:
                station_name = station.get('StationName', '')
                county_name = station.get('GeoInfo', {}).get('CountyName', '')
                if (search_term in station_name or station_name in search_term or 
                    search_term in county_name or county_name in search_term):
                    matches.append(station)
            
            print(f"   📍 找到 {len(matches)} 個相關測站")
            if matches:
                for station in matches[:5]:  # 只顯示前5個
                    name = station.get('StationName', '未知')
                    county = station.get('GeoInfo', {}).get('CountyName', '未知')
                    print(f"      - {name} - {county}")
                if len(matches) > 5:
                    print(f"      ... 還有 {len(matches) - 5} 個")
        
        print(f"\n✅ 測試完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        logger.error(f"測試失敗: {str(e)}")

def demonstrate_expected_responses():
    """展示預期的系統回應"""
    
    print(f"\n📱 預期的 Discord 回應訊息")
    print("=" * 50)
    
    scenarios = [
        {
            "input": "/weather_station location:火星市",
            "response": "❌ 找不到 火星市 地區的氣象站資料"
        },
        {
            "input": "/weather_station station_id:999999",
            "response": "❌ 找不到測站代碼 999999 的觀測資料"
        },
        {
            "input": "/weather_station location:南極洲",
            "response": "❌ 找不到 南極洲 地區的氣象站資料"
        },
        {
            "input": "/weather_station location:台北",
            "response": "✅ 找到台北相關的氣象站資料（會顯示詳細資訊或翻頁選單）"
        },
        {
            "input": "/weather_station station_id:466920",
            "response": "✅ 顯示臺北測站的詳細觀測資料"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. 用戶輸入: {scenario['input']}")
        print(f"   Bot 回應: {scenario['response']}")
    
    print(f"\n💡 說明:")
    print("   - 當找不到指定地區時，會顯示友善的錯誤訊息")
    print("   - 錯誤訊息包含用戶輸入的地區名稱，方便確認")
    print("   - 系統不會崩潰，會優雅地處理無效輸入")
    print("   - 對於有效的查詢，會正常顯示氣象站資料")

if __name__ == "__main__":
    try:
        print("🌤️  氣象站指令 - 查詢不到地區的處理測試")
        print("=" * 60)
        
        # 運行搜尋邏輯測試
        asyncio.run(test_weather_station_search_logic())
        
        # 展示預期回應
        demonstrate_expected_responses()
        
    except KeyboardInterrupt:
        print("\n⏹️  測試被用戶中斷")
    except Exception as e:
        print(f"❌ 執行測試時發生錯誤: {str(e)}")
        logging.error(f"主要測試錯誤: {str(e)}")
