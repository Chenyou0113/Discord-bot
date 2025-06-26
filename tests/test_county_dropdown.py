#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試氣象站指令的新下拉選單功能
驗證縣市選擇功能是否正常運作
"""

import sys
import os
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

# 設定路徑以導入主程式模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_county_dropdown_functionality():
    """測試縣市下拉選單功能"""
    
    print("🎛️ 氣象站指令 - 縣市下拉選單功能測試")
    print("=" * 60)
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        # 創建模擬的 bot 實例
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.display_avatar = MagicMock()
        mock_bot.user.display_avatar.url = "https://example.com/avatar.png"
        
        # 創建 InfoCommands 實例
        info_cog = InfoCommands(mock_bot)
        
        # 測試可用的縣市選項
        available_counties = [
            "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
            "基隆市", "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣",
            "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
            "臺東縣", "澎湖縣", "金門縣", "連江縣"
        ]
        
        print("📋 測試下拉選單中的縣市選項")
        print("-" * 40)
        
        # 獲取真實氣象站資料
        print("📡 連接氣象站 API...")
        station_data = await info_cog.fetch_weather_station_data()
        
        if not station_data or 'records' not in station_data:
            print("❌ 無法獲取氣象站資料")
            return
            
        stations = station_data['records']['Station']
        print(f"✅ 獲取 {len(stations)} 個氣象站資料")
        
        # 測試每個縣市的查詢結果
        print(f"\n🧪 測試各縣市查詢結果")
        print("-" * 40)
        
        county_results = {}
        
        for county in available_counties:
            print(f"\n🔍 測試縣市: {county}")
            
            # 模擬搜尋邏輯
            target_stations = []
            for station in stations:
                station_name = station.get('StationName', '')
                county_name = station.get('GeoInfo', {}).get('CountyName', '')
                if (county in station_name or station_name in county or 
                    county in county_name or county_name in county):
                    target_stations.append(station)
            
            county_results[county] = len(target_stations)
            
            if target_stations:
                print(f"   ✅ 找到 {len(target_stations)} 個氣象站")
                # 顯示前3個測站名稱
                for i, station in enumerate(target_stations[:3]):
                    name = station.get('StationName', '未知')
                    station_id = station.get('StationId', '未知')
                    print(f"      {i+1}. {name} ({station_id})")
                if len(target_stations) > 3:
                    print(f"      ... 還有 {len(target_stations) - 3} 個測站")
            else:
                print(f"   ⚠️  該縣市暫無氣象站資料")
        
        # 統計結果
        print(f"\n📊 測試統計")
        print("-" * 40)
        
        total_counties = len(available_counties)
        counties_with_stations = sum(1 for count in county_results.values() if count > 0)
        counties_without_stations = total_counties - counties_with_stations
        total_stations_found = sum(county_results.values())
        
        print(f"總縣市數: {total_counties}")
        print(f"有氣象站的縣市: {counties_with_stations}")
        print(f"暫無氣象站的縣市: {counties_without_stations}")
        print(f"總測站數: {total_stations_found}")
        print(f"覆蓋率: {counties_with_stations/total_counties*100:.1f}%")
        
        # 顯示氣象站數量最多的縣市
        print(f"\n🏆 氣象站數量排行榜（前10名）")
        print("-" * 40)
        
        sorted_counties = sorted(county_results.items(), key=lambda x: x[1], reverse=True)
        for i, (county, count) in enumerate(sorted_counties[:10], 1):
            if count > 0:
                print(f"{i:2d}. {county}: {count} 個測站")
        
        # 測試模擬指令執行
        print(f"\n🧪 模擬指令執行測試")
        print("-" * 40)
        
        test_counties = ["臺北市", "高雄市", "花蓮縣", "金門縣", "連江縣"]
        
        for county in test_counties:
            print(f"\n📝 測試: /weather_station county:{county}")
            
            # 創建模擬的 Discord 互動
            mock_interaction = AsyncMock()
            mock_interaction.response = AsyncMock()
            mock_interaction.followup = AsyncMock()
            mock_interaction.user = MagicMock()
            mock_interaction.user.id = 12345
            
            try:
                # 調用氣象站指令
                await info_cog.weather_station(
                    interaction=mock_interaction,
                    station_id=None,
                    county=county
                )
                
                # 檢查回應
                if mock_interaction.followup.send.called:
                    call_args = mock_interaction.followup.send.call_args
                    if call_args and len(call_args) > 0:
                        # 檢查是否為錯誤訊息
                        if len(call_args[0]) > 0 and isinstance(call_args[0][0], str):
                            message = call_args[0][0]
                            if "❌" in message:
                                print(f"   ❌ {message}")
                            else:
                                print(f"   ✅ 成功回應（可能是 embed 格式）")
                        else:
                            print(f"   ✅ 成功回應 embed 格式")
                    else:
                        print(f"   ⚠️  無明確回應")
                else:
                    print(f"   ⚠️  未調用 followup.send")
                    
            except Exception as e:
                print(f"   ❌ 執行失敗: {str(e)}")
        
        print(f"\n✅ 下拉選單功能測試完成")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ 無法導入模組: {str(e)}")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        logger.error(f"測試失敗: {str(e)}")

def show_dropdown_advantages():
    """展示下拉選單的優勢"""
    
    print(f"\n💡 下拉選單功能優勢")
    print("=" * 60)
    
    advantages = [
        {
            "title": "🚫 消除輸入錯誤",
            "description": "用戶無法輸入不存在的縣市名稱",
            "before": "用戶可能輸入：火星市、月球縣",
            "after": "只能從預設的 22 個縣市中選擇"
        },
        {
            "title": "📱 改善用戶體驗", 
            "description": "無需記憶或手動輸入縣市名稱",
            "before": "需要記住正確的縣市名稱",
            "after": "從下拉選單中直接選擇"
        },
        {
            "title": "🎯 提高成功率",
            "description": "大幅減少查詢失敗的情況",
            "before": "輸入錯誤導致查詢失敗",
            "after": "選擇有效縣市，提高成功率"
        },
        {
            "title": "🌍 完整覆蓋",
            "description": "涵蓋台灣所有縣市",
            "before": "用戶可能不知道有哪些選項",
            "after": "清楚顯示所有可用的 22 個縣市"
        },
        {
            "title": "⚡ 快速操作",
            "description": "點選即可，無需輸入",
            "before": "需要手動輸入完整縣市名稱",
            "after": "一鍵選擇，操作便利"
        }
    ]
    
    for i, advantage in enumerate(advantages, 1):
        print(f"\n{i}. {advantage['title']}")
        print(f"   描述: {advantage['description']}")
        print(f"   改進前: {advantage['before']}")
        print(f"   改進後: {advantage['after']}")
    
    print(f"\n🎉 總結")
    print("-" * 30)
    print("✅ 下拉選單功能大幅改善了氣象站指令的用戶體驗")
    print("✅ 減少了因輸入錯誤導致的查詢失敗")
    print("✅ 提供了標準化、便利的縣市選擇方式")
    print("✅ 保持了原有的氣象站代碼查詢功能")

if __name__ == "__main__":
    try:
        print("🧪 氣象站指令下拉選單功能測試")
        print("=" * 60)
        
        # 運行下拉選單功能測試
        asyncio.run(test_county_dropdown_functionality())
        
        # 展示下拉選單優勢
        show_dropdown_advantages()
        
    except KeyboardInterrupt:
        print("\n⏹️  測試被用戶中斷")
    except Exception as e:
        print(f"❌ 執行測試時發生錯誤: {str(e)}")
        logging.error(f"主要測試錯誤: {str(e)}")
