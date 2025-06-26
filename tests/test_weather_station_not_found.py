#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試氣象站指令 - 查詢不到地區的處理
測試各種無效的地區名稱和氣象站代碼
"""

import sys
import os
import asyncio
import logging
import discord
from unittest.mock import AsyncMock, MagicMock, patch

# 設定路徑以導入主程式模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_weather_station_not_found():
    """測試氣象站指令查詢不到地區的情況"""
    
    print("🔍 開始測試氣象站指令 - 查詢不到地區的處理")
    print("=" * 60)
    
    try:
        # 導入必要的模組
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        # 創建模擬的 bot 實例
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.display_avatar = MagicMock()
        mock_bot.user.display_avatar.url = "https://example.com/avatar.png"
        
        # 創建 InfoCommands 實例
        info_cog = InfoCommands(mock_bot)
        
        # 模擬正常的氣象站資料（但不包含測試地區）
        mock_weather_data = {
            "records": {
                "Station": [
                    {
                        "StationId": "466920",
                        "StationName": "臺北",
                        "GeoInfo": {
                            "CountyName": "臺北市",
                            "TownName": "中正區"
                        },
                        "WeatherElement": {
                            "AirTemperature": "25.5",
                            "RelativeHumidity": "65",
                            "AirPressure": "1013.2"
                        },
                        "ObsTime": {
                            "DateTime": "2025-06-25T10:00:00+08:00"
                        }
                    },
                    {
                        "StationId": "467490",
                        "StationName": "高雄",
                        "GeoInfo": {
                            "CountyName": "高雄市",
                            "TownName": "前金區"
                        },
                        "WeatherElement": {
                            "AirTemperature": "28.3",
                            "RelativeHumidity": "72",
                            "AirPressure": "1012.8"
                        },
                        "ObsTime": {
                            "DateTime": "2025-06-25T10:00:00+08:00"
                        }
                    }
                ]
            }
        }
        
        # 模擬 fetch_weather_station_data 方法
        async def mock_fetch_weather_station_data():
            return mock_weather_data
        
        info_cog.fetch_weather_station_data = mock_fetch_weather_station_data
        
        # 測試案例
        test_cases = [
            {
                "description": "不存在的地區名稱",
                "location": "火星市",
                "station_id": None,
                "expected_message": "❌ 找不到 火星市 地區的氣象站資料"
            },
            {
                "description": "不存在的氣象站代碼",
                "location": None,
                "station_id": "999999",
                "expected_message": "❌ 找不到測站代碼 999999 的觀測資料"
            },
            {
                "description": "完全不相關的地區名稱",
                "location": "南極洲",
                "station_id": None,
                "expected_message": "❌ 找不到 南極洲 地區的氣象站資料"
            },
            {
                "description": "錯誤的地區拼寫",
                "location": "台北市中山區忠孝東路",
                "station_id": None,
                "expected_message": None  # 可能會找到台北的資料
            },
            {
                "description": "空白的氣象站代碼",
                "location": None,
                "station_id": "",
                "expected_message": "❌ 找不到測站代碼  的觀測資料"
            }
        ]
        
        # 執行測試案例
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 測試案例 {i}: {test_case['description']}")
            print(f"   參數 - 地區: '{test_case['location']}', 代碼: '{test_case['station_id']}'")
            
            # 創建模擬的 Discord 互動
            mock_interaction = AsyncMock()
            mock_interaction.response = AsyncMock()
            mock_interaction.followup = AsyncMock()
            
            # 調用氣象站指令
            try:
                await info_cog.weather_station(
                    interaction=mock_interaction,
                    station_id=test_case['station_id'],
                    location=test_case['location']
                )
                
                # 檢查回應
                if mock_interaction.followup.send.called:
                    sent_message = mock_interaction.followup.send.call_args
                    if sent_message and len(sent_message) > 0:
                        # 檢查是否為字串訊息
                        if isinstance(sent_message[0][0], str):
                            actual_message = sent_message[0][0]
                            print(f"   ✅ 回應訊息: {actual_message}")
                            
                            if test_case['expected_message']:
                                if test_case['expected_message'] in actual_message:
                                    print(f"   ✅ 預期結果正確")
                                else:
                                    print(f"   ❌ 預期: {test_case['expected_message']}")
                                    print(f"   ❌ 實際: {actual_message}")
                        else:
                            # 可能是 embed 訊息
                            print(f"   📋 回應類型: {type(sent_message[0][0])}")
                            if test_case['description'] == "錯誤的地區拼寫":
                                print(f"   ✅ 找到相關地區資料（正常行為）")
                else:
                    print(f"   ⚠️  無回應訊息")
                    
            except Exception as e:
                print(f"   ❌ 測試失敗: {str(e)}")
                logger.error(f"測試案例 {i} 失敗: {str(e)}")
        
        # 測試特殊情況
        print(f"\n🔧 測試特殊情況")
        print("-" * 40)
        
        # 測試 API 無回應的情況
        print("📝 測試 API 無回應情況")
        
        async def mock_fetch_no_data():
            return None
        
        info_cog.fetch_weather_station_data = mock_fetch_no_data
        
        mock_interaction = AsyncMock()
        mock_interaction.response = AsyncMock()
        mock_interaction.followup = AsyncMock()
        
        await info_cog.weather_station(
            interaction=mock_interaction,
            station_id=None,
            location="台北"
        )
        
        if mock_interaction.followup.send.called:
            sent_message = mock_interaction.followup.send.call_args[0][0]
            print(f"   ✅ API 無回應時的訊息: {sent_message}")
        
        # 測試資料格式異常的情況
        print("\n📝 測試資料格式異常情況")
        
        async def mock_fetch_invalid_format():
            return {"invalid": "format"}
        
        info_cog.fetch_weather_station_data = mock_fetch_invalid_format
        
        mock_interaction = AsyncMock()
        mock_interaction.response = AsyncMock()
        mock_interaction.followup = AsyncMock()
        
        await info_cog.weather_station(
            interaction=mock_interaction,
            station_id=None,
            location="台北"
        )
        
        if mock_interaction.followup.send.called:
            sent_message = mock_interaction.followup.send.call_args[0][0]
            print(f"   ✅ 資料格式異常時的訊息: {sent_message}")
        
        print(f"\n✅ 測試完成")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ 無法導入模組: {str(e)}")
        print("請確認 cogs/info_commands_fixed_v4_clean.py 存在")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        logger.error(f"測試失敗: {str(e)}")

async def test_real_weather_station_command():
    """測試真實的氣象站指令"""
    print(f"\n🌐 測試真實氣象站 API 回應")
    print("-" * 40)
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.display_avatar = MagicMock()
        mock_bot.user.display_avatar.url = "https://example.com/avatar.png"
        
        info_cog = InfoCommands(mock_bot)
        
        # 測試真實 API 調用
        print("📡 呼叫真實氣象站 API...")
        real_data = await info_cog.fetch_weather_station_data()
        
        if real_data:
            print("✅ 成功獲取真實資料")
            if 'records' in real_data and 'Station' in real_data['records']:
                stations = real_data['records']['Station']
                print(f"📊 共獲取 {len(stations)} 個氣象站資料")
                
                # 顯示前幾個氣象站名稱
                print("🏢 可用的氣象站:")
                for i, station in enumerate(stations[:10]):
                    station_name = station.get('StationName', '未知')
                    station_id = station.get('StationId', '未知')
                    county = station.get('GeoInfo', {}).get('CountyName', '未知')
                    print(f"   {i+1}. {station_name} ({station_id}) - {county}")
                
                if len(stations) > 10:
                    print(f"   ... 還有 {len(stations) - 10} 個氣象站")
                
                # 測試查詢不存在的地區
                print(f"\n🔍 測試查詢不存在的地區")
                
                test_locations = ["火星", "月球", "不存在的地方", "XYZ市"]
                
                for location in test_locations:
                    found_stations = []
                    for station in stations:
                        station_name = station.get('StationName', '')
                        county_name = station.get('GeoInfo', {}).get('CountyName', '')
                        if (location in station_name or station_name in location or 
                            location in county_name or county_name in location):
                            found_stations.append(station)
                    
                    if found_stations:
                        print(f"   🔍 {location}: 找到 {len(found_stations)} 個相關測站")
                    else:
                        print(f"   ❌ {location}: 找不到相關測站")
            else:
                print("❌ 資料格式異常")
        else:
            print("❌ 無法獲取真實資料")
            
    except Exception as e:
        print(f"❌ 測試真實 API 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    try:
        print("🧪 氣象站指令測試 - 查詢不到地區處理")
        print("=" * 60)
        
        # 運行測試
        asyncio.run(test_weather_station_not_found())
        
        # 運行真實 API 測試（如果有網路連線）
        print(f"\n" + "=" * 60)
        asyncio.run(test_real_weather_station_command())
        
    except KeyboardInterrupt:
        print("\n⏹️  測試被用戶中斷")
    except Exception as e:
        print(f"❌ 執行測試時發生錯誤: {str(e)}")
        logging.error(f"主要測試錯誤: {str(e)}")
